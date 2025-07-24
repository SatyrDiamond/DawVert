# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from fractions import Fraction
import math
from objects import tempocalc
from functions import xtramath
from dataclasses import dataclass
from dataclasses import field
from contextlib import contextmanager
import bisect

def pos_get_tempo(timeid, pos, is_seconds):
	if timeid in tempocalc.global_stores:
		return float(tempocalc.global_stores[timeid].get_tempo(pos, is_seconds))
	else:
		raise ValueError('id "%s" not found in tempocalc_store' % str(timeid))

def pos_get_pos(timeid, pos, is_seconds):
	if timeid in tempocalc.global_stores:
		return float(tempocalc.global_stores[timeid].get_pos(pos, is_seconds))
	else:
		raise ValueError('id "%s" not found in tempocalc_store' % str(timeid))

# --------------------------------------------- PLACEMENTS ---------------------------------------------

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
		if type(value) not in [float, int]:
			raise ValueError('time_duration: numeric only')
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
		if type(value) not in [float, int]:
			raise ValueError('time_position: numeric only')
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
		if self.timemode == 'ppq': return pos_get_tempo(self.timeid, self.value/ppq, False)
		elif self.timemode == 'beats': return pos_get_tempo(self.timeid, self.value, False)
		elif self.timemode == 'seconds': return pos_get_tempo(self.timeid, self.value, True)

	def get(self, timemode, ppq):
		if self.timemode == 'ppq':
			if timemode == 'beats': return self.value/ppq
			elif timemode == 'ppq': return self.value
			elif timemode == 'seconds': return pos_get_pos(self.timeid, self.value/ppq, True)

		elif self.timemode == 'beats':
			if timemode == 'beats': return self.value
			elif timemode == 'ppq': return self.value*ppq
			elif timemode == 'seconds': return pos_get_pos(self.timeid, self.value, True)

		elif self.timemode == 'seconds':
			if timemode == 'seconds': return self.value
			elif timemode == 'beats': return pos_get_pos(self.timeid, self.value, False)
			elif timemode == 'ppq': return pos_get_pos(self.timeid, self.value, False)*ppq

# --------------------------------------------- CONTENT ---------------------------------------------

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

	def points__add_beatsec(self, beat, second):
		warp_point_obj = cvpj_warp_point()
		warp_point_obj.beat = beat
		warp_point_obj.second = second
		self.points.append(warp_point_obj)
		return warp_point_obj

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
			for d in [x.beat, x.second*x.speed*2 if x.speed else '!!!', x.second, x.speed]:
				print(str(d).ljust(25), end=' ')
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

	def fix__alwaysplus(self):
		self.points = [x for x in self.points if round(x.beat, 7)>=0 and round(x.second, 7)>=0]

	def fix__last(self):
		seconds = [x.second>=self.seconds for x in self.points]
		if True not in seconds: self.points__add__based_second(self.seconds)

	def fix__onlyone(self):
		if len(self.points) == 1:
			self.points__add__based_beat(0)
			self.points__add__based_second(self.seconds)

	def fix__fill(self):
		if self.points:
			self.points__add__based_second(0)
			self.points__add__based_beat(0)
			#self.points__add__based_second(self.seconds)

	def fix__round(self):
		for point in self.points:
			point.beat = round(point.beat, 7)
			point.second = round(point.second, 7)

	def fix__remove_dupe_sec(self):
		warppoints = {}
		for point in self.points: 
			if point.second not in warppoints: warppoints[point.second] = point
			elif point.speed is not None: 
				warppoints[point.second].speed = point.speed
		self.points = list(warppoints.values())

	def fixpl__offset(self, pltime_obj, ppq):
		offset = self.get__offset()
		cut_start = pltime_obj.get_offset()
		cus = -(offset+cut_start)
		actmove = max(0, cus)

		warpmove = max(0, offset)

		if pltime_obj.cut_type in ['none', 'cut']:
			pltime_obj.cut_type = 'cut'
			pltime_obj.calc_pos_add((actmove)*ppq)
			pltime_obj.calc_dur_add(-(actmove)*ppq)
			pltime_obj.calc_offset_add((actmove)*ppq)

			self.manp__shift_beats(warpmove)
			pltime_obj.calc_offset_add((warpmove)*ppq)

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

	#def fix__fill_last(self):
	#	if self.points:
	#		offset = self.get__offset()
	#		if True not in [x.second>=self.seconds for x in self.points]:
	#			off_sec = (offset/2)/self.speed
	#			warp_point_obj = self.points__add()
	#			warp_point_obj.beat = ((self.seconds*2)*self.speed)-offset
	#			warp_point_obj.second = self.seconds
	#			warp_point_obj.speed = self.speed

	#def fix__fill_first(self):
	#	if self.points:
	#		offset = self.get__offset()
	#		if -offset not in [x.beat for x in self.points]:
	#			warp_point_obj = self.points__add()
	#			warp_point_obj.beat = -offset
	#			warp_point_obj.speed = self.speed

	def fix__sort(self):
		self.points = sorted(self.points, key=lambda x: x.beat)

