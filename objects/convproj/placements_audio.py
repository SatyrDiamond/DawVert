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

	def add(self):
		pl_obj = cvpj_placement_audio(self.time_ppq)
		self.data.append(pl_obj)
		return pl_obj

	def sort(self):
		self.data = placements.internal_sort(self.data)

	def get_dur(self):
		return placements.internal_get_dur(self.data)

	def get_start(self):
		return placements.internal_get_start(self.data)

	def change_timings(self, time_ppq):
		for pl in self.data:
			pl.time.change_timing(self.time_ppq, time_ppq)
			if pl.auto:
				for mpename, autodata in pl.auto.items():
					autodata.change_timings(time_ppq)
		self.time_ppq = time_ppq

	def change_seconds(self, is_seconds, bpm, ppq):
		for pl in self.data: 
			pl.time.change_seconds(is_seconds, bpm, ppq)
			for _, a in pl.auto.items(): a.change_seconds(is_seconds, bpm, ppq)

	def remove_loops(self, out__placement_loop):
		new_data = []
		for audiopl_obj in self.data: 
			if audiopl_obj.time.cut_type in ['loop', 'loop_off', 'loop_eq', 'loop_adv', 'loop_adv_off'] and audiopl_obj.time.cut_type not in out__placement_loop:

				loop_start, loop_loopstart, loop_loopend = audiopl_obj.time.get_loop_data()
				if audiopl_obj.time.cut_type in ['loop_adv', 'loop_adv_off'] and 'loop_eq' in out__placement_loop:
					dur = audiopl_obj.time.duration
					offset = audiopl_obj.time.cut_start
	
					cutplpl_obj = copy.deepcopy(audiopl_obj)
					cutplpl_obj.time.duration = min(loop_loopend-offset, dur)
					cutplpl_obj.time.set_offset(audiopl_obj.time.cut_start)
					new_data.append(cutplpl_obj)
	
					if dur>loop_loopend:
						cutplpl_obj = copy.deepcopy(audiopl_obj)
						cutplpl_obj.time.position += loop_loopend-offset
						cutplpl_obj.time.duration = (dur-loop_loopend)+offset
						cutplpl_obj.time.set_loop_data(loop_loopstart, loop_loopstart, loop_loopend)
						new_data.append(cutplpl_obj)

				else:
					loop_start, loop_loopstart, loop_loopend = audiopl_obj.time.get_loop_data()
					duration = audiopl_obj.time.duration
					duration = duration+audiopl_obj.time.cut_start if audiopl_obj.time.cut_type == 'loop_eq' else duration
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
			isvalid_b = placements.internal_eq_content(pl, prev)
			return isvalid_a & isvalid_b
		else:
			return False

	def eq_connect(self, pl, prev, loopcompat):
		if prev:
			isvalid_a = self.eq_content(pl, prev)
			isvalid_b = placements.internal_eq_connect(pl, prev, loopcompat)
			isvalid_c = not (bool(pl.fade_in) or bool(pl.fade_out))
			return isvalid_a & isvalid_b & isvalid_c
		else:
			return False

	def add_loops(self, loopcompat):
		self.data = placements.internal_addloops(self.data, self.eq_connect, loopcompat)

	#def all_stretch_set_pitch_nonsync(self):
	#	for x in self.data: x.all_stretch_set_pitch_nonsync()

	def changestretch(self, convproj_obj, target, tempo):
		for x in self.data:
			x.changestretch(convproj_obj, target, tempo)

	def remove_overlaps(self):
		old_data_audio = copy.deepcopy(self.data)
		new_data_audio = []

		prev = None
		for pl in old_data_audio:
			endpos = pl.time.duration+pl.time.position
			if prev:
				poevendpos = prev.time.duration+prev.time.position
				prev.time.duration = min(prev.time.duration, pl.time.position-prev.time.position)
			prev = pl
			new_data_audio.append(pl)

		self.data = new_data_audio

	def merge_crop(self, apl_obj, pos, dur, visualfill, groupid):
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
				copy_apl_obj.group = groupid
				self.data.append(copy_apl_obj)


