# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import project as convproj
from functions import xtramath
import copy

from objects.convproj import notelist
from objects.convproj import tracks

from objects.convproj import placements_notes
from objects.convproj import placements_audio
from objects.convproj import placements_index
from objects.convproj import time

def internal_addloops(pldata, eq_connect, loopcompat):
	old_data = copy.deepcopy(pldata)
	new_data = []

	prev = None
	for pl in old_data:
		if not eq_connect(pl, prev, loopcompat):
			new_data.append(pl)
		else:
			prevreal = new_data[-1]
			prevreal.time.duration += pl.time.duration
			if prevreal.time.cut_type == 'none': 
				prevreal.time.cut_type = 'loop'
				prevreal.time.cut_loopend = pl.time.duration
			if 'loop_adv' in loopcompat:
				if prevreal.time.cut_type == 'cut': 
					prevreal.time.cut_type = 'loop_off'
					prevreal.time.cut_loopstart = pl.time.cut_start
					prevreal.time.cut_loopend = pl.time.duration+pl.time.cut_start
		prev = pl

	return new_data

def internal_removeloops(pldata, out__placement_loop):
	new_data = []
	for oldpl_obj in pldata: 
		if oldpl_obj.time.cut_type in ['loop', 'loop_off', 'loop_adv'] and oldpl_obj.time.cut_type not in out__placement_loop:
			loop_start, loop_loopstart, loop_loopend = oldpl_obj.time.get_loop_data()
			for cutpoint in xtramath.cutloop(oldpl_obj.time.position, oldpl_obj.time.duration, loop_start, loop_loopstart, loop_loopend):
				cutplpl_obj = copy.deepcopy(oldpl_obj)
				cutplpl_obj.time.position = cutpoint[0]
				cutplpl_obj.time.duration = cutpoint[1]
				cutplpl_obj.time.cut_type = 'cut'
				cutplpl_obj.time.cut_start = cutpoint[2]
				new_data.append(cutplpl_obj)
		else: new_data.append(oldpl_obj)
	return new_data

def internal_sort(pldata):
	ta_bsort = {}
	ta_sorted = {}
	new_a = []
	for n in self.data:
		if n.time.position not in ta_bsort: ta_bsort[n.time.position] = []
		ta_bsort[n.time.position].append(n)
	ta_sorted = dict(sorted(ta_bsort.items(), key=lambda item: item[0]))
	for p in ta_sorted:
		for note in ta_sorted[p]: new_a.append(note)
	return new_a


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
#	loop_off		LoopStart                       Start                           LoopEnd
#	loop_adv		Start                           LoopStart                       LoopEnd
#	loop_adv_off	        Start                   LoopStart                       LoopEnd




class cvpj_placement_timing:
	__slots__ = ['position','duration','position_real','duration_real','cut_type','cut_start','cut_loopstart','cut_loopend']
	def __init__(self):
		self.position = 0
		self.duration = 0
		self.position_real = None
		self.duration_real = None
		self.cut_type = 'none'
		self.cut_start = 0
		self.cut_loopstart = 0
		self.cut_loopend = -1

	def set_block_dur(self, durval, blksize):
		self.duration = (durval/blksize).__ceil__()*blksize
		self.duration_real = None

	def set_posdur(self, pos, dur):
		self.position = pos
		self.duration = dur
		self.position_real = None
		self.duration_real = None
 
	def set_startend(self, start, end):
		self.set_posdur(start, end-start)

	def set_block_posdur(self, pos, blocksize):
		self.set_posdur(pos*blocksize, blocksize)

	def set_offset(self, offset):
		if offset:
			self.cut_type = 'cut'
			self.cut_start = offset

	def copy(self):
		return copy.deepcopy(self)

	def change_timing(self, old_ppq, new_ppq, is_float):
		self.position = xtramath.change_timing(old_ppq, new_ppq, is_float, self.position)
		self.duration = xtramath.change_timing(old_ppq, new_ppq, is_float, self.duration)
		self.cut_start = xtramath.change_timing(old_ppq, new_ppq, is_float, self.cut_start)
		self.cut_loopstart = xtramath.change_timing(old_ppq, new_ppq, is_float, self.cut_loopstart)
		self.cut_loopend = xtramath.change_timing(old_ppq, new_ppq, is_float, self.cut_loopend)

	def set_loop_data(self, start, loopstart, loopend):
		if loopstart and start: self.cut_type = 'loop_adv_off'
		elif loopstart: self.cut_type = 'loop_adv'
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

	def loop_scale(self, v):
		self.cut_start *= v
		self.cut_loopstart *= v
		self.cut_loopend *= v

	def loop_shift(self, v):
		self.cut_start += v
		self.cut_loopstart += v
		self.cut_loopend += v

	def get_end(self):
		return self.position+self.duration

	def change_seconds(self, is_seconds, bpm, ppq):
		if is_seconds:
			self.position_real = xtramath.step2sec(self.position, bpm)/(ppq/4)
			self.duration_real = xtramath.step2sec(self.duration, bpm)/(ppq/4)
		else:
			self.position = xtramath.sec2step(self.position_real, bpm)
			self.duration = xtramath.sec2step(self.duration_real, bpm)
		
