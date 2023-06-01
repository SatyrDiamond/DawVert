# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
from functions import idvals
from functions import tracks
from functions import song
from functions import note_data
from functions import placement_data
import plugin_input
import json
import io

instnames = ['MARIO','MUSHROOM','YOSHI','STAR','FLOWER','GAMEBOY','DOG','CAT','PIG','SWAN','FACE','PLANE','BOAT','CAR','HEART','PIRANHA','COIN','SHYGUY','BOO','LUIGI','PEACH','FEATHER','BULLETBILL','GOOMBA','BOBOMB','SPINY','FRUIT','ONEUP','MOON','EGG','GNOME']
smpnames = {'MARIO': "mario", 'MUSHROOM': "toad", 'YOSHI': "yoshi", 'STAR': "star", 'FLOWER': "flower", 'GAMEBOY': "gameboy", 'DOG': "dog", 'CAT': "cat", 'PIG': "pig", 'SWAN': "swan", 'FACE': "face", 'PLANE': "plane", 'BOAT': "boat", 'CAR': "car", 'HEART': "heart", 'PIRANHA': "plant", 'COIN': "coin", 'SHYGUY': "shyguy", 'BOO': "ghost", 'LUIGI': "luigi", 'PEACH': "peach", 'FEATHER': "feather", 'BULLETBILL': "bulletbill", 'GOOMBA': "goomba", 'BOBOMB': "bobomb", 'SPINY': "spiny", 'FRUIT': "fruit", 'ONEUP': "oneup", 'MOON': "moon", 'EGG': "egg", 'GNOME': "gnome"}
keytable = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

def makenote(n_pos, notes, vol, notesize):
    for note in notes:
        notesplit = note.split(' ')
        notetxt = notesplit[1]
        smpnote_size = len(notetxt)
        smpnote_str = io.StringIO(notetxt)

        out_key = keytable[smpnote_str.read(1)]
        out_oct = int(smpnote_str.read(1))-4
        out_mode = 0
        out_offset = 0

        while smpnote_str.tell() < smpnote_size:
            t_txtp = smpnote_str.read(1)
            if t_txtp == '#': out_offset = 1
            if t_txtp == 'b': out_offset = -1
            if t_txtp == 'm': out_mode = smpnote_str.read(1)

        if out_mode == 0: cvpj_notelist.append(note_data.mx_makenote(notesplit[0], n_pos*notesize, notesize, out_key+out_oct*12+out_offset, vol/100, None))

class input_mariopaint_smp(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mariopaint_smp'
    def getname(self): return 'Super Mario Paint'
    def gettype(self): return 'm'
    def getdawcapabilities(self):
        return {'track_lanes': True, 'track_nopl': True}
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global cvpj_notelist
        idvals_mariopaint_inst = idvals.parse_idvalscsv('data_idvals/mariopaint_inst.csv')
        cvpj_l = {}
        cvpj_notelist = []
        smp_values = {}
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
                smp_tempo, notelen = song.get_lower_tempo(smp_tempo, 2, 180)
            else: 
                s_point = line.rstrip().split(',')
                s_data = s_point[1:]
                s_pos = s_point[:1][0].split(':')
                s_pos_out = ((int(s_pos[0])-1)*4) + int(s_pos[1])
                s_notes = s_data[:-1]
                s_vol = int(s_data[-1:][0].split(':')[1])
                makenote(s_pos_out, s_notes, s_vol, notelen)
            linecount += 1

        tracks.m_playlist_pl(cvpj_l, 1, None, None, placement_data.nl2pl(cvpj_notelist))

        for instname in instnames:
            s_inst_name = idvals.get_idval(idvals_mariopaint_inst, smpnames[instname], 'name')
            s_inst_color = idvals.get_idval(idvals_mariopaint_inst, smpnames[instname], 'color')
            if s_inst_color != None: s_inst_color = colors.moregray(s_inst_color)
            tracks.m_create_inst(cvpj_l, instname, {'plugin': 'general-midi', 'plugindata': {'bank':0, 'inst':instnames.index(instname)}})
            tracks.m_basicdata_inst(cvpj_l, instname, s_inst_name, s_inst_color, None, None)

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True
        
        cvpj_l['timesig_numerator'] = 4
        cvpj_l['timesig_denominator'] = 4
        cvpj_l['bpm'] = smp_tempo
        return json.dumps(cvpj_l)

