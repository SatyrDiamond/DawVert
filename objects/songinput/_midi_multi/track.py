# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import numpy as np
from objects_midi import sysex
from objects.songinput._midi_multi import notes
from objects.songinput._midi_multi import chanauto

class midi_track:
	def __init__(self, numevents, song_obj):
		self.notes = notes.midi_notes_multi(numevents)
		self.song_obj = song_obj
		self.portnum = 0

		self.track_name = None
		self.track_color = None
		self.used_insts = None
		self.seqspec = []

	def startpos_chan(self, channel): 
		return self.notes.startpos_chan(channel)

	def endpos_chan(self, channel):
		return self.notes.endpos_chan(channel)

	def note_on(self, curpos, channel, note, velocity):
		return self.notes.note_on(curpos, channel, note, velocity)

	def note_off(self, curpos, channel, note):
		return self.notes.note_off(curpos, channel, note)

	def note_dur(self, curpos, channel, note, velocity, duration):
		return self.notes.note_dur(curpos, channel, note, velocity, duration)

	def track_name(self, text):
		self.track_name = text

	def portnum(self, port):
		self.portnum = port

	def pitchwheel(self, curpos, channel, pitch):
		pitchchan = self.song_obj.auto_pitch.add()
		pitchchan['pos'] = curpos
		pitchchan['channel'] = channel
		pitchchan['value'] = pitch

	def control_change(self, curpos, channel, controller, value):
		if controller == 0: self.song_obj.auto_insts.addp_bank(curpos, channel, value)
		elif controller == 32: self.song_obj.auto_insts.addp_bank_hi(curpos, channel, value)
		elif controller == 111: self.song_obj.loop_start = curpos
		elif controller == 116: self.song_obj.loop_start = curpos
		elif controller == 117: self.song_obj.loop_end = curpos
		else: self.song_obj.auto_chan.add_point(curpos, controller, value, 0, channel)

	def program_change(self, curpos, channel, program):
		self.song_obj.auto_insts.addp_inst(curpos, channel, program)

	def set_tempo(self, curpos, tempo):
		tempoauto = self.song_obj.auto_bpm
		tempoauto.add()
		tempoauto['pos'] = curpos
		tempoauto['tempo'] = tempo

	def time_signature(self, curpos, numerator, denominator):
		tsauto = self.song_obj.auto_timesig
		tsauto.add()
		tsauto['pos'] = curpos
		tsauto['numerator'] = numerator
		tsauto['denominator'] = denominator

	def text(self, curpos, text):
		self.song_obj.texts.add_point(curpos, text)

	def marker(self, curpos, text):
		if text == 'loopStart': self.song_obj.loop_start = curpos
		if text == 'loopEnd': self.song_obj.loop_end = curpos
		if text == 'Start': 
			self.song_obj.start_pos_est = False
			self.song_obj.start_pos = curpos
		self.song_obj.marker.add_point(curpos, text)

	def copyright(self, copyright):
		self.song_obj.copyright = copyright

	def sequencer_specific(self, data):
		seqspec_obj = sysex.seqspec_obj()
		seqspec_obj.detect(data)
		color_found = None
		if seqspec_obj.sequencer == 'signal_midi' and seqspec_obj.param == 'color': color_found = seqspec_obj.value
		if seqspec_obj.sequencer == 'anvil_studio' and seqspec_obj.param == 'color': color_found = seqspec_obj.value
		if seqspec_obj.sequencer == 'studio_one' and seqspec_obj.param == 'color': color_found = seqspec_obj.value
		if color_found: self.track_color = [x/255 for x in color_found]
		self.seqspec.append(seqspec_obj)

	def sysex(self, curpos, data):
		sysex_obj = sysex.sysex_obj()
		sysex_obj.detect(data)
		self.song_obj.auto_sysex.add_point(curpos, sysex_obj)

		if sysex_obj.vendor.id == 67:
			if (sysex_obj.param, sysex_obj.value) == ('reset', 'all_params'): self.song_obj.device = 'xg'

		if sysex_obj.vendor.id == 65:
			if sysex_obj.param == 'gs_reset': self.song_obj.device = 'gs'
			if sysex_obj.model_id == 22: self.song_obj.device = 'mt32'

	def lyric(self, curpos, data):
		self.song_obj.lyrics[curpos] = data
