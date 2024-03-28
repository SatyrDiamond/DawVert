# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import convproj
from objects import dv_dataset
from functions import xtramath
import json
import plugin_input
import xml.etree.ElementTree as ET

instnames = ['mario','toad','yoshi','star','flower','gameboy','dog','cat','pig','swan','face','plane','boat','car','heart','coin','plant','shyguy','ghost']
notekeys = ['A','B','C','D','E','F','G','H','a','b','c','d','e','f','g','h','i']
keytable = [-3 ,-1 ,0  ,2  ,4  ,5  ,7  ,9  ,11 ,12 ,14 ,16 ,17 ,19 ,21 ,23 ,24 ]

def addnotes(notelist_obj, n_pos, n_len, inst, txt, chordvolume):
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
        notelist_obj.add_m(inst, n_pos, n_len, outnote, chordvolume, {})
    noteoffset = 0

def add_tempo_point(convproj_obj, position, value, notelen): 
    autopl_obj = convproj_obj.automation.add_pl_points(['main','bpm'], 'float')
    autopl_obj.position = position
    autopl_obj.duration = notelen
    autopoint_obj = autopl_obj.data.add_point()
    autopoint_obj.value = value/notelen

class input_mariopaint_mss(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mariopaint_mss'
    def gettype(self): return 'm'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.file_ext = 'mss'
        dawinfo_obj.name = 'Advanced Mario Sequencer'
        dawinfo_obj.track_lanes = True
        dawinfo_obj.track_nopl = True
        dawinfo_obj.plugin_included = ['midi']
    def supported_autodetect(self): return True
    def detect(self, input_file):
        output = False
        try:
            tree = ET.parse(input_file)
            root = tree.getroot()
            if root.tag == "MarioSequencerSong": output = True
        except ET.ParseError: output = False
        return output
    def parse(self, convproj_obj, input_file, dv_config):
        
        # ---------- CVPJ Start ----------
        convproj_obj.type = 'm'
        convproj_obj.set_timings(4, False)
 
        playlist_obj = convproj_obj.add_playlist(0, 0, False)

        # ---------- File ----------
        tree = ET.parse(input_file)
        root = tree.getroot()

        # ---------- Parse & Notelist----------
        mss_measure = int(root.get('measure'))
        chords = tree.findall('chord')
        mss_tempo, notelen = xtramath.get_lower_tempo(int(root.get('tempo')), 4, 180)
        duration = 0
        curpos = 0
        add_tempo_point(convproj_obj, 0, mss_tempo, notelen)
        for chord in chords:
            chordvolume = int(chord.get('volume'))/8
            for instname in instnames:
                x_chord = chord.find(instname)
                duration = curpos
                if x_chord != None: 
                    addnotes(playlist_obj.placements.notelist, curpos, notelen, instname, x_chord.text, chordvolume)
            if chord.find('bookmark') != None: 
                timemarker_obj = convproj_obj.add_timemarker()
                timemarker_obj.visual.name = 'Bookmark'
                timemarker_obj.type = 'text'
                timemarker_obj.position = curpos
            t_sm = chord.find('speedmark')
            if t_sm != None: 
                t_sm_tempo = int(t_sm.get('tempo'))
                add_tempo_point(convproj_obj, curpos, t_sm_tempo, notelen)
            curpos += notelen

        # ---------- CVPJ ----------
        dataset = dv_dataset.dataset('./data_dset/mariopaint.dset')
        dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')

        for instname in instnames: 
            convproj_obj.add_instrument_from_dset(instname, instname, dataset, dataset_midi, instname, None, None)
        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_singlenotelistcut')
        convproj_obj.timesig = [mss_measure,4]
        convproj_obj.params.add('bpm', mss_tempo, 'float')
