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
		point_start = env_pointsdata[0]
		point_end = env_pointsdata[1]

		env_duration = point_end.pos
		env_value = point_start.value - point_end.value
		maxval = max(point_start.value, point_end.value)
		minval = min(point_start.value, point_end.value)
		sustainp = sustainnum == 0
		use_fadeout = env_pointsdata.data['use_fadeout'] if 'use_fadeout' in env_pointsdata.data else 0
		fadeout = env_pointsdata.data['fadeout'] if 'fadeout' in env_pointsdata.data else True

		if point_start.value != point_end.value:
			if env_pointsdata.loop_on and env_pointsdata.loop_start < env_pointsdata.loop_end:
				self.release = fadeout
				self.amount = 1
				if plugin_obj:
					if VERBOSE: print("env_asdr_from_points | 2 | LFO")
					lfo_obj = plugin_obj.lfo_add(a_type)
					lfo_obj.prop.shape = 'saw' if env_value>0 else 'saw_down'
					lfo_obj.time.set_seconds(env_duration)
					lfo_obj.amount = min(abs(env_value/1.3),1)
					lfo_obj.retrigger = True

			elif sustainp:
				self.release = env_duration
				if point_start.value>point_end.value: 
					if VERBOSE: print("env_asdr_from_points | 2A | █▁")
					self.release = env_duration
					self.sustain = 1
					self.amount = 1
					return 201

			else:
				if env_value > 0:
					if VERBOSE: print("env_asdr_from_points | 2B | █▁")
					self.decay = env_duration
					self.sustain = minval
					self.amount = 1
					return 202
				else: 
					if VERBOSE: print("env_asdr_from_points | 2B | ▁█")
					self.attack = env_duration
					self.amount = 1
					return 203

	def from_envpoints__internal_3point(self, sustainnum, plugin_obj, env_pointsdata):
		use_fadeout = env_pointsdata.data['use_fadeout'] if 'use_fadeout' in env_pointsdata.data else 0
		fadeout = env_pointsdata.data['fadeout'] if 'fadeout' in env_pointsdata.data else True

		envp_middle = env_pointsdata[1].pos
		envp_end = env_pointsdata[2].pos
		envv_first = env_pointsdata[0].value
		envv_middle = env_pointsdata[1].value
		envv_end = env_pointsdata[2].value
		firstmid_s = envv_first-envv_middle
		midend_s = envv_end-envv_middle

		#if VERBOSE: print(pointsdata[0].pos, pointsdata[0].value)
		#if VERBOSE: print(pointsdata[1].pos, pointsdata[1].value)
		#if VERBOSE: print(pointsdata[2].pos, pointsdata[2].value)
		#if VERBOSE: print(envp_middle, envp_end, '|', envv_first, envv_middle, envv_end)

		if firstmid_s > 0 and sustainnum == -1: a_sustain = 0

		debugnum = 0

		if firstmid_s > 0 and midend_s == 0:
			if VERBOSE: print("env_asdr_from_points | 3 | █__" )
			if sustainnum == -1: self.decay = envp_middle
			if sustainnum == 0: self.release = envp_middle
			debugnum = 300
			self.amount = 1

		elif firstmid_s > 0 and midend_s < 0:
			if VERBOSE: print("env_asdr_from_points | 3 | █▄▁" )
			if sustainnum == -1: 
				self.decay = envp_end
				self.decay_tension = (envv_middle-(envv_first/2))*2
				self.sustain = 0
				if use_fadeout: self.release = fadeout
				self.amount = 1
				debugnum = 301

			if sustainnum == 0: 
				self.release = envp_end
				self.release_tension = ((((envp_middle/envp_end)/2)+(envv_middle/2))-0.5)*2
				self.amount = 1
				debugnum = 302

			if sustainnum == 1: 
				self.decay = envp_middle
				self.release = envp_end-envp_middle
				self.sustain = envv_middle
				self.amount = 1
				debugnum = 303
   
		elif firstmid_s < 0 and midend_s < 0:
			if VERBOSE: print("env_asdr_from_points | 3 | ▁█▄" )
			if sustainnum in [0, -1]: 
				self.attack = envp_middle
				self.decay = (envp_end-envp_middle)
				self.sustain = envv_end
				self.amount = 1
				debugnum = 304
			if sustainnum == 1: 
				self.attack = envp_middle
				self.release = (envp_end-envp_middle)
				self.amount = 1
				debugnum = 305

		elif firstmid_s == 0 and midend_s < 0:
			if VERBOSE: print("env_asdr_from_points | 3 | ██▄")
			if sustainnum == -1:
				self.hold = envp_middle
				self.decay = envp_end-envp_middle
				self.sustain = envv_end
				self.amount = 1
				debugnum = 306
			if sustainnum == 0: 
				self.hold = envp_middle
				self.release = envp_end-envp_middle
				self.amount = 1
				debugnum = 307

		elif firstmid_s < 0 and midend_s > 0:
			if VERBOSE: print("env_asdr_from_points | 3 | ▁▄█")
			self.attack = envp_end
			self.attack_tension = ((envp_end-envp_middle)-1)
			self.amount = 1
			debugnum = 308

		elif firstmid_s == 0 and midend_s > 0:
			if VERBOSE: print("env_asdr_from_points | 3 | __█")
			self.predelay = envp_middle
			self.attack = envp_end-envp_middle
			self.amount = 1
			debugnum = 309

		elif firstmid_s < 0 and midend_s == 0:
			if VERBOSE: print("env_asdr_from_points | 3 | _██")
			self.attack = envp_middle
			self.hold = envp_end-envp_middle
			self.amount = 1
			debugnum = 310

		#elif firstmid_s > 0 and midend_s > 0:
		#	#print("env_asdr_from_points | 3 | █.█")
		#	if sustainnum in [None, 1]:
		#		self.attack = envp_middle
		#		a_decay = (envp_end-envp_middle)
		#		a_amount = envv_middle-1
		#	if sustainnum == 1: 
		#		self.attack = envp_middle
		#		self.release = (envp_end-envp_middle)
		#		a_amount = envv_middle-1
		#	return True

		if debugnum != 0 and self.sustain != 0 and self.release == 0: self.release = fadeout
		return debugnum

	def from_envpoints__internal_adsr(self, sustainnum, env_pointsdata):
		env_a = env_pointsdata[0]
		env_d = env_pointsdata[1]
		env_s = env_pointsdata[2]
		env_r = env_pointsdata[3]

		cond_sus = sustainnum in [-1, 2]
		cond_adsr1 = env_a.value == 0
		cond_adsr3 = env_d.value>=env_s.value
		cond_adsr2 = env_r.value == 0

		if cond_sus and cond_adsr1 and cond_adsr2 and cond_adsr3:
			if VERBOSE: print("env_asdr_from_points | 4 | ADSR")
			self.attack = env_d.pos
			self.decay = env_s.pos-env_d.pos
			self.sustain = env_s.value
			self.release = env_r.pos-env_s.pos
			self.amount = 1
			return True

	def from_envpoints__internal_5point(self, sustainnum, env_pointsdata):
		numpoints = len(env_pointsdata)

		if env_pointsdata['pos'][-1] != 0:
			cond1 = not env_pointsdata.loop_on
			cond2 = env_pointsdata.loop_on and env_pointsdata.loop_start==env_pointsdata.loop_end

			t_dif = data_values.list__dif_val(env_pointsdata['value'], None)

			if cond1 or cond2:
				if sustainnum in [-1, 0]:
					lastpos = env_pointsdata['pos'][-1]
					tension = tension_detect(env_pointsdata, None, None)
					outv = False
					while len(t_dif)>1:
						if t_dif[-1]==0: del t_dif[-1]
						else: break

					if min(t_dif)<=0 and max(t_dif)<0:
						if VERBOSE: print("env_asdr_from_points | 5 | █▄▁")
						outv = True
						if sustainnum == -1:
							self.decay = lastpos
							self.decay_tension = tension
							self.sustain = 0
							self.amount = 1
						if sustainnum == 0:
							self.release = lastpos
							self.release_tension = tension
							self.amount = 1
					if min(t_dif)>0 and max(t_dif)>=0:
						if VERBOSE: print("env_asdr_from_points | 5 | ▁▄█")
						outv = True
						self.attack = lastpos
						self.attack_tension = tension
						self.amount = 1
					if outv: return 500

				susmode = True
				if sustainnum == -1:
					susmode = False
					sustainnum = 0
					for x in t_dif:
						if x>0: sustainnum += 1
						else: break

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

				outv = False

				if susmode:
					if firstval<midval:
						if first_dif_higher:
							if VERBOSE: print("env_asdr_from_points | 5F| ▁▄█")
							self.attack = midpos
							self.attack_tension = tension_detect(env_pointsdata, 0, sustainnum+1)
							self.amount = 1
							outv = True

					elif firstval>midval:
						if not first_dif_higher:
							if VERBOSE: print("env_asdr_from_points | 5F| █▄▁")
							self.decay = midpos
							self.decay_tension = tension_detect(env_pointsdata, 0, sustainnum+1)
							self.sustain = midval
							self.amount = 1
							outv = True

					if lastval<midval:
						if last_dif_lower:
							if VERBOSE: print("env_asdr_from_points | 5L| █▄▁")
							self.release = lastpos-midpos
							self.release_tension = tension_detect(env_pointsdata, sustainnum, numpoints)
							self.amount = 1
							outv = True
					if outv: return 501
				else:
					if firstval<midval:
						if first_dif_higher:
							if VERBOSE: print("env_asdr_from_points | 6F| ▁▄█")
							self.attack = midpos
							self.attack_tension = tension_detect(env_pointsdata, 0, sustainnum+1)
							self.amount = 1
							outv = True

					if lastval<midval:
						if last_dif_lower:
							if VERBOSE: print("env_asdr_from_points | 6L| █▄▁")
							self.decay = lastpos-midpos
							self.decay_tension = tension_detect(env_pointsdata, sustainnum, numpoints)
							self.sustain = 0
							self.amount = 1
							outv = True
					if outv: return 601

				#outv = 0
				#for x in t_dif:
				#	if x<=0: outv += 1
				#	else: break

	def from_envpoints(self, env_pointsdata, a_type, plugin_obj):
		self.reset()
		
		use_fadeout = env_pointsdata.data['use_fadeout'] if 'use_fadeout' in env_pointsdata.data else 0
		fadeout = env_pointsdata.data['fadeout'] if 'fadeout' in env_pointsdata.data else True
		pointsdata = env_pointsdata.points
		numpoints = len(pointsdata)
		#if VERBOSE: 
		#	if not data_values.list__ifallsame([x.value for x in pointsdata]):
		#		env_pointsdata.debugview()

		sustainnum = -1 if (not env_pointsdata.sustain_on or env_pointsdata.sustain_point > numpoints-1) else env_pointsdata.sustain_point

		if numpoints == 2:
			return self.from_envpoints__internal_2point(sustainnum, a_type, plugin_obj, env_pointsdata)

		elif numpoints == 3:
			return self.from_envpoints__internal_3point(sustainnum, plugin_obj, env_pointsdata)

		elif numpoints > 3:
			if numpoints == 4:
				if self.from_envpoints__internal_adsr(sustainnum, env_pointsdata): return True

			self.from_envpoints__internal_5point(sustainnum, env_pointsdata)

class cvpj_envelope_blocks:
	def __init__(self):
		self.found = False

		self.values = []
		self.time = 0.01
		self.max = 1
		self.loop = -1
		self.release = -1
