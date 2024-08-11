# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class cvpj_warp_point:
	def __init__(self):
		self.beat = 0
		self.second = 0
		self.speed = None

class cvpj_stretch:
	def __init__(self):
		self.algorithm = 'stretch'
		self.algorithm_mode = None
		self.preserve_pitch = False
		self.params = {}
		self.is_warped = False
		self.warppoints = []

		self.uses_tempo = False

		self.bpm = 120
		self.org_speed = 1
		self.calc_bpm_speed = 1
		self.calc_bpm_size = 1
		self.calc_tempo_speed = 1
		self.calc_tempo_size = 1
		self.calc_real_speed = 1
		self.calc_real_size = 1

	def add_warp_point(self):
		warp_point_obj = cvpj_warp_point()
		self.warppoints.append(warp_point_obj)
		return warp_point_obj

	def rem_last_warp_point(self):
		self.warppoints = self.warppoints[0:-1]

	def iter_warp_points(self):
		for x in self.warppoints:
			yield x

	def calc_warp_points(self):
		if self.warppoints:
			numpoints = len(self.warppoints)-1
			for n, warp_point_obj in enumerate(self.warppoints):
				if n<numpoints:
					next_warp = self.warppoints[n+1]
					calc_beat = next_warp.beat - warp_point_obj.beat
					calc_second = next_warp.second - warp_point_obj.second
					calctempo = (calc_beat/2)/calc_second
					warp_point_obj.speed = calctempo

			if numpoints>2:
				self.warppoints[-1].speed = self.warppoints[-2].speed

			#for warp_point_obj in self.warppoints:
			#	print(warp_point_obj.beat, warp_point_obj.second, warp_point_obj.speed*120)

	def __eq__(self, x):
		s_algorithm = self.algorithm == x.algorithm
		s_params = self.params == x.params
		s_is_warped = self.is_warped == x.is_warped
		s_warp = self.warppoints == x.warppoints
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

	def changestretch(self, samplereflist, sampleref, target, tempo, ppq):
		iffound = sampleref in samplereflist
		#print(iffound, sampleref, target, tempomul, self.method, self.rate, self.warp, self.algorithm)
		pos_offset = 0
		cut_offset = 0

		finalspeed = 1

		if iffound:
			sampleref_obj = samplereflist[sampleref]

			if not self.is_warped and target == 'warp':
				pos_real = sampleref_obj.dur_sec*self.calc_tempo_speed
				self.warppoints = []

				warp_point_obj = self.add_warp_point()
				warp_point_obj.beat = 0
				warp_point_obj.second = 0

				warp_point_obj = self.add_warp_point()
				warp_point_obj.beat = pos_real
				warp_point_obj.second = sampleref_obj.dur_sec

			finalspeed = 1
			if self.is_warped and target == 'rate':
				warplen = len(self.warppoints)-1
				firstwarp = self.warppoints[0]
				fw_p = firstwarp.beat
				fw_s = firstwarp.second

				if len(self.warppoints)>1:
					for wn, warpd in enumerate(self.warppoints):
						pos = warpd.beat
						pos_real = warpd.second/4
						pos -= fw_p
						pos_real -= fw_s
						timecalc = (pos_real*8)
						speedchange = (pos/timecalc if timecalc else 1)
						finalspeed = speedchange
				else:
					finalspeed = self.warppoints[0].speed

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