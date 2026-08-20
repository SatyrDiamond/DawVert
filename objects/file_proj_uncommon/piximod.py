# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from external.easybinrw import chunked
from objects.exceptions import ProjectFileParserException
import logging
import numpy as np
logger_projparse = logging.getLogger('projparse')

class piximod_pattern:
	def __init__(self, ebrw_readstr):
		self.tracks = 0
		self.length = 0
		self.data = None
		if ebrw_readstr is not None: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		ebrw_readstr.skip(4)
		self.tracks = ebrw_readstr.int_u32()
		self.length = ebrw_readstr.int_u32()
		self.data = ebrw_readstr.list_int_u8(self.length*self.tracks*4)
		self.data = np.reshape(self.data, [self.length, self.tracks, 4])

class piximod_sample:
	def __init__(self):
		self.channels = 1
		self.rate = 44100
		self.fine = 0
		self.transpose = 0
		self.volume = 100
		self.start = 0
		self.end = 0
		self.data = b''

class piximod_song:
	def __init__(self):
		self.bpm = 120
		self.lpb = 4
		self.tpl = 6
		self.vol = 100
		self.shuffle = 0
		self.order = []
		self.patterns = {}
		self.sounds = [piximod_sample() for x in range(16)]

	def load_from_raw(self, input_data):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(input_data)
		return self.load(ebrw_readstr)

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		return self.load(ebrw_readstr)

	def load(self, ebrw_readstr):
		try: 
			ebrw_readstr.magic_check(b'PIXIMOD1')
		except ValueError as t:
			raise ProjectFileParserException('piximod: '+str(t))

		cur_patnum = 0
		cur_sound = 0
		for part_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):
			if part_obj.id == b'BPM ': self.bpm = ebrw_readstr.int_u32()
			if part_obj.id == b'LPB ': self.lpb = ebrw_readstr.int_u32()
			if part_obj.id == b'TPL ': self.tpl = ebrw_readstr.int_u32()
			if part_obj.id == b'SHFL': self.shuffle = ebrw_readstr.int_u32()
			if part_obj.id == b'VOL ': self.vol = ebrw_readstr.int_u32()
			if part_obj.id == b'PATT':
				ebrw_readstr.skip(4)
				num = ebrw_readstr.int_u32()
				ebrw_readstr.skip(4)
				self.order = ebrw_readstr.list_int_u16(num)
			if part_obj.id == b'PATN': cur_patnum = ebrw_readstr.int_u32()
			if part_obj.id == b'PATD': self.patterns[cur_patnum] = piximod_pattern(ebrw_readstr)
			if part_obj.id == b'SNDN': cur_sound = ebrw_readstr.int_u32()
			if part_obj.id == b'CHAN': self.sounds[cur_sound].channels = ebrw_readstr.int_s32()
			if part_obj.id == b'RATE': self.sounds[cur_sound].rate = ebrw_readstr.int_s32()
			if part_obj.id == b'FINE': self.sounds[cur_sound].fine = ebrw_readstr.int_s32()
			if part_obj.id == b'RELN': self.sounds[cur_sound].transpose = ebrw_readstr.int_s32()
			if part_obj.id == b'SVOL': self.sounds[cur_sound].volume = ebrw_readstr.int_s32()
			if part_obj.id == b'SOFF': self.sounds[cur_sound].start = ebrw_readstr.int_s32()
			if part_obj.id == b'SOF2': self.sounds[cur_sound].end = ebrw_readstr.int_s32()
			if part_obj.id == b'SND1': 
				ebrw_readstr.skip(8)
				self.sounds[cur_sound].data = ebrw_readstr.raw(part_obj.size-8)
			if part_obj.id == b'SND2': 
				ebrw_readstr.skip(8)
				self.sounds[cur_sound].data = ebrw_readstr.raw(part_obj.size-8)
		return True
