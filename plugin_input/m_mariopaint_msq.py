# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
from functions import idvals
from functions import tracks
import plugin_input
import json
import io

instnames = ['mario','toad','yoshi','star','flower','gameboy','dog','cat','pig','swan','face','plane','boat','car','heart','coin','plant','shyguy','ghost']
keytable =  [19, 17, 16, 14, 12, 11, 9, 7, 5, 4, 2, 0, -1]

def readpart(msq_score_str, n_pos, n_len):
    global notelist
    numnotes = 3

    msq_notes = {}
    char1 = int(msq_score_str.read(1), 16)
    char2 = int(msq_score_str.read(1), 16)
    char3 = int(msq_score_str.read(1), 16)
    #print(char1, char2, char3)
    if char1 == 0 and char2 == 0 and char3 == 0: numnotes = 0
    if char1 == 0 and char2 == 0 and char3 != 0: numnotes = 1
    if char1 == 0 and char2 != 0 and char3 != 0: numnotes = 2
    if char1 != 0 and char2 != 0 and char3 != 0: numnotes = 3

    if numnotes == 1:
        msq_notes[char3] = int(msq_score_str.read(1), 16)

    if numnotes == 2:
        msq_notes[char2] = char3
        t_note = int(msq_score_str.read(1), 16)
        t_inst = int(msq_score_str.read(1), 16)
        msq_notes[t_note] = t_inst

    if numnotes == 3:
        msq_notes[char1] = char2
        t_inst = int(msq_score_str.read(1), 16)
        msq_notes[char3] = t_inst
        t_note = int(msq_score_str.read(1), 16)
        t_inst = int(msq_score_str.read(1), 16)
        msq_notes[t_note] = t_inst

    for msq_note in msq_notes:
        k_inst = instnames[msq_notes[msq_note]-1]
        k_key = keytable[msq_note-1]
        notedata = {}
        notedata['position'] = n_pos
        notedata['key'] = k_key
        notedata['vol'] = 1.0
        notedata['duration'] = n_len
        notedata['instrument'] = k_inst
        notelist.append(notedata)

class input_mariopaint_msq(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mariopaint_msq'
    def getname(self): return 'MarioSequencer'
    def gettype(self): return 'm'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global notelist

        idvals_mariopaint_inst = idvals.parse_idvalscsv('idvals/mariopaint_inst.csv')

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_playlist = {}
        
        notelist = []

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

        notelen = 4

        while msq_tempo > 180:
            msq_tempo = msq_tempo/2
            notelen = notelen/2

        msq_score = msq_values['SCORE']
        msq_score_size = len(msq_score)
        msq_score_str = io.StringIO(msq_score)

        curpos = 0
        while msq_score_str.tell() < msq_score_size:
            readpart(msq_score_str, curpos, notelen)
            curpos += notelen

        tracks.m_playlist_pl(cvpj_l, 1, None, None, [{'type': "instruments", 'position': 0, 'duration': curpos+1, 'notelist': notelist}])

        for instname in instnames:
            s_inst_name = idvals.get_idval(idvals_mariopaint_inst, str(instname), 'name')
            s_inst_color = idvals.get_idval(idvals_mariopaint_inst, str(instname), 'color')
            if s_inst_color != None: s_inst_color = colors.moregray(s_inst_color)

            tracks.m_addinst(cvpj_l, instname, {'plugin': 'general-midi', 'plugindata': {'bank':0, 'inst':instnames.index(instname)}})
            tracks.m_addinst_data(cvpj_l, instname, s_inst_name, s_inst_color, None, None)

        cvpj_l['do_addwrap'] = True
        cvpj_l['do_singlenotelistcut'] = True

        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        cvpj_l['use_placements_notes'] = False
        
        cvpj_l['timesig_numerator'] = msq_measure
        cvpj_l['timesig_denominator'] = 4
        
        cvpj_l['bpm'] = msq_tempo
        return json.dumps(cvpj_l)

