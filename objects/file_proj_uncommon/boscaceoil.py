# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from objects.exceptions import ProjectFileParserException
import numpy as np

# ============================================= instrument ============================================= 

scale_data = [
["Scale: Major", [2, 2, 1, 2, 2, 2, 1]],
["Scale: Minor", [2, 1, 2, 2, 2, 2, 1]],
["Scale: Blues", [3, 2, 1, 1, 3, 2]],
["Scale: Harmonic Minor", [2, 1, 2, 2, 1, 3, 1]],
["Scale: Pentatonic Major", [2, 3, 2, 2, 3]],
["Scale: Pentatonic Minor", [3, 2, 2, 3, 2]],
["Scale: Pentatonic Blues", [3, 2, 1, 1, 3, 2]],
["Scale: Pentatonic Neutral", [2, 3, 2, 3, 2]],
["Scale: Romanian Folk", [2, 1, 3, 1, 2, 1, 2]],
["Scale: Spanish Gypsy", [2, 1, 3, 1, 2, 1, 2]],
["Scale: Arabic Magam", [2, 2, 1, 1, 2, 2, 2]],
["Scale: Chinese", [4, 2, 1, 4, 1]],
["Scale: Hungarian", [2, 1, 3, 1, 1, 3, 1]],
["Chord: Major", [4, 3, 5]],
["Chord: Minor", [3, 4, 5]],
["Chord: 5th", [7, 5]],
["Chord: Dom 7th", [4, 3, 3, 2]],
["Chord: Major 7th", [4, 3, 4, 1]],
["Chord: Minor 7th", [3, 4, 3, 2]],
["Chord: Minor Major 7th", [3, 4, 4, 1]],
["Chord: Sus4", [5, 2, 5]],
["Chord: sus2", [2, 5, 5]]
]

class ceol_instrument:
	def __init__(self, ebrw_readstr):
		self.inst = 0
		self.type = 0
		self.palette = 0
		self.cutoff = 128
		self.resonance = 0
		self.volume = 256
		if ebrw_readstr:
			self.inst = ebrw_readstr.int_u16()
			self.type = ebrw_readstr.int_u16()
			self.palette = ebrw_readstr.int_u16()
			self.cutoff = ebrw_readstr.int_u16()
			self.resonance = ebrw_readstr.int_u16()
			self.volume = ebrw_readstr.int_u16()

	def write_ebrw(self, ebrw_writestr):
		ebrw_writestr.int_u16(self.inst)
		ebrw_writestr.int_u16(self.type)
		ebrw_writestr.int_u16(self.palette)
		ebrw_writestr.int_u16(self.cutoff)
		ebrw_writestr.int_u16(self.resonance)
		ebrw_writestr.int_u16(self.volume)

# ============================================= pattern ============================================= 

class ceol_note:
	__slots__ = ['key','len','pos']
	def __init__(self):
		self.key = 0
		self.len = 0
		self.pos = 0

	def read(self, ebrw_readstr):
		self.key = ebrw_readstr.int_u16()
		self.len = ebrw_readstr.int_u16()
		self.pos = ebrw_readstr.int_u16()
		ebrw_readstr.skip(2)

	def write_ebrw(self, ebrw_writestr):
		ebrw_writestr.int_u16(self.key)
		ebrw_writestr.int_u16(self.len)
		ebrw_writestr.int_u16(self.pos)
		ebrw_writestr.int_u16(0)

class ceol_pattern:
	def __init__(self, ebrw_readstr):
		self.notes = []
		self.recordfilter = None
		if ebrw_readstr:
			self.key = ebrw_readstr.int_u16()
			self.scale = ebrw_readstr.int_u16()
			self.inst = ebrw_readstr.int_u16()
			self.palette = ebrw_readstr.int_u16()
			numnotes = ebrw_readstr.int_u16()
			for _ in range(numnotes):
				note_obj = ceol_note()
				note_obj.read(ebrw_readstr)
				self.notes.append(note_obj)
			if ebrw_readstr.int_u16():
				self.recordfilter = ebrw_readstr.list_int_u16(16*3)
				self.recordfilter = np.reshape(self.recordfilter, [16, 3])

	def write_ebrw(self, ebrw_writestr):
		ebrw_writestr.int_u16(self.key)
		ebrw_writestr.int_u16(self.scale)
		ebrw_writestr.int_u16(self.inst)
		ebrw_writestr.int_u16(self.palette)
		ebrw_writestr.int_u16(len(self.notes))
		for n in self.notes: n.write_ebrw(ebrw_writestr)
		ebrw_writestr.int_u16(1 if self.recordfilter!=None else 0)
		if self.recordfilter!=None:
			ebrw_readstr.list_int_u16(self.recordfilter.reshape([3, 16]).flatten(), 16*3)

# ============================================= song ============================================= 

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
		self.length = 0
		self.loopstart = 0
		self.loopend = 0

	def load_from_file(self, input_file):
		ceol_file = open(input_file, 'r')

		try: ceolnums = ceol_file.readline().split(',')[:-1]
		except: raise ProjectFileParserException('boscaceoil: File is not text.')

		ceol_array = np.asarray([int(x) for x in ceolnums], dtype=np.int16)

		if not len(ceol_array): raise ProjectFileParserException('boscaceoil: array is empty')
		
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(ceol_array.tobytes())
		self.versionnum = ebrw_readstr.int_u16()

		self.swing = ebrw_readstr.int_u16()
		self.effect_type = ebrw_readstr.int_u16()
		self.effect_value = ebrw_readstr.int_u16()
		self.bpm = ebrw_readstr.int_u16()
		self.pattern_length = ebrw_readstr.int_u16()
		self.bar_length = ebrw_readstr.int_u16()
		self.instruments = [ceol_instrument(ebrw_readstr) for x in range(ebrw_readstr.int_u16())]
		self.patterns = [ceol_pattern(ebrw_readstr) for x in range(ebrw_readstr.int_u16())]
		self.length = ebrw_readstr.int_u16()
		self.loopstart = ebrw_readstr.int_u16()
		self.loopend = ebrw_readstr.int_u16()
		self.spots = ebrw_readstr.list_int_s16(self.length*8)
		self.spots = np.reshape(self.spots, [self.length, 8])
		return True

	def write_ebrw(self, ebrw_writestr):
		ebrw_writestr.int_u16(self.versionnum)
		ebrw_writestr.int_u16(self.swing)
		ebrw_writestr.int_u16(self.effect_type)
		ebrw_writestr.int_u16(self.effect_value)
		ebrw_writestr.int_u16(self.bpm)
		ebrw_writestr.int_u16(self.pattern_length)
		ebrw_writestr.int_u16(self.bar_length)
		ebrw_writestr.int_u16(len(self.instruments))
		for i in self.instruments: i.write_ebrw(ebrw_writestr)
		ebrw_writestr.int_u16(len(self.patterns))
		for i in self.patterns: i.write_ebrw(ebrw_writestr)
		ebrw_writestr.int_u16(self.length)
		ebrw_writestr.int_u16(self.loopstart)
		ebrw_writestr.int_u16(self.loopend)
		spots = np.reshape(self.spots, [8, self.length]).flatten()
		ebrw_writestr.list_int_s16(spots, self.length*8)

	def save_to_file(self, output_file):
		ebrw_writestr = easybinrw.binwrite()
		self.write_ebrw(ebrw_writestr)
		outd = np.frombuffer(ebrw_writestr.getvalue(), dtype=np.int16)
		outtxt = ','.join([str(x) for x in outd])
		f = open(output_file, 'w')
		f.write(outtxt)