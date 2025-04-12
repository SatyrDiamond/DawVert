# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from fractions import Fraction
from functions import xtramath
import math

class cvpj_time_size:
	def __init__(self, time_ppq, time_float):
		self.ticks = None
		self.seconds = None
		self.bpm = 0

		self.time_ppq = time_ppq
		self.time_float = time_float

	def __float__(self):
		if self.ticks==None: self.tick_from_second()
		return self.ticks if self.ticks else 0.0

	def __imul__(self, i):
		if self.ticks==None: self.tick_from_second()
		if self.ticks!=None: self.ticks *= i
		self.second_from_tick()
		return self

	def __isub__(self, i):
		if self.ticks==None: self.tick_from_second()
		if self.ticks!=None: self.ticks -= i
		self.second_from_tick()
		return self

	def __iadd__(self, i):
		if self.ticks==None: self.tick_from_second()
		if self.ticks!=None: self.ticks += i
		self.second_from_tick()
		return self

	def second_from_tick(self):
		if self.ticks is not None and self.bpm:
			self.seconds = (self.ticks/(ppq/4))*(tempo/120)*2

	def tick_from_second(self):
		if self.seconds is not None and self.bpm:
			self.ticks = (self.seconds*(ppq/4))/(tempo/120)/2

	def set_tick(self, beats):
		self.ticks = beats
		if self.bpm: self.second_from_tick()

	def set_seconds(self, seconds):
		self.seconds = seconds
		if self.bpm: self.tick_from_second()

	def set_bpm(self, bpm):
		self.bpm = bpm
		if self.bpm: self.second_from_tick()

	def change_timing(self, new_ppq, is_float):
		if self.ticks is not None:
			self.ticks = xtramath.change_timing(self.time_ppq, new_ppq, is_float, self.ticks)

outletters = ['','d','t']

class cvpj_time:
	def __init__(self):
		self.type = 'seconds'
		self.org_bpm = 120
		self.speed_seconds = 1
		self.speed_steps = 8
		self.from_bpm = False
		self.frozen = False
		self.keytrack_transpose = 0
		self.keytrack_tune = 0

	def set_seconds(self, seconds):
		self.type = 'seconds'
		self.org_bpm = 120
		self.speed_seconds = seconds
		self.speed_steps = (seconds*8)
		self.from_bpm = False
		self.frozen = seconds==0

	def set_hz(self, hz):
		self.type = 'seconds'
		self.org_bpm = 120
		self.speed_seconds = 1/hz if hz != 0 else 1000
		self.speed_steps = (1/hz*8) if hz != 0 else 1000
		self.from_bpm = False
		self.frozen = hz==0

	def set_steps(self, steps, convproj_obj):
		bpm = convproj_obj.params.get('bpm', 120).value
		self.type = 'steps'
		self.org_bpm = bpm
		self.speed_seconds = (steps*(120/bpm))/8
		self.speed_steps = steps
		self.from_bpm = True
		self.frozen = steps==0

	def set_steps_nonsync(self, steps, tempo):
		self.type = 'seconds'
		self.org_bpm = tempo
		self.speed_seconds = (steps/8)*tempo
		self.speed_steps = steps
		self.from_bpm = True
		self.frozen = steps==0

	def set_frac(self, num, denum, letter, convproj_obj):
		calc_val = (num/denum if denum else 1)*16
		if letter == 'd': calc_val /= 4/3
		if letter == 't': calc_val *= 11/8
		self.set_steps(calc_val, convproj_obj)
		self.frozen = denum==0

	def set_frac_nonsync(self, num, denum, letter, tempo):
		calc_val = (num/(denum if denum else 1))*16
		if letter == 'd': calc_val /= 4/3
		if letter == 't': calc_val *= 11/8
		self.set_steps_nonsync(calc_val, tempo)
		self.frozen = denum==0

	def set_keytrack(self, transpose, tune):
		self.type = 'keytrack'
		self.keytrack_transpose = transpose
		self.keytrack_tune = tune
		self.set_seconds(1)

	def get_frac(self):
		if self.type == 'steps':
			frac = Fraction(self.speed_steps/4).limit_denominator()
			return frac.numerator, frac.denominator
		else:
			return self.speed_seconds, 1

	def get_step_offset(self, validsteps):
		lognum = math.log2(self.speed_steps)
		stepslog = [math.log2(x) for x in validsteps]
		minval = [abs(x-lognum) for x in stepslog]
		minidx = minval.index(min(minval))
		basestep = validsteps[minidx]
		return minidx, math.log2(self.speed_steps/basestep)

	def get_frac_letter_mul(self):
		lognum = math.log2(self.speed_steps)
		lognum_d = math.log2(self.speed_steps*(4/3))
		lognum_t = math.log2(self.speed_steps/(11/8))

		m_lognum = abs(round(lognum)-(lognum))
		m_lognum_d = abs(round(lognum_d)-(lognum_d))
		m_lognum_t = abs(round(lognum_t)-(lognum_t))

		logv = [m_lognum, m_lognum_d, m_lognum_t]
		minidx = logv.index(min(logv))

		outvals = [2**lognum, 2**lognum_d, 2**lognum_t]

		oidx = round(math.log2(outvals[minidx])-4)

		numerator = max(1, 2**(-oidx))
		denominator = max(1, 2**(oidx))

		return numerator, denominator, outletters[minidx]