# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import placements
from objects.convproj import autoticks
from objects.convproj import visual
from objects.convproj import time

class cvpj_placements_autoticks:
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

	def add(self, val_type):
		placement_obj = cvpj_placement_autoticks(self.time_ppq, self.time_float, self.val_type)
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

class cvpj_placement_autoticks:
	__slots__ = ['time','muted','visual','data']

	def __init__(self, time_ppq, time_float, val_type):
		self.time = placements.cvpj_placement_timing()
		self.data = autoticks.cvpj_autoticks(time_ppq, time_float, val_type)
		self.muted = False
		self.visual = visual.cvpj_visual()
