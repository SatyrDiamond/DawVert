# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import copy

from objects import counter
from functions import note_data
from objects.convproj import autoticks
from objects.convproj import autopoints
from objects.convproj import placements_autopoints
from objects.convproj import placements_autoticks

import logging
logger_automation = logging.getLogger('automation')

class cvpj_s_automation:
	__slots__ = ['pl_points','pl_ticks','nopl_points','nopl_ticks','id','u_pl_points','u_pl_ticks','u_nopl_points','u_nopl_ticks','time_float','valtype','time_ppq','time_float','valtype','conv_tres']
	def __init__(self, time_ppq, time_float, valtype):
		self.pl_points = None
		self.pl_ticks = None
		self.nopl_points = None
		self.nopl_ticks = None
		self.id = ''
		self.conv_tres = 1

		self.u_pl_points = False
		self.u_pl_ticks = False
		self.u_nopl_points = False
		self.u_nopl_ticks = False

		self.time_ppq = time_ppq
		self.time_float = time_float
		self.valtype = valtype

	def __repr__(self):
		outtxt = ''
		if self.u_pl_points: outtxt += 'pl_points '
		if self.u_pl_ticks: outtxt += 'pl_ticks '
		if self.u_nopl_points: outtxt += 'nopl_points '
		if self.u_nopl_ticks: outtxt += 'nopl_ticks '

		return 'AutoSet '+ outtxt

	def merge(self, other):
		other = copy.deepcopy(other)
		other.change_timings(self.time_ppq, self.time_float)

		if not self.u_pl_points:
			self.u_pl_points = other.u_pl_points
			self.pl_points = other.pl_points

		if not self.u_pl_ticks:
			self.u_pl_ticks = other.u_pl_ticks
			self.pl_ticks = other.pl_ticks

		if not self.u_nopl_points:
			self.u_nopl_points = other.u_nopl_points
			self.nopl_points = other.nopl_points
		else:
			self.u_nopl_ticks = True
			self.nopl_points.merge(other.nopl_points)

		if not self.u_nopl_ticks:
			self.u_nopl_ticks = other.u_nopl_ticks
			self.nopl_ticks = other.nopl_ticks
		else:
			self.u_nopl_ticks = True
			self.nopl_ticks.merge(other.nopl_ticks)


	def sort(self):
		if self.u_pl_points: self.pl_points.sort()

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

	def calc(self, mathtype, val1, val2, val3, val4):
		if self.u_nopl_points: self.nopl_points.calc(mathtype, val1, val2, val3, val4)
		if self.u_nopl_ticks: self.nopl_ticks.calc(mathtype, val1, val2, val3, val4)
		if self.u_pl_points: self.pl_points.calc(mathtype, val1, val2, val3, val4)
		if self.u_pl_ticks: self.pl_ticks.calc(mathtype, val1, val2, val3, val4)

	def add_autotick(self, p_pos, p_val):
		self.make_nopl_ticks()
		self.nopl_ticks.add_point(p_pos, p_val)

	def add_autopoint(self, p_pos, p_val, p_type):
		self.make_nopl_points()
		autopoint_obj = self.nopl_points.add_point()
		autopoint_obj.pos = p_pos
		autopoint_obj.value = p_val
		autopoint_obj.type = p_type

	def add_autopoint_real(self, p_pos, p_val, p_type):
		self.make_nopl_points()
		autopoint_obj = self.nopl_points.add_point()
		autopoint_obj.pos_real = p_pos
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

	def change_seconds(self, is_seconds, bpm, ppq):
		if self.u_nopl_points: self.nopl_points.change_seconds(is_seconds, bpm, ppq)
		
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
				pl.time.position = x
				pl.time.duration = pl_dur

		self.nopl_ticks = None
		self.u_nopl_ticks = False

	def convert__nopl_ticks___nopl_points(self):
		if self.u_nopl_ticks:
			points_out = self.nopl_ticks.to_points(8*self.conv_tres)

			for x in points_out:
				self.add_autopoint(x[0], x[1], 'normal' if x[2] else 'instant')

		self.nopl_ticks = None
		self.u_nopl_ticks = False

	def convert____pl_ticks_____pl_points(self):

		if self.u_pl_ticks:
			for x in self.pl_ticks:
				pl = self.add_pl_points()
				pl.time = x.time.copy()
				pl.muted = x.muted
				pl.visual = x.visual
				points_out = x.data.to_points(8*self.conv_tres)
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
			for x in self.pl_points:
				x.remove_cut()
				for c, p in enumerate(x.data.points):
					self.add_autopoint(p.pos+x.time.position, p.value, p.type if c != 0 else 'instant')
				

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

			for m, point in enumerate(self.nopl_points):
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
				pl.time.position = ppl[0]
				pl.time.duration = ppl[1]-pl.time.position

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

