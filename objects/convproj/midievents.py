# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import dynbytearr
import numpy as np
import struct

in_dtype = np.dtype([
	('used', np.uint8),

	('pos', np.uint32),
	('proc_end', np.uint32),
	('proc_complete', np.uint8),

	('type', np.uint8),
	('chan', np.uint8),
	('value', np.uint8),
	('value2', np.uint8),
	('uhival', np.uint64),
	('shival', np.int32),
	])

EVENTID__NOTE_OFF = 8
EVENTID__NOTE_ON = 9
EVENTID__NOTE_DUR = 10
EVENTID__NOTE_PRESSURE = 11
EVENTID__CONTROL = 12
EVENTID__PROGRAM = 13
EVENTID__PRESSURE = 14
EVENTID__PITCH = 15

EVENTID__TEMPO = 100
EVENTID__TIMESIG = 101
EVENTID__SYSEX = 102
EVENTID__TEXT = 103
EVENTID__MARKER = 104
EVENTID__LYRIC = 105

class midievents:
	def __init__(self):
		self.data = dynbytearr.dynbytearr(in_dtype)
		self.cursor = self.data.create_cursor()
		self.ppq = 96
		self.track_name = None
		self.copyright = None
		self.port = 0
		self.sysex = {}
		self.texts = {}
		self.markers = {}
		self.lyrics = {}
		self.seq_spec = []
		self.has_duration = False

	def __iter__(self):
		for x in self.data:
			if x['used']:
				yield x

	def __eq__(self, nlo):
		nl_same = np.all(self.data == nlo.data) if len(self.data)==len(nlo.data) else False
		sysex_same = self.sysex == nlo.sysex
		texts_same = self.texts == nlo.texts
		markers_same = self.markers == nlo.markers
		lyrics_same = self.lyrics == nlo.lyrics
		seq_spec_same = self.seq_spec == nlo.seq_spec
		ppq_same = self.ppq == nlo.ppq
		track_name_same = self.track_name == nlo.track_name
		copyright_same = self.copyright == nlo.copyright
		return nl_same and sysex_same and texts_same and markers_same and lyrics_same and seq_spec_same and seq_spec_same and seq_spec_same and ppq_same and track_name_same and copyright_same

	def get_channums(self):
		used_chan = np.unique(self.data.get_used()['chan'])
		used_chan = used_chan[used_chan!=255]
		return used_chan

	def add_note_durs(self):
		if not self.has_duration:
			activenotes = [[[] for x in range(128)] for x in range(16)]
			for p, d in enumerate(self.data):
				if d['type'] == EVENTID__NOTE_ON:
					activenotes[d['chan']][d['value']].append(p)

				if d['type'] == EVENTID__NOTE_OFF:
					d['used'] = 0
					nd = activenotes[d['chan']][d['value']]
					if nd:
						notenum = nd.pop()
						non = self.data.data[notenum]
						non['proc_complete'] = 1
						non['uhival'] = d['pos']-non['pos']
						non['type'] = EVENTID__NOTE_DUR
			self.has_duration = True

	def add_note_off(self, curpos, channel, key, vol):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__NOTE_OFF
		cursor['chan'] = channel
		cursor['value'] = key
		cursor['value2'] = vol

	def add_note_on(self, curpos, channel, key, vol):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__NOTE_ON if vol else EVENTID__NOTE_OFF
		cursor['chan'] = channel
		cursor['value'] = key
		cursor['value2'] = vol
		cursor['shival'] = 1

	def add_note_dur(self, curpos, channel, key, vol, dur):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__NOTE_DUR
		cursor['chan'] = channel
		cursor['value'] = key
		cursor['value2'] = vol
		cursor['uhival'] = dur
		cursor['proc_complete'] = 1

	def add_note_pressure(self, curpos, channel, note, pressure):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__NOTE_PRESSURE
		cursor['chan'] = channel
		cursor['uhival'] = pressure
		cursor['value'] = note

	def add_control(self, curpos, channel, control, value):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__CONTROL
		cursor['chan'] = channel
		cursor['value'] = control
		cursor['uhival'] = value

	def add_program(self, curpos, channel, program):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__PROGRAM
		cursor['chan'] = channel
		cursor['value'] = program

	def add_chan_pressure(self, curpos, channel, pressure):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__PRESSURE
		cursor['chan'] = channel
		cursor['uhival'] = pressure

	def add_pitch(self, curpos, channel, value):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__PITCH
		cursor['chan'] = channel
		cursor['shival'] = value



	def add_port(self, port):
		self.port = port

	def add_track_name(self, track_name):
		self.track_name = track_name

	def add_copyright(self, copyright):
		self.copyright = copyright

	def add_tempo(self, curpos, value):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__TEMPO
		cursor['uhival'] = struct.unpack('I', struct.pack('f', value))[0]
		cursor['chan'] = 255

	def add_timesig(self, curpos, numerator, denominator):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__TIMESIG
		cursor['value'] = numerator
		cursor['value2'] = denominator
		cursor['chan'] = 255

	def add_end_of_track(self, curpos):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = 255
		cursor['chan'] = 255

	def add_sysex(self, curpos, sysexdata):
		sysexnum = 0
		while True:
			sysexnum += 1
			if sysexnum not in self.sysex: break

		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__SYSEX
		cursor['uhival'] = sysexnum
		cursor['chan'] = 255
		self.sysex[sysexnum] = bytes(sysexdata)

	def add_text(self, curpos, txtdata):
		textnum = 0
		while True:
			textnum += 1
			if textnum not in self.texts: break

		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__TEXT
		cursor['uhival'] = textnum
		cursor['chan'] = 255
		self.texts[textnum] = txtdata

	def add_marker(self, curpos, txtdata):
		markernum = 0
		while True:
			markernum += 1
			if markernum not in self.markers: break

		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__MARKER
		cursor['uhival'] = markernum
		cursor['chan'] = 255
		self.markers[markernum] = txtdata

	def add_lyric(self, curpos, txtdata):
		lyricnum = 0
		while True:
			lyricnum += 1
			if lyricnum not in self.texts: break

		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__LYRIC
		cursor['uhival'] = lyricnum
		cursor['chan'] = 255
		self.lyrics[lyricnum] = txtdata

	def add_seq_spec(self, data):
		self.seq_spec.append(data)

	def sort(self):
		self.data.sort(['pos'])

	def clean(self):
		self.data.clean()

	def count_part(self, k, v):
		return self.data.count_part(k, v)

	def get_used_notes(self):
		self.add_note_durs()
		used_data = self.data.get_used()
		used_data = used_data[used_data['proc_complete']==1]
		return used_data[['pos','uhival','chan','value','value2']]
