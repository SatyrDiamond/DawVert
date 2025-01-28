# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from dataclasses import field
from functions import xtramath
from contextlib import contextmanager
import bisect

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

	def beat_from_sec(self, speed):
		return (self.second*2)*speed

	def sec_from_beat(self, speed):
		return (self.beat/2)/speed


@dataclass
class cvpj_stretch_warp:
	points: list = field(default_factory=list)
	seconds: float = -1
	speed: float = 1
	bpm: float = 120

	def internal__set_speed(self, speed):
		self.speed = speed
		self.bpm = round(self.speed*120, 8)

	def points__add(self):
		warp_point_obj = cvpj_warp_point()
		self.points.append(warp_point_obj)
		return warp_point_obj

	def points__add_start(self):
		warp_point_obj = cvpj_warp_point()
		self.points.insert(0, warp_point_obj)
		return warp_point_obj

	def points__del_last(self):
		self.points = self.points[0:-1]

	def points__iter(self):
		for x in self.points: yield x

	def debugtxt_warp(self):
		print('------------- warps')
		for x in self.points__iter():
			print('warp', end=' ')
			for d in [x.beat, x.second*x.speed*2, x.second, x.speed]:
				print(str(d).ljust(20), end=' ')
			print('')

	def calcpoints__speed(self):
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

	def post__speed(self):
		if self.points:
			speedpoints = [x.speed for x in self.points]
			if None not in speedpoints: self.internal__set_speed(xtramath.average(speedpoints))

	def manp__tempo_set(self, tempo):
		self.manp__speed_set(tempo/120)

	def manp__speed_set(self, speed):
		self.manp__speed_mul(speed/self.speed)

	def manp__speed_mul(self, speed):
		for warp_point_obj in self.points: 
			warp_point_obj.beat *= speed
			warp_point_obj.speed *= speed
		self.internal__set_speed(self.speed*speed)

	def manp__shift_beats(self, pos):
		for warp_point_obj in self.points: warp_point_obj.beat += pos

	def manp__shift_sec(self, pos):
		for warp_point_obj in self.points: warp_point_obj.second -= pos

	def manp__shift_secbeat(self, pos):
		for warp_point_obj in self.points: warp_point_obj.second -= pos*self.speed

	def manp__shift_points(self, pos):
		for warp_point_obj in self.points: 
			warp_point_obj.beat += pos
			warp_point_obj.second += pos*self.speed

	def get__first_sec(self):
		if self.points:
			return self.points[0].second
		else:
			return 0

	def get__first_beat(self):
		if self.points:
			firstpoint = self.points[0]
			return firstpoint.second*firstpoint.speed*2
		else:
			return 0

	def get__dur_sec(self):
		if self.points:
			lastpoint = self.points[-1]
			firstpoint = self.points[0]
			return lastpoint.second-((firstpoint.beat/firstpoint.speed)/2)
		else:
			return 0

	def get__dur_beat(self):
		if self.points:
			lastpoint = self.points[-1]
			firstpoint = self.points[0]
			return (lastpoint.second*firstpoint.speed*2)-firstpoint.beat
		else:
			return 0

	def get__offset(self):
		if self.points:
			firstpoint = self.points[0]
			dest_sec = firstpoint.second*firstpoint.speed*2
			outval = dest_sec-firstpoint.beat
			return outval
		return 0

	def fix__offset_before(self):
		offset = self.get__offset()
		offset = min(offset, 0)
		self.manp__shift_secbeat(offset)
		return offset

	def points__add__based_beat(self, inbeat):
		if self.points:
			numpoints = len(self.points)-1
			beats = [x.beat for x in self.points]
			seconds = [x.second for x in self.points]

			vright = bisect.bisect_right(beats, inbeat)
			vleft = vright-1
			is_ob = -int(vleft<0) + int(vright>numpoints)

			if inbeat not in beats:
				if is_ob == 0:
					outval = xtramath.between_to_one(beats[vleft], beats[vright], inbeat)
					warp_point_obj = cvpj_warp_point()
					warp_point_obj.second = xtramath.between_from_one(seconds[vleft], seconds[vright], outval)
					warp_point_obj.beat = inbeat
					self.points.insert(vright, warp_point_obj)
				if is_ob == -1:
					warp_point_obj = cvpj_warp_point()
					warp_point_obj.speed = self.speed
					warp_point_obj.beat = inbeat
					totalbeat = inbeat-beats[0]
					warp_point_obj.second = seconds[0]+((totalbeat/self.speed)/2)
					self.points.insert(0, warp_point_obj)
				if is_ob == 1:
					totalbeat = inbeat-beats[-1]
					warp_point_obj = cvpj_warp_point()
					warp_point_obj.speed = self.points[-1].speed
					warp_point_obj.beat = inbeat
					warp_point_obj.second = seconds[-1]+((totalbeat/self.speed)/2)
					self.points.append(warp_point_obj)

	def points__add__based_second(self, insec):
		if self.points:
			numpoints = len(self.points)-1
			beats = [x.beat for x in self.points]
			seconds = [x.second for x in self.points]

			vright = bisect.bisect_right(seconds, insec)
			vleft = vright-1
			is_ob = -int(vleft<0) + int(vright>numpoints)

			if insec not in seconds:
				if is_ob == 0:
					outval = xtramath.between_to_one(seconds[vleft], seconds[vright], insec)
					warp_point_obj = cvpj_warp_point()
					warp_point_obj.second = insec
					warp_point_obj.beat = xtramath.between_from_one(beats[vleft], beats[vright], outval)
					self.points.insert(vright, warp_point_obj)
				if is_ob == -1:
					warp_point_obj = cvpj_warp_point()
					warp_point_obj.speed = self.speed
					warp_point_obj.second = insec
					totalsec = insec+seconds[0]
					warp_point_obj.beat = beats[0]-((totalsec*self.speed)*2)
					self.points.insert(0, warp_point_obj)
				if is_ob == 1:
					offset = self.get__offset()
					totalsec = -(seconds[-1]-insec)
					warp_point_obj = cvpj_warp_point()
					warp_point_obj.speed = self.points[-1].speed
					warp_point_obj.second = insec
					warp_point_obj.beat = beats[-1]+((totalsec*self.speed)*2)
					self.points.append(warp_point_obj)

	def fix__fill(self):
		if self.points:
			self.points__add__based_second(0)
			self.points__add__based_beat(0)
			self.points__add__based_second(self.seconds)

	def fix__round(self):
		for point in self.points:
			point.beat = round(point.beat, 7)
			point.second = round(point.second, 7)

	def fix__remove_dupe_sec(self):
		warppoints = {}
		for point in self.points: warppoints[point.second] = point
		self.points = list(warppoints.values())

	def fixpl__offset(self, pltime_obj, ppq):
		offset = self.get__offset()
		cut_start = pltime_obj.cut_start/ppq
		cus = -(offset+cut_start)
		actmove = max(0, cus)

		warpmove = max(0, offset)

		if pltime_obj.cut_type in ['none', 'cut']:
			pltime_obj.cut_type = 'cut'
			pltime_obj.position += (actmove)*ppq
			pltime_obj.duration += -(actmove)*ppq
			pltime_obj.cut_start += (actmove)*ppq

			self.manp__shift_beats(warpmove)
			pltime_obj.cut_start += (warpmove)*ppq

		#if offset != 0:
		#	if pltime_obj.cut_type == 'none':
		#		pltime_obj.position += -(offset)*ppq
		#		pltime_obj.duration += (offset)*ppq
		#	if pltime_obj.cut_type == 'cut':
		#		cut_start = pltime_obj.cut_start/ppq
		#		mincut = max(cut_start, 0)
		#		pltime_obj.cut_start -= mincut*ppq
		#		total = offset+mincut
		#		pltime_obj.position += -(total)*ppq
		#		pltime_obj.duration += (total)*ppq

	def fix__fill_last(self):
		if self.points:
			offset = self.get__offset()
			if True not in [x.second>=self.seconds for x in self.points]:
				off_sec = (offset/2)/self.speed
				warp_point_obj = self.points__add()
				warp_point_obj.beat = ((self.seconds*2)*self.speed)-offset
				warp_point_obj.second = self.seconds
				warp_point_obj.speed = self.speed

	def fix__fill_first(self):
		if self.points:
			offset = self.get__offset()
			if -offset not in [x.beat for x in self.points]:
				warp_point_obj = self.points__add()
				warp_point_obj.beat = -offset
				warp_point_obj.speed = self.speed

	def fix__sort(self):
		self.points = sorted(self.points, key=lambda x: x.beat)

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

	@contextmanager
	def setup_warp(self):
		try:
			yield self.warp
		finally:
			self.warp.calcpoints__speed()
			self.warp.post__speed()

	def changestretch(self, samplereflist, sampleref, target, tempo, ppq, pitch):
		iffound = sampleref in samplereflist
		pos_offset = 0
		cut_offset = 0

		finalspeed = 1

		warp_obj = self.warp

		if iffound:
			sampleref_obj = samplereflist[sampleref]

			if not self.is_warped and target == 'warp':
				self.is_warped = True
				warp_obj.points = []

				if self.uses_tempo:
					pos_real = sampleref_obj.dur_sec*self.calc_tempo_size
	
					warp_point_obj = warp_obj.points__add()
					warp_point_obj.beat = 0
					warp_point_obj.second = 0
					warp_point_obj.speed = self.calc_tempo_size
	
					warp_point_obj = warp_obj.points__add()
					warp_point_obj.beat = pos_real*2
					warp_point_obj.second = sampleref_obj.dur_sec
					warp_point_obj.speed = self.calc_tempo_size
				else:
					pos_real = sampleref_obj.dur_sec*self.calc_real_size
	
					pitch = pow(2, -pitch/12)

					warp_point_obj = warp_obj.points__add()
					warp_point_obj.beat = 0
					warp_point_obj.second = 0
	
					warp_point_obj = warp_obj.points__add()
					warp_point_obj.beat = pos_real*2*self.calc_bpm_size*pitch
					warp_point_obj.second = sampleref_obj.dur_sec

				warp_obj.calcpoints__speed()

			finalspeed = 1
			if self.is_warped and target == 'rate':
				warp_obj = self.warp
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