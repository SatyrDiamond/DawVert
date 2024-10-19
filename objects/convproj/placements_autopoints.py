# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import placements
from objects.convproj import autopoints
from objects.convproj import visual

class cvpj_placements_autopoints:
	__slots__ = ['data','type','time_ppq','time_float','val_type']
	def __init__(self, time_ppq, time_float, val_type):
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.val_type = val_type
		self.data = []

	def __iter__(self):
		for x in self.data: yield x

	def __len__(self):
		return self.data.__len__()

	def __bool__(self):
		return bool(self.data)

	def sort(self):
		ta_bsort = {}
		ta_sorted = {}
		new_a = []
		for n in self.data:
			if n.time.position not in ta_bsort: ta_bsort[n.time.position] = []
			ta_bsort[n.time.position].append(n)
		ta_sorted = dict(sorted(ta_bsort.items(), key=lambda item: item[0]))
		for p in ta_sorted:
			for note in ta_sorted[p]: new_a.append(note)
		self.data = new_a

	def add(self, val_type):
		placement_obj = cvpj_placement_autopoints(self.time_ppq, self.time_float, self.val_type)
		self.data.append(placement_obj)
		return placement_obj

	def change_timings(self, time_ppq, time_float):
		for pl in self.data:
			pl.time.change_timing(self.time_ppq, time_ppq, time_float)
			pl.data.change_timings(time_ppq, time_float)

		self.time_ppq = time_ppq
		self.time_float = time_float

	def calc(self, mathtype, val1, val2, val3, val4):
		for pl in self.data: pl.data.calc(mathtype, val1, val2, val3, val4)

	def funcval(self, i_function):
		for pl in self.data: pl.data.funcval(i_function)

	def check(self):
		return len(self.data) != 0

	def remove_cut(self):
		for x in self.data: 
			if x.cut_type == 'cut':
				x.data.edit_trimmove(x.time.cut_start, x.time.duration)
				x.cut_start = 0
				x.cut_type = None

	def remove_unused(self):
		for x in self.data: 
			if x.cut_type == 'cut':
				x.data.edit_trimmove(x.time.cut_start, x.time.duration)
			else:
				x.data.edit_trimmove(0, x.time.duration)

class cvpj_placement_autopoints:
	__slots__ = ['time','muted','visual','data']

	def __init__(self, time_ppq, time_float, val_type):
		self.time = placements.cvpj_placement_timing()
		self.data = autopoints.cvpj_autopoints(time_ppq, time_float, val_type)
		self.muted = False
		self.visual = visual.cvpj_visual()

	def remove_cut(self):
		if self.time.cut_type == 'cut':
			self.data.edit_trimmove(self.time.cut_start, self.time.duration+self.time.cut_start)
		if self.time.cut_type == 'none':
			self.data.edit_trimmove(0, self.time.duration)

