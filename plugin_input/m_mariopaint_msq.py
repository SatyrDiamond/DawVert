# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
from functions import idvals
from functions import song
from functions import plugins
from functions import note_data
from functions import placement_data
from functions_tracks import tracks_m
import plugin_input
import json
import io

instnames = ['mario','toad','yoshi','star','flower','gameboy','dog','cat','pig','swan','face','plane','boat','car','heart','coin','plant','shyguy','ghost']
keytable =  [19, 17, 16, 14, 12, 11, 9, 7, 5, 4, 2, 0, -1]

def readpart(msq_score_str, n_pos, n_len):
    msq_notes = {}
    char1 = int(msq_score_str.read(1), 16)
    char2 = int(msq_score_str.read(1), 16)
    char3 = int(msq_score_str.read(1), 16)
    if char1 == 0:
        if char2 == 0:
            if char3 == 0: numnotes = 0
            else: numnotes = 1
        else: numnotes = 2
    else: numnotes = 3

    if numnotes == 1:
        msq_notes[char3] = int(msq_score_str.read(1), 16)

    if numnotes == 2:
        msq_notes[char2] = char3
        t_note = int(msq_score_str.read(1), 16)
        msq_notes[t_note] = int(msq_score_str.read(1), 16)

    if numnotes == 3:
        msq_notes[char1] = char2
        msq_notes[char3] = int(msq_score_str.read(1), 16)
        t_note = int(msq_score_str.read(1), 16)
        msq_notes[t_note] = int(msq_score_str.read(1), 16)

    for msq_note in msq_notes:
        cvpj_note = note_data.mx_makenote(instnames[msq_notes[msq_note]-1], n_pos, n_len, keytable[msq_note-1], None, None)
        cvpj_notelist.append(cvpj_note)

class input_mariopaint_msq(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mariopaint_msq'
    def getname(self): return 'MarioSequencer'
    def gettype(self): return 'm'
    def getdawcapabilities(self): 
        return {
        'track_lanes': True,
        'track_nopl': True
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global cvpj_notelist
        idvals_mariopaint_inst = idvals.parse_idvalscsv('data_idvals/mariopaint_inst.csv')
        cvpj_l = {}
        cvpj_notelist = []
        msq_values = {}
        f_msq = open(input_file, 'r')
        lines_msq = f_msq.readlines()
        for line in lines_msq:
            msq_name, fmf_val = line.rstrip().split('=')
            msq_values[msq_name] = fmf_val

        if 'TIME44' in msq_values:
            if msq_values['TIME44'] == 'TRUE': msq_measure = 4
            else: msq_measure = 2
        else: msq_measure = 4

        if 'TEMPO' in msq_values: msq_tempo = int(msq_values['TEMPO'])
        else: msq_tempo = 180

        msq_tempo, notelen = song.get_lower_tempo(msq_tempo, 4, 180)
        msq_score = msq_values['SCORE']
        msq_score_size = len(msq_score)
        msq_score_str = io.StringIO(msq_score)

        curpos = 0
        while msq_score_str.tell() < msq_score_size:
            readpart(msq_score_str, curpos, notelen)
            curpos += notelen

        tracks_m.playlist_add(cvpj_l, 1)
        tracks_m.add_pl(cvpj_l, 1, 'notes', placement_data.nl2pl(cvpj_notelist))

        for instname in instnames:
            s_inst_name = idvals.get_idval(idvals_mariopaint_inst, str(instname), 'name')
            s_inst_color = idvals.get_idval(idvals_mariopaint_inst, str(instname), 'color')
            if s_inst_color != None: s_inst_color = colors.moregray(s_inst_color)
            mpinstid = instnames.index(instname)
            plugins.add_plug_gm_midi(cvpj_l, instname, 0, mpinstid)
            tracks_m.inst_create(cvpj_l, instname)
            tracks_m.inst_visual(cvpj_l, instname, name=s_inst_name, color=s_inst_color)
            tracks_m.inst_pluginid(cvpj_l, instname, instname)
            tracks_m.inst_dataval_add(cvpj_l, instname, 'midi', 'output', {'program': mpinstid})

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True

        cvpj_l['timesig'] = [msq_measure, 4]
        
        song.add_param(cvpj_l, 'bpm', msq_tempo)
        return json.dumps(cvpj_l)

