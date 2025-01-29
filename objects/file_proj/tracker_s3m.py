# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects import audio_data
from objects.exceptions import ProjectFileParserException
from functions import data_bytes
import numpy as np
import os

import logging
logger_projparse = logging.getLogger('projparse')

class s3m_instrument:
	def __init__(self, song_file, ptr):
		self.song_file = song_file
		song_file.seek(ptr)
		self.type = song_file.uint8()
		self.filename = song_file.string(12, encoding="windows-1252")
		self.name = ''
		self.volume = 1
		if self.type == 0 or self.type == 1:
			self.ptrDataH = song_file.raw(1)
			self.ptrDataL = song_file.raw(2)
			self.sampleloc = int.from_bytes(self.ptrDataL + self.ptrDataH, "little")*16
			self.length = song_file.uint32()
			self.loopStart = song_file.uint32()
			self.loopEnd = song_file.uint32()
			self.volume = song_file.uint8()
			self.reserved = song_file.uint8()
			self.pack = song_file.uint8()
			self.flags = song_file.flags8()
			self.double = 2 in self.flags
			self.stereo = 1 in self.flags
			self.loopon = 0 in self.flags
			self.c2spd = song_file.uint32()
			self.internal = song_file.raw(12)
			self.name = song_file.string(28, encoding="windows-1252")
			self.sig = song_file.raw(4)
			samplelen = self.length if not self.double else self.length*2
			self.data = song_file.raw(samplelen)
		if self.type == 2:
			self.reserved = song_file.raw(3)
			self.oplValues = song_file.l_uint8(12)
			self.volume = song_file.uint8()
			self.dsk = song_file.uint8()
			self.reserved2 = song_file.raw(2)
			self.c2spd = song_file.uint32()
			self.unused = song_file.raw(12)
			self.name = song_file.string(28, encoding="windows-1252")
			self.sig = song_file.raw(4)

		if self.type == 0: logger_projparse.info('s3m: MSG | "' + self.name + '", Filename:"' + self.filename+ '"')
		if self.type == 1: logger_projparse.info('s3m: PCM | "' + self.name + '", Filename:"' + self.filename+ '"')
		if self.type == 2: logger_projparse.info('s3m: OPL | "' + self.name + '", Filename:"' + self.filename+ '"')

	def rip_sample(self, samplefolder, s3m_samptype, wave_path):
		if self.type == 1:
			if self.sampleloc != 0 and self.length != 0:
				self.song_file.seek(self.sampleloc)
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
						tempsample = np.frombuffer(self.song_file.read(t_samplelen), dtype=np.uint8)
						outdata[:len(tempsample)*2] = tempsample
					else:
						outdata = np.zeros(t_samplelen*2, dtype=np.uint8)
						tempsample = np.frombuffer(self.song_file.read(t_samplelen), dtype=np.uint8)
						outdata[:len(tempsample)*2][0::2] = tempsample
						tempsample = np.frombuffer(self.song_file.read(t_samplelen), dtype=np.uint8)
						outdata[:len(tempsample)*2][1::2] = tempsample

				if self.double == 1: 
					audio_obj.set_codec('uint16')
					if not self.stereo: 
						outdata = np.zeros(t_samplelen//2, dtype=np.uint16)
						tempsample = np.frombuffer(self.song_file.read(t_samplelen), dtype=np.uint16)
						outdata[:len(tempsample)] = tempsample
					else:
						outdata = np.zeros(t_samplelen*2, dtype=np.uint16)
						tempsample = np.frombuffer(self.song_file.read(t_samplelen), dtype=np.uint16)
						outdata[:len(tempsample)*2][0::2] = tempsample
						tempsample = np.frombuffer(self.song_file.read(t_samplelen), dtype=np.uint16)
						outdata[:len(tempsample)*2][1::2] = tempsample

				audio_obj.pcm_from_list(outdata)
				if self.loopon: audio_obj.loop = [self.loopStart, self.loopEnd-1]
				audio_obj.to_file_wav(wave_path)

class s3m_pattern:
	def __init__(self, song_file, ptr):
		song_file.seek(ptr)
		data_len = song_file.uint16()
		self.data = []
		if ptr != 0:
			for _ in range(64):
				pattern_done = 0
				rowdata = []
				while pattern_done == 0:
					packed_what = song_file.uint8()

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
							packed_note = song_file.uint8()
							packed_inst = song_file.uint8()
						if packed_what_vol == 1: packed_vol = song_file.uint8()
						if packed_what_command_info == 1: packed_command = song_file.uint8()
						if packed_what_command_info == 1: packed_info = song_file.uint8()

						rowdata.append([packed_what_channel, packed_note, packed_inst, packed_vol, packed_command, packed_info])
				self.data.append(rowdata)


class s3m_song:
	def __init__(self):
		pass

	def load_from_raw(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_raw(input_file)
		return self.load(song_file)

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)
		return self.load(song_file)

	def load(self, song_file):
		self.name = song_file.string(28, encoding="windows-1252")
		logger_projparse.info("s3m: Song Name: " + str(self.name))
		self.sig1 = song_file.uint8()
		self.type = song_file.uint8()
		self.reserved = song_file.uint16()
		self.num_orders = song_file.uint16()
		self.num_instruments = song_file.uint16()
		if self.num_instruments > 255: raise ProjectFileParserException('s3m: # of Instruments is over 255')
		logger_projparse.info("s3m: # of Instruments: " + str(self.num_instruments))
		self.num_patterns = song_file.uint16()
		if self.num_patterns > 255: raise ProjectFileParserException('s3m: # of Patterns is over 255')
		logger_projparse.info("s3m: # of Patterns: " + str(self.num_patterns))
		self.flags = song_file.flags16()
		self.trkrvers = song_file.raw(2)
		self.samptype = song_file.uint16()
		self.sig2 = song_file.raw(4)
		self.global_vol = song_file.uint8()
		self.speed = song_file.uint8()
		self.tempo = song_file.uint8()
		logger_projparse.info("s3m: Tempo: " + str(self.tempo))
		self.mastervol = song_file.uint8()
		self.ultra_click_removal = song_file.uint8()
		self.default_pan = song_file.uint8()
		self.reserved2 = song_file.raw(8)
		self.num_special = song_file.uint16()
		self.channel_settings = song_file.l_uint8(32)
		self.l_order = song_file.l_int8(self.num_orders)
		logger_projparse.info("s3m: Order List: " + str(self.l_order))
		self.ptrs_insts = [song_file.uint16()*16 for _ in range(self.num_instruments)]
		self.ptrs_patterns = [song_file.uint16()*16 for _ in range(self.num_patterns)]

		self.instruments = [s3m_instrument(song_file, x) for n, x in enumerate(self.ptrs_insts)]
		self.patterns = [s3m_pattern(song_file, x) for n, x in enumerate(self.ptrs_patterns)]

		#self.instruments[0].rip_sample(song_file, '.', self.samptype, 'test.wav')
		return True