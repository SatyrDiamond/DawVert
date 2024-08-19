# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import os

from functions import data_values

class dataset_visual:
	def __init__(self, i_visual):
		if i_visual:
			self.name = i_visual['name'] if 'name' in i_visual else None
			self.color = i_visual['color'] if 'color' in i_visual else None
		else:
			self.color = None
			self.name = None

	def is_used(self):
		return self.name != None or self.color != None

	def write(self):
		outlist = {}
		if self.color != None: outlist['color'] = self.color
		if self.name != None: outlist['name'] = self.name
		return outlist

	def read(self, i_visual):
		if i_visual != None: 
			self.name = i_visual['name'] if 'name' in i_visual else None
			self.color = i_visual['color'] if 'color' in i_visual else None

class dataset_objectset:
	def __init__(self, in_obj):
		self.data = {}
		self.used = False
		self.in_obj = in_obj

	def read(self, indata): 
		self.used = True
		for name, idata in indata.items():
			self.data[name] = self.in_obj(idata) if self.in_obj else idata

	def list(self): 
		return data_values.list__fancysort([x for x in self.data])
	def setused(self): self.used = True
	def create(self, p_name): 
		self.setused()
		self.data[p_name] = self.in_obj(None) if self.in_obj else None
		return self.data[p_name]
	def remove(self, p_name): 
		if p_name in self.data: del self.data[p_name]
	def get(self, p_name): 
		return self.data[p_name] if p_name in self.data else None
	def iter(self): 
		for n, d in self.data.items(): yield n, d
	def write(self): 
		outdict = {}
		for name, paramd in self.data.items(): outdict[name] = paramd.write()
		return outdict

class dataset_param:
	__slots__ = ['noauto','type','defv','min','max','name']

	def __init__(self, i_param):
		self.noauto = False
		self.type = 'none'
		self.defv = 0
		self.min = 0
		self.max = 1
		self.name = ''
		if i_param:
			if 'noauto' in i_param: self.noauto = i_param['noauto']
			if 'type' in i_param: self.type = i_param['type']
			if 'def' in i_param: self.defv = i_param['def']
			if 'min' in i_param: self.min = i_param['min']
			if 'max' in i_param: self.max = i_param['max']
			if 'name' in i_param: self.name = i_param['name']

	def write(self):
		out_data = {}
		out_data['def'] = self.defv
		if self.max != 1: out_data['max'] = self.max
		if self.min != 0: out_data['min'] = self.min
		if self.name: out_data['name'] = self.name
		if self.noauto: out_data['noauto'] = self.noauto
		out_data['type'] = self.type
		return out_data

class dataset_drum:
	def __init__(self, i_drum):
		self.visual = dataset_visual(i_drum['visual'] if 'visual' in i_drum else None) if i_drum else dataset_visual(None)

	def write(self):
		outlist = {}
		if self.visual.is_used(): outlist['visual'] = self.visual.write()
		return outlist

class dataset_value:
	def __init__(self, indata):
		self.value = indata

	def write(self):
		return self.value

class dataset_datadef:
	def __init__(self):
		self.path = None
		self.name = None
		self.struct = None

	def is_used(self): return self.path and self.name and self.struct

	def read(self, i_data):
		if i_data != None: 
			self.path = i_data['path'] if 'path' in i_data else None
			self.name = i_data['name'] if 'name' in i_data else None
			self.struct = i_data['struct'] if 'struct' in i_data else None

	def write(self):
		outlist = {}
		if self.path: outlist['path'] = self.path
		if self.name: outlist['name'] = self.name
		if self.struct: outlist['struct'] = self.struct
		return outlist

class dataset_midi:
	def __init__(self):
		self.used = False
		self.bank = 0
		self.bank_hi = 0
		self.is_drum = False
		self.patch = 0
		self.transpose = 0

	def read(self, i_data):
		if i_data != None: 
			self.used = True
			if 'bank' in i_data: self.bank = i_data['bank']
			if 'bank_hi' in i_data: self.bank_hi = i_data['bank_hi']
			if 'is_drum' in i_data: self.is_drum = i_data['is_drum']
			if 'patch' in i_data: self.patch = i_data['patch']
			if 'transpose' in i_data: self.transpose = i_data['transpose']

	def write(self):
		outlist = {}
		outlist['active'] = True
		if self.bank: outlist['bank'] = self.bank
		if self.bank_hi: outlist['bank_hi'] = self.bank_hi
		if self.is_drum: outlist['is_drum'] = self.is_drum
		if self.patch: outlist['patch'] = self.patch
		if self.transpose: outlist['transpose'] = self.transpose
		return outlist

