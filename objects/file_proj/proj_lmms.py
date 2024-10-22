# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import zlib
from functions import data_values
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

def is_float(inval):
	if isinstance(inval, bool):
		return False
	elif isinstance(inval, int):
		return True
	elif isinstance(inval, float):
		return True
	else:
		try: return float(inval)
		except ValueError: return False

def findfirst(xmldata, name):
	found = xmldata.findall(name)
	if found: return found[0]
	else: return None

def get_xml_tree(path):
	with open(path, 'rb') as file:
		try:
			file.seek(4)
			data = zlib.decompress(file.read())
			return ET.fromstring(data)

		except zlib.error:
			return ET.parse(path).getroot()

class lmms_param:
	def __init__(self, name, value):
		self.name = name
		self.value = value
		self.expanded = False
		self.is_sync = False
		self.sync_denominator = 4
		self.sync_numerator = 4
		self.sync_mode = 0
		self.scale_type = None
		self.id = None

	def __int__(self):
		return int(float(self.value)) if is_float(self.value) else 0

	def __float__(self):
		return float(self.value) if is_float(self.value) else 0.0

	def __bool__(self):
		return bool(float(self.value) if is_float(self.value) else 0)

	def __str__(self):
		return str(self.value)

	def read(self, xmldata):
		noauto = xmldata.get(self.name)
		sync_denom = xmldata.get(self.name+'_denominator')
		sync_num = xmldata.get(self.name+'_numerator')
		sync_mode = xmldata.get(self.name+'_syncmode')

		if sync_num or sync_denom or sync_mode:
			self.is_sync = True
			if sync_num: self.sync_denominator = int(sync_num)
			if sync_denom: self.sync_numerator = int(sync_denom)
			if sync_mode: self.sync_mode = int(sync_mode)

		if noauto != None: 
			self.value = noauto
		else:
			vardata = findfirst(xmldata, self.name)

			if vardata != None:
				a_value = vardata.get('value')

				self.expanded = True
				a_value = vardata.get('value')
				a_scale_type = vardata.get('scale_type')
				a_id = vardata.get('id')
				if a_id:
					self.automated = True
					self.id = int(a_id)
				self.value = a_value
				self.scale_type = a_scale_type



	def write(self, xmldata):
		if not self.expanded: xmldata.set(self.name, str(self.value))
		else:
			tempxml = ET.SubElement(xmldata, self.name)
			tempxml.set('value', str(self.value))
			if self.scale_type: tempxml.set('scale_type', str(self.scale_type))
			if self.id: tempxml.set('id', str(self.id))
		if self.is_sync:
			xmldata.set(self.name+'_denominator', str(self.sync_denominator))
			xmldata.set(self.name+'_numerator', str(self.sync_numerator))
			xmldata.set(self.name+'_syncmode', str(self.sync_mode))