class cvpj_placements:
	__slots__ = ['pl_notes','pl_audio','pl_notes_indexed','pl_audio_indexed','pl_audio_nested','notelist','time_ppq','time_float','uses_placements','is_indexed']
	def __init__(self, time_ppq, time_float, uses_placements, is_indexed):
		self.uses_placements = uses_placements
		self.is_indexed = is_indexed
		self.time_ppq = time_ppq
		self.time_float = time_float

		self.notelist = notelist.cvpj_notelist(time_ppq, time_float)

		self.pl_notes = placements_notes.cvpj_placements_notes()
		self.pl_audio = placements_audio.cvpj_placements_audio()

		self.pl_notes_indexed = placements_index.cvpj_placements_index()
		self.pl_audio_indexed = placements_index.cvpj_placements_index()

		self.pl_audio_nested = placements_audio.cvpj_placements_nested_audio()

	def sort(self):
		self.pl_notes.sort()
		self.pl_audio.sort()
		self.pl_notes_indexed.sort()
		self.pl_audio_indexed.sort()
		self.pl_audio_nested.sort()

	def autosplit(self):
		self.pl_notes.autosplit(self.time_ppq)

	def merge_crop(self, pl_obj, pos, dur, visualfill):
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (self.time_float==pl_obj.time_float):
			self.pl_notes.merge_crop(pl_obj.pl_notes, pos, dur, visualfill)
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (self.time_float==pl_obj.time_float):
			self.pl_audio.merge_crop(pl_obj.pl_audio, pos, dur, visualfill)

	def merge_crop_nestedaudio(self, pl_obj, pos, dur, visualfill):
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (self.time_float==pl_obj.time_float):
			self.pl_notes.merge_crop(pl_obj.pl_notes, pos, dur, visualfill)
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (self.time_float==pl_obj.time_float):
			placement_obj = self.add_nested_audio()
			placement_obj.time.set_posdur(pos, dur)
			placement_obj.events = copy.deepcopy(pl_obj.pl_audio)
			if visualfill: placement_obj.visual = visualfill

	def get_dur(self):
		#print(self.pl_notes.get_dur(),self.pl_audio.get_dur(),self.notelist.get_dur())
		return max(self.pl_notes.get_dur(),self.pl_audio.get_dur(),self.pl_notes_indexed.get_dur(),self.pl_audio_indexed.get_dur(),self.notelist.get_dur())

	def get_start(self):
		return min(self.pl_notes.get_start(),self.pl_audio.get_start(),self.notelist.get_start_end()[0])

	def change_seconds(self, is_seconds, bpm, ppq):
		self.pl_notes.change_seconds(is_seconds, bpm, ppq)
		self.pl_audio.change_seconds(is_seconds, bpm, ppq)

	def remove_cut(self):
		self.pl_notes.remove_cut()

	def remove_loops(self, out__placement_loop):
		self.pl_notes.remove_loops(out__placement_loop)
		self.pl_audio.remove_loops(out__placement_loop)
		self.pl_audio_nested.remove_loops(out__placement_loop)
		self.pl_notes_indexed.remove_loops(out__placement_loop)
		self.pl_audio_indexed.remove_loops(out__placement_loop)

	def add_loops(self, loopcompat):
		self.pl_notes.add_loops(loopcompat)
		self.pl_notes_indexed.add_loops(loopcompat)
		#self.pl_audio.add_loops(loopcompat)
		self.pl_audio_indexed.add_loops(loopcompat)

	def add_notes(self): return self.pl_notes.add(self.time_ppq, self.time_float)

	def add_notes_timed(self, time_ppq, time_float): return self.pl_notes.add(time_ppq, time_float)

	def add_audio(self): return self.pl_audio.add()

	def add_notes_indexed(self): return self.pl_notes_indexed.add()

	def add_audio_indexed(self): return self.pl_audio_indexed.add()

	def all_stretch_set_pitch_nonsync(self):
		if not self.is_indexed: 
			self.pl_audio.all_stretch_set_pitch_nonsync()
			for x in self.pl_audio_nested: 
				for i in x.events: 
					i.all_stretch_set_pitch_nonsync()

	def changestretch(self, convproj_obj, target, tempo):
		if not self.is_indexed: 
			self.pl_audio.changestretch(convproj_obj, target, tempo)
			for x in self.pl_audio_nested: 
				for i in x.events: 
					i.changestretch(convproj_obj, target, tempo)

	def change_timings(self, time_ppq, time_float):
		self.notelist.change_timings(time_ppq, time_float)

		for pl in self.pl_notes:
			pl.time.change_timing(self.time_ppq, time_ppq, time_float)
			if not self.is_indexed: 
				pl.notelist.change_timings(time_ppq, time_float)
				pl.timesig_auto.change_timings(time_ppq, time_float)
				pl.timemarkers.change_timings(time_ppq, time_float)
				for mpename, autodata in pl.auto.items():
					autodata.change_timings(time_ppq, time_float)

		for pl in self.pl_audio:
			pl.time.change_timing(self.time_ppq, time_ppq, time_float)
			if pl.auto:
				for mpename, autodata in pl.auto.items():
					autodata.change_timings(time_ppq, time_float)

		for pl in self.pl_notes_indexed:
			pl.time.change_timing(self.time_ppq, time_ppq, time_float)

		for pl in self.pl_audio_indexed:
			pl.time.change_timing(self.time_ppq, time_ppq, time_float)

		for pl in self.pl_audio_nested:
			pl.time.change_timing(self.time_ppq, time_ppq, time_float)
			for x in pl.events: x.time.change_timing(self.time_ppq, time_ppq, time_float)

		self.time_ppq = time_ppq
		self.time_float = time_float

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
			new_notespl_obj = placements_notes.cvpj_placement_notes(1, 1)
			new_notespl_obj.time = indexpl_obj.time.copy()
			new_notespl_obj.muted = indexpl_obj.muted

			if indexpl_obj.fromindex in notelist_index:
				nle_obj = notelist_index[indexpl_obj.fromindex]
				new_notespl_obj.notelist = copy.deepcopy(nle_obj.notelist)
				new_notespl_obj.visual = nle_obj.visual
				new_notespl_obj.timesig_auto = nle_obj.timesig_auto.copy()
				new_notespl_obj.timemarkers = nle_obj.timemarkers.copy()

			self.pl_notes.data.append(new_notespl_obj)
		self.pl_notes_indexed = placements_index.cvpj_placements_index()
		self.is_indexed = False

	def unindex_audio(self, sample_index):
		for indexpl_obj in self.pl_audio_indexed:
			apl_obj = placements_audio.cvpj_placement_audio()

			if indexpl_obj.fromindex in sample_index:
				sle_obj = sample_index[indexpl_obj.fromindex]
				apl_obj.time = indexpl_obj.time.copy()
				apl_obj.muted = indexpl_obj.muted
				apl_obj.fade_in = indexpl_obj.fade_in
				apl_obj.fade_out = indexpl_obj.fade_out
				
				apl_obj.visual = sle_obj.visual
				apl_obj.sample = sle_obj
				self.pl_audio.data.append(apl_obj)

		self.pl_audio_indexed = placements_index.cvpj_placements_index()
		self.is_indexed = False

	def to_indexed_notes(self, existingpatterns, pattern_number):
		existingpatterns = []
		self.pl_notes_indexed = placements_index.cvpj_placements_index()

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


			new_index_obj = placements_index.cvpj_placement_index()
			new_index_obj.time = notepl_obj.time.copy()
			new_index_obj.fromindex = dupepatternfound
			new_index_obj.muted = notepl_obj.muted

			self.pl_notes_indexed.data.append(new_index_obj)

		self.is_indexed = True
		self.pl_notes = placements_notes.cvpj_placements_notes()
		return existingpatterns, pattern_number

	def to_indexed_audio(self, existingsamples, sample_number):
		new_data_audio = []
		self.pl_audio_indexed = placements_index.cvpj_placements_index()

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

			new_index_obj = placements_index.cvpj_placement_index()
			new_index_obj.time = audiopl_obj.time.copy()
			new_index_obj.fromindex = dupepatternfound
			new_index_obj.muted = audiopl_obj.muted
			self.pl_audio_indexed.data.append(new_index_obj)

		self.pl_audio = placements_audio.cvpj_placements_audio()
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
		for nestedpl_obj in self.pl_audio_nested:
			main_s = nestedpl_obj.time.cut_start
			main_e = nestedpl_obj.time.duration+main_s
			basepos = nestedpl_obj.time.position

			#print('PL', end=' ')
			#for x in [main_s, main_e]:
			#	print(str(x).ljust(19), end=' ')
			#print()

			for e in nestedpl_obj.events:
				event_s = e.time.position
				event_et = e.time.duration
				event_e = e.time.position+event_et
				event_o = e.time.cut_start

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
					cutplpl_obj.time.position = (out_start+basepos)-main_s
					cutplpl_obj.time.duration = out_end-out_start
					cutplpl_obj.time.cut_type = 'cut'
					cutplpl_obj.time.cut_start += scs
					cutplpl_obj.muted = nestedpl_obj.muted
					if not cutplpl_obj.visual.name: 
						cutplpl_obj.visual.name = nestedpl_obj.visual.name
					self.pl_audio.data.append(cutplpl_obj)

		self.pl_audio_nested = placements_audio.cvpj_placements_nested_audio()

	def debugtxt(self):
		print(len(self.notelist.nl), end='|')
		print(str(len(self.pl_notes.data))+'-'+str(len(self.pl_audio.data)), end='|')
		print(str(len(self.pl_notes_indexed.data))+'-'+str(len(self.pl_audio_indexed.data)))
