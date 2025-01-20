# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import os
import importlib.util

from functions import data_values
from functions import xtramath
import xml.etree.ElementTree as ET

rapidjson_usable = importlib.util.find_spec('rapidjson')

def make_color_text(color):
	return '|'.join([("%g" % round((x*255), 7)) for x in color])

def text_to_color(color):
	if '#' in color:
		nonumsign = color.lstrip('#')
		return list(int(nonumsign[i:i+2], 16) for i in (0, 2, 4))
	else:
		return [round(float(x)/255, 7) for x in color.split('|')]			

class dataset_visual:
	__slots__ = ['name', 'color']

	def __init__(self, i_visual):
		self.color = None
		self.name = None
		if i_visual: self.read(i_visual)

	def is_used(self):
		return self.name != None or self.color != None

	def read(self, i_visual):
		self.name = i_visual['name'] if 'name' in i_visual else None
		self.color = i_visual['color'] if 'color' in i_visual else None

	def read_xml(self, x_part):
		self.name = x_part.get('name')
		color = x_part.get('color')
		if color: self.color = text_to_color(color)

	def write(self):
		outlist = {}
		if self.color != None: outlist['color'] = self.color
		if self.name != None: outlist['name'] = self.name
		return outlist

	def write_xml(self, xml_data):
		tempxml = ET.SubElement(xml_data, 'visual')
		if self.name: tempxml.set('name', self.name)
		if self.color: tempxml.set('color', make_color_text(self.color))

class dataset_objectset:
	__slots__ = ['data', 'used', 'in_obj']
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
	def adddef(self, p_name):
		if p_name not in self.data:
			self.setused()
			self.data[p_name] = self.in_obj(None) if self.in_obj else None
		return self.data[p_name]
	def remove(self, p_name): 
		if p_name in self.data: del self.data[p_name]
	def get(self, p_name): 
		return self.data[p_name] if p_name in self.data else None
	def __iter__(self): 
		for d in self.data.__iter__(): yield d
	def iter(self): 
		for n, d in self.data.items(): yield n, d
	def write(self): 
		outdict = {}
		for name, paramd in self.data.items(): outdict[name] = paramd.write()
		return outdict

	def write_xml(self, xml_data, objname):
		for name, paramd in self.data.items(): 
			tempxml = ET.SubElement(xml_data, objname)
			tempxml.set('id', name)
			paramd.write_xml(tempxml)

class dataset_param_extplug_assoc:
	__slots__ = ['name','num']
	def __init__(self, i_param):
		self.name = ''
		self.num = -1
		if i_param:
			if 'name' in i_param: self.name = i_param['name']
			if 'num' in i_param: self.num = i_param['num']

	def write(self):
		out_data = {}
		if self.name: out_data['name'] = self.name
		if self.num != -1: out_data['num'] = self.num
		return out_data

	def write_xml(self, xml_data):
		if self.name: xml_data.set('name', self.name)
		if self.num != -1: xml_data.set('num', str(self.num))

class dataset_param_onemath:
	__slots__ = ['type','val']
	def __init__(self, i_param):
		self.type = 'lin'
		self.val = 1
		if i_param: self.read(i_param)

	def read(self, i_param):
		if i_param:
			if 'type' in i_param: self.type = i_param['type']
			if 'val' in i_param: self.val = i_param['val']

	def read_xml(self, xml_data):
		attrib = xml_data.attrib
		if 'type' in attrib: self.type = attrib['type']
		if 'val' in attrib: self.val = float(attrib['val'])

	def is_used(self):
		return self.val != 1 or self.type != 'lin'

	def write(self):
		out_data = {}
		if self.type != 'lin': out_data['type'] = self.type
		if self.val != 1: out_data['val'] = self.val
		return out_data

	def write_xml(self, xml_data):
		if self.type != 'lin': xml_data.set('type', self.type)
		if self.val != 1: xml_data.set('val', str(self.val))

