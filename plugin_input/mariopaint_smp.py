# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
import plugin_input
import json
import io

instnames = ['MARIO','MUSHROOM','YOSHI','STAR','FLOWER','GAMEBOY','DOG','CAT','PIG','SWAN','FACE','PLANE','BOAT','CAR','HEART','PIRANHA','COIN','SHYGUY','BOO','LUIGI','PEACH','FEATHER','BULLETBILL','GOOMBA','BOBOMB','SPINY','FRUIT','ONEUP','MOON','EGG','GNOME']
keytable = {'C': 0,
'D': 2,
'E': 4,
'F': 5,
'G': 7,
'A': 9,
'B': 11}

out_names = {'MARIO': 'Mario',
'MUSHROOM': 'Toad',
'YOSHI': 'Yoshi',
'STAR': 'Star',
'FLOWER': 'Flower',
'GAMEBOY': 'Game Boy',
'DOG': 'Dog',
'CAT': 'Cat',
'PIG': 'Pig',
'SWAN': 'Swan',
'FACE': 'Face',
'PLANE': 'Plane',
'BOAT': 'Boat',
'CAR': 'Car',
'HEART': 'Heart',
'PIRANHA': 'Plant',
'COIN': 'Coin',
'SHYGUY': 'Shy Guy',
'BOO': 'Ghost',
'LUIGI': 'Luigi',
'PEACH': 'Peach',
'FEATHER': 'Feather',
'BULLETBILL': 'Bullet Bill',
'GOOMBA': 'Goomba',
'BOBOMB': 'Bob-omb',
'SPINY': 'Spiny',
'FRUIT': 'Fruit',
'ONEUP': '1-Up',
'MOON': 'Moon',
'EGG': 'Egg',
'GNOME': 'Gnome'}

out_colors = {'MARIO': [0.92, 0.77, 0.56],
'MUSHROOM': [0.98, 0.00, 0.00],
'YOSHI': [0.00, 0.98, 0.02],
'STAR': [0.97, 0.98, 0.00],
'FLOWER': [0.96, 0.50, 0.00],
'GAMEBOY': [0.76, 0.76, 0.76],
'DOG': [1.00, 1.00, 1.00],
'CAT': [0.98, 0.75, 0.51],
'PIG': [0.96, 0.75, 0.52],
'SWAN': [0.75, 0.75, 0.76],
'FACE': [0.98, 0.76, 0.51],
'PLANE': [1.00, 1.00, 1.00],
'BOAT': [0.96, 0.00, 0.01],
'CAR': [0.88, 0.53, 0.17],
'HEART': [0.96, 0.00, 0.00],
'PIRANHA': [0.73, 0.00, 0.01],
'COIN': [0.93, 0.75, 0.20],
'SHYGUY': [0.64, 0.00, 0.01],
'BOO': [0.57, 0.96, 0.99],
'LUIGI': [0.00, 0.97, 0.48],
'PEACH': [0.97, 0.31, 0.56],
'FEATHER': [0.97, 0.47, 0.00],
'BULLETBILL': [0.00, 0.00, 0.00],
'GOOMBA': [0.75, 0.25, 0.13],
'BOBOMB': [0.00, 0.00, 0.00],
'SPINY': [0.97, 0.50, 0.00],
'FRUIT': [0.97, 0.00, 0.00],
'ONEUP': [0.00, 0.97, 0.00],
'MOON': [0.97, 0.97, 0.00],
'EGG': [0.00, 0.97, 0.00],
'GNOME': [0.00, 0.50, 0.25]}

def makenote(n_pos, notes, vol, notesize):
    for note in notes:
        notesplit = note.split(' ')
        notetxt = notesplit[1]
        smpnote_size = len(notetxt)
        smpnote_str = io.StringIO(notetxt)

        out_inst = notesplit[0]
        out_key = keytable[smpnote_str.read(1)]
        out_oct = int(smpnote_str.read(1))-4
        out_mode = 0
        out_offset = 0

        while smpnote_str.tell() < smpnote_size:
            t_txtp = smpnote_str.read(1)
            if t_txtp == '#': out_offset = 1
            if t_txtp == 'b': out_offset = -1
            if t_txtp == 'm': 
                out_mode = smpnote_str.read(1)

        if out_mode == 0:
            out_note = out_key + out_oct*12 + out_offset
            notedata = {}
            notedata['position'] = n_pos*notesize
            notedata['key'] = out_note
            notedata['vol'] = vol/100
            notedata['duration'] = notesize
            notedata['instrument'] = out_inst
            notelist.append(notedata)

class input_mariopaint_smp(plugin_input.base):
    def __init__(self): pass
    def getshortname(self): return 'mariopaint_smp'
    def getname(self): return 'Super Mario Paint'
    def gettype(self): return 'm'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global notelist

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_playlist = {}
        
        notelist = []

        smp_values = {}

        notelen = 2
        linecount = 0
        f_smp = open(input_file, 'r')
        lines_smp = f_smp.readlines()
        for line in lines_smp:
            if linecount == 0: 
                t_smp_values = line.rstrip().split(', ')
                for t_smp_value in t_smp_values:
                    smp_nameval = t_smp_value.split(':')
                    smp_values[smp_nameval[0]] = smp_nameval[1]
                    if smp_nameval[0] == "TEMPO": smp_tempo = float(smp_nameval[1])
                    else: smp_tempo = 200
                while smp_tempo > 180:
                    smp_tempo = smp_tempo/2
                    notelen = notelen/2

            else: 
                s_point = line.rstrip().split(',')
                s_data = s_point[1:]

                s_pos = s_point[:1][0].split(':')
                s_pos_beat = int(s_pos[0])
                s_pos_pos = int(s_pos[1])

                s_pos_out = ((s_pos_beat-1)*4) + s_pos_pos

                s_notes = s_data[:-1]
                s_vol = int(s_data[-1:][0].split(':')[1])

                makenote(s_pos_out, s_notes, s_vol, notelen)

            linecount += 1

        l_placement = {}
        l_placement['type'] = "instruments"
        l_placement['position'] = 0
        l_placement['notelist'] = notelist

        cvpj_l_playlist[str(1)] = {}
        cvpj_l_playlist[str(1)]['placements'] = [l_placement]

        for instname in instnames:
            cvpj_inst = {}
            cvpj_inst["name"] = out_names[instname]
            cvpj_inst["color"] = colors.moregray(out_colors[instname])
            cvpj_inst["instdata"] = {}
            cvpj_instdata = cvpj_inst["instdata"]
            cvpj_instdata['plugin'] = 'general-midi'
            cvpj_instdata['plugindata'] = {'bank':0, 'inst':instnames.index(instname)}
            cvpj_l_instruments[instname] = cvpj_inst
            cvpj_l_instrumentsorder.append(instname)

        cvpj_l['timesig_numerator'] = 4
        cvpj_l['timesig_denominator'] = 4
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = smp_tempo
        return json.dumps(cvpj_l)

