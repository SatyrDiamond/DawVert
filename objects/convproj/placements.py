# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import project as convproj
from functions import xtramath
import copy

from objects.convproj import notelist
from objects.convproj import midievents
from objects.convproj import tracks

from objects.convproj import placements_midi
from objects.convproj import placements_notes
from objects.convproj import placements_audio
from objects.convproj import placements_index
from objects.convproj import placements_video
from objects.convproj import placements_custom
from objects.convproj import time

def internal_addloops(pldata, eq_connect, loopcompat):
	old_data = copy.deepcopy(pldata)
	new_data = []

	prev = None
	for pl in old_data:
		if not eq_connect(pl, prev, loopcompat):
			new_data.append(pl)
		else:
			cur_time_obj = pl.time
			cur_duration = cur_time_obj.get_dur()
			cur_cut_start = cur_time_obj.get_offset()

			prevreal = new_data[-1]
			pr_time_obj = prevreal.time
			pr_time_obj.calc_dur_add(cur_duration)
			if pr_time_obj.cut_type == 'none': 
				pr_time_obj.cut_type = 'loop'
				pr_time_obj.calc_loopend_add(cur_duration)
			if 'loop_adv' in loopcompat:
				if pr_time_obj.cut_type == 'cut': 
					pr_time_obj.cut_type = 'loop_off'
					pr_time_obj.cut_loopstart.set(cur_cut_start, 'ppq')
					pr_time_obj.calc_loopend_add(cur_duration+cur_cut_start)
		prev = pl

	return new_data

def internal_removeloops(pldata, out__placement_loop):
	new_data = []

	for oldpl_obj in pldata: 
		oldtime_obj = oldpl_obj.time
		if oldtime_obj.cut_type in ['loop', 'loop_eq', 'loop_off', 'loop_adv', 'loop_adv_off'] and oldtime_obj.cut_type not in out__placement_loop:
			loop_start, loop_loopstart, loop_loopend = oldtime_obj.get_loop_data()
			if oldtime_obj.cut_type in ['loop_adv', 'loop_adv_off'] and 'loop_eq' in out__placement_loop:
				dur = oldtime_obj.get_dur()
				offset = oldtime_obj.get_offset()

				cutplpl_obj = copy.deepcopy(oldpl_obj)
				cutplpl_obj.time.set_dur(min(loop_loopend-offset, dur))
				cutplpl_obj.time.set_offset(offset)
				new_data.append(cutplpl_obj)

				if dur>loop_loopend:
					cutplpl_obj = copy.deepcopy(oldpl_obj)
					cpl_time_obj = cutplpl_obj.time
					cpl_time_obj.calc_pos_add(loop_loopend-offset)
					cpl_time_obj.set_dur((dur-loop_loopend)+offset)
					cpl_time_obj.set_loop_data(loop_loopstart, loop_loopstart, loop_loopend)
					new_data.append(cutplpl_obj)

			else:
				position = oldtime_obj.get_pos()
				outeq = oldtime_obj.get_dur()
				cut_start = oldtime_obj.get_offset()

				if oldtime_obj.cut_type == 'loop_eq': 
					dur = outeq+cut_start
				elif oldtime_obj.cut_type == 'loop_adv_off': 
					durr = cut_start-(loop_loopend-loop_loopstart)
					dur = outeq+cut_start-durr
				else: 
					dur = outeq

				for cutpoint in xtramath.cutloop(oldtime_obj.get_pos(), dur, loop_start, loop_loopstart, loop_loopend):
					cutplpl_obj = copy.deepcopy(oldpl_obj)
					cpl_time_obj = cutplpl_obj.time
					cpl_time_obj.cut_type = 'cut'
					cpl_time_obj.set_pos(cutpoint[0])
					cpl_time_obj.set_dur(cutpoint[1])
					cpl_time_obj.set_offset(cutpoint[2])
					new_data.append(cutplpl_obj)
		else: new_data.append(oldpl_obj)
	return new_data

