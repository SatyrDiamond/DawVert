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

	def change_timings(self, time_ppq):
		for pl in self.data:
			pl.time.change_timing(self.time_ppq, time_ppq)
			for mpename, autodata in pl.auto.items():
				autodata.change_timings(time_ppq)
		self.time_ppq = time_ppq

	def append(self, value):
		self.data.append(value)

	def check_overlap(self, start, end):
		for npl in self.data:
			npl_time = npl.time
			if xtramath.overlap(start, start+end, npl_time.get_pos(), npl_time.get_end()): return True
		return False

	def clear(self):
		self.data = []
		
	def add(self, time_ppq):
		pl_obj = cvpj_placement_midi(time_ppq)
		self.data.append(pl_obj)
		return pl_obj

	def sort(self):
		self.data = placements.internal_sort(self.data)

	def get_dur(self):
		return placements.internal_get_dur(self.data)

	def get_start(self):
		return placements.internal_get_start(self.data)

	def change_seconds(self, is_seconds, bpm, ppq):
		for pl in self.data: 
			pl.time.change_seconds(is_seconds, bpm, ppq)
			for _, a in pl.auto.items(): a.change_seconds(is_seconds, bpm, ppq)
		
	def eq_content(self, pl, prev):
		if prev:
			isvalid_a = pl.events==prev.events
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
		old_data_midi = copy.deepcopy(self.data)
		new_data_midi = []

		prev = None
		for pl in old_data_notes:
			time_obj = pl.time
			position, duration = time_obj.get_posdur_real()
			if prev: 
				prev_time_obj = prev.time
				prev_time_obj.set_dur( min(prev_time_obj.get_dur(), position-prev_time_obj.get_pos()) )
			prev = pl
			new_data_midi.append(pl)

		self.data = new_data_midi

	def make_base_from_notes(self, notesp):
		plb_obj = cvpj_placement_midi(self.time_ppq)
		plb_obj.time = notesp.time.copy()
		plb_obj.time_ppq = notesp.time_ppq
		plb_obj.muted = notesp.muted
		plb_obj.visual = notesp.visual
		plb_obj.group = notesp.group
		plb_obj.locked = notesp.locked
		self.data.append(plb_obj)
		return plb_obj

class cvpj_placement_midi:
	__slots__ = ['time','muted','visual','midievents','time_ppq','auto','group','locked','pitch']
	def __init__(self, time_ppq):
		self.time = placements.cvpj_placement_timing(time_ppq)
		self.time_ppq = time_ppq
		self.midievents = midievents.midievents()
		self.muted = False
		self.visual = visual.cvpj_visual()
		self.auto = {}
		self.group = None
		self.locked = False
		self.pitch = 0

	def make_base(self):
		plb_obj = cvpj_placement_midi(self.time_ppq)
		plb_obj.time = self.time.copy()
		plb_obj.time_ppq = self.time_ppq
		plb_obj.muted = self.muted
		plb_obj.visual = self.visual
		plb_obj.group = self.group
		plb_obj.locked = self.locked
		return plb_obj

	def add_autopoints(self, a_type):
		self.auto[a_type] = autopoints.cvpj_autopoints(self.time_ppq, 'float')
		return self.auto[a_type]

	def midi_from(self, input_file):
		from objects.midi_file.parser import MidiFile
		from objects.midi_file import events as MidiEvents

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

