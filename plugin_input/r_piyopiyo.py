# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import struct
import os.path
from functions import audio_wav
from functions import data_bytes
from functions import placement_data
from functions import tracks
from functions import plugins
from functions import song
from functions import note_data

track_colors = [[0.25, 0.38, 0.49], [0.36, 0.43, 0.46], [0.51, 0.57, 0.47], [0.58, 0.64, 0.40]]

class input_piyopiyo(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'piyopiyo'
    def getname(self): return 'PiyoPiyo'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'auto_nopl': True,
        'track_nopl': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(3)
        if bytesdata == b'PMD': return True
        else: return False
    def parse(self, input_file, extra_param):
        pmdfile = open(input_file, 'rb')
        header = pmdfile.read(4)
        trackdatapos = int.from_bytes(pmdfile.read(4), "little")
        musicwait = int.from_bytes(pmdfile.read(4), "little")
        bpm = (120/musicwait)*120
        print("[input-piyopiyo] MusicWait: " + str(musicwait))
        loopstart = int.from_bytes(pmdfile.read(4), "little")
        print("[input-piyopiyo] Loop Beginning: " + str(loopstart))
        loopend = int.from_bytes(pmdfile.read(4), "little")
        print("[input-piyopiyo] Loop End: " + str(loopend))
        recordspertrack = int.from_bytes(pmdfile.read(4), "little")
        print("[input-piyopiyo] Records Per Track: " + str(recordspertrack))

        #samplefolder = extra_param['samplefolder']

        pmdtrackdata = []
        keyoffset = [0,0,0,0]

        cvpj_l = {}

        for tracknum in range(3):
            pluginid = str(tracknum)
            plugins.add_plug(cvpj_l, pluginid, 'native-piyopiyo', 'wave')
            print("[input-piyopiyo] Track " + str(tracknum+1), end=",")
            trk_octave = pmdfile.read(1)[0]
            print(" Oct:" + str(trk_octave), end=",")
            trk_icon = pmdfile.read(1)[0]
            print(" Icon:" + str(trk_icon), end=",")
            trk_unk = pmdfile.read(2)
            trk_length = int.from_bytes(pmdfile.read(4), "little")
            print(" Len:" + str(trk_length), end=",")
            trk_volume = int.from_bytes(pmdfile.read(4), "little")
            print(" Vol:" + str(trk_volume))
            trk_unk2 = pmdfile.read(8)
            trk_waveform = struct.unpack('b'*256, pmdfile.read(256))
            trk_envelope = struct.unpack('B'*64, pmdfile.read(64))
            keyoffset[tracknum] = (trk_octave-2)*12
            #wave_path = samplefolder+'/'+str(tracknum+1)+'.wav'
            plugins.add_wave(cvpj_l, pluginid, 'main', trk_waveform, -128, 128)
            plugins.add_env_blocks(cvpj_l, pluginid, 'vol', trk_envelope, 128, None, None)
            idval = str(tracknum)
            tracks.r_create_inst(cvpj_l, idval, {'pluginid': pluginid})
            tracks.r_basicdata(cvpj_l, idval, 'note'+str(tracknum), track_colors[tracknum], trk_volume/250, None)

        TrackPVol = int.from_bytes(pmdfile.read(4), "little")
        plugins.add_plug(cvpj_l, "3", 'native-piyopiyo', 'drums')
        tracks.r_create_inst(cvpj_l, "3", {'pluginid': "3"})
        tracks.r_basicdata(cvpj_l, "3", 'perc', track_colors[3], TrackPVol/250, None)

        pmdfile.seek(trackdatapos)
        for tracknum in range(4):
            notelist = []
            t_placements = []
            currentpan = 0
            for pmdpos in range(recordspertrack):
                bitnotes = bin(int.from_bytes(pmdfile.read(3), "little"))[2:].zfill(24)
                pan = pmdfile.read(1)[0]
                if pan != 0: currentpan = (pan-4)/3
                notenum = 11
                for bitnote in bitnotes:
                    if bitnote == '1': notelist.append(note_data.rx_makenote(pmdpos, 1, notenum+keyoffset[tracknum], 1.0, currentpan))
                    notenum -= 1
            if notelist != []: t_placements = placement_data.nl2pl(notelist)
            else: t_placements = []
            tracks.r_pl_notes(cvpj_l, str(tracknum), t_placements)

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True
        cvpj_l['bpm'] = bpm

        song.add_timemarker_looparea(cvpj_l, None, loopstart, loopend)
        return json.dumps(cvpj_l)