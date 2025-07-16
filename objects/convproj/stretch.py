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


	def changestretch_rate2warp(self, pl_timemul, sampleref_obj, tempo, pitch):
		s_timing_obj = self.timing

		dur_sec = sampleref_obj.get_dur_sec()

		muloffset = 1

		if s_timing_obj.tempo_based:
			calc_tempo_size = s_timing_obj.get__speed(sampleref_obj)
			pos_real = sampleref_obj.dur_sec*calc_tempo_size
		
			with s_timing_obj.setup_warp(False) as warp_obj:
				warp_point_obj = warp_obj.points__add()
				warp_point_obj.speed = 1/calc_tempo_size
		
				warp_point_obj = warp_obj.points__add()
				warp_point_obj.beat = pos_real*2
				warp_point_obj.second = sampleref_obj.dur_sec
				warp_point_obj.speed = 1/calc_tempo_size
		else:
			calc_speed_size = s_timing_obj.get__speed(sampleref_obj)
			calc_bpm_size = (tempo/120)
			pos_real = sampleref_obj.dur_sec*calc_speed_size*calc_bpm_size
		
			if self.timing.time_type == 'speed':
				pl_timemul.cut_mul = calc_speed_size

			with s_timing_obj.setup_warp(True) as warp_obj:
				warp_point_obj = warp_obj.points__add()
		
				warp_point_obj = warp_obj.points__add()
				warp_point_obj.beat = pos_real*2
				warp_point_obj.second = sampleref_obj.dur_sec

			muloffset = calc_speed_size

		warp_obj.calcpoints__speed()

	def changestretch(self, samplereflist, sampleref, target, tempo, ppq, pitch):
		iffound = sampleref in samplereflist
		pl_timemul = pl_manip()
		finalspeed = 1

		if iffound:
			sampleref_obj = samplereflist[sampleref]

			is_warped = self.timing.time_type == 'warp'

			if not is_warped and target == 'warp':
				dur_sec = sampleref_obj.get_dur_sec()
				if dur_sec: self.changestretch_rate2warp(pl_timemul, sampleref_obj, tempo, pitch)

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