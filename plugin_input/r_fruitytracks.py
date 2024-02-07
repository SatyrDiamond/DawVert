# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_plugin import format_flp_tlv
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

    def parse(self, convproj_obj, input_file, extra_param):
        convproj_obj.type = 'r'
        convproj_obj.set_timings(4, True)

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

                track_obj = convproj_obj.add_track(str(tracknum), 'audio', 1, False)
                track_obj.visual.name = 'Track '+str(tracknum)
                track_obj.visual.color = maincolor

            if event[0] == 5: sampledata[tablenum].append({})
            if event[0] == 66: bpm = event[1]
            if event[0] == 196: sampledata[tablenum][-1]['file'] = event[1].decode().rstrip('\x00')
            if event[0] == 193: sampledata[tablenum][-1]['name'] = event[1].decode().rstrip('\x00')
            if event[0] == 129: sampledata[tablenum][-1]['pos'] = event[1]
            if event[0] == 130: sampledata[tablenum][-1]['dur'] = event[1]
            if event[0] == 131: sampledata[tablenum][-1]['repeatlen'] = event[1]
            if event[0] == 137: sampledata[tablenum][-1]['stretch'] = event[1]

        bpmdiv = 120/bpm
        bpmticks = 5512

        for tracknum in sampledata:

            track_found, track_obj = convproj_obj.find_track(str(tracknum+1))

            if track_found:
                for sampleda in tracknum:

                    placement_obj = track_obj.placements.add_audio()
                    placement_obj.position = (sampleda["pos"]/bpmticks)/bpmdiv
                    placement_obj.visual.name = sampleda['name']

                    filepath = sampleda['file']
                    sampleref_obj = convproj_obj.add_sampleref(filepath, filepath)
                    placement_obj.sampleref = filepath

                    placement_obj.cut_type = 'loop'
                    placement_obj.cut_data = {}

                    stretch = sampleda["stretch"]

                    if stretch == 0:
                        placement_obj.duration = (sampleda["dur"]/bpmticks)
                        placement_obj.cut_data['loopend'] = (sampleda["repeatlen"]/bpmticks)
                    else:
                        duration = sampleref_obj.dur_samples
                        audduration = sampleref_obj.dur_sec*8

                        placement_obj.duration = (sampleda["dur"]/bpmticks)/bpmdiv
                        placement_obj.cut_data['loopstart'] = 0
                        placement_obj.cut_data['loopend'] = (sampleda["repeatlen"]/bpmticks)/bpmdiv
                        placement_obj.stretch_algorithm = 'resample'
                        placement_obj.stretch_method = 'rate_tempo'
                        placement_obj.stretch_rate = audduration/stretch

        convproj_obj.params.add('bpm', bpm, 'float')