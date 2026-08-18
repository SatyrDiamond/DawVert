# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import zlib
import zipfile
from functions import note_data
from external.easybinrw import easybinrw
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

	def from_v2(self, ebrw_readstr):
		self.pos = ebrw_readstr.int_u32()
		self.note = ebrw_readstr.int_u8()
		self.layer = ebrw_readstr.int_u8()
		self.inst = ebrw_readstr.int_u16()
		sharp = ebrw_readstr.int_u8()
		self.sharp = sharp==2
		self.flat = sharp==1
		self.vol = ebrw_readstr.float()
		self.pan = ebrw_readstr.float()
		self.dur = ebrw_readstr.int_u16()
		ebrw_readstr.skip(1)

class notev2_pattern:
	def __init__(self, ebrw_readstr, tempo):
		self.tempo = tempo
		self.notes = []
		self.size = ebrw_readstr.int_u32()
		num_notes = ebrw_readstr.int_u32()
		for _ in range(num_notes):
			note = note_note()
			note.from_v2(ebrw_readstr)
			self.notes.append(note)

class notev2_song:
	def __init__(self):
		pass

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		try: 
			decompdata = zlib.decompress(ebrw_readstr.rest(), zlib.MAX_WBITS|32)
		except zlib.error as t:
			raise ProjectFileParserException('notessimo_v2: '+str(t))

		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(decompdata)
		ebrw_readstr.state.endian = True
		self.name = ebrw_readstr.string_i16()
		self.author = ebrw_readstr.string_i16()
		self.date1 = ebrw_readstr.string_i16()
		self.date2 = ebrw_readstr.string_i16()
		self.order = ebrw_readstr.list_int_u8(ebrw_readstr.int_u16())
		self.tempo_table = ebrw_readstr.list_int_u16(100)
		self.patterns = [notev2_pattern(ebrw_readstr, self.tempo_table[m]) for m in range(100)]
		return True
