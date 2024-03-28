# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from functions import placement
import copy

from objects_convproj import stretch
from objects_convproj import visual

class cvpj_placements_audio:
    __slots__ = ['data']
    def __init__(self):
        self.data = []

    def __iter__(self):
        for x in self.data: yield x

    def add(self):
        pl_obj = cvpj_placement_audio()
        self.data.append(pl_obj)
        return pl_obj

    def sort(self):
        ta_bsort = {}
        ta_sorted = {}
        new_a = []
        for n in self.data:
            if n.position not in ta_bsort: ta_bsort[n.position] = []
            ta_bsort[n.position].append(n)
        ta_sorted = dict(sorted(ta_bsort.items(), key=lambda item: item[0]))
        for p in ta_sorted:
            for note in ta_sorted[p]: new_a.append(note)
        self.data = new_a

    def get_start(self):
        start_final = 100000000000000000
        for pl in self.data:
            pl_start = pl.position
            if pl_start < start_final: start_final = pl_start
        return start_final

    def get_dur(self):
        duration_final = 0
        for pl in self.data:
            pl_end = pl.position+pl.duration
            if duration_final < pl_end: duration_final = pl_end
        return duration_final

    def change_seconds(self, is_seconds, bpm):
        for pl in self.data: pl.change_seconds(is_seconds, bpm)

    def remove_loops(self, out__placement_loop):
        new_data = []
        for notespl_obj in self.data: 
            if notespl_obj.cut_type in ['loop', 'loop_off', 'loop_adv'] and notespl_obj.cut_type not in out__placement_loop:
                loop_start, loop_loopstart, loop_loopend = notespl_obj.get_loop_data()
                for cutpoint in xtramath.cutloop(notespl_obj.position, notespl_obj.duration, loop_start, loop_loopstart, loop_loopend):
                    cutplpl_obj = copy.deepcopy(notespl_obj)
                    cutplpl_obj.position = cutpoint[0]
                    cutplpl_obj.duration = cutpoint[1]
                    cutplpl_obj.cut_type = 'cut'
                    cutplpl_obj.cut_data = {'start': cutpoint[2]}
                    new_data.append(cutplpl_obj)
            else: new_data.append(notespl_obj)
        self.data = new_data

class cvpj_placement_audio:
    __slots__ = ['position','duration','cut_type','cut_data','muted','pan','vol','pitch','visual','sampleref','audiomod','fxrack_channel','stretch','fade_in','fade_out']

    def __init__(self):
        self.position = 0
        self.duration = 0
        self.cut_type = 'none'
        self.cut_data = {}
        self.muted = False
        self.pan = 0
        self.vol = 1
        self.pitch = 0
        self.visual = visual.cvpj_visual()
        self.sampleref = ''
        self.audiomod = {}
        self.fxrack_channel = -1
        self.stretch = stretch.cvpj_stretch()
        self.fade_in = {}
        self.fade_out = {}

    def cut_loop_data(self, start, loopstart, loopend):
        self.cut_type, self.cut_data = placement.cutloopdata(start, loopstart, loopend)

    def get_loop_data(self):
        loop_start = self.cut_data['start'] if 'start' in self.cut_data else 0
        loop_loopstart = self.cut_data['loopstart'] if 'loopstart' in self.cut_data else 0
        loop_loopend = self.cut_data['loopend'] if 'loopend' in self.cut_data else self.duration
        return loop_start, loop_loopstart, loop_loopend

    def change_seconds(self, is_seconds, bpm):
        self.position = xtramath.step2sec(self.position, bpm) if is_seconds else xtramath.sec2step(self.position, bpm)
        self.duration = xtramath.step2sec(self.duration, bpm) if is_seconds else xtramath.sec2step(self.duration, bpm)

    def changestretch(self, convproj_obj, target, tempo):
        pos_offset, cut_offset, finalspeed = self.stretch.changestretch(convproj_obj.samplerefs, self.sampleref, target, tempo, convproj_obj.time_ppq)

        if self.cut_type == 'cut':
            if 'start' in self.cut_data: self.cut_data['start'] += cut_offset
        if self.cut_type == 'loop':
            if 'loopend' in self.cut_data: self.cut_data['loopend'] += cut_offset
            if 'loopstart' in self.cut_data: self.cut_data['loopstart'] += cut_offset

        if 'start' not in self.cut_data: self.cut_data['start'] = 0
        self.cut_data['start'] += abs(min(0, pos_offset))
        self.duration -= max(0, pos_offset)
        self.position += max(pos_offset, 0)

class cvpj_placements_nested_audio:
    __slots__ = ['data']
    def __init__(self):
        self.data = []

    def __iter__(self):
        for x in self.data: yield x

    def add(self):
        pl_obj = cvpj_placement_nested_audio()
        self.data.append(pl_obj)
        return pl_obj

    def change_seconds(self, is_seconds, bpm):
        for pl in self.data: pl.change_seconds(is_seconds, bpm)

class cvpj_placement_nested_audio:
    __slots__ = ['position','duration','cut_type','cut_data','visual','events']

    def __init__(self):
        self.position = 0
        self.duration = 0
        self.cut_type = 'none'
        self.cut_data = {}
        self.visual = visual.cvpj_visual()
        self.events = []

    def add(self):
        apl_obj = cvpj_placement_audio()
        self.events.append(apl_obj)
        return apl_obj

    def change_seconds(self, is_seconds, bpm):
        self.position = xtramath.step2sec(self.position, bpm) if is_seconds else xtramath.sec2step(self.position, bpm)
        self.duration = xtramath.step2sec(self.duration, bpm) if is_seconds else xtramath.sec2step(self.duration, bpm)