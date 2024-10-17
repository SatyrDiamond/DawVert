# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET

def get_pointee(xmltag, counter_obj):
	if xmltag:
		Pointee = xmltag.findall('Pointee')
		if Pointee:
			return int(Pointee[0].get('Id'))
	return int(counter_obj.get() if counter_obj else 0)

def add_value(xmltag, name, value):
	if isinstance(value, float): value = "%g"%value
	x_temp = ET.SubElement(xmltag, name)
	x_temp.set('Value', str(value))
	return x_temp

def add_value_opt(xmltag, name, value):
	if value != None:
		if isinstance(value, float): value = "%g"%value
		x_temp = ET.SubElement(xmltag, name)
		x_temp.set('Value', str(value))
		return x_temp

def get_value(xmldata, varname, fallback): 
	return (xmldata.findall(varname)[0].get('Value') if len(xmldata.findall(varname)) != 0 else fallback) if xmldata else fallback

def get_value_multi(xmldata, varnames, fallback): 
	if xmldata:
		for varname in varnames:
			valuevar = xmldata.findall(varname)
			if len(valuevar) != 0: return valuevar[0].get('Value')
		return fallback
	else: 
		return fallback

def get_value_opt(xmldata, varname, fallback): 
	if xmldata:
		valvar = xmldata.findall(varname)
		if len(valvar) != 0: return valvar[0].get('Value')
		else: return fallback
	else: return None

def add_bool(xmltag, name, value):
	x_temp = ET.SubElement(xmltag, name)
	x_temp.set('Value', ['false','true'][int(value)])
	return x_temp

def add_bool_opt(xmltag, name, value):
	if value != None:
		x_temp = ET.SubElement(xmltag, name)
		x_temp.set('Value', ['false','true'][int(value)])
		return x_temp

def get_bool(xmldata, varname, fallback): 
	if xmldata:
		boolvar = xmldata.findall(varname)
		if len(boolvar) != 0: return ['false','true'].index(boolvar[0].get('Value'))
		else: return fallback
	else: return fallback

def get_bool_multi(xmldata, varnames, fallback): 
	if xmldata:
		for varname in varnames:
			boolvar = xmldata.findall(varname)
			if len(boolvar) != 0: return ['false','true'].index(boolvar[0].get('Value'))
		return fallback
	else: 
		return fallback

def get_bool_opt(xmldata, varname, fallback): 
	if xmldata:
		boolvar = xmldata.findall(varname)
		if len(boolvar) != 0: return ['false','true'].index(boolvar[0].get('Value'))
		else: return fallback
	else: return None

def add_id(xmltag, name, value):
	x_temp = ET.SubElement(xmltag, name)
	x_temp.set('Id', str(value))
	return x_temp

def add_lomid(xmltag, name, value):
	x_temp = ET.SubElement(xmltag, name)
	x_temp.set('LomId', str(value))
	return x_temp

def get_list(xmltag, name, inname, inobject):
	outdict = {}
	if xmltag:
		mainobj = xmltag.findall(name)
		if mainobj:
			for subobj in mainobj[0].findall(inname): 
				outdict[int(subobj.get('Id'))] = inobject(subobj)
		else: return None
	return outdict

def set_list(xmltag, dictobj, name, inname):
	inxmldata = ET.SubElement(xmltag, name)
	for nid, data in dictobj.items():
		xmlpart = ET.SubElement(inxmldata, inname)
		xmlpart.set('Id', str(nid))
		data.write(xmlpart)

class ableton_LomId:
	__slots__ = ['LomId','LomIdView']
	def __init__(self, xmltag):
		if xmltag:
			self.LomId = int(get_value(xmltag, 'LomId', 0))
			self.LomIdView = int(get_value(xmltag, 'LomIdView', 0))
		else:
			self.LomId = 0
			self.LomIdView = 0

	def write(self, xmltag):
		add_value(xmltag, 'LomId', self.LomId)
		add_value(xmltag, 'LomIdView', self.LomIdView)

class ableton_upperlowertarget:
	__slots__ = ['name','Target','UpperDisplayString','LowerDisplayString']
	def __init__(self, xmltag, name):
		self.name = name
		if xmltag:
			x_TrackDelay = xmltag.findall(self.name)[0]
			self.Target = get_value(x_TrackDelay, 'Target', '')
			self.UpperDisplayString = get_value(x_TrackDelay, 'UpperDisplayString', '')
			self.LowerDisplayString = get_value(x_TrackDelay, 'LowerDisplayString', '')
		else:
			self.Target = ''
			self.UpperDisplayString = ''
			self.LowerDisplayString = ''

	def set(self, Target, UpperDisplayString, LowerDisplayString):
		self.Target = Target
		self.UpperDisplayString = UpperDisplayString
		self.LowerDisplayString = LowerDisplayString

	def write(self, xmltag):
		x_data = ET.SubElement(xmltag, self.name)
		add_value(x_data, 'Target', self.Target)
		add_value(x_data, 'UpperDisplayString', self.UpperDisplayString)
		add_value(x_data, 'LowerDisplayString', self.LowerDisplayString)
