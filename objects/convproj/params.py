# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import copy

from objects.convproj import visual
from objects.convproj import automation

visname = {
	'bpm': 'Tempo',
	'vol': 'Volume',
	'pan': 'Pan',
	'solo': 'Solo',
	'enabled': 'On',
	'pitch': 'Pitch'
}

class cvpj_datavals:
	__slots__ = ['data']
	def __init__(self): self.data = {}
	def add(self, i_name, i_value): self.data[i_name] = i_value
	def add_if_missing(self, i_name, i_value): 
		if i_name not in self.data: self.data[i_name] = i_value
	def get(self, i_name, fallbackval): return self.data[i_name] if i_name in self.data else fallbackval
	def pop(self, i_name, fallbackval): 
		if i_name in self.data:
			outval = self.data[i_name]
			del self.data[i_name]
			return outval
		else:
			return fallbackval
	def list(self): return [x for x in self.data]
	def remove(self, i_name): 
		if i_name in self.data: del self.data[i_name]
	def match(self, i_name, i_value): return (self.data[i_name] == i_value) if i_name in self.data else False

	def clear(self): self.data = {}
	def debugtxt(self):
		for x in self.data:
			print(x, '|', self.data[x] )

class cvpj_param:
	__slots__ = ['value','type','min','max','visual','found']
	def __init__(self, p_value, p_type):
		self.value = p_value
		self.type = p_type
		self.min = 0
		self.max = 1
		self.visual = visual.cvpj_visual()
		self.found = True
	
	def __int__(self): return int(self.value)

	def __float__(self): return float(self.value)

	def __bool__(self): return bool(self.value)

	def __str__(self): return str(self.value)

class cvpj_paramset:
	__slots__ = ['paramset']
	def __init__(self):
		self.paramset = {}

	def __bool__(self):
		return bool(self.paramset)

	def move(self, other_paramset, p_id):
		if p_id in self.paramset: 
			other_paramset.paramset[p_id] = copy.deepcopy(self.paramset[p_id])
			del self.paramset[p_id]

	def copy(self, other_paramset, p_id):
		if p_id in self.paramset: 
			other_paramset.paramset[p_id] = copy.deepcopy(self.paramset[p_id])

	def add(self, p_id, p_value, p_type):
		if p_type == 'float': p_value = float(p_value)
		if p_type == 'int': p_value = int(float(p_value))
		if p_type == 'bool': p_value = bool(p_value)
		if p_type == 'string': p_value = p_value
		self.paramset[p_id] = cvpj_param(p_value, p_type)
		self.paramset[p_id].visual.name = visname[p_id] if p_id in visname else p_id
		return self.paramset[p_id]

	def add_named(self, p_id, p_value, p_type, p_name):
		if p_type == 'float': p_value = float(p_value)
		if p_type == 'int': p_value = int(float(p_value))
		if p_type == 'bool': p_value = bool(p_value)
		if p_type == 'string': p_value = p_value
		self.paramset[p_id] = cvpj_param(p_value, p_type)
		self.paramset[p_id].visual.name = p_name if p_name else p_id
		return self.paramset[p_id]

	def add_minmax(self, p_id, i_min, i_max):
		if p_id in self.paramset: self.paramset[p_id].min, self.paramset[p_id].max = i_min, i_max

	def get(self, p_id, fallbackval):
		if p_id in self.paramset:
			return self.paramset[p_id]
		else: 
			outparam = cvpj_param(fallbackval, 'float')
			outparam.found = False
			return outparam

	def pop(self, p_id, fallbackval): 
		if p_id in self.paramset:
			outparam = self.paramset[p_id]
			del self.paramset[p_id]
			return outparam
		else: 
			outparam = cvpj_param(fallbackval, 'float')
			outparam.found = False
			return outparam

	def add_minmax(self, p_id, i_min, i_max):
		return (self.paramset[p_id].min, self.paramset[p_id].max) if p_id in self.paramset else (0, 1)

	def list(self):
		return [x for x in self.paramset]

	def remove(self, p_id):
		if p_id in self.paramset: del self.paramset[p_id]

	def clear(self):
		self.paramset = {}

	def get_auto(self, p_id, fallbackval, cvpj_obj, autopath):
		param_obj = self.get(p_id, fallbackval)
		autopath = automation.cvpj_autoloc(autopath+[p_id])
		if autopath in cvpj_obj.automation: 
			return param_obj, cvpj_obj.automation[autopath]
		else: 
			return param_obj, None

	def debugtxt(self):
		for x in self.paramset:
			print(x, '|', self.paramset[x].value, self.paramset[x].visual.name )
