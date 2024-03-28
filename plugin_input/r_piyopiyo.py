# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import struct
import os.path
from functions import colors
from objects import dv_dataset

class input_piyopiyo(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'piyopiyo'
    def gettype(self): return 'r'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'PiyoPiyo'
        dawinfo_obj.file_ext = 'pmd'
        dawinfo_obj.track_nopl = True
        dawinfo_obj.plugin_included = ['universal:synth-osc']
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(3)
        if bytesdata == b'PMD': return True
        else: return False

    def parse(self, convproj_obj, input_file, dv_config):
        convproj_obj.type = 'r'
        convproj_obj.set_timings(4, True)

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

        pmdtrackdata = []
        keyoffset = [0,0,0,0]

        cvpj_l = {}

        dataset = dv_dataset.dataset('./data_dset/piyopiyo.dset')
        colordata = colors.colorset(dataset.colorset_e_list('inst', 'main'))

        for tracknum in range(3):
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
            idval = str(tracknum)

            track_obj = convproj_obj.add_track(idval, 'instrument', 0, False)
            track_obj.visual.name = 'Inst #'+str(tracknum)
            track_obj.visual.color = colordata.getcolornum(tracknum)
            track_obj.params.add('vol', trk_volume/250, 'float')

            plugin_obj, pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
            plugin_obj.role = 'synth'
            osc_data = plugin_obj.osc_add()
            osc_data.shape = 'custom_wave'
            osc_data.name_id = 'main'
            wave_obj = plugin_obj.wave_add('main')
            wave_obj.set_all_range(trk_waveform, -128, 128)
            plugin_obj.env_blocks_add('vol', trk_envelope, 1/64, 128, None, None)
            plugin_obj.env_points_from_blocks('vol')
            track_obj.inst_pluginid = pluginid

        TrackPVol = int.from_bytes(pmdfile.read(4), "little")

        track_obj = convproj_obj.add_track("3", 'instrument', False, False)
        track_obj.visual.name = 'Drums'
        track_obj.visual.color = colordata.getcolornum(3)
        track_obj.params.add('vol', trk_volume/250, 'float')
        plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-piyopiyo', 'drums')
        plugin_obj.role = 'synth'
        track_obj.inst_pluginid = pluginid

        pmdfile.seek(trackdatapos)

        for tracknum in range(4):
            track_found, track_obj = convproj_obj.find_track(str(tracknum))

            currentpan = 0
            for pmdpos in range(recordspertrack):
                bitnotes = bin(int.from_bytes(pmdfile.read(3), "little"))[2:].zfill(24)
                pan = pmdfile.read(1)[0]
                if pan != 0: currentpan = (pan-4)/3
                notenum = 11
                pitches = []
                for bitnote in bitnotes:
                    if bitnote == '1': pitches.append(notenum)
                    notenum -= 1
                if pitches: track_obj.placements.notelist.add_r_multi(pmdpos, 1, [x+keyoffset[tracknum] for x in pitches], 1, {'pan':currentpan})

        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_singlenotelistcut')
        convproj_obj.params.add('bpm', bpm, 'float')

        convproj_obj.loop_active = True
        convproj_obj.loop_start = loopstart
        convproj_obj.loop_end = loopend