class lmms_automationpattern:
	def __init__(self):
		self.pos = 0
		self.mute = 0
		self.len = 0
		self.prog = 0
		self.tens = 0
		self.name = ''
		self.color = ''

		self.auto_points = {}
		self.auto_target = []

	def read(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'pos': self.pos = int(v)
			if n == 'mute': self.mute = int(v)
			if n == 'len': self.len = int(v)
			if n == 'prog': self.prog = int(v)
			if n == 'tens': self.tens = float(v)
			if n == 'name': self.name = v
			if n == 'color': self.color = v

		for xmlpart in xmldata:
			if xmlpart.tag == 'time': self.auto_points[int(xmlpart.get('pos'))] = float(xmlpart.get('value'))
			if xmlpart.tag == 'object': self.auto_target.append(int(xmlpart.get('id')))

	def write(self, xmldata, name):
		tempxml = ET.SubElement(xmldata, name)
		tempxml.set('pos', str(self.pos))
		tempxml.set('mute', str(self.mute))
		tempxml.set('len', str(self.len))
		tempxml.set('prog', str(self.prog))
		tempxml.set('tens', str(self.tens))
		tempxml.set('name', self.name)
		if self.color: tempxml.set('color', self.color)
		for p_pos, p_val in self.auto_points.items():
			timexml = ET.SubElement(tempxml, 'time')
			timexml.set('pos', str(p_pos))
			timexml.set('value', str(p_val))

		for val in self.auto_target:
			targetxml = ET.SubElement(tempxml, 'object')
			targetxml.set('id', str(val))

class lmms_note:
	__slots__ = ['vol','pos','key','len','pan','auto']
	def __init__(self):
		self.vol = 100
		self.pos = 0
		self.key = 0
		self.len = 0
		self.pan = 0
		self.auto = {}

	def read(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'vol': self.vol = int(v)
			if n == 'pos': self.pos = int(v)
			if n == 'key': self.key = int(v)
			if n == 'len': self.len = int(v)
			if n == 'pan': self.pan = int(v)

		for xmlpart in xmldata:
			if xmlpart.tag == 'automationpattern':
				for subxml in xmlpart:
					auto_obj = lmms_automationpattern()
					auto_obj.read(subxml)
					self.auto[subxml.tag] = auto_obj

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'note')
		tempxml.set('vol', str(self.vol))
		tempxml.set('pos', str(self.pos))
		tempxml.set('key', str(self.key))
		tempxml.set('len', str(self.len))
		tempxml.set('pan', str(self.pan))
		if self.auto:
			automationpatternxml = ET.SubElement(tempxml, 'automationpattern')
			for name, auto_obj in self.auto.items():
				auto_obj.write(automationpatternxml, name)

class lmms_pattern:
	def __init__(self):
		self.type = 1
		self.steps = 16
		self.pos = 0
		self.muted = 0
		self.name = ''
		self.color = ''
		self.notes = []

	def read(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'type': self.type = int(v)
			if n == 'steps': self.steps = int(v)
			if n == 'pos': self.pos = int(v)
			if n == 'muted': self.muted = int(v)
			if n == 'name': self.name = v
			if n == 'color': self.color = v

		for xmlpart in xmldata:
			if xmlpart.tag == 'note':
				note_obj = lmms_note()
				note_obj.read(xmlpart)
				self.notes.append(note_obj)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'pattern')
		tempxml.set('type', str(self.type))
		tempxml.set('steps', str(self.steps))
		tempxml.set('pos', str(self.pos))
		tempxml.set('muted', str(self.muted))
		tempxml.set('name', self.name)
		if self.color: tempxml.set('color', self.color)

		for note_obj in self.notes:
			note_obj.write(tempxml)

class lmms_arpeggiator:
	def __init__(self):
		self.arp = lmms_param('arp', 0)
		self.arpmiss = lmms_param('arpmiss', 0)
		self.arptime = lmms_param('arptime', 100)
		self.arpdir = lmms_param('arpdir', 0)
		self.arpskip = lmms_param('arpskip', 0)
		self.arprange = lmms_param('arprange', 1)
		self.arp_enabled = lmms_param('arp-enabled', 0)
		self.arpgate = lmms_param('arpgate', 100)
		self.arpmode = lmms_param('arpmode', 0)
		self.arpcycle = lmms_param('arpcycle', 0)

	def read(self, xmldata):
		self.arp.read(xmldata)
		self.arpmiss.read(xmldata)
		self.arptime.read(xmldata)
		self.arpdir.read(xmldata)
		self.arpskip.read(xmldata)
		self.arprange.read(xmldata)
		self.arp_enabled.read(xmldata)
		self.arpgate.read(xmldata)
		self.arpmode.read(xmldata)
		self.arpcycle.read(xmldata)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'arpeggiator')
		self.arp.write(tempxml)
		self.arpmiss.write(tempxml)
		self.arptime.write(tempxml)
		self.arpdir.write(tempxml)
		self.arpskip.write(tempxml)
		self.arprange.write(tempxml)
		self.arp_enabled.write(tempxml)
		self.arpgate.write(tempxml)
		self.arpmode.write(tempxml)
		self.arpcycle.write(tempxml)
		
class lmms_chordcreator:
	def __init__(self):
		self.chord_enabled = lmms_param('chord-enabled', 0)
		self.chord = lmms_param('chord', 0)
		self.chordrange = lmms_param('chordrange', 0)

	def read(self, xmldata):
		self.chord_enabled.read(xmldata)
		self.chord.read(xmldata)
		self.chordrange.read(xmldata)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'chordcreator')
		self.chord_enabled.write(tempxml)
		self.chord.write(tempxml)
		self.chordrange.write(tempxml)
		
class lmms_midiport:
	def __init__(self):
		self.inputchannel = 0
		self.fixedoutputnote = -1
		self.outputchannel = 1
		self.fixedinputvelocity = -1
		self.fixedoutputvelocity = -1
		self.basevelocity = 63
		self.outputprogram = 1
		self.readable = 0
		self.outputcontroller = 0
		self.inputcontroller = 0
		self.writable = 0

	def read(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'inputchannel': self.inputchannel = int(v)
			if n == 'fixedoutputnote': self.fixedoutputnote = int(v)
			if n == 'outputchannel': self.outputchannel = int(v)
			if n == 'fixedinputvelocity': self.fixedinputvelocity = int(v)
			if n == 'fixedoutputvelocity': self.fixedoutputvelocity = int(v)
			if n == 'basevelocity': self.basevelocity = int(v)
			if n == 'outputprogram': self.outputprogram = int(v)
			if n == 'readable': self.readable = int(v)
			if n == 'outputcontroller': self.outputcontroller = int(v)
			if n == 'inputcontroller': self.inputcontroller = int(v)
			if n == 'writable': self.writable = int(v)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'midiport')
		tempxml.set('inputchannel', str(self.inputchannel))
		tempxml.set('fixedoutputnote', str(self.fixedoutputnote))
		tempxml.set('outputchannel', str(self.outputchannel))
		tempxml.set('fixedinputvelocity', str(self.fixedinputvelocity))
		tempxml.set('fixedoutputvelocity', str(self.fixedoutputvelocity))
		tempxml.set('basevelocity', str(self.basevelocity))
		tempxml.set('outputprogram', str(self.outputprogram))
		tempxml.set('readable', str(self.readable))
		tempxml.set('outputcontroller', str(self.outputcontroller))
		tempxml.set('inputcontroller', str(self.inputcontroller))
		tempxml.set('writable', str(self.writable))
		
