# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
import copy
import math
import numpy as np

from objects.convproj import placements
from objects.convproj import autopoints
from objects.convproj import visual
from objects.convproj import notelist
from objects.convproj import time
from objects.convproj import autoticks
from objects.convproj import timemarker
from objects import notelist_splitter

class cvpj_placements_notes:
	__slots__ = ['data']
	def __init__(self):
		self.data = []

	def __iter__(self):
		for x in self.data: yield x

	def __len__(self):
		return self.data.__len__()

	def __bool__(self):
		return bool(self.data)

	def merge_crop(self, npl_obj, pos, dur, visualfill):
		for n in npl_obj.data:
			if n.time.position < dur:
				copy_npl_obj = copy.deepcopy(n)
				plend = copy_npl_obj.time.get_end()
				numval = copy_npl_obj.time.duration+min(0, dur-plend)
				if copy_npl_obj.time.duration > numval:
					copy_npl_obj.notelist.edit_trimmove(0, numval)
				copy_npl_obj.time.position += pos
				copy_npl_obj.time.duration = numval
				if visualfill.name and not copy_npl_obj.visual.name:
					copy_npl_obj.visual.name = visualfill.name
				if visualfill.color and not copy_npl_obj.visual.color:
					copy_npl_obj.visual.color = visualfill.color
				self.data.append(copy_npl_obj)

	def append(self, value):
		self.data.append(value)

	def check_overlap(self, start, end):
		for npl in self.data:
			if xtramath.overlap(start, start+end, npl.time.position, npl.time.position+npl.time.duration): return True
		return False

	def clear(self):
		self.data = []
		
	def add(self, time_ppq, time_float):
		pl_obj = cvpj_placement_notes(time_ppq, time_float)
		self.data.append(pl_obj)
		return pl_obj

	def sort(self):
		self.data = placements.internal_sort(self.data)

	def get_dur(self):
		duration_final = 0
		for pl in self.data:
			if pl.time.duration == 0: pl.time.duration = pl.notelist.get_dur()
			pl_end = pl.time.get_end()
			if duration_final < pl_end: duration_final = pl_end
		return duration_final

	def get_start(self):
		start_final = 100000000000000000
		for pl in self.data:
			pl_start = pl.position
			if pl_start < start_final: start_final = pl_start
		return start_final

	def change_seconds(self, is_seconds, bpm, ppq):
		for pl in self.data: 
			pl.time.change_seconds(is_seconds, bpm, ppq)
		
	def remove_cut(self):
		for x in self.data: 
			if x.time.cut_type == 'cut':
				x.notelist.edit_trimmove(x.time.cut_start, x.time.duration)
				x.time.cut_start = 0
				x.time.cut_type = None

	def eq_content(self, pl, prev):
		if prev:
			isvalid_a = pl.notelist==prev.notelist
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
		self.data = placements.internal_addloops(self.data, self.eq_connect, loopcompat)

	def remove_loops(self, out__placement_loop):
		self.data = placements.internal_removeloops(self.data, out__placement_loop)

	def remove_overlaps(self):
		old_data_notes = copy.deepcopy(self.data)
		new_data_notes = []

		prev = None
		for pl in old_data_notes:
			endpos = pl.time.duration+pl.time.position
			if prev:
				poevendpos = prev.time.duration+prev.time.position
				prev.time.duration = min(prev.time.duration, pl.time.position-prev.time.position)
			prev = pl
			new_data_notes.append(pl)

		self.data = new_data_notes

class cvpj_placement_notes:
	__slots__ = ['time','muted','visual','notelist','time_ppq','time_float','auto','timesig_auto','timemarkers']
	def __init__(self, time_ppq, time_float):
		self.time = placements.cvpj_placement_timing()
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.notelist = notelist.cvpj_notelist(time_ppq, time_float)
		self.muted = False
		self.visual = visual.cvpj_visual()
		self.auto = {}
		self.timesig_auto = autoticks.cvpj_autoticks(self.time_ppq, self.time_float, 'timesig')
		self.timemarkers = timemarker.cvpj_timemarkers(self.time_ppq, self.time_float)

	def make_base(self):
		plb_obj = cvpj_placement_notes(self.time_ppq, self.time_float)
		plb_obj.time = self.time.copy()
		plb_obj.time_ppq = self.time_ppq
		plb_obj.time_float = self.time_float
		plb_obj.muted = self.muted
		plb_obj.visual = self.visual
		plb_obj.timesig_auto = self.timesig_auto.copy()
		plb_obj.timemarkers = self.timemarkers.copy()
		return plb_obj

	def inst_split(self, splitted_pl):
		nl_splitted = self.notelist.inst_split()
		for inst_id, notelist_obj in nl_splitted.items():
			plb_obj = self.make_base()
			plb_obj.notelist = notelist_obj
			if inst_id not in splitted_pl: splitted_pl[inst_id] = []
			splitted_pl[inst_id].append(plb_obj)

	def auto_dur(self, dur_p, dur_e):
		self.time.duration = self.notelist.get_dur()
		if self.time.duration != 0: self.time.duration = (self.time.duration/dur_p).__ceil__()*dur_p
		else: self.time.duration = dur_e

	def antiminus(self):
		loop_start, loop_loopstart, loop_loopend = self.time.get_loop_data()
		notepos = -min([self.notelist.get_start()]+[0, loop_start, loop_loopstart])
		if notepos:
			self.notelist.edit_move_minus(notepos)
			loop_start += notepos
			loop_loopstart += notepos
			loop_loopend += notepos
			self.time.set_loop_data(loop_start, loop_loopstart, loop_loopend)

	def get_logdur(self):
		durp = math.log2(self.duration/self.time_ppq)
		return (durp==int(durp)), durp
		
	def add_autopoints(self, a_type):
		self.auto[a_type] = autopoints.cvpj_autopoints(self.time_ppq, self.time_float, 'float')
		return self.auto[a_type]