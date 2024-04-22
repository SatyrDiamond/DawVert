# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from functions import placement
from objects_convproj import time
import copy

class cvpj_placements_index:
    __slots__ = ['data']
    def __init__(self):
        self.data = []

    def __iter__(self):
        for x in self.data: yield x

    def add(self):
        pl_obj = cvpj_placement_index()
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

class cvpj_placement_index:
    __slots__ = ['position','duration','position_real','duration_real','cut_type','cut_data','muted','visual','fromindex']

    def __init__(self):
        self.position = 0
        self.duration = 0
        self.position_real = None
        self.duration_real = None
        self.cut_type = 'none'
        self.cut_data = {}
        self.fromindex = ''
        self.muted = False

    def cut_loop_data(self, start, loopstart, loopend):
        self.cut_type, self.cut_data = placement.cutloopdata(start, loopstart, loopend)

    def get_loop_data(self):
        loop_start = self.cut_data['start'] if 'start' in self.cut_data else 0
        loop_loopstart = self.cut_data['loopstart'] if 'loopstart' in self.cut_data else 0
        loop_loopend = self.cut_data['loopend'] if 'loopend' in self.cut_data else x.duration
        return loop_start, loop_loopstart, loop_loopend
