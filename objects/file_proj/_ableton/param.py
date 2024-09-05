# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj._ableton.automation import *
from objects.file_proj._ableton.func import *
from objects.file_proj._ableton.samplepart import *

from functions import data_values
import xml.etree.ElementTree as ET

verbose = False

excludenames =  ['LomId', 'LomIdView', 'IsExpanded', 'On', 
'ModulationSourceCount', 'ParametersListWrapper', 'Pointee', 
'LastSelectedTimeableIndex', 'LastSelectedClipEnvelopeIndex', 
'LastPresetRef', 'LockedScripts', 'IsFolded', 'ShouldShowPresetName', 
'UserName', 'Annotation', 'SourceContext', 'OverwriteProtectionNumber']

class ableton_Param:
	__slots__ = ['name','Manual','AutomationTarget','ModulationTarget','MidiCCOnOffThresholds','MidiControllerRange','type','exists']
	def __init__(self, xmltag, n, t):
		self.exists = False
		self.name = n
		self.Manual = 0
		self.AutomationTarget = ableton_ReceiveTarget(None, 'AutomationTarget')
		self.ModulationTarget = ableton_ReceiveTarget(None, 'ModulationTarget')
		self.MidiCCOnOffThresholds = [64,127]
		self.MidiControllerRange = None
		self.type = t

		if xmltag:
			x_Params = xmltag.findall(self.name)
			if x_Params:
				self.exists = True
				x_Param = x_Params[0]
				if self.type == 'bool': self.Manual = get_bool(x_Param, 'Manual', False)
				if self.type == 'int': self.Manual = int(get_value(x_Param, 'Manual', 0))
				if self.type == 'float': self.Manual = float(get_value(x_Param, 'Manual', 0))
				xm_MidiCCOnOffThresholds = x_Param.findall('MidiCCOnOffThresholds')
				xm_MidiControllerRange = x_Param.findall('MidiControllerRange')

				self.AutomationTarget = ableton_ReceiveTarget(x_Param, 'AutomationTarget')
				self.ModulationTarget = ableton_ReceiveTarget(x_Param, 'ModulationTarget')

				if xm_MidiControllerRange:
					self.MidiControllerRange = [0,1]
					self.MidiControllerRange[0] = float(get_value(xm_MidiControllerRange[0], 'Min', 64))
					self.MidiControllerRange[1] = float(get_value(xm_MidiControllerRange[0], 'Max', 127))

				if xm_MidiCCOnOffThresholds:
					self.MidiCCOnOffThresholds[0] = int(get_value(xm_MidiCCOnOffThresholds[0], 'Min', 64))
					self.MidiCCOnOffThresholds[1] = int(get_value(xm_MidiCCOnOffThresholds[0], 'Max', 127))

	def __float__(self):
		return float(self.Manual)

	def __int__(self):
		return int(self.Manual)
		
	def __bool__(self):
		return bool(float(self.Manual))

	def setvalue(self, value):
		self.exists = True
		self.Manual = value

	def write(self, xmltag):
		if self.exists:
			x_Param = ET.SubElement(xmltag, self.name)
			add_value(x_Param, 'LomId', 0)
			add_value(x_Param, 'Manual', ['false','true'][int(self.Manual)] if self.type == 'bool' else str(self.Manual))
			if self.MidiControllerRange:
				x_MidiControllerRange = ET.SubElement(x_Param, "MidiControllerRange")
				add_value(x_MidiControllerRange, 'Min', self.MidiControllerRange[0])
				add_value(x_MidiControllerRange, 'Max', self.MidiControllerRange[1])
			self.AutomationTarget.write(x_Param)
			self.ModulationTarget.write(x_Param)
			if self.type == 'bool':
				x_MidiCCOnOffThresholds = ET.SubElement(x_Param, "MidiCCOnOffThresholds")
				add_value(x_MidiCCOnOffThresholds, 'Min', self.MidiCCOnOffThresholds[0])
				add_value(x_MidiCCOnOffThresholds, 'Max', self.MidiCCOnOffThresholds[1])

