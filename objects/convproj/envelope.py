# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from functions import data_values
from objects.valobjs import dualstr

VERBOSE = False

def __init__(self):
	self.reset()

def get_updown(indata):
	outvals = []
	for x in indata:
		if x>0: outvals.append(1)
		elif x<0: outvals.append(-1)
		else: outvals.append(0)
	return outvals

def tension_detect(env_pointsdata, start, end):
	t_pos = env_pointsdata['pos']
	t_val = env_pointsdata['value']
	numpoints = len(t_pos)

	if end:
		t_pos = t_pos[:end]
		t_val = t_val[:end]
		numpoints = end

	if start:
		t_pos = t_pos[start:]
		t_val = t_val[start:]
		numpoints -= start

	p_min = min(t_val)
	p_max = max(t_val)
	t_val = [xtramath.between_to_one(p_min, p_max, x) for x in t_val]

	t_pos_chan = data_values.list__dif_val(t_pos, None)
	t_val_chan = data_values.list__dif_val(t_val, None)

	t_val_chan_a = [abs(x) for x in t_val_chan]
	t_val_chan_d = get_updown(t_val_chan_a)

	pcv = 1/(numpoints-1)
	t_comb = [(t_val_chan_a[n]/pcv)/(v if v else 1) for n, v in enumerate(t_pos_chan)]
	t_comb_c = [(1/t_comb[n] if t_comb[n] != 0 else 1) for n, v in enumerate(t_comb)]
	t_comb_s = [1/(x+1) for x in range(numpoints-1)]
	t_comb_e = t_comb_s[::-1]
	t_comb_chan = [(t_val_chan[n]/(x if x else 1)) for n, x in enumerate(t_pos_chan)]

	maxcval = sum(t_comb_s)
	tens_start = 0
	tens_end = 0
	for x in range(numpoints-1):
		tens_start += t_comb_c[x]*t_comb_s[x]
		tens_end += t_comb_c[x]*t_comb_e[x]
	tens_start /= maxcval
	tens_end /= maxcval
	tension = (tens_start-1)+(1-tens_end)

	posneg = xtramath.average(t_val_chan_d)*1.3

	return tension


