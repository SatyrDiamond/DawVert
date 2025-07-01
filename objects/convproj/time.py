# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from fractions import Fraction
import math
from objects import tempocalc
from functions import xtramath

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

	def json__make(self):
		outjson = {}
		outjson['type'] = self.type
		outjson['org_bpm'] = self.org_bpm
		outjson['speed_seconds'] = self.speed_seconds
		outjson['speed_steps'] = self.speed_steps
		outjson['from_bpm'] = self.from_bpm
		if self.frozen: outjson['frozen'] = self.frozen
		if self.keytrack_transpose: outjson['keytrack_transpose'] = self.keytrack_transpose
		if self.keytrack_tune: outjson['keytrack_tune'] = self.keytrack_tune
		return outjson

	@classmethod
	def json__parse(cls, injson):
		cls = cls()
		if 'type' in injson: cls.type = injson['type']
		if 'org_bpm' in injson: cls.org_bpm = injson['org_bpm']
		if 'speed_seconds' in injson: cls.speed_seconds = injson['speed_seconds']
		if 'speed_steps' in injson: cls.speed_steps = injson['speed_steps']
		if 'from_bpm' in injson: cls.from_bpm = injson['from_bpm']
		if 'frozen' in injson: cls.frozen = injson['frozen']
		if 'keytrack_transpose' in injson: cls.keytrack_transpose = injson['keytrack_transpose']
		if 'keytrack_tune' in injson: cls.keytrack_tune = injson['keytrack_tune']
		return cls

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

class time_duration:
	__slots__ = ['value','timemode']
	def __repr__(self):
		shorttime = '...'
		if self.timemode == 'seconds': shorttime = 'sec'
		if self.timemode == 'ppq': shorttime = 'ppq'
		return '[%s, %s]' % (str(round(self.value, 5)).rjust(8)[0:8], shorttime)

	def __init__(self):
		self.value = 0
		self.timemode = 'ppq'

	def calc_add(self, timemode, val, ppq, src_tempo):
		org_timemode = self.timemode
		self.convert(timemode, ppq, src_tempo)
		self.value += val
		self.convert(org_timemode, ppq, src_tempo)

	def calc_mul(self, timemode, val, ppq, src_tempo):
		org_timemode = self.timemode
		self.convert(timemode, ppq, src_tempo)
		self.value *= val
		self.convert(org_timemode, ppq, src_tempo)

	def change_ppq(self, old_ppq, new_ppq):
		if self.timemode == 'ppq':
			self.value = xtramath.change_timing(old_ppq, new_ppq, self.value)

	def get(self, timemode, ppq, src_tempo):
		if self.timemode == 'ppq':
			if timemode == 'beats': return self.value/ppq
			elif timemode == 'ppq': return self.value
			elif timemode == 'seconds': return xtramath.step2sec((self.value/ppq)*4, src_tempo)
			elif timemode == 'seconds_playback': 
				return xtramath.step2sec((self.value/ppq)*4, (120/src_tempo)*120)

		elif self.timemode == 'beats':
			if timemode == 'beats': return self.value
			elif timemode == 'ppq': return self.value*ppq
			elif timemode == 'seconds': return xtramath.step2sec(self.value*4, src_tempo)
			elif timemode == 'seconds_playback': 
				return xtramath.step2sec(self.value*4, (120/src_tempo)*120)

		elif self.timemode == 'seconds':
			if timemode == 'seconds': return self.value
			elif timemode == 'beats': return xtramath.sec2step(self.value, src_tempo)/4
			elif timemode == 'ppq': return (xtramath.sec2step(self.value, src_tempo)/4)*ppq

		elif self.timemode == 'seconds_playback':
			if timemode == 'seconds_playback': return self.value
			elif timemode == 'beats':
				return xtramath.sec2step(self.value, (120/src_tempo)*120)/4
			elif timemode == 'ppq':
				return (xtramath.sec2step(self.value, (120/src_tempo)*120)/4)*ppq

	def convert(self, timemode, ppq, src_tempo):
		#print(self.timemode, self.value, end=' > ')
		self.value = self.get(timemode, ppq, src_tempo)
		self.timemode = timemode
		#print(self.timemode, self.value)

	def set(self, value, timemode):
		self.value = value
		self.timemode = timemode

class time_position:
	__slots__ = ['value','timemode','timeid']
	def __repr__(self):
		shorttime = '...'
		if self.timemode == 'seconds': shorttime = 'sec'
		if self.timemode == 'ppq': shorttime = 'ppq'
		return '[%s, %s]' % (str(round(self.value, 5)).rjust(8)[0:8], shorttime)

	def __init__(self):
		self.value = 0
		self.timemode = 'ppq'
		self.timeid = 'global'

	def set(self, value, timemode):
		self.value = value
		self.timemode = timemode

	def change_ppq(self, old_ppq, new_ppq):
		if self.timemode == 'ppq':
			self.value = xtramath.change_timing(old_ppq, new_ppq, self.value)

	def get_timed(self):
		if self.timeid in tempocalc.global_stores:
			return tempocalc.global_stores[self.timeid]
		else:
			print('id not found in tempocalc_store')
			exit()

	def convert(self, timemode, ppq):
		self.value = self.get(timemode, ppq)
		self.timemode = timemode

	def calc_add(self, timemode, val, ppq, src_tempo):
		org_timemode = self.timemode
		self.convert(timemode, ppq)
		self.value += val
		self.convert(org_timemode, ppq)

	def get_tempo(self, ppq):
		if self.timemode == 'ppq': return self.get_timed().get_tempo(self.value/ppq, False)
		elif self.timemode == 'beats': return self.get_timed().get_tempo(self.value, False)
		elif self.timemode == 'seconds': return self.get_timed().get_tempo(self.value, True)

	def get(self, timemode, ppq):
		if self.timemode == 'ppq':
			if timemode == 'beats': return self.value/ppq
			elif timemode == 'ppq': return self.value
			elif timemode == 'seconds': return self.get_timed().get_pos(self.value/ppq, True)

		elif self.timemode == 'beats':
			if timemode == 'beats': return self.value
			elif timemode == 'ppq': return self.value*ppq
			elif timemode == 'seconds': return self.get_timed().get_pos(self.value, True)

		elif self.timemode == 'seconds':
			if timemode == 'seconds': return self.value
			elif timemode == 'beats': return self.get_timed().get_pos(self.value, False)
			elif timemode == 'ppq': return self.get_timed().get_pos(self.value, False)*ppq