def internal_sort(pldata):
	ta_bsort = {}
	ta_sorted = {}
	new_a = []
	for n in pldata:
		n_time = n.time
		pos = n_time.get_pos()
		if pos not in ta_bsort: ta_bsort[pos] = []
		ta_bsort[pos].append(n)
	ta_sorted = dict(sorted(ta_bsort.items(), key=lambda item: item[0]))
	for p in ta_sorted:
		for note in ta_sorted[p]: new_a.append(note)
	return new_a

def internal_get_dur(pldata):
	duration_final = 0
	for pl in pldata:
		pl_end = pl.time.get_end()
		if duration_final < pl_end: duration_final = pl_end
	return duration_final

def internal_get_start(pldata):
	start_final = 100000000000000000
	for pl in self.data:
		pl_start = curpl_time.get_pos()
		if pl_start < start_final: start_final = pl_start
	return start_final

def internal_eq_content(pl, prev):
	curpl_time = pl.time
	prevpl_time = prev.time
	isvalid_b = curpl_time.cut_type==prevpl_time.cut_type
	isvalid_c = curpl_time.get_offset()==prevpl_time.get_offset()
	isvalid_d = curpl_time.get_loopstart()==prevpl_time.get_loopstart()
	isvalid_e = curpl_time.get_loopend()==prevpl_time.get_loopend()
	isvalid_f = pl.muted==prev.muted
	return isvalid_b & isvalid_c & isvalid_d & isvalid_e & isvalid_f

def internal_eq_connect(pl, prev, loopcompat):
	curpl_time = pl.time
	prevpl_time = prev.time
	isvalid_b = curpl_time.cut_type in ['none', 'cut']
	isvalid_c = (prevpl_time.get_end()-curpl_time.get_pos())==0
	isvalid_d = prevpl_time.cut_type in ['none', 'cut']
	isvalid_e = ('loop_adv' in loopcompat) if curpl_time.cut_type == 'cut' else True
	isvalid_f = curpl_time.get_dur()==prevpl_time.get_dur()
	return isvalid_b & isvalid_c & isvalid_d & isvalid_e & isvalid_f

def internal_tempo_calc(placements):
	for pl_obj in placements:
		time_obj = pl_obj.time
		time_obj.realtime_tempo = time_obj.position.get_tempo(time_obj.time_ppq)

def internal_tempo_calc_audio(placements):
	for pl_obj in placements:
		time_obj = pl_obj.time
		time_obj.realtime_tempo = time_obj.position.get_tempo(time_obj.time_ppq)
		stretch_obj = pl_obj.sample.stretch
		stretch_timing = stretch_obj.timing
		if stretch_timing.time_type == 'real_rate': 
			stretch_timing.original_bpm = time_obj.realtime_tempo

class cvpj_placement_fade:
	__slots__ = ['dur','time_type','skew','slope']

	def __init__(self):
		self.dur = 0
		self.time_type = 'seconds'
		self.skew = 0
		self.slope = 0

	def clear(self):
		self.dur = 0
		self.time_type = 'seconds'
		self.skew = 0
		self.slope = 0

	def set_dur(self, dur, time_type):
		self.dur = dur
		self.time_type = time_type

	def get_dur_beat(self, tempo):
		if self.time_type == 'seconds': return self.dur*(tempo/120)*2
		if self.time_type == 'beats': return self.dur

	def get_dur_seconds(self, tempo):
		if self.time_type == 'beats': return self.dur/(tempo/120)/2
		if self.time_type == 'seconds': return self.dur

#					|_______|_______|_______|_______|_______|_______|_______|_______|
#	loop			Start/LoopStart                                                 LoopEnd
#	loop_eq							Start/LoopStart                                 LoopEnd
#	loop_off		LoopStart                       Start                           LoopEnd
#	loop_adv		Start                           LoopStart                       LoopEnd
#	loop_adv_off	        Start                   LoopStart                       LoopEnd

