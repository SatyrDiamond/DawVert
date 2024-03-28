# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from functions import placement
from objects_convproj import autopoints
from objects_convproj import visual

class cvpj_placements_autopoints:
    __slots__ = ['data','type','time_ppq','time_float','val_type']
    def __init__(self, time_ppq, time_float, val_type):
        self.time_ppq = time_ppq
        self.time_float = time_float
        self.val_type = val_type
        self.data = []

    def add(self, val_type):
        placement_obj = cvpj_placement_autopoints(self.time_ppq, self.time_float, self.val_type)
        self.data.append(placement_obj)
        return placement_obj

    def change_timings(self, time_ppq, time_float):
        for pl in self.data:
            pl.position = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.position)
            pl.duration = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.duration)
            pl.data.change_timings(time_ppq, time_float)

        self.time_ppq = time_ppq
        self.time_float = time_float

    def addmul(self, addval, mulval):
        for pl in self.data: pl.data.addmul(addval, mulval)

    def to_one(self, i_min, i_max):
        for pl in self.data: pl.data.to_one(i_min, i_max)

    def from_one(self, i_min, i_max):
        for pl in self.data: pl.data.from_one(i_min, i_max)

    def funcval(self, i_function):
        for pl in self.data: pl.data.funcval(i_function)

    def pow(self, i_val):
        for pl in self.data: pl.data.pow(i_val)

    def pow_r(self, i_val):
        for pl in self.data: pl.data.pow_r(i_val)

    def log(self, i_val):
        for pl in self.data: pl.data.log(i_val)

    def log_r(self, i_val):
        for pl in self.data: pl.data.log_r(i_val)

    def iter(self):
        for x in self.data: yield x

    def check(self):
        return len(self.data) != 0

    def remove_cut(self):
        for x in self.data: 
            if x.cut_type == 'cut':
                c_start = x.cut_data['start'] if 'start' in x.cut_data else 0
                x.data.edit_trimmove(c_start, x.duration)

    def remove_unused(self):
        for x in self.data: 
            if x.cut_type == 'cut':
                c_start = x.cut_data['start'] if 'start' in x.cut_data else 0
                x.data.edit_trimmove(c_start, x.duration)
            else:
                x.data.edit_trimmove(0, x.duration)

class cvpj_placement_autopoints:
    __slots__ = ['position','duration','cut_type','cut_data','muted','visual','data']

    def __init__(self, time_ppq, time_float, val_type):
        self.position = 0
        self.duration = 0
        self.cut_type = 'none'
        self.cut_data = {}
        self.data = autopoints.cvpj_autopoints(time_ppq, time_float, val_type)
        self.muted = False
        self.visual = visual.cvpj_visual()

    def cut_loop_data(self, start, loopstart, loopend):
        self.cut_type, self.cut_data = placement.cutloopdata(start, loopstart, loopend)

    def remove_cut(self):
        if self.cut_type == 'cut':
            c_start = self.cut_data['start'] if 'start' in self.cut_data else 0
            self.data.edit_trimmove(c_start/4, self.duration)

