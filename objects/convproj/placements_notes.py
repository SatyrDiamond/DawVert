# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
import copy
import math
import numpy as np

from objects.convproj import visual
from objects.convproj import notelist
from objects.convproj import time
from objects import notelist_splitter

class cvpj_placements_notes:
	__slots__ = ['data']
	def __init__(self):
		self.data = []

	def __iter__(self):
		for x in self.data: yield x

	def merge_crop(self, npl_obj, pos, dur, visualfill):
		for n in npl_obj.data:
			if n.position < dur:
				copy_npl_obj = copy.deepcopy(n)
				plend = copy_npl_obj.position+copy_npl_obj.duration
				numval = copy_npl_obj.duration+min(0, dur-plend)
				if copy_npl_obj.duration > numval:
					copy_npl_obj.notelist.edit_trimmove(0, numval)
				copy_npl_obj.position += pos
				copy_npl_obj.duration = numval
				if visualfill.name and not copy_npl_obj.visual.name:
					copy_npl_obj.visual.name = visualfill.name
				if visualfill.color and not copy_npl_obj.visual.color:
					copy_npl_obj.visual.color = visualfill.color
				self.data.append(copy_npl_obj)

	#def autosplit(self, ppq):
	#	if len(self.data) == 1:
	#		spl = self.data[0]
	#		if spl.position == 0 and spl.duration:
	#			isbeat, num = spl.get_logdur()
	#			if isbeat and num>2:
	#				timesigblocks_obj = notelist_splitter.timesigblocks()
	#				print('BEAT', isbeat, num, spl.duration)
#
	#				valspldurs = [x for x in range(int(num-1), 1, -1)]
	#				valspldurs.reverse()
#
	#				usedregions = np.zeros(spl.duration//16, dtype=np.uint8)
#
	#				for cnum in valspldurs:
	#					beatlen = int(ppq*(2**cnum))
#
	#					print('_ PART', cnum-1, beatlen)
#
	#					hashlist = spl.notelist.get_hash_split(beatlen, spl.duration)
#
	#					print(hashlist)

						#timesigblocks_obj.endsplit(spl.duration, beatlen, 0)
						
						#hashtxt = spl.notelist.get_hash(0, 16)
						#print(hashtxt)

						#print(timesigblocks_obj.splitpoints[0:-1])
						#print(timesigblocks_obj.splitts[0:-1])

	#	exit()

	def append(self, value):
		self.data.append(value)

	def check_overlap(self, start, end):
		for npl in self.data:
			if xtramath.overlap(start, start+end, npl.position, npl.position+npl.duration): return True
		return False

	def clear(self):
		self.data = []
		
	def add(self, time_ppq, time_float):
		pl_obj = cvpj_placement_notes(time_ppq, time_float)
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

	def get_dur(self):
		duration_final = 0
		for pl in self.data:
			if pl.duration == 0: pl.duration = pl.notelist.get_dur()
			pl_end = pl.position+pl.duration
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
			if is_seconds:
				pl.position_real = xtramath.step2sec(pl.position, bpm)/(ppq/4)
				pl.duration_real = xtramath.step2sec(pl.duration, bpm)/(ppq/4)
			else:
				pl.position = xtramath.sec2step(pl.position_real, bpm)
				pl.duration = xtramath.sec2step(pl.duration_real, bpm)
		
	def remove_cut(self):
		for x in self.data: 
			if x.cut_type == 'cut':
				x.notelist.edit_trimmove(x.cut_start, x.duration)
				x.cut_start = 0
				x.cut_type = None

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

	def eq_content(self, pl, prev):
		if prev:
			isvalid_a = pl.notelist==prev.notelist
			isvalid_b = pl.cut_type==prev.cut_type
			isvalid_c = pl.cut_start==prev.cut_start
			isvalid_d = pl.cut_loopstart==prev.cut_loopstart
			isvalid_e = pl.cut_loopend==prev.cut_loopend
			isvalid_f = pl.muted==prev.muted
			return isvalid_a & isvalid_b & isvalid_c & isvalid_d & isvalid_e & isvalid_f
		else:
			return False

	def eq_connect(self, pl, prev, loopcompat):
		if prev:
			isvalid_a = self.eq_content(pl, prev)
			isvalid_b = pl.cut_type in ['none', 'cut']
			isvalid_c = ((prev.position+prev.duration)-pl.position)==0
			isvalid_d = prev.cut_type in ['none', 'cut']
			isvalid_e = ('loop_adv' in loopcompat) if pl.cut_type == 'cut' else True
			isvalid_f = pl.duration==prev.duration
			return isvalid_a & isvalid_b & isvalid_c & isvalid_d & isvalid_e & isvalid_f
		else:
			return False

	def add_loops(self, loopcompat):
		old_data_notes = copy.deepcopy(self.data)
		new_data_notes = []

		prev = None
		for pl in old_data_notes:
			if not self.eq_connect(pl, prev, loopcompat):
				new_data_notes.append(pl)
			else:
				prevreal = new_data_notes[-1]
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

		self.data = new_data_notes

class cvpj_placement_notes:
	__slots__ = ['position','duration','position_real','duration_real','cut_type','cut_start','cut_loopstart','cut_loopend','muted','visual','notelist','time_ppq','time_float']
	def __init__(self, time_ppq, time_float):
		self.position = 0
		self.duration = 0
		self.position_real = None
		self.duration_real = None
		self.cut_type = 'none'
		self.cut_start = 0
		self.cut_loopstart = 0
		self.cut_loopend = -1
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.notelist = notelist.cvpj_notelist(time_ppq, time_float)
		self.muted = False
		self.visual = visual.cvpj_visual()

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
		loop_loopend = self.cut_loopend if self.cut_loopend>0 else self.duration
		return loop_start, loop_loopstart, loop_loopend

	def inst_split(self, splitted_pl):
		nl_splitted = self.notelist.inst_split()
		for inst_id, notelist_obj in nl_splitted.items():
			plb_obj = cvpj_placement_notes(self.time_ppq, self.time_float)
			plb_obj.position = self.position
			plb_obj.duration = self.duration
			plb_obj.position_real = self.position_real
			plb_obj.duration_real = self.duration_real
			plb_obj.cut_type = self.cut_type
			plb_obj.cut_start = self.cut_start
			plb_obj.cut_loopstart = self.cut_loopstart
			plb_obj.cut_loopend = self.cut_loopend
			plb_obj.time_ppq = self.time_ppq
			plb_obj.time_float = self.time_float
			plb_obj.notelist = notelist_obj
			plb_obj.muted = self.muted
			plb_obj.visual = self.visual
			if inst_id not in splitted_pl: splitted_pl[inst_id] = []
			splitted_pl[inst_id].append(plb_obj)

	def auto_dur(self, dur_p, dur_e):
		self.duration = self.notelist.get_dur()
		if self.duration != 0: self.duration = (self.duration/dur_p).__ceil__()*dur_p
		else: self.duration = dur_e

	def antiminus(self):
		loop_start, loop_loopstart, loop_loopend = self.get_loop_data()
		notepos = -min([self.notelist.get_start()]+[0, loop_start, loop_loopstart])
		if notepos:
			self.notelist.edit_move_minus(notepos)
			loop_start += notepos
			loop_loopstart += notepos
			loop_loopend += notepos
			self.cut_loop_data(loop_start, loop_loopstart, loop_loopend)

	def get_logdur(self):
		durp = math.log2(self.duration/self.time_ppq)
		return (durp==int(durp)), durp