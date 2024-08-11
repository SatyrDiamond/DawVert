# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import time
import copy

class cvpj_placements_index:
	__slots__ = ['data']
	def __init__(self):
		self.data = []

	def __iter__(self):
		for x in self.data: yield x

	def add(self):
		pl_obj = cvpj_placement_index()
		self.data.append(pl_obj)
		return pl_obj
		
	def sort(self):
		ta_bsort = {}
		ta_sorted = {}
		new_a = []
		for n in self.data:
			if n.position not in ta_bsort: ta_bsort[n.position] = []
			ta_bsort[n.position].append(n)
		ta_sorted = dict(sorted(ta_bsort.items(), key=lambda item: item[0]))
		for p in ta_sorted:
			for x in ta_sorted[p]: new_a.append(x)
		self.data = new_a

	def get_start(self):
		start_final = 100000000000000000
		for pl in self.data:
			pl_start = pl.position
			if pl_start < start_final: start_final = pl_start
		return start_final

	def get_dur(self):
		duration_final = 0
		for pl in self.data:
			pl_end = pl.position+pl.duration
			if duration_final < pl_end: duration_final = pl_end
		return duration_final

	def remove_loops(self, out__placement_loop):
		new_data = []
		for notespl_obj in self.data: 
			if notespl_obj.cut_type in ['loop', 'loop_off', 'loop_adv'] and notespl_obj.cut_type not in out__placement_loop:
				loop_start, loop_loopstart, loop_loopend = notespl_obj.get_loop_data()
				for cutpoint in xtramath.cutloop(notespl_obj.position, notespl_obj.duration, loop_start, loop_loopstart, loop_loopend):
					cutplpl_obj = copy.deepcopy(notespl_obj)
					cutplpl_obj.position = cutpoint[0]
					cutplpl_obj.duration = cutpoint[1]
					cutplpl_obj.cut_type = 'cut'
					cutplpl_obj.cut_start = cutpoint[2]
					new_data.append(cutplpl_obj)
			else: new_data.append(notespl_obj)
		self.data = new_data

	def add_loops(self):
		old_data_notes = copy.deepcopy(self.data)
		new_data_index = []
		prev_pos = 0
		prev_dur = 0
		prev_posdur = 0
		prev_ind = None
		prevtype = False

		for pl in old_data_notes:
			ifvalid_a = (pl.position-prev_posdur)==0
			isvalid_b = pl.cut_type=='none'
			isvalid_c = pl.fromindex==prev_ind

			ifvalid = ifvalid_a and isvalid_b and prevtype and isvalid_c

			if not ifvalid:
				pl.cut_type = 'loop'
				pl.cut_loopend = pl.duration
				new_data_index.append(pl)
			else:
				new_data_index[-1].duration += pl.duration

			prevtype = isvalid_b
			prev_ind = pl.fromindex
			prev_pos = pl.position
			prev_dur = pl.duration
			prev_posdur = prev_pos+prev_dur

		self.data = new_data_index

class cvpj_placement_index:
	__slots__ = ['position','duration','position_real','duration_real','cut_type','cut_start','cut_loopstart','cut_loopend','muted','visual','fromindex','fade_in','fade_out']

	def __init__(self):
		self.position = 0
		self.duration = 0
		self.position_real = None
		self.duration_real = None
		self.cut_type = 'none'
		self.cut_start = 0
		self.cut_loopstart = 0
		self.cut_loopend = -1
		self.fromindex = ''
		self.muted = False
		self.fade_in = {}
		self.fade_out = {}

	def cut_loop_data(self, start, loopstart, loopend):
		if loopstart: self.cut_type = 'loop_adv'
		elif start: self.cut_type = 'loop_off'
		elif loopend: self.cut_type = 'loop'
		self.cut_start = start
		self.cut_loopstart = loopstart
		self.cut_loopend = loopend

	def get_loop_data(self):
		loop_start = self.cut_start
		loop_loopstart = self.cut_loopstart
		loop_loopend = self.cut_loopend if self.cut_loopend>0 else x.duration
		return loop_start, loop_loopstart, loop_loopend