class ableton_parampart:
	__slots__ = ['type','value','groupname','name']
	def __init__(self):
		self.type = None
		self.value = None
		self.groupname = None
		self.name = None

	def getval(self):
		if self.type == 'value': 
			try: return float(self.value)
			except: return self.value
		if self.type == 'param': return float(self.value)
		if self.type == 'bool': return self.value
		if self.type == 'buffer': return self.value

	def __str__(self):
		return str(self.getval())

	def __float__(self):
		return float(self.getval())

	def __int__(self):
		return int(self.getval())
		
	def __bool__(self):
		return bool(float(self.getval()))

	@classmethod
	def as_bool(cls, name, valuetxt):
		outobj = cls()
		outobj.name = name
		outobj.type = 'bool'
		outobj.value = valuetxt
		return outobj

	@classmethod
	def as_value(cls, name, valuetxt):
		outobj = cls()
		outobj.name = name
		outobj.type = 'value'
		outobj.value = valuetxt
		return outobj

	@classmethod
	def as_param(cls, name, paramtype, value):
		outobj = cls()
		outobj.name = name
		outobj.type = 'param'
		outobj.value = ableton_Param(None, name, paramtype)
		outobj.value.setvalue(value)
		return outobj

	@classmethod
	def as_buffer(cls, name, valuetxt):
		outobj = cls()
		outobj.name = name
		outobj.type = 'buffer'
		outobj.value = valuetxt
		return outobj

	@classmethod
	def as_sampleref(cls, name):
		outobj = cls()
		outobj.name = name
		outobj.type = 'sampleref'
		outobj.value = ableton_SampleRef(None)
		return outobj

	@classmethod
	def as_sampleparts(cls, name):
		outobj = cls()
		outobj.groupname = name
		outobj.type = 'sampleparts'
		outobj.value = {}
		return outobj

	@classmethod
	def as_numset(cls, name):
		outobj = cls()
		outobj.groupname = name
		outobj.type = 'numset'
		outobj.value = {}
		return outobj.value

	def detect(self, xmlin, xmltag):
		self.name = xmlin.tag
		valuetxt = xmlin.get('Value')
		isparam = xmlin.findall('Manual')
		out = None
		txtdata = '' if xmlin.text == None else xmlin.text.strip()
		if valuetxt != None:
			if valuetxt in ['true', 'false']: 
				self.type = 'bool'
				self.value = valuetxt=='true'
			else:
				self.type = 'value'
				self.value = valuetxt
			if verbose: paramprint('VALUE', xmlin.tag)

		elif isparam:
			if verbose: paramprint('PARAM', xmlin.tag)
			i_Param = isparam[0]
			Manual = i_Param.get('Value')

			if Manual in ['true', 'false']: paramtype = 'bool'
			elif '.' in Manual: paramtype = 'float'
			else: paramtype = 'int'
			self.type = 'param'
			self.value = ableton_Param(xmltag, self.name, paramtype)
		elif txtdata:
			if verbose: paramprint('BUFFER', xmlin.tag)
			hextxt = xmlin.text.replace('\t', '').replace('\n', '')
			self.type = 'buffer'
			self.value = bytes.fromhex(hextxt)
		elif xmlin.tag == 'SampleRef':
			if verbose: paramprint('SAMPLEREF', xmlin.tag)
			self.type = 'sampleref'
			self.value = ableton_SampleRef(xmltag)
		else:
			is_numset = True if xmlin else False
			ids = [xmlpart.get('Id') for xmlpart in xmlin]
			tags = [xmlpart.tag for xmlpart in xmlin]

			is_numset = (None not in ids)
			if not is_numset:
				if verbose: paramprint('GROUP', xmlin.tag)
				groupdata = ableton_paramset()
				groupdata.scan(xmlin)
				self.type = 'group'
				self.value = groupdata
				self.groupname = xmlin.tag
			else:
				out = {}
				if verbose: paramprint('NUMSET', xmlin.tag)

				issamplepart = False
				if tags:
					if all(tags) and tags[0]=='MultiSamplePart':
						issamplepart = True

				if not issamplepart:
					for xmlpart in xmlin: 
						Id = int(xmlpart.get('Id'))
						attribdata = xmlpart.attrib.copy()
						del attribdata['Id']
						numdata = ableton_paramset()
						numdata.attr = attribdata
						numdata.name = xmlpart.tag
						numdata.scan(xmlpart)
						out[Id] = numdata
					self.type = 'numset'
					self.value = out
					self.groupname = xmlin.tag
				else:
					sampleparts = {}
					for xmlpart in xmlin: 
						Id = int(xmlpart.get('Id'))
						sampleparts[Id] = ableton_MultiSamplePart(xmlpart)
					self.type = 'sampleparts'
					self.value = sampleparts
					self.groupname = xmlin.tag

	def create(self, xmltag, numset):
		if self.type == 'param': self.value.write(xmltag)
		if self.type == 'value': add_value(xmltag, self.name, self.value)
		if self.type == 'bool': add_bool(xmltag, self.name, self.value)
		if self.type == 'group': 
			if numset:
				xmld = ET.SubElement(xmltag, self.groupname)
				self.value.create(xmld)
			else:
				self.value.create(xmltag)
		if self.type == 'numset': 
			xmlg = ET.SubElement(xmltag, self.groupname)
			for x, v in self.value.items():
				xmlp = ET.SubElement(xmlg, v.name)
				xmlp.attrib['Id'] = str(x)
				for f, d in v.attr.items(): xmlp.set(f, d)
				#xmlp.attrib |= v.attr
				v.create(xmlp)
		if self.type == 'buffer': 
			xmlg = ET.SubElement(xmltag, self.name)
			xmlg.text = '\n'
			for num in range((len(self.value)/40).__ceil__()):
				xmlg.text += self.value[num*40:(num+1)*40].hex().upper()+'\n'

		if self.type == 'sampleref': self.value.write(xmltag)

		if self.type == 'sampleparts': 
			xmlg = ET.SubElement(xmltag, self.groupname)
			for x, v in self.value.items():
				xmlp = ET.SubElement(xmlg, 'MultiSamplePart')
				xmlp.attrib['Id'] = str(x)
				v.write(xmlp)

