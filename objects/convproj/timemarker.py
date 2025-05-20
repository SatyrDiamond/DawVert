# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import copy
from functions import xtramath
from objects.convproj import visual

class cvpj_timemarker:
	__slots__ = ['type','visual','position','duration','data','special']
	def __init__(self):
		self.visual = visual.cvpj_visual()
		self.type = ''
		self.position = 0
		self.duration = 0
		self.data = None
		self.special = False

class cvpj_timemarkers:
	__slots__ = ['data', 'time_ppq', 'time_float', 'is_seconds']
	def __init__(self, time_ppq, time_float):
		self.data = []
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.is_seconds = False

	def __getitem__(self, v):
		return self.data[v]

	def __len__(self):
		return self.data.__len__()

	def __iter__(self):
		for v in self.data: yield v

	def copy(self):
		return copy.deepcopy(self)

	def add(self):
		timemarker_obj = cvpj_timemarker()
		self.data.append(timemarker_obj)
		return timemarker_obj

	def change_timings(self, time_ppq, time_float):
		if not self.is_seconds:
			for m in self.data: 
				m.position = xtramath.change_timing(self.time_ppq, time_ppq, time_float, m.position)
				m.duration = xtramath.change_timing(self.time_ppq, time_ppq, time_float, m.duration)
			self.time_ppq = time_ppq
			self.time_float = time_float
		
	def change_seconds(self, is_seconds, bpm, ppq):
		if is_seconds and not self.is_seconds:
			for x in self.data: 
				x.position = xtramath.step2sec(x.position, bpm)/(ppq/4)
				x.duration = xtramath.step2sec(x.duration, bpm)/(ppq/4)
				self.is_seconds = True
		elif self.is_seconds:
			for x in self.data: 
				x.position = xtramath.sec2step(x.position, bpm)
				x.duration = xtramath.sec2step(x.duration, bpm)
				self.is_seconds = False
		
	def add_key(self, key):
		timemarker_obj = cvpj_timemarker()
		timemarker_obj.type = 'key_single'
		timemarker_obj.visual.name = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'][key%12]
		timemarker_obj.data = key
		timemarker_obj.special = True
		self.data.append(timemarker_obj)
		return timemarker_obj

