# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
from functions import idvals
from functions import tracks
from functions import song
from functions import note_data
from functions import placement_data
import plugin_input
import json
import xml.etree.ElementTree as ET

instnames = ['mario','toad','yoshi','star','flower','gameboy','dog','cat','pig','swan','face','plane','boat','car','heart','coin','plant','shyguy','ghost']
notekeys = ['A','B','C','D','E','F','G','H','a','b','c','d','e','f','g','h','i']
keytable = [-3 ,-1 ,0  ,2  ,4  ,5  ,7  ,9  ,11 ,12 ,14 ,16 ,17 ,19 ,21 ,23 ,24 ]

def addnotes(n_pos, n_len, inst, txt, chordvolume):
    noteoffset = 0
    notetable = []

    notestr = ""
    for noteletter in txt:
        notestr += noteletter
        if noteletter != '-' and noteletter != '+':
            if len(notestr) == 1: notestr = ' '+notestr
            notetable.append(notestr)
            notestr = ""

    for s_note in notetable:
        symbol = s_note[0]
        outnote = keytable[notekeys.index(s_note[1])]
        if symbol == '-': outnote -= 1
        if symbol == '+': outnote += 1
        cvpj_notelist.append(note_data.mx_makenote(inst, n_pos, n_len, outnote, chordvolume, None))

    noteoffset = 0


class input_mariopaint_mss(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mariopaint_mss'
    def getname(self): return 'Advanced Mario Sequencer'
    def gettype(self): return 'm'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': True,
        'placement_cut': False,
        'placement_loop': False,
        'no_pl_auto': False,
        'no_placements': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        output = False
        try:
            tree = ET.parse(input_file)
            root = tree.getroot()
            if root.tag == "MarioSequencerSong": output = True
        except ET.ParseError: output = False
        return output
    def parse(self, input_file, extra_param):
        global cvpj_notelist
        tree = ET.parse(input_file)
        root = tree.getroot()

        idvals_mariopaint_inst = idvals.parse_idvalscsv('idvals/mariopaint_inst.csv')

        cvpj_l = {}

        cvpj_notelist = []

        mss_measure = int(root.get('measure'))
        chords = tree.findall('chord')

        mss_tempo, notelen = song.get_lower_tempo(int(root.get('tempo')), 4, 180)

        auto_tempo = []
        tempo_placement = {"position": 0, 'duration': notelen}
        tempo_placement['points'] = [{"position": 0, "value": mss_tempo}]
        auto_tempo.append(tempo_placement)

        duration = 0
        curpos = 0
        for chord in chords:
            chordvolume = int(chord.get('volume'))/8
            for instname in instnames:
                x_chord = chord.find(instname)
                duration = curpos
                if x_chord != None: addnotes(curpos, notelen, instname, x_chord.text, chordvolume)
            if chord.find('bookmark') != None: song.add_timemarker_text(cvpj_l, curpos, 'Bookmark')
            t_sm = chord.find('speedmark')
            if t_sm != None: 
                t_sm_tempo = int(t_sm.get('tempo'))
                tempo_placement = {'position': curpos, 'duration': notelen}
                tempo_placement['points'] = [{"position": 0, "value": t_sm_tempo*(notelen/4)}]
                auto_tempo.append(tempo_placement)
            curpos += notelen

        tracks.m_playlist_pl(cvpj_l, 1, None, None, placement_data.nl2pl(cvpj_notelist))

        for instname in instnames:
            s_inst_name = idvals.get_idval(idvals_mariopaint_inst, str(instname), 'name')
            s_inst_color = idvals.get_idval(idvals_mariopaint_inst, str(instname), 'color')
            if s_inst_color != None: s_inst_color = colors.moregray(s_inst_color)
            tracks.m_create_inst(cvpj_l, instname, {'plugin': 'general-midi', 'plugindata': {'bank':0, 'inst':instnames.index(instname)}})
            tracks.m_basicdata_inst(cvpj_l, instname, s_inst_name, s_inst_color, None, None)

        cvpj_l['automation'] = {'main': {'bpm': auto_tempo}}

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True

        cvpj_l['timesig_numerator'] = mss_measure
        cvpj_l['timesig_denominator'] = 4
        cvpj_l['bpm'] = mss_tempo
        return json.dumps(cvpj_l)

