# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
import bisect

class cvpj_s_autopoint:
    __slots__ = ['pos','value','type','tension']
    def __init__(self):
        self.pos = 0
        self.value = 0
        self.type = 'normal'
        self.tension = 0

    def __eq__(self, aps):
        s_pos = self.pos == aps.pos
        s_value = self.value == aps.value
        s_type = self.type == aps.type
        s_tension = self.tension == aps.tension
        return s_pos and s_value and s_type and s_tension

class cvpj_autopoints:
    __slots__ = ['type','time_ppq','time_float','val_type','points','data']

    def __init__(self, time_ppq, time_float, val_type):
        self.time_ppq = time_ppq
        self.time_float = time_float
        self.val_type = val_type
        self.data = {}
        self.points = []

    def __eq__(self, aps):
        s_time_ppq = self.time_ppq == aps.time_ppq
        s_time_float = self.time_float == aps.time_float
        s_val_type = self.val_type == aps.val_type
        s_points = self.points == aps.points
        s_data = self.data == aps.data
        return s_time_ppq and s_time_float and s_val_type and s_points and s_data

    def change_timings(self, time_ppq, time_float):
        for ap in self.points:
            ap.pos = xtramath.change_timing(self.time_ppq, time_ppq, time_float, ap.pos)
        self.time_ppq = time_ppq
        self.time_float = time_float

    def add_point(self):
        autopoint_obj = cvpj_s_autopoint()
        self.points.append(autopoint_obj)
        return autopoint_obj

    def count(self):
        return len(self.points)

    def get_dur(self):
        out_dur = 0
        for p in self.points:
            if out_dur < p.pos: out_dur = p.pos
        return out_dur

    def get_durpos(self):
        out_dur = 0
        out_pos = 1000000000000 if self.points else 0
        for p in self.points:
            if out_dur < p.pos: out_dur = p.pos
            if out_pos > p.pos: out_pos = p.pos
        return out_pos, out_dur

    def edit_move(self, pos):
        for p in self.points: p.pos += pos

    def edit_trimmove(self, startat, endat):
        autopos = [x.pos for x in self.points]
        pointlen = len(autopos)-1
        start_point = xtramath.clamp(bisect.bisect_right(autopos, startat)-1, 0, pointlen)
        end_point = bisect.bisect_left(autopos, endat)

        for i in range(start_point, end_point):
            cp = self.points[i]
            np = self.points[min(i+1, pointlen)]
            if xtramath.is_between(cp.pos, np.pos, startat):
                if cp.type != 'instant':
                    betpos = xtramath.between_to_one(cp.pos, np.pos, startat)
                    cp.value = xtramath.between_from_one(cp.value, np.value, betpos)
                    cp.pos = startat
        
            if xtramath.is_between(cp.pos, np.pos, endat):
                if cp.type != 'instant':
                    betpos = xtramath.between_to_one(cp.pos, np.pos, endat)
                    cp.value = xtramath.between_from_one(cp.value, np.value, betpos)
                    cp.pos = endat

        self.points = self.points[start_point:end_point]

    def addmul(self, addval, mulval):
        for p in self.points: p.value = (p.value+addval)*mulval

    def change_valrange(self, old_min, old_max, new_min, new_max):
        for p in self.points: p.pos = xtramath.between_from_one(new_min, new_max, xtramath.between_to_one(old_min, old_max, p.pos))

    def to_one(self, i_min, i_max):
        for p in self.points: p.pos = xtramath.between_to_one(i_min, i_max, p.pos)

    def from_one(self, i_min, i_max):
        for p in self.points: p.pos = xtramath.between_from_one(i_min, i_max, p.pos)

    def sort(self):
        ta_bsort = {}
        ta_sorted = {}
        new_a = []
        for n in self.points:
            if n.pos not in ta_bsort: ta_bsort[n.pos] = []
            ta_bsort[n.pos].append(n)
        ta_sorted = dict(sorted(ta_bsort.items(), key=lambda item: item.pos))
        for p in ta_sorted:
            for note in ta_sorted[p]: new_a.append(note)
        self.points = new_a

    def iter(self):
        for p in self.points: yield p

    def check(self):
        return len(self.points) != 0

    def remove_instant(self):
        prev_pos = 0
        prev_val = 0
        new_points = []
        for p in self.points:

            if p.type == 'instant' and new_points:
                autopoint_obj = cvpj_s_autopoint()
                autopoint_obj.pos = p.pos-0.001
                autopoint_obj.value = prev_val
                autopoint_obj.type = 'normal'
                autopoint_obj.tension = p.tension
                new_points.append(autopoint_obj)
                
            autopoint_obj = cvpj_s_autopoint()
            autopoint_obj.pos = p.pos
            autopoint_obj.value = p.value
            autopoint_obj.type = 'normal'
            autopoint_obj.tension = p.tension
            new_points.append(autopoint_obj)

            prev_pos = p.pos
            prev_val = p.value
        self.points = new_points

    def to_cvpj(self):
        out_cvpj = []
        for autod in self.points:
            pointJ = {}
            pointJ['position'] = (autod.pos/self.time_ppq)*4
            pointJ['value'] = autod.value
            pointJ['type'] = autod.type if autod.type != None else 'normal'
            pointJ['tension'] = autod.tension if autod.tension != None else 0
            out_cvpj.append(pointJ)
        return out_cvpj
