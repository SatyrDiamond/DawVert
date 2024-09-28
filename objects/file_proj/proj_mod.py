# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects.file_proj import proj_mod
import numpy as np
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

class mod_sample:
	def __init__(self, song_file): 
		self.errored = False
		self.name = song_file.string(22, encoding="ascii", errors="ignore") if song_file else ''
		self.length = song_file.uint16_b() if song_file else 0
		self.finetune = song_file.uint8() if song_file else 0
		self.default_vol = song_file.uint8() if song_file else 0
		self.loop_start = song_file.uint16_b() if song_file else 0
		self.loop_length = song_file.uint16_b() if song_file else 0
		self.data = None

pattern_dt = np.dtype('>H')

class mod_pattern:
	def __init__(self, song_file, num_chans):
		if song_file:
			self.data = np.frombuffer(song_file.raw(64*num_chans*4), pattern_dt).reshape(64, num_chans, 2)
		else:
			self.data = np.empty((64, num_chans, 2), dtype=pattern_dt)

class mod_song:
	def __init__(self):
		self.title = ''
		self.samples = []

	def load_from_raw(self, input_file, IGNORE_ERRORS):
		song_file = bytereader.bytereader()
		song_file.load_raw(input_file)
		return self.load(song_file, IGNORE_ERRORS)

	def load_from_file(self, input_file, IGNORE_ERRORS):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)
		return self.load(song_file, IGNORE_ERRORS)

	def load(self, song_file, IGNORE_ERRORS):
		self.title = song_file.string(20, encoding="ascii", errors="ignore")
		logger_projparse.info('mod: Song Name: ' + str(self.title))
		for _ in range(31):
			sample_obj = mod_sample(song_file)
			if sample_obj.finetune > 15: 
				if not IGNORE_ERRORS:
					raise ProjectFileParserException('mod: sample finetune over 15')
				else:
					logger_projparse.warning('mod: sample finetune over 15')

			self.samples.append(sample_obj)
		self.num_orders = song_file.uint8()
		self.extravalue = song_file.uint8()
		if not self.num_orders:
			if IGNORE_ERRORS:
				self.l_order = song_file.l_int8(128)
			else:
				raise ProjectFileParserException('mod: Pattern Order is 0')
		else:
			self.l_order = song_file.l_int8(128)[0:self.num_orders]
		self.num_patterns = max(self.l_order)

		self.tag = song_file.string(4, errors="ignore")
		self.num_chans = 4

		logger_projparse.info('mod: Sample Tag: ' + str(self.tag))
		logger_projparse.info('mod: Channels: ' + str(self.num_chans))

		if self.tag == '1CHN': self.num_chans = 1
		if self.tag == '6CHN': self.num_chans = 6
		if self.tag == '8CHN': self.num_chans = 8
		if self.tag == 'CD81': self.num_chans = 8
		if self.tag == 'OKTA': self.num_chans = 8
		if self.tag == 'OCTA': self.num_chans = 8
		if self.tag == '6CHN': self.num_chans = 6
		if self.tag[-2:] == 'CH': self.num_chans = int(self.tag[:2])
		if self.tag == '2CHN': self.num_chans = 2
		if self.tag[-2:] == 'CN': self.num_chans = int(self.tag[:2])
		if self.tag == 'TDZ1': self.num_chans = 1
		if self.tag == 'TDZ2': self.num_chans = 2
		if self.tag == 'TDZ3': self.num_chans = 3
		if self.tag == '5CHN': self.num_chans = 5
		if self.tag == '7CHN': self.num_chans = 7
		if self.tag == '9CHN': self.num_chans = 9
		if self.tag == 'FLT4': self.num_chans = 4
		if self.tag == 'FLT8': self.num_chans = 8

		self.patterns = [mod_pattern(song_file, self.num_chans) for _ in range(self.num_patterns+1)]
		for sample_obj in self.samples: sample_obj.data = song_file.raw(sample_obj.length*2)
		return True