class cvpj_envelope_adsr:
	def __init__(self):
		self.reset()

	def reset(self):
		self.predelay = 0
		self.attack = 0
		self.hold = 0
		self.decay = 0
		self.sustain = 1
		self.release = 0
		self.amount = 0

		self.attack_tension = 0
		self.decay_tension = 0
		self.release_tension = 0

	def from_envpoints__internal_2point(self, sustainnum, a_type, plugin_obj, env_pointsdata):
		pointsdata = env_pointsdata.points
		point_start = pointsdata[0]
		point_end = pointsdata[1]

		env_duration = point_end.pos
		env_value = point_start.value - point_end.value
		maxval = max(point_start.value, point_end.value)
		minval = min(point_start.value, point_end.value)
		sustainp = sustainnum == 0
		use_fadeout = env_pointsdata.data['use_fadeout'] if 'use_fadeout' in env_pointsdata.data else 0
		fadeout = env_pointsdata.data['fadeout'] if 'fadeout' in env_pointsdata.data else True

		debug_num = 0
		if point_start.value != point_end.value:
			if env_pointsdata.loop_on and env_pointsdata.loop_start < env_pointsdata.loop_end:
				debug_num = 200
				self.release = fadeout
				self.amount = 1
				if plugin_obj:
					if VERBOSE: print("[env_asdr_from_points] 2 | LFO")
					lfo_obj = plugin_obj.lfo_add(a_type)
					lfo_obj.prop.shape = 'saw' if env_value>0 else 'saw_down'
					lfo_obj.time.set_seconds(env_duration)
					lfo_obj.amount = min(abs(env_value/1.3),1)
					lfo_obj.retrigger = True

			elif sustainp:
				self.release = env_duration
				if env_value < 0: 
					self.amount = -1
					debug_num = 201
			else:
				if env_value > 0:
					if VERBOSE: print("[env_asdr_from_points] 2 | ^_")
					self.decay = env_duration
					self.sustain = minval
					debug_num = 202
				else: 
					if VERBOSE: print("[env_asdr_from_points] 2 | _^")
					self.attack = env_duration
					debug_num = 203

		return debug_num

	def from_envpoints__internal_3point(self, sustainnum, plugin_obj, env_pointsdata):
		use_fadeout = env_pointsdata.data['use_fadeout'] if 'use_fadeout' in env_pointsdata.data else 0
		fadeout = env_pointsdata.data['fadeout'] if 'fadeout' in env_pointsdata.data else True

		pointsdata = env_pointsdata.points
		envp_middle = pointsdata[1].pos
		envp_end = pointsdata[2].pos
		envv_first = pointsdata[0].value
		envv_middle = pointsdata[1].value
		envv_end = pointsdata[2].value
		firstmid_s = envv_first-envv_middle
		midend_s = envv_end-envv_middle

		debug_num = 0

		#if VERBOSE: print(pointsdata[0].pos, pointsdata[0].value)
		#if VERBOSE: print(pointsdata[1].pos, pointsdata[1].value)
		#if VERBOSE: print(pointsdata[2].pos, pointsdata[2].value)
		#if VERBOSE: print(envp_middle, envp_end, '|', envv_first, envv_middle, envv_end)

		if firstmid_s > 0 and sustainnum == -1: a_sustain = 0

		if firstmid_s > 0 and midend_s == 0:
			if VERBOSE: print("[env_asdr_from_points] 3 | ^__" )
			if sustainnum == -1: self.decay = envp_middle
			if sustainnum == 0: self.release = envp_middle
			debug_num = 300

		elif firstmid_s > 0 and midend_s < 0:
			if VERBOSE: print("[env_asdr_from_points] 3 | ^._" )
			if sustainnum == -1: 
				self.decay = envp_end
				self.decay_tension = (envv_middle-(envv_first/2))*2
				self.sustain = 0
				if use_fadeout: self.release = fadeout
				debug_num = 301

			if sustainnum == 0: 
				self.release = envp_end
				self.release_tension = ((((envp_middle/envp_end)/2)+(envv_middle/2))-0.5)*2
				debug_num = 302

			if sustainnum == 1: 
				self.decay = envp_middle
				self.release = envp_end-envp_middle
				self.sustain = envv_middle
				debug_num = 303
   
		elif firstmid_s < 0 and midend_s < 0:
			if VERBOSE: print("[env_asdr_from_points] 3 | _^." )
			if sustainnum in [0, -1]: 
				self.attack = envp_middle
				self.decay = (envp_end-envp_middle)
				self.sustain = envv_end
				debug_num = 304
			if sustainnum == 1: 
				self.attack = envp_middle
				self.release = (envp_end-envp_middle)
				debug_num = 305

		elif firstmid_s == 0 and midend_s < 0:
			if VERBOSE: print("[env_asdr_from_points] 3 | ^^.")
			if sustainnum == -1:
				self.hold = envp_middle
				self.decay = envp_end-envp_middle
				self.sustain = envv_end
				debug_num = 306
			if sustainnum == 0: 
				self.hold = envp_middle
				self.release = envp_end-envp_middle
				debug_num = 307

		elif firstmid_s < 0 and midend_s > 0:
			if VERBOSE: print("[env_asdr_from_points] 3 | _.^")
			self.attack = envp_end
			self.attack_tension = ((envp_end-envp_middle)-1)
			debug_num = 308

		elif firstmid_s == 0 and midend_s > 0:
			if VERBOSE: print("[env_asdr_from_points] 3 | __^")
			self.predelay = envp_middle
			self.attack = envp_end-envp_middle
			debug_num = 309

		elif firstmid_s < 0 and midend_s == 0:
			if VERBOSE: print("[env_asdr_from_points] 3 | _^^")
			self.attack = envp_middle
			self.hold = envp_end-envp_middle
			debug_num = 310

		#elif firstmid_s > 0 and midend_s > 0:
		#	#print("[env_asdr_from_points] 3 | ^.^")
		#	if sustainnum in [None, 1]:
		#		self.attack = envp_middle
		#		a_decay = (envp_end-envp_middle)
		#		a_amount = envv_middle-1
		#	if sustainnum == 1: 
		#		self.attack = envp_middle
		#		self.release = (envp_end-envp_middle)
		#		a_amount = envv_middle-1
		#	debug_num = True

		if debug_num != 0 and self.sustain != 0 and self.release == 0: self.release = fadeout
		return debug_num

	def from_envpoints(self, env_pointsdata, a_type, plugin_obj):
		self.reset()
		
		use_fadeout = env_pointsdata.data['use_fadeout'] if 'use_fadeout' in env_pointsdata.data else 0
		fadeout = env_pointsdata.data['fadeout'] if 'fadeout' in env_pointsdata.data else True
		pointsdata = env_pointsdata.points
		numpoints = len(pointsdata)

		sustainnum = -1 if (not env_pointsdata.sustain_on or env_pointsdata.sustain_point > numpoints-1) else env_pointsdata.sustain_point
		debug_num = 0

		if numpoints == 2:
			debug_num = self.from_envpoints__internal_2point(sustainnum, a_type, plugin_obj, env_pointsdata)

		elif numpoints == 3:
			debug_num = self.from_envpoints__internal_3point(sustainnum, plugin_obj, env_pointsdata)

		elif numpoints == 4 and (
			(sustainnum in [-1, 2]) and 
			(pointsdata[0].value == 0) and 
			(pointsdata[3].value == 0) and 
			(pointsdata[1].value>=pointsdata[2].value)):
				if VERBOSE: print("[env_asdr_from_points] 4 | ADSR")
				self.attack = pointsdata[1].pos
				self.decay = pointsdata[2].pos-pointsdata[1].pos
				self.sustain = pointsdata[2].value
				self.release = pointsdata[3].pos-pointsdata[2].pos
				debug_num = 400

		elif numpoints > 3:

			if env_pointsdata['pos'][-1] != 0:

				if not env_pointsdata.loop_on:
					if sustainnum in [-1, 0]:
						lastpos = env_pointsdata['pos'][-1]
						t_dif = data_values.list__dif_val(env_pointsdata['value'], None)
						tension = tension_detect(env_pointsdata, None, None)
						if min(t_dif)<=0 and max(t_dif)<0:
							debug_num = 500
							if VERBOSE: print("[env_asdr_from_points] 5 | _.^._")
							if sustainnum == -1:
								self.decay = lastpos
								self.decay_tension = tension
								self.sustain = 0
							if sustainnum == 0:
								self.release = lastpos
								self.release_tension = tension
						if min(t_dif)>0 and max(t_dif)>=0:
							if VERBOSE: print("[env_asdr_from_points] 5 | _.^")
							debug_num = 501
							self.attack = lastpos
							self.attack_tension = tension

					else:
						firstpos = env_pointsdata['pos'][0]
						firstval = env_pointsdata['value'][0]

						midpos = env_pointsdata['pos'][sustainnum]
						midval = env_pointsdata['value'][sustainnum]

						lastpos = env_pointsdata['pos'][-1]
						lastval = env_pointsdata['value'][-1]

						dif_first = data_values.list__dif_val(env_pointsdata['value'][0:sustainnum+1], None)
						dif_last = data_values.list__dif_val(env_pointsdata['value'][sustainnum:numpoints], None)

						if not dif_first: dif_first = [0]
						if not dif_last: dif_last = [0]

						first_dif_higher = (min(dif_first)>=0 and max(dif_first)>=0)
						last_dif_lower = (min(dif_last)<=0 and max(dif_last)<0)

						if firstval<midval:
							if first_dif_higher:
								if VERBOSE: print("[env_asdr_from_points] 5 F| _.^")
								self.attack = midpos
								self.attack_tension = tension_detect(env_pointsdata, 0, sustainnum+1)
								debug_num = 502
						elif firstval>midval:
							if not first_dif_higher:
								if VERBOSE: print("[env_asdr_from_points] 5 F| ^._")
								self.decay = midpos
								self.decay_tension = tension_detect(env_pointsdata, 0, sustainnum+1)
								self.sustain = midval
								debug_num = 502


						if lastval<midval:
							if last_dif_lower:
								if VERBOSE: print("[env_asdr_from_points] 5 L| ^._")
								self.release = lastpos-midpos
								self.release_tension = tension_detect(env_pointsdata, sustainnum, numpoints)
								debug_num = 502
						#elif (

				#exit()

		#if VERBOSE: print(numpoints, a_type, sustainnum, debug_num)



class cvpj_envelope_blocks:
	def __init__(self):
		self.found = False

		self.values = []
		self.time = 0.01
		self.max = 1
		self.loop = -1
		self.release = -1
