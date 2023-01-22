# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
import plugin_input
import json
import xml.etree.ElementTree as ET

instnames = ['mario','toad','yoshi','star','flower','gameboy','dog','cat','pig','swan','face','plane','boat','car','heart','coin','plant','shyguy','ghost']
notekeys = ['A','B','C','D','E','F','G','H','a','b','c','d','e','f','g','h','i']
keytable = [-3 ,-1 ,0  ,2  ,4  ,5  ,7  ,9  ,11 ,12 ,14 ,16 ,17 ,19 ,21 ,23 ,24 ]

out_names = {'mario': 'Piano (Mario)',
'toad': 'Tom (Mushroom)',
'yoshi': 'SMW Yoshi',
'star': 'Xylophone (Star)',
'flower': 'Trumpet (Flower)',
'gameboy': 'Square Wave (GameBoy)',
'dog': 'Bark (Dog)',
'cat': 'Meow (Cat)',
'pig': 'Oink (Pig)',
'swan': 'String Hit (Swan)',
'face': 'Face',
'plane': 'Acoustic Guitar (Plane)',
'boat': 'Hat (Boat)',
'car': 'Organ (Car)',
'heart': 'Bass Guitar (Heart)',
'coin': 'Piano (Coin)',
'plant': 'Distorted Guitar (Plant)',
'shyguy': 'String (Shy Guy)',
'ghost': 'Harp (Ghost)'}

out_colors = {'mario': [0.92, 0.77, 0.56],
'toad': [0.98, 0.00, 0.00],
'yoshi': [0.00, 0.98, 0.02],
'star': [0.97, 0.98, 0.00],
'flower': [0.96, 0.50, 0.00],
'gameboy': [0.76, 0.76, 0.76],
'dog': [1.00, 1.00, 1.00],
'cat': [0.98, 0.75, 0.51],
'pig': [0.96, 0.75, 0.52],
'swan': [0.75, 0.75, 0.76],
'face': [0.98, 0.76, 0.51],
'plane': [1.00, 1.00, 1.00],
'boat': [0.96, 0.00, 0.01],
'car': [0.88, 0.53, 0.17],
'heart': [0.96, 0.00, 0.00],
'coin': [0.93, 0.75, 0.20],
'plant': [0.73, 0.00, 0.01],
'shyguy': [0.64, 0.00, 0.01],
'ghost': [0.57, 0.96, 0.99]}

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
        notedata = {}
        notedata['position'] = n_pos
        notedata['key'] = outnote
        notedata['vol'] = chordvolume
        notedata['duration'] = n_len
        notedata['instrument'] = inst
        notelist.append(notedata)

    noteoffset = 0


class input_mariopaint_mss(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mariopaint_mss'
    def getname(self): return 'Advanced Mario Sequencer'
    def gettype(self): return 'm'
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
        global notelist
        tree = ET.parse(input_file)
        root = tree.getroot()

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_timemarkers = []
        cvpj_l_playlist = {}
        notelist = []

        mss_tempo = int(root.get('tempo'))
        mss_measure = int(root.get('measure'))

        chords = tree.findall('chord')
        notelen = 4

        if mss_tempo > 200:
            mss_tempo = mss_tempo/2
            notelen = notelen/2

        auto_tempo = []

        tempo_placement = {"position": 0}
        tempo_placement['duration'] = notelen
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
            t_bm = chord.find('bookmark')
            if t_bm != None: cvpj_l_timemarkers.append({'position':curpos, 'name': 'Bookmark'})
            t_sm = chord.find('speedmark')
            if t_sm != None: 
                t_sm_tempo = int(t_sm.get('tempo'))
                tempo_placement = {"position": curpos}
                tempo_placement['duration'] = notelen
                tempo_placement['points'] = [{"position": 0, "value": t_sm_tempo*(notelen/4)}]
                auto_tempo.append(tempo_placement)
            curpos += notelen

        l_placement = {}
        l_placement['type'] = "instruments"
        l_placement['position'] = 0
        l_placement['duration'] = duration
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

        placements_auto = {}
        placements_auto['bpm'] = auto_tempo
        cvpj_l['use_fxrack'] = False
        cvpj_l['placements_auto_main'] = placements_auto
        cvpj_l['timesig_numerator'] = mss_measure
        cvpj_l['timesig_denominator'] = 4
        cvpj_l['timemarkers'] = cvpj_l_timemarkers
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = mss_tempo
        return json.dumps(cvpj_l)