class cvpj_placement_timing:
	#__slots__ = ['position','duration','position_real','duration_real',
	#'cut_type','cut_start','cut_loopstart','cut_loopend',
	#'time_ppq','position_timemode','duration_timemode','content_timemode']
	def __init__(self, time_ppq):
		self.time_ppq = time_ppq

		self.position = time.time_position()
		self.duration = time.time_duration()

		self.cut_type = 'none'
		self.cut_start = time.time_duration()
		self.cut_loopstart = time.time_duration()
		self.cut_loopend = time.time_duration()

		self.realtime_tempo = 120

	# ---------------- Position ----------------

	def set_pos(self, pos):
		self.position.set(pos, 'ppq')
 
	def get_pos(self):
		return self.position.get('ppq', self.time_ppq)

	def calc_pos_add(self, val):
		self.position.calc_add('ppq', val, self.time_ppq, self.realtime_tempo)

	# ---------------- Duration ----------------

	def set_dur(self, dur):
		self.duration.set(dur, 'ppq')
 
	def get_dur(self):
		return self.duration.get('ppq', self.time_ppq, self.realtime_tempo)

	def set_block_dur(self, durval, blksize):
		dur = (durval/blksize).__ceil__()*blksize
		self.duration.set(dur, 'ppq')

	def calc_dur_add(self, val):
		self.duration.calc_add('ppq', val, self.time_ppq, self.realtime_tempo)

	# ---------------- Offset ----------------

	def set_offset(self, offset):
		if offset:
			self.cut_type = 'cut'
			self.cut_start.set(offset, 'ppq')

	def set_offset_real(self, offset):
		if offset:
			self.cut_type = 'cut'
			self.cut_start.set(offset, 'seconds')

	def get_offset(self):
		return self.cut_start.get('ppq', self.time_ppq, self.realtime_tempo)

	def get_offset_real(self):
		return self.cut_start.get('seconds', self.time_ppq, self.realtime_tempo)

	def calc_offset_add(self, val):
		self.cut_start.calc_add('ppq', val, self.time_ppq, self.realtime_tempo)

	# ---------------- Both ----------------

	def set_posdur(self, pos, dur):
		self.position.set(pos, 'ppq')
		self.duration.set(dur, 'ppq')
 
	def set_posdur_real(self, pos, dur):
		self.position.set(pos, 'seconds')
		self.duration.set(dur, 'seconds')
 
	def get_posdur(self):
		return self.position.get('ppq', self.time_ppq), self.duration.get('ppq', self.time_ppq, self.realtime_tempo)

	def get_posdur_real(self):
		posstart = self.position.get('seconds', self.time_ppq)
		durstart = self.duration.get('seconds', self.time_ppq, self.realtime_tempo)
		return posstart, durstart

	def set_block_posdur(self, pos, blocksize):
		self.set_posdur(pos*blocksize, blocksize)

	# ---- startend

	def set_startend(self, start, end):
		self.set_posdur(start, end-start)

	def get_startend(self):
		posstart = self.position.get('ppq', self.time_ppq)
		durstart = self.duration.get('ppq', self.time_ppq, self.realtime_tempo)
		return posstart, posstart+durstart

	def get_end(self):
		return self.get_pos()+self.get_dur()

	def set_startend_real(self, start, end):
		self.set_posdur_real(start, end-start)

	def get_startend_real(self):
		posstart = self.position.get('seconds', self.time_ppq)
		durstart = self.duration.get('seconds', self.time_ppq, self.realtime_tempo)
		return posstart, posstart+durstart

	# ---------------- Loop ----------------

	def set_loop_data(self, start, loopstart, loopend):
		if start and start==loopstart: self.cut_type = 'loop_eq'
		elif loopstart and start: self.cut_type = 'loop_adv_off'
		elif loopstart: self.cut_type = 'loop_adv'
		elif start: self.cut_type = 'loop_off'
		elif loopend: self.cut_type = 'loop'
		self.cut_start.set(start, 'ppq')
		self.cut_loopstart.set(loopstart, 'ppq')
		self.cut_loopend.set(loopend, 'ppq')

	def get_loop_data(self):
		loop_start = self.cut_start.get('ppq', self.time_ppq, self.realtime_tempo)
		loop_loopstart = self.cut_loopstart.get('ppq', self.time_ppq, self.realtime_tempo)
		loop_loopend = self.cut_loopend.get('ppq', self.time_ppq, self.realtime_tempo)
		if loop_loopend==0: loop_loopend = self.duration.get('ppq', self.time_ppq, self.realtime_tempo)
		return loop_start, loop_loopstart, loop_loopend

	def get_loopstart(self):
		return self.cut_loopstart.get('ppq', self.time_ppq, self.realtime_tempo)

	def get_loopend(self):
		return self.cut_loopend.get('ppq', self.time_ppq, self.realtime_tempo)

	def loop_scale(self, v):
		self.cut_start.calc_mul('ppq', v, self.time_ppq, self.realtime_tempo)
		self.cut_loopstart.calc_mul('ppq', v, self.time_ppq, self.realtime_tempo)
		self.cut_loopend.calc_mul('ppq', v, self.time_ppq, self.realtime_tempo)

	def loop_shift(self, v):
		self.cut_start.calc_add('ppq', v, self.time_ppq, self.realtime_tempo)
		self.cut_loopstart.calc_add('ppq', v, self.time_ppq, self.realtime_tempo)
		self.cut_loopend.calc_add('ppq', v, self.time_ppq, self.realtime_tempo)

	def get_loopcount(self):
		pos = self.position.get('seconds', self.time_ppq)
		dur = self.duration.get('seconds', self.time_ppq, self.realtime_tempo)
		return pos, pos+dur

	def calc_loopstart_add(self, val):
		self.cut_loopstart.calc_add('ppq', val, self.time_ppq, self.realtime_tempo)

	def calc_loopend_add(self, val):
		self.cut_loopend.calc_add('ppq', val, self.time_ppq, self.realtime_tempo)

	# ---------------- Other ----------------

	def copy(self):
		return copy.deepcopy(self)

	def change_timing(self, old_ppq, new_ppq):
		self.position.change_ppq(old_ppq, new_ppq)
		self.duration.change_ppq(old_ppq, new_ppq)
		self.cut_start.change_ppq(old_ppq, new_ppq)
		self.cut_loopstart.change_ppq(old_ppq, new_ppq)
		self.cut_loopend.change_ppq(old_ppq, new_ppq)
		self.time_ppq = new_ppq

	def change_seconds(self, is_seconds, bpm, ppq):
		if is_seconds:
			self.position.convert('seconds', ppq)
			self.duration.convert('seconds', ppq, self.realtime_tempo)
		else:
			self.position.convert('ppq', ppq)
			self.duration.convert('ppq', ppq, self.realtime_tempo)
		
