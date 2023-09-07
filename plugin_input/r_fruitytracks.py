# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
from functions import data_bytes
from functions import data_values
from functions import note_data
from functions import tracks
from functions import song
from functions import audio
from functions import format_flp_tlv

import plugin_input
import json
import os

class input_fruitytracks(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'fruitytracks'
    def getname(self): return 'FruityTracks'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'placement_loop': ['loop', 'loop_off', 'loop_adv'],
        'placement_audio_stretch': ['rate'],
        }
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'FThd': return True
        else: return False
    def supported_autodetect(self): return True
    def parse(self, input_file, extra_param):

        cvpj_l = {}

        fileobject = open(input_file, 'rb')
        headername = fileobject.read(4)
        rifftable = data_bytes.riff_read(fileobject, 0)
        for riffobj in rifftable:
            ##print(str(riffobj[0]) + str(len(riffobj[1])))
            if riffobj[0] == b'FTdt':
                eventtable = format_flp_tlv.decode(riffobj[1])

        bpm = 120
        tracknum = 0
        sampledata = []
        for event in eventtable:

            tablenum = tracknum-1

            #print(event)
            if event[0] == 2: 
                tracknum += 1
                sampledata.append([])
                tracks.r_create_track(cvpj_l, 'audio', str(tracknum), name=str(tracknum))

            if event[0] == 5: sampledata[tablenum].append({})
            if event[0] == 66: bpm = event[1]
            if event[0] == 196: 
                filename = event[1].decode().rstrip('\x00')
                filenamesplit = filename.split('\\')
                if filenamesplit[0] == '':
                    basefolder = os.path.dirname(input_file)
                    filename = os.path.normpath(os.path.join(basefolder, '..','Samples',*filenamesplit[1:]))

                sampledata[tablenum][-1]['file'] = filename 

            if event[0] == 193: sampledata[tablenum][-1]['name'] = event[1].decode().rstrip('\x00')
            if event[0] == 129: sampledata[tablenum][-1]['pos'] = event[1]
            if event[0] == 130: sampledata[tablenum][-1]['dur'] = event[1]
            if event[0] == 131: sampledata[tablenum][-1]['repeatlen'] = event[1]
            if event[0] == 137: sampledata[tablenum][-1]['stretch'] = event[1]

        bpmdiv = 120/bpm
        bpmticks = 5512

        tracknum = 1
        for trackdata in sampledata:
            tracknum += 1
            for sampleda in trackdata:

                cvpj_pldata = {}

                cvpj_pldata["file"] = sampleda['file']
                cvpj_pldata["name"] = sampleda['name']

                stretch = sampleda["stretch"]

                cvpj_pldata["position"] = (sampleda["pos"]/bpmticks)/bpmdiv

                cvpj_pldata['cut'] = {}
                cvpj_pldata['cut']['type'] = 'loop'
                if stretch == 0:
                    cvpj_pldata["duration"] = (sampleda["dur"]/bpmticks)
                    cvpj_pldata['cut']['loopend'] = (sampleda["repeatlen"]/bpmticks)
                else:
                    audioinfo = audio.get_audiofile_info(sampleda['file'])
                    duration = audioinfo['dur']
                    audduration = audioinfo["dur_sec"]*8

                    cvpj_pldata["duration"] = (sampleda["dur"]/bpmticks)/bpmdiv
                    cvpj_pldata['cut']['loopstart'] = 0
                    cvpj_pldata['cut']['loopend'] = (sampleda["repeatlen"]/bpmticks)/bpmdiv
                    cvpj_pldata['audiomod'] = {}
                    cvpj_pldata['audiomod']['stretch_algorithm'] = 'resample'
                    cvpj_pldata['audiomod']['stretch_method'] = 'rate_tempo'
                    cvpj_pldata['audiomod']['stretch_data'] = {'rate': audduration/stretch}

                tracks.r_pl_audio(cvpj_l, str(tracknum), cvpj_pldata)

        song.add_param(cvpj_l, 'bpm', bpm)
        return json.dumps(cvpj_l)