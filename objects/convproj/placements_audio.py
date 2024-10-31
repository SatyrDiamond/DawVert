# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
import copy

from objects.convproj import placements
from objects.convproj import autopoints
from objects.convproj import stretch
from objects.convproj import visual
from objects.convproj import time
from objects.convproj import sample_entry

class cvpj_placements_audio:
	__slots__ = ['data']
	def __init__(self):
		self.data = []

	def __iter__(self):
		for x in self.data: yield x

	def __len__(self):
		return self.data.__len__()

	def __bool__(self):
		return bool(self.data)

	def merge_crop(self, apl_obj, pos, dur, visualfill):
		for n in apl_obj.data:
			if n.time.position < dur:
				copy_apl_obj = copy.deepcopy(n)
				plend = copy_apl_obj.time.get_end()
				numval = copy_apl_obj.time.duration+min(0, dur-plend)
				copy_apl_obj.time.position += pos
				copy_apl_obj.time.duration = numval
				if visualfill.name and not copy_apl_obj.visual.name:
					copy_apl_obj.visual.name = visualfill.name
				if visualfill.color and not copy_apl_obj.visual.color:
					copy_apl_obj.visual.color = visualfill.color
				self.data.append(copy_apl_obj)

	def add(self):
		pl_obj = cvpj_placement_audio()
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
			for note in ta_sorted[p]: new_a.append(note)
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

	def change_seconds(self, is_seconds, bpm, ppq):
		for pl in self.data: 
			pl.time.change_seconds(is_seconds, bpm, ppq)
		
	def remove_loops(self, out__placement_loop):
		new_data = []
		for audiopl_obj in self.data: 
			if audiopl_obj.time.cut_type in ['loop', 'loop_off', 'loop_adv', 'loop_adv_off'] and audiopl_obj.time.cut_type not in out__placement_loop:
				loop_start, loop_loopstart, loop_loopend = audiopl_obj.time.get_loop_data()
				duration = audiopl_obj.time.duration
				for cutpoint in xtramath.cutloop(audiopl_obj.time.position, duration, loop_start, loop_loopstart, loop_loopend):
					cutplpl_obj = copy.deepcopy(audiopl_obj)
					cutplpl_obj.time.position = cutpoint[0]
					cutplpl_obj.time.duration = cutpoint[1]
					cutplpl_obj.time.cut_type = 'cut'
					cutplpl_obj.time.cut_start = cutpoint[2]
					new_data.append(cutplpl_obj)
			else: new_data.append(audiopl_obj)

			for n, x in enumerate(new_data):
				#print(len(new_data)-1, n, x)
				if not n==len(new_data)-1: x.fade_out.clear()
				if not n==0: x.fade_in.clear()

		self.data = new_data

	def eq_content(self, pl, prev):
		if prev:
			isvalid_a = pl.sample==prev.sample
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
			isvalid_g = not (bool(pl.fade_in) or bool(pl.fade_out))
			return isvalid_a & isvalid_b & isvalid_c & isvalid_d & isvalid_e & isvalid_f & isvalid_g
		else:
			return False

	def add_loops(self, loopcompat):
		old_data_audio = copy.deepcopy(self.data)
		new_data_audio = []

		prev = None
		for pl in old_data_audio:
			if not self.eq_connect(pl, prev, loopcompat):
				new_data_audio.append(pl)
			else:
				prevreal = new_data_audio[-1]
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

		self.data = new_data_audio

class cvpj_placement_audio:
	__slots__ = ['time','muted','sample','visual','sample','fade_in','fade_out','auto']

	def __init__(self):
		self.time = placements.cvpj_placement_timing()
		self.muted = False
		self.sample = sample_entry.cvpj_sample_entry()
		self.visual = self.sample.visual
		self.fade_in = placements.cvpj_placement_fade()
		self.fade_out = placements.cvpj_placement_fade()
		self.auto = {}

	def changestretch(self, convproj_obj, target, tempo):
		pos_offset, cut_offset, finalspeed = self.sample.stretch.changestretch(convproj_obj.samplerefs, self.sample.sampleref, target, tempo, convproj_obj.time_ppq)

		if self.time.cut_type == 'cut':
			self.time.cut_start += cut_offset
		if self.time.cut_type == 'loop':
			self.time.cut_loopend += cut_offset
			self.time.cut_loopstart += cut_offset

		self.time.cut_start += abs(min(0, pos_offset))
		self.time.duration -= max(0, pos_offset)
		self.time.position += max(pos_offset, 0)

	def add_autopoints(self, a_type, ppq_time, ppq_float):
		self.auto[a_type] = autopoints.cvpj_autopoints(ppq_time, ppq_float, 'float')
		return self.auto[a_type]

class cvpj_placements_nested_audio:
	__slots__ = ['data']
	def __init__(self):
		self.data = []

	def __iter__(self):
		for x in self.data: yield x

	def __bool__(self):
		return bool(self.data)

	def add(self):
		pl_obj = cvpj_placement_nested_audio()
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
			for note in ta_sorted[p]: new_a.append(note)
		self.data = new_a

	def changestretch(self, convproj_obj, target, tempo):
		for audiopl_obj in self.data:
			audiopl_obj.changestretch(convproj_obj, target, tempo)

	def remove_loops(self, out__placement_loop):
		new_data = []
		for audiopl_obj in self.data: 
			if audiopl_obj.time.cut_type in ['loop', 'loop_off', 'loop_adv'] and audiopl_obj.time.cut_type not in out__placement_loop:
				loop_start, loop_loopstart, loop_loopend = audiopl_obj.time.get_loop_data()
				for cutpoint in xtramath.cutloop(audiopl_obj.time.position, audiopl_obj.time.duration, loop_start, loop_loopstart, loop_loopend):
					cutplpl_obj = copy.deepcopy(audiopl_obj)
					cutplpl_obj.time.position = cutpoint[0]
					cutplpl_obj.time.duration = cutpoint[1]
					cutplpl_obj.time.cut_type = 'cut'
					cutplpl_obj.time.cut_start = cutpoint[2]
					new_data.append(cutplpl_obj)
			else: new_data.append(audiopl_obj)
		self.data = new_data

	def change_seconds(self, is_seconds, bpm):
		for pl in self.data: pl.change_seconds(is_seconds, bpm)

class cvpj_placement_nested_audio:
	__slots__ = ['time','visual','events','fade_in','fade_out']

	def __init__(self):
		self.time = placements.cvpj_placement_timing()
		self.visual = visual.cvpj_visual()
		self.events = []
		self.fade_in = placements.cvpj_placement_fade()
		self.fade_out = placements.cvpj_placement_fade()

	def add(self):
		apl_obj = cvpj_placement_audio()
		self.events.append(apl_obj)
		return apl_obj

	def change_seconds(self, is_seconds, bpm):
		self.position = xtramath.step2sec(self.position, bpm) if is_seconds else xtramath.sec2step(self.position, bpm)
		self.duration = xtramath.step2sec(self.duration, bpm) if is_seconds else xtramath.sec2step(self.duration, bpm)