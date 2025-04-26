# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects import debug
from objects.convproj import time
from objects.data_bytes import dynbytearr
from objects import valobjs
import math
import numpy as np
import copy

autopoints_premake = dynbytearr.dynbytearr_premake([
	('pos', np.float64), 
	('value', np.float64), 
	('value_end', np.float64), 
	('instant_mode', np.uint8), 
	('tension', np.float64), 
	('point_type', np.int32), 
	])

verbose_blocks_gfx = [' ','▁','▂','▃','▄','▅','▆','▇','█']

class debug_display:
	def __init__(self):
		self.val_min = 0
		self.val_max = 1
		self.dur_max = 1
		self.sustain = -1
		self.vsize = 6
		self.hsize = 120
		self.color_norm = '\x1b[37;40m'
		self.color_point = '\x1b[96;44m'
		self.color_sus = '\x1b[33;41m'
		self.points = []
		self.set_size(8, 120)

	def set_size(self, vs, hs):
		self.vsize = vs
		self.hsize = hs
		self.gfxdata_vals = [0 for x in range(hs)]

	def from_points(self, autopoints_obj):
		useddata = autopoints_obj.points.get_used()
		self.points = [[x['pos'], x['value'], x['instant_mode'], x['value_end']] for x in useddata]
		if self.points:
			self.dur_max = autopoints_obj.get_dur()
			self.val_min = min(useddata['value'])
			self.val_max = max(useddata['value'])
			self.sustain =  autopoints_obj.sustain_point if autopoints_obj.sustain_on else -1
		else:
			self.val_min = 0
			self.val_max = 1
			self.dur_max = 1
			self.sustain = -1

	def gfxval_range(self, p_start, p_end, v_start, v_end):
		size = p_end-p_start
		for x in range(size):
			self.gfxdata_vals[p_start+x] = xtramath.between_from_one(v_start, v_end, x/size)

	def gfxval_flat(self, p_start, p_end, val):
		size = p_end-p_start
		for x in range(size):
			self.gfxdata_vals[p_start+x] = val

	def print(self):
		procpoints = [[p/self.dur_max, xtramath.between_to_one(self.val_min, self.val_max, v), i, xtramath.between_to_one(self.val_min, self.val_max, e)] for p,v,i,e in self.points]
		print('NUM POINTS: ',len(self.points))

		gfxdata_colors = ['\x1b[37;40m' for x in range(self.hsize)]

		debp = [[int(xtramath.clamp(x,0,1)*self.hsize), y, i, e] for x,y,i,e in procpoints]

		for n in range(len(debp)-1):
			curp = debp[n]
			nextp = debp[n+1]
			size = nextp[0]-curp[0]

			if curp[2] == 0:
				if nextp[2]==0:
					self.gfxval_range(debp[n][0], nextp[0], curp[1], nextp[1])
				elif nextp[2]==1:
					self.gfxval_flat(debp[n][0], nextp[0], curp[1])
				elif nextp[2]==2:
					self.gfxval_range(debp[n][0], nextp[0], curp[1], nextp[1])
			if curp[2] == 1:
				if nextp[2]==0:
					self.gfxval_range(debp[n][0], nextp[0], curp[1], nextp[1])
				elif nextp[2]==1:
					self.gfxval_flat(debp[n][0], nextp[0], curp[1])
				elif nextp[2]==2:
					self.gfxval_range(debp[n][0], nextp[0], curp[1], nextp[1])
			if curp[2] == 2:
				if nextp[2]==0:
					self.gfxval_range(debp[n][0], nextp[0], curp[3], nextp[1])
				elif nextp[2]==1:
					self.gfxval_flat(debp[n][0], nextp[0], curp[1])
				elif nextp[2]==2:
					self.gfxval_range(debp[n][0], nextp[0], curp[3], nextp[1])

		for n, d in enumerate(procpoints):
			p, v, i, e = d
			blocknum = int((p)*self.hsize)
			gfxdata_colors[min(blocknum, self.hsize-1)] = '\x1b[96;44m'
			sustain = self.sustain
			if sustain>=0:
				if sustain==n:
					gfxdata_colors[min(blocknum, self.hsize-1)] = '\x1b[33;41m'

		for vh in range(self.vsize, 0, -1):
			ft = [int(xtramath.clamp((x*self.vsize)-(vh-1), 0, 1)*(len(verbose_blocks_gfx)-1)) for x in self.gfxdata_vals]
			gfxdata_txt = [' ' for x in range(self.hsize)]
			for n, x in enumerate(ft): gfxdata_txt[n] = verbose_blocks_gfx[int(x)]
			for x in range(self.hsize): print(gfxdata_colors[x]+gfxdata_txt[x], end='')
			print('\033[0;0m')


