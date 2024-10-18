# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import copy
from functions import xtramath
from objects.convproj import visual

class cvpj_timemarker:
	__slots__ = ['type','visual','position','duration']
	def __init__(self):
		self.visual = visual.cvpj_visual()
		self.type = ''
		self.position = 0
		self.duration = 0

class cvpj_timemarkers:
	__slots__ = ['data', 'time_ppq', 'time_float']
	def __init__(self, time_ppq, time_float):
		self.data = []
		self.time_ppq = time_ppq
		self.time_float = time_float

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
		for m in self.data: m.position = xtramath.change_timing(self.time_ppq, time_ppq, time_float, m.position)
		self.time_ppq = time_ppq
		self.time_float = time_float