class lmms_elpart:
	def __init__(self, name):
		self.name = name
		self.amt = lmms_param('amt', 0)
		self.att = lmms_param('att', 0)
		self.ctlenvamt = lmms_param('ctlenvamt', 0)
		self.dec = lmms_param('dec', 0.5)
		self.hold = lmms_param('hold', 0.5)
		self.lamt = lmms_param('lamt', 0)
		self.latt = lmms_param('latt', 0)
		self.lpdel = lmms_param('lpdel', 0)
		self.lshp = lmms_param('lshp', 0)
		self.lspd = lmms_param('lspd', 0.1)
		self.pdel = lmms_param('pdel', 0)
		self.rel = lmms_param('rel', 0.1)
		self.sustain = lmms_param('sustain', 0.5)
		self.userwavefile = ''
		self.x100 = lmms_param('x100', 0)

	def read(self, xmldata):
		self.dec.read(xmldata)
		self.sustain.read(xmldata)
		self.pdel.read(xmldata)
		self.rel.read(xmldata)
		self.lamt.read(xmldata)
		self.lshp.read(xmldata)
		self.userwavefile = xmldata.attrib['userwavefile'] if 'userwavefile' in xmldata.attrib else ''
		self.lspd.read(xmldata)
		self.x100.read(xmldata)
		self.amt.read(xmldata)
		self.lpdel.read(xmldata)
		self.hold.read(xmldata)
		self.latt.read(xmldata)
		self.att.read(xmldata)
		self.ctlenvamt.read(xmldata)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, self.name)
		self.dec.write(tempxml)
		self.sustain.write(tempxml)
		self.pdel.write(tempxml)
		self.rel.write(tempxml)
		self.lamt.write(tempxml)
		self.lshp.write(tempxml)
		tempxml.set('userwavefile', self.userwavefile)
		self.lspd.write(tempxml)
		self.x100.write(tempxml)
		self.amt.write(tempxml)
		self.lpdel.write(tempxml)
		self.hold.write(tempxml)
		self.latt.write(tempxml)
		self.att.write(tempxml)
		self.ctlenvamt.write(tempxml)

class lmms_eldata:
	def __init__(self):
		self.fwet = lmms_param('fwet', 0)
		self.ftype = lmms_param('ftype', 0)
		self.fres = lmms_param('fres', 0.5)
		self.fcut = lmms_param('fcut', 14000)
		self.elvol = lmms_elpart('elvol')
		self.elcut = lmms_elpart('elcut')
		self.elres = lmms_elpart('elres')

	def read(self, xmldata):
		self.fwet.read(xmldata)
		self.ftype.read(xmldata)
		self.fres.read(xmldata)
		self.fcut.read(xmldata)

		for xmlpart in xmldata:
			if xmlpart.tag == 'elvol': self.elvol.read(xmlpart)
			if xmlpart.tag == 'elcut': self.elcut.read(xmlpart)
			if xmlpart.tag == 'elres': self.elres.read(xmlpart)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'eldata')
		self.fwet.write(tempxml)
		self.ftype.write(tempxml)
		self.fres.write(tempxml)
		self.fcut.write(tempxml)
		self.elvol.write(tempxml)
		self.elcut.write(tempxml)
		self.elres.write(tempxml)

class lmms_effect:
	def __init__(self):
		self.name = ''
		self.autoquit = lmms_param('autoquit', 1)
		self.gate = lmms_param('gate', 0)
		self.on = lmms_param('on', 1)
		self.wet = lmms_param('wet', 1)
		self.plugin = lmms_plugin()
		self.keys = {}

	def read(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'name': self.name = v

		self.autoquit.read(xmldata)
		self.gate.read(xmldata)
		self.on.read(xmldata)
		self.wet.read(xmldata)

		for xmlpart in xmldata:
			if xmlpart.tag == 'key':
				for subxml in xmlpart:
					if subxml.tag == 'attribute': self.keys[subxml.get('name')] = subxml.get('value')
			else:
				self.plugin.read(xmlpart)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'effect')
		self.wet.write(tempxml)
		self.autoquit.write(tempxml)
		self.gate.write(tempxml)
		self.on.write(tempxml)
		tempxml.set('name', self.name)
		self.plugin.write(tempxml)
		keys_xml = ET.SubElement(tempxml, 'key')
		for n, v in self.keys.items():
			attribute_xml = ET.SubElement(keys_xml, 'attribute')
			attribute_xml.set('value', str(v))
			attribute_xml.set('name', str(n))

