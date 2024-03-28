# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
import math

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

    #def move(self, pos):
    #    for p in self.points: 
    #        self.points[p += pos] == self.points[p]

    def addmul(self, addval, mulval):
        for p in self.points: self.points[p] = (self.points[p]+addval)*mulval

    def change_valrange(self, old_min, old_max, new_min, new_max):
        for p in self.points: self.points[p] = xtramath.between_from_one(new_min, new_max, xtramath.between_to_one(old_min, old_max, self.points[p]))

    def to_one(self, i_min, i_max):
        for p in self.points: self.points[p] = xtramath.between_to_one(i_min, i_max, self.points[p])

    def from_one(self, i_min, i_max):
        for p in self.points: self.points[p] = xtramath.between_from_one(i_min, i_max, self.points[p])

    def funcval(self, i_function):
        for p in self.points: self.points[p] = i_function(self.points[p])

    def pow(self, i_val):
        for p in self.points: self.points[p] = self.points[p]**i_val
        
    def pow_r(self, i_val):
        for p in self.points: self.points[p] = i_val**self.points[p]
        
    def log(self, i_val):
        for p in self.points: self.points[p] = math.log(self.points[p],i_val)

    def log_r(self, i_val):
        for p in self.points: self.points[p] = math.log(i_val,self.points[p])

    def check(self):
        return len(self.points) != 0

    def sort(self):
        self.points = dict(sorted(self.points.items()))

    def edit_trimmove(self, startat, endat):
        self.sort()
        old_points = self.points
        self.points = {}
        prev_data = None
        for p, v in old_points.items():
            mpos = p-startat
            if mpos<0: prev_data = v
            elif mpos<endat: 
                if prev_data != None: 
                    self.points[0] = prev_data
                    prev_data = None
                self.points[mpos] = v



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
            if pos <= before_pos: ba_autos[0][pos] = self.points[pos]
            else: ba_autos[1][pos] = self.points[pos]
        out = def_val
        poslist = [x for x in ba_autos[0]]
        if poslist: out = ba_autos[0][max(poslist)]
        return out

    def split(self):
        prev_val = -1000000000000000
        autotspl = []
        lastsplit = 0
        for p, v in self.points.items():
            normlvl = (p-prev_val)/self.time_ppq
            if normlvl>=2: 
                lastsplit = p
                autotspl.append([p, cvpj_autoticks(self.time_ppq, self.time_float, self.val_type)])
            splittedpos = p-lastsplit
            autotspl[-1][1].add_point(splittedpos, v)
            prev_val = p
        return autotspl, self.time_ppq

    def to_points(self):
        pp = 0
        pv = 0

        hp = self.time_ppq//4

        tres = 0.02

        points_out = []

        for p, v in self.iter():
            cp = p-pp
            cv = abs(v-pv)

            ip = hp>cp
            iv = cv<tres

            ia = ip and iv

            points_out.append([p, v, ia])

            pp, pv = p, v

        return points_out