class ableton_paramset:
	__slots__ = ['name','data','nocreate','attr']
	def __init__(self):
		self.name = ''
		self.attr = {}
		self.data = {}
		self.nocreate = True

	def __float__(self):
		return float(self.Manual)

	def scan(self, xmltag):
		for xmlpart in xmltag:
			if xmlpart.tag not in excludenames:
				parampart = ableton_parampart()
				parampart.detect(xmlpart, xmltag)
				self.data[xmlpart.tag] = parampart

	def get_all_keys_internal(self, npath, out_data):
		for key, part in self.data.items():
			if part.type == 'group':
				part.value.get_all_keys_internal(npath+[key], out_data)
			elif part.type == 'numset':
				numdata = {}
				for n, p in part.value.items(): 
					numdata[str(n)+'/'+p.name] = p.get_all_keys([])
				out_data['/'.join(npath+[key])] = numdata
			else:
				out_data['/'.join(npath+[key])] = part

	def get_all_keys(self, npath):
		out_data = {}
		self.get_all_keys_internal(npath, out_data)
		return out_data

	def import_keys_f_internal(self, in_data, paramdata):
		for n, v in in_data.items():
			if not isinstance(v, dict): 
				paramdata[n] = v
			else:
				outval = paramdata[n] = ableton_parampart()
				outval.type = 'group'
				outval.value = ableton_paramset()
				outval.groupname = n
				self.import_keys_f_internal(v, outval.value.data)

	def import_keys(self, in_data):
		self.data = {}
		predata = {}
		foldereddata = {}

		for n, v in in_data.items(): 
			in_path = n.split('/')
			isnumset = isinstance(v, dict)

			#print(isnumset, in_path, v)

			if not isnumset: outval = v
			else: 
				outval = ableton_parampart()
				outval.type = 'numset'
				outval.groupname = in_path[-1]
				outval.value = {}
				for ns_n, ns_v in v.items():
					ns_num, ns_name = ns_n.split('/')
					ns_ps = outval.value[int(ns_num)] = ableton_paramset()
					ns_ps.name = ns_name
					ns_ps.import_keys(ns_v)

			predata[n] = outval

		for n, v in predata.items(): 
			data_values.dict__nested_add_value(foldereddata, n.split('/'), v)
		del predata

		self.import_keys_f_internal(foldereddata, self.data)

	def create(self, xmltag):
		#out_data = self.get_all_keys([])
		#self.import_keys(out_data)

		for n, v in self.data.items():
			v.create(xmltag, self.nocreate)

	def __getitem__(self, name):
		return self.data[name]