class lmms_fxchain:
	def __init__(self):
		self.enabled = lmms_param('enabled', 1)
		self.effects = []

	def read(self, xmldata):
		self.enabled.read(xmldata)

		for xmlpart in xmldata:
			if xmlpart.tag == 'effect':
				effect_obj = lmms_effect()
				effect_obj.read(xmlpart)
				self.effects.append(effect_obj)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'fxchain')
		tempxml.set('numofeffects', str(len(self.effects)))
		for effect_obj in self.effects:
			effect_obj.write(tempxml)
		self.enabled.write(tempxml)

class lmms_ladspa_param:
	def __init__(self):
		self.link = lmms_param('link', 0)
		self.data = lmms_param('data', 0)

	def read(self, xmldata):
		self.link.read(xmldata)
		self.data.read(xmldata)

	def write(self, xmldata):
		self.link.write(xmldata)
		self.data.write(xmldata)

class lmms_vst_param:
	def __init__(self):
		self.visname = ''
		self.value = 0
		self.inlist = False
		self.scale_type = 'linear'
		self.id = None

	def read_param(self, instr):
		paramdata = instr.split(':')
		self.visname = paramdata[1]
		self.value = float(paramdata[2])
		self.inlist = True

	def __float__(self):
		return float(self.value)

	def write(self, xmldata, num):
		paramname = 'param'+str(num)
		if self.inlist: xmldata.set(paramname, ':'.join([str(num), self.visname, str(self.value)]))
		if self.id:
			tempxml = ET.SubElement(xmldata, paramname)
			tempxml.set('scale_type', str(self.scale_type))
			tempxml.set('id', str(self.id))
			tempxml.set('value', str(self.value))

class lmms_plugin:
	def __init__(self):
		self.name = ''
		self.params = {}
		self.custom = {}
		self.ladspa_params = {}
		self.ladspa_ports = 0
		self.ladspa_link = -1
		self.vst_params = {}

	def read(self, xmldata):
		self.name = xmldata.tag

		if self.name == 'ladspacontrols':
			ladlink = xmldata.get('link')
			self.ladspa_ports = int(xmldata.get('ports'))
			self.ladspa_link = int(ladlink if ladlink else 0)
			for xmlpart in xmldata:
				ladspa_param_obj = lmms_ladspa_param()
				ladspa_param_obj.read(xmlpart)
				self.ladspa_params[xmlpart.tag] = ladspa_param_obj
		elif self.name in ['vestige', 'vsteffect']:
			for n, v in xmldata.attrib.items():
				isvstparam = False
				if n.startswith('param'):
					paramnum = n[5:]
					if paramnum.isnumeric():
						paramnum = int(paramnum)
						isvstparam = True
						vst_param = self.add_vst_param(paramnum)
						vst_param.read_param(v)
				
				if not isvstparam:
					param_obj = lmms_param(n, v)
					param_obj.read(xmldata)
					self.params[n] = param_obj

			for xmlpart in xmldata:
				isvstparam = False
				isvalid = data_values.list__only_values(list(xmlpart.attrib.keys()), ['value','scale_type','id'])
				if isvalid:
					if xmlpart.tag.startswith('param'):
						paramnum = xmlpart.tag[5:]
						if paramnum.isnumeric():
							paramnum = int(paramnum)
							isvstparam = True
							vst_param = self.add_vst_param(paramnum)
							if 'value' in xmlpart.attrib: 
								vst_param.value = float(xmlpart.attrib['value'])
							if 'scale_type' in xmlpart.attrib: 
								vst_param.scale_type = xmlpart.attrib['scale_type']
							if 'id' in xmlpart.attrib: 
								vst_param.id = int(xmlpart.attrib['id'])
					if not isvstparam:
						param_obj = lmms_param(xmlpart.tag, '')
						param_obj.read(xmldata)
						self.params[xmlpart.tag] = param_obj
				else:
					self.custom[xmlpart.tag] = xmlpart

		else:
			for n, v in xmldata.attrib.items():
				if not True in [n.endswith(x) for x in ['_numerator', '_denominator', '_syncmode']]:
					param_obj = lmms_param(n, v)
					param_obj.read(xmldata)
					self.params[n] = param_obj

			for xmlpart in xmldata:
				isvalid = data_values.list__only_values(list(xmlpart.attrib.keys()), ['value','scale_type','id'])
				if isvalid:
					param_obj = lmms_param(xmlpart.tag, '')
					param_obj.read(xmldata)
					self.params[xmlpart.tag] = param_obj
				else:
					self.custom[xmlpart.tag] = xmlpart

	def get_param(self, name, fallback):
		return self.params[name] if name in self.params else lmms_param(name, fallback)

	def add_param(self, name, value):
		param_obj = lmms_param(name, value)
		self.params[name] = param_obj
		return param_obj

	def add_vst_param(self, num):
		param_obj = lmms_vst_param()
		if num not in self.vst_params: self.vst_params[num] = param_obj
		return self.vst_params[num]

	def write(self, xmldata):
		if self.name:
			tempxml = ET.SubElement(xmldata, self.name)
			if self.name == 'ladspacontrols':
				tempxml.set('ports', str(self.ladspa_ports))
				tempxml.set('link', str(self.ladspa_link))
				for name, ladspa_param_obj in self.ladspa_params.items():
					lpxml = ET.SubElement(tempxml, name)
					ladspa_param_obj.write(lpxml)
			else:
				for name, param_obj in self.params.items():
					param_obj.write(tempxml)
				for _, cusxml in self.custom.items():
					tempxml.append(cusxml)
				if self.name in ['vestige', 'vsteffectcontrols']:
					for paramid, vst_param in self.vst_params.items():
						vst_param.write(tempxml, paramid)

