# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import zlib
import zipfile
from objects.data_bytes import bytereader
import xml.etree.ElementTree as ET
from functions import note_data
from objects.exceptions import ProjectFileParserException

class note_note:
	__slots__ = ['pos','note','layer','inst','sharp','flat','vol','pan','dur']
	def __init__(self):
		self.pos = 0
		self.note = 0
		self.layer = 0
		self.inst = None
		self.sharp = False
		self.flat = False
		self.vol = None
		self.pan = 0
		self.dur = 0

	def get_note(self):
		n_key = (self.note-41)*-1
		out_oct = int(n_key/7)
		out_key = n_key - out_oct*7
		out_note = note_data.keynum_to_note(out_key, out_oct-3)
		out_offset = 0
		if self.sharp: out_offset = 1
		if self.flat: out_offset = -1
		return out_note+out_offset

	def from_v2(self, song_data):
		self.pos = song_data.uint32_b()
		self.note = song_data.uint8()
		self.layer = song_data.uint8()
		self.inst = song_data.uint16_b()
		sharp = song_data.uint8()
		self.sharp = sharp==2
		self.flat = sharp==1
		self.vol = song_data.float_b()
		self.pan = song_data.float_b()
		self.dur = song_data.uint16_b()
		song_data.skip(1)

# ============================== V2 ==============================

class notev2_pattern:
	def __init__(self, song_data, tempo):
		self.tempo = tempo
		self.notes = []
		self.size = song_data.uint32_b()
		num_notes = song_data.uint32_b()
		for _ in range(num_notes):
			note = note_note()
			note.from_v2(song_data)
			self.notes.append(note)

class notev2_song:
	def __init__(self):
		pass

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)

		song_data = bytereader.bytereader()

		try: 
			decompdata = zlib.decompress(song_file.rest(), zlib.MAX_WBITS|32)
		except zlib.error as t:
			raise ProjectFileParserException('notessimo_v2: '+str(t))

		song_data.load_raw(decompdata)
		self.name = song_data.c_string__int16(True)
		self.author = song_data.c_string__int16(True)
		self.date1 = song_data.c_string__int16(True)
		self.date2 = song_data.c_string__int16(True)
		self.order = song_data.l_uint8(song_data.uint16_b())
		self.tempo_table = song_data.l_uint16_b(100)
		self.patterns = [notev2_pattern(song_data, self.tempo_table[m]) for m in range(100)]
		return True
