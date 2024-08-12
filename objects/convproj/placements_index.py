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

	def eq_connect(self, pl, prev, loopcompat):
		if prev:
			isvalid_a = pl.cut_type in ['none', 'cut']
			isvalid_b = ((prev.position+prev.duration)-pl.position)==0
			isvalid_c = pl.fromindex==prev.fromindex
			isvalid_d = pl.cut_type==prev.cut_type
			isvalid_e = prev.cut_type in ['none', 'cut']
			isvalid_f = pl.cut_start==prev.cut_start
			isvalid_g = pl.muted==prev.muted
			isvalid_h = ('loop_adv' in loopcompat) if pl.cut_type == 'cut' else True
			print(isvalid_a, isvalid_b, isvalid_c, isvalid_d, isvalid_e, isvalid_f, isvalid_g, isvalid_h)
			return isvalid_a & isvalid_b & isvalid_c & isvalid_d & isvalid_e & isvalid_f & isvalid_g & isvalid_h
		else:
			return False

	def add_loops(self, loopcompat):
		old_data_index = copy.deepcopy(self.data)
		new_data_index = []

		prev = None
		for pl in old_data_index:
			if not self.eq_connect(pl, prev, loopcompat):
				new_data_index.append(pl)
			else:
				prevreal = new_data_index[-1]
				prevreal.duration += pl.duration
				if prevreal.cut_type == 'none': 
					prevreal.cut_type = 'loop'
					prevreal.cut_loopend = pl.duration
				if 'loop_adv' in loopcompat:
					if prevreal.cut_type == 'cut': 
						prevreal.cut_type = 'loop_off'
						prevreal.cut_loopstart = pl.cut_start
						prevreal.cut_loopend = pl.duration+pl.cut_start
			prev = pl

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