class dataset_object:
	def __init__(self, i_object):
		self.visual = dataset_visual(None)
		self.data = {}
		self.params = dataset_objectset(dataset_param)
		self.drumset = dataset_objectset(dataset_drum)
		self.datadef = dataset_datadef()
		self.midi = dataset_midi()
		if i_object:
			self.visual = dataset_visual(i_object['visual'] if 'visual' in i_object else None)
			self.data = i_object['data'] if 'data' in i_object else {}
			if 'params' in i_object: self.params.read(i_object['params'])
			if 'midi' in i_object: self.midi.read(i_object['midi'])
			if 'drumset' in i_object: self.drumset.read(i_object['drumset'])
			if 'datadef' in i_object: 
				ddd = i_object['datadef']
				if isinstance(ddd, dict): self.datadef.read(ddd)
				else: self.datadef.path = ddd
			if 'datadef_name' in i_object: self.datadef.name = i_object['datadef_name']
			if 'datadef_struct' in i_object: self.datadef.struct = i_object['datadef_struct']
			for name, var in i_object.items():
				if name not in ['visual','data','params','drumset','datadef_struct','datadef_name','datadef']: self.data[name] = var

	def write(self):
		outlist = {}
		if self.data: outlist['data'] = self.data
		if self.datadef.is_used(): outlist['datadef'] = self.datadef.write()
		if self.midi.used: outlist['midi'] = self.midi.write()
		if self.drumset.used: outlist['drumset'] = self.drumset.write()
		if self.params.used: outlist['params'] = self.params.write()
		if self.visual.is_used(): outlist['visual'] = self.visual.write()
		return outlist

	def var_get(self, v_name):
		return self.data[v_name] if v_name in self.data else None
	def var_set(self, v_name, v_value):
		if v_value != None: self.data[v_name] = v_value

def midid_to_num(i_bank, i_patch, i_isdrum): return i_bank*256 + i_patch + int(i_isdrum)*128
def midid_from_num(value): return (value>>8), (value%128), int(bool(value&0b10000000))

class dataset_group:
	def __init__(self, i_group):
		self.visual = dataset_visual(None)
		if i_group:
			self.visual = dataset_visual(i_group['visual'] if 'visual' in i_group else None)

	def write(self):
		outlist = {}
		if self.visual.is_used(): outlist['visual'] = self.visual.write()
		return outlist

class dataset_category:
	def __init__(self, i_category):
		self.colorset = dataset_objectset(dataset_value)
		self.midi_to = dataset_objectset(dataset_value)
		self.groups = dataset_objectset(dataset_group)
		self.objects = dataset_objectset(dataset_object)
		if i_category:
			if 'colorset' in i_category: self.colorset.read(i_category['colorset'])
			if 'groups' in i_category: self.groups.read(i_category['groups'])
			if 'objects' in i_category: self.objects.read(i_category['objects'])

			if 'midi_to' in i_category: 
				for objname, midiinst in i_category['midi_to'].items():

					objd = self.objects.get(objname)
					if not objd: objd = self.objects.create(objname)

					i_bank, i_patch, i_isdrum = midid_from_num(midiinst)

					objd.midi.used = True
					objd.midi.is_drum = midiinst == 128
					objd.midi.patch = midiinst%128


	def write(self):
		outdata = {}
		if self.midi_to.used: outdata['midi_to'] = self.midi_to.write()
		if self.colorset.used: outdata['colorset'] = self.colorset.write()
		if self.groups.used: outdata['groups'] = self.groups.write()
		if self.objects.used: outdata['objects'] = self.objects.write()
		return outdata



class dataset:
	def __init__(self, in_dataset):
		self.categorys = {}
		self.category_list = []
		if in_dataset != None:
			if os.path.exists(in_dataset):
				f = open(in_dataset, "r")
				dataset = json.load(f)
				for x, d in dataset.items():
					self.categorys[x] = dataset_category(d)
					self.category_list.append(x)

	def write(self, filename):
		f = open(filename, "w")
		outjson = {}

		for n, c in self.categorys.items():
			outjson[n] = c.write()

		f.write(json.dumps(outjson, indent=4))

	def category_add(self, c_name):
		if c_name not in self.categorys: 
			self.categorys[c_name] = dataset_category(None)
			self.category_list.append(c_name)

	def category_del(self, c_name):
		if c_name in self.categorys: 
			del self.categorys[c_name]
			self.category_list.remove(c_name)
			return True
		else:
			return False