class lmms_instrument:
	def __init__(self):
		self.name = 'audiofileprocessor'
		self.plugin = lmms_plugin()

	def read(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'name': self.name = v

		for xmlpart in xmldata:
			self.plugin.read(xmlpart)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'instrument')
		tempxml.set('name', self.name)
		self.plugin.write(tempxml)

class lmms_sampletco:
	def __init__(self):
		self.sample_rate = 0
		self.len = 0
		self.muted = 0
		self.pos = 0
		self.off = -1
		self.src = ''

	def read(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'sample_rate': self.sample_rate = int(v)
			if n == 'len': self.len = int(v)
			if n == 'muted': self.muted = int(v)
			if n == 'pos': self.pos = int(v)
			if n == 'off': self.off = int(v)
			if n == 'src': self.src = v

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'sampletco')
		tempxml.set('src', self.src)
		tempxml.set('pos', str(self.pos))
		tempxml.set('muted', str(self.muted))
		tempxml.set('len', str(self.len))
		if self.off != -1: tempxml.set('off', str(self.off))
		if self.sample_rate: tempxml.set('sample_rate', str(self.sample_rate))

class lmms_instrumenttrack:
	def __init__(self):
		self.vol = lmms_param('vol', 100)
		self.fxch = lmms_param('fxch', -1)
		self.pitch = lmms_param('pitch', 0)
		self.pan = lmms_param('pan', 0)
		self.basenote = 57
		self.pitchrange = lmms_param('pitchrange', 1)
		self.usemasterpitch = lmms_param('usemasterpitch', 1)
		self.arpeggiator = lmms_arpeggiator()
		self.chordcreator = lmms_chordcreator()
		self.eldata = lmms_eldata()
		self.midiport = lmms_midiport()
		self.fxchain = lmms_fxchain()
		self.instrument = lmms_instrument()

	def read(self, xmldata):
		self.vol.read(xmldata)
		self.fxch.read(xmldata)
		self.pitch.read(xmldata)
		self.pan.read(xmldata)
		self.pitchrange.read(xmldata)
		self.usemasterpitch.read(xmldata)

		for n, v in xmldata.attrib.items():
			if n == 'basenote': self.basenote = int(v)

		for xmlpart in xmldata:
			if xmlpart.tag == 'instrument': self.instrument.read(xmlpart)
			if xmlpart.tag == 'arpeggiator': self.arpeggiator.read(xmlpart)
			if xmlpart.tag == 'chordcreator': self.chordcreator.read(xmlpart)
			if xmlpart.tag == 'eldata': self.eldata.read(xmlpart)
			if xmlpart.tag == 'midiport': self.midiport.read(xmlpart)
			if xmlpart.tag == 'fxchain': self.fxchain.read(xmlpart)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'instrumenttrack')
		self.instrument.write(tempxml)
		self.vol.write(tempxml)
		self.fxch.write(tempxml)
		self.pitch.write(tempxml)
		self.pan.write(tempxml)
		tempxml.set('basenote', str(self.basenote))
		self.pitchrange.write(tempxml)
		self.usemasterpitch.write(tempxml)
		self.eldata.write(tempxml)
		self.chordcreator.write(tempxml)
		self.arpeggiator.write(tempxml)
		self.midiport.write(tempxml)
		self.fxchain.write(tempxml)
		
class lmms_sampletrack:
	def __init__(self):
		self.fxchain = lmms_fxchain()
		self.vol = lmms_param('vol', 100)
		self.pan = lmms_param('pan', 0)
		self.fxch = lmms_param('fxch', -1)

	def read(self, xmldata):
		self.vol.read(xmldata)
		self.pan.read(xmldata)
		self.fxch.read(xmldata)
		for xmlpart in xmldata:
			if xmlpart.tag == 'fxchain': self.fxchain.read(xmlpart)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'sampletrack')
		self.vol.write(tempxml)
		self.pan.write(tempxml)
		self.fxch.write(tempxml)
		self.fxchain.write(tempxml)

