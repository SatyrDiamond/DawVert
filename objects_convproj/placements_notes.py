# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from functions import placement
import copy

from objects_convproj import visual
from objects_convproj import notelist

class cvpj_placements_notes:
    __slots__ = ['data']
    def __init__(self):
        self.data = []

    def __iter__(self):
        for x in self.data: yield x

    def append(self, value):
        self.data.append(value)

    def check_overlap(self, start, end):
        for npl in self.data:
            if xtramath.overlap(start, start+end, npl.position, npl.position+npl.duration): return True
        return False

    def clear(self):
        self.data = []
        
    def add(self, time_ppq, time_float):
        pl_obj = cvpj_placement_notes(time_ppq, time_float)
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
            for x in ta_sorted[p]: new_a.append(x)
        self.data = new_a

    def get_dur(self):
        duration_final = 0
        for pl in self.data:
            if pl.duration == 0: pl.duration = pl.notelist.get_dur()
            pl_end = pl.position+pl.duration
            if duration_final < pl_end: duration_final = pl_end
        return duration_final

    def get_start(self):
        start_final = 100000000000000000
        for pl in self.data:
            pl_start = pl.position
            if pl_start < start_final: start_final = pl_start
        return start_final

    def change_seconds(self, is_seconds, bpm):
        for pl in self.data: 
            pl.position = xtramath.step2sec(pl.position, bpm) if is_seconds else xtramath.sec2step(pl.position, bpm)
            pl.duration = xtramath.step2sec(pl.duration, bpm) if is_seconds else xtramath.sec2step(pl.duration, bpm)

    def remove_cut(self):
        for x in self.data: 
            if x.cut_type == 'cut':
                c_start = x.cut_data['start'] if 'start' in x.cut_data else 0
                x.notelist.edit_trimmove(c_start, x.duration)

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

    def add_loops(self):
        old_data_notes = copy.deepcopy(self.data)
        new_data_notes = []
        prevpp = None
        for pl in old_data_notes:
            ipnl = False
            pl_data = pl.notelist
            if prevpp != None:
                if prevpp[0]==pl.position-pl.duration and prevpp[2]==pl_data and prevpp[1]==pl.duration and pl.cut_type=='none': 
                    ipnl = True
                    if pl.cut_type=='none':
                        new_data_notes[-1].cut_type = 'loop'
                        new_data_notes[-1].cut_data['loopend'] = pl.duration
                    new_data_notes[-1].duration += pl.duration
            if ipnl == False: 
                new_data_notes.append(pl)
            prevpp = [pl.position, pl.duration, pl_data] if pl.cut_type=='none' else None
        self.data = new_data_notes

class cvpj_placement_notes:
    __slots__ = ['position','duration','cut_type','cut_data','muted','visual','notelist','time_ppq','time_float']
    def __init__(self, time_ppq, time_float):
        self.position = 0
        self.duration = 0
        self.cut_type = 'none'
        self.cut_data = {}
        self.time_ppq = time_ppq
        self.time_float = time_float
        self.notelist = notelist.cvpj_notelist(time_ppq, time_float)
        self.muted = False
        self.visual = visual.cvpj_visual()

    def cut_loop_data(self, start, loopstart, loopend):
        self.cut_type, self.cut_data = placement.cutloopdata(start, loopstart, loopend)

    def get_loop_data(self):
        loop_start = self.cut_data['start'] if 'start' in self.cut_data else 0
        loop_loopstart = self.cut_data['loopstart'] if 'loopstart' in self.cut_data else 0
        loop_loopend = self.cut_data['loopend'] if 'loopend' in self.cut_data else x.duration
        return loop_start, loop_loopstart, loop_loopend

    def inst_split(self, splitted_pl):
        nl_splitted = self.notelist.inst_split()
        for inst_id, notelist_obj in nl_splitted.items():
            plb_obj = cvpj_placement_notes(self.time_ppq, self.time_float)
            plb_obj.position = self.position
            plb_obj.duration = self.duration
            plb_obj.cut_type = self.cut_type
            plb_obj.cut_data = self.cut_data
            plb_obj.time_ppq = self.time_ppq
            plb_obj.time_float = self.time_float
            plb_obj.notelist = notelist_obj
            plb_obj.muted = self.muted
            plb_obj.visual = self.visual
            if inst_id not in splitted_pl: splitted_pl[inst_id] = []
            splitted_pl[inst_id].append(plb_obj)

    def antiminus(self):
        loop_start, loop_loopstart, loop_loopend = self.get_loop_data()
        notepos = -min([x[0] for x in self.notelist.nl]+[0, loop_start, loop_loopstart])
        if notepos:
            self.notelist.edit_move_minus(notepos)
            loop_start += notepos
            loop_loopstart += notepos
            loop_loopend += notepos
            self.cut_loop_data(loop_start, loop_loopstart, loop_loopend)