class cvpj_placement_audio:
	__slots__ = ['time','muted','sample','visual','sample','fade_in','fade_out','auto','time_ppq','group','locked']

	def __init__(self, time_ppq):
		self.time_ppq = time_ppq
		self.time = placements.cvpj_placement_timing(time_ppq)
		self.muted = False
		self.sample = sample_entry.cvpj_sample_entry()
		self.visual = self.sample.visual
		self.fade_in = placements.cvpj_placement_fade()
		self.fade_out = placements.cvpj_placement_fade()
		self.auto = {}
		self.group = None
		self.locked = False

	def changestretch(self, convproj_obj, target, tempo):
		stretch_obj = self.sample.stretch
		pos_offset, cut_offset, finalspeed = stretch_obj.changestretch(convproj_obj.samplerefs, self.sample.sampleref, target, tempo, convproj_obj.time_ppq, self.sample.pitch)

		if self.time.cut_type in ['cut', 'none']:
			self.time.cut_start += cut_offset
			self.time.cut_type = 'cut'
		if self.time.cut_type == 'loop':
			self.time.cut_loopend += cut_offset
			self.time.cut_loopstart += cut_offset

		#if not stretch_obj.is_warped and target == 'warp' and not stretch_obj.timing.tempo_based:
		#	print('s')

		self.time.cut_start += abs(min(0, pos_offset))
		self.time.duration -= max(0, pos_offset)
		self.time.position += max(pos_offset, 0)

	def add_autopoints(self, a_type, ppq_time, ppq_float):
		self.auto[a_type] = autopoints.cvpj_autopoints(ppq_time, ppq_float, 'float')
		return self.auto[a_type]

	def all_stretch_set_pitch_nonsync(self):
		pitch = self.sample.stretch_get_pitch_nonsync()
		self.time.loop_scale(pitch)

class cvpj_placements_nested_audio:
	__slots__ = ['data','time_ppq']
	def __init__(self, time_ppq):
		self.time_ppq = time_ppq
		self.data = []

	def __iter__(self):
		for x in self.data: yield x

	def __bool__(self):
		return bool(self.data)

	def add(self):
		pl_obj = cvpj_placement_nested_audio(self.time_ppq)
		self.data.append(pl_obj)
		return pl_obj

	def sort(self):
		self.data = placements.internal_sort(self.data)

	def changestretch(self, convproj_obj, target, tempo):
		for audiopl_obj in self.data:
			audiopl_obj.changestretch(convproj_obj, target, tempo)

	def remove_loops(self, out__placement_loop):
		self.data = placements.internal_removeloops(self.data, out__placement_loop)

	def change_timings(self, time_ppq):
		for pl in self.data:
			pl.time.change_timing(self.time_ppq, time_ppq)
			for x in pl.events: x.time.change_timing(self.time_ppq, time_ppq)
		self.time_ppq = time_ppq

	def change_seconds(self, is_seconds, bpm):
		for pl in self.data: pl.change_seconds(is_seconds, bpm)

class cvpj_placement_nested_audio:
	__slots__ = ['time','visual','events','fade_in','fade_out','muted','time_ppq','locked']

	def __init__(self, time_ppq):
		self.time_ppq = time_ppq
		self.time = placements.cvpj_placement_timing(time_ppq)
		self.visual = visual.cvpj_visual()
		self.events = []
		self.muted = False
		self.fade_in = placements.cvpj_placement_fade()
		self.fade_out = placements.cvpj_placement_fade()
		self.locked = False

	def add(self):
		apl_obj = cvpj_placement_audio(self.time_ppq)
		self.events.append(apl_obj)
		return apl_obj

	def change_seconds(self, is_seconds, bpm):
		self.position = xtramath.step2sec(self.position, bpm) if is_seconds else xtramath.sec2step(self.position, bpm)
		self.duration = xtramath.step2sec(self.duration, bpm) if is_seconds else xtramath.sec2step(self.duration, bpm)