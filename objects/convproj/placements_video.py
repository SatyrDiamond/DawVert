# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import placements
from objects.convproj import time
from objects.convproj import visual
import copy

class cvpj_placements_video:
	__slots__ = ['data','videoref','time_ppq','time_float']
	def __init__(self, time_ppq, time_float):
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.videoref = ''
		self.data = []

	def __iter__(self):
		for x in self.data: yield x

	def __len__(self):
		return self.data.__len__()

	def __bool__(self):
		return bool(self.data) or bool(self.video_fileref)

	def add(self):
		pl_obj = cvpj_placement_video(self.time_ppq, self.time_float)
		self.data.append(pl_obj)
		return pl_obj
		
	def sort(self):
		self.data = placements.internal_sort(self.data)

	def get_start(self):
		start_final = 100000000000000000
		for pl in self.data:
			pl_start = pl.time.position
			if pl_start < start_final: start_final = pl_start
		return start_final

	def get_dur(self):
		duration_final = 0
		for pl in self.data:
			pl_end = pl.time.get_end()
			if duration_final < pl_end: duration_final = pl_end
		return duration_final

	def remove_loops(self, out__placement_loop):
		self.data = placements.internal_removeloops(self.data, out__placement_loop)

	def eq_content(self, pl, prev):
		if prev:
			isvalid_a = pl.video_fileref==prev.video_fileref
			isvalid_b = pl.time.cut_type==prev.time.cut_type
			isvalid_c = pl.time.cut_start==prev.time.cut_start
			isvalid_d = pl.time.cut_loopstart==prev.time.cut_loopstart
			isvalid_e = pl.time.cut_loopend==prev.time.cut_loopend
			isvalid_f = pl.muted==prev.muted
			return isvalid_a & isvalid_b & isvalid_c & isvalid_d & isvalid_e & isvalid_f
		else:
			return False

	def eq_connect(self, pl, prev, loopcompat):
		if prev:
			isvalid_a = self.eq_content(pl, prev)
			isvalid_b = pl.time.cut_type in ['none', 'cut']
			isvalid_c = ((prev.time.position+prev.time.duration)-pl.time.position)==0
			isvalid_d = prev.time.cut_type in ['none', 'cut']
			isvalid_e = ('loop_adv' in loopcompat) if pl.time.cut_type == 'cut' else True
			isvalid_f = pl.time.duration==prev.time.duration
			return isvalid_a & isvalid_b & isvalid_c & isvalid_d & isvalid_e & isvalid_f
		else:
			return False

	def change_timings(self, time_ppq, time_float):
		for pl in self.data:
			pl.time.change_timing(self.time_ppq, time_ppq, time_float)
		self.time_ppq = time_ppq
		self.time_float = time_float

	def change_seconds(self, is_seconds, bpm, ppq):
		for pl in self.data: 
			pl.time.change_seconds(is_seconds, bpm, ppq)

	def add_loops(self, loopcompat):
		self.data = placements.internal_addloops(self.data, self.eq_connect, loopcompat)

class cvpj_placement_video:
	__slots__ = ['time','muted','visual','videoref','fade_in','fade_out','time_ppq','time_float','vol','looped']

	def __init__(self, time_ppq, time_float):
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.visual = visual.cvpj_visual()
		self.time = placements.cvpj_placement_timing(time_ppq, time_float)
		self.videoref = ''
		self.muted = False
		self.fade_in = placements.cvpj_placement_fade()
		self.fade_out = placements.cvpj_placement_fade()
		self.vol = 1
		self.looped = False