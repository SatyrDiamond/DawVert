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
	'pitch': 'Pitch',

	'amount': 'Amount',
	'attack': 'Attack',
	'bits': 'Bits',
	'decay': 'Decay',
	'delay': 'Delay',
	'floor': 'Floor',
	'freq': 'Freq',
	'gain': 'Gain',
	'hold': 'Hold',
	'post': 'Post',
	'pre': 'Pre',
	'pregain': 'Pregain',
	'ratio': 'Ratio',
	'release': 'Release',
	'threshold': 'Threshold',
	'wet': 'Wet',
}

def fixval(p_type, p_value):
	if p_type == 'float': return float(p_value)
	elif p_type == 'int': return int(float(p_value))
	elif p_type == 'bool': return bool(p_value)
	elif p_type == 'string': return str(p_value)
	else: return p_value

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

class cvpj_param_enum_part:
	def __init__(self):
		self.num = 0
		self.id = ''
		self.name = None

class cvpj_param_unit:
	def __init__(self):
		self.current = None
		self.custom_calc = []

	def outcalc(self, unit_org, unit_targ):
		outd = [unit_org, unit_targ]
		if outd==None: 
			if unit_targ=="decibel": return [['to_db']]

		elif  outd == ["volume", "decibel"]:                return [['to_db']]

		elif  outd == ["time:ms", "time:seconds"]:          return [['div', 10]]
		elif  outd == ["time:ms", "time:samples"]:          return [['mul', 44.100]]
		elif  outd == ["time:seconds", "time:ms"]:          return [['mul', 1000]]
		elif  outd == ["time:seconds", "time:samples"]:     return [['mul', 44100]]
		elif  outd == ["time:samples", "time:ms"]:          return [['div', 44100*1000]]
		elif  outd == ["time:samples", "time:seconds"]:     return [['div', 44100]]

		elif  outd == ["freq:midikey", "freq:hz"]:          return [['midi2freq']]
		elif  outd == ["freq:hz", "freq:midikey"]:          return [['freq2midi']]

		elif  outd == ["pitch:cents", "pitch:semitones"]:   return [['div', 100]]
		elif  outd == ["pitch:cents", "pitch:octave"]:      return [['div', 1200]]
		elif  outd == ["pitch:semitones", "pitch:cents"]:   return [['mul', 100]]
		elif  outd == ["pitch:semitones", "pitch:octave"]:  return [['div', 12]]
		elif  outd == ["pitch:octave", "pitch:cents"]:      return [['mul', 1200]]
		elif  outd == ["pitch:octave", "pitch:semitones"]:  return [['mul', 12]]

class cvpj_param:
	__slots__ = ['value','type','min','max','range_defined','visual','found','unit','is_enum','enum_max','enum_parts','enum_end_point']
	def __init__(self, p_value, p_type):
		self.value = p_value
		self.type = p_type
		self.range_defined = False
		self.min = 0
		self.max = 1
		self.visual = visual.cvpj_visual()
		self.found = True
		self.unit = cvpj_param_unit()
		self.is_enum = False
		self.enum_max = 0
		self.enum_parts = []
		self.enum_end_point = 'end'

	def add_enum_part(self, num, idv):
		self.is_enum = True
		self.enum_max = max(num, self.enum_max)
		enum_part = cvpj_param_enum_part()
		enum_part.num = num
		enum_part.id = idv
		return enum_part

	def add_data(self, **kwargs):
		if 'name' in kwargs: param_visname = kwargs['name']
		elif p_id in visname: param_visname = visname[p_id]
		else: param_visname = p_id
		self.visual.name = param_visname
		if 'minmax' in kwargs:
			self.min, self.max = kwargs['minmax']
			self.range_defined = True
		elif 'max' in kwargs:
			self.min = 0
			self.max = kwargs['max']
			self.range_defined = True
		if 'unit' in kwargs: self.unit.current = kwargs['unit']

	def add_minmax(self, i_min, i_max):
		self.min, self.max = i_min, i_max
		self.range_defined = True

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

	def __contains__(self, x):
		return self.list().__contains__(x)

	def move(self, dest_paramset, p_id):
		if p_id in self.paramset: 
			dest_paramset.paramset[p_id] = copy.deepcopy(self.paramset[p_id])
			del self.paramset[p_id]

	def copy(self, dest_paramset, p_id):
		if p_id in self.paramset: 
			dest_paramset.paramset[p_id] = copy.deepcopy(self.paramset[p_id])

	def add(self, p_id, p_value, p_type):
		p_value = fixval(p_type, p_value)
		self.paramset[p_id] = cvpj_param(p_value, p_type)
		self.paramset[p_id].visual.name = visname[p_id] if p_id in visname else p_id
		return self.paramset[p_id]

	def add_named(self, p_id, p_value, p_type, p_name):
		p_value = fixval(p_type, p_value)
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
		return param_obj, (cvpj_obj.automation[autopath] if autopath in cvpj_obj.automation else None)

	def debugtxt(self):
		for x in self.paramset:
			print(x, '|', self.paramset[x].value, self.paramset[x].visual.name )
