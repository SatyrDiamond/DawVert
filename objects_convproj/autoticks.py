# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath

class cvpj_autoticks:
    __slots__ = ['val_type','time_ppq','time_float','points']

    def __init__(self, time_ppq, time_float, val_type):
        self.val_type = val_type
        self.time_ppq = time_ppq
        self.time_float = time_float
        self.points = {}

    def iter(self):
        for p, v in self.points.items(): 
            yield p, v

    def add_point(self, p_pos, p_val):
        self.points[p_pos] = p_val


    def change_timings(self, time_ppq, time_float):
        r = []
        for p, v in self.points.items(): r.append([p, v])
        for t in r: t[0] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, t[0])
        self.points = {}
        for t in r: self.points[t[0]] = t[1]
        self.time_ppq = time_ppq
        self.time_float = time_float

    def get_dur(self):
        out_dur = 0
        for p in self.points:
            if out_dur < p: out_dur = p
        return out_dur

    def get_durpos(self):
        out_dur = 0
        out_pos = 10000000000
        for p in self.points:
            if out_dur < p: out_dur = p
            if out_pos > p: out_pos = p
        return out_pos, out_dur

    def move(self, pos):
        for p in self.points: self.points[p] += pos

    def addmul(self, addval, mulval):
        for p in self.points: self.points[p] = (self.points[p]+addval)*mulval

    def change_valrange(self, old_min, old_max, new_min, new_max):
        for p in self.points: self.points[p] = xtramath.between_from_one(new_min, new_max, xtramath.between_to_one(old_min, old_max, self.points[p]))

    def to_one(self, i_min, i_max):
        for p in self.points: self.points[p] = xtramath.between_to_one(i_min, i_max, self.points[p])

    def from_one(self, i_min, i_max):
        for p in self.points: self.points[p] = xtramath.between_from_one(i_min, i_max, self.points[p])

    def check(self):
        return len(self.points) != 0

    def optimize(self):
        prevval = None
        norepeats = {}
        for ctrlpos in self.points:
            ctrlval = self.points[ctrlpos]
            if prevval == None: norepeats[ctrlpos] = ctrlval
            elif prevval != ctrlval: norepeats[ctrlpos] = ctrlval
            prevval = ctrlval
        self.points = norepeats

    def get_paramval(self, before_pos, def_val):
        ba_autos = [{},{}]
        for pos in self.points:
            if pos < before_pos: ba_autos[0][pos] = self.points[pos]
            else: ba_autos[1][pos] = self.points[pos]
        out = def_val
        poslist = [x for x in ba_autos[0]]
        if poslist: out = ba_autos[0][max(poslist)]
        return out

    def to_cvpj(self):
        out_cvpj = []
        for pos in self.points:
            pointJ = {}
            pointJ['position'] = (pos/self.time_ppq)*4
            pointJ['value'] = self.points[pos]
            pointJ['type'] = 'instant'
            pointJ['tension'] = 0
            out_cvpj.append(pointJ)
        return out_cvpj
