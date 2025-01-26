# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from dataclasses import field
from functions import xtramath

class cvpj_warp_point:
	def __init__(self):
		self.beat = 0
		self.second = 0
		self.speed = None

	def __eq__(self, other):
		e_beat = self.beat == other.beat
		e_second = self.second == other.second
		e_speed = self.speed == other.speed
		return e_beat and e_second and e_speed

	def __repr__(self):
		return ','.join([str(self.beat),str(self.second),str(self.speed)])

@dataclass
class cvpj_stretch_warp:
	points: list = field(default_factory=list)

	def add_warp_point(self):
		warp_point_obj = cvpj_warp_point()
		self.points.append(warp_point_obj)
		return warp_point_obj

	def rem_last_warp_point(self):
		self.points = self.points[0:-1]

	def iter_warp_points(self):
		for x in self.points: yield x

	def debugtxt_warp(self):
		print('------------- warps')
		for x in self.iter_warp_points():
			print('warp', end=' ')
			for d in [x.beat, x.second*x.speed*2, x.second, x.speed]:
				print(str(d).ljust(20), end=' ')
			print('')

	def calc_warp_points(self):
		if self.points:
			numpoints = len(self.points)-1
			for n, warp_point_obj in enumerate(self.points):
				if n<numpoints:
					next_warp = self.points[n+1]
					calc_beat = next_warp.beat - warp_point_obj.beat
					calc_second = next_warp.second - warp_point_obj.second
					calctempo = (calc_beat/2)/calc_second if calc_second else 1
					warp_point_obj.speed = calctempo

			if numpoints>2:
				self.points[-1].speed = self.points[-2].speed

			if numpoints>0:
				if not self.points[-1].speed:
					self.points[-1].speed = self.points[-2].speed

	def calc_warp_speed(self):
		if self.points:
			speedpoints = [x.speed for x in self.points]
			if None not in speedpoints:
				return xtramath.average(speedpoints)
			else:
				return 1
		else:
			return 1

	def change_warp_speed(self, speed):
		for warp_point_obj in self.points:
			warp_point_obj.beat *= speed

		self.calc_warp_points()

	def fix_single_warp(self, convproj_obj, sp_obj):
		if len(self.points) == 1:
			firstpoint = self.points[0]
			ref_found, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)
			if ref_found:
				warp_point_obj = self.add_warp_point()
				warp_point_obj.beat = sampleref_obj.dur_sec*firstpoint.speed*2
				warp_point_obj.second = sampleref_obj.dur_sec
				warp_point_obj.speed = firstpoint.speed

	def fix_warps(self, convproj_obj, sp_obj):
		offset = 0
		if self.points:
			if len(self.points)>1:
				firstpoint = self.points[0]

				if firstpoint.beat==0 and firstpoint.second>0:
					dursec = self.get_dur_sec()
					durbeat = self.get_dur_beat()
					speed = self.get_warp_speed()
					firstpoint.beat = (firstpoint.second/dursec)*durbeat
					warp_point_obj = cvpj_warp_point()
					warp_point_obj.speed = firstpoint.speed
					self.points.insert(0, warp_point_obj)
					offset += firstpoint.beat

				if firstpoint.beat<0:
					durbeat = self.get_dur_beat()
					dursec = self.get_dur_sec()
					speed = self.get_warp_speed()
					shiftpart = firstpoint.beat+durbeat

					splitb = (dursec/speed)/durbeat

					offset += durbeat*splitb

					for x in self.points:
						x.beat += shiftpart*2
						x.second += (dursec*splitb)

					warp_point_obj = cvpj_warp_point()
					warp_point_obj.speed = firstpoint.speed
					self.points.insert(0, warp_point_obj)

		return offset

	def get_first_sec(self):
		if self.points:
			return self.points[0].second
		else:
			return 0

	def get_first_beat(self):
		if self.points:
			firstpoint = self.points[0]
			return firstpoint.second*firstpoint.speed*2
		else:
			return 0

	def get_dur_beat(self):
		if self.points:
			lastpoint = self.points[-1]
			firstpoint = self.points[0]
			return (lastpoint.second*firstpoint.speed*2)-firstpoint.beat
		else:
			return 0

	def get_dur_sec(self):
		if self.points:
			lastpoint = self.points[-1]
			firstpoint = self.points[0]
			return lastpoint.second-((firstpoint.beat/firstpoint.speed)/2)
		else:
			return 0

	def get_warp_speed(self):
		if self.points:
			return 1/self.points[-1].speed
		else:
			return 1