class dataset_param:
	__slots__ = ['noauto','type','defv','min','max','name','num','math_zeroone','extplug_assoc','extplug_paramid']

	def __init__(self, i_param):
		self.noauto = False
		self.type = 'none'
		self.defv = 0
		self.min = 0
		self.max = 1
		self.name = ''
		self.num = -1
		self.extplug_paramid = None
		self.extplug_assoc = None
		self.math_zeroone = dataset_param_onemath(None)
		if i_param: self.load_dict(i_param)

	def load_dict(self, i_param):
		if i_param:
			if 'noauto' in i_param: self.noauto = i_param['noauto']
			if 'type' in i_param: self.type = i_param['type']
			if 'def' in i_param: self.defv = i_param['def']
			if 'min' in i_param: 
				val = i_param['min']
				if val is not None: self.min = float(val)
			if 'max' in i_param: 
				val = i_param['max']
				if val is not None: self.max = float(val)
			if 'name' in i_param: self.name = i_param['name']
			if 'num' in i_param: self.num = i_param['num']
			if 'math_zeroone' in i_param: self.math_zeroone.read(i_param['math_zeroone'])
			if 'extplug_assoc' in i_param: 
				self.extplug_assoc = {}
				for k, v in i_param['extplug_assoc'].items(): 
					self.extplug_assoc[k] = dataset_param_extplug_assoc(v)
			if 'extplug_paramid' in i_param: self.extplug_paramid = i_param['extplug_paramid']

	def read_xml(self, xml_data):
		attrib = xml_data.attrib
		#print(attrib)
		ptype = attrib['type'] if 'type' in attrib else 'float'
		if 'noauto' in attrib: self.noauto = attrib['noauto']=='1'
		if 'type' in attrib: self.type = attrib['type']
		if 'name' in attrib: self.name = attrib['name']
		if 'num' in attrib: self.num = int(attrib['num'])
		if ptype == 'int':
			if 'def' in attrib: self.defv = int(float(attrib['def']))
			if 'min' in attrib: self.min = int(float(attrib['min']))
			if 'max' in attrib: self.max = int(float(attrib['max']))
		if ptype == 'float':
			if 'def' in attrib: self.defv = float(attrib['def'])
			if 'min' in attrib: self.min = float(attrib['min'])
			if 'max' in attrib: self.max = float(attrib['max'])
		if ptype == 'bool':
			if 'def' in attrib: self.defv = bool(int(attrib['def']))
		if ptype == 'string':
			if 'def' in attrib: self.defv = attrib['def']
		if 'ext_id' in attrib: self.extplug_paramid = attrib['ext_id']

		for x_part in xml_data:
			if x_part.tag == 'extplug_assoc':
				partattrib = x_part.attrib
				extplug_assoc_obj = dataset_param_extplug_assoc(None)
				if 'name' in partattrib: extplug_assoc_obj.name = partattrib['name']
				if 'num' in partattrib: extplug_assoc_obj.num = int(partattrib['num'])
				if self.extplug_assoc is None: self.extplug_assoc = {}
				self.extplug_assoc[partattrib['type']] = extplug_assoc_obj
			elif x_part.tag == 'math_zeroone':
				partattrib = x_part.attrib
				math_zeroone_obj = self.math_zeroone
				if 'type' in partattrib: math_zeroone_obj.type = partattrib['type']
				if 'val' in partattrib: math_zeroone_obj.val = float(partattrib['val'])

	def get_def_one(self):
		return xtramath.between_to_one(self.min, self.max, self.defv)

	def add_extplug_assoc(self, k):
		if self.extplug_assoc is None: self.extplug_assoc = {}
		self.extplug_assoc[exttype] = dataset_param_extplug_assoc(None)
		return self.extplug_assoc[exttype]

	def get_extplug_info(self, exttype):
		outname = self.name
		outnum = self.num

		if self.extplug_assoc:
			if exttype in self.extplug_assoc:
				extdata = self.extplug_assoc[exttype]
				if extdata.name: outname = extdata.name
				if extdata.num != -1: outnum = extdata.num
				if extdata.num < -1: outnum = -1

		return outnum, outname

	def write(self):
		out_data = {}
		out_data['type'] = self.type
		if self.name: out_data['name'] = self.name
		if self.defv not in [0, None]: out_data['def'] = self.defv
		if self.type != 'string':
			if self.max not in [1, None]: out_data['max'] = self.max
			if self.min not in [0, None]: out_data['min'] = self.min
		if self.noauto: out_data['noauto'] = self.noauto
		if self.num != -1: out_data['num'] = self.num
		if self.math_zeroone.is_used(): out_data['math_zeroone'] = self.math_zeroone.write()
		if self.extplug_assoc != None: 
			extplug_assoc = out_data['extplug_assoc'] = {}
			for k, v in self.extplug_assoc.items(): 
				extplug_assoc[k] = v.write()
		if self.extplug_paramid != None: out_data['extplug_paramid'] = self.extplug_paramid
		return out_data

	def write_xml(self, xml_data):
		if self.name: xml_data.set('name', str(self.name))
		if self.type: xml_data.set('type', str(self.type))
		if self.defv not in [0, None]: 
			if self.type=='string': xml_data.set('def', str(self.defv))
			elif self.type=='bool': xml_data.set('def', "%g" % int(self.defv))
			elif self.type=='float': xml_data.set('def', "%g" % round(self.defv, 7))
			elif self.type=='list': pass
			else: xml_data.set('def', str(self.defv))
		if self.max not in [1, None]: xml_data.set('max', "%g" % round(self.max, 7))
		if self.min not in [0, None]: xml_data.set('min', "%g" % round(self.min, 7))
		if self.noauto: xml_data.set('noauto', str(int(self.noauto)))
		if self.num not in [-1, None]: xml_data.set('num', str(self.num))
		if self.extplug_paramid != None: xml_data.set('ext_id', str(self.extplug_paramid))
		if self.math_zeroone.is_used(): 
			tempxml = ET.SubElement(xml_data, 'math_zeroone')
			self.math_zeroone.write_xml(tempxml)
		if self.extplug_assoc != None: 
			for k, v in self.extplug_assoc.items(): 
				tempxml = ET.SubElement(xml_data, 'extplug_assoc')
				tempxml.set('type', k)
				v.write_xml(tempxml)

