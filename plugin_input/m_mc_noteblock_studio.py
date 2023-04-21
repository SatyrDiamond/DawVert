# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import math
from functions import data_bytes
from functions import tracks
from functions import idvals
from functions import note_data
from functions import placement_data

def getstring(nbs_file):
    stringlen = int.from_bytes(nbs_file.read(4), "little")
    if stringlen != 0: return nbs_file.read(stringlen).decode("utf-8")
    else: return ''

def nbs_parsekey(nbs_file, nbs_newformat):
    nbs_inst = nbs_file.read(1)[0]
    nbs_key = nbs_file.read(1)[0]-51
    if nbs_newformat == 1:
        nbs_velocity = nbs_file.read(1)[0]
        nbs_pan = nbs_file.read(1)[0]
        nbs_pitch = int.from_bytes(nbs_file.read(2), "little", signed="True")
        return [nbs_key, nbs_inst, [nbs_velocity, nbs_pan, nbs_pitch]]
    else: return [nbs_key, nbs_inst, None, None, None]

class input_gt_mnbs(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mnbs'
    def getname(self): return 'Minecraft Note Block Studio'
    def gettype(self): return 'm'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': True,
        'placement_cut': False,
        'placement_warp': False,
        'no_pl_auto': False,
        'no_placements': False
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):

        cvpj_l = {}
        song_message = ""

        nbs_file = open(input_file, 'rb')
        nbs_file.seek(0,2)
        nbs_len = nbs_file.tell()
        nbs_file.seek(0)

        idvals_inst_mnbs = idvals.parse_idvalscsv('idvals/noteblockstudio_inst.csv')

        # PART 1: HEADER
        nbs_startbyte = int.from_bytes(nbs_file.read(2), "little")
        if nbs_startbyte == 0: 
            nbs_newformat = 1
        else: 
            nbs_layercount = nbs_startbyte
            nbs_newformat = 0

        if nbs_newformat == 1:
            nbs_new_version = nbs_file.read(1)[0]
            if nbs_new_version != 5:
                print('[input-mnbs] only version 5 new-NBS or old format is supported.')
                exit()
            nbs_vanilla_inst_count = nbs_file.read(1)[0]
            nbs_songlength = int.from_bytes(nbs_file.read(2), "little")
            nbs_layercount = int.from_bytes(nbs_file.read(2), "little")

        nbs_notes = {}
        for playlistid in range(nbs_layercount):
            tracks.m_playlist_pl(cvpj_l, playlistid+1, None, [0.23, 0.23, 0.23], [])
            nbs_notes[playlistid+1] = {}

        nbs_song_name = getstring(nbs_file)
        print('[input-mnbs] Song Title: '+nbs_song_name)

        nbs_song_author = getstring(nbs_file)
        print('[input-mnbs] Song Author: '+nbs_song_author)

        nbs_song_orgauthor = getstring(nbs_file)
        print('[input-mnbs] Song Original Author: '+nbs_song_orgauthor)

        nbs_description = getstring(nbs_file)
        print('[input-mnbs] Song Description: '+nbs_song_orgauthor)

        nbs_tempo = int.from_bytes(nbs_file.read(2), "little")
        tempo = (nbs_tempo/800)*120
        print('[input-mnbs] Tempo: '+str(tempo))
        nbs_file.read(2)
        timesig_numerator = nbs_file.read(1)[0]
        print('[input-mnbs] Time Signature: '+str(timesig_numerator)+'/4')
        nbs_file.read(20)
        nbs_song_sourcefilename = getstring(nbs_file)
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
                tracks.m_playlist_pl_add(cvpj_l, nbs_layer, placement_data.makepl_n(placenum, split_duration, layer_placements[placenum]))

        # PART 3: LAYERS
        if nbs_file.tell() <= nbs_len:
            for layernum in range(nbs_layercount):
                layername = getstring(nbs_file)
                if layername != None: tracks.m_playlist_pl(cvpj_l, playlistid+1, layername, None, None)
                if nbs_newformat == 1: nbs_file.read(3)

        # OUTPUT
        for instnum in range(16):
            instid = 'NoteBlock'+str(instnum)
            cvpj_instname = idvals.get_idval(idvals_inst_mnbs, str(instnum), 'name')
            cvpj_instcolor = idvals.get_idval(idvals_inst_mnbs, str(instnum), 'color')
            cvpj_instgm = idvals.get_idval(idvals_inst_mnbs, str(instnum), 'gm_inst')
            cvpj_instdata = {}
            if cvpj_instgm != None: cvpj_instdata = {'plugin': 'general-midi', 'plugindata': {'bank': 0, 'inst': cvpj_instgm-1}}

            tracks.m_create_inst(cvpj_l, instid, cvpj_instdata)
            tracks.m_basicdata_inst(cvpj_l, instid, cvpj_instname, cvpj_instcolor, 1.0, 0.0)

        cvpj_l['info'] = {}
        cvpj_l['info']['title'] = nbs_song_name
        cvpj_l['info']['author'] = nbs_song_author
        cvpj_l['info']['original_author'] = nbs_song_orgauthor
        cvpj_l['info']['message'] = {}
        cvpj_l['info']['message']['type'] = 'text'
        cvpj_l['info']['message']['text'] = nbs_description

        cvpj_l['do_addwrap'] = True
        cvpj_l['do_singlenotelistcut'] = True
        
        cvpj_l['timesig_numerator'] = timesig_numerator
        cvpj_l['timesig_denominator'] = 4
        cvpj_l['bpm'] = tempo
        return json.dumps(cvpj_l)

