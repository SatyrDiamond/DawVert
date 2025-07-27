# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import dynbytearr
import numpy as np
import struct

in_dtype = np.dtype([
	('used', np.uint8),

	('pos', np.uint64),
	('uflags', np.uint8),

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
EVENTID__SEQSPEC = 106
EVENTID__TRACKEND = 255

FLAGS__CHAN = 1
FLAGS__NOTE = 2
FLAGS__DUR = 4
FLAGS__NONNOTE = 8

PBFLAGVAL__NONNOTE = FLAGS__CHAN | FLAGS__NONNOTE
PBFLAGVAL__NOTE = FLAGS__CHAN | FLAGS__NOTE
PBFLAGVAL__NOTE_DUR = FLAGS__CHAN | FLAGS__NOTE | FLAGS__DUR

state_dtype = np.dtype([
	('pos', np.uint64),
	('type', np.str_, 8),
	('chan', np.uint8),
	('val1', np.int64),
	('val2', np.int64),
	('val3', np.int64),
	('hqval', np.double),
	('pos_prev', np.uint64),
	('pos_dif', np.uint64),
	])

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
		self.seq_spec = {}
		self.has_duration = False

	def iter_events(self):
		state = np.zeros(1, state_dtype)[0]
		for x in self.data:
			if x['used']:
				etype = x['type']
				state[0] = x['pos']
				state[8] = state[0]-state[7]
				state[2] = x['chan']
				if etype == EVENTID__NOTE_OFF:
					state[1] = "NOTE_OFF"
					state[3] = x['value']
					state[4] = x['value2']
				elif etype == EVENTID__NOTE_ON:
					state[1] = "NOTE_ON"
					state[3] = x['value']
					state[4] = x['value2']
				elif etype == EVENTID__NOTE_DUR:
					state[1] = "NOTE_DUR"
					state[3] = x['value']
					state[4] = x['value2']
					state[5] = x['uhival']
				elif etype == EVENTID__CONTROL:
					state[1] = "CONTROL"
					state[3] = x['value']
					state[4] = x['uhival']
				elif etype == EVENTID__PROGRAM:
					state[1] = "PROGRAM"
					state[3] = x['value']
				elif etype == EVENTID__NOTE_PRESSURE:
					state[1] = "NOTE_PRS"
					state[3] = x['value']
					state[4] = x['uhival']
				elif etype == EVENTID__PRESSURE:
					state[1] = "PRESSURE"
					state[3] = x['uhival']
				elif etype == EVENTID__PITCH:
					state[1] = "PITCH"
					state[3] = x['shival']
				elif etype == EVENTID__TEMPO:
					state[1] = "TEMPO"
					state[6] = struct.unpack('f', struct.pack('I', x['uhival']))[0]
				elif etype == EVENTID__TIMESIG:
					state[1] = "TIMESIG"
					state[3] = x['value']
					state[4] = x['value2']
				elif etype == EVENTID__SYSEX:
					state[1] = "SYSEX"
					state[3] = x['uhival']
				elif etype == EVENTID__TEXT:
					state[1] = "TEXT"
					state[3] = x['uhival']
				elif etype == EVENTID__MARKER:
					state[1] = "MARKER"
					state[3] = x['uhival']
				elif etype == EVENTID__LYRIC:
					state[1] = "LYRIC"
					state[3] = x['uhival']
				elif etype == EVENTID__SEQSPEC:
					state[1] = "SEQSPEC"
					state[3] = x['uhival']
				elif etype == EVENTID__TRACKEND:
					state[1] = "END"
				else:
					state[1] = "UNKNOWN"

				state[7] = x['pos']
				yield state

	def __len__(self):
		return self.data.count()

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

	def change_ppq(self, inppq):
		ppqcalc = self.ppq/inppq
		self.data.data['pos'] = self.data.data['pos']/ppqcalc
		durloc = self.data.data['type']==EVENTID__NOTE_DUR
		self.data.data['uhival'][durloc] = self.data.data['uhival'][durloc]/ppqcalc
		self.ppq = inppq

	def get_channums(self):
		used_data = self.data.get_used()
		used_flag = (used_data['uflags']&FLAGS__CHAN).astype(np.bool_)
		used_chan = np.unique(used_data['chan'][used_flag])
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
						non['uhival'] = d['pos']-non['pos']
						non['type'] = EVENTID__NOTE_DUR
						non['uflags'] = PBFLAGVAL__NOTE_DUR
			self.has_duration = True

	def del_note_durs(self):
		if self.has_duration:
			notedata = self.data.data
			wherebools = notedata['type']==EVENTID__NOTE_DUR
			self.data.data['type'][wherebools] = EVENTID__NOTE_ON
			self.data.data['uflags'][wherebools] = PBFLAGVAL__NOTE
			wb = self.data.data[wherebools]
			self.data.data['uhival'][wherebools] = 0
			self.data.extend(len(wb))
			for n in wb:
				self.add_note_off(n['pos']+n['uhival'], n['chan'], n['value'], n['value2'])
			self.has_duration = False

	def detect_duration(self):
		used_data = self.data.get_used()
		durc = np.count_nonzero(used_data['type']==EVENTID__NOTE_DUR)
		durn = np.count_nonzero(used_data['type']==EVENTID__NOTE_ON)
		print(durc, durn)

	def add_note_off(self, curpos, channel, key, vol):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__NOTE_OFF
		cursor['chan'] = channel
		cursor['uflags'] = PBFLAGVAL__NOTE
		cursor['value'] = key
		cursor['value2'] = vol
		cursor['uhival'] = 0

	def add_note_on(self, curpos, channel, key, vol):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__NOTE_ON if vol else EVENTID__NOTE_OFF
		cursor['chan'] = channel
		cursor['uflags'] = PBFLAGVAL__NOTE
		cursor['value'] = key
		cursor['value2'] = vol
		cursor['uhival'] = 0

	def add_note_dur(self, curpos, channel, key, vol, dur):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__NOTE_DUR
		cursor['chan'] = channel
		cursor['uflags'] = PBFLAGVAL__NOTE_DUR
		cursor['value'] = key
		cursor['value2'] = vol
		cursor['uhival'] = dur

	def add_note_pressure(self, curpos, channel, note, pressure):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__NOTE_PRESSURE
		cursor['chan'] = channel
		cursor['uflags'] = PBFLAGVAL__NONNOTE
		cursor['uhival'] = pressure
		cursor['value'] = note

	def add_control(self, curpos, channel, control, value):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__CONTROL
		cursor['chan'] = channel
		cursor['uflags'] = PBFLAGVAL__NONNOTE
		cursor['value'] = control
		cursor['uhival'] = value

	def add_program(self, curpos, channel, program):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__PROGRAM
		cursor['chan'] = channel
		cursor['uflags'] = PBFLAGVAL__NONNOTE
		cursor['value'] = program

	def add_chan_pressure(self, curpos, channel, pressure):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__PRESSURE
		cursor['chan'] = channel
		cursor['uflags'] = PBFLAGVAL__NONNOTE
		cursor['uhival'] = pressure

	def add_pitch(self, curpos, channel, value):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__PITCH
		cursor['chan'] = channel
		cursor['uflags'] = PBFLAGVAL__NONNOTE
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
		cursor['uflags'] = FLAGS__NONNOTE

	def add_timesig(self, curpos, numerator, denominator):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__TIMESIG
		cursor['value'] = numerator
		cursor['value2'] = denominator
		cursor['uflags'] = FLAGS__NONNOTE

	def add_end_of_track(self, curpos):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = 255
		cursor['uflags'] = FLAGS__NONNOTE

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
		cursor['uflags'] = FLAGS__NONNOTE
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
		cursor['uflags'] = FLAGS__NONNOTE
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
		cursor['uflags'] = FLAGS__NONNOTE
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
		cursor['uflags'] = FLAGS__NONNOTE
		self.lyrics[lyricnum] = txtdata

	def add_seq_spec(self, curpos, data):
		seqspecnum = 0
		while True:
			seqspecnum += 1
			if seqspecnum not in self.seq_spec: break

		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__SEQSPEC
		cursor['uhival'] = seqspecnum
		cursor['uflags'] = FLAGS__NONNOTE
		self.seq_spec[seqspecnum] = data

	def add_end_track(self, curpos):
		self.cursor.add()
		cursor = self.cursor
		cursor['pos'] = curpos
		cursor['type'] = EVENTID__TRACKEND
		cursor['uflags'] = FLAGS__NONNOTE

	def sort(self):
		is_sorted = np.all(np.diff(self.data.get_used()['pos'].astype(np.int64)) >= 0)
		if not is_sorted:
			self.data.sort(['pos'])

	def get_dur(self):
		used_data = self.data.get_used()

		n_out = used_data[(used_data['uflags']&FLAGS__NOTE).astype(np.bool_)]
		n_dur = n_out['uhival']+n_out['pos']
		maxn = max(n_dur) if len(n_dur) else 0

		c_out = used_data[(used_data['uflags']&FLAGS__NONNOTE).astype(np.bool_)]
		c_dur = n_out['pos']
		maxc = max(c_dur) if len(c_dur) else 0

		return max(maxn, maxc)

	def get_start(self):
		used_data = self.data.get_used()
		tab = used_data['pos']
		return min(tab) if tab.any() else 0

	def get_start_end(self):
		used_data = self.data.get_used()
		tab = used_data['pos']
		return (min(tab), max(tab)) if tab.any() else (0, 0)

	def clean(self):
		self.data.clean()

	def count_part(self, k, v):
		return self.data.count_part(k, v)

	def get_used_notes(self):
		self.add_note_durs()
		used_data = self.data.get_used()
		used_data = used_data[used_data['uflags']|FLAGS__NOTE]
		return used_data[['pos','uhival','chan','value','value2']]

	def getvalue(self):
		return self.data.get_used().tobytes()

	def merge(self, other_event, pos, dur, offset):
		useddata = other_event.data.get_used()

		if other_event.has_duration:
			self.has_duration = other_event.has_duration

		o = np.logical_and((dur+offset)>useddata['pos'], useddata['pos']>=offset)
		trimmed_events = useddata[o]

		for t in trimmed_events:
			t['pos'] += pos
			if t['type'] not in [EVENTID__SYSEX, EVENTID__TEXT, EVENTID__MARKER, EVENTID__LYRIC, EVENTID__SEQSPEC]:
				self.cursor.add_copied(t)

	def midi_to(self, output_file):
		import mido

		metamsg = mido.MetaMessage
		rmsg = mido.Message

		midiobj = mido.MidiFile()
		midiobj.ticks_per_beat = self.ppq

		miditrack = mido.MidiTrack()

		self.sort()
		self.del_note_durs()
		self.sort()

		for x in self.iter_events():
			etype = x[1]
			etime = int(x['pos_dif'])

			if etype == 'NOTE_OFF':
				outnote = int(x[3])
				if 127>outnote>=0: miditrack.append(rmsg('note_off', channel=int(x[2]), note=outnote, time=etime))

			elif etype == 'NOTE_ON':
				outnote = int(x[3])
				if 127>outnote>=0: miditrack.append(rmsg('note_on', channel=int(x[2]), note=outnote, velocity=int(x[4]), time=etime))

			elif etype == 'PROGRAM':
				miditrack.append(rmsg('program_change', channel=int(x[2]), program=int(x[3]), time=etime))

			elif etype == 'CONTROL':
				miditrack.append(rmsg('control_change', channel=int(x[2]), control=int(x[3]), value=int(x[4]), time=etime))

			elif etype == 'TEMPO':
				miditrack.append(metamsg('set_tempo', tempo=mido.bpm2tempo(x[6]), time=etime))

			elif etype == 'PITCH':
				miditrack.append(rmsg('pitchwheel', pitch=int(x[3]/4096), time=etime))

			elif etype == 'TIMESIG':
				miditrack.append(metamsg('time_signature', numerator=4, denominator=4, time=etime))

			elif etype == 'SYSEX':
				sysexdata = bytearray(self.sysex[int(x[3])])
				miditrack.append(rmsg('sysex', data=sysexdata, time=etime))

			elif etype == 'TEXT':
				miditrack.append(metamsg('text', text=self.texts[int(x[3])], time=etime))

			elif etype == 'SEQSPEC':
				sysexdata = bytearray(self.seq_spec[int(x[3])])
				miditrack.append(metamsg('sequencer_specific', data=sysexdata, time=etime))

		midiobj.tracks.append(miditrack)
		midiobj.save(output_file)