class dataset_drum:
	__slots__ = ['visual']
	def __init__(self, i_drum):
		self.visual = dataset_visual(i_drum['visual'] if 'visual' in i_drum else None) if i_drum else dataset_visual(None)

	def read_xml(self, xml_data):
		for x_part in xml_data:
			if x_part.tag == 'visual': self.visual.read_xml(x_part)

	def write(self):
		outlist = {}
		if self.visual.is_used(): outlist['visual'] = self.visual.write()
		return outlist

	def write_xml(self, xml_data):
		self.visual.write_xml(xml_data)

class dataset_colorset:
	__slots__ = ['value']
	def __init__(self, indata):
		self.value = indata

	def write(self):
		return self.value

	def read_xml(self, xml_data):
		attrib = xml_data.attrib
		self.value = []
		for x_part in xml_data:
			if x_part.tag == 'color':
				self.value.append(text_to_color(x_part.text))

	def write_xml(self, xml_data):
		for color in self.value:
			tempxml = ET.SubElement(xml_data, 'color')
			tempxml.text = make_color_text(color)

class dataset_datadef:
	__slots__ = ['path', 'name', 'struct']
	def __init__(self):
		self.path = None
		self.name = None
		self.struct = None

	def is_used(self): return self.path or self.name or self.struct

	def read(self, i_data):
		if i_data != None: 
			self.path = i_data['path'] if 'path' in i_data else None
			self.name = i_data['name'] if 'name' in i_data else None
			self.struct = i_data['struct'] if 'struct' in i_data else None

	def read_xml(self, xml_data):
		self.path = xml_data.get('path')
		self.name = xml_data.get('name')
		self.struct = xml_data.get('struct')

	def write(self):
		outlist = {}
		if self.path: outlist['path'] = self.path
		if self.name: outlist['name'] = self.name
		if self.struct: outlist['struct'] = self.struct
		return outlist

	def write_xml(self, xml_data):
		tempxml = ET.SubElement(xml_data, 'datadef')
		if self.path is not None: tempxml.set('path',str(self.path))
		if self.name is not None: tempxml.set('name',str(self.name))
		if self.struct is not None: tempxml.set('struct',str(self.struct))

