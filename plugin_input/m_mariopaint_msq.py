# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import dv_dataset
from objects import convproj
from functions import xtramath
import io
import json
import plugin_input

instnames = ['mario','toad','yoshi','star','flower','gameboy','dog','cat','pig','swan','face','plane','boat','car','heart','coin','plant','shyguy','ghost']
keytable =  [19, 17, 16, 14, 12, 11, 9, 7, 5, 4, 2, 0, -1]

def readpart(notelist_obj, msq_score_str, n_pos, n_len):
    msq_notes = {}
    char1 = int(msq_score_str.read(1), 16)
    char2 = int(msq_score_str.read(1), 16)
    char3 = int(msq_score_str.read(1), 16)
    if char1 == 0:
        if char2 == 0: numnotes = 0 if char3 == 0 else 1
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
        notelist_obj.add_m(instnames[msq_notes[msq_note]-1], n_pos, n_len, keytable[msq_note-1], 1, {})

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
    def parse(self, convproj_obj, input_file, extra_param):

        # ---------- CVPJ Start ----------
        convproj_obj.type = 'm'
        convproj_obj.set_timings(4, False)
 
        playlist_obj = convproj_obj.add_playlist(0, 0, False)
        cvpj_placement = playlist_obj.placements.add_notes()

        # ---------- Parse ----------
        msq_values = {}
        f_msq = open(input_file, 'r')
        lines_msq = f_msq.readlines()
        for line in lines_msq:
            msq_name, fmf_val = line.rstrip().split('=')
            msq_values[msq_name] = fmf_val

        if 'TIME44' in msq_values: msq_measure = 4 if msq_values['TIME44'] == 'TRUE' else 2
        else: msq_measure = 4

        msq_tempo = int(msq_values['TEMPO']) if 'TEMPO' in msq_values else 180
        msq_score = msq_values['SCORE']
        msq_score_size = len(msq_score)
        msq_score_str = io.StringIO(msq_score)

        # ---------- CVPJ ----------
        dataset = dv_dataset.dataset('./data_dset/mariopaint.dset')
        dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')

        msq_tempo, notelen = xtramath.get_lower_tempo(msq_tempo, 4, 180)
        curpos = 0
        while msq_score_str.tell() < msq_score_size:
            readpart(cvpj_placement.notelist, msq_score_str, curpos, notelen)
            curpos += notelen

        for instname in instnames: convproj_obj.add_instrument_from_dset(instname, instname, dataset, dataset_midi, instname, None, None)
        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_singlenotelistcut')
        convproj_obj.timesig = [msq_measure,4]
        convproj_obj.params.add('bpm', msq_tempo, 'float')
        
        cvpj_placement.duration = cvpj_placement.notelist.get_dur()