class cvpj_placements:
	__slots__ = ['pl_midi','pl_notes','pl_audio','pl_notes_indexed','pl_audio_indexed','pl_audio_nested','pl_video','pl_custom','notelist','midievents','time_ppq','uses_placements','is_indexed']
	def __init__(self, time_ppq, uses_placements, is_indexed):
		self.uses_placements = uses_placements
		self.is_indexed = is_indexed
		self.time_ppq = time_ppq

		self.notelist = notelist.cvpj_notelist(time_ppq)
		self.midievents = midievents.midievents()

		self.pl_midi = placements_midi.cvpj_placements_midi(self.time_ppq)

		self.pl_notes = placements_notes.cvpj_placements_notes(self.time_ppq)
		self.pl_audio = placements_audio.cvpj_placements_audio(self.time_ppq)

		self.pl_notes_indexed = placements_index.cvpj_placements_index(self.time_ppq)
		self.pl_audio_indexed = placements_index.cvpj_placements_index(self.time_ppq)

		self.pl_audio_nested = placements_audio.cvpj_placements_nested_audio(self.time_ppq)

		self.pl_video = placements_video.cvpj_placements_video(self.time_ppq)
		self.pl_custom = placements_custom.cvpj_placements_custom(self.time_ppq)

	def do_tempo(self, get_pos_temp):
		internal_tempo_calc(self.pl_midi.data)
		internal_tempo_calc(self.pl_notes.data)
		internal_tempo_calc_audio(self.pl_audio.data)
		internal_tempo_calc(self.pl_notes_indexed.data)
		internal_tempo_calc(self.pl_audio_indexed.data)
		internal_tempo_calc(self.pl_audio_nested.data)
		internal_tempo_calc(self.pl_video.data)
		internal_tempo_calc(self.pl_custom.data)

	def sort(self):
		self.pl_notes.sort()
		self.pl_audio.sort()
		self.pl_notes_indexed.sort()
		self.pl_audio_indexed.sort()
		self.pl_audio_nested.sort()
		self.pl_video.sort()
		self.pl_custom.sort()

	def autosplit(self):
		self.pl_notes.autosplit(self.time_ppq)

	def merge_crop(self, pl_obj, pos, dur, visualfill, groupid):
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (type(self.time_ppq)==type(pl_obj.time_ppq)):
			self.pl_notes.merge_crop(pl_obj.pl_notes, pos, dur, visualfill)
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (type(self.time_ppq)==type(pl_obj.time_ppq)):
			self.pl_audio.merge_crop(pl_obj.pl_audio, pos, dur, visualfill, groupid)

	def merge_crop_nestedaudio(self, pl_obj, pos, dur, visualfill):
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (type(self.time_ppq)==type(pl_obj.time_ppq)):
			self.pl_notes.merge_crop(pl_obj.pl_notes, pos, dur, visualfill)
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (type(self.time_ppq)==type(pl_obj.time_ppq)):
			placement_obj = self.add_nested_audio()
			placement_obj.time.set_posdur(pos, dur)
			placement_obj.events = copy.deepcopy(pl_obj.pl_audio)
			if visualfill: placement_obj.visual = visualfill

	def get_dur(self):
		#print(self.pl_notes.get_dur(),self.pl_audio.get_dur(),self.notelist.get_dur())
		return max(self.pl_notes.get_dur(),self.pl_audio.get_dur(),self.pl_notes_indexed.get_dur(),self.pl_audio_indexed.get_dur(),self.notelist.get_dur())

	def get_start(self):
		outcount = min(self.pl_notes.get_start(),self.pl_audio.get_start())
		if self.notelist.count(): outcount = min(self.notelist.get_start_end()[0], outcount)
		return outcount

	def change_seconds(self, is_seconds, bpm, ppq):
		self.pl_notes.change_seconds(is_seconds, bpm, ppq)
		self.pl_audio.change_seconds(is_seconds, bpm, ppq)
		self.pl_custom.change_seconds(is_seconds, bpm, ppq)
		self.pl_video.change_seconds(is_seconds, bpm, ppq)
		self.pl_midi.change_seconds(is_seconds, bpm, ppq)

	def remove_cut(self):
		self.pl_notes.remove_cut()

	def remove_loops(self, out__placement_loop):
		self.pl_notes.remove_loops(out__placement_loop)
		self.pl_midi.remove_loops(out__placement_loop)
		self.pl_audio.remove_loops(out__placement_loop)
		self.pl_audio_nested.remove_loops(out__placement_loop)
		self.pl_notes_indexed.remove_loops(out__placement_loop)
		self.pl_audio_indexed.remove_loops(out__placement_loop)
		self.pl_video.remove_loops(out__placement_loop)
		self.pl_custom.remove_loops(out__placement_loop)

	def add_loops(self, loopcompat):
		self.pl_notes.add_loops(loopcompat)
		self.pl_notes_indexed.add_loops(loopcompat)
		#self.pl_audio.add_loops(loopcompat)
		self.pl_audio_indexed.add_loops(loopcompat)

	def add_notes(self): return self.pl_notes.add(self.time_ppq)

	def add_notes_timed(self, time_ppq): return self.pl_notes.add(time_ppq)

	def add_audio(self): return self.pl_audio.add()

	def add_notes_indexed(self): return self.pl_notes_indexed.add()

	def add_audio_indexed(self): return self.pl_audio_indexed.add()

	def add_video(self): return self.pl_video.add()

	def add_midi(self): return self.pl_midi.add(self.time_ppq)

	def add_custom(self): return self.pl_custom.add()

	#def all_stretch_set_pitch_nonsync(self):
	#	if not self.is_indexed: 
	#		self.pl_audio.all_stretch_set_pitch_nonsync()
	#		for x in self.pl_audio_nested: 
	#			for i in x.events: 
	#				i.all_stretch_set_pitch_nonsync()

	def changestretch(self, convproj_obj, target, tempo):
		if not self.is_indexed: 
			self.pl_audio.changestretch(convproj_obj, target, tempo)
			for x in self.pl_audio_nested: 
				for i in x.events: 
					i.changestretch(convproj_obj, target, tempo)

	def change_timings(self, time_ppq):
		self.notelist.change_timings(time_ppq)

		self.pl_notes.change_timings(time_ppq, self.is_indexed)
		self.pl_notes.change_timings(time_ppq, self.is_indexed)
		self.pl_audio.change_timings(time_ppq)
		self.pl_midi.change_timings(time_ppq)
		self.pl_notes_indexed.change_timings(time_ppq)
		self.pl_audio_indexed.change_timings(time_ppq)
		self.pl_audio_nested.change_timings(time_ppq)
		self.pl_video.change_timings(time_ppq)
		self.pl_custom.change_timings(time_ppq)

		self.time_ppq = time_ppq

	def add_inst_to_notes(self, inst):
		for x in self.pl_notes:
			x.notelist.inst_all(inst)

	def used_insts(self):
		used_insts = []
		for notespl_obj in self.pl_notes: 

			for instid in notespl_obj.notelist.get_used_inst():
				if instid not in used_insts: used_insts.append(instid)

		for instid in self.notelist.get_used_inst():
			if instid not in used_insts: used_insts.append(instid)

		return used_insts

	def inst_split(self):
		splitted_pl = {}
		for notespl_obj in self.pl_notes: notespl_obj.inst_split(splitted_pl)
		return splitted_pl

	def unindex_notes(self, notelist_index):
		for indexpl_obj in self.pl_notes_indexed:
			new_notespl_obj = placements_notes.cvpj_placement_notes(self.time_ppq)
			new_notespl_obj.time = indexpl_obj.time.copy()
			new_notespl_obj.muted = indexpl_obj.muted

			if indexpl_obj.fromindex in notelist_index:
				nle_obj = notelist_index[indexpl_obj.fromindex]
				new_notespl_obj.notelist = copy.deepcopy(nle_obj.notelist)
				new_notespl_obj.visual = nle_obj.visual
				new_notespl_obj.timesig_auto = nle_obj.timesig_auto.copy()
				new_notespl_obj.timemarkers = nle_obj.timemarkers.copy()

			self.pl_notes.data.append(new_notespl_obj)
		self.pl_notes_indexed = placements_index.cvpj_placements_index(self.time_ppq)
		self.is_indexed = False

	def unindex_audio(self, sample_index):
		for indexpl_obj in self.pl_audio_indexed:
			apl_obj = placements_audio.cvpj_placement_audio(self.time_ppq)

			if indexpl_obj.fromindex in sample_index:
				sle_obj = sample_index[indexpl_obj.fromindex]
				apl_obj.time = indexpl_obj.time.copy()
				apl_obj.muted = indexpl_obj.muted
				apl_obj.fade_in = indexpl_obj.fade_in
				apl_obj.fade_out = indexpl_obj.fade_out
				
				apl_obj.visual = sle_obj.visual
				apl_obj.sample = copy.deepcopy(sle_obj)

				apl_obj.sample.vol *= indexpl_obj.vol
				self.pl_audio.data.append(apl_obj)

		self.pl_audio_indexed = placements_index.cvpj_placements_index(self.time_ppq)
		self.is_indexed = False

	def to_indexed_notes(self, existingpatterns, pattern_number):
		existingpatterns = []
		self.pl_notes_indexed = placements_index.cvpj_placements_index(self.time_ppq)

		for notepl_obj in self.pl_notes:
			nle_data = [notepl_obj.notelist, notepl_obj.visual.name, notepl_obj.visual.color]

			dupepatternfound = None
			for existingpattern in existingpatterns:
				if existingpattern[1] == nle_data: 
					dupepatternfound = existingpattern[0]
					break

			if dupepatternfound == None:
				patid = 'm2mi_' + str(pattern_number)
				existingpatterns.append([patid, nle_data])
				dupepatternfound = patid
				pattern_number += 1

			new_index_obj = placements_index.cvpj_placement_index(self.time_ppq)
			new_index_obj.time = notepl_obj.time.copy()
			new_index_obj.fromindex = dupepatternfound
			new_index_obj.muted = notepl_obj.muted

			self.pl_notes_indexed.data.append(new_index_obj)

		self.is_indexed = True
		self.pl_notes = placements_notes.cvpj_placements_notes(self.time_ppq)
		return existingpatterns, pattern_number

	def to_indexed_audio(self, existingsamples, sample_number):
		new_data_audio = []
		self.pl_audio_indexed = placements_index.cvpj_placements_index(self.time_ppq)

		for audiopl_obj in self.pl_audio:
			sle_obj = audiopl_obj.sample

			dupepatternfound = None
			for existingsample in existingsamples:
				if existingsample[1] == sle_obj: 
					dupepatternfound = existingsample[0]
					break

			if dupepatternfound == None:
				patid = 'm2mi_audio_' + str(sample_number)
				existingsamples.append([patid, sle_obj])
				dupepatternfound = patid
				sample_number += 1

			new_index_obj = placements_index.cvpj_placement_index(self.time_ppq)
			new_index_obj.time = audiopl_obj.time.copy()
			new_index_obj.fromindex = dupepatternfound
			new_index_obj.muted = audiopl_obj.muted
			self.pl_audio_indexed.data.append(new_index_obj)

		self.pl_audio = placements_audio.cvpj_placements_audio(self.time_ppq)
		return existingsamples, sample_number

	def add_nested_audio(self):
		return self.pl_audio_nested.add()

	def add_fxrack_channel(self, fxnum):
		if not self.is_indexed:
			for pl_obj in self.pl_audio:
				if pl_obj.sample.fxrack_channel == -1: 
					pl_obj.sample.fxrack_channel = fxnum
			for nestedpl_obj in self.pl_audio_nested:
				for e in nestedpl_obj.events:
					e.sample.fxrack_channel = fxnum

	def remove_nested(self):

		self.pl_audio_nested.remove_loops([])
		for nestedpl_obj in self.pl_audio_nested:
			nest_time_obj = nestedpl_obj.time
			main_s = nest_time_obj.cut_start
			main_e = nest_time_obj.duration+main_s
			basepos = nest_time_obj.position

			#print('PL', end=' ')
			#for x in [main_s, main_e]:
			#	print(str(x).ljust(19), end=' ')
			#print()

			for e in nestedpl_obj.events:
				e_time_obj = e.time
				event_s = e_time_obj.position
				event_et = e_time_obj.duration
				event_e = e_time_obj.position+event_et
				event_o = e_time_obj.cut_start

				if main_e>=event_s and main_s<=event_e:
					out_start = max(main_s, event_s)
					out_end = min(main_e, event_e)

					scs = out_start-event_s
					
					if False:
						print('E ', end='| ')
						for x in [main_s+event_o, main_e]: print(str(round(x, 4)).ljust(7), end=' ')
						print('|', end=' ')
						for x in [event_s, event_e]: print(str(round(x, 4)).ljust(7), end=' ')
						print('|', end=' ')
						for x in [out_start, out_end]: print(str(round(x, 4)).ljust(7), end=' ')
						print('|', end=' ')
						for x in [scs]: print(str(round(x, 4)).ljust(7), end=' ')
						print()

					cutplpl_obj = copy.deepcopy(e)

					cpl_time_obj = cutplpl_obj.time
					cpl_time_obj.position = (out_start+basepos)-main_s
					sco = out_start-event_o
					offset_d = (main_e-main_s)-sco
					cpl_time_obj.duration = min(max(out_end-out_start, offset_d), event_et)
					cpl_time_obj.cut_type = 'cut'
					cpl_time_obj.cut_start += scs

					cutplpl_obj.muted = cutplpl_obj.muted or nestedpl_obj.muted
					if not cutplpl_obj.visual.name: 
						cutplpl_obj.visual.name = nestedpl_obj.visual.name
					self.pl_audio.data.append(cutplpl_obj)

		self.pl_audio_nested = placements_audio.cvpj_placements_nested_audio(self.time_ppq)

	def debugtxt(self):
		print(len(self.notelist.nl), end='|')
		print(str(len(self.pl_notes.data))+'-'+str(len(self.pl_audio.data)), end='|')
		print(str(len(self.pl_notes_indexed.data))+'-'+str(len(self.pl_audio_indexed.data)))