class lmms_bbtco:
	def __init__(self):
		self.pos = 0
		self.muted = 0
		self.color = 0
		self.len = 0
		self.usestyle = 0
		self.name = ''

	def read(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'pos': self.pos = int(v)
			if n == 'muted': self.muted = int(v)
			if n == 'color': self.color = int(v)
			if n == 'len': self.len = int(v)
			if n == 'usestyle': self.usestyle = int(v)
			if n == 'name': self.name = v

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'bbtco')
		tempxml.set('pos', str(self.pos))
		tempxml.set('muted', str(self.muted))
		tempxml.set('color', str(self.color))
		tempxml.set('len', str(self.len))
		tempxml.set('usestyle', str(self.usestyle))
		tempxml.set('name', self.name)

class lmms_bbtrack:
	def __init__(self):
		self.trackcontainer = lmms_trackcontainer('bbtrackcontainer')
		self.trackcontainer_used = False

	def read(self, xmldata):
		for xmlpart in xmldata:
			if xmlpart.tag == 'trackcontainer':
				self.trackcontainer_used = True
				self.trackcontainer.read(xmlpart)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'bbtrack')
		if self.trackcontainer_used: self.trackcontainer.write(tempxml)
		
class lmms_track:
	def __init__(self):
		self.muted = lmms_param('muted', 0)
		self.solo = lmms_param('solo', 0)
		self.type = 0
		self.name = ''
		self.color = ''
		self.patterns = []
		self.instrumenttrack = lmms_instrumenttrack()
		self.sampletrack = lmms_sampletrack()
		self.bbtrack = lmms_bbtrack()
		self.automationpatterns = []
		self.sampletcos = []
		self.bbtcos = []

	def read(self, xmldata):
		self.muted.read(xmldata)
		self.solo.read(xmldata)
		for n, v in xmldata.attrib.items():
			if n == 'type': self.type = int(v)
			if n == 'name': self.name = v
			if n == 'color': self.color = v

		for xmlpart in xmldata:
			if xmlpart.tag == 'instrumenttrack':
				self.instrumenttrack.read(xmlpart)
			if xmlpart.tag in ['bbtrack', 'patterntrack']:
				self.bbtrack.read(xmlpart)
			if xmlpart.tag == 'sampletrack':
				self.sampletrack.read(xmlpart)
			if xmlpart.tag in ['pattern', 'midiclip']:
				pattern_obj = lmms_pattern()
				pattern_obj.read(xmlpart)
				self.patterns.append(pattern_obj)
			if xmlpart.tag == 'automationpattern':
				automationpattern_obj = lmms_automationpattern()
				automationpattern_obj.read(xmlpart)
				self.automationpatterns.append(automationpattern_obj)
			if xmlpart.tag == 'sampletco':
				sampletco_obj = lmms_sampletco()
				sampletco_obj.read(xmlpart)
				self.sampletcos.append(sampletco_obj)
			if xmlpart.tag in ['bbtco', 'patternclip']:
				bbtco_obj = lmms_bbtco()
				bbtco_obj.read(xmlpart)
				self.bbtcos.append(bbtco_obj)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'track')
		tempxml.set('type', str(self.type))
		self.muted.write(tempxml)
		self.solo.write(tempxml)
		tempxml.set('name', self.name)

		if self.color: tempxml.set('color', self.color)
		if self.type == 0: self.instrumenttrack.write(tempxml)
		if self.type == 1: self.bbtrack.write(tempxml)
		if self.type == 2: self.sampletrack.write(tempxml)
		if self.type in [5, 6]: ET.SubElement(tempxml, 'automationtrack')

		for pattern_obj in self.patterns: pattern_obj.write(tempxml)
		for sampletco_obj in self.sampletcos: sampletco_obj.write(tempxml)
		for bbtco_obj in self.bbtcos: bbtco_obj.write(tempxml)

		if self.type in [5, 6]:
			for automationpattern_obj in self.automationpatterns:
				automationpattern_obj.write(tempxml, 'automationpattern')