class cvpj_autoloc:
	def __init__(self, indata):
		if isinstance(indata, list): self.autoloc = indata
		elif isinstance(indata, str): self.autoloc = indata.split(';')
		else: self.autoloc = []

	def __eq__(self, other):
		if isinstance(other, list): return self.autoloc==other
		elif isinstance(other, str): return self.__str__()==other
		elif isinstance(other, cvpj_autoloc): return self.autoloc==other.autoloc
		else: return False

	def __str__(self):
		return ';'.join(self.autoloc)

	def __repr__(self):
		return ';'.join(self.autoloc)

	def __hash__(self):
		return self.__str__().__hash__()

	def __setitem__(self, p, v):
		self.autoloc[p] = v

	def __getitem__(self, p):
		return self.autoloc[p]

	def get_list(self):
		return self.autoloc

	def startswith(self, inlist):
		return self.autoloc[0:len(inlist)]==inlist if inlist else False

	def change_start(self, startlen, listin):
		self.autoloc = listin+self.autoloc[startlen:]

class cvpj_automation:
	__slots__ = ['data','time_ppq','time_float','auto_num','movenotfound','calcnotfound']
	def __init__(self, time_ppq, time_float):
		self.data = {}
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.auto_num = counter.counter(200000, 'auto_')
		self.movenotfound = []
		self.calcnotfound = []

	def __setitem__(self, p, v):
		autoloc = cvpj_autoloc(p)
		self.autoloc[autoloc] = v

	def attempt_after(self):
		for autopath, mathtype, val1, val2, val3, val4 in self.calcnotfound:
			if autopath in self.data: 
				self.data[autopath].calc(mathtype, val1, val2, val3, val4)

		for autopath, to_autopath in self.movenotfound:
			if autopath in self.data: 
				logger_automation.info('Moving '+str(autopath)+' to '+str(to_autopath))
				self.data[to_autopath] = self.data.pop(autopath)

	def list(self):
		return list(self.data)

	def sort(self):
		for x, v in self.data.items():
			v.sort()

	def debugtxt(self):
		for x, v in self.data.items():
			#pl_points, nopl_points, pl_ticks, nopl_ticks
			#v.convert(True, False, False, False)
			#print(x.ljust(30), '|',int(v.u_pl_points), int(v.u_nopl_points), '|', int(v.u_pl_ticks), int(v.u_nopl_ticks), '|')
			if v.u_pl_points:
				print(x, '- pl_points')
				for d in v.pl_points: print(d)
			if v.u_nopl_points:
				print(x, '- nopl_points')
				for d in v.nopl_points: print(d)
			if v.u_pl_ticks:
				print(x, '- pl_ticks')
				for d in v.pl_ticks: print(d)
			if v.u_nopl_ticks:
				print(x, '- nopl_ticks')
				for d in v.nopl_ticks: print(d)

	def change_timings(self, time_ppq, time_float):
		for autopath, autodata in self.data.items():
			autodata.change_timings(time_ppq, time_float)
		self.time_ppq = time_ppq
		self.time_float = time_float

	def change_seconds(self, is_seconds, bpm, ppq):
		for autopath, autodata in self.data.items():
			autodata.change_seconds(is_seconds, bpm, ppq)

	def convert(self, pl_points, nopl_points, pl_ticks, nopl_ticks):
		for autopath, autodata in self.data.items(): 
			autodata.convert(pl_points, nopl_points, pl_ticks, nopl_ticks)

	def create(self, autopath, valtype, replace):
		autopath = cvpj_autoloc(autopath)
		if (autopath not in self.data) or (replace):
			self.data[autopath] = cvpj_s_automation(self.time_ppq, self.time_float, valtype)
			self.data[autopath].id = self.auto_num.get()
			if autopath == ['main', 'bpm']:
				self.data[autopath].conv_tres = 8

	def get(self, autopath, valtype):
		autopath = cvpj_autoloc(autopath)
		if autopath in self.data: return True, self.data[autopath]
		else: return False, cvpj_s_automation(self.time_ppq, self.time_float, valtype)

	def pop_f(self, autopath):
		autopath = ';'.join(autopath)
		if autopath in self.data: 
			outauto = self.data[autopath]
			del self.data[autopath]
			return outauto
		else: 
			return None

	def delete(self, autopath):
		autopath = cvpj_autoloc(autopath)
		logger_automation.info('Removing '+str(autopath))
		if autopath in self.data: del self.data[autopath]

	def move(self, autopath, to_autopath):
		autopath = cvpj_autoloc(autopath)
		to_autopath = cvpj_autoloc(to_autopath)

		if autopath in self.data: 
			logger_automation.info('Moving '+str(autopath)+' to '+str(to_autopath))
			if to_autopath not in self.data:
				self.data[to_autopath] = self.data.pop(autopath)
			else:
				self.data[to_autopath].merge(self.data.pop(autopath))
		else:
			self.movenotfound.append([autopath, to_autopath])
			logger_automation.debug('(not found) Moving '+str(autopath)+' to '+str(to_autopath))

	def copy(self, autopath, to_autopath):
		autopath = cvpj_autoloc(autopath)
		to_autopath = cvpj_autoloc(to_autopath)
		if autopath in self.data: 
			logger_automation.info('Copying '+str(autopath)+' to '+str(to_autopath))
			self.data[to_autopath] = copy.deepcopy(self.data[autopath])
			self.data[to_autopath].id = self.auto_num.get()
		else:
			logger_automation.debug('(not found) Copying '+str(autopath)+' to '+str(to_autopath))

	def move_group(self, autopath, fval, tval):
		self.move(autopath+[fval], autopath+[tval])

	def move_everything(self, locset_from, locset_to):
		logger_automation.info('Moving all from '+';'.join(locset_from)+' to '+';'.join(locset_to))
		foundparts = [x for x in self.list() if x.startswith(locset_from)]
		for autopath in foundparts:
			autopart = self.pop_f(autopath)
			autopath.change_start(len(locset_from), locset_to)
			self.data[autopath] = autopart

	def copy_everything(self, locset_from, locset_to):
		logger_automation.info('Coping all from '+';'.join(locset_from)+' to '+';'.join(locset_to))
		foundparts = [x for x in self.list() if x.startswith(locset_from)]
		for autopath in foundparts:
			if autopath in self.data:
				autopoints = self.data[autopath]
				newpath = copy.deepcopy(autopath)
				newpath.change_start(len(locset_from), locset_to)
				self.data[newpath] = autopoints

	def calc(self, autopath, mathtype, val1, val2, val3, val4):
		autopath = cvpj_autoloc(autopath)
		logger_automation.info('Math '+str(autopath))
		if autopath in self.data:
			self.data[autopath].calc(mathtype, val1, val2, val3, val4)
		else:
			self.calcnotfound.append([autopath, mathtype, val1, val2, val3, val4])



	def add_autotick(self, autopath, valtype, p_pos, p_val):
		self.create(autopath, valtype, False)
		autopath = cvpj_autoloc(autopath)
		self.data[autopath].add_autotick(p_pos, p_val)

	def add_autopoint(self, autopath, valtype, p_pos, p_val, p_type):
		self.create(autopath, valtype, False)
		autopath = cvpj_autoloc(autopath)
		self.data[autopath].add_autopoint(p_pos, p_val, p_type)

	def add_autopoint_real(self, autopath, valtype, p_pos, p_val, p_type):
		self.create(autopath, valtype, False)
		autopath = cvpj_autoloc(autopath)
		self.data[autopath].add_autopoint_real(p_pos, p_val, p_type)

	def add_autopoints_twopoints(self, autopath, valtype, twopoints):
		self.create(autopath, valtype, False)
		autopath = cvpj_autoloc(autopath)
		self.data[autopath].add_autopoints_twopoints(twopoints)

	def add_pl_points(self, autopath, valtype):
		self.create(autopath, valtype, False)
		autopath = cvpj_autoloc(autopath)
		return self.data[autopath].add_pl_points()

	def add_pl_ticks(self, autopath, valtype):
		self.create(autopath, valtype, False)
		autopath = cvpj_autoloc(autopath)
		return self.data[autopath].add_pl_ticks()

	def get_paramval_tick(self, autopath, firstnote, fallback):
		autopath = cvpj_autoloc(autopath)
		out_val = fallback
		if autopath in self.data: 
			out_val = self.data[autopath].get_paramval_tick(firstnote, fallback)
		return out_val

	def iter_nopl_points(self, **kwargs):
		locfilter = kwargs['filter'] if 'filter' in kwargs else []
		for autopath, autodata in self.data.items():
			if autodata.u_nopl_points != None and (autopath.startswith(locfilter) if locfilter else True): 
				yield autopath, autodata.nopl_points

	def iter_nopl_ticks(self, **kwargs):
		locfilter = kwargs['filter'] if 'filter' in kwargs else []
		for autopath, autodata in self.data.items():
			if autodata.u_nopl_ticks != None and (autopath.startswith(locfilter) if locfilter else True): 
				yield autopath, autodata.nopl_ticks

	def iter_pl_points(self, **kwargs):
		locfilter = kwargs['filter'] if 'filter' in kwargs else []
		for autopath, autodata in self.data.items():
			if autodata.u_pl_points != None and (autopath.startswith(locfilter) if locfilter else True): 
				yield autopath, autodata.pl_points

	def get_autopoints(self, autopath):
		autopath = cvpj_autoloc(autopath)
		if autopath in self.data:
			autodata = self.data[autopath]
			if autodata.u_nopl_points: return True, autodata.nopl_points
			else: return False, None
		else: return False, None


	def iter_nopl_points_external(self, pluginid):
		for autoloc, autodata in self.iter_nopl_points(filter=['plugin', pluginid]):
			paramname = autoloc[-1]
			if paramname.startswith('ext_param_'):
				paramnum = int(paramname[10:])
				yield autoloc, autodata, paramnum

	def iter_pl_points_external(self, pluginid):
		for autoloc, autodata in self.iter_pl_points(filter=['plugin', pluginid]):
			paramname = autoloc[-1]
			if paramname.startswith('ext_param_'):
				paramnum = int(paramname[10:])
				yield autoloc, autodata, paramnum











