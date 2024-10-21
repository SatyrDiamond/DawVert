# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import placements
from objects.convproj import time
import copy

class cvpj_placements_index:
	__slots__ = ['data']
	def __init__(self):
		self.data = []

	def __iter__(self):
		for x in self.data: yield x

	def __len__(self):
		return self.data.__len__()

	def __bool__(self):
		return bool(self.data)

	def add(self):
		pl_obj = cvpj_placement_index()
		self.data.append(pl_obj)
		return pl_obj
		
	def sort(self):
		ta_bsort = {}
		ta_sorted = {}
		new_a = []
		for n in self.data:
			if n.time.position not in ta_bsort: ta_bsort[n.time.position] = []
			ta_bsort[n.time.position].append(n)
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
			pl_end = pl.time.get_end()
			if duration_final < pl_end: duration_final = pl_end
		return duration_final

	def remove_loops(self, out__placement_loop):
		new_data = []
		for notespl_obj in self.data: 
			if notespl_obj.time.cut_type in ['loop', 'loop_off', 'loop_adv'] and notespl_obj.time.cut_type not in out__placement_loop:
				loop_start, loop_loopstart, loop_loopend = notespl_obj.time.get_loop_data()
				for cutpoint in xtramath.cutloop(notespl_obj.time.position, notespl_obj.time.duration, loop_start, loop_loopstart, loop_loopend):
					cutplpl_obj = copy.deepcopy(notespl_obj)
					cutplpl_obj.time.position = cutpoint[0]
					cutplpl_obj.time.duration = cutpoint[1]
					cutplpl_obj.time.cut_type = 'cut'
					cutplpl_obj.time.cut_start = cutpoint[2]
					new_data.append(cutplpl_obj)
			else: new_data.append(notespl_obj)
		self.data = new_data

	def eq_content(self, pl, prev):
		if prev:
			isvalid_a = pl.fromindex==prev.fromindex
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

	def add_loops(self, loopcompat):
		old_data_index = copy.deepcopy(self.data)
		new_data_index = []

		prev = None
		for pl in old_data_index:

			if not self.eq_connect(pl, prev, loopcompat):
				new_data_index.append(pl)
			else:
				prevreal = new_data_index[-1]
				prevreal.time.duration += pl.time.duration
				if prevreal.time.cut_type == 'none': 
					prevreal.time.cut_type = 'loop'
					prevreal.time.cut_loopend = pl.time.duration
				if 'loop_adv' in loopcompat:
					if prevreal.time.cut_type == 'cut': 
						prevreal.time.cut_type = 'loop_adv'
						prevreal.time.cut_start = 0
						prevreal.time.cut_loopstart = pl.time.cut_start
						prevreal.time.cut_loopend = pl.time.duration+pl.time.cut_start
			prev = pl

		self.data = new_data_index

class cvpj_placement_index:
	__slots__ = ['time','muted','visual','fromindex','fade_in','fade_out']

	def __init__(self):
		self.time = placements.cvpj_placement_timing()
		self.fromindex = ''
		self.muted = False
		self.fade_in = placements.cvpj_placement_fade()
		self.fade_out = placements.cvpj_placement_fade()