class lmms_window:
	def __init__(self):
		self.x = -1
		self.y = -1
		self.minimized = -1
		self.height = -1
		self.visible = -1
		self.maximized = -1
		self.width = -1

	def read(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'x': self.x = v
			elif n == 'type': self.type = v
			elif n == 'y': self.y = int(v)
			elif n == 'minimized': self.minimized = int(v)
			elif n == 'height': self.height = int(v)
			elif n == 'visible': self.visible = int(v)
			elif n == 'maximized': self.maximized = int(v)
			elif n == 'width': self.width = int(v)

	def write(self, xmldata):
		if self.x != -1: xmldata.set('x', str(self.x))
		if self.y != -1: xmldata.set('y', str(self.y))
		if self.minimized != -1: xmldata.set('minimized', str(self.minimized))
		if self.height != -1: xmldata.set('height', str(self.height))
		if self.visible != -1: xmldata.set('visible', str(self.visible))
		if self.maximized != -1: xmldata.set('maximized', str(self.maximized))
		if self.width != -1: xmldata.set('width', str(self.width))

class lmms_fxchannel:
	def __init__(self):
		self.volume = lmms_param('volume', 1)
		self.soloed = lmms_param('soloed', 0)
		self.muted = lmms_param('muted', 0)
		self.name = ''
		self.color = ''
		self.fxchain = lmms_fxchain()
		self.sends = {}

	def read(self, xmldata):
		self.volume.read(xmldata)
		self.soloed.read(xmldata)
		self.muted.read(xmldata)
		self.name = xmldata.get('name')
		for xmlpart in xmldata:
			if xmlpart.tag == 'fxchain':
				self.fxchain.read(xmlpart)
			if xmlpart.tag == 'send':
				param_obj = lmms_param('amount', 1)
				param_obj.read(xmlpart)
				self.sends[int(xmlpart.get('channel'))] = param_obj

	def write(self, xmldata, num):
		tempxml = ET.SubElement(xmldata, 'fxchannel')
		self.fxchain.write(tempxml)
		self.muted.write(tempxml)
		self.volume.write(tempxml)
		self.soloed.write(tempxml)
		tempxml.set('num', str(num))
		tempxml.set('name', self.name)
		if self.color: tempxml.set('color', self.color)
		for num, param_obj in self.sends.items():
			send_xml = ET.SubElement(tempxml, 'send')
			send_xml.set('channel', str(num))
			param_obj.write(send_xml)

class lmms_fxmixer:
	def __init__(self):
		self.window = lmms_window()
		self.fxchannels = {}

	def read(self, xmldata):
		self.window.read(xmldata)
		for xmlpart in xmldata:
			if xmlpart.tag in ['fxchannel', 'mixerchannel']:
				fxchannel_obj = lmms_fxchannel()
				fxchannel_obj.read(xmlpart)
				self.fxchannels[int(xmlpart.get('num'))] = fxchannel_obj

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'fxmixer')
		self.window.write(tempxml)
		for num, fxchannel_obj in self.fxchannels.items():
			fxchannel_obj.write(tempxml, num)

class lmms_trackcontainer:
	def __init__(self, tctype):
		self.type = tctype
		self.window = lmms_window()
		self.tracks = []

	def read(self, xmldata):
		self.window.read(xmldata)
		for n, v in xmldata.attrib.items():
			if n == 'type': self.type = v

		for xmlpart in xmldata:
			if xmlpart.tag == 'track':
				track_obj = lmms_track()
				track_obj.read(xmlpart)
				self.tracks.append(track_obj)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'trackcontainer')
		self.window.write(tempxml)
		if self.type != -1: tempxml.set('type', self.type)

		for track_obj in self.tracks:
			track_obj.write(tempxml)

class lmms_projectnotes:
	def __init__(self):
		self.window = lmms_window()
		self.text = ''

	def read(self, xmldata):
		self.window.read(xmldata)
		self.text = xmldata.text

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'projectnotes')
		self.window.write(tempxml)
		tempxml.text = self.text

class lmms_timeline:
	def __init__(self):
		self.lp1pos = 0
		self.lpstate = 0
		self.lp0pos = 0

	def read(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'lp1pos': self.lp1pos = int(v)
			elif n == 'lpstate': self.lpstate = int(v)
			elif n == 'lp0pos': self.lp0pos = int(v)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'timeline')
		tempxml.set('lp1pos', str(self.lp1pos))
		tempxml.set('lpstate', str(self.lpstate))
		tempxml.set('lp0pos', str(self.lp0pos))

class lmms_lfocontroller:
	def __init__(self):
		self.type = 1
		self.userwavefile = ''
		self.name = ''
		self.base = lmms_param('base', 0)
		self.speed = lmms_param('speed', 0)
		self.amount = lmms_param('amount', 0)
		self.phase = lmms_param('phase', 0)
		self.wave = lmms_param('wave', 0)
		self.multiplier = lmms_param('multiplier', 0)

	def read(self, xmldata):
		if 'name' in xmldata.attrib: self.name = xmldata.attrib['name']
		if 'type' in xmldata.attrib: self.type = xmldata.attrib['type']
		if 'userwavefile' in xmldata.attrib: self.userwavefile = xmldata.attrib['userwavefile']
		self.base.read(xmldata)
		self.speed.read(xmldata)
		self.amount.read(xmldata)
		self.phase.read(xmldata)
		self.wave.read(xmldata)
		self.multiplier.read(xmldata)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'lfocontroller')
		self.base.write(tempxml)
		self.speed.write(tempxml)
		self.amount.write(tempxml)
		self.phase.write(tempxml)
		self.wave.write(tempxml)
		self.multiplier.write(tempxml)
		tempxml.set('name', self.name)
		tempxml.set('type', str(self.type))
		tempxml.set('userwavefile', self.userwavefile)

