# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import placements
from objects.convproj import time
import copy

class cvpj_placements_custom:
	__slots__ = ['data','custom','time_ppq']
	def __init__(self, time_ppq):
		self.time_ppq = time_ppq
		self.custom = {}
		self.data = []

	def __iter__(self):
		for x in self.data: yield x

	def __len__(self):
		return self.data.__len__()

	def __bool__(self):
		return bool(self.data)

	def add(self):
		pl_obj = cvpj_placement_custom(self.time_ppq)
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
			isvalid_a = pl.custom==prev.custom
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

	def change_seconds(self, is_seconds, bpm, ppq):
		for pl in self.data: 
			pl.time.change_seconds(is_seconds, bpm, ppq)

	def change_timings(self, time_ppq):
		for pl in self.data:
			pl.time.change_timing(self.time_ppq, time_ppq)
		self.time_ppq = time_ppq

	def add_loops(self, loopcompat):
		self.data = placements.internal_addloops(self.data, self.eq_connect, loopcompat)

class cvpj_placement_custom:
	__slots__ = ['time','muted','visual','custom','fade_in','fade_out','time_ppq','vol']

	def __init__(self, time_ppq):
		self.time_ppq = time_ppq
		self.time = placements.cvpj_placement_timing(time_ppq)
		self.custom = {}
		self.muted = False
		self.fade_in = placements.cvpj_placement_fade()
		self.fade_out = placements.cvpj_placement_fade()
		self.vol = 1