class dataset_dataset_ext:
	__slots__ = ['id', 'category', 'object']
	def __init__(self):
		self.id = None
		self.category = None
		self.object = None

	def is_used(self): return self.id or self.category or self.object

	def read(self, i_data):
		if i_data != None: 
			self.id = i_data['id'] if 'id' in i_data else None
			self.category = i_data['category'] if 'category' in i_data else None
			self.object = i_data['object'] if 'object' in i_data else None

	def read_xml(self, xml_data):
		attrib = xml_data.attrib
		if 'id' in attrib: self.id = attrib['id']
		if 'category' in attrib: self.category = attrib['category']
		if 'object' in attrib: self.object = attrib['object']

	def write(self):
		outlist = {}
		if self.id: outlist['id'] = self.id
		if self.category: outlist['category'] = self.category
		if self.object: outlist['object'] = self.object
		return outlist

	def write_xml(self, xml_data):
		tempxml = ET.SubElement(xml_data, 'dataset_ext')
		if self.id: tempxml.set('id', self.id)
		if self.category: tempxml.set('category', self.category)
		if self.object: tempxml.set('object', self.object)


class dataset_midi:
	__slots__ = ['used', 'bank', 'bank_hi', 'is_drum', 'patch', 'transpose']
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

	def read_xml(self, xml_data):
		attrib = xml_data.attrib
		self.used = True
		if 'bank' in attrib: self.bank = int(attrib['bank'])
		if 'bank_hi' in attrib: self.bank_hi = int(attrib['bank_hi'])
		if 'is_drum' in attrib: self.is_drum = attrib['is_drum']=='1'
		if 'patch' in attrib: self.patch = int(attrib['patch'])
		if 'transpose' in attrib: self.transpose = int(attrib['transpose'])

	def write(self):
		outlist = {}
		outlist['active'] = True
		if self.bank: outlist['bank'] = self.bank
		if self.bank_hi: outlist['bank_hi'] = self.bank_hi
		if self.is_drum: outlist['is_drum'] = self.is_drum
		if self.patch: outlist['patch'] = self.patch
		if self.transpose: outlist['transpose'] = self.transpose
		return outlist

	def write_xml(self, xml_data):
		tempxml = ET.SubElement(xml_data, 'midi')
		if self.bank is not None:
			if self.bank: tempxml.set('bank',str(self.bank))
		if self.bank_hi is not None:
			if self.bank_hi: tempxml.set('bank_hi',str(self.bank_hi))
		if self.is_drum is not None:
			if self.is_drum: tempxml.set('is_drum',str(int(self.is_drum)))
		if self.patch is not None:
			if self.patch: tempxml.set('patch',str(self.patch))
		if self.transpose is not None:
			if self.transpose: tempxml.set('transpose',str(self.transpose))

