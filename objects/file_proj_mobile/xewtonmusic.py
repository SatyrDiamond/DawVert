# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
import numpy as np

# =========================================== SONG ===========================================

class xewtonmusic_song_track:
	def __init__(self):
		self.unk = []
		self.tracknum = 0
		self.instnum = 0
		self.color = None
		self.fx_on = 0
		self.selected = 0
		self.volume = 1
		self.pan = 0
		self.notes = []

	def read(self, ebrw_readstr):
		self.unk = []
		self.tracknum = ebrw_readstr.int_u32()
		self.instnum = ebrw_readstr.int_u32()
		self.color = ebrw_readstr.list_int_u8(4)
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.fx_on = ebrw_readstr.int_u8()
		self.selected = ebrw_readstr.int_u8()
		self.volume = ebrw_readstr.float()
		self.pan = ebrw_readstr.float()

class xewtonmusic_song_header:
	def __init__(self):
		self.unk = []
		self.seconds = 0
		self.tempo = 120
		self.timesig1 = 4
		self.timesig2 = 4

	def read(self, ebrw_readstr):
		self.unk = []
		ebrw_readstr.skip(2)
		self.seconds = ebrw_readstr.float()
		ebrw_readstr.skip(6)
		self.tempo = ebrw_readstr.float()
		self.timesig1 = ebrw_readstr.int_u8()
		self.timesig2 = ebrw_readstr.int_u8()
		#self.unk.append(  ebrw_readstr.int_u8()  )
		#self.unk.append(  ebrw_readstr.int_u32()  )
		#self.unk.append(  ebrw_readstr.int_u32()  )
		#self.unk.append(  ebrw_readstr.int_u32()  )
		#self.unk.append(  ebrw_readstr.int_u16()  )
		#self.unk.append(  ebrw_readstr.int_u16()  )

class xewtonmusic_song_effx:
	def __init__(self):
		self.unk = []
		self.params = []

	def read(self, ebrw_readstr):
		self.unk = []
		self.version = ebrw_readstr.int_u16()
		self.fxtype = ebrw_readstr.int_u8()
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.float()  )
		if self.fxtype==0:
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.float())
		elif self.fxtype==1:
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.int_u8())
			self.params.append(ebrw_readstr.int_u8())
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.float())
		elif self.fxtype==2:
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.int_u8())
			self.params.append(ebrw_readstr.int_u8())
			self.params.append(ebrw_readstr.float())
		elif self.fxtype==3:
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.float())
		elif self.fxtype==4:
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.int_u8())
			self.params.append(ebrw_readstr.float())
		elif self.fxtype==5:
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.int_u8())
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.float())
			self.params.append(ebrw_readstr.int_u8())
			self.params.append(ebrw_readstr.int_u8())
			self.params.append(ebrw_readstr.float())

notes_dtype = np.dtype([
	('pos', np.uint32),
	('dur', np.uint32),
	('key', np.uint8),
	('vol', np.uint8),
	('unk', np.uint16),
	])

class xewtonmusic_song_note:
	def __init__(self):
		self.pos = 0
		self.dur = 0
		self.key = 0
		self.vol = 0
		self.auto = []

	def read(self, ebrw_readstr):
		self.pos = ebrw_readstr.int_u32()
		self.dur = ebrw_readstr.int_u32()
		self.key = ebrw_readstr.int_u8()
		self.vol = ebrw_readstr.int_u8()
		numauto = ebrw_readstr.int_u16()
		if numauto: 
			for _ in range(numauto):
				auto_pos = ebrw_readstr.int_u16()
				auto_val = ebrw_readstr.int_u16()
				self.auto.append([auto_pos, auto_val])

class xewtonmusic_song_notes:
	def __init__(self):
		self.tracknum = 0
		self.notes = []

	def read(self, ebrw_readstr):
		self.tracknum = ebrw_readstr.int_u16()
		self.unk = ebrw_readstr.int_u16()
		num_notes = ebrw_readstr.int_u32()
		for n in range(num_notes):
			note = xewtonmusic_song_note()
			note.read(ebrw_readstr)
			self.notes.append(note)

