# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter
from objects.exceptions import ProjectFileParserException
import struct

import logging
logger_projparse = logging.getLogger('projparse')

def stream_decode(song_file, org_numofnotes, maxchange, org_notelist, tnum):
	global cur_val
	for x in range(org_numofnotes):
		pre_val = song_file.uint8()
		if maxchange != None:
			if 0 <= pre_val <= maxchange: cur_val = pre_val
			org_notelist[x][tnum] = cur_val
		else:
			org_notelist[x][tnum] = pre_val

def stream_encode(invals):
	cur_val = -1
	for n, x in enumerate(invals):
		if cur_val == x: invals[n] = 255
		cur_val = x
	return invals

class orgyana_orgsamp():
	def __init__(self): 
		self.sample_data = []
		self.drum_data = []
		self.num_drums = 0
		self.drum_rate = 0
		self.loaded = False

	def load_from_file(self, input_file):
		self.loaded = True
		try:
			song_file = bytereader.bytereader()
			song_file.load_file(input_file)
			song_file.seek(4)

			self.sample_data = [song_file.l_int8(256) for x in range(100)]
			self.num_drums = song_file.uint8()
			self.drum_rate = song_file.uint16()
			self.drum_data = [song_file.c_uint8__int24(True) for x in range(self.num_drums)]
			return True
		except:
			return False

class orgyana_track:
	def __init__(self):
		self.pitch = 1000
		self.instrument = 0
		self.disable_sustaining_notes = 0
		self.number_of_notes = 0
		self.notes = []

	def read(self, song_file):
		self.pitch = song_file.uint16()
		self.instrument = song_file.uint8()
		self.disable_sustaining_notes = song_file.uint8()
		self.number_of_notes = song_file.uint16()
		self.notes = [[0,0,0,0,0] for _ in range(self.number_of_notes)]

	def write(self, byw_stream):
		byw_stream.uint16(self.pitch)
		byw_stream.uint8(self.instrument)
		byw_stream.uint8(self.disable_sustaining_notes)
		byw_stream.uint16(len(self.notes))

class orgyana_project:
	def __init__(self):
		self.oldperc = False
		self.wait = 120
		self.stepsperbar = 4
		self.beatsperstep = 4
		self.loop_beginning = 0
		self.loop_end = 0
		self.tracks = [orgyana_track() for x in range(16)]

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)

		try: 
			song_file.magic_check(b'Org-')
		except ValueError as t:
			raise ProjectFileParserException('orgyana: '+str(t))

		self.oldperc = song_file.raw(2) == b'03'
		self.wait = song_file.uint16()
		self.stepsperbar = song_file.uint8()
		self.beatsperstep = song_file.uint8()
		self.loop_beginning = song_file.uint32()
		self.loop_end = song_file.uint32()

		for n in range(16): self.tracks[n].read(song_file)

		for n in range(16):
			org_track = self.tracks[n]
			for x in range(org_track.number_of_notes): org_track.notes[x][0] = song_file.uint32() #position
			stream_decode(song_file, org_track.number_of_notes, 95, org_track.notes, 1) #note
			stream_decode(song_file, org_track.number_of_notes, 256, org_track.notes, 2) #duration
			stream_decode(song_file, org_track.number_of_notes, 254, org_track.notes, 3) #vol
			stream_decode(song_file, org_track.number_of_notes, 12, org_track.notes, 4) #pan
		return True

	def write(self, byw_stream):
		byw_stream.raw(b'Org-'+(b'03' if self.oldperc else b'02'))
		byw_stream.uint16(self.wait)
		byw_stream.uint8(self.stepsperbar)
		byw_stream.uint8(self.beatsperstep)
		byw_stream.uint32(self.loop_beginning)
		byw_stream.uint32(self.loop_end)

		for n in range(16): self.tracks[n].write(byw_stream)

		for n in range(16):
			org_track = self.tracks[n]
			n_notes = len(org_track.notes)
			m_pos = [x[0] for x in org_track.notes]
			m_note = [x[1] for x in org_track.notes]
			m_dur = [x[2] for x in org_track.notes]
			m_vol = [x[3] for x in org_track.notes]
			m_pan = [x[4] for x in org_track.notes]
			byw_stream.l_uint32(m_pos, len(m_pos))
			byw_stream.l_uint8(m_note, len(m_note))
			byw_stream.l_uint8(m_dur, len(m_dur))
			byw_stream.l_uint8(m_vol, len(m_vol))
			byw_stream.l_uint8(m_pan, len(m_pan))

	def save_to_file(self, output_file):
		byw_stream = bytewriter.bytewriter()
		self.write(byw_stream)
		f = open(output_file, 'wb')
		f.write(byw_stream.getvalue())