# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from external.easybinrw import easybinrw
from external.easybinrw import chunked
from objects.exceptions import ProjectFileParserException

dtype_patdata = np.dtype([
	('n_pos', np.int8), 
	('n_key', np.int8), 
	('n_inst', np.int8), 
	('fx', [('fx_type', np.int8), ('fx_param', np.int8)], 3),
	]) 

# ============================================= instrument ============================================= 

class trackerboy_instrument:
	def __init__(self):
		self.id = 0
		self.name = ''
		self.channel = 0
		self.envelopeEnabled = 0
		self.envelope = 0
		self.param1 = 0
		self.param2 = 0
		self.envs = []

	def read(self, ebrw_readstr):
		self.id = ebrw_readstr.int_u8()+1
		self.name = ebrw_readstr.raw_i16()
		self.channel = ebrw_readstr.int_u8()
		self.envelopeEnabled = ebrw_readstr.int_u8()
		self.param1, self.param2 = ebrw_readstr.int_u4_2()
		for _ in range(4):
			o = trackerboy_env()
			o.read(ebrw_readstr)
			self.envs.append(o)

class trackerboy_env:
	def __init__(self):
		self.loopEnabled = 0
		self.loopIndex = 0
		self.values = []

	def read(self, ebrw_readstr):
		envlength = ebrw_readstr.int_u16()
		self.loopEnabled = ebrw_readstr.int_u8()
		self.loopIndex = ebrw_readstr.int_u8()
		self.values = list(ebrw_readstr.list_int_u8(envlength))

	def __bool__(self):
		return bool(len(self.values))

class trackerboy_wave:
	def __init__(self):
		self.id = 0
		self.name = b''
		self.wave = []

	def read(self, ebrw_readstr):
		self.id = ebrw_readstr.int_u8()+1
		self.name = ebrw_readstr.raw_i16()
		self.wave = ebrw_readstr.list_int_u4(16)

# ============================================= song ============================================= 

class trackerboy_song:
	def __init__(self):
		self.patterns = {}
		self.orders = []
		self.name = ''
		self.beat = 0
		self.measure = 0
		self.speed = 0
		self.len = 0
		self.rows = 0
		self.pat_num = 0
		self.numfxareas = 0

	def read(self, ebrw_readstr):
		self.name = ebrw_readstr.raw_i16()
		self.beat = ebrw_readstr.int_u8()
		self.measure = ebrw_readstr.int_u8()
		self.speed = ebrw_readstr.int_u8()
		self.len = ebrw_readstr.int_u8()+1
		self.rows = ebrw_readstr.int_u8()+1
		self.pat_num = ebrw_readstr.int_u16()
		self.numfxareas = ebrw_readstr.int_u8()
		self.orders = ebrw_readstr.list_int_u8(self.len*4)
		self.orders = np.reshape(self.orders, [self.len, 4])

		self.orders = np.rot90(self.orders)

		for _ in range(self.pat_num):
			pate_ch = ebrw_readstr.int_u8()
			pate_trkid = ebrw_readstr.int_u8()
			pate_rows = ebrw_readstr.int_u8()+1
			pate_data = np.frombuffer(ebrw_readstr.read(9*pate_rows), dtype=dtype_patdata)

			if pate_ch not in self.patterns: self.patterns[pate_ch] = {}
			self.patterns[pate_ch][pate_trkid] = pate_data

class trackerboy_project:
	def __init__(self):
		self.m_rev = 0
		self.n_rev = 0
		self.songs = []
		self.insts = {}
		self.waves = {}
		self.title = ''
		self.artist = ''
		self.copyright = ''
		self.icount = 0
		self.scount = 0
		self.wcount = 0
		self.system = 0


	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		try: 
			ebrw_readstr.magic_check(b'\x00TRACKERBOY\x00')
		except ValueError as t:
			raise ProjectFileParserException('trackerboy: '+str(t))

		ebrw_readstr.seek(24)
		self.m_rev = ebrw_readstr.int_u8()
		self.n_rev = ebrw_readstr.int_u8()
		ebrw_readstr.skip(2)

		self.title = ebrw_readstr.string(23, encoding="utf")
		self.artist = ebrw_readstr.string(23, encoding="utf")
		self.copyright = ebrw_readstr.string(23, encoding="utf")
		self.icount = ebrw_readstr.int_u8()
		self.scount = ebrw_readstr.int_u8()
		self.wcount = ebrw_readstr.int_u8()
		self.system = ebrw_readstr.int_u8()

		ebrw_readstr.seek(160)
		for part_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):
			if part_obj.id == b'INST':
				inst_obj = trackerboy_instrument()
				inst_obj.read(ebrw_readstr)
				self.insts[inst_obj.id] = inst_obj
			if part_obj.id == b'SONG':
				song_obj = trackerboy_song()
				song_obj.read(ebrw_readstr)
				self.songs.append(song_obj)
			if part_obj.id == b'WAVE':
				wave_obj = trackerboy_wave()
				wave_obj.read(ebrw_readstr)
				self.waves[wave_obj.id] = wave_obj
		return True