# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.valobjs import dualstr

VERBOSE = False

class cvpj_envelope_adsr:
	def __init__(self):
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

	def from_envpoints(self, env_pointsdata, a_type, plugin_obj):
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
		
		fadeout = env_pointsdata.data['fadeout'] if 'fadeout' in env_pointsdata.data else 0
		pointsdata = env_pointsdata.points
		numpoints = len(pointsdata)

		sustainnum = -1 if (not env_pointsdata.sustain_on or env_pointsdata.sustain_point > numpoints) else env_pointsdata.sustain_point
		isenvconverted = 0

		if numpoints == 2:
			env_duration = pointsdata[1].pos
			env_value = pointsdata[0].value - pointsdata[1].value
			maxval = max(pointsdata[0].value, pointsdata[1].value)
			minval = min(pointsdata[0].value, pointsdata[1].value)

			if pointsdata[0].value != pointsdata[1].value:
				if sustainnum in [-1, 1]:
					if env_value > 0:
						self.decay = env_duration
						self.sustain = 0
						if a_type == 'vol': self.amount = 1-minval
						if VERBOSE: print("[env_asdr_from_points] 2 | ^_")
						isenvconverted = 201 #debug
					else: 
						self.attack = env_duration
						#self.release = fadeout
						if VERBOSE: print("[env_asdr_from_points] 2 | _^")
						isenvconverted = 202 #debug

				elif sustainnum == 0:
					if env_value >= 0: 
						self.release = env_duration
						isenvconverted = 203 #debug
					else:
						self.release = env_duration
						self.amount = -1
						isenvconverted = 204 #debug

				if VERBOSE: print(sustainnum, isenvconverted)

		elif numpoints == 3:
			envp_middle = pointsdata[1].pos
			envp_end = pointsdata[2].pos
			envv_first = pointsdata[0].value
			envv_middle = pointsdata[1].value
			envv_end = pointsdata[2].value
			firstmid_s = envv_first-envv_middle
			midend_s = envv_end-envv_middle

			if VERBOSE: print(pointsdata[0].pos, pointsdata[0].value)
			if VERBOSE: print(pointsdata[1].pos, pointsdata[1].value)
			if VERBOSE: print(pointsdata[2].pos, pointsdata[2].value)

			if VERBOSE: print(envp_middle, envp_end, '|', envv_first, envv_middle, envv_end)
			if firstmid_s > 0 and sustainnum == -1: a_sustain = 0

			if firstmid_s > 0 and midend_s == 0:
				if VERBOSE: print("[env_asdr_from_points] 3 | ^__" )
				if sustainnum == -1: self.decay = envp_middle
				if sustainnum == 0: self.release = envp_middle
				isenvconverted = 300

			elif firstmid_s > 0 and midend_s < 0:
				if VERBOSE: print("[env_asdr_from_points] 3 | ^._" )
				if sustainnum == -1: 
					self.decay = envp_end
					self.decay_tension = (envv_middle-(envv_first/2))*2
					self.sustain = 0
					self.release = fadeout
					isenvconverted = 301

				if sustainnum == 0: 
					self.release = envp_end
					self.release_tension = ((((envp_middle/envp_end)/2)+(envv_middle/2))-0.5)*2
					isenvconverted = 302

				if sustainnum == 1: 
					self.decay = envp_middle
					self.release = envp_end-envp_middle
					self.sustain = envv_middle
					isenvconverted = 303
   
			elif firstmid_s < 0 and midend_s < 0:
				if VERBOSE: print("[env_asdr_from_points] 3 | _^." )
				if sustainnum in [0, -1]: 
					self.attack = envp_middle
					self.decay = (envp_end-envp_middle)
					self.sustain = envv_end
					isenvconverted = 304
				if sustainnum == 1: 
					self.attack = envp_middle
					self.release = (envp_end-envp_middle)
					isenvconverted = 305

			elif firstmid_s == 0 and midend_s < 0:
				if VERBOSE: print("[env_asdr_from_points] 3 | ^^.")
				if sustainnum == -1:
					self.hold = envp_middle
					self.decay = envp_end-envp_middle
					self.sustain = envv_end
					isenvconverted = 306
				if sustainnum == 0: 
					self.hold = envp_middle
					self.release = envp_end-envp_middle
					isenvconverted = 307

			elif firstmid_s < 0 and midend_s > 0:
				if VERBOSE: print("[env_asdr_from_points] 3 | _.^")
				self.attack = envp_end
				self.attack_tension = ((envp_end-envp_middle)-1)
				isenvconverted = 308

			elif firstmid_s == 0 and midend_s > 0:
				if VERBOSE: print("[env_asdr_from_points] 3 | __^")
				self.predelay = envp_middle
				self.attack = envp_end-envp_middle
				isenvconverted = 309

			elif firstmid_s < 0 and midend_s == 0:
				if VERBOSE: print("[env_asdr_from_points] 3 | _^^")
				self.attack = envp_middle
				self.hold = envp_end-envp_middle
				isenvconverted = 310

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
			#	isenvconverted = True

			if VERBOSE: print(sustainnum, isenvconverted)

			if isenvconverted != 0 and self.sustain != 0 and self.release == 0: self.release = fadeout

		elif numpoints > 3:
			if sustainnum in [-1, 2] and numpoints == 4 and pointsdata[0].value == 0 and pointsdata[3].value == 0 and pointsdata[1].value>=pointsdata[2].value:
				self.attack = pointsdata[1].pos
				self.decay = pointsdata[2].pos-pointsdata[1].pos
				self.sustain = pointsdata[2].value
				self.release = pointsdata[3].pos-pointsdata[2].pos
			elif env_pointsdata.loop_on and env_pointsdata.loop_start > env_pointsdata.loop_end:
				sv = [x.value for x in pointsdata[0:env_pointsdata.loop_start+1]]
				sp = [x.pos for x in pointsdata[0:env_pointsdata.loop_start+1]]
				lv = [x.value for x in pointsdata[env_pointsdata.loop_start:env_pointsdata.loop_end+1]]
				lp = [x.pos for x in pointsdata[env_pointsdata.loop_start:env_pointsdata.loop_end+1]]

				if (env_pointsdata.loop_start+1 > 1):
					if sustainnum == -1:
						lfo_amt = max(lv)-min(lv)

						if sv[0] < sv[-1]: 
							self.attack = sp[-1]
						elif sv[-1] < sv[0]: 
							self.decay = sp[-1]*4
							self.sustain = (sv[-1]*lfo_amt)+(1-lfo_amt)

						if plugin_obj:
							lfo_obj = plugin_obj.lfo_add(a_type)
							lfo_obj.predelay = sp[-1]-sp[0]
							lfo_obj.time.set_seconds(1/(lp[-1]-lp[0])/2)
							lfo_obj.amount = lfo_amt

					elif sustainnum == 0:
						if sv[0] < sv[-1]: 
							self.attack = sp[-1]
							self.release = fadeout
						elif sv[-1] < sv[0]: 
							self.sustain = sv[0]
							self.release = sp[-1]

			elif env_pointsdata.points[-1].pos != 0:
				last_pos = env_pointsdata.points[-1].pos
				t_pos = [x.pos for x in env_pointsdata.points]
				t_val = [x.value for x in env_pointsdata.points]
				p_min = min(t_val)
				p_max = max(t_val)
				t_val = [xtramath.between_to_one(p_min, p_max, x) for x in t_val]

				pcv = 1/(numpoints-1)

				t_pos_chan = []
				prev = None
				for x in t_pos:
					if prev != None: t_pos_chan.append( ((x-prev)/last_pos)/pcv )
					prev = x

				t_val_chan = []
				prev = None
				for x in t_val:
					if prev != None: t_val_chan.append(x-prev)
					prev = x

				t_val_chan_a = [abs(x) for x in t_val_chan]
				t_val_chan_d = []
				for x in t_val_chan:
					if x>0: t_val_chan_d.append(1)
					elif x<0: t_val_chan_d.append(-1)
					else: t_val_chan_d.append(0)

				t_comb = [(t_val_chan_a[n]/pcv)/(v if v else 1) for n, v in enumerate(t_pos_chan)]
				t_comb_c = [(1/t_comb[n] if t_comb[n] != 0 else 1) for n, v in enumerate(t_comb)]
				t_comb_s = [1/(x+1) for x in range(numpoints-1)]
				t_comb_e = t_comb_s[::-1]
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
				self.release = fadeout

				if sustainnum == 0 and posneg<=-1:
					if VERBOSE: print("[env_asdr_from_points] 4 | ^_")
					self.release = last_pos
					self.release_tension = (tension/2)

				elif sustainnum == -1 and posneg>=1:
					if VERBOSE: print("[env_asdr_from_points] 4 | _^")
					self.attack = last_pos
					self.attack_tension = -(tension/2)

				elif sustainnum == -1 and posneg<=-1:
					if VERBOSE: print("[env_asdr_from_points] 4 | ^_")
					self.decay = last_pos
					self.decay_tension = (tension/2)



class cvpj_envelope_blocks:
	def __init__(self):
		self.found = False

		self.values = []
		self.time = 0.01
		self.max = 1
		self.loop = -1
		self.release = -1
