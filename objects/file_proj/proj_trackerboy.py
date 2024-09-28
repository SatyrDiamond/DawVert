# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from objects.data_bytes import bytereader
from objects.exceptions import ProjectFileParserException

dtype_patdata = np.dtype([
	('n_pos', np.int8), 
	('n_key', np.int8), 
	('n_inst', np.int8), 
	('fx', [('fx_type', np.int8), ('fx_param', np.int8)], 3),
	]) 

class trackerboy_instrument:
	def __init__(self, song_data):
		self.id = 0
		self.name = ''
		self.channel = 0
		self.envelopeEnabled = 0
		self.envelope = 0
		self.param1 = 0
		self.param2 = 0
		self.envs = []

		if song_data:
			self.id = song_data.uint8()+1
			self.name = song_data.c_raw__int16(False)
			self.channel = song_data.uint8()
			self.envelopeEnabled = song_data.uint8()
			self.param1, self.param2 = song_data.bytesplit()
			self.envs = [trackerboy_env(song_data) for _ in range(4)]

class trackerboy_env:
	def __init__(self, song_data):
		self.loopEnabled = 0
		self.loopIndex = 0
		self.values = []

		if song_data:
			envlength = song_data.uint16()
			self.loopEnabled = song_data.uint8()
			self.loopIndex = song_data.uint8()
			self.values = list(song_data.l_int8(envlength))

	def __bool__(self):
		return bool(len(self.values))

class trackerboy_song:
	def __init__(self, song_data):
		self.patterns = {}

		if song_data:
			self.name = song_data.c_raw__int16(False)
			self.beat = song_data.uint8()
			self.measure = song_data.uint8()
			self.speed = song_data.uint8()
			self.len = song_data.uint8()+1
			self.rows = song_data.uint8()+1
			self.pat_num = song_data.uint16()
			self.numfxareas = song_data.uint8()
			self.orders = song_data.table8([self.len, 4])

			self.orders = np.rot90(self.orders)

			for _ in range(self.pat_num):
				pate_ch = song_data.uint8()
				pate_trkid = song_data.uint8()
				pate_rows = song_data.uint8()+1
				pate_data = np.frombuffer(song_data.read(9*pate_rows), dtype=dtype_patdata)

				if pate_ch not in self.patterns: self.patterns[pate_ch] = {}
				self.patterns[pate_ch][pate_trkid] = pate_data

class trackerboy_wave:
	def __init__(self, song_data):
		if song_data:
			self.id = song_data.uint8()+1
			self.name = song_data.c_raw__int16(False)
			self.wave = song_data.l_int4(16)

class trackerboy_project:
	def __init__(self):
		self.m_rev = 0
		self.n_rev = 0
		self.songs = []
		self.insts = {}
		self.waves = {}

	def load_from_file(self, input_file):
		song_data = bytereader.bytereader()
		song_data.load_file(input_file)

		try: 
			song_data.magic_check(b'\x00TRACKERBOY\x00')
		except ValueError as t:
			raise ProjectFileParserException('trackerboy: '+str(t))

		song_data.seek(24)
		self.m_rev = song_data.uint8()
		self.n_rev = song_data.uint8()
		song_data.skip(2)

		self.title = song_data.string(23, encoding="utf")
		self.artist = song_data.string(23, encoding="utf")
		self.copyright = song_data.string(23, encoding="utf")
		self.icount = song_data.uint8()
		self.scount = song_data.uint8()
		self.wcount = song_data.uint8()
		self.system = song_data.uint8()

		main_iff_obj = song_data.chunk_objmake()
		for chunk_obj in main_iff_obj.iter(160, song_data.end):
			if chunk_obj.id == b'INST':
				inst_obj = trackerboy_instrument(song_data)
				self.insts[inst_obj.id] = inst_obj
			if chunk_obj.id == b'SONG':
				song_obj = trackerboy_song(song_data)
				self.songs.append(song_obj)
			if chunk_obj.id == b'WAVE':
				wave_obj = trackerboy_wave(song_data)
				self.waves[wave_obj.id] = wave_obj
		return True