# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

class sn2_instrument:
	def __init__(self, song_file, chunkend):
		self.type = song_file.uint8()
		self.name = ''
		if self.type == 1: 
			self.name = song_file.string(chunkend-song_file.tell())
		if self.type == 0: 
			insttype = song_file.raw(3)
			if insttype == b'SMP':
				self.name = song_file.string_t()

				self.unk0 = song_file.uint16()

				self.samplesize = song_file.int32()
				self.loopstart = song_file.int32()
				self.unk3 = song_file.int32()
				self.unk4 = song_file.uint16()
				self.freq = song_file.uint16()

				self.data = song_file.raw(self.samplesize)
			else:
				self.name = ''
				self.samplesize = 0
				self.loopstart = 0
				self.freq = 0
				self.data = b''
		#print('[soundclub2] Instrument:', self.name)

class sn2_event:
	__slot__ = ['len', 'type', 'value', 'p_len', 'p_key']
	def __init__(self):
		self.len = 0
		self.type = 0
		self.value = 0
		self.p_len = 0
		self.p_key = 0

class sn2_voice:
	def __init__(self, song_file, end):
		self.instid = song_file.uint8()
		song_file.skip(3)
		self.events = []
		while song_file.tell() < end:
			event = sn2_event()
			event.len = song_file.uint8()
			if event.len == 255: 
				event.len = song_file.int32()
				song_file.skip(4)
			event.type = song_file.uint8()
			event.value = song_file.uint8()
			if event.type == 54: 
				event.p_key = song_file.uint8()
				event.p_len = song_file.uint8()
			self.events.append(event)


class sn2_pattern:
	def __init__(self, song_file, chunk_obj):
		self.voices = []
		self.name = []
		self.tempos = []
		#print('[soundclub2] Pattern')
		for subchunk_obj in chunk_obj.iter(4):
			if subchunk_obj.id == b'pna': 
				self.name = song_file.string(subchunk_obj.size)
				#print('[soundclub2]	  Name:',self.name)
			if subchunk_obj.id == b'tem': 
				pointssize = subchunk_obj.size//8
				#print('[soundclub2]	  Tempo Points:',pointssize)
				for x  in range(pointssize):
					self.tempos.append([song_file.uint32(), song_file.uint8(), song_file.uint8(), song_file.uint8(), song_file.uint8()])

			if subchunk_obj.id == b'voi': 
				voice_obj = sn2_voice(song_file, subchunk_obj.end)
				self.voices.append(voice_obj)
				#print('[soundclub2]	  Events for Inst '+str(voice_obj.instid)+':', len(voice_obj.notes))


class sn2_song:
	def __init__(self):
		pass

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)

		try: song_file.magic_check(b'SN2')
		except ValueError as t: raise ProjectFileParserException('soundclub2: '+str(t))
		
		end_data = song_file.uint32()

		self.unk1 = song_file.uint32()
		self.unk2 = song_file.uint32()
		self.unk3 = song_file.uint32()
		self.tempo = song_file.uint32()
		self.ts_num = song_file.uint32()
		self.ts_denum = song_file.uint32()

		self.comment = ''
		self.sequence = []
		self.instruments = []
		self.patterns = []

		main_iff_obj = song_file.chunk_objmake()
		main_iff_obj.set_sizes(3, 4, False)
		for chunk_obj in main_iff_obj.iter(song_file.tell(), song_file.end):
			if chunk_obj.id == b'NAM': self.comment = song_file.string(chunk_obj.size)
			if chunk_obj.id == b'SEQ': self.sequence = song_file.l_int32(chunk_obj.size//4)
			if chunk_obj.id == b'INS': self.instruments.append(sn2_instrument(song_file, chunk_obj.end))
			if chunk_obj.id == b'PAT': self.patterns.append(sn2_pattern(song_file, chunk_obj))

		return True