@dataclass
class time_content:
	time_type: str = 'speed'
	original_bpm: float = 0
	tempo_based: bool = False
	warp: cvpj_stretch_warp = field(default_factory=cvpj_stretch_warp)

	beats__num: float = 0
	speed__rate: float = 1

	def set__speed(self, speed):
		self.time_type = 'speed'
		self.speed__rate = speed
		self.tempo_based = False

	def set__orgtempo(self, org_tempo):
		self.time_type = 'tempo'
		self.original_bpm = org_tempo
		self.tempo_based = True

	def set__rate(self, rate):
		self.time_type = 'tempo'
		self.original_bpm = rate*120
		self.tempo_based = True

	def set__size(self, rate):
		self.time_type = 'tempo'
		self.original_bpm = 120/rate
		self.tempo_based = True

	def set__real_rate(self, tempo, rate):
		self.time_type = 'real_rate'
		self.original_bpm = tempo
		self.speed__rate = rate
		self.tempo_based = True

	def set__beats(self, num_beats):
		self.time_type = 'beats'
		self.beats__num = num_beats
		self.tempo_based = True

	def set__warp(self):
		self.time_type = 'warp'
		self.tempo_based = True

	@contextmanager
	def setup_warp(self, procspeed):
		self.set__warp()
		try:
			yield self.warp
		finally:
			if procspeed:
				self.warp.calcpoints__speed()
			self.warp.post__speed()

	def get__speed(self, sampleref_obj):
		if self.time_type == 'beats':
			if sampleref_obj:
				dur_sec = sampleref_obj.get_dur_sec()
				if dur_sec:
					outval = ( self.beats__num/(dur_sec*2) )
					return outval
			return 1

		if self.time_type == 'tempo':
			return (self.original_bpm/120)

		if self.time_type == 'real_rate':
			return (self.original_bpm/120)/self.speed__rate

		if self.time_type == 'speed':
			return self.speed__rate
 
		if self.time_type == 'warp':
			return 1

	def get__speed_real(self, sampleref_obj, tempo):
		tempom = tempo/120 if not self.tempo_based else 1
		return self.get__speed(sampleref_obj)*tempom

	def get__tempo(self, sampleref_obj):
		return self.get__speed(sampleref_obj)*120

	def get__real_rate(self, sampleref_obj, tempo):
		if self.time_type == 'real_rate':
			return self.speed__rate

		if self.time_type == 'speed':
			return 1/self.speed__rate

		tempom = tempo/120
		if self.time_type == 'beats':
			outrate = 1
			if sampleref_obj:
				dur_sec = sampleref_obj.get_dur_sec()
				if dur_sec:
					outval = ( self.beats__num/(dur_sec*2) )
					outrate = (1/outval)
			return outrate*tempom

		if self.time_type == 'tempo':
			sized = 120/self.original_bpm
			return sized*tempom
		return 1

	def get__beats(self, sampleref_obj):
		if self.time_type == 'beats':
			return self.beats__num
		if self.time_type == 'tempo':
			sized = 120/self.original_bpm
			if sampleref_obj:
				dur_sec = sampleref_obj.get_dur_sec()
				if dur_sec: return (dur_sec*2)/sized
			return 1
		if self.time_type == 'real_rate':
			sized = 120/self.original_bpm
			if sampleref_obj:
				dur_sec = sampleref_obj.get_dur_sec()
				if dur_sec: return (dur_sec*2)/(self.speed__rate*sized)
			return 1

	def changestretch_rate2warp(self, pl_timemul, sampleref_obj, tempo, pitch):
		dur_sec = sampleref_obj.get_dur_sec()

		muloffset = 1

		if self.tempo_based:
			calc_tempo_size = self.get__speed(sampleref_obj)
			pos_real = sampleref_obj.dur_sec*calc_tempo_size
		
			with self.setup_warp(False) as warp_obj:
				warp_point_obj = warp_obj.points__add()
				warp_point_obj.speed = 1/calc_tempo_size
		
				warp_point_obj = warp_obj.points__add()
				warp_point_obj.beat = pos_real*2
				warp_point_obj.second = sampleref_obj.dur_sec
				warp_point_obj.speed = 1/calc_tempo_size
		else:
			calc_speed_size = self.get__speed(sampleref_obj)
			calc_bpm_size = (tempo/120)
			pos_real = sampleref_obj.dur_sec*calc_speed_size*calc_bpm_size
		
			if self.time_type == 'speed':
				pl_timemul.cut_mul = calc_speed_size

			with self.setup_warp(True) as warp_obj:
				warp_point_obj = warp_obj.points__add()
		
				warp_point_obj = warp_obj.points__add()
				warp_point_obj.beat = pos_real*2
				warp_point_obj.second = sampleref_obj.dur_sec

			muloffset = calc_speed_size

		warp_obj.calcpoints__speed()

	def changestretch_warp2rate(self, pl_timemul):
		finalspeed = 1

		warp_obj = self.warp

		warplen = len(warp_obj.points)-1
		firstwarp = warp_obj.points[0]
		fw_p = firstwarp.beat
		fw_s = firstwarp.second

		warp_obj.calcpoints__speed()
		warp_obj.post__speed()

		offs = warp_obj.get__offset()*4

		pl_timemul.cut_offset = max(offs, 0)
		#pl_timemul.pos_offset = -min(offs, 0)

		#if len(warp_obj.points)>1:
		#	for wn, warpd in enumerate(warp_obj.points):
		#		pos = warpd.beat
		#		pos_real = warpd.second/4
		#		pos -= fw_p
		#		pos_real -= fw_s
		#		timecalc = (pos_real*8)
		#		speedchange = (pos/timecalc if timecalc else 1)
		#		finalspeed = speedchange
		#else:
		#	finalspeed = warp_obj.points[0].speed

		if finalspeed>0:
			self.set__rate(warp_obj.speed)

		#pl_timemul.pos_offset = fw_p*4
		#pl_timemul.cut_offset = (fw_s*8)



# --------------------------------------------- PLUGINS ---------------------------------------------

outletters = ['','d','t']

class time_lfo:
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