class dataset_object_extplug_assoc:
	__slots__ = ['vst2_id', 'vst3_id', 'clap_id', 'vst2_name', 'vst3_name', 'clap_name', 'used']
	def __init__(self):
		self.used = False
		self.vst2_id = None
		self.vst3_id = None
		self.clap_id = None
		self.vst2_name = None
		self.vst3_name = None
		self.clap_name = None

	def read_xml(self, xml_data):
		self.used = True
		attrib = xml_data.attrib
		plugtype = attrib['type']
		if plugtype == 'vst2':
			if 'id' in attrib: self.vst2_id = int(attrib['id'])
			if 'name' in attrib: self.vst2_name = attrib['name']
		if plugtype == 'vst3':
			if 'id' in attrib: self.vst3_id = attrib['id']
			if 'name' in attrib: self.vst3_name = attrib['name']
		if plugtype == 'clap':
			if 'id' in attrib: self.clap_id = attrib['id']
			if 'name' in attrib: self.clap_name = attrib['name']

	def read(self, i_data):
		if i_data:
			self.used = True
			if 'vst2_id' in i_data: self.vst2_id = i_data['vst2_id']
			if 'vst3_id' in i_data: self.vst3_id = i_data['vst3_id']
			if 'clap_id' in i_data: self.clap_id = i_data['clap_id']
			if 'vst2_name' in i_data: self.vst2_name = i_data['vst2_name']
			if 'vst3_name' in i_data: self.vst3_name = i_data['vst3_name']
			if 'clap_name' in i_data: self.clap_name = i_data['clap_name']

	def write(self):
		out_data = {}
		if self.vst2_id: out_data['vst2_id'] = self.vst2_id
		if self.vst3_id: out_data['vst3_id'] = self.vst3_id
		if self.clap_id: out_data['clap_id'] = self.clap_id
		if self.vst2_name: out_data['vst2_name'] = self.vst2_name
		if self.vst3_name: out_data['vst3_name'] = self.vst3_name
		if self.clap_name: out_data['clap_name'] = self.clap_name
		return out_data

	def write_xml(self, xml_data):
		if self.vst2_id or self.vst2_name:
			tempxml = ET.SubElement(xml_data, 'extplug_assoc')
			tempxml.set('type', 'vst2')
			if self.vst2_id: tempxml.set('id', str(self.vst2_id))
			if self.vst2_name: tempxml.set('name', self.vst2_name)
		if self.vst3_id or self.vst3_name:
			tempxml = ET.SubElement(xml_data, 'extplug_assoc')
			tempxml.set('type', 'vst3')
			if self.vst3_id: tempxml.set('id', self.vst3_id)
			if self.vst3_name: tempxml.set('name', self.vst3_name)
		if self.clap_id or self.clap_name:
			tempxml = ET.SubElement(xml_data, 'extplug_assoc')
			tempxml.set('type', 'clap')
			if self.clap_id: tempxml.set('id', self.clap_id)
			if self.clap_name: tempxml.set('name', self.clap_name)


