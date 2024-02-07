# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import math
from functions import data_bytes
from objects import dv_dataset

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
    def parse(self, convproj_obj, input_file, extra_param):
        convproj_obj.type = 'rm'
        convproj_obj.set_timings(4, True)
        
        nbs_file = open(input_file, 'rb')
        nbs_len = nbs_file.__sizeof__()
        dataset = dv_dataset.dataset('./data_dset/noteblockstudio.dset')
        dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')

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
        for nbs_layer in range(nbs_layercount):
            cvpj_trackid = str(nbs_layer+1)
            track_obj = convproj_obj.add_track(cvpj_trackid, 'instruments', 1, False)
            track_obj.visual.name = cvpj_trackid
            track_obj.visual.color = [0.23, 0.23, 0.23]
            nbs_notes[nbs_layer+1] = {}

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
                if layername != None: 
                    track_found, track_obj = convproj_obj.find_track(cvpj_trackid)
                    if track_found: track_obj.visual.name = layername
                if nbs_newformat == 1: nbs_file.read(3)

        # OUTPUT
        for instnum in range(16):
            instid = 'NoteBlock'+str(instnum)
            convproj_obj.add_instrument_from_dset(instid, instid, dataset, dataset_midi, instid, None, None)

        # PART 4: CUSTOM INSTRUMENTS
        custominstid = 16
        if nbs_file.tell() <= nbs_len:
            num_custominst = nbs_file.read(1)[0]
            for custominstnum in range(num_custominst):
                custominst_name = data_bytes.readstring_lenbyte(nbs_file, 4, "little", "utf-8")
                custominst_file = data_bytes.readstring_lenbyte(nbs_file, 4, "little", "utf-8")
                custominst_key = nbs_file.read(1)[0]
                custominst_presskey = nbs_file.read(1)[0]

                instid = 'NoteBlock'+str(instnum)

                inst_obj = convproj_obj.add_instrument(inst_id)
                inst_obj.visual.name = custominst_name
                plugin_obj, sampleref_obj = convproj_obj.add_plugin_sampler(instid, custominst_file)
                inst_obj.pluginid = instid

                custominstid += 1

        for nbs_layer in nbs_notes:
            nbs_layerdata = nbs_notes[nbs_layer]
            layer_placements = {}
            for note in nbs_layerdata:
                nbs_notedata = nbs_layerdata[note]
                placementnum = math.floor(note/split_duration)*split_duration
                if placementnum not in layer_placements: 
                    layer_placements[placementnum] = []

                if nbs_notedata[2] != None:
                    layer_placements[placementnum].append([
                        'NoteBlock'+str(nbs_notedata[1]), 
                        note-placementnum, 
                        2, nbs_notedata[0], nbs_notedata[2][0]/100, 
                        {'pan': (nbs_notedata[2][1]/100)-1, 'finepitch': nbs_notedata[2][2]}])
                else:
                    layer_placements[placementnum].append([
                        'NoteBlock'+str(nbs_notedata[1]), 
                        note-placementnum, 
                        2, nbs_notedata[0], 1, 
                        {}])
                
            for placenum in layer_placements:
                track_found, track_obj = convproj_obj.find_track(str(nbs_layer))
                if track_found:
                    placement_obj = track_obj.placements.add_notes()
                    placement_obj.position = placenum
                    placement_obj.duration = split_duration
                    for n in layer_placements[placenum]: placement_obj.notelist.add_m(n[0], n[1], n[2], n[3], n[4], n[5])

        convproj_obj.metadata.name = nbs_song_name
        convproj_obj.metadata.author = nbs_song_author
        convproj_obj.metadata.original_author = nbs_song_orgauthor
        convproj_obj.metadata.comment_text = nbs_description

        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_singlenotelistcut')
        convproj_obj.params.add('bpm', tempo, 'float')
        convproj_obj.timesig = [timesig_numerator, 4]
