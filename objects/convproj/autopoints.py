# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import time
import bisect
import math

class cvpj_s_autopoint:
	__slots__ = ['pos','pos_real','value','type','tension','extra']
	def __init__(self):
		self.pos = 0
		self.pos_real = None
		self.value = 0
		self.type = 'normal'
		self.tension = 0.0
		self.extra = {}

	def __add__(self, v):
		self.value += v

	def __eq__(self, aps):
		s_pos = self.pos == aps.pos
		s_value = self.value == aps.value
		s_type = self.type == aps.type
		s_tension = self.tension == aps.tension
		return s_pos and s_value and s_type and s_tension


class cvpj_autopoints:
	__slots__ = ['type','time_ppq','time_float','val_type','points','data','enabled','loop_on','loop_start','loop_end','sustain_on','sustain_loop','sustain_point','sustain_end','name']

	def __init__(self, time_ppq, time_float, val_type):
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.val_type = val_type
		self.data = {}
		self.points = []

		self.enabled = True
		self.loop_on = False
		self.loop_start = 0
		self.loop_end = 0

		self.sustain_on = False
		self.sustain_loop = False
		self.sustain_point = 0
		self.sustain_end = 0

		self.name = ''

	def __eq__(self, aps):
		s_time_ppq = self.time_ppq == aps.time_ppq
		s_time_float = self.time_float == aps.time_float
		s_val_type = self.val_type == aps.val_type
		s_points = self.points == aps.points
		s_data = self.data == aps.data
		return s_time_ppq and s_time_float and s_val_type and s_points and s_data

	def __getitem__(self, num):
		if num == 'pos': return [x.pos for x in self.points]
		elif num == 'value': return [x.value for x in self.points]
		else: return self.points[num]

	def __len__(self):
		return self.points.__len__()

	def __iter__(self):
		for x in self.points:
			yield x

	def merge(self, other):
		other = copy.deepcopy(other)
		other.change_timings(self.time_ppq, self.time_float)
		self.points += other.points
		self.sort()

	def clear(self):
		self.data = {}
		self.points = []

		self.enabled = True
		self.loop_on = False
		self.loop_start = 0
		self.loop_end = 0

		self.sustain_on = False
		self.sustain_loop = False
		self.sustain_point = 0
		self.sustain_end = 0

	def change_seconds(self, is_seconds, bpm, ppq):
		if is_seconds:
			for x in self.points: x.pos_real = xtramath.step2sec(x.pos, bpm)/(ppq/4)
		else:
			for x in self.points: x.pos = xtramath.sec2step(x.pos_real, bpm)
		
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
		
			endcon = xtramath.is_between(cp.pos, np.pos, endat)
			if endcon: 
				endcon = endat!=np.pos
				end_point += 1
				
			if endcon:
				if cp.type != 'instant':
					betpos = xtramath.between_to_one(cp.pos, np.pos, endat)
					cp.value = xtramath.between_from_one(cp.value, np.value, betpos)
					cp.pos = endat

		for p in self.points: p.pos -= startat
		self.points = self.points[start_point:end_point]

	def calc(self, mathtype, val1, val2, val3, val4):
		for p in self.points: p.value = xtramath.do_math(p.value, mathtype, val1, val2, val3, val4)

	def funcval(self, i_function):
		for p in self.points: p.value = i_function(p.value)

	def sort(self):
		ta_bsort = {}
		ta_sorted = {}
		new_a = []
		for n in self.points:
			if n.pos not in ta_bsort: ta_bsort[n.pos] = []
			ta_bsort[n.pos].append(n)
		ta_sorted = dict(sorted(ta_bsort.items(), key=lambda item: item))
		for p in ta_sorted:
			for note in ta_sorted[p]: new_a.append(note)
		self.points = new_a

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
				if p.pos_real: autopoint_obj.pos_real = p.pos_real-0.001
				autopoint_obj.value = prev_val
				autopoint_obj.type = 'normal'
				autopoint_obj.tension = p.tension
				new_points.append(autopoint_obj)
				
			autopoint_obj = cvpj_s_autopoint()
			autopoint_obj.pos = p.pos
			autopoint_obj.pos_real = p.pos_real
			autopoint_obj.value = p.value
			autopoint_obj.type = 'normal'
			autopoint_obj.tension = p.tension
			new_points.append(autopoint_obj)

			prev_pos = p.pos
			prev_val = p.value
		self.points = new_points

	def blocks(self):
		prev_val = 0
		prev_prev = 0
		cur_num = 0

		blocks_out = []

		while cur_num < len(self.points)-1:
			p = self.points[cur_num]
			pn = self.points[cur_num+1]
			#print(p.pos, p.value, p.type,'|',pn.pos, pn.value, pn.type)
			if cur_num==0 and p.pos!=0 and p.value!=0: 
				blocks_out.append([p.pos, 0, p.value])
			if (p.value != pn.value):
				slidesize = pn.pos-p.pos
				if p.type != 'instant': 
					blocks_out.append([p.pos, 0 if slidesize<(self.time_ppq/64) else slidesize, pn.value])
				else: 
					blocks_out.append([p.pos, 0, p.value])
			cur_num += 1

		return blocks_out

	def from_steps(self, steps, smooth, ppq):
		auto_duration = int(len(steps))
		steplens = ((1-smooth)*ppq)/4

		autopoints = []
		for stepnum, value in enumerate(steps):
			steplen = (stepnum*ppq)/4
			if smooth == 0.0: 
				autopoints.append([steplen, value, 'instant'])
			elif smooth == 0.0: 
				autopoints.append([steplen, value, 'normal'])
			else:
				autopoints.append([steplen, value, 'normal'])
				autopoints.append([steplen+steplens, value, 'normal'])
			prev_val = 0

		for p_pos, p_value, p_type in autopoints:
			autopoint_obj = self.add_point()
			autopoint_obj.pos = p_pos
			autopoint_obj.value = p_value
			autopoint_obj.type = p_type

	def from_blocks_obj(self, blocks_obj):
		self.clear()
		for numblock in range(len(blocks_obj.values)): 
			apoint_obj = self.add_point()
			apoint_obj.pos = numblock*blocks_obj.time
			apoint_obj.value = xtramath.between_to_one(0, blocks_obj.max, blocks_obj.values[numblock])