class xewtonmusic_song_file:
	def __init__(self):
		self.tracks = {}
		self.header = xewtonmusic_song_header()
		self.effects = {}

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		ebrw_readstr.magic_check(b'\x99XMS\x0D\x0A\x1A\x0A')

		self.tracks = {}
		self.effects = {}
		while ebrw_readstr.remaining():
			chunk_name = ebrw_readstr.raw(4)
			chunk_size = ebrw_readstr.int_u32()

			ebrw_readstr.isolate_size(chunk_size)

			if chunk_name==b'HEAD':
				self.header.read(ebrw_readstr)
			elif chunk_name==b'TINF':
				tinf_obj = xewtonmusic_song_track()
				tinf_obj.read(ebrw_readstr)
				self.tracks[tinf_obj.tracknum] = tinf_obj
			elif chunk_name==b'TNOT':
				tnot_obj = xewtonmusic_song_notes()
				tnot_obj.read(ebrw_readstr)
				if tnot_obj.tracknum in self.tracks:
					self.tracks[tnot_obj.tracknum].notes = tnot_obj
			elif chunk_name==b'EFFX':
				tinf_obj = xewtonmusic_song_effx()
				tinf_obj.read(ebrw_readstr)
				self.effects[tinf_obj.fxtype] = tinf_obj
			#elif chunk_name==b'TPAD':
			#	print( ebrw_readstr.rest().hex() )
			#elif chunk_name==b'KEYB':
			#	print( ebrw_readstr.rest().hex() )
			#elif chunk_name==b'METR':
			#	print( ebrw_readstr.rest().hex() )
			#elif chunk_name==b'PITB':
			#	print( ebrw_readstr.rest().hex() )
			#elif chunk_name==b'CHRD':
			#	print( ebrw_readstr.rest().hex() )
			#elif chunk_name==b'ATRK':
			#	print( ebrw_readstr.rest().hex() )
			#else:
			#	print(chunk_name)
			#	chunk_data = ebrw_readstr.raw(chunk_size)

			ebrw_readstr.isolate_end()

		return True

# =========================================== INST ===========================================

def read_string(ebrw_readstr):
	nsize = ebrw_readstr.int_u16()
	return ebrw_readstr.string16(nsize)

class xewtonmusic_inst_header:
	def __init__(self):
		self.unk = []
		self.unkf = []
		self.attack = 0
		self.release = 0

	def read(self, ebrw_readstr):
		self.unk = []
		self.unkf = []
		self.version = ebrw_readstr.int_u16()
		self.num_regions = ebrw_readstr.int_u16()
		self.instnum = ebrw_readstr.int_u16()
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u16()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unkf.append(  ebrw_readstr.float()  )
		self.attack = ebrw_readstr.float()
		self.release = ebrw_readstr.float()
		self.unkf.append(  ebrw_readstr.float()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		#print(self.unkf)

class xewtonmusic_inst_sample:
	def __init__(self):
		self.unk = []
		self.unkf = []
		self.filename = ''
		self.name = ''
		self.name2 = ''
		self.key_root = 0
		self.key_lo = 0
		self.key_hi = 0
		self.loop_on = 0
		self.loop_1 = 0
		self.loop_2 = 0
		self.loop_3 = 0
		self.data = None
		self.vol = 1

	def read(self, ebrw_readstr):
		self.unk = []
		self.unkf = []
		self.filename = read_string(ebrw_readstr)
		self.name = read_string(ebrw_readstr)
		self.name2 = read_string(ebrw_readstr)
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.key_root = ebrw_readstr.int_u8()
		self.key_lo = ebrw_readstr.int_u8()
		self.key_hi = ebrw_readstr.int_u8()
		self.vol = ebrw_readstr.float()
		self.unkf.append(  ebrw_readstr.float()  )
		self.loop_on = ebrw_readstr.int_u8()
		self.unkf.append(  ebrw_readstr.float()  )
		self.loop_1 = ebrw_readstr.int_u32()
		self.loop_2 = ebrw_readstr.int_u32()
		self.loop_3 = ebrw_readstr.int_u32()

class xewtonmusic_inst_file:
	def __init__(self):
		self.name = None
		self.header = xewtonmusic_inst_header()
		self.samples = []

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		ebrw_readstr.magic_check(b'INST')
		ebrw_readstr.skip(4)

		self.samples = []
		while ebrw_readstr.remaining():
			chunk_name = ebrw_readstr.raw(4)
			chunk_size = ebrw_readstr.int_u32()

			ebrw_readstr.isolate_size(chunk_size)

			if chunk_name==b'HEAD':
				self.header.read(ebrw_readstr)
			elif chunk_name==b'NAME':
				self.name = read_string(ebrw_readstr)
			elif chunk_name==b'SINF':
				sample_obj = xewtonmusic_inst_sample()
				sample_obj.read(ebrw_readstr)
				self.samples.append(sample_obj)
			elif chunk_name==b'SDAT':
				sample_obj.data = ebrw_readstr.rest()
			#else:
			#	print(chunk_name)

			ebrw_readstr.isolate_end()

		return True
