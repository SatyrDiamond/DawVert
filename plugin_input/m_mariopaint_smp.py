# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import convproj
from objects import dv_dataset
from functions import xtramath
import io
import json
import plugin_input

instnames = ['MARIO','MUSHROOM','YOSHI','STAR','FLOWER','GAMEBOY','DOG','CAT','PIG','SWAN','FACE','PLANE','BOAT','CAR','HEART','PIRANHA','COIN','SHYGUY','BOO','LUIGI','PEACH','FEATHER','BULLETBILL','GOOMBA','BOBOMB','SPINY','FRUIT','ONEUP','MOON','EGG','GNOME']
smpnames = {'MARIO': "mario", 'MUSHROOM': "toad", 'YOSHI': "yoshi", 'STAR': "star", 'FLOWER': "flower", 'GAMEBOY': "gameboy", 'DOG': "dog", 'CAT': "cat", 'PIG': "pig", 'SWAN': "swan", 'FACE': "face", 'PLANE': "plane", 'BOAT': "boat", 'CAR': "car", 'HEART': "heart", 'PIRANHA': "plant", 'COIN': "coin", 'SHYGUY': "shyguy", 'BOO': "ghost", 'LUIGI': "luigi", 'PEACH': "peach", 'FEATHER': "feather", 'BULLETBILL': "bulletbill", 'GOOMBA': "goomba", 'BOBOMB': "bobomb", 'SPINY': "spiny", 'FRUIT': "fruit", 'ONEUP': "oneup", 'MOON': "moon", 'EGG': "egg", 'GNOME': "gnome"}
keytable = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

def makenote(notelist_obj, n_pos, notes, vol, notesize):
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

        if out_mode == 0: notelist_obj.add_m(notesplit[0], n_pos*notesize, notesize, out_key+out_oct*12+out_offset, vol/100, {})

class input_mariopaint_smp(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mariopaint_smp'
    def getname(self): return 'Super Mario Paint'
    def gettype(self): return 'm'
    def getdawcapabilities(self):
        return {'track_lanes': True, 'track_nopl': True}
    def supported_autodetect(self): return False
    def parse(self, convproj_obj, input_file, extra_param):

        # ---------- CVPJ Start ----------
        convproj_obj.type = 'm'
        convproj_obj.set_timings(4, False)
 
        playlist_obj = convproj_obj.add_playlist(0, 0, False)
        placement_obj = playlist_obj.placements.add_notes()

        # ---------- Parse ----------
        smp_values = {}
        linecount = 0
        f_smp = open(input_file, 'r')
        smp_tempo = 140
        notelen = 1
        lines_smp = f_smp.readlines()
        for line in lines_smp:
            if linecount == 0: 
                t_smp_values = line.rstrip().split(', ')
                for t_smp_value in t_smp_values:
                    smp_nameval = t_smp_value.split(':')
                    smp_values[smp_nameval[0]] = smp_nameval[1]
                    if smp_nameval[0] == "TEMPO": smp_tempo = float(smp_nameval[1])
                    else: smp_tempo = 200
                smp_tempo, notelen = xtramath.get_lower_tempo(smp_tempo, 2, 180)
            else: 
                s_point = line.rstrip().split(',')
                s_data = s_point[1:]
                s_pos = s_point[:1][0].split(':')
                s_pos_out = ((int(s_pos[0])-1)*4) + int(s_pos[1])
                s_notes = s_data[:-1]
                s_vol = int(s_data[-1:][0].split(':')[1])
                makenote(placement_obj.notelist, s_pos_out, s_notes, s_vol, notelen)
            linecount += 1

        # ---------- CVPJ ----------
        dataset = dv_dataset.dataset('./data_dset/mariopaint.dset')
        dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')

        for instname in instnames: 
            convproj_obj.add_instrument_from_dset(instname, instname, dataset, dataset_midi, smpnames[instname], None, None)
        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_singlenotelistcut')
        convproj_obj.params.add('bpm', smp_tempo, 'float')
