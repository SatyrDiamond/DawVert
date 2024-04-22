# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from functions import placement
from objects_convproj import autoticks
from objects_convproj import visual
from objects_convproj import time

class cvpj_placements_autoticks:
    __slots__ = ['data','type','time_ppq','time_float','val_type']
    def __init__(self, time_ppq, time_float, val_type):
        self.time_ppq = time_ppq
        self.time_float = time_float
        self.val_type = val_type
        self.data = []

    def add(self, val_type):
        placement_obj = cvpj_placement_autoticks(self.time_ppq, self.time_float, self.val_type)
        self.data.append(placement_obj)
        return placement_obj

    def change_timings(self, time_ppq, time_float):
        for pl in self.data:
            pl.position = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.position)
            pl.duration = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.duration)
            pl.data.change_timings(time_ppq, time_float)

        self.time_ppq = time_ppq
        self.time_float = time_float

    def calc(self, mathtype, val1, val2, val3, val4):
        for pl in self.data: pl.data.calc(mathtype, val1, val2, val3, val4)

    def funcval(self, i_function):
        for pl in self.data: pl.data.funcval(i_function)

    def iter(self):
        for x in self.data: yield x

    def check(self):
        return len(self.data) != 0

    def remove_cut(self):
        for x in self.data: 
            if x.cut_type == 'cut':
                c_start = x.cut_data['start'] if 'start' in x.cut_data else 0
                x.data.edit_trimmove(c_start, x.duration)

class cvpj_placement_autoticks:
    __slots__ = ['position','duration','position_real','duration_real','cut_type','cut_data','muted','visual','data']

    def __init__(self, time_ppq, time_float, val_type):
        self.position = 0
        self.duration = 0
        self.position_real = None
        self.duration_real = None
        self.cut_type = 'none'
        self.cut_data = {}
        self.data = autoticks.cvpj_autoticks(time_ppq, time_float, val_type)
        self.muted = False
        self.visual = visual.cvpj_visual()

    def cut_loop_data(self, start, loopstart, loopend):
        self.cut_type, self.cut_data = placement.cutloopdata(start, loopstart, loopend)