@dataclass
class cvpj_stretch:
	algorithm: str = 'stretch'
	algorithm_mode: str = ''
	preserve_pitch: bool = False
	params: dict = field(default_factory=dict)
	is_warped: bool = False
	warppoints: list = field(default_factory=list)
	warp: cvpj_stretch_warp = field(default_factory=cvpj_stretch_warp)

	uses_tempo: bool = False

	bpm: float = 120
	org_speed: float = 1
	calc_bpm_speed: float = 1
	calc_bpm_size: float = 1
	calc_tempo_speed: float = 1
	calc_tempo_size: float = 1
	calc_real_speed: float = 1
	calc_real_size: float = 1

	def __bool__(self):
		return self.is_warped or (self.calc_tempo_speed != 1) or self.uses_tempo

	def __eq__(self, x):
		s_algorithm = self.algorithm == x.algorithm
		s_params = self.params == x.params
		s_is_warped = self.is_warped == x.is_warped
		s_warp = self.warp == x.warp
		uses_tempo = self.uses_tempo == x.uses_tempo

		s_bpm = self.bpm == x.bpm
		s_org_speed = self.org_speed == x.org_speed
		s_calc_bpm_speed = self.calc_bpm_speed == x.calc_bpm_speed
		s_calc_bpm_size = self.calc_bpm_size == x.calc_bpm_size
		s_calc_tempo_speed = self.calc_tempo_speed == x.calc_tempo_speed
		s_calc_tempo_size = self.calc_tempo_size == x.calc_tempo_size
		s_calc_real_speed = self.calc_real_speed == x.calc_real_speed
		s_calc_real_size = self.calc_real_size == x.calc_real_size

		return s_algorithm and s_params and s_is_warped and s_warp and uses_tempo and s_bpm and s_org_speed and s_calc_bpm_speed and s_calc_bpm_size and (s_calc_tempo_speed or s_calc_tempo_size or s_calc_real_speed or s_calc_real_size)

	def set_rate_speed(self, bpm, rate, is_size):
		self.uses_tempo = False
		self.bpm = bpm
		self.calc_bpm_speed = 120/self.bpm
		self.calc_bpm_size = self.bpm/120
		self.org_speed = rate
		self.calc_real_speed = rate if not is_size else 1/rate
		self.calc_real_size = 1/rate if not is_size else rate
		self.calc_tempo_speed = self.calc_real_speed*self.calc_bpm_speed
		self.calc_tempo_size = self.calc_real_size*self.calc_bpm_size

	def set_rate_tempo(self, bpm, rate, is_size):
		self.uses_tempo = True
		self.bpm = bpm
		self.calc_bpm_speed = 120/self.bpm
		self.calc_bpm_size = self.bpm/120
		self.org_speed = rate
		self.calc_tempo_speed = (rate if not is_size else 1/rate) if rate else 1
		self.calc_tempo_size = (1/rate if not is_size else rate) if rate else 1
		self.calc_real_speed = self.calc_tempo_speed/self.calc_bpm_speed
		self.calc_real_size = self.calc_tempo_size/self.calc_bpm_size

	def changestretch(self, samplereflist, sampleref, target, tempo, ppq, pitch):
		iffound = sampleref in samplereflist
		pos_offset = 0
		cut_offset = 0

		finalspeed = 1

		if iffound:
			sampleref_obj = samplereflist[sampleref]

			if not self.is_warped and target == 'warp':
				warp_obj.points = []
				self.is_warped = True
				warp_obj = stretch_obj.warp

				if self.uses_tempo:
					pos_real = sampleref_obj.dur_sec*self.calc_tempo_size
	
					warp_point_obj = warp_obj.add_warp_point()
					warp_point_obj.beat = 0
					warp_point_obj.second = 0
					warp_point_obj.speed = self.calc_tempo_size
	
					warp_point_obj = warp_obj.add_warp_point()
					warp_point_obj.beat = pos_real*2
					warp_point_obj.second = sampleref_obj.dur_sec
					warp_point_obj.speed = self.calc_tempo_size
				else:
					pos_real = sampleref_obj.dur_sec*self.calc_real_size
	
					pitch = pow(2, -pitch/12)

					warp_point_obj = warp_obj.add_warp_point()
					warp_point_obj.beat = 0
					warp_point_obj.second = 0
	
					warp_point_obj = warp_obj.add_warp_point()
					warp_point_obj.beat = pos_real*2*self.calc_bpm_size*pitch
					warp_point_obj.second = sampleref_obj.dur_sec

				warp_obj.calc_warp_points()

			finalspeed = 1
			if self.is_warped and target == 'rate':
				warp_obj = stretch_obj.warp
				warplen = len(warp_obj.points)-1
				firstwarp = warp_obj.points[0]
				fw_p = firstwarp.beat
				fw_s = firstwarp.second

				if len(warp_obj.points)>1:
					for wn, warpd in enumerate(warp_obj.points):
						pos = warpd.beat
						pos_real = warpd.second/4
						pos -= fw_p
						pos_real -= fw_s
						timecalc = (pos_real*8)
						speedchange = (pos/timecalc if timecalc else 1)
						finalspeed = speedchange
				else:
					finalspeed = warp_obj.points[0].speed

				self.set_rate_tempo(tempo, finalspeed, True)

				pos_offset = fw_p*4
				cut_offset = (fw_s*8)

		return pos_offset, cut_offset*finalspeed, finalspeed

	def debugtxt(self):
		print('- main')
		print('uses tempo:', self.uses_tempo)
		print('bpm:', self.bpm)
		print('speed:', self.org_speed)
		print('- bpm calc')
		print('speed:', self.calc_bpm_speed)
		print('size:', self.calc_bpm_size)
		print('- with tempo')
		print('speed:', self.calc_tempo_speed)
		print('size:', self.calc_tempo_size)
		print('- no tempo')
		print('speed:', self.calc_real_speed)
		print('size:', self.calc_real_size)