class lmms_song:
	def __init__(self):
		self.trackcontainer = lmms_trackcontainer('song')
		self.tracks = []
		self.fxmixer = lmms_fxmixer()
		self.ControllerRackView = lmms_window()
		self.pianoroll = lmms_window()
		self.automationeditor = lmms_window()
		self.projectnotes = lmms_projectnotes()
		self.timeline = lmms_timeline()
		self.controllers = []

	def read(self, xmldata):
		for xmlpart in xmldata:
			if xmlpart.tag == 'trackcontainer': 
				self.trackcontainer.read(xmlpart)

			if xmlpart.tag == 'fxmixer': self.fxmixer.read(xmlpart)

			if xmlpart.tag == 'track':
				track_obj = lmms_track()
				track_obj.read(xmlpart)
				self.tracks.append(track_obj)

			if xmlpart.tag == 'ControllerRackView': self.ControllerRackView.read(xmlpart)
			if xmlpart.tag == 'pianoroll': self.pianoroll.read(xmlpart)
			if xmlpart.tag == 'automationeditor': self.automationeditor.read(xmlpart)
			if xmlpart.tag == 'projectnotes': self.projectnotes.read(xmlpart)
			if xmlpart.tag == 'timeline': self.timeline.read(xmlpart)
			if xmlpart.tag == 'controllers':
				for subxml in xmlpart:
					if subxml.tag == 'lfocontroller':
						ctrlr_obj = lmms_lfocontroller()
						ctrlr_obj.read(subxml)
						self.controllers.append(ctrlr_obj)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'song')
		self.trackcontainer.write(tempxml)
		for track_obj in self.tracks: track_obj.write(tempxml)
		self.fxmixer.write(tempxml)
		ControllerRackView_xml = ET.SubElement(tempxml, 'ControllerRackView')
		pianoroll_xml = ET.SubElement(tempxml, 'pianoroll')
		automationeditor_xml = ET.SubElement(tempxml, 'automationeditor')
		self.ControllerRackView.write(ControllerRackView_xml)
		self.pianoroll.write(pianoroll_xml)
		self.automationeditor.write(automationeditor_xml)
		self.projectnotes.write(tempxml)
		self.timeline.write(tempxml)
		if self.controllers:
			controllers_xml = ET.SubElement(tempxml, 'ControllerRackView')
			for ctrlr_obj in self.controllers:
				ctrlr_obj.write(controllers_xml)

class lmms_head:
	def __init__(self):
		self.timesig_numerator = lmms_param('timesig_numerator', 4)
		self.timesig_denominator = lmms_param('timesig_denominator', 4)
		self.mastervol = lmms_param('mastervol', 100)
		self.masterpitch = lmms_param('masterpitch', 0)
		self.bpm = lmms_param('bpm', 140)

	def read(self, xmldata):
		self.timesig_numerator.read(xmldata)
		self.timesig_denominator.read(xmldata)
		self.mastervol.read(xmldata)
		self.masterpitch.read(xmldata)
		self.bpm.read(xmldata)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'head')
		self.bpm.write(tempxml)
		self.timesig_numerator.write(tempxml)
		self.timesig_denominator.write(tempxml)
		self.mastervol.write(tempxml)
		self.masterpitch.write(tempxml)

class lmms_project:
	def __init__(self):
		self.head = lmms_head()
		self.song = lmms_song()
		self.type = 'song'
		self.version = '1.0'
		self.creator = 'LMMS'
		self.creatorversion = '1.2.2'

	def load_from_file(self, input_file):
		try:
			xmldata = get_xml_tree(input_file)
		except ET.ParseError as t:
			raise ProjectFileParserException('lmms: XML parsing error: '+str(t))
		self.type = xmldata.get('type')
		self.version = xmldata.get('version')
		self.creator = xmldata.get('creator')
		self.creatorversion = xmldata.get('creatorversion')
		for xmlpart in xmldata:
			if xmlpart.tag == 'head': self.head.read(xmlpart)
			if xmlpart.tag == 'song': self.song.read(xmlpart)
		return True

	def save_to_file(self, output_file):
		xmldata = ET.Element("lmms-project")
		if self.type: xmldata.set('type', self.type)
		if self.version: xmldata.set('version', self.version)
		if self.creator: xmldata.set('creator', self.creator)
		if self.creatorversion: xmldata.set('creatorversion', self.creatorversion)
		self.head.write(xmldata)
		self.song.write(xmldata)

		outfile = ET.ElementTree(xmldata)
		ET.indent(outfile)
		outfile.write(output_file, encoding='utf-8', xml_declaration = True)
