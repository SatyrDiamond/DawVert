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

	def change_timings(self, time_ppq, is_indexed):
		for pl in self.data:
			pl.time.change_timing(self.time_ppq, time_ppq)
			if not is_indexed: 
				pl.notelist.change_timings(time_ppq)
				pl.timesig_auto.change_timings(time_ppq)
				pl.timemarkers.change_timings(time_ppq)
				for mpename, autodata in pl.auto.items():
					autodata.change_timings(time_ppq)
		self.time_ppq = time_ppq

	def merge_crop(self, npl_obj, pos, dur, visualfill):
		for n in npl_obj.data:
			if n.time.get_pos() < dur:
				copy_npl_obj = copy.deepcopy(n)
				copytime_obj = copy_npl_obj.time
				plend = copytime_obj.get_end()
				numval = copytime_obj.get_dur()+min(0, dur-plend)
				if copytime_obj.get_dur() > numval:
					copy_npl_obj.notelist.edit_trimmove(0, numval)
				copytime_obj.calc_pos_add(pos)
				copytime_obj.set_dur(numval)
				if visualfill.name and not copy_npl_obj.visual.name:
					copy_npl_obj.visual.name = visualfill.name
				if visualfill.color and not copy_npl_obj.visual.color:
					copy_npl_obj.visual.color = visualfill.color
				self.data.append(copy_npl_obj)

	def append(self, value):
		self.data.append(value)

	def check_overlap_timeobj(self, time_obj):
		start, end = time_obj.get_startend()
		return self.check_overlap(start, end)

	def check_overlap(self, start, end):
		for npl in self.data:
			istart, iend = npl.time.get_startend()
			if xtramath.overlap(start, start+end, istart, iend):
				return True
		return False

	def clear(self):
		self.data = []
		
	def add(self, time_ppq):
		pl_obj = cvpj_placement_notes(time_ppq)
		self.data.append(pl_obj)
		return pl_obj

	def sort(self):
		self.data = placements.internal_sort(self.data)

	def get_dur(self):
		return placements.internal_get_dur(self.data)

	def get_start(self):
		start_final = 100000000000000000
		for pl in self.data:
			if pl.notelist.count():
				pl_start = pl.time.get_pos()
				if pl_start < start_final: start_final = pl_start
		return start_final

	def change_seconds(self, is_seconds, bpm, ppq):
		for pl in self.data: 
			pl.time.change_seconds(is_seconds, bpm, ppq)
			for _, a in pl.auto.items(): a.change_seconds(is_seconds, bpm, ppq)
		
	def remove_cut(self):
		for x in self.data: 
			if x.time.cut_type == 'cut':
				ooffset = x.time.get_offset()
				x.notelist.edit_trimmove(ooffset, round(ooffset+x.time.get_dur(), 8))
				x.time.set_offset(0)
				x.time.cut_type = None

	def eq_content(self, pl, prev):
		if prev:
			isvalid_a = pl.notelist==prev.notelist
			isvalid_b = placements.internal_eq_content(pl, prev)
			return isvalid_a & isvalid_b
		else:
			return False

	def eq_connect(self, pl, prev, loopcompat):
		if prev:
			prevtime = prev.time
			isvalid_a = self.eq_content(pl, prev)
			isvalid_b = placements.internal_eq_connect(pl, prev, loopcompat)
			return isvalid_a & isvalid_b
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
			time_obj = pl.time
			position, duration = time_obj.get_posdur()
			if prev: 
				prev_time_obj = prev.time
				prev_time_obj.set_dur( min(prev_time_obj.get_dur(), position-prev_time_obj.get_pos()) )
			prev = pl
			new_data_notes.append(pl)

		self.data = new_data_notes

	def make_base_from_midi(self, midip):
		plb_obj = cvpj_placement_notes(self.time_ppq)
		plb_obj.time = midip.time.copy()
		plb_obj.time_ppq = midip.time_ppq
		plb_obj.muted = midip.muted
		plb_obj.visual = midip.visual
		plb_obj.group = midip.group
		plb_obj.locked = midip.locked
		self.data.append(plb_obj)
		return plb_obj

class cvpj_placement_notes:
	__slots__ = ['time','muted','visual','notelist','time_ppq','auto','timesig_auto','timemarkers','group','locked']
	def __init__(self, time_ppq):
		self.time = placements.cvpj_placement_timing(time_ppq)
		self.time_ppq = time_ppq
		self.notelist = notelist.cvpj_notelist(time_ppq)
		self.muted = False
		self.visual = visual.cvpj_visual()
		self.auto = {}
		self.timesig_auto = autoticks.cvpj_autoticks(self.time_ppq, 'timesig')
		self.timemarkers = timemarker.cvpj_timemarkers(self.time_ppq)
		self.group = None
		self.locked = False

	def make_base(self):
		plb_obj = cvpj_placement_notes(self.time_ppq)
		plb_obj.time = self.time.copy()
		plb_obj.time_ppq = self.time_ppq
		plb_obj.muted = self.muted
		plb_obj.visual = self.visual
		plb_obj.timesig_auto = self.timesig_auto.copy()
		plb_obj.timemarkers = self.timemarkers.copy()
		plb_obj.group = self.group
		plb_obj.locked = self.locked
		return plb_obj

	def inst_split(self, splitted_pl):
		nl_splitted = self.notelist.inst_split()
		for inst_id, notelist_obj in nl_splitted.items():
			plb_obj = self.make_base()
			plb_obj.notelist = notelist_obj
			if inst_id not in splitted_pl: splitted_pl[inst_id] = []
			splitted_pl[inst_id].append(plb_obj)

	def auto_dur(self, dur_p, dur_e):
		nl_dur = self.notelist.get_dur()
		time_obj = self.time
		if nl_dur != 0: time_obj.set_dur( (nl_dur/dur_p).__ceil__()*dur_p )
		else: time_obj.set_dur(dur_e)

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
		durp = math.log2(self.get_dur()/self.time_ppq)
		return (durp==int(durp)), durp
		
	def add_autopoints(self, a_type):
		self.auto[a_type] = autopoints.cvpj_autopoints(self.time_ppq, 'float')
		return self.auto[a_type]