class dataset_object:
	__slots__ = ['visual', 'data', 'params', 'drumset', 'datadef', 'dataset_ext', 'midi', 'extplug_assoc']
	def __init__(self, i_object):
		self.visual = dataset_visual(None)
		self.data = {}
		self.params = dataset_objectset(dataset_param)
		self.drumset = dataset_objectset(dataset_drum)
		self.datadef = dataset_datadef()
		self.dataset_ext = dataset_dataset_ext()
		self.midi = dataset_midi()
		self.extplug_assoc = dataset_object_extplug_assoc()
		if i_object: self.load_dict(i_object)

	def read_xml(self, xml_data):
		for x_part in xml_data:
			cat_id = x_part.get('id')
			if x_part.tag == 'param':
				param_obj = self.params.create(cat_id)
				param_obj.read_xml(x_part)
			elif x_part.tag == 'data':
				partattrib = x_part.attrib
				for k, v in partattrib.items():
					self.data[k] = v
			elif x_part.tag == 'datadef': self.datadef.read_xml(x_part)
			elif x_part.tag == 'visual': self.visual.read_xml(x_part)
			elif x_part.tag == 'midi': self.midi.read_xml(x_part)
			elif x_part.tag == 'drumset':
				drumset_obj = self.drumset.create(cat_id)
				drumset_obj.read_xml(x_part)
			elif x_part.tag == 'extplug_assoc': self.extplug_assoc.read_xml(x_part)
			elif x_part.tag == 'dataset_ext': self.dataset_ext.read_xml(x_part)

	def load_dict(self, i_object):
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
				if name not in ['visual','data','params','drumset','datadef_struct','datadef_name','datadef','extplug_assoc','dataset_ext','midi']: 
					self.data[name] = var
			if 'extplug_assoc' in i_object:
				self.extplug_assoc.read(i_object['extplug_assoc'])
				if 'extplug_assoc' in self.data: del self.data['extplug_assoc']
			if 'dataset_ext' in i_object:
				self.dataset_ext.read(i_object['dataset_ext'])
				if 'dataset_ext' in self.data: del self.data['dataset_ext']

	def write(self):
		outlist = {}
		if self.data: outlist['data'] = self.data
		if self.datadef.is_used(): outlist['datadef'] = self.datadef.write()
		if self.midi.used: outlist['midi'] = self.midi.write()
		if self.drumset.used: outlist['drumset'] = self.drumset.write()
		if self.params.used: outlist['params'] = self.params.write()
		if self.visual.is_used(): outlist['visual'] = self.visual.write()
		if self.extplug_assoc.used: outlist['extplug_assoc'] = self.extplug_assoc.write()
		if self.dataset_ext.is_used(): outlist['dataset_ext'] = self.dataset_ext.write()
		return outlist

	def write_xml(self, xml_data):
		if self.data:
			tempxml = ET.SubElement(xml_data, 'data')
			for k,v in self.data.items(): tempxml.set(k,str(v))
		if self.datadef.is_used(): self.datadef.write_xml(xml_data)
		if self.dataset_ext.is_used(): self.dataset_ext.write_xml(xml_data)
		if self.midi.used: self.midi.write_xml(xml_data)
		if self.drumset.used: self.drumset.write_xml(xml_data, 'drumset')
		if self.visual.is_used(): self.visual.write_xml(xml_data)
		if self.extplug_assoc.used: self.extplug_assoc.write_xml(xml_data)
		if self.params.used: self.params.write_xml(xml_data, 'param')

	def var_get(self, v_name):
		return self.data[v_name] if v_name in self.data else None

	def var_set(self, v_name, v_value):
		if v_value != None: self.data[v_name] = v_value

def midid_to_num(i_bank, i_patch, i_isdrum): return i_bank*256 + i_patch + int(i_isdrum)*128
def midid_from_num(value): return (value>>8), (value%128), int(bool(value&0b10000000))

class dataset_group:
	__slots__ = ['visual']
	def __init__(self, i_group):
		self.visual = dataset_visual(None)
		if i_group: self.load_dict(i_group)

	def load_dict(self, i_group):
		self.visual = dataset_visual(i_group['visual'] if 'visual' in i_group else None)

	def read_xml(self, xml_data):
		for x_part in xml_data:
			if x_part.tag == 'visual': self.visual.read_xml(x_part)

	def write(self):
		outlist = {}
		if self.visual.is_used(): outlist['visual'] = self.visual.write()
		return outlist

	def write_xml(self, xml_data):
		self.visual.write_xml(xml_data)

