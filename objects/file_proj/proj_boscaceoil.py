# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
import numpy as np
from objects.data_bytes import bytereader

class ceol_instrument:
	def __init__(self, song_file):
		self.inst = 0
		self.type = 0
		self.palette = 0
		self.cutoff = 128
		self.resonance = 0
		self.volume = 256
		if song_file:
			self.inst = song_file.uint16()
			self.type = song_file.uint16()
			self.palette = song_file.uint16()
			self.cutoff = song_file.uint16()
			self.resonance = song_file.uint16()
			self.volume = song_file.uint16()

class ceol_note:
	__slots__ = ['key','len','pos']
	def __init__(self):
		self.key = 0
		self.len = 0
		self.pos = 0

class ceol_pattern:
	def __init__(self, song_file):
		self.notes = []
		self.recordfilter = None
		if song_file:
			self.key = song_file.uint16()
			self.scale = song_file.uint16()
			self.inst = song_file.uint16()
			self.palette = song_file.uint16()
			numnotes = song_file.uint16()
			for _ in range(numnotes):
				note_obj = ceol_note()
				note_obj.key = song_file.uint16()
				note_obj.len = song_file.uint16()
				note_obj.pos = song_file.uint16()
				song_file.skip(2)
				self.notes.append(note_obj)
			if song_file.uint16():
				self.recordfilter = song_file.table16([16, 3])

class ceol_song:
	def __init__(self):
		self.swing = 0
		self.effect_type = 0
		self.effect_value = 0
		self.bpm = 120
		self.pattern_length = 16
		self.bar_length = 4
		self.instruments = []
		self.patterns = []
		self.spots = []

	def load_from_file(self, input_file):
		ceol_file = open(input_file, 'r')

		try: ceolnums = ceol_file.readline().split(',')[:-1]
		except: raise ProjectFileParserException('boscaceoil: File is not text.')

		ceol_array = np.asarray([int(x) for x in ceolnums], dtype=np.int16)

		if not len(ceol_array):
			raise ProjectFileParserException('boscaceoil: array is empty')
		
		song_file = bytereader.bytereader()
		song_file.load_raw(ceol_array.tobytes())
		self.versionnum = song_file.uint16()

		self.swing = song_file.uint16()
		self.effect_type = song_file.uint16()
		self.effect_value = song_file.uint16()
		self.bpm = song_file.uint16()
		self.pattern_length = song_file.uint16()
		self.bar_length = song_file.uint16()
		self.instruments = [ceol_instrument(song_file) for x in range(song_file.uint16())]
		self.patterns = [ceol_pattern(song_file) for x in range(song_file.uint16())]

		self.length = song_file.uint16()
		self.loopstart = song_file.uint16()
		self.loopend = song_file.uint16()
		self.spots = song_file.stable16([self.length, 8])
		return True