class output_autopoint:
	def __init__(self, maindata, point):
		val_type = maindata.val_type
		self.pos = float(point['pos']) if maindata.time_float else int(point['pos'])
		if val_type == 'float':
			self.value = float(point['value'])
			self.value_end = float(point['value_end'])
		elif val_type == 'int':
			self.value = int(point['value'])
			self.value_end = int(point['value_end'])
		elif val_type == 'bool':
			self.value = bool(int(point['value']))
			self.value_end = bool(int(point['value_end']))
		else:
			self.value = float(point['value'])
			self.value_end = float(point['value_end'])
		self.instant_mode = int(point['instant_mode'])
		self.tension = float(point['tension'])
		self.point_type = point['point_type']

autoblocks_premake = dynbytearr.dynbytearr_premake([
	('pos_start', np.float64), 
	('pos_end', np.float64), 
	('dur', np.float64), 
	('value_start', np.float64), 
	('value_end', np.float64), 
	('diff', np.float64), 
	])

class cvpj_autopoints:
	def __init__(self, time_ppq, time_float, val_type):
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.val_type = val_type
		self.is_seconds = False

		self.clear()

		self.name = ''

	def __len__(self):
		return self.points.__len__()

	def __bool__(self):
		return bool(len(self.points))

	def __iter__(self):
		for x in self.points:
			yield output_autopoint(self, x)

	def __getitem__(self, v):
		if isinstance(v, int):
			dataval = self.points.data
			usednums = np.where(self.points.data['used'])[0]
			return output_autopoint(self, dataval[usednums[v]]) 
		if isinstance(v, str):
			usedvals = self.points.get_used()
			if v == 'pos': return [float(x) for x in usedvals['pos']]
			if v == 'value': return [float(x) for x in usedvals['value']]

	def iter_raw(self):
		for x in self.points:
			yield x.copy()

	def clear(self):
		self.data = {}

		self.points = autopoints_premake.create()
		self.points_cur = self.points.create_cursor()
		self.point_types = valobjs.indexed_value()

		self.enabled = True
		self.loop_on = False
		self.loop_start = 0
		self.loop_end = 0

		self.sustain_on = False
		self.sustain_loop = False
		self.sustain_point = 0
		self.sustain_end = 0

	def debugview(self, txti='', vsize=6, hsize=120):
		debug_display_obj = debug_display()
		debug_display_obj.from_points(self)
		debug_display_obj.print()

	def to_plot(self, plot_obj):
		op_pos = []
		op_val = []

		scat_pos = []
		scat_val = []

		prev_val = 0
		for n, p in enumerate(self.points):
			im = p['instant_mode']

			scat_pos.append(p['pos'])
			scat_val.append(p['value'])

			if im == 0:
				op_pos.append(p['pos'])
				op_val.append(p['value'])
			elif im == 1:
				if n == 0:
					op_pos.append(p['pos'])
					op_val.append(p['value'])
				else:
					op_pos.append(p['pos'])
					op_val.append(prev_val)
					op_pos.append(p['pos'])
					op_val.append(p['value'])
			elif im == 2:
				op_pos.append(p['pos'])
				op_val.append(p['value'])
				op_pos.append(p['pos'])
				op_val.append(p['value_end'])

			prev_val = p['value']

		plot_obj.plot(op_pos, op_val)
		plot_obj.scatter(scat_pos, scat_val)

	def change_seconds(self, is_seconds, bpm, ppq):
		if is_seconds and not self.is_seconds:
			self.points.data['pos'] = xtramath.step2sec(self.points.data['pos']/(ppq), bpm)
			self.is_seconds = True
		elif not is_seconds and self.is_seconds:
			self.points.data['pos'] = xtramath.sec2step(self.points.data['pos'], bpm)*(ppq)
			self.is_seconds = False
		
	def change_timings(self, time_ppq, time_float):
		if not self.is_seconds:
			for n, x in enumerate(self.points.data):
				self.points.data[n]['pos'] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, x['pos'])
		self.time_ppq = time_ppq
		self.time_float = time_float

	def sort(self):
		diffv = self.points.get_used()['pos']
		diffv = np.diff(diffv)<0
		if np.any(diffv):
			self.points_cur.sort(['pos'])

	def clean(self):
		self.points_cur.clean()

	def points__add_point(self, pos, val, ptype):
		points_cur = self.points_cur
		points_cur.add()
		points_cur['pos'] = pos
		points_cur['value'] = val
		if ptype == 'instant':
			points_cur['instant_mode'] = 1
		else:
			points_cur['point_type'] = self.point_types.add(ptype)
		return points_cur

	def points__add_normal(self, pos, val, tension, ptype):
		points_cur = self.points_cur
		points_cur.add()
		points_cur['pos'] = pos
		points_cur['value'] = val
		points_cur['tension'] = tension
		points_cur['point_type'] = self.point_types.add(ptype)
		return points_cur

	def points__add_instant(self, pos, val):
		points_cur = self.points_cur
		points_cur.add()
		points_cur['pos'] = pos
		points_cur['value'] = val
		points_cur['instant_mode'] = 1
		return points_cur

	def points__add_instant_cha(self, pos, val, end):
		points_cur = self.points_cur
		points_cur.add()
		points_cur['pos'] = pos
		points_cur['value'] = val
		points_cur['value_end'] = end
		points_cur['instant_mode'] = 2
		return points_cur

	def points__add_copied(self, x):
		points_cur = self.points_cur
		points_cur.add_copied(x)

	def get_dur(self):
		if self: 
			return max(self.points.get_used()['pos'])
		else: 
			return -1

	def get_durpos(self):
		if self: 
			useddata = self.points.get_used()['pos']
			return min(useddata), max(useddata)
		else: 
			return -1, -1

	def remove_instant(self):
		useddata = self.points.get_used()
		if len(useddata):
			if np.count_nonzero(useddata['instant_mode']):
				self.points_cur.clear_keep_size()
				prev_val = 0
				for n, p in enumerate(useddata):
					im = p['instant_mode']

					if n == 0:
						if im == 0:
							self.points__add_normal(p['pos'], p['value'], 0, None)
						elif im == 1:
							self.points__add_normal(p['pos'], p['value'], 0, None)
						elif im == 2:
							self.points__add_normal(p['pos'], p['value_end'], 0, None)
					else:
						if im == 0:
							self.points__add_normal(p['pos'], p['value'], 0, None)
						elif im == 1:
							self.points__add_normal(p['pos'], prev_val, 0, None)
							self.points__add_normal(p['pos'], p['value'], 0, None)
						elif im == 2:
							self.points__add_normal(p['pos'], p['value'], 0, None)
							self.points__add_normal(p['pos'], p['value_end'], 0, None)
					prev_val = p['value']

	def add_instant(self):
		self.remove_instant()
		self.sort()
		self.clean()

		useddata = self.points.get_used()
		if len(useddata):
			self.points_cur.add_copied(useddata[0])

			diffc = useddata[1:]
			diff1 = np.diff(useddata['value'])==0
			diff2 = np.diff(useddata['pos'])!=0
			diffo = (diff1 & diff2).astype(np.int8)

			wherevals = np.where(diffo==1)[0]
			self.points.data['used'][wherevals+1] = 0
			self.points.data['instant_mode'][wherevals+2] = 1

			self.sort()
			self.clean()

	def edit_move(self, pos):
		self.points.data['pos'] += pos

	def copy(self):
		return copy.deepcopy(self)

	def edit_trim_left(self, startat, has_start):
		self.clean()
		self.sort()
		durval = len(self)

		if durval:
			useddata = self.points.get_used()
			usedpos = useddata['pos']

			sidep = int(min(useddata['pos'])>startat)*-1
			sidep += int(max(useddata['pos'])<=startat)*1

			if sidep==0:
				sidesear_l = np.searchsorted(usedpos, startat, side='left')
				sidesear_r = np.searchsorted(usedpos, startat, side='right')

				data_r = self.points.data[sidesear_r]
				data_rm = self.points.data[sidesear_r-1]

				wherepos = np.where(usedpos<=startat)[0]-1
				self.points.data['used'][wherepos] = 0

				if sidesear_l == sidesear_r:
					if len(self)>1:
						instant_mode = self.points.data[sidesear_r-1]['instant_mode']

						if instant_mode==0:
							pos_min = data_rm['pos']
							pos_max = data_r['pos']

							val_min = data_rm['value']
							val_max = data_r['value']

							btw_one = xtramath.between_to_one(pos_min, pos_max, startat)
							self.points.data[sidesear_r-1]['pos'] = startat
							self.points.data[sidesear_r-1]['value'] = xtramath.between_from_one(val_min, val_max, btw_one)

						if instant_mode==1:
							self.points.data[sidesear_r-1]['pos'] = startat

						if instant_mode==2:
							pos_min = data_rm['pos']
							pos_max = data_r['pos']

							val_min = data_rm['value_end']
							val_max = data_r['value']

							btw_one = xtramath.between_to_one(pos_min, pos_max, startat)
							self.points.data[sidesear_r-1]['pos'] = startat
							self.points.data[sidesear_r-1]['value'] = xtramath.between_from_one(val_min, val_max, btw_one)
							self.points.data[sidesear_r-1]['instant_mode'] = 0

			if sidep==-1:
				if useddata[0]['instant_mode'] == 2:
					useddata[0]['value'] = self.points.data[0]['value_end']

				self.points_cur.clear_keep_size()
				if has_start:
					c = useddata[0].copy()
					c['pos'] = startat
					c['instant_mode'] = 1
					self.points_cur.add_copied(c)

				for x in useddata:
					self.points_cur.add_copied(x)

			if sidep==1:
				wherepos = np.where(self.points.data['used'])[0][-1]
				self.points.data['used'] = 0
				self.points.data['used'][wherepos] = 1

				instant_mode = self.points.data[wherepos]['instant_mode']
				if instant_mode == 2:
					self.points.data[wherepos]['pos'] = startat
					self.points.data[wherepos]['value'] = self.points.data[wherepos]['value_end']
					self.points.data[wherepos]['instant_mode'] = 0
				else:
					self.points.data[wherepos]['pos'] = startat

		self.clean()

	def edit_trim_right(self, startat, has_end, defualtval=None):
		self.clean()
		self.sort()
		durval = len(self)

		if durval:
			useddata = self.points.get_used()
			usedpos = useddata['pos']

			sidep = int(min(useddata['pos'])>startat)*-1
			sidep += int(max(useddata['pos'])<=startat)*1

			if sidep==0:
				sidesear_l = np.searchsorted(usedpos, startat, side='left')
				sidesear_r = np.searchsorted(usedpos, startat, side='right')

				wherepos = np.where(usedpos>=startat)[0]
				wherepos = wherepos[(len(self.points.data)-1)>wherepos]

				if len(wherepos):
					self.points.data['used'][wherepos+1] = 0
					if sidesear_l == sidesear_r:
						if len(self)>1:
							lastused = wherepos[0]
							instant_mode = self.points.data[lastused]['instant_mode']
	
							#instant_mode = self.points.data[sidesear_r]['instant_mode']
	
							if instant_mode==0:
								pos_min = self.points.data[lastused-1]['pos']
								pos_max = self.points.data[lastused]['pos']
	
								val_min = self.points.data[lastused-1]['value']
								val_max = self.points.data[lastused]['value']
	
								btw_one = xtramath.between_to_one(pos_min, pos_max, startat)
	
								self.points.data[lastused]['value'] = xtramath.between_from_one(val_min, val_max, btw_one)
								self.points.data[lastused]['pos'] = startat
	
							if instant_mode==1:
								self.points.data[lastused]['value'] = self.points.data[lastused-1]['value']
								self.points.data[lastused]['pos'] = startat
								self.points.data[lastused]['instant_mode'] = 0
	
							if instant_mode==2:
								pos_min = self.points.data[lastused-1]['pos']
								pos_max = self.points.data[lastused]['pos']
	
								val_min = self.points.data[lastused-1]['value_end']
								val_max = self.points.data[lastused]['value']
	
								btw_one = xtramath.between_to_one(pos_min, pos_max, startat)
	
								self.points.data[lastused]['pos'] = startat
								self.points.data[lastused]['value'] = xtramath.between_from_one(val_min, val_max, btw_one)
								self.points.data[lastused]['instant_mode'] = 0
	
							#print(self.points.data[lastused])

			if sidep==-1:
				wherepos = np.where(usedpos>startat)[0]
				wherepos = wherepos[(len(self.points.data)-1)>wherepos]
				if len(wherepos):
					self.points.data['used'][wherepos+1] = 0
	
					if self.points.data[0]['instant_mode'] == 2:
						self.points.data[0]['pos'] = startat
						self.points.data[0]['instant_mode'] = 0
					if self.points.data[0]['instant_mode'] == 1:
						self.points.data[0]['pos'] = startat
						self.points.data[0]['instant_mode'] = 0
					if self.points.data[0]['instant_mode'] == 0:
						self.points.data[0]['pos'] = startat

			if sidep==1:
				if has_end:
					self.clean()
					lastused = useddata[-1]
					instant_mode = lastused['instant_mode']

					if defualtval is not None:
						self.points__add_normal(lastused['pos'], defualtval, 0, None)
						if instant_mode == 2:
							self.points__add_normal(startat, lastused['value_end'], 0, None)
						else:
							self.points__add_normal(startat, defualtval, 0, None)
					else:
						if instant_mode == 2:
							self.points__add_normal(startat, lastused['value_end'], 0, None)
						else:
							self.points__add_normal(startat, lastused['value'], 0, None)

		self.clean()

	def edit_trim_both(self, startat, endat, sides):
		if startat<=endat:
			self.edit_trim_right(endat, sides)
			self.edit_trim_left(startat, sides)
		else:
			self.clear()

	def edit_trimmove(self, startat, endat):
		self.edit_trim_both(startat, endat, True)
		self.edit_move(-startat)

	def calc(self, mathtype, val1, val2, val3, val4):
		for p in self.points.data:
			p['value'] = xtramath.do_math(p['value'], mathtype, val1, val2, val3, val4)

	def funcval(self, i_function):
		for p in self.points.data:
			p['value'] = i_function(p['value'])

	def merge_types_data(self, other):
		main_point_types = self.point_types
		other_point_types = other.point_types
		return main_point_types.merge_other(other_point_types)

	def find_areas(self, tres):
		self.sort()
		useddata = self.points.get_used()

		if len(useddata)>1:
			diff_pos = np.diff(useddata['pos'])
			cond_pos = diff_pos>(tres)
			diff_val = np.diff(useddata['value'])
			cond_val = diff_val==0

			outconds = np.logical_and(cond_pos, cond_val)

			splitareas = []

			for n, x in enumerate(useddata):
				is_split = outconds[n-1] if n else True

				if is_split: splitareas.append([float(x['pos']), float(x['pos'])+tres])
				else: splitareas[-1][1] = max(float(x['pos']), splitareas[-1][1])

				#print(
				#	str(x['pos']).ljust(12),
				#	str(x['value']).ljust(12),
				#	str(is_split).ljust(12),
				#	)

			return splitareas

		elif len(useddata)==1:
			x = useddata[0]
			return [[float(x['pos']), float(x['pos'])+tres]]

		else:
			return []

	def inject(self, other, main_start, main_end, in_offset, nonpersist_val=None):
		if main_end>main_start:
			r_end = self.get_dur()

			main_points_start = self.copy()
			main_points_start.edit_trim_right(main_start, True)
			
			main_points_end = self.copy()
			main_points_end.edit_trim_left(main_end, True)
	
			in_points = other.copy()
			in_points.change_timings(self.time_ppq, self.time_float)

			if in_offset>=0: in_points.edit_move(main_start-in_offset)

			in_points.edit_trim_both(main_start, main_end, True)
	
			pointsmove = self.merge_types_data(in_points)
			in_points.points.data['point_type'] *= -1
	
			for s, d in pointsmove.items():
				wherevals = np.where(in_points.points.data['point_type']==(-s))
				in_points.points.data['point_type'][wherevals] = d

			self.points_cur.clear_keep_size()

			used_1 = main_points_start.points.get_used()
			for x in used_1: self.points_cur.add_copied(x)

			used_2 = in_points.points.get_used()
			if len(used_2):
				if nonpersist_val is not None: 
					first_point = used_2[0]
					self.points__add_instant(first_point['pos'], nonpersist_val)

				for x in used_2: self.points_cur.add_copied(x)

				if nonpersist_val is not None:
					last_point = used_2[-1]
					self.points__add_instant(last_point['pos'], nonpersist_val)

			if main_end<r_end:
				used_3 = main_points_end.points.get_used()
				for x in used_3: self.points_cur.add_copied(x)

			self.sort()

	def to_regions(self):
		useddata = self.points.get_used()
		autoblocks = autoblocks_premake.create()
		abc = autoblocks.create_cursor()

		for n in range(len(useddata)-1):
			d_cur = useddata[n]
			d_next = useddata[n+1]

			abc.add()
			abc['pos_start'] = d_cur['pos']
			abc['pos_end'] = d_next['pos']
			abc['dur'] = d_next['pos']-d_cur['pos']
			abc['value_start'] = d_cur['value'] if d_cur['instant_mode']!=2 else d_cur['value_end']
			abc['value_end'] = d_next['value'] if d_next['instant_mode']!=1 else d_cur['value']
			abc['diff'] = abc['value_end']-abc['value_start']

		return autoblocks.get_used()

	def from_blocks_obj(self, blocks_obj):
		self.clear()
		for numblock in range(len(blocks_obj.values)): 
			p_pos = numblock*blocks_obj.time
			p_value = xtramath.between_to_one(0, blocks_obj.max, blocks_obj.values[numblock])
			self.points__add_normal(p_pos, p_value, 0, None)
