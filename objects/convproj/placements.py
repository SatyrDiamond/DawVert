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

	def autosplit(self):
		self.pl_notes.autosplit(self.time_ppq)

	def merge_crop(self, pl_obj, pos, dur, visualfill):
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (self.time_float==pl_obj.time_float):
			self.pl_notes.merge_crop(pl_obj.pl_notes, pos, dur, visualfill)
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (self.time_float==pl_obj.time_float):
			self.pl_audio.merge_crop(pl_obj.pl_audio, pos, dur, visualfill)


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

	def changestretch(self, convproj_obj, target, tempo):
		if not self.is_indexed: 
			for x in self.pl_audio: 
				x.changestretch(convproj_obj, target, tempo)

	def change_timings(self, time_ppq, time_float):
		self.notelist.change_timings(time_ppq, time_float)

		for pl in self.pl_notes:
			pl.position = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.position)
			pl.duration = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.duration)
			pl.cut_start = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_start)
			pl.cut_loopstart = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_loopstart)
			pl.cut_loopend = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_loopend)
			if not self.is_indexed: pl.notelist.change_timings(time_ppq, time_float)

		for pl in self.pl_audio:
			pl.position = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.position)
			pl.duration = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.duration)
			pl.cut_start = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_start)
			pl.cut_loopstart = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_loopstart)
			pl.cut_loopend = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_loopend)

		for pl in self.pl_notes_indexed:
			pl.position = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.position)
			pl.duration = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.duration)
			pl.cut_start = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_start)
			pl.cut_loopstart = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_loopstart)
			pl.cut_loopend = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_loopend)

		for pl in self.pl_audio_indexed:
			pl.position = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.position)
			pl.duration = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.duration)
			pl.cut_start = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_start)
			pl.cut_loopstart = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_loopstart)
			pl.cut_loopend = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_loopend)

		for pl in self.pl_audio_nested:
			pl.position = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.position)
			pl.duration = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.duration)
			pl.cut_start = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_start)
			pl.cut_loopstart = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_loopstart)
			pl.cut_loopend = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_loopend)

		self.time_ppq = time_ppq
		self.time_float = time_float

	def add_inst_to_notes(self, inst):
		for x in self.pl_notes:
			x.notelist.used_inst = [inst]
			x.notelist.inst_all(inst)

	def used_insts(self):
		used_insts = []
		for notespl_obj in self.pl_notes: 
			used_insts += notespl_obj.notelist.get_used_inst()
		used_insts += self.notelist.get_used_inst()
		return list(set(used_insts))

	def inst_split(self):
		splitted_pl = {}
		for notespl_obj in self.pl_notes: notespl_obj.inst_split(splitted_pl)
		return splitted_pl

	def unindex_notes(self, notelist_index):
		for indexpl_obj in self.pl_notes_indexed:
			new_notespl_obj = placements_notes.cvpj_placement_notes(1, 1)
			new_notespl_obj.position = indexpl_obj.position
			new_notespl_obj.duration = indexpl_obj.duration
			new_notespl_obj.cut_type = indexpl_obj.cut_type
			new_notespl_obj.cut_start = indexpl_obj.cut_start
			new_notespl_obj.cut_loopstart = indexpl_obj.cut_loopstart
			new_notespl_obj.cut_loopend = indexpl_obj.cut_loopend
			new_notespl_obj.muted = indexpl_obj.muted

			if indexpl_obj.fromindex in notelist_index:
				nle_obj = notelist_index[indexpl_obj.fromindex]
				new_notespl_obj.notelist = copy.deepcopy(nle_obj.notelist)
				new_notespl_obj.visual = nle_obj.visual

			self.pl_notes.data.append(new_notespl_obj)
		self.pl_notes_indexed = placements_index.cvpj_placements_index()
		self.is_indexed = False

	def unindex_audio(self, sample_index):
		for indexpl_obj in self.pl_audio_indexed:
			apl_obj = placements_audio.cvpj_placement_audio()

			if indexpl_obj.fromindex in sample_index:
				sle_obj = sample_index[indexpl_obj.fromindex]
				apl_obj.position = indexpl_obj.position
				apl_obj.duration = indexpl_obj.duration
				apl_obj.cut_type = indexpl_obj.cut_type
				apl_obj.cut_start = indexpl_obj.cut_start
				apl_obj.cut_loopstart = indexpl_obj.cut_loopstart
				apl_obj.cut_loopend = indexpl_obj.cut_loopend
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
			new_index_obj.position = notepl_obj.position
			new_index_obj.duration = notepl_obj.duration
			new_index_obj.cut_type = notepl_obj.cut_type
			new_index_obj.cut_start = notepl_obj.cut_start
			new_index_obj.cut_loopstart = notepl_obj.cut_loopstart
			new_index_obj.cut_loopend = notepl_obj.cut_loopend
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
			new_index_obj.position = audiopl_obj.position
			new_index_obj.duration = audiopl_obj.duration
			new_index_obj.cut_type = audiopl_obj.cut_type
			new_index_obj.cut_start = audiopl_obj.cut_start
			new_index_obj.cut_loopstart = audiopl_obj.cut_loopstart
			new_index_obj.cut_loopend = audiopl_obj.cut_loopend
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
			main_s = nestedpl_obj.cut_start
			main_e = nestedpl_obj.duration+main_s
			basepos = nestedpl_obj.position

			#print('PL', end=' ')
			#for x in [main_s, main_e]:
			#	print(str(x).ljust(19), end=' ')
			#print()

			for e in nestedpl_obj.events:
				event_s, event_et = e.position, e.duration
				event_e = e.position+event_et
				event_o = e.cut_start

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
					cutplpl_obj.position = (out_start+basepos)-main_s
					cutplpl_obj.duration = out_end-out_start
					cutplpl_obj.cut_type = 'cut'
					cutplpl_obj.cut_start += scs
					self.pl_audio.data.append(cutplpl_obj)

		self.pl_audio_nested = placements_audio.cvpj_placements_nested_audio()

	def debugtxt(self):
		print(len(self.notelist.nl), end='|')
		print(str(len(self.pl_notes.data))+'-'+str(len(self.pl_audio.data)), end='|')
		print(str(len(self.pl_notes_indexed.data))+'-'+str(len(self.pl_audio_indexed.data)))
