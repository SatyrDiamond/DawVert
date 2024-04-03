# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import copy

from objects import counter
from functions import note_data
from objects_convproj import autoticks
from objects_convproj import autopoints
from objects_convproj import placements_autopoints
from objects_convproj import placements_autoticks

class cvpj_s_automation:
	def __init__(self, time_ppq, time_float, valtype):
		self.pl_points = None
		self.pl_ticks = None
		self.nopl_points = None
		self.nopl_ticks = None
		self.id = ''

		self.u_pl_points = False
		self.u_pl_ticks = False
		self.u_nopl_points = False
		self.u_nopl_ticks = False

		self.time_ppq = time_ppq
		self.time_float = time_float
		self.valtype = valtype

	def make_nopl_ticks(self):
		if not self.u_nopl_ticks: 
			self.nopl_ticks = autoticks.cvpj_autoticks(self.time_ppq, self.time_float, self.valtype)
			self.u_nopl_ticks = True

	def make_nopl_points(self):
		if not self.u_nopl_points: 
			self.nopl_points = autopoints.cvpj_autopoints(self.time_ppq, self.time_float, self.valtype)
			self.u_nopl_points = True

	def make_pl_ticks(self):
		if not self.u_pl_ticks: 
			self.pl_ticks = placements_autoticks.cvpj_placements_autoticks(self.time_ppq, self.time_float, self.valtype)
			self.u_pl_ticks = True

	def make_pl_points(self):
		if not self.u_pl_points: 
			self.pl_points = placements_autopoints.cvpj_placements_autopoints(self.time_ppq, self.time_float, self.valtype)
			self.u_pl_points = True

	def calc_div(self, calcval):
		if self.u_nopl_points: self.nopl_points.addmul(0, 1/calcval)
		if self.u_nopl_ticks: self.nopl_ticks.addmul(0, 1/calcval)
		if self.u_pl_points: self.pl_points.addmul(0, 1/calcval)
		if self.u_pl_ticks: self.pl_ticks.addmul(0, 1/calcval)

	def calc_mul(self, calcval):
		if self.u_nopl_points: self.nopl_points.addmul(0, calcval)
		if self.u_nopl_ticks: self.nopl_ticks.addmul(0, calcval)
		if self.u_pl_points: self.pl_points.addmul(0, calcval)
		if self.u_pl_ticks: self.pl_ticks.addmul(0, calcval)

	def calc_add(self, calcval):
		if self.u_nopl_points: self.nopl_points.addmul(calcval, 1)
		if self.u_nopl_ticks: self.nopl_ticks.addmul(calcval, 1)
		if self.u_pl_points: self.pl_points.addmul(calcval, 1)
		if self.u_pl_ticks: self.pl_ticks.addmul(calcval, 1)

	def calc_note2freq(self):
		if self.u_nopl_points: self.nopl_points.funcval(note_data.note_to_freq)
		if self.u_nopl_ticks: self.nopl_ticks.funcval(note_data.note_to_freq)
		if self.u_pl_points: self.pl_points.funcval(note_data.note_to_freq)
		if self.u_pl_ticks: self.pl_ticks.funcval(note_data.note_to_freq)

	def calc_addmul(self, i_add, i_mul):
		if self.u_nopl_points: self.nopl_points.addmul(i_add, i_mul)
		if self.u_nopl_ticks: self.nopl_ticks.addmul(i_add, i_mul)
		if self.u_pl_points: self.pl_points.addmul(i_add, i_mul)
		if self.u_pl_ticks: self.pl_ticks.addmul(i_add, i_mul)

	def calc_to_one(self, i_min, i_max):
		if self.u_nopl_points: self.nopl_points.to_one(i_min, i_max)
		if self.u_nopl_ticks: self.nopl_ticks.to_one(i_min, i_max)
		if self.u_pl_points: self.pl_points.to_one(i_min, i_max)
		if self.u_pl_ticks: self.pl_ticks.to_one(i_min, i_max)

	def calc_from_one(self, i_min, i_max):
		if self.u_nopl_points: self.nopl_points.from_one(i_min, i_max)
		if self.u_nopl_ticks: self.nopl_ticks.from_one(i_min, i_max)
		if self.u_pl_points: self.pl_points.from_one(i_min, i_max)
		if self.u_pl_ticks: self.pl_ticks.from_one(i_min, i_max)

	def calc_add(self, calcval):
		if self.u_nopl_points: self.nopl_points.addmul(calcval, 1)
		if self.u_nopl_ticks: self.nopl_ticks.addmul(calcval, 1)
		if self.u_pl_points: self.pl_points.addmul(calcval, 1)
		if self.u_pl_ticks: self.pl_ticks.addmul(calcval, 1)

	def calc_pow(self, calcval):
		if self.u_nopl_points: self.nopl_points.pow(calcval)
		if self.u_nopl_ticks: self.nopl_ticks.pow(calcval)
		if self.u_pl_points: self.pl_points.pow(calcval)
		if self.u_pl_ticks: self.pl_ticks.pow(calcval)

	def calc_pow_r(self, calcval):
		if self.u_nopl_points: self.nopl_points.pow_r(calcval)
		if self.u_nopl_ticks: self.nopl_ticks.pow_r(calcval)
		if self.u_pl_points: self.pl_points.pow_r(calcval)
		if self.u_pl_ticks: self.pl_ticks.pow_r(calcval)

	def calc_log(self, calcval):
		if self.u_nopl_points: self.nopl_points.log(calcval)
		if self.u_nopl_ticks: self.nopl_ticks.log(calcval)
		if self.u_pl_points: self.pl_points.log(calcval)
		if self.u_pl_ticks: self.pl_ticks.log(calcval)

	def calc_log_r(self, calcval):
		if self.u_nopl_points: self.nopl_points.log_r(calcval)
		if self.u_nopl_ticks: self.nopl_ticks.log_r(calcval)
		if self.u_pl_points: self.pl_points.log_r(calcval)
		if self.u_pl_ticks: self.pl_ticks.log_r(calcval)

	def add_autotick(self, p_pos, p_val):
		self.make_nopl_ticks()
		self.nopl_ticks.add_point(p_pos, p_val)

	def add_autopoint(self, p_pos, p_val, p_type):
		self.make_nopl_points()
		autopoint_obj = self.nopl_points.add_point()
		autopoint_obj.pos = p_pos
		autopoint_obj.value = p_val
		autopoint_obj.type = p_type

	def add_autopoints_twopoints(self, twopoints):
		self.make_nopl_points()
		for twopoint in twopoints:
			autopoint_obj = self.nopl_points.add_point()
			autopoint_obj.pos = twopoint[0]
			autopoint_obj.value = twopoint[1]

	def add_pl_points(self):
		self.make_pl_points()
		return self.pl_points.add(self.valtype)

	def add_pl_ticks(self):
		self.make_pl_ticks()
		return self.pl_ticks.add(self.valtype)

	def get_paramval_tick(self, firstnote, fallback):
		out_val = fallback
		if self.u_nopl_ticks: out_val = self.nopl_ticks.get_paramval(firstnote, out_val)
		return out_val

	def change_timings(self, time_ppq, time_float):
		if self.u_nopl_points: self.nopl_points.change_timings(time_ppq, time_float)
		if self.u_nopl_ticks: self.nopl_ticks.change_timings(time_ppq, time_float)
		if self.u_pl_points: self.pl_points.change_timings(time_ppq, time_float)
		if self.u_pl_ticks: self.pl_ticks.change_timings(time_ppq, time_float)
		self.time_ppq = time_ppq
		self.time_float = time_float


	# | Ticks       | Points      |
	# | NoPL | -PL- | NoPL | -PL- |
	# +------+------+------+------+---+
	# | iiii | 1--> |      | OOOO | M | convert__nopl_ticks_____pl_points
	# |      | iiii |      | OOOO | S | convert____pl_ticks_____pl_points

	# | iiii |      | OOOO |      | S | convert__nopl_ticks___nopl_points
	# |      |      | OOOO | iiii | S | convert____pl_points__nopl_points
	# |      | iiii | OOOO | <--1 | M | convert____pl_ticks___nopl_points
	
	# | iiii | OOOO |      |      | S | convert__nopl_ticks_____pl_ticks

	def convert__nopl_ticks_____pl_ticks(self):
		if self.u_nopl_ticks:
			self.make_pl_ticks()
			splitpl, ppq = self.nopl_ticks.split()
			for x, v in splitpl:
				pl_pos = x
				pl_dur = max(v.get_dur(), ppq)
				pl = self.add_pl_ticks()
				pl.data = v
				pl.position = x
				pl.duration = pl_dur

		self.nopl_ticks = None
		self.u_nopl_ticks = False

	def convert__nopl_ticks___nopl_points(self):
		if self.u_nopl_ticks:
			points_out = self.nopl_ticks.to_points()

			for x in points_out:
				self.add_autopoint(x[0], x[1], 'normal' if x[2] else 'instant')

		self.nopl_ticks = None
		self.u_nopl_ticks = False

	def convert____pl_ticks_____pl_points(self):

		if self.u_pl_ticks:
			for x in self.pl_ticks.iter():
				pl = self.add_pl_points()
				pl.position = x.position
				pl.duration = x.duration
				pl.cut_type = x.cut_type
				pl.cut_data = x.cut_data
				pl.muted = x.muted
				pl.visual = x.visual
				points_out = x.data.to_points()
				for x in points_out:
					autopoint_obj = pl.data.add_point()
					autopoint_obj.pos = x[0]
					autopoint_obj.value = x[1]
					autopoint_obj.type = 'normal' if x[2] else 'instant'


		self.pl_ticks = None
		self.u_pl_ticks = False

	def convert__nopl_ticks_____pl_points(self):
		self.convert__nopl_ticks_____pl_ticks()
		self.convert____pl_ticks_____pl_points()

	def convert____pl_points__nopl_points(self):
		if self.u_pl_points:
			for x in self.pl_points.iter():
				x.data.edit_trimmove(0, x.duration)
				for c, p in enumerate(x.data.points):
					self.add_autopoint(p.pos+x.position, p.value, p.type if c != 0 else 'instant')

		self.pl_points = None
		self.u_pl_points = False

	def convert____pl_ticks___nopl_points(self):
		self.convert____pl_ticks_____pl_points()
		self.convert____pl_points__nopl_points()

	def convert__nopl_points____pl_points(self):
		#print('--------------')

		if self.u_nopl_points and self.nopl_points.check():
			tres = self.nopl_points.time_ppq
			oldpos = 0
			oldval = 0
			startpos = self.nopl_points.points[0].pos

			outdata = [[startpos, startpos+tres, []]]

			s, e = self.nopl_points.get_durpos()

			for m, point in enumerate(self.nopl_points.iter()):
				difpos = point.pos-oldpos

				diffval = (point.value != oldval) if point.type == 'normal' else False
				dont_split = difpos<tres or diffval

				if not dont_split: outdata.append([point.pos, point.pos+tres, []])
				else: outdata[-1][1] += difpos
				outdata[-1][2].append(point)

				oldpos = point.pos
				oldval = point.value

			for ppl in outdata:
				pl = self.add_pl_points()
				pl.position = ppl[0]
				pl.duration = ppl[1]-pl.position
				for point in ppl[2]:
					autopoint_obj = pl.data.add_point()
					autopoint_obj.pos = point.pos-ppl[0]
					autopoint_obj.value = point.value
					autopoint_obj.type = point.type
					autopoint_obj.tension = point.tension
					autopoint_obj.extra = point.extra
					

		self.u_nopl_points = False
		self.nopl_points = None

	def convert(self, pl_points, nopl_points, pl_ticks, nopl_ticks):

		if_ticks = True in [nopl_ticks, pl_ticks]
		if_points = True in [nopl_points, pl_points]

		if not if_ticks and if_points:
			if (not nopl_ticks):
				if nopl_points:
					self.convert__nopl_ticks___nopl_points()
				elif pl_points:
					self.convert__nopl_ticks_____pl_points()

			if (not pl_ticks):
				if (pl_points, nopl_points) == (True, False):
					self.convert__nopl_points____pl_points()
					self.convert____pl_ticks_____pl_points()
				elif (pl_points, nopl_points) == (True, True):
					self.convert____pl_ticks_____pl_points()
				elif (pl_points, nopl_points) == (False, True):
					self.convert____pl_ticks___nopl_points()





