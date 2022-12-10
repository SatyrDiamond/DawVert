# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
import plugin_input
import json
import math

def getstring(nbs_file):
    stringlen = int.from_bytes(nbs_file.read(4), "little")
    if stringlen != 0:
        return nbs_file.read(stringlen).decode("utf-8")
    else: return None

def nbs_parsekey(nbs_file, nbs_newformat):
    nbs_inst = int.from_bytes(nbs_file.read(1), "little")
    #print('I:'+str(nbs_inst), end=' ')
    nbs_key = int.from_bytes(nbs_file.read(1), "little")-51
    #print('K:'+str(nbs_key), end=' ')
    if nbs_newformat == 1:
        nbs_velocity = int.from_bytes(nbs_file.read(1), "little")
        #print('V:'+str(nbs_velocity), end=' ')
        nbs_pan = int.from_bytes(nbs_file.read(1), "little")
        #print('P:'+str(nbs_pan), end=' ')
        nbs_pitch = int.from_bytes(nbs_file.read(2), "little", signed="True")
        #print('F:'+str(nbs_pitch))
        return [nbs_key, nbs_inst, [nbs_velocity, nbs_pan, nbs_pitch]]
    else:
        return [nbs_key, nbs_inst, None]

class input_gt_mnbs(plugin_input.base):
    def __init__(self): pass
    def getshortname(self): return 'mnbs'
    def getname(self): return 'Minecraft Note Block Studio'
    def gettype(self): return 'm'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_playlist = {}
        song_message = ""

        nbs_file = open(input_file, 'rb')

        noteblockinst = {}
        noteblockinst[0] = "Piano (Air)"
        noteblockinst[1] = "Double Bass (Wood)"
        noteblockinst[2] = "Bass Drum (Stone)"
        noteblockinst[3] = "Snare Drum (Sand)"
        noteblockinst[4] = "Click (Glass)"
        noteblockinst[5] = "Guitar (Wool)"
        noteblockinst[6] = "Flute (Clay)"
        noteblockinst[7] = "Bell (Block of Gold)"
        noteblockinst[8] = "Chime (Packed Ice)"
        noteblockinst[9] = "Xylophone (Bone Block)"
        noteblockinst[10] = "Iron Xylophone (Iron Block)"
        noteblockinst[11] = "Cow Bell (Soul Sand)"
        noteblockinst[12] = "Didgeridoo (Pumpkin)"
        noteblockinst[13] = "Bit (Block of Emerald)"
        noteblockinst[14] = "Banjo (Hay)"
        noteblockinst[15] = "Pling (Glowstone)"

        colors = {}
        colors[0] = [0.00, 0.27, 0.55]
        colors[1] = [0.13, 0.43, 0.18]
        colors[2] = [0.61, 0.30, 0.31]
        colors[3] = [0.61, 0.61, 0.00]
        colors[4] = [0.49, 0.24, 0.48]
        colors[5] = [0.40, 0.18, 0.12]
        colors[6] = [0.61, 0.58, 0.25]
        colors[7] = [0.61, 0.00, 0.61]
        colors[8] = [0.21, 0.44, 0.49]
        colors[9] = [0.61, 0.61, 0.61]
        colors[10] = [0.00, 0.44, 0.61]
        colors[11] = [0.61, 0.04, 0.05]
        colors[12] = [0.61, 0.23, 0.06]
        colors[13] = [0.00, 0.61, 0.00]
        colors[14] = [0.61, 0.00, 0.23]
        colors[15] = [0.24, 0.24, 0.24]

        for instnum in range(16):
            instid = 'NoteBlock'+str(instnum)
            cvpj_l_instruments[instid] = {}
            cvpj_l_instruments[instid]['name'] = noteblockinst[instnum]
            cvpj_l_instruments[instid]['color'] = colors[instnum]
            cvpj_l_instruments[instid]['instdata'] = {}
            cvpj_l_instruments[instid]['instdata']['plugin'] = 'none'
            cvpj_l_instrumentsorder.append(instid)

        # PART 1: HEADER
        nbs_startbyte = int.from_bytes(nbs_file.read(2), "little")
        if nbs_startbyte == 0: 
            nbs_newformat = 1
        else: 
            nbs_layercount = nbs_startbyte
            nbs_newformat = 0

        if nbs_newformat == 1:
            nbs_new_version = int.from_bytes(nbs_file.read(1), "little")
            if nbs_new_version != 5:
                print('only version 5 new-NBS or old format is supported.')
                exit()
            nbs_vanilla_inst_count = int.from_bytes(nbs_file.read(1), "little")
            nbs_songlength = int.from_bytes(nbs_file.read(2), "little")
            nbs_layercount = int.from_bytes(nbs_file.read(2), "little")

        nbs_notes = {}
        for playlistid in range(nbs_layercount):
            cvpj_l_playlist[playlistid+1] = {}
            cvpj_l_playlist[playlistid+1]['color'] = [0.23, 0.23, 0.23]
            cvpj_l_playlist[playlistid+1]['name'] = 'Layer ' + str(playlistid+1)
            cvpj_l_playlist[playlistid+1]['placements'] = []
            nbs_notes[playlistid+1] = {}

        nbs_song_name = getstring(nbs_file)
        if nbs_song_name != None: cvpj_l['title'] = nbs_song_name

        nbs_song_author = getstring(nbs_file)
        if nbs_song_author != None: cvpj_l['author'] = nbs_song_author

        nbs_song_orgauthor = getstring(nbs_file)
        nbs_description = getstring(nbs_file)

        if nbs_description != None: song_message += nbs_description
        if nbs_song_orgauthor != None: song_message += '\n\n' + 'Original Author: ' + nbs_song_orgauthor

        nbs_tempo = int.from_bytes(nbs_file.read(2), "little")
        tempo = (nbs_tempo/800)*120
        nbs_file.read(2)
        timesig_numerator = int.from_bytes(nbs_file.read(1), "little")
        nbs_file.read(4)
        nbs_file.read(4)
        nbs_file.read(4)
        nbs_file.read(4)
        nbs_file.read(4)
        nbs_song_sourcefilename = getstring(nbs_file)
        if nbs_newformat == 1:
            nbs_loopon = int.from_bytes(nbs_file.read(1), "little")
            nbs_maxloopcount = int.from_bytes(nbs_file.read(1), "little")
            nbs_loopstarttick = int.from_bytes(nbs_file.read(2), "little")

        # PART 2: NOTE BLOCKS
        notes_done = 0
        note_tick = -1
        split_duration = timesig_numerator*4

        while notes_done == 0:
            nbs_jump_tick = int.from_bytes(nbs_file.read(2), "little")
            if nbs_jump_tick != 0:
                nbs_jump_layer = int.from_bytes(nbs_file.read(2), "little")
                note_tick += nbs_jump_tick
                if nbs_jump_layer != 0:
                    note_layer = nbs_jump_layer
                    layer_done = 0
                    while layer_done == 0:
                        #print('T:'+str(note_tick), end=' ')
                        #print('L:'+str(note_layer), end=' ')
                        nbs_notes[note_layer][note_tick] = nbs_parsekey(nbs_file, nbs_newformat)
                        nbs_jump_layer = int.from_bytes(nbs_file.read(2), "little")
                        if nbs_jump_layer == 0: layer_done = 1
                        note_layer += nbs_jump_layer
            if nbs_jump_tick == 0:
                notes_done = 1
                #print(nbs_jump_tick, 'Done')

        for nbs_layer in nbs_notes:
            nbs_layerdata = nbs_notes[nbs_layer]
            #print(nbs_layer, len(nbs_layerdata))
            layer_placements = {}
            for note in nbs_layerdata:
                nbs_notedata = nbs_layerdata[note]
                placementnum = math.floor(note/split_duration)*split_duration
                if placementnum not in layer_placements:
                    layer_placements[placementnum] = []
                cvpj_notedata = {}
                cvpj_notedata['position'] = note-placementnum
                cvpj_notedata['duration'] = 1
                cvpj_notedata['instrument'] = 'NoteBlock'+str(nbs_notedata[1])
                cvpj_notedata['key'] = nbs_notedata[0]
                if nbs_notedata[2] != None:
                    cvpj_notedata['vol'] = nbs_notedata[2][0]/100
                    cvpj_notedata['pan'] = (nbs_notedata[2][0]/200)-0.5
                    cvpj_notedata['finepitch'] = nbs_notedata[2][0]
                layer_placements[placementnum].append(cvpj_notedata)
                #print(placementnum, note-placementnum, nbs_notedata)
            for placenum in layer_placements:
                cvpj_pl_data = {}
                cvpj_pl_data['type'] = 'instruments'
                cvpj_pl_data['position'] = placenum
                cvpj_pl_data['notelist'] = layer_placements[placenum]
                cvpj_l_playlist[nbs_layer]['placements'].append(cvpj_pl_data)

        cvpj_l['message'] = {}
        cvpj_l['message']['type'] = 'text'
        cvpj_l['message']['text'] = song_message

        cvpj_l['timesig_numerator'] = timesig_numerator
        cvpj_l['timesig_denominator'] = 4
        cvpj_l['bpm'] = tempo
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        return json.dumps(cvpj_l)

