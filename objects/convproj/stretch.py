# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from dataclasses import field
from functions import xtramath
from contextlib import contextmanager
from objects.convproj import time
import bisect

time_content = time.time_content

@dataclass
class cvpj_stretch_algo:
	type: str = 'stretch'
	subtype: str = ''
	params: dict = field(default_factory=dict)
	formant: float = 0

@dataclass
class pl_manip:
	pos_offset: float = 0
	cut_offset: float = 0
	cut_mul: float = 1

@dataclass
class cvpj_stretch:
	algorithm: cvpj_stretch_algo = field(default_factory=cvpj_stretch_algo)
	timing: time_content = field(default_factory=time_content)
	preserve_pitch: bool = False

	def changestretch(self, samplereflist, sampleref, target, tempo, ppq, pitch):
		iffound = sampleref in samplereflist
		pl_timemul = pl_manip()
		finalspeed = 1

		if iffound:
			sampleref_obj = samplereflist[sampleref]

			is_warped = self.timing.time_type == 'warp'

			if not is_warped and target == 'warp':
				dur_sec = sampleref_obj.get_dur_sec()
				if dur_sec: self.timing.changestretch_rate2warp(pl_timemul, sampleref_obj, tempo, pitch)

			if is_warped and target == 'rate':
				self.timing.changestretch_warp2rate(pl_timemul)

		return pl_timemul

	def debugtxt(self):
		headersize = 12
		debugsize = 20
		print('-'*headersize, end='')
		print('+' + '-'*debugsize, end='')
		print('+' + '-'*debugsize, end='')
		print('+', end='')
		print()
		print('bpm/speed'.ljust(headersize), end='')
		print('|' + str(self.bpm).ljust(debugsize), end='')
		print('|' + str(self.org_speed).ljust(debugsize), end='')
		print('|', end='')
		print()
		print('calc_bpm'.ljust(headersize), end='')
		print('|' + str(self.calc_bpm_speed).ljust(debugsize), end='')
		print('|' + str(self.calc_bpm_size).ljust(debugsize), end='')
		print('|', end='')
		print()
		print('calc_tempo'.ljust(headersize), end='')
		print('|' + str(self.calc_tempo_speed).ljust(debugsize), end='')
		print('|' + str(self.calc_tempo_size).ljust(debugsize), end='')
		print('|', end='')
		print()
		print('calc_real'.ljust(headersize), end='')
		print('|' + str(self.calc_real_speed).ljust(debugsize), end='')
		print('|' + str(self.calc_real_size).ljust(debugsize), end='')
		print('|', end='')
		print()
		print('-'*headersize, end='')
		print('+' + '-'*debugsize, end='')
		print('+' + '-'*debugsize, end='')
		print('+', end='')
		print()