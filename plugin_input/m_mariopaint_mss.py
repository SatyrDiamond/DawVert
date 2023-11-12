# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
from functions import data_dataset
from functions import note_data
from functions import placement_data
from functions import plugins
from functions import song
from functions_tracks import auto_data
from functions_tracks import tracks_m
import json
import plugin_input
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

def add_tempo_point(cvpj_l, position, value, notelen): 
    tempo_placement = {'position': position, 'duration': notelen}
    tempo_placement['points'] = [{"position": 0, "value": value*(notelen/4)}]
    auto_data.add_pl(cvpj_l, 'float', ['main', 'bpm'], tempo_placement)

class input_mariopaint_mss(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mariopaint_mss'
    def getname(self): return 'Advanced Mario Sequencer'
    def gettype(self): return 'm'
    def getdawcapabilities(self): 
        return {'track_lanes': True, 'track_nopl': True}
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
        cvpj_l = {}
        cvpj_notelist = []

        dataset = data_dataset.dataset('./data_dset/onlineseq.dset')
        dataset_midi = data_dataset.dataset('./data_dset/midi.dset')

        mss_measure = int(root.get('measure'))
        chords = tree.findall('chord')
        mss_tempo, notelen = song.get_lower_tempo(int(root.get('tempo')), 4, 180)
        duration = 0
        curpos = 0
        add_tempo_point(cvpj_l, 0, mss_tempo, notelen)
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
                add_tempo_point(cvpj_l, curpos, t_sm_tempo, notelen)
            curpos += notelen

        tracks_m.playlist_add(cvpj_l, 1)
        tracks_m.add_pl(cvpj_l, 1, 'notes', placement_data.nl2pl(cvpj_notelist))

        for instname in instnames:
            tracks_m.import_dset(cvpj_l, instname, instname, dataset, dataset_midi, None, None)

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True

        song.add_timesig(cvpj_l, mss_measure, 4)
        song.add_param(cvpj_l, 'bpm', mss_tempo)
        return json.dumps(cvpj_l)

