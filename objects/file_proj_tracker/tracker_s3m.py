# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from objects import audio_data
from objects.exceptions import ProjectFileParserException
from functions import data_bytes
import numpy as np
import os

import logging
logger_projparse = logging.getLogger('projparse')

class s3m_instrument:
	def __init__(self):
		self.c2spd = 0
		self.double = False
		self.filename = ''
		self.internal = 0
		self.length = 0
		self.loopEnd = 0
		self.loopon = False
		self.loopStart = 0
		self.name = ''
		self.pack = 0
		self.reserved = None
		self.sampleloc = 0
		self.sig = 0
		self.stereo = False
		self.type = 0
		self.volume = 0
		self.oplValues = None
		self.dsk = None
		self.reserved2 = None
		self.unused = None
		self.data = None
		self.ebrw_readstr = None

	def read(self, ebrw_readstr, ptr):
		self.__init__()
		self.ebrw_readstr = ebrw_readstr
		ebrw_readstr.seek(ptr)
		self.type = ebrw_readstr.int_u8()
		self.filename = ebrw_readstr.string(12, encoding="windows-1252")
		if self.type == 0 or self.type == 1:
			self.ptrDataH = ebrw_readstr.raw(1)
			self.ptrDataL = ebrw_readstr.raw(2)
			self.sampleloc = int.from_bytes(self.ptrDataL + self.ptrDataH, "little")*16
			self.length = ebrw_readstr.int_u32()
			self.loopStart = ebrw_readstr.int_u32()
			self.loopEnd = ebrw_readstr.int_u32()
			self.volume = ebrw_readstr.int_u8()
			self.reserved = ebrw_readstr.int_u8()
			self.pack = ebrw_readstr.int_u8()
			self.flags = ebrw_readstr.flags_i8()
			self.double = 2 in self.flags
			self.stereo = 1 in self.flags
			self.loopon = 0 in self.flags
			self.c2spd = ebrw_readstr.int_u32()
			self.internal = ebrw_readstr.raw(12)
			self.name = ebrw_readstr.string(28, encoding="windows-1252")
			self.sig = ebrw_readstr.raw(4)
			samplelen = self.length if not self.double else self.length*2
			self.data = ebrw_readstr.raw(samplelen)
		if self.type == 2:
			self.reserved = ebrw_readstr.raw(3)
			self.oplValues = ebrw_readstr.list_int_u8(12)
			self.volume = ebrw_readstr.int_u8()
			self.dsk = ebrw_readstr.int_u8()
			self.reserved2 = ebrw_readstr.raw(2)
			self.c2spd = ebrw_readstr.int_u32()
			self.unused = ebrw_readstr.raw(12)
			self.name = ebrw_readstr.string(28, encoding="windows-1252")
			self.sig = ebrw_readstr.raw(4)

		if self.type == 0: logger_projparse.info('s3m: MSG | "' + self.name + '", Filename:"' + self.filename+ '"')
		if self.type == 1: logger_projparse.info('s3m: PCM | "' + self.name + '", Filename:"' + self.filename+ '"')
		if self.type == 2: logger_projparse.info('s3m: OPL | "' + self.name + '", Filename:"' + self.filename+ '"')

	def get_len(self):
		return self.length if not self.double else self.length*2

	def rip_sample(self, samplefolder, s3m_samptype, wave_path):
		if self.type == 1 and self.ebrw_readstr is not None:
			if self.sampleloc != 0 and self.length != 0:
				self.ebrw_readstr.seek(self.sampleloc)
				os.makedirs(samplefolder, exist_ok=True)
				t_samplelen = self.length if not self.double else self.length*2
				wave_bits = 8 if not self.double else 16
				wave_channels = 1 if not self.stereo else 2

				audio_obj = audio_data.audio_obj()
				audio_obj.rate = self.c2spd
				audio_obj.channels = wave_channels

				if self.double == 0:
					audio_obj.set_codec('uint8')
					if not self.stereo: 
						outdata = np.zeros(t_samplelen, dtype=np.uint8)
						tempsample = np.frombuffer(self.ebrw_readstr.read(t_samplelen), dtype=np.uint8)
						outdata[:len(tempsample)*2] = tempsample
					else:
						outdata = np.zeros(t_samplelen*2, dtype=np.uint8)
						tempsample = np.frombuffer(self.ebrw_readstr.read(t_samplelen), dtype=np.uint8)
						outdata[:len(tempsample)*2][0::2] = tempsample
						tempsample = np.frombuffer(self.ebrw_readstr.read(t_samplelen), dtype=np.uint8)
						outdata[:len(tempsample)*2][1::2] = tempsample

				if self.double == 1: 
					audio_obj.set_codec('uint16')
					if not self.stereo: 
						outdata = np.zeros(t_samplelen//2, dtype=np.uint16)
						tempsample = np.frombuffer(self.ebrw_readstr.read(t_samplelen), dtype=np.uint16)
						outdata[:len(tempsample)] = tempsample
					else:
						outdata = np.zeros(t_samplelen*2, dtype=np.uint16)
						tempsample = np.frombuffer(self.ebrw_readstr.read(t_samplelen), dtype=np.uint16)
						outdata[:len(tempsample)*2][0::2] = tempsample
						tempsample = np.frombuffer(self.ebrw_readstr.read(t_samplelen), dtype=np.uint16)
						outdata[:len(tempsample)*2][1::2] = tempsample

				audio_obj.pcm_from_list(outdata)
				if self.loopon: audio_obj.loop = [self.loopStart, self.loopEnd-1]
				audio_obj.to_file_wav(wave_path)

class s3m_pattern:
	def __init__(self):
		self.data = []

	def read(self, ebrw_readstr, ptr):
		ebrw_readstr.seek(ptr)
		data_len = ebrw_readstr.int_u16()
		self.data = []
		if ptr != 0:
			for _ in range(64):
				pattern_done = 0
				rowdata = []
				while pattern_done == 0:
					packed_what = ebrw_readstr.int_u8()

					if not packed_what: pattern_done = 1
					else:
						packed_what_command_info = bool(packed_what&128)
						packed_what_vol = bool(packed_what&64)
						packed_what_note_instrument = bool(packed_what&32)
						packed_what_channel = packed_what&31

						packed_note = None
						packed_inst = None
						packed_vol = None
						packed_command = None
						packed_info = None

						if packed_what_note_instrument == 1:
							packed_note = ebrw_readstr.int_u8()
							packed_inst = ebrw_readstr.int_u8()
						if packed_what_vol == 1: packed_vol = ebrw_readstr.int_u8()
						if packed_what_command_info == 1: packed_command = ebrw_readstr.int_u8()
						if packed_what_command_info == 1: packed_info = ebrw_readstr.int_u8()

						rowdata.append([packed_what_channel, packed_note, packed_inst, packed_vol, packed_command, packed_info])
				self.data.append(rowdata)

class s3m_song:
	def __init__(self):
		self.name = ''
		self.sig1 = 26
		self.type = 16
		self.reserved = 0
		self.flags = []
		self.trkrvers = b' \x13'
		self.samptype = 2
		self.sig2 = b'SCRM'
		self.global_vol = 32
		self.speed = 6
		self.tempo = 120
		self.mastervol = 128
		self.ultra_click_removal = 16
		self.default_pan = 252
		self.reserved2 = None
		self.num_special = 0
		self.channel_settings = []
		self.l_order = []
		self.instruments = []
		self.patterns = []

	def load_from_raw(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(input_file)
		return self.load(ebrw_readstr)

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		return self.load(ebrw_readstr)

	def load(self, ebrw_readstr):
		self.name = ebrw_readstr.string(28, encoding="windows-1252")
		logger_projparse.info("s3m: Song Name: " + str(self.name))
		self.sig1 = ebrw_readstr.int_u8()
		self.type = ebrw_readstr.int_u8()
		self.reserved = ebrw_readstr.int_u16()

		num_orders = ebrw_readstr.int_u16()

		num_instruments = ebrw_readstr.int_u16()
		if num_instruments > 255: 
			raise ProjectFileParserException('s3m: # of Instruments is over 255')
		else:
			logger_projparse.info("s3m: # of Instruments: " + str(num_instruments))

		num_patterns = ebrw_readstr.int_u16()
		if num_patterns > 255: 
			raise ProjectFileParserException('s3m: # of Patterns is over 255')
		else:
			logger_projparse.info("s3m: # of Patterns: " + str(num_patterns))

		self.flags = ebrw_readstr.flags_i16()
		self.trkrvers = ebrw_readstr.raw(2)
		self.samptype = ebrw_readstr.int_u16()
		self.sig2 = ebrw_readstr.raw(4)
		self.global_vol = ebrw_readstr.int_u8()
		self.speed = ebrw_readstr.int_u8()
		self.tempo = ebrw_readstr.int_u8()

		logger_projparse.info("s3m: Tempo: " + str(self.tempo))
		self.mastervol = ebrw_readstr.int_u8()
		self.ultra_click_removal = ebrw_readstr.int_u8()
		self.default_pan = ebrw_readstr.int_u8()
		self.reserved2 = ebrw_readstr.raw(8)
		self.num_special = ebrw_readstr.int_u16()
		self.channel_settings = ebrw_readstr.list_int_u8(32)
		self.l_order = ebrw_readstr.list_int_u8(num_orders)
		logger_projparse.info("s3m: Order List: " + str(self.l_order))
		ptrs_insts = [ebrw_readstr.int_u16()*16 for _ in range(num_instruments)]
		ptrs_patterns = [ebrw_readstr.int_u16()*16 for _ in range(num_patterns)]

		self.instruments = [s3m_instrument() for _ in range(num_instruments)]
		self.patterns = [s3m_pattern() for _ in range(num_patterns)]

		for n, x in enumerate(ptrs_insts):
			self.instruments[n].read(ebrw_readstr, x)
		for n, x in enumerate(ptrs_patterns):
			self.patterns[n].read(ebrw_readstr, x)

		#self.instruments[0].rip_sample(ebrw_readstr, '.', self.samptype, 'test.wav')
		return True