# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import math
from functions import data_bytes
from functions import data_dataset
from functions import plugins
from functions import note_data
from functions import placement_data
from functions import song
from functions_tracks import tracks_rm

def nbs_parsekey(nbs_file, nbs_newformat):
    nbs_inst = nbs_file.read(1)[0]
    nbs_key = nbs_file.read(1)[0]-51
    if nbs_newformat == 1:
        nbs_velocity = nbs_file.read(1)[0]
        nbs_pan = nbs_file.read(1)[0]
        nbs_pitch = int.from_bytes(nbs_file.read(2), "little", signed=True)
        return [nbs_key, nbs_inst, [nbs_velocity, nbs_pan, nbs_pitch]]
    else: return [nbs_key, nbs_inst, None, None, None]

class input_gt_mnbs(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mnbs'
    def getname(self): return 'Minecraft Note Block Studio'
    def gettype(self): return 'rm'
    def getdawcapabilities(self): return {}
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        cvpj_l = {}
        
        nbs_file = open(input_file, 'rb')
        nbs_len = nbs_file.__sizeof__()
        dataset = data_dataset.dataset('./data_dset/noteblockstudio.dset')
        dataset_midi = data_dataset.dataset('./data_dset/midi.dset')

        # PART 1: HEADER
        nbs_startbyte = int.from_bytes(nbs_file.read(2), "little")
        if nbs_startbyte == 0: 
            nbs_newformat = 1
            nbs_new_version = nbs_file.read(1)[0]
            if nbs_new_version != 5:
                print('[input-mnbs] only version 5 new-NBS or old format is supported.')
                exit()
            nbs_vanilla_inst_count = nbs_file.read(1)[0]
            nbs_songlength = int.from_bytes(nbs_file.read(2), "little")
            nbs_layercount = int.from_bytes(nbs_file.read(2), "little")
        else: 
            nbs_layercount = nbs_startbyte
            nbs_newformat = 0

        nbs_notes = {}
        for playlistid in range(nbs_layercount):
            cvpj_trackid = str(playlistid+1)
            tracks_rm.track_create(cvpj_l, cvpj_trackid, 'instruments')
            tracks_rm.track_visual(cvpj_l, cvpj_trackid, color=[0.23, 0.23, 0.23])
            nbs_notes[playlistid+1] = {}

        nbs_song_name = data_bytes.readstring_lenbyte(nbs_file, 4, "little", "utf-8")
        print('[input-mnbs] Song Title: '+nbs_song_name)

        nbs_song_author = data_bytes.readstring_lenbyte(nbs_file, 4, "little", "utf-8")
        print('[input-mnbs] Song Author: '+nbs_song_author)

        nbs_song_orgauthor = data_bytes.readstring_lenbyte(nbs_file, 4, "little", "utf-8")
        print('[input-mnbs] Song Original Author: '+nbs_song_orgauthor)

        nbs_description = data_bytes.readstring_lenbyte(nbs_file, 4, "little", "utf-8")
        print('[input-mnbs] Song Description: '+nbs_song_orgauthor)

        nbs_tempo = int.from_bytes(nbs_file.read(2), "little")
        tempo = (nbs_tempo/800)*120
        print('[input-mnbs] Tempo: '+str(tempo))
        nbs_file.read(2)
        timesig_numerator = nbs_file.read(1)[0]
        print('[input-mnbs] Time Signature: '+str(timesig_numerator)+'/4')
        nbs_file.read(20)
        nbs_song_sourcefilename = data_bytes.readstring_lenbyte(nbs_file, 4, "little", "utf-8")
        if nbs_newformat == 1:
            nbs_loopon = nbs_file.read(1)[0]
            print('[input-mnbs] Loop Enabled: '+str(nbs_loopon))
            nbs_maxloopcount = nbs_file.read(1)[0]
            print('[input-mnbs] Loop Max Count: '+str(nbs_maxloopcount))
            nbs_loopstarttick = int.from_bytes(nbs_file.read(2), "little")
            print('[input-mnbs] Loop Start Tick: '+str(nbs_loopstarttick))

        # PART 2: NOTE BLOCKS
        notes_done = 0
        note_tick = -1
        split_duration = (timesig_numerator*4)*2
        print_notes = 0

        while notes_done == 0:
            nbs_jump_tick = int.from_bytes(nbs_file.read(2), "little")
            if nbs_jump_tick != 0:
                nbs_jump_layer = int.from_bytes(nbs_file.read(2), "little")
                note_tick += nbs_jump_tick
                if nbs_jump_layer != 0:
                    note_layer = nbs_jump_layer
                    layer_done = 0
                    while layer_done == 0:
                        nbs_notes[note_layer][note_tick] = nbs_parsekey(nbs_file, nbs_newformat)
                        print_notes += 1
                        nbs_jump_layer = int.from_bytes(nbs_file.read(2), "little")
                        if nbs_jump_layer == 0: layer_done = 1
                        note_layer += nbs_jump_layer
            if nbs_jump_tick == 0:
                notes_done = 1
                print('[input-mnbs] Number of Notes: '+str(print_notes))

        # PART 3: LAYERS
        if nbs_file.tell() <= nbs_len:
            for layernum in range(nbs_layercount):
                layername = data_bytes.readstring_lenbyte(nbs_file, 4, "little", "utf-8")
                if layername != None: tracks_rm.track_visual(cvpj_l, str(layernum+1), name=layername)
                if nbs_newformat == 1: nbs_file.read(3)

        # OUTPUT
        for instnum in range(16):
            instid = 'NoteBlock'+str(instnum)
            tracks_rm.import_dset(cvpj_l, instid, instid, dataset, dataset_midi, None, None)

        # PART 4: CUSTOM INSTRUMENTS
        custominstid = 16
        if nbs_file.tell() <= nbs_len:
            num_custominst = nbs_file.read(1)[0]
            for custominstnum in range(num_custominst):
                custominst_name = data_bytes.readstring_lenbyte(nbs_file, 4, "little", "utf-8")
                custominst_file = data_bytes.readstring_lenbyte(nbs_file, 4, "little", "utf-8")
                custominst_key = nbs_file.read(1)[0]
                custominst_presskey = nbs_file.read(1)[0]
                #print(custominst_name, custominst_file, custominst_key, custominst_presskey)

                instid = 'NoteBlock'+str(instnum)

                tracks_rm.inst_create(cvpj_l, instid)
                tracks_rm.inst_visual(cvpj_l, instid, name=custominst_name)
                tracks_rm.inst_pluginid(cvpj_l, instid, instid)

                plugindata = plugins.cvpj_plugindata.cvpj_plugin('sampler', 'single')
                plugindata.dataval_add('file', custominst_file)
                plugindata.to_cvpj(cvpj_l, instid)
                custominstid += 1

        for nbs_layer in nbs_notes:
            nbs_layerdata = nbs_notes[nbs_layer]
            layer_placements = {}
            for note in nbs_layerdata:
                nbs_notedata = nbs_layerdata[note]
                placementnum = math.floor(note/split_duration)*split_duration
                if placementnum not in layer_placements: layer_placements[placementnum] = []
                cvpj_notedata = {}
                if nbs_notedata[2] != None:
                    cvpj_notedata = note_data.mx_makenote('NoteBlock'+str(nbs_notedata[1]), note-placementnum, 2, nbs_notedata[0], nbs_notedata[2][0]/100, (nbs_notedata[2][1]/100)-1)
                    cvpj_notedata['finepitch'] = nbs_notedata[2][2]
                else:
                    cvpj_notedata = note_data.mx_makenote('NoteBlock'+str(nbs_notedata[1]), note-placementnum, 2, nbs_notedata[0], None, None)
                layer_placements[placementnum].append(cvpj_notedata)
            for placenum in layer_placements:
                tracks_rm.add_pl(cvpj_l, str(nbs_layer), 'notes', placement_data.makepl_n(placenum, split_duration, layer_placements[placenum]))

        song.add_info(cvpj_l, 'title', nbs_song_name)
        song.add_info(cvpj_l, 'author', nbs_song_author)
        song.add_info(cvpj_l, 'original_author', nbs_song_orgauthor)
        song.add_info_msg(cvpj_l, 'text', nbs_description)

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True
        
        song.add_timesig(cvpj_l, timesig_numerator, 4)
        song.add_param(cvpj_l, 'bpm', tempo)
        return json.dumps(cvpj_l)

