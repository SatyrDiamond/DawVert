# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
from external.easybinrw import easybinrw
from external.easybinrw import chunked

import logging
logger_projparse = logging.getLogger('projparse')

chunk_size_data = chunked.chunk_part_size()
chunk_size_data.name_size = 3

class sn2_instrument:
	def __init__(self, ebrw_readstr, chunkend):
		self.type = ebrw_readstr.int_u8()
		self.name = ''
		if self.type == 1: 
			self.name = ebrw_readstr.string(chunkend-ebrw_readstr.tell())
		if self.type == 0: 
			insttype = ebrw_readstr.raw(3)
			if insttype == b'SMP':
				self.name = ebrw_readstr.string_t()
				self.unk0 = ebrw_readstr.int_u16()
				self.samplesize = ebrw_readstr.int_s32()
				self.loopstart = ebrw_readstr.int_s32()
				self.unk3 = ebrw_readstr.int_s32()
				self.unk4 = ebrw_readstr.int_u16()
				self.freq = ebrw_readstr.int_u16()
				self.data = ebrw_readstr.raw(self.samplesize)
			else:
				self.name = ''
				self.samplesize = 0
				self.loopstart = 0
				self.freq = 0
				self.data = b''

class sn2_event:
	__slot__ = ['len', 'type', 'value', 'p_len', 'p_key']
	def __init__(self):
		self.len = 0
		self.type = 0
		self.value = 0
		self.p_len = 0
		self.p_key = 0

class sn2_voice:
	def __init__(self, ebrw_readstr, end):
		self.instid = ebrw_readstr.int_u8()
		ebrw_readstr.skip(3)
		self.events = []
		while ebrw_readstr.tell() < end:
			event = sn2_event()
			event.len = ebrw_readstr.int_u8()
			if event.len == 255: 
				event.len = ebrw_readstr.int_s32()
				ebrw_readstr.skip(4)
			event.type = ebrw_readstr.int_u8()
			event.value = ebrw_readstr.int_u8()
			if event.type == 54: 
				event.p_key = ebrw_readstr.int_u8()
				event.p_len = ebrw_readstr.int_u8()
			self.events.append(event)

class sn2_pattern:
	def __init__(self, ebrw_readstr, chunk_obj):
		self.voices = []
		self.name = []
		self.tempos = []
		ebrw_readstr.skip(4)
		#print('[soundclub2] Pattern')
		for part_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if part_obj.id == b'pna': 
				self.name = ebrw_readstr.string(part_obj.size)
				#print('[soundclub2]	  Name:',self.name)
			if part_obj.id == b'tem': 
				pointssize = part_obj.size//8
				#print('[soundclub2]	  Tempo Points:',pointssize)
				for x  in range(pointssize):
					self.tempos.append([ebrw_readstr.int_u32(), ebrw_readstr.int_u8(), ebrw_readstr.int_u8(), ebrw_readstr.int_u8(), ebrw_readstr.int_u8()])
			if part_obj.id == b'voi': 
				voice_obj = sn2_voice(ebrw_readstr, part_obj.size)
				self.voices.append(voice_obj)
				#print('[soundclub2]	  Events for Inst '+str(voice_obj.instid)+':', len(voice_obj.notes))


class sn2_song:
	def __init__(self):
		pass

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		try: ebrw_readstr.magic_check(b'SN2')
		except ValueError as t: raise ProjectFileParserException('soundclub2: '+str(t))
		
		end_data = ebrw_readstr.int_u32()

		self.unk1 = ebrw_readstr.int_u32()
		self.unk2 = ebrw_readstr.int_u32()
		self.unk3 = ebrw_readstr.int_u32()
		self.tempo = ebrw_readstr.int_u32()
		self.ts_num = ebrw_readstr.int_u32()
		self.ts_denum = ebrw_readstr.int_u32()

		self.comment = ''
		self.sequence = []
		self.instruments = []
		self.patterns = []

		for part_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if part_obj.id == b'NAM': self.comment = ebrw_readstr.string(part_obj.size)
			if part_obj.id == b'SEQ': self.sequence = ebrw_readstr.list_int_s32(part_obj.size//4)
			if part_obj.id == b'INS': self.instruments.append(sn2_instrument(ebrw_readstr, part_obj.end))
			if part_obj.id == b'PAT': self.patterns.append(sn2_pattern(ebrw_readstr, part_obj))

		return True