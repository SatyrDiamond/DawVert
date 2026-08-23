# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import placements
from objects.convproj import time
from objects.convproj import visual
import copy

class cvpj_placements_marker:
	__slots__ = ['data','time_ppq']
	def __init__(self, time_ppq):
		self.time_ppq = time_ppq
		self.data = []

	def __iter__(self):
		for x in self.data: yield x

	def __len__(self):
		return self.data.__len__()

	def __bool__(self):
		return bool(self.data)

	def add(self):
		pl_obj = cvpj_placement_marker(self.time_ppq)
		self.data.append(pl_obj)
		return pl_obj
		
	def sort(self):
		self.data = placements.internal_sort(self.data)

	def get_dur(self):
		return placements.internal_get_dur(self.data)

	def get_start(self):
		return placements.internal_get_start(self.data)

	def remove_loops(self, out__placement_loop):
		self.data = placements.internal_removeloops(self.data, out__placement_loop)

	def eq_content(self, pl, prev):
		if prev:
			isvalid_a = pl.frommarker==prev.frommarker
			isvalid_b = placements.internal_eq_content(pl, prev)
			return isvalid_a & isvalid_b
		else:
			return False

	def eq_connect(self, pl, prev, loopcompat):
		if prev:
			isvalid_a = self.eq_content(pl, prev)
			isvalid_b = placements.internal_eq_connect(pl, prev, loopcompat)
			return isvalid_a & isvalid_b
		else:
			return False

	def change_timings(self, time_ppq):
		for pl in self.data: pl.time.change_timing(self.time_ppq, time_ppq)
		self.time_ppq = time_ppq

	def add_key(self, key):
		timemarker_obj = self.add()
		timemarker_obj.type = 'key_single'
		timemarker_obj.visual.name = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'][key%12]
		timemarker_obj.data = key
		timemarker_obj.special = True
		return timemarker_obj

class cvpj_placement_marker:
	__slots__ = ['time_ppq','time','visual','type','data','special']

	def __init__(self, time_ppq):
		self.time_ppq = time_ppq
		self.time = placements.cvpj_placement_timing(time_ppq)
		self.visual = visual.cvpj_visual()
		self.type = ''
		self.data = None
		self.special = False