def autopath_encode(autol):
	return ';'.join(autol)

class cvpj_automation:
	def __init__(self, time_ppq, time_float):
		self.data = {}
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.auto_num = counter.counter(200000, 'auto_')

	def debugtxt(self):
		for x, v in self.data.items():
			#pl_points, nopl_points, pl_ticks, nopl_ticks
			#v.convert(True, False, False, False)
			#print(x.ljust(30), '|',int(v.u_pl_points), int(v.u_nopl_points), '|', int(v.u_pl_ticks), int(v.u_nopl_ticks), '|')
			if v.u_pl_points:
				print(x, '- pl_points')
				for d in v.pl_points.iter(): print(d)
			if v.u_nopl_points:
				print(x, '- nopl_points')
				for d in v.nopl_points.iter(): print(d)
			if v.u_pl_ticks:
				print(x, '- pl_ticks')
				for d in v.pl_ticks.iter(): print(d)
			if v.u_nopl_ticks:
				print(x, '- nopl_ticks')
				for d in v.nopl_ticks.iter(): print(d)

	def change_timings(self, time_ppq, time_float):
		for autopath, autodata in self.data.items():
			autodata.change_timings(time_ppq, time_float)
		self.time_ppq = time_ppq
		self.time_float = time_float

	def convert(self, pl_points, nopl_points, pl_ticks, nopl_ticks):
		for autopath, autodata in self.data.items(): 
			autodata.convert(pl_points, nopl_points, pl_ticks, nopl_ticks)



	def create(self, autopath, valtype, replace):
		autopath = autopath_encode(autopath)
		if (autopath not in self.data) or (replace):
			self.data[autopath] = cvpj_s_automation(self.time_ppq, self.time_float, valtype)
			self.data[autopath].id = self.auto_num.get()

	def get(self, autopath, valtype):
		autopath = autopath_encode(autopath)
		if autopath in self.data: return True, self.data[autopath]
		else: return False, cvpj_s_automation(self.time_ppq, self.time_float, valtype)



	def delete(self, autopath):
		autopath = autopath_encode(autopath)
		print('[automation] Auto: Removing', autopath)
		if autopath in self.data: del self.data[autopath]

	def move(self, autopath, to_autopath):
		autopath = autopath_encode(autopath)
		to_autopath = autopath_encode(to_autopath)
		print('[automation] Auto: Moving', autopath, 'to', to_autopath)
		if autopath in self.data: self.data[to_autopath] = self.data.pop(autopath)

	def copy(self, autopath, to_autopath):
		autopath = autopath_encode(autopath)
		to_autopath = autopath_encode(to_autopath)
		print('[automation] Auto: Copying', autopath, 'to', to_autopath)
		if autopath in self.data: self.data[to_autopath] = copy.deepcopy(self.data[autopath])

	def move_group(self, autopath, fval, tval):
		self.move(autopath+[fval], autopath+[tval])



	def calc_div(self, autopath, calcval):
		print('[automation] Auto: Math-Div', autopath)
		autopath = autopath_encode(autopath)
		if autopath in self.data: self.data[autopath].calc_div(calcval)

	def calc_mul(self, autopath, calcval):
		print('[automation] Auto: Math-Mul', autopath)
		autopath = autopath_encode(autopath)
		if autopath in self.data: self.data[autopath].calc_mul(calcval)

	def calc_add(self, autopath, calcval):
		print('[automation] Auto: Math-Add', autopath)
		autopath = autopath_encode(autopath)
		if autopath in self.data: self.data[autopath].calc_add(calcval)

	def calc_note2freq(self, autopath):
		print('[automation] Auto: Math-Note2Freq', autopath)
		autopath = autopath_encode(autopath)
		if autopath in self.data: self.data[autopath].calc_note2freq()

	def calc_addmul(self, autopath, i_add, i_mul):
		print('[automation] Auto: Math-AddMul', autopath)
		autopath = autopath_encode(autopath)
		if autopath in self.data: self.data[autopath].calc_addmul(i_add, i_mul)

	def calc_to_one(self, autopath, i_min, i_max):
		print('[automation] Auto: Math-ToOne', autopath)
		autopath = autopath_encode(autopath)
		if autopath in self.data: self.data[autopath].calc_to_one(i_min, i_max)

	def calc_from_one(self, autopath, i_min, i_max):
		print('[automation] Auto: Math-FromOne', autopath)
		autopath = autopath_encode(autopath)
		if autopath in self.data: self.data[autopath].calc_from_one(i_min, i_max)

	def calc_exp(self, autopath, calcval):
		print('[automation] Auto: Math-Exp', autopath)
		autopath = autopath_encode(autopath)
		if autopath in self.data: self.data[autopath].calc_exp(calcval)

	def calc_exp_r(self, autopath, calcval):
		print('[automation] Auto: Math-ExpR', autopath)
		autopath = autopath_encode(autopath)
		if autopath in self.data: self.data[autopath].calc_exp_r(calcval)

	def calc_log(self, autopath, calcval):
		print('[automation] Auto: Math-Log', autopath)
		autopath = autopath_encode(autopath)
		if autopath in self.data: self.data[autopath].calc_log(calcval)

	def calc_log_r(self, autopath, calcval):
		print('[automation] Auto: Math-LogR', autopath)
		autopath = autopath_encode(autopath)
		if autopath in self.data: self.data[autopath].calc_log_r(calcval)



	def add_autotick(self, autopath, valtype, p_pos, p_val):
		self.create(autopath, valtype, False)
		autopath = autopath_encode(autopath)
		self.data[autopath].add_autotick(p_pos, p_val)

	def add_autopoint(self, autopath, valtype, p_pos, p_val, p_type):
		self.create(autopath, valtype, False)
		autopath = autopath_encode(autopath)
		self.data[autopath].add_autopoint(p_pos, p_val, p_type)

	def add_autopoints_twopoints(self, autopath, valtype, twopoints):
		self.create(autopath, valtype, False)
		autopath = autopath_encode(autopath)
		self.data[autopath].add_autopoints_twopoints(twopoints)

	def add_pl_points(self, autopath, valtype):
		self.create(autopath, valtype, False)
		autopath = autopath_encode(autopath)
		return self.data[autopath].add_pl_points()

	def add_pl_ticks(self, autopath, valtype):
		self.create(autopath, valtype, False)
		autopath = autopath_encode(autopath)
		return self.data[autopath].add_pl_ticks()



	def get_paramval_tick(self, autopath, firstnote, fallback):
		autopath = autopath_encode(autopath)
		out_val = fallback
		if autopath in self.data: 
			out_val = self.data[autopath].get_paramval_tick(firstnote, fallback)
		return out_val

	def iter_nopl_points(self):
		autopath = autopath_encode(autopath)
		for autopath in self.data:
			if self.u_data[autopath].nopl_points != None: 
				yield autopath.split(';'), self.data[autopath].nopl_points

	def iter_nopl_ticks(self):
		autopath = autopath_encode(autopath)
		for autopath in self.data:
			if self.u_data[autopath].nopl_ticks != None: 
				yield autopath.split(';'), self.data[autopath].nopl_ticks

	def iter_pl_points(self):
		autopath = autopath_encode(autopath)
		for autopath in self.data:
			if self.u_data[autopath].pl_points != None: 
				yield autopath.split(';'), self.data[autopath].pl_points





	def get_autopoints(self, autopath):
		autopath = autopath_encode(autopath)
		if autopath in self.data:
			autodata = self.data[autopath]
			if autodata.u_nopl_points: return True, autodata.nopl_points
			else: return False, None
		else: return False, None