class dataset_category:
	def __init__(self, i_category):
		self.cache_ids_vst2 = {}
		self.cache_ids_vst3 = {}
		self.cache_ids_clap = {}
		self.colorset = dataset_objectset(dataset_colorset)
		self.groups = dataset_objectset(dataset_group)
		self.objects = dataset_objectset(dataset_object)
		self.ext_dataset_ids = {}
		if i_category: self.load_dict(i_category)

	def load_dict(self, i_category):
		if 'ext_dataset_ids' in i_category: self.ext_dataset_ids = i_category['ext_dataset_ids']
		if 'colorset' in i_category: self.colorset.read(i_category['colorset'])
		if 'groups' in i_category: self.groups.read(i_category['groups'])
		if 'objects' in i_category: 
			self.objects.read(i_category['objects'])
			for n, x in self.objects.iter():
				extassoc = x.extplug_assoc
				if extassoc.vst2_id: self.cache_ids_vst2[extassoc.vst2_id] = n
				if extassoc.vst3_id: self.cache_ids_vst3[extassoc.vst3_id] = n
				if extassoc.clap_id: self.cache_ids_clap[extassoc.clap_id] = n

		if 'midi_to' in i_category: 
			for objname, midiinst in i_category['midi_to'].items():
				objd = self.objects.get(objname)
				if not objd: objd = self.objects.create(objname)
				i_bank, i_patch, i_isdrum = midid_from_num(midiinst)
				objd.midi.used = True
				objd.midi.is_drum = midiinst == 128
				objd.midi.patch = midiinst%128

	def read_xml(self, xml_data):
		for x_part in xml_data:
			cat_id = x_part.get('id')
			if x_part.tag == 'group':
				object_obj = self.groups.create(cat_id)
				object_obj.read_xml(x_part)
			if x_part.tag == 'object':
				object_obj = self.objects.create(cat_id)
				object_obj.read_xml(x_part)
				extassoc = object_obj.extplug_assoc
				if extassoc.vst2_id: self.cache_ids_vst2[extassoc.vst2_id] = cat_id
				if extassoc.vst3_id: self.cache_ids_vst3[extassoc.vst3_id] = cat_id
				if extassoc.clap_id: self.cache_ids_clap[extassoc.clap_id] = cat_id
			if x_part.tag == 'colorset':
				object_obj = self.colorset.create(cat_id)
				object_obj.read_xml(x_part)

	def write(self):
		outdata = {}
		if self.colorset.used: outdata['colorset'] = self.colorset.write()
		if self.groups.used: outdata['groups'] = self.groups.write()
		if self.objects.used: outdata['objects'] = self.objects.write()
		if self.ext_dataset_ids: outdata['ext_dataset_ids'] = self.ext_dataset_ids
		return outdata

	def write_xml(self, xml_data, name):
		tempxml = ET.SubElement(xml_data, "category")
		tempxml.set('id', name)
		for k, v in self.ext_dataset_ids.items():
			pathxml = ET.SubElement(tempxml, 'external_path')
			pathxml.set('id', k)
			pathxml.text = v
		if self.colorset.used: self.colorset.write_xml(tempxml, 'colorset')
		if self.groups.used: self.groups.write_xml(tempxml, 'group')
		if self.objects.used: self.objects.write_xml(tempxml, 'object')

class dataset:
	def __init__(self, in_dataset):
		self.categorys = {}
		self.category_list = []
		if in_dataset != None:
			if os.path.exists(in_dataset): self.load_file(in_dataset)

	def load_file_json(self, in_dataset):
		self.categorys = {}
		self.category_list = []
		f = open(in_dataset, "r")
		if rapidjson_usable:
			import rapidjson
			dataset = rapidjson.load(f)
		else:
			dataset = json.load(f)

		for x, d in dataset.items():
			self.categorys[x] = dataset_category(d)
			self.category_list.append(x)

	def load_file(self, input_file):
		self.categorys = {}
		self.category_list = []
		parser = ET.XMLParser()
		xml_data = ET.parse(input_file, parser).getroot()
		for x_part in xml_data:
			cat_id = x_part.get('id')
			if x_part.tag == 'category':
				cat_obj = self.categorys[cat_id] = dataset_category(None)
				cat_obj.read_xml(x_part)

	def write(self, filename):
		f = open(filename, "w")
		outjson = {}

		for n, c in self.categorys.items():
			outjson[n] = c.write()

		if rapidjson_usable:
			import rapidjson
			f.write(rapidjson.dumps(outjson, indent=4))
		else:
			f.write(json.dumps(outjson, indent=4))
		
	def write_xml(self, filename):
		xml_proj = ET.Element("dataset")

		for n, c in self.categorys.items():
			c.write_xml(xml_proj, n)

		outfile = ET.ElementTree(xml_proj)
		ET.indent(outfile, space="    ", level=0)
		outfile.write(filename)

	def category_add(self, c_name):
		if c_name not in self.categorys: 
			self.categorys[c_name] = dataset_category(None)
			self.category_list.append(c_name)
		return self.categorys[c_name]

	def category_del(self, c_name):
		if c_name in self.categorys: 
			del self.categorys[c_name]
			self.category_list.remove(c_name)
			return True
		else:
			return False
