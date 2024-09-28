# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
import logging
from objects.exceptions import ProjectFileParserException
logger_projparse = logging.getLogger('projparse')

class piximod_pattern:
	def __init__(self, song_file):
		song_file.skip(4)
		self.tracks = song_file.uint32()
		self.length = song_file.uint32()
		self.data = song_file.table8([self.length, self.tracks, 4])

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
		self.order = []
		self.patterns = {}
		self.sounds = [piximod_sample() for x in range(16)]

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)

		try: 
			song_file.magic_check(b'PIXIMOD1')
		except ValueError as t:
			raise ProjectFileParserException('piximod: '+str(t))

		main_iff_obj = song_file.chunk_objmake()
		cur_patnum = 0
		cur_sound = 0
		for chunk_obj in main_iff_obj.iter(song_file.tell(), song_file.end):
			if chunk_obj.id == b'BPM ': self.bpm = song_file.uint32()
			if chunk_obj.id == b'LPB ': self.lpb = song_file.uint32()
			if chunk_obj.id == b'TPL ': self.tpl = song_file.uint32()
			if chunk_obj.id == b'SHFL': self.shuffle = song_file.uint32()
			if chunk_obj.id == b'VOL ': self.vol = song_file.uint32()
			if chunk_obj.id == b'PATT':
				song_file.skip(4)
				num = song_file.uint32()
				song_file.skip(4)
				self.order = song_file.l_uint16(num)
			if chunk_obj.id == b'PATN': cur_patnum = song_file.uint32()
			if chunk_obj.id == b'PATD': self.patterns[cur_patnum] = piximod_pattern(song_file)
			if chunk_obj.id == b'SNDN': cur_sound = song_file.uint32()
			if chunk_obj.id == b'CHAN': self.sounds[cur_sound].channels = song_file.int32()
			if chunk_obj.id == b'RATE': self.sounds[cur_sound].rate = song_file.int32()
			if chunk_obj.id == b'FINE': self.sounds[cur_sound].fine = song_file.int32()
			if chunk_obj.id == b'RELN': self.sounds[cur_sound].transpose = song_file.int32()
			if chunk_obj.id == b'SVOL': self.sounds[cur_sound].volume = song_file.int32()
			if chunk_obj.id == b'SOFF': self.sounds[cur_sound].start = song_file.int32()
			if chunk_obj.id == b'SOF2': self.sounds[cur_sound].end = song_file.int32()
			if chunk_obj.id == b'SND1': 
				song_file.skip(8)
				self.sounds[cur_sound].data = song_file.raw(chunk_obj.size-8)
			if chunk_obj.id == b'SND2': 
				song_file.skip(8)
				self.sounds[cur_sound].data = song_file.raw(chunk_obj.size-8)
		return True