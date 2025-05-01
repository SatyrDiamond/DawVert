# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
import copy
import math
import numpy as np
import os

from objects.convproj import placements
from objects.convproj import autopoints
from objects.convproj import visual
from objects.convproj import midievents
from objects.convproj import time

class cvpj_placements_midi:
	__slots__ = ['data','time_ppq','time_float']
	def __init__(self, time_ppq, time_float):
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.data = []

	def __iter__(self):
		for x in self.data: yield x

	def __len__(self):
		return self.data.__len__()

	def __bool__(self):
		return bool(self.data)

	def change_timings(self, time_ppq, time_float):
		for pl in self.data:
			pl.time.change_timing(self.time_ppq, time_ppq, time_float)
			for mpename, autodata in pl.auto.items():
				autodata.change_timings(time_ppq, time_float)
		self.time_ppq = time_ppq
		self.time_float = time_float

	def append(self, value):
		self.data.append(value)

	def check_overlap(self, start, end):
		for npl in self.data:
			if xtramath.overlap(start, start+end, npl.time.position, npl.time.position+npl.time.duration): return True
		return False

	def clear(self):
		self.data = []
		
	def add(self, time_ppq, time_float):
		pl_obj = cvpj_placement_midi(time_ppq, time_float)
		self.data.append(pl_obj)
		return pl_obj

	def sort(self):
		self.data = placements.internal_sort(self.data)

	def get_dur(self):
		duration_final = 0
		for pl in self.data:
			pl_end = pl.time.get_end()
			if duration_final < pl_end: duration_final = pl_end
		return duration_final

	def get_start(self):
		start_final = 100000000000000000
		for pl in self.data:
			pl_start = pl.time.position
			if pl_start < start_final: start_final = pl_start
		return start_final

	def change_seconds(self, is_seconds, bpm, ppq):
		for pl in self.data: 
			pl.time.change_seconds(is_seconds, bpm, ppq)
			for _, a in pl.auto.items(): a.change_seconds(is_seconds, bpm, ppq)
		
	def eq_content(self, pl, prev):
		if prev:
			isvalid_a = pl.events==prev.events
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
		old_data_midi = copy.deepcopy(self.data)
		new_data_midi = []

		prev = None
		for pl in old_data_midi:
			endpos = pl.time.duration+pl.time.position
			if prev:
				poevendpos = prev.time.duration+prev.time.position
				prev.time.duration = min(prev.time.duration, pl.time.position-prev.time.position)
			prev = pl
			new_data_midi.append(pl)

		self.data = new_data_midi

	def make_base_from_notes(self, notesp):
		plb_obj = cvpj_placement_midi(self.time_ppq, self.time_float)
		plb_obj.time = notesp.time.copy()
		plb_obj.time_ppq = notesp.time_ppq
		plb_obj.time_float = notesp.time_float
		plb_obj.muted = notesp.muted
		plb_obj.visual = notesp.visual
		plb_obj.group = notesp.group
		plb_obj.locked = notesp.locked
		self.data.append(plb_obj)
		return plb_obj

class cvpj_placement_midi:
	__slots__ = ['time','muted','visual','midievents','time_ppq','time_float','auto','group','locked']
	def __init__(self, time_ppq, time_float):
		self.time = placements.cvpj_placement_timing(time_ppq, time_float)
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.midievents = midievents.midievents()
		self.muted = False
		self.visual = visual.cvpj_visual()
		self.auto = {}
		self.group = None
		self.locked = False

	def make_base(self):
		plb_obj = cvpj_placement_midi(self.time_ppq, self.time_float)
		plb_obj.time = self.time.copy()
		plb_obj.time_ppq = self.time_ppq
		plb_obj.time_float = self.time_float
		plb_obj.muted = self.muted
		plb_obj.visual = self.visual
		plb_obj.group = self.group
		plb_obj.locked = self.locked
		return plb_obj

	def add_autopoints(self, a_type):
		self.auto[a_type] = autopoints.cvpj_autopoints(self.time_ppq, self.time_float, 'float')
		return self.auto[a_type]

	def midi_from(self, input_file):
		from objects_midi.parser import MidiFile
		from objects_midi import events as MidiEvents

		if os.path.exists(input_file):
			midifile = MidiFile.fromFile(input_file)

			events_obj = self.midievents
			events_obj.ppq = midifile.ppqn

			if midifile.tracks:
				for eventlist in midifile.tracks:
					curpos = 0
					for msg in eventlist.events:
						curpos += msg.deltaTime
						if type(msg) == MidiEvents.NoteOnEvent: events_obj.add_note_on(curpos, msg.channel, msg.note, msg.velocity)
						elif type(msg) == MidiEvents.NoteOffEvent: events_obj.add_note_off(curpos, msg.channel, msg.note, 0)
						elif type(msg) == MidiEvents.CopyrightEvent: events_obj.add_copyright(msg.copyright)
						elif type(msg) == MidiEvents.PitchBendEvent: events_obj.add_pitch(curpos, msg.channel, msg.pitch)
						elif type(msg) == MidiEvents.ControllerEvent: events_obj.add_control(curpos, msg.channel, msg.controller, msg.value)
						elif type(msg) == MidiEvents.ProgramEvent: events_obj.add_program(curpos, msg.channel, msg.program)
						elif type(msg) == MidiEvents.EndOfTrackEvent: break
						elif type(msg) == MidiEvents.TrackNameEvent:
							if not events_obj.track_name:
								events_obj.track_name = msg.name

