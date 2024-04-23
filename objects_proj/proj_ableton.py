# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
from functions import data_values
from xml.dom import minidom
import gzip

mixerp_unused_id = data_values.counter(1000)
counter_unused_id = data_values.counter(30000)

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

# --------------------------------------------- Device ---------------------------------------------

excludenames =  ['LomId', 'LomIdView', 'IsExpanded', 'On', 
'ModulationSourceCount', 'ParametersListWrapper', 'Pointee', 
'LastSelectedTimeableIndex', 'LastSelectedClipEnvelopeIndex', 
'LastPresetRef', 'LockedScripts', 'IsFolded', 'ShouldShowPresetName', 
'UserName', 'Annotation', 'SourceContext', 'OverwriteProtectionNumber']

def paramdetect(pathd, xmltag, xmlin, dictdata):
	valuetxt = xmlin.get('Value')
	isparam = xmlin.findall('Manual')
	valtype = 'unknown'
	out = None
	txtdata = '' if xmlin.text == None else xmlin.text.strip()
	if valuetxt != None:
		if valuetxt in ['true', 'false']: 
			valtype = 'bool'
			out = valuetxt=='true'
		else:
			valtype = 'value'
			out = valuetxt

	elif isparam:
		valtype = 'param'
		i_Param = isparam[0]
		Manual = i_Param.get('Value')

		if Manual in ['true', 'false']: paramtype = 'bool'
		elif '.' in Manual: paramtype = 'float'
		else: paramtype = 'int'
		out = ableton_Param(xmltag, xmlin.tag, paramtype)
	elif txtdata:
		valtype = 'buffer'
		hextxt = xmlin.text.replace('\t', '').replace('\n', '')
		out = bytes.fromhex(hextxt)
	elif xmlin.tag == 'SampleRef':
		valtype = 'sampleref'
		out = ableton_SampleRef(xmltag)
	else:
		numset = {}
		groupdata = []
		is_numset = True if xmlin else False

		ids = [xmlpart.get('Id') for xmlpart in xmlin]
		is_numset = (None not in ids)

		if not is_numset:
			valtype = 'group'
			out = {}
			for xmlpart in xmlin: paramdetect(pathd+[xmlin.tag], xmlin, xmlpart, dictdata)
		else:
			valtype = 'numset'
			out = {}
			for xmlpart in xmlin: 
				Id = int(xmlpart.get('Id'))
				attribdata = xmlpart.attrib.copy()
				del attribdata['Id']
				insideo = {}
				paramdetect([], xmlin, xmlpart, insideo)
				out[Id] = [insideo, xmlin.tag, attribdata]

	if valtype != 'group':
		paramname = '/'.join(pathd+[xmlin.tag])
		dictdata[paramname] = [valtype, out]

def paramscan(xmltag):
	dictdata = {}
	for xmlpart in xmltag:
		name = xmlpart.tag
		if name not in excludenames:
			paramdetect([], xmltag, xmlpart, dictdata)
	return dictdata

def paramcreate(xmltag, params):
	for pname, ptype, pout in params:
		if ptype == 'param': pout.write(xmltag)
		if ptype == 'value': add_value(xmltag, pname, pout)
		if ptype == 'bool': add_bool(xmltag, pname, pout)
		if ptype == 'group': 
			xmlg = ET.SubElement(xmltag, pname)
			paramcreate(xmlg, pout)
		if ptype == 'numset': 
			xmlg = ET.SubElement(xmltag, pname)
			for x, v in pout.items():
				xname, xdata, xattr = v
				iname, itype, iout = xdata
				xmld = ET.SubElement(xmlg, xname)
				xmld.attrib['Id'] = str(x)
				xmld.attrib |= xattr
				paramcreate(xmld, iout)
		if ptype == 'sampleref': pout.write(xmltag)

class ableton_Device:
	def __init__(self, xmltag):
		self.params = []
		self.LomId = ableton_LomId(xmltag)
		if xmltag:
			self.name = xmltag.tag
			self.id = int(xmltag.get('Id'))
			self.IsExpanded = get_bool(xmltag, 'IsExpanded', True)
			self.On = ableton_Param(xmltag, 'On', 'bool')
			self.ModulationSourceCount = int(get_value(xmltag, 'ModulationSourceCount', 0))
			self.Pointee = int(xmltag.findall('Pointee')[0].get('Id') if xmltag else 0)
			self.LastSelectedTimeableIndex = int(get_value(xmltag, 'LastSelectedTimeableIndex', 0))
			self.LastSelectedClipEnvelopeIndex = int(get_value(xmltag, 'LastSelectedClipEnvelopeIndex', 0))
			self.IsFolded = get_bool(xmltag, 'IsFolded', False)
			self.ShouldShowPresetName = get_bool(xmltag, 'ShouldShowPresetName', False)
			self.UserName = get_value(xmltag, 'UserName', '')
			self.Annotation = get_value(xmltag, 'Annotation', '')
			x_SourceContext = xmltag.findall('SourceContext')[0]
			self.SourceContext = get_list(x_SourceContext, 'Value', 'BranchSourceContext', ableton_SourceContext)
			self.params = paramscan(xmltag)

	def get_paramdata(self, params, pathd, outfow):
		return get_paramdata(params, pathd, [])

	def write(self, xmltag):
		x_DeviceData = ET.SubElement(xmltag, self.name)
		x_DeviceData.set('Id', str(self.id))
		self.LomId.write(x_DeviceData)
		add_bool(x_DeviceData, 'IsExpanded', self.IsExpanded)
		self.On.write(x_DeviceData)
		add_value(x_DeviceData, 'ModulationSourceCount', self.ModulationSourceCount)
		add_lomid(x_DeviceData, 'ParametersListWrapper', 0)
		add_id(x_DeviceData, 'Pointee', self.Pointee)
		add_value(x_DeviceData, 'LastSelectedTimeableIndex', self.LastSelectedTimeableIndex)
		add_value(x_DeviceData, 'LastSelectedClipEnvelopeIndex', self.LastSelectedClipEnvelopeIndex)
		x_LastPresetRef = ET.SubElement(x_DeviceData, "LastPresetRef")
		ET.SubElement(x_LastPresetRef, "Value")
		ET.SubElement(x_DeviceData, "LockedScripts")
		add_bool(x_DeviceData, 'IsFolded', self.IsFolded)
		add_bool(x_DeviceData, 'ShouldShowPresetName', self.ShouldShowPresetName)
		add_value(x_DeviceData, 'UserName', self.UserName)
		add_value(x_DeviceData, 'Annotation', self.Annotation)
		x_SourceContext = ET.SubElement(x_DeviceData, "SourceContext")
		x_Value = ET.SubElement(x_SourceContext, "Value")
		add_value(x_DeviceData, 'OverwriteProtectionNumber', 2816)
		#set_list(x_SourceContext, self.SourceContext, "Value", "BranchSourceContext")
		paramcreate(x_DeviceData, self.params)


# --------------------------------------------- AutomationLane ---------------------------------------------

class ableton_AutomationLane:
	def __init__(self, xmltag):
		self.SelectedDevice = int(get_value(xmltag, 'SelectedDevice', 0))
		self.SelectedEnvelope = int(get_value(xmltag, 'SelectedEnvelope', 0))
		self.IsContentSelectedInDocument = get_bool(xmltag, 'IsContentSelectedInDocument', False)
		self.LaneHeight = int(get_value(xmltag, 'LaneHeight', 68))

	def write(self, xmltag):
		add_value(xmltag, 'SelectedDevice', self.SelectedDevice)
		add_value(xmltag, 'SelectedEnvelope', self.SelectedEnvelope)
		add_bool(xmltag, 'IsContentSelectedInDocument', self.IsContentSelectedInDocument)
		add_value(xmltag, 'LaneHeight', self.LaneHeight)

class ableton_AutomationLanes:
	def __init__(self, xmltag):
		self.AutomationLanes = {}
		if xmltag:
			x_AutomationLanes = xmltag.findall('AutomationLanes')[0]
			self.AreAdditionalAutomationLanesFolded = get_bool(x_AutomationLanes, 'AreAdditionalAutomationLanesFolded', False)
			self.AutomationLanes = get_list(x_AutomationLanes, 'AutomationLanes', 'AutomationLane', ableton_AutomationLane)
		else: self.AreAdditionalAutomationLanesFolded = False

	def write(self, xmltag):
		x_AutomationLanes = ET.SubElement(xmltag, "AutomationLanes")
		set_list(x_AutomationLanes, self.AutomationLanes, "AutomationLanes", "AutomationLane")
		add_bool(x_AutomationLanes, 'AreAdditionalAutomationLanesFolded', self.AreAdditionalAutomationLanesFolded)

# --------------------------------------------- Varibles ---------------------------------------------

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

class ableton_TrackDelay:
	__slots__ = ['Value','IsValueSampleBased']
	def __init__(self, xmltag):
		if xmltag:
			x_TrackDelay = xmltag.findall('TrackDelay')[0]
			self.Value = int(get_value(x_TrackDelay, 'Value', 0))
			self.IsValueSampleBased = get_bool(x_TrackDelay, 'IsValueSampleBased', 0)
		else:
			self.Value = 0
			self.IsValueSampleBased = False

	def write(self, xmltag):
		x_TrackDelay = ET.SubElement(xmltag, "TrackDelay")
		add_value(x_TrackDelay, 'Value', self.Value)
		add_bool(x_TrackDelay, 'IsValueSampleBased', self.IsValueSampleBased)

class ableton_Name:
	__slots__ = ['EffectiveName','UserName','Annotation','MemorizedFirstClipName']
	def __init__(self, xmltag):
		if xmltag:
			x_Name = xmltag.findall('Name')[0]
			self.EffectiveName = get_value(x_Name, 'EffectiveName', '')
			self.UserName = get_value(x_Name, 'UserName', '')
			self.Annotation = get_value(x_Name, 'Annotation', '')
			self.MemorizedFirstClipName = get_value(x_Name, 'MemorizedFirstClipName', '')
		else:
			self.EffectiveName = ''
			self.UserName = ''
			self.Annotation = ''
			self.MemorizedFirstClipName = ''

	def write(self, xmltag):
		x_Name = ET.SubElement(xmltag, "Name")
		add_value(x_Name, 'EffectiveName', self.EffectiveName)
		add_value(x_Name, 'UserName', self.UserName)
		add_value(x_Name, 'Annotation', self.Annotation)
		add_value(x_Name, 'MemorizedFirstClipName', self.MemorizedFirstClipName)

class ableton_ClipEnvelopeChooserViewState:
	__slots__ = ['SelectedDevice','SelectedEnvelope','PreferModulationVisible']
	def __init__(self, xmltag):
		if xmltag:
			x_Name = xmltag.findall('ClipEnvelopeChooserViewState')[0]
			self.SelectedDevice = get_value(x_Name, 'SelectedDevice', 0)
			self.SelectedEnvelope = get_value(x_Name, 'SelectedEnvelope', 0)
			self.PreferModulationVisible = get_bool(x_Name, 'PreferModulationVisible', False)
		else:
			self.SelectedDevice = 0
			self.SelectedEnvelope = 0
			self.PreferModulationVisible = False

	def write(self, xmltag):
		x_Name = ET.SubElement(xmltag, "ClipEnvelopeChooserViewState")
		add_value(x_Name, 'SelectedDevice', self.SelectedDevice)
		add_value(x_Name, 'SelectedEnvelope', self.SelectedEnvelope)
		add_bool(x_Name, 'PreferModulationVisible', self.PreferModulationVisible)

class ableton_ReceiveTarget:
	__slots__ = ['name','exists','id','lock']
	def __init__(self, xmltag, name):
		self.name = name
		self.exists = False
		self.id = -1
		self.lock = 0
		if xmltag:
			xm_ReceiveTarget = xmltag.findall(self.name)
			if xm_ReceiveTarget:
				self.exists = True
				self.lock = int(get_value(xm_ReceiveTarget[0], 'LockEnvelope', 0))
				self.id = xm_ReceiveTarget[0].get('Id')

	def set_id(self, autoid):
		self.exists = True
		self.id = autoid

	def set_unused(self):
		self.exists = True
		self.id = counter_unused_id.get()

	def write(self, xmltag):
		if self.exists:
			x_ReceiveTarget = ET.SubElement(xmltag, self.name)
			x_ReceiveTarget.set('Id', str(self.id))
			add_value(x_ReceiveTarget, 'LockEnvelope', self.lock)

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

# --------------------------------------------- Mixer ---------------------------------------------

class ableton_TrackSendHolder:
	__slots__ = ['Send','TrackUnfolded']
	def __init__(self, xmltag):
		self.Send = ableton_Param(xmltag, 'Send', 'float')
		self.TrackUnfolded = get_bool(xmltag, 'Active', True)

	def write(self, xmltag):
		self.Send.write(xmltag)
		add_bool(xmltag, 'Active', self.TrackUnfolded)

class ableton_Mixer:
	#__slots__ = ['LomId','IsExpanded','On','ModulationSourceCount','Pointee','LastSelectedTimeableIndex','LastSelectedClipEnvelopeIndex','IsFolded','ShouldShowPresetName','UserName','Annotation','Sends','Speaker','SoloSink','PanMode','Pan','SplitStereoPanL','SplitStereoPanR','Volume','ViewStateSesstionTrackWidth','CrossFadeState']
	def __init__(self, xmltag, tracktype):
		self.LomId = ableton_LomId(xmltag)
		self.IsExpanded = get_bool(xmltag, 'IsExpanded', True)
		self.On = ableton_Param(xmltag, 'On', 'bool')
		self.ModulationSourceCount = int(get_value(xmltag, 'ModulationSourceCount', 0))
		self.Pointee = int(xmltag.findall('Pointee')[0].get('Id') if xmltag else 0)
		self.LastSelectedTimeableIndex = int(get_value(xmltag, 'LastSelectedTimeableIndex', 0))
		self.LastSelectedClipEnvelopeIndex = int(get_value(xmltag, 'LastSelectedClipEnvelopeIndex', 0))
		self.IsFolded = get_bool(xmltag, 'IsFolded', False)
		self.ShouldShowPresetName = get_bool(xmltag, 'ShouldShowPresetName', False)
		self.UserName = get_value(xmltag, 'UserName', '')
		self.Annotation = get_value(xmltag, 'Annotation', '')
		self.Sends = get_list(xmltag, 'Sends', 'TrackSendHolder', ableton_TrackSendHolder)
		self.Speaker = ableton_Param(xmltag, 'Speaker', 'bool')
		self.SoloSink = get_bool(xmltag, 'SoloSink', False)
		self.PanMode = get_value(xmltag, 'PanMode', 0)
		self.Pan = ableton_Param(xmltag, 'Pan', 'float')
		self.SplitStereoPanL = ableton_Param(xmltag, 'SplitStereoPanL', 'float')
		self.SplitStereoPanR = ableton_Param(xmltag, 'SplitStereoPanR', 'float')
		self.Volume = ableton_Param(xmltag, 'Volume', 'float')
		self.ViewStateSesstionTrackWidth = get_value(xmltag, 'ViewStateSesstionTrackWidth', 93)
		self.CrossFadeState = ableton_Param(xmltag, 'CrossFadeState', 'int')
		self.Tempo = ableton_Param(xmltag, 'Tempo', 'float')
		self.TimeSignature = ableton_Param(xmltag, 'TimeSignature', 'int')
		self.GlobalGrooveAmount = ableton_Param(xmltag, 'GlobalGrooveAmount', 'float')
		self.CrossFade = ableton_Param(xmltag, 'CrossFade', 'float')
		self.TempoAutomationViewBottom = get_value_opt(xmltag, 'TempoAutomationViewBottom', None)
		self.TempoAutomationViewTop = get_value_opt(xmltag, 'TempoAutomationViewTop', None)

		if xmltag == None:

			self.On.exists = True
			self.On.Manual = True

			self.Speaker.exists = True
			self.Speaker.Manual = True

			self.Pan.exists = True
			self.Pan.Manual = 0.0
			self.Pan.MidiControllerRange = [-1,1]

			self.SplitStereoPanL.exists = True
			self.SplitStereoPanL.Manual = -1.0
			self.SplitStereoPanL.MidiControllerRange = [-1,1]

			self.SplitStereoPanR.exists = True
			self.SplitStereoPanR.Manual = 1.0
			self.SplitStereoPanR.MidiControllerRange = [-1,1]

			self.Volume.exists = True
			self.Volume.Manual = 1.0
			self.Volume.MidiControllerRange = [0.000316228,1.99526]

			self.ViewStateSesstionTrackWidth = 74

			self.CrossFadeState.exists = True
			self.CrossFadeState.Manual = 1

			if tracktype == 'prehear':
				self.Pointee = 19732
				self.On.AutomationTarget.set_id(21)
				self.Speaker.AutomationTarget.set_id(22)
				self.Pan.AutomationTarget.set_id(23)
				self.Pan.ModulationTarget.set_id(24)
				self.SplitStereoPanL.AutomationTarget.set_id(16179)
				self.SplitStereoPanL.ModulationTarget.set_id(16180)
				self.SplitStereoPanR.AutomationTarget.set_id(16181)
				self.SplitStereoPanR.ModulationTarget.set_id(16182)
				self.Volume.AutomationTarget.set_id(25)
				self.Volume.ModulationTarget.set_id(26)
				self.CrossFadeState.AutomationTarget.set_id(27)

			elif tracktype == 'master':
				self.Pointee = 19730
				self.On.AutomationTarget.set_id(1)
				self.Speaker.AutomationTarget.set_id(2)
				self.Pan.AutomationTarget.set_id(3)
				self.Pan.ModulationTarget.set_id(4)
				self.SplitStereoPanL.AutomationTarget.set_id(16175)
				self.SplitStereoPanL.ModulationTarget.set_id(16176)
				self.SplitStereoPanR.AutomationTarget.set_id(16177)
				self.SplitStereoPanR.ModulationTarget.set_id(16178)
				self.Volume.AutomationTarget.set_id(5)
				self.Volume.ModulationTarget.set_id(6)

				self.ViewStateSesstionTrackWidth = 93

				self.Tempo.exists = True
				self.Tempo.Manual = 120.0
				self.Tempo.MidiControllerRange = [60,200]
				self.Tempo.AutomationTarget.set_id(8)
				self.Tempo.ModulationTarget.set_id(9)

				self.TimeSignature.exists = True
				self.TimeSignature.Manual = 201
				self.TimeSignature.AutomationTarget.set_id(10)

				self.GlobalGrooveAmount.exists = True
				self.GlobalGrooveAmount.Manual = 100.0
				self.GlobalGrooveAmount.MidiControllerRange = [0,131.25]
				self.GlobalGrooveAmount.AutomationTarget.set_id(11)
				self.GlobalGrooveAmount.ModulationTarget.set_id(12)

				self.CrossFade.exists = True
				self.CrossFade.Manual = 0.0
				self.CrossFade.MidiControllerRange = [-1,1]
				self.CrossFade.AutomationTarget.set_id(13)
				self.CrossFade.ModulationTarget.set_id(14)

				self.TempoAutomationViewBottom = 60
				self.TempoAutomationViewTop = 200

				self.LastSelectedTimeableIndex = 2

				self.CrossFadeState.AutomationTarget.set_id(7)

			else:
				self.Pointee = mixerp_unused_id.get()
				self.On.AutomationTarget.set_unused()
				self.Speaker.AutomationTarget.set_unused()
				self.Pan.AutomationTarget.set_unused()
				self.Pan.ModulationTarget.set_unused()
				self.SplitStereoPanL.AutomationTarget.set_unused()
				self.SplitStereoPanL.ModulationTarget.set_unused()
				self.SplitStereoPanR.AutomationTarget.set_unused()
				self.SplitStereoPanR.ModulationTarget.set_unused()
				self.Volume.AutomationTarget.set_unused()
				self.Volume.ModulationTarget.set_unused()


	def write(self, xmltag):
		x_Mixer = ET.SubElement(xmltag, "Mixer")
		self.LomId.write(x_Mixer)
		add_bool(x_Mixer, 'IsExpanded', self.IsExpanded)
		self.On.write(x_Mixer)
		add_value(x_Mixer, 'ModulationSourceCount', self.ModulationSourceCount)
		add_lomid(x_Mixer, 'ParametersListWrapper', 0)
		add_id(x_Mixer, 'Pointee', self.Pointee)
		add_value(x_Mixer, 'LastSelectedTimeableIndex', self.LastSelectedTimeableIndex)
		add_value(x_Mixer, 'LastSelectedClipEnvelopeIndex', self.LastSelectedClipEnvelopeIndex)
		x_LastPresetRef = ET.SubElement(x_Mixer, "LastPresetRef")
		ET.SubElement(x_LastPresetRef, "Value")
		ET.SubElement(x_Mixer, "LockedScripts")
		add_bool(x_Mixer, 'IsFolded', self.IsFolded)
		add_bool(x_Mixer, 'ShouldShowPresetName', self.ShouldShowPresetName)
		add_value(x_Mixer, 'UserName', self.UserName)
		add_value(x_Mixer, 'Annotation', self.Annotation)
		x_SourceContext = ET.SubElement(x_Mixer, "SourceContext")
		ET.SubElement(x_SourceContext, "Value")
		x_Sends = ET.SubElement(x_Mixer, "Sends")
		for nid, data in self.Sends.items():
			x_TrackSendHolder = ET.SubElement(x_Sends, "TrackSendHolder")
			x_TrackSendHolder.set('Id', str(nid))
			data.write(x_TrackSendHolder)
		self.Speaker.write(x_Mixer)
		add_bool(x_Mixer, 'SoloSink', self.SoloSink)
		add_value(x_Mixer, 'PanMode', self.PanMode)
		self.Pan.write(x_Mixer)
		self.SplitStereoPanL.write(x_Mixer)
		self.SplitStereoPanR.write(x_Mixer)
		self.Volume.write(x_Mixer)
		add_value(x_Mixer, 'ViewStateSesstionTrackWidth', self.ViewStateSesstionTrackWidth)
		self.CrossFadeState.write(x_Mixer)
		add_lomid(x_Mixer, 'SendsListWrapper', 0)
		self.Tempo.write(x_Mixer)
		self.TimeSignature.write(x_Mixer)
		self.GlobalGrooveAmount.write(x_Mixer)
		self.CrossFade.write(x_Mixer)
		add_value_opt(x_Mixer, 'TempoAutomationViewBottom', self.TempoAutomationViewBottom)
		add_value_opt(x_Mixer, 'TempoAutomationViewTop', self.TempoAutomationViewTop)

# --------------------------------------------- Sequencer ---------------------------------------------

class ableton_FloatEvent:
	__slots__ = ['Time','Value','CurveControl1X','CurveControl1Y','CurveControl2X','CurveControl2Y']
	def __init__(self, xmltag):
		if xmltag != None:
			self.Time = float(xmltag.get('Time'))
			self.Value = float(xmltag.get('Value'))
			self.CurveControl1X = xmltag.get('CurveControl1X')
			self.CurveControl1Y = xmltag.get('CurveControl1Y')
			self.CurveControl2X = xmltag.get('CurveControl2X')
			self.CurveControl2Y = xmltag.get('CurveControl2Y')
		else:
			self.Time = 0
			self.Value = 0
			self.CurveControl1X = 0.5
			self.CurveControl1Y = 0.5
			self.CurveControl2X = 0.5
			self.CurveControl2Y = 0.5

	def write(self, xmltag):
		xmltag.set('Time', str(self.Time))
		xmltag.set('Value', str(self.Value))
		if self.CurveControl1X not in [None, 0.5]: xmltag.set('CurveControl1X', str(self.CurveControl1X))
		if self.CurveControl1Y not in [None, 0.5]: xmltag.set('CurveControl1Y', str(self.CurveControl1Y))
		if self.CurveControl2X not in [None, 0.5]: xmltag.set('CurveControl2X', str(self.CurveControl2X))
		if self.CurveControl2Y not in [None, 0.5]: xmltag.set('CurveControl2Y', str(self.CurveControl2Y))

class ableton_EnumEvent:
	__slots__ = ['Time','Value']
	def __init__(self, xmltag):
		self.Time = float(xmltag.get('Time')) if xmltag != None else 0
		self.Value = int(xmltag.get('Value')) if xmltag != None else 0

	def write(self, xmltag):
		xmltag.set('Time', str(self.Time))
		xmltag.set('Value', str(self.Value))

class ableton_BoolEvent:
	__slots__ = ['Time','Value']
	def __init__(self, xmltag):
		self.Time = float(xmltag.get('Time')) if xmltag != None else 0
		self.Value = bool(['false','true'].index(xmltag.get('Value'))) if xmltag != None else False

	def write(self, xmltag):
		xmltag.set('Time', str(self.Time))
		xmltag.set('Value', str(['false','true'][self.Value]))

class ableton_Automation:
	__slots__ = ['tracktype','Events', 'name']
	def __init__(self, xmltag, name):
		self.Events = []
		self.name = name
		if xmltag:
			x_ArrangerAutomation = xmltag.findall(self.name)[0]
			x_Events = x_ArrangerAutomation.findall('Events')[0]
			for x_Event in x_Events:
				event_id = int(x_Event.get('Id'))
				if x_Event.tag == 'AudioClip': self.Events.append([event_id, 'AudioClip', ableton_AudioClip(x_Event)])
				if x_Event.tag == 'MidiClip': self.Events.append([event_id, 'MidiClip', ableton_MidiClip(x_Event)])
				if x_Event.tag == 'FloatEvent': self.Events.append([event_id, 'FloatEvent', ableton_FloatEvent(x_Event)])
				if x_Event.tag == 'EnumEvent': self.Events.append([event_id, 'EnumEvent', ableton_EnumEvent(x_Event)])
				if x_Event.tag == 'BoolEvent': self.Events.append([event_id, 'BoolEvent', ableton_BoolEvent(x_Event)])

	def write(self, xmltag):
		x_ArrangerAutomation = ET.SubElement(xmltag, self.name)

		x_Events = ET.SubElement(x_ArrangerAutomation, "Events")

		for n, t, o in self.Events: 
			x_Event = ET.SubElement(x_Events, t)
			x_Event.set('Id', str(n))
			o.write(x_Event)

		x_AutomationTransformViewState = ET.SubElement(x_ArrangerAutomation, "AutomationTransformViewState")
		add_bool(x_AutomationTransformViewState, 'IsTransformPending', False)
		ET.SubElement(x_AutomationTransformViewState, "TimeAndValueTransforms")

class ableton_RemoteableTimeSignature:
	__slots__ = ['Numerator','Denominator','Time']
	def __init__(self, xmltag):
		self.Numerator = int(get_value(xmltag, 'Numerator', 4))
		self.Denominator = int(get_value(xmltag, 'Denominator', 4))
		self.Time = float(get_value(xmltag, 'Time', 0))

	def write(self, xmltag):
		add_value(xmltag, 'Numerator', self.Numerator)
		add_value(xmltag, 'Denominator', self.Denominator)
		add_value(xmltag, 'Time', self.Time)

class ableton_Loop:
	__slots__ = ['LoopStart','LoopEnd','StartRelative','LoopOn','OutMarker','HiddenLoopStart','HiddenLoopEnd']
	def __init__(self, xmltag):
		if xmltag:
			x_Loop = xmltag.findall('Loop')[0]
			self.LoopStart = float(get_value(x_Loop, 'LoopStart', 0))
			self.LoopEnd = float(get_value(x_Loop, 'LoopEnd', 4))
			self.StartRelative = float(get_value(x_Loop, 'StartRelative', 0))
			self.LoopOn = get_bool(x_Loop, 'LoopOn', False)
			self.OutMarker = float(get_value(x_Loop, 'OutMarker', 4))
			self.HiddenLoopStart = float(get_value(x_Loop, 'HiddenLoopStart', 0))
			self.HiddenLoopEnd = float(get_value(x_Loop, 'HiddenLoopEnd', 4))
		else:
			self.LoopStart = 0
			self.LoopEnd = 4
			self.StartRelative = 0
			self.LoopOn = False
			self.OutMarker = 4
			self.HiddenLoopStart = 0
			self.HiddenLoopEnd = 4

	def write(self, xmltag):
		x_Loop = ET.SubElement(xmltag, "Loop")
		add_value(x_Loop, 'LoopStart', self.LoopStart)
		add_value(x_Loop, 'LoopEnd', self.LoopEnd)
		add_value(x_Loop, 'StartRelative', self.StartRelative)
		add_bool(x_Loop, 'LoopOn', self.LoopOn)
		add_value(x_Loop, 'OutMarker', self.OutMarker)
		add_value(x_Loop, 'HiddenLoopStart', self.HiddenLoopStart)
		add_value(x_Loop, 'HiddenLoopEnd', self.HiddenLoopEnd)

class ableton_Grid:
	__slots__ = ['name','FixedNumerator','FixedDenominator','GridIntervalPixel','Ntoles','SnapToGrid','Fixed']
	def __init__(self, xmltag, name):
		self.name = name
		if xmltag:
			x_Grid = xmltag.findall(name)[0]
			self.FixedNumerator = int(get_value(x_Grid, 'FixedNumerator', 1))
			self.FixedDenominator = int(get_value(x_Grid, 'FixedDenominator', 16))
			self.GridIntervalPixel = int(get_value(x_Grid, 'GridIntervalPixel', 20))
			self.Ntoles = int(get_value(x_Grid, 'Ntoles', 2))
			self.SnapToGrid = get_bool(x_Grid, 'SnapToGrid', True)
			self.Fixed = get_bool(x_Grid, 'Fixed', True)
		else:
			self.FixedNumerator = 1
			self.FixedDenominator = 16
			self.GridIntervalPixel = 20
			self.Ntoles = 2
			self.SnapToGrid = True
			self.Fixed = False

	def write(self, xmltag):
		x_Grid = ET.SubElement(xmltag, self.name)
		add_value(x_Grid, 'FixedNumerator', self.FixedNumerator)
		add_value(x_Grid, 'FixedDenominator', self.FixedDenominator)
		add_value(x_Grid, 'GridIntervalPixel', self.GridIntervalPixel)
		add_value(x_Grid, 'Ntoles', self.Ntoles)
		add_bool(x_Grid, 'SnapToGrid', self.SnapToGrid)
		add_bool(x_Grid, 'Fixed', self.Fixed)

class ableton_FollowAction:
	__slots__ = ['FollowTime','IsLinked','LoopIterations','FollowActionA','FollowActionB','FollowChanceA','FollowChanceB','JumpIndexA','JumpIndexB','FollowActionEnabled']
	def __init__(self, xmltag):
		if xmltag:
			x_FollowAction = xmltag.findall('FollowAction')[0]
			self.FollowTime = int(get_value(x_FollowAction, 'FollowTime', 4))
			self.IsLinked = get_bool(x_FollowAction, 'IsLinked', True)
			self.LoopIterations = int(get_value(x_FollowAction, 'LoopIterations', 1))
			self.FollowActionA = int(get_value(x_FollowAction, 'FollowActionA', 4))
			self.FollowActionB = int(get_value(x_FollowAction, 'FollowActionB', 0))
			self.FollowChanceA = int(get_value(x_FollowAction, 'FollowChanceA', 100))
			self.FollowChanceB = int(get_value(x_FollowAction, 'FollowChanceB', 0))
			self.JumpIndexA = int(get_value(x_FollowAction, 'JumpIndexA', 1))
			self.JumpIndexB = int(get_value(x_FollowAction, 'JumpIndexB', 1))
			self.FollowActionEnabled = get_bool(x_FollowAction, 'FollowActionEnabled', False)
		else:
			self.FollowTime = 4
			self.IsLinked = True
			self.LoopIterations = 1
			self.FollowActionA = 4
			self.FollowActionB = 0
			self.FollowChanceA = 100
			self.FollowChanceB = 0
			self.JumpIndexA = 0
			self.JumpIndexB = 0
			self.FollowActionEnabled = False

	def write(self, xmltag):
		x_FollowAction = ET.SubElement(xmltag, "FollowAction")
		add_value(x_FollowAction, 'FollowTime', self.FollowTime)
		add_bool(x_FollowAction, 'IsLinked', self.IsLinked)
		add_value(x_FollowAction, 'LoopIterations', self.LoopIterations)
		add_value(x_FollowAction, 'FollowActionA', self.FollowActionA)
		add_value(x_FollowAction, 'FollowActionB', self.FollowActionB)
		add_value(x_FollowAction, 'FollowChanceA', self.FollowChanceA)
		add_value(x_FollowAction, 'FollowChanceB', self.FollowChanceB)
		add_value(x_FollowAction, 'JumpIndexA', self.JumpIndexA)
		add_value(x_FollowAction, 'JumpIndexB', self.JumpIndexB)
		add_bool(x_FollowAction, 'FollowActionEnabled', self.FollowActionEnabled)

class ableton_TimeSelection:
	__slots__ = ['AnchorTime','OtherTime']
	def __init__(self, xmltag):
		if xmltag:
			x_TimeSelection = xmltag.findall('TimeSelection')[0]
			self.AnchorTime = float(get_value(x_TimeSelection, 'AnchorTime', 0))
			self.OtherTime = float(get_value(x_TimeSelection, 'OtherTime', 0))
		else:
			self.AnchorTime = 0
			self.OtherTime = 0

	def write(self, xmltag):
		x_TimeSelection = ET.SubElement(xmltag, "TimeSelection")
		add_value(x_TimeSelection, 'AnchorTime', self.AnchorTime)
		add_value(x_TimeSelection, 'OtherTime', self.OtherTime)

class ableton_ScaleInformation:
	__slots__ = ['RootNote','Name']
	def __init__(self, xmltag):
		if xmltag:
			x_ScaleInformation = xmltag.findall('ScaleInformation')[0]
			self.RootNote = float(get_value(x_ScaleInformation, 'RootNote', 0))
			self.Name = get_value(x_ScaleInformation, 'Name', '')
		else:
			self.RootNote = 0
			self.Name = 'Major'

	def write(self, xmltag):
		x_ScaleInformation = ET.SubElement(xmltag, "ScaleInformation")
		add_value(x_ScaleInformation, 'RootNote', self.RootNote)
		add_value(x_ScaleInformation, 'Name', self.Name)

class ableton_GrooveSettings:
	__slots__ = ['GrooveId']
	def __init__(self, xmltag):
		if xmltag:
			x_GrooveSettings = xmltag.findall('GrooveSettings')[0]
			self.GrooveId = float(get_value(x_GrooveSettings, 'GrooveId', -1))
		else:
			self.GrooveId = -1

	def write(self, xmltag):
		x_GrooveSettings = ET.SubElement(xmltag, "GrooveSettings")
		add_value(x_GrooveSettings, 'GrooveId', self.GrooveId)

class ableton_ScrollerTimePreserver:
	__slots__ = ['LeftTime','RightTime']
	def __init__(self, xmltag):
		if xmltag:
			x_Loop = xmltag.findall('ScrollerTimePreserver')[0]
			self.LeftTime = float(get_value(x_Loop, 'LeftTime', 0))
			self.RightTime = float(get_value(x_Loop, 'RightTime', 16))
		else:
			self.LeftTime = 0
			self.RightTime = 16

	def write(self, xmltag):
		x_ScrollerTimePreserver = ET.SubElement(xmltag, "ScrollerTimePreserver")
		add_value(x_ScrollerTimePreserver, 'LeftTime', self.LeftTime)
		add_value(x_ScrollerTimePreserver, 'RightTime', self.RightTime)

class ableton_x_MidiNoteEvent:
	__slots__ = ['Time','Duration','Velocity','VelocityDeviation','OffVelocity','Probability','IsEnabled','NoteId']
	def __init__(self, xmltag):
		if xmltag != None:
			self.Time = float(xmltag.get('Time'))
			self.Duration = float(xmltag.get('Duration'))
			self.Velocity = float(xmltag.get('Velocity'))
			self.VelocityDeviation = int(xmltag.get('VelocityDeviation'))
			self.OffVelocity = int(xmltag.get('OffVelocity'))
			self.Probability = int(xmltag.get('Probability'))
			self.IsEnabled = bool(['false','true'].index(xmltag.get('IsEnabled')))
			self.NoteId = int(xmltag.get('NoteId'))
		else:
			self.Time = 1.25
			self.Duration = 0.75
			self.Velocity = 100
			self.VelocityDeviation = 0
			self.OffVelocity = 64
			self.Probability = 1
			self.IsEnabled = True
			self.NoteId = 0

	def write(self, xmltag):
		x_MidiNoteEvent = ET.SubElement(xmltag, "MidiNoteEvent")
		x_MidiNoteEvent.set('Time', str(self.Time))
		x_MidiNoteEvent.set('Duration', str(self.Duration))
		x_MidiNoteEvent.set('Velocity', str(self.Velocity))
		x_MidiNoteEvent.set('VelocityDeviation', str(self.VelocityDeviation))
		x_MidiNoteEvent.set('OffVelocity', str(self.OffVelocity))
		x_MidiNoteEvent.set('Probability', str(self.Probability))
		x_MidiNoteEvent.set('IsEnabled',  ['false','true'][self.IsEnabled])
		x_MidiNoteEvent.set('NoteId', str(self.NoteId))

class ableton_KeyTrack:
	__slots__ = ['MidiKey','NoteEvents']
	def __init__(self, xmltag):
		self.NoteEvents = []
		if xmltag:
			self.MidiKey = int(get_value(xmltag, 'MidiKey', 60))
			x_Notes = xmltag.findall('Notes')[0]
			self.NoteEvents = [ableton_x_MidiNoteEvent(x) for x in x_Notes.findall('MidiNoteEvent')]
		else:
			self.MidiKey = 60

	def write(self, xmltag):
		x_Notes = ET.SubElement(xmltag, "Notes")
		add_value(xmltag, 'MidiKey', self.MidiKey)
		for x in self.NoteEvents:
			x.write(x_Notes)

class ableton_x_PerNoteEvent:
	__slots__ = ['TimeOffset','Value','CurveControl1X','CurveControl1Y','CurveControl2X','CurveControl2Y']
	def __init__(self, xmltag):
		if xmltag != None:
			self.TimeOffset = float(xmltag.get('TimeOffset'))
			self.Value = float(xmltag.get('Value'))
			self.CurveControl1X = float(xmltag.get('CurveControl1X'))
			self.CurveControl1Y = float(xmltag.get('CurveControl1Y'))
			self.CurveControl2X = float(xmltag.get('CurveControl2X'))
			self.CurveControl2Y = float(xmltag.get('CurveControl2Y'))
		else:
			self.TimeOffset = 0
			self.Value = 0
			self.CurveControl1X = 0.5
			self.CurveControl1Y = 0.5
			self.CurveControl2X = 0.5
			self.CurveControl2Y = 0.5

	def write(self, xmltag):
		x_MidiNoteEvent = ET.SubElement(xmltag, "PerNoteEvent")
		x_MidiNoteEvent.set('TimeOffset', str(self.TimeOffset))
		x_MidiNoteEvent.set('Value', str(self.Value))
		x_MidiNoteEvent.set('CurveControl1X', str(self.CurveControl1X))
		x_MidiNoteEvent.set('CurveControl1Y', str(self.CurveControl1Y))
		x_MidiNoteEvent.set('CurveControl2X', str(self.CurveControl2X))
		x_MidiNoteEvent.set('CurveControl2Y', str(self.CurveControl2Y))

class ableton_PerNoteEventList:
	__slots__ = ['NoteId','CC','Events']
	def __init__(self, xmltag):
		self.NoteId = int(xmltag.get('NoteId'))
		self.CC = int(xmltag.get('CC'))
		x_Events = xmltag.findall('Events')[0]
		self.Events = [ableton_x_PerNoteEvent(x) for x in x_Events.findall('PerNoteEvent')]

	def write(self, xmltag):
		xmltag.set('NoteId', str(self.NoteId))
		xmltag.set('CC', str(self.CC))
		x_Events = ET.SubElement(xmltag, "Events")
		for x in self.Events:
			x.write(x_Events)

class ableton_Notes:
	__slots__ = ['KeyTrack','NoteNextId','PerNoteEventStore']
	def __init__(self, xmltag):
		self.KeyTrack = {}
		self.PerNoteEventStore = {}
		self.NoteNextId = 0
		if xmltag:
			x_Notes = xmltag.findall('Notes')[0]
			self.KeyTrack = get_list(x_Notes, 'KeyTracks', 'KeyTrack', ableton_KeyTrack)
			x_NoteIdGenerator = x_Notes.findall('NoteIdGenerator')
			if x_NoteIdGenerator: self.NoteNextId = get_value(x_NoteIdGenerator[0], 'NextId', 0)
			x_PerNoteEventStore = x_Notes.findall('PerNoteEventStore')[0]
			self.PerNoteEventStore = get_list(x_PerNoteEventStore, 'EventLists', 'PerNoteEventList', ableton_PerNoteEventList)

	def write(self, xmltag):
		x_Notes = ET.SubElement(xmltag, "Notes")
		set_list(x_Notes, self.KeyTrack, "KeyTracks", "KeyTrack")
		x_PerNoteEventStore = ET.SubElement(x_Notes, "PerNoteEventStore")
		set_list(x_PerNoteEventStore, self.PerNoteEventStore, "EventLists", "PerNoteEventList")
		x_NoteIdGenerator = ET.SubElement(x_Notes, "NoteIdGenerator")
		add_value(x_NoteIdGenerator, 'NextId', self.NoteNextId)

class ableton_OnsetEvent:
	__slots__ = ['Time','Energy','IsVolatile']
	def __init__(self, xmltag):
		energy = xmltag.get('Energy')
		self.Time = float(xmltag.get('Time')) if xmltag != None else 0
		self.Energy = (float(energy) if energy != 'Invalid' else energy) if xmltag != None else 0
		self.IsVolatile = bool(['false','true'].index(xmltag.get('IsVolatile'))) if xmltag != None else False

	def write(self, xmltag):
		xmltag.set('Time', str(self.Time))
		xmltag.set('Energy', str(self.Energy))
		xmltag.set('IsVolatile', str(['false','true'][int(self.IsVolatile)]))

class ableton_Onsets:
	__slots__ = ['HasUserOnsets','UserOnsets']
	def __init__(self, xmltag):
		self.UserOnsets = []
		self.HasUserOnsets = get_bool(xmltag, 'HasUserOnsets', True)
		x_UserOnsets = xmltag.findall('UserOnsets')[0]
		for x in x_UserOnsets:
			if x.tag == 'OnsetEvent': self.UserOnsets.append(ableton_OnsetEvent(x))

	def write(self, xmltag):
		x_UserOnsets = ET.SubElement(xmltag, "UserOnsets")
		for x in self.UserOnsets:
			x_OnsetEvent = ET.SubElement(x_UserOnsets, "OnsetEvent")
			x.write(x_OnsetEvent)
		add_bool(xmltag, 'HasUserOnsets', self.HasUserOnsets)

class ableton_Fades:
	def __init__(self, xmltag):
		self.FadeInLength = float(get_value(xmltag, 'FadeInLength', 0))
		self.FadeOutLength = float(get_value(xmltag, 'FadeOutLength', 0))
		self.ClipFadesAreInitialized = get_bool(xmltag, 'ClipFadesAreInitialized', True)
		self.CrossfadeInState = float(get_value(xmltag, 'CrossfadeInState', 0))
		self.FadeInCurveSkew = float(get_value(xmltag, 'FadeInCurveSkew', 0))
		self.FadeInCurveSlope = float(get_value(xmltag, 'FadeInCurveSlope', 0))
		self.FadeOutCurveSkew = float(get_value(xmltag, 'FadeOutCurveSkew', 0))
		self.FadeOutCurveSlope = float(get_value(xmltag, 'FadeOutCurveSlope', 0))
		self.IsDefaultFadeIn = get_bool(xmltag, 'IsDefaultFadeIn', True)
		self.IsDefaultFadeOut = get_bool(xmltag, 'IsDefaultFadeOut', True)

	def write(self, xmltag):
		add_value(xmltag, 'FadeInLength', self.FadeInLength)
		add_value(xmltag, 'FadeOutLength', self.FadeOutLength)
		add_bool(xmltag, 'ClipFadesAreInitialized', self.ClipFadesAreInitialized)
		add_value(xmltag, 'CrossfadeInState', self.CrossfadeInState)
		add_value(xmltag, 'FadeInCurveSkew', self.FadeInCurveSkew)
		add_value(xmltag, 'FadeInCurveSlope', self.FadeInCurveSlope)
		add_value(xmltag, 'FadeOutCurveSkew', self.FadeOutCurveSkew)
		add_value(xmltag, 'FadeOutCurveSlope', self.FadeOutCurveSlope)
		add_bool(xmltag, 'IsDefaultFadeIn', self.IsDefaultFadeIn)
		add_bool(xmltag, 'IsDefaultFadeOut', self.IsDefaultFadeOut)

class ableton_WarpMarker:
	def __init__(self, xmltag):
		if xmltag != None:
			self.SecTime = float(xmltag.get('SecTime'))
			self.BeatTime = float(xmltag.get('BeatTime'))
		else:
			self.SecTime = 0
			self.BeatTime = 0

	def write(self, xmltag):
		xmltag.set('SecTime', str(self.SecTime))
		xmltag.set('BeatTime', str(self.BeatTime))

class ableton_TakeLanes:
	def __init__(self, xmltag):
		if xmltag:
			x_TakeLanes = xmltag.findall('TakeLanes')[0]
			self.AreTakeLanesFolded = get_bool(x_TakeLanes, 'AreTakeLanesFolded', False)
			self.TakeLanes = get_list(x_TakeLanes, 'TakeLanes', 'TakeLane', ableton_TakeLane)
		else:
			self.AreTakeLanesFolded = True
			self.TakeLanes = {}

	def write(self, xmltag):
		x_TakeLanes = ET.SubElement(xmltag, "TakeLanes")
		set_list(x_TakeLanes, self.TakeLanes, "TakeLanes", "TakeLane")
		add_bool(x_TakeLanes, 'AreTakeLanesFolded', self.AreTakeLanesFolded)


class ableton_AudioClip:
	def __init__(self, xmltag):
		self.Time = float(xmltag.get('Time'))
		self.LomId = ableton_LomId(xmltag)
		self.CurrentStart = float(get_value(xmltag, 'CurrentStart', 0))
		self.CurrentEnd = float(get_value(xmltag, 'CurrentEnd', 16))
		self.Loop = ableton_Loop(xmltag)
		self.Name = get_value(xmltag, 'Name', '')
		self.Annotation = get_value(xmltag, 'Annotation', '')
		self.Color = int(get_value(xmltag, 'Color', 2))

		self.LaunchMode = int(get_value(xmltag, 'LaunchMode', 0))
		self.LaunchQuantisation = int(get_value(xmltag, 'LaunchQuantisation', 0))
		if xmltag:
			x_TimeSignature = xmltag.findall('TimeSignature')[0]
			self.TimeSignatures = get_list(x_TimeSignature, 'TimeSignatures', 'RemoteableTimeSignature', ableton_RemoteableTimeSignature)
			x_Envelopes = xmltag.findall('Envelopes')[0]
			self.Envelopes = get_list(x_Envelopes, 'Envelopes', 'ClipEnvelope', ableton_AutomationEnvelope)
		else:
			self.TimeSignatures = {}
			self.Envelopes = {}

		self.ScrollerTimePreserver = ableton_ScrollerTimePreserver(xmltag)
		self.TimeSelection = ableton_TimeSelection(xmltag)
		self.Legato = get_bool(xmltag, 'Legato', False)
		self.Ram = get_bool(xmltag, 'Ram', False)
		self.GrooveSettings = ableton_GrooveSettings(xmltag)
		self.Disabled = get_bool(xmltag, 'Disabled', False)
		self.VelocityAmount = int(get_value(xmltag, 'VelocityAmount', 0))
		self.FollowAction = ableton_FollowAction(xmltag)
		self.Grid = ableton_Grid(xmltag, 'Grid')
		self.FreezeStart = float(get_value(xmltag, 'FreezeStart', 0))
		self.FreezeEnd = float(get_value(xmltag, 'FreezeEnd', 0))
		self.IsWarped = get_bool(xmltag, 'IsWarped', True)
		self.TakeId = int(get_value(xmltag, 'TakeId', 1))
		self.SampleRef = ableton_SampleRef(xmltag)
		self.Onsets = ableton_Onsets(xmltag.findall('Onsets')[0])

		self.WarpMode = int(get_value(xmltag, 'WarpMode', 0))
		self.GranularityTones = float(get_value(xmltag, 'GranularityTones', 30))
		self.GranularityTexture = float(get_value(xmltag, 'GranularityTexture', 65))
		self.FluctuationTexture = float(get_value(xmltag, 'FluctuationTexture', 25))
		self.TransientResolution = int(get_value(xmltag, 'TransientResolution', 6))
		self.TransientLoopMode = int(get_value(xmltag, 'TransientLoopMode', 2))
		self.TransientEnvelope = int(get_value(xmltag, 'TransientEnvelope', 100))
		self.ComplexProFormants = float(get_value(xmltag, 'ComplexProFormants', 100))
		self.ComplexProEnvelope = int(get_value(xmltag, 'ComplexProEnvelope', 128))
		self.Sync = get_bool(xmltag, 'Sync', True)
		self.HiQ = get_bool(xmltag, 'HiQ', True)
		self.Fade = get_bool(xmltag, 'Fade', True)
		self.Fades = ableton_Fades(xmltag.findall('Fades')[0])
		self.PitchCoarse = float(get_value(xmltag, 'PitchCoarse', 0))
		self.PitchFine = float(get_value(xmltag, 'PitchFine', 0))
		self.SampleVolume = float(get_value(xmltag, 'SampleVolume', 1))
		self.MarkerDensity = float(get_value(xmltag, 'MarkerDensity', 2))
		self.AutoWarpTolerance = int(get_value(xmltag, 'AutoWarpTolerance', 4))
		self.WarpMarkers = get_list(xmltag, 'WarpMarkers', 'WarpMarker', ableton_WarpMarker)
		self.SavedWarpMarkersForStretched = get_list(xmltag, 'SavedWarpMarkersForStretched', 'WarpMarker', ableton_WarpMarker)
		self.MarkersGenerated = get_bool(xmltag, 'MarkersGenerated', False)
		self.IsSongTempoMaster = get_bool(xmltag, 'IsSongTempoMaster', False)

	def write(self, xmltag):
		xmltag.set('Time', "%g"%self.Time)
		self.LomId.write(xmltag)
		add_value(xmltag, 'CurrentStart', self.CurrentStart)
		add_value(xmltag, 'CurrentEnd', self.CurrentEnd)
		self.Loop.write(xmltag)
		add_value(xmltag, 'Name', self.Name)
		add_value(xmltag, 'Annotation', self.Annotation)
		add_value(xmltag, 'Color', self.Color)
		add_value(xmltag, 'LaunchMode', self.LaunchMode)
		add_value(xmltag, 'LaunchQuantisation', self.LaunchQuantisation)
		x_TimeSignature = ET.SubElement(xmltag, "TimeSignature")
		set_list(x_TimeSignature, self.TimeSignatures, "TimeSignatures", "RemoteableTimeSignature")
		x_Envelopes = ET.SubElement(xmltag, "Envelopes")
		set_list(x_Envelopes, self.Envelopes, "Envelopes", "ClipEnvelope")
		self.ScrollerTimePreserver.write(xmltag)
		self.TimeSelection.write(xmltag)
		add_bool(xmltag, 'Legato', self.Legato)
		add_bool(xmltag, 'Ram', self.Ram)
		self.GrooveSettings.write(xmltag)
		add_bool(xmltag, 'Disabled', self.Disabled)
		add_value(xmltag, 'VelocityAmount', self.VelocityAmount)
		self.FollowAction.write(xmltag)
		self.Grid.write(xmltag)
		add_value(xmltag, 'FreezeStart', self.FreezeStart)
		add_value(xmltag, 'FreezeEnd', self.FreezeEnd)
		add_bool(xmltag, 'IsWarped', self.IsWarped)
		add_value(xmltag, 'TakeId', self.TakeId)
		self.SampleRef.write(xmltag)
		x_Onsets = ET.SubElement(xmltag, "Onsets")
		self.Onsets.write(x_Onsets)

		add_value(xmltag, 'WarpMode', self.WarpMode)
		add_value(xmltag, 'GranularityTones', self.GranularityTones)
		add_value(xmltag, 'GranularityTexture', self.GranularityTexture)
		add_value(xmltag, 'FluctuationTexture', self.FluctuationTexture)
		add_value(xmltag, 'TransientResolution', self.TransientResolution)
		add_value(xmltag, 'TransientLoopMode', self.TransientLoopMode)
		add_value(xmltag, 'TransientEnvelope', self.TransientEnvelope)
		add_value(xmltag, 'ComplexProFormants', self.ComplexProFormants)
		add_value(xmltag, 'ComplexProEnvelope', self.ComplexProEnvelope)
		add_bool(xmltag, 'Sync', self.Sync)
		add_bool(xmltag, 'HiQ', self.HiQ)
		add_bool(xmltag, 'Fade', self.Fade)
		x_Fades = ET.SubElement(xmltag, "Fades")
		self.Fades.write(x_Fades)
		add_value(xmltag, 'PitchCoarse', self.PitchCoarse)
		add_value(xmltag, 'PitchFine', self.PitchFine)
		add_value(xmltag, 'SampleVolume', self.SampleVolume)
		add_value(xmltag, 'MarkerDensity', self.MarkerDensity)
		add_value(xmltag, 'AutoWarpTolerance', self.AutoWarpTolerance)
		set_list(xmltag, self.WarpMarkers, 'WarpMarkers', 'WarpMarker')
		set_list(xmltag, self.SavedWarpMarkersForStretched, 'SavedWarpMarkersForStretched', 'WarpMarker')
		add_bool(xmltag, 'MarkersGenerated', self.MarkersGenerated)
		add_bool(xmltag, 'IsSongTempoMaster', self.IsSongTempoMaster)

class ableton_MidiClip:
	def __init__(self, xmltag):
		self.Time = float(xmltag.get('Time'))
		self.LomId = ableton_LomId(xmltag)
		self.CurrentStart = float(get_value(xmltag, 'CurrentStart', 0))
		self.CurrentEnd = float(get_value(xmltag, 'CurrentEnd', 16))
		self.Loop = ableton_Loop(xmltag)
		self.Name = get_value(xmltag, 'Name', '')
		self.Annotation = get_value(xmltag, 'Annotation', '')
		self.Color = int(get_value(xmltag, 'Color', 2))

		self.LaunchMode = int(get_value(xmltag, 'LaunchMode', 0))
		self.LaunchQuantisation = int(get_value(xmltag, 'LaunchQuantisation', 0))
		if xmltag:
			x_TimeSignature = xmltag.findall('TimeSignature')[0]
			self.TimeSignatures = get_list(x_TimeSignature, 'TimeSignatures', 'RemoteableTimeSignature', ableton_RemoteableTimeSignature)
		else:
			self.TimeSignatures = {}
		self.ScrollerTimePreserver = ableton_ScrollerTimePreserver(xmltag)
		self.TimeSelection = ableton_TimeSelection(xmltag)
		self.Legato = get_bool(xmltag, 'Legato', False)
		self.Ram = get_bool(xmltag, 'Ram', False)
		self.GrooveSettings = ableton_GrooveSettings(xmltag)
		self.Disabled = get_bool(xmltag, 'Disabled', False)
		self.VelocityAmount = int(get_value(xmltag, 'VelocityAmount', 0))
		self.FollowAction = ableton_FollowAction(xmltag)
		self.Grid = ableton_Grid(xmltag, 'Grid')
		self.FreezeStart = float(get_value(xmltag, 'FreezeStart', 0))
		self.FreezeEnd = float(get_value(xmltag, 'FreezeEnd', 0))
		self.IsWarped = get_bool(xmltag, 'IsWarped', True)
		self.TakeId = int(get_value(xmltag, 'TakeId', 1))
		self.Notes = ableton_Notes(xmltag)

		self.BankSelectCoarse = int(get_value(xmltag, 'BankSelectCoarse', -1))
		self.BankSelectFine = int(get_value(xmltag, 'BankSelectFine', -1))
		self.ProgramChange = int(get_value(xmltag, 'ProgramChange', -1))
		self.NoteEditorFoldInZoom = int(get_value(xmltag, 'NoteEditorFoldInZoom', -1))
		self.NoteEditorFoldInScroll = int(get_value(xmltag, 'NoteEditorFoldInScroll', 0))
		self.NoteEditorFoldOutZoom = int(get_value(xmltag, 'NoteEditorFoldOutZoom', 847))
		self.NoteEditorFoldOutScroll = int(get_value(xmltag, 'NoteEditorFoldOutScroll', -364))
		self.NoteEditorFoldScaleZoom = int(get_value(xmltag, 'NoteEditorFoldScaleZoom', -1))
		self.NoteEditorFoldScaleScroll = int(get_value(xmltag, 'NoteEditorFoldScaleScroll', 0))

		self.ScaleInformation = ableton_ScaleInformation(xmltag)
		self.IsInKey = get_bool(xmltag, 'IsInKey', False)
		self.NoteSpellingPreference = int(get_value(xmltag, 'NoteSpellingPreference', 3))
		self.PreferFlatRootNote = get_bool(xmltag, 'PreferFlatRootNote', False)
		self.ExpressionGrid = ableton_Grid(xmltag, 'ExpressionGrid')

	def write(self, xmltag):
		xmltag.set('Time', "%g"%self.Time)
		self.LomId.write(xmltag)
		add_value(xmltag, 'CurrentStart', self.CurrentStart)
		add_value(xmltag, 'CurrentEnd', self.CurrentEnd)
		self.Loop.write(xmltag)
		add_value(xmltag, 'Name', self.Name)
		add_value(xmltag, 'Annotation', self.Annotation)
		add_value(xmltag, 'Color', self.Color)
		add_value(xmltag, 'LaunchMode', self.LaunchMode)
		add_value(xmltag, 'LaunchQuantisation', self.LaunchQuantisation)
		x_TimeSignature = ET.SubElement(xmltag, "TimeSignature")
		set_list(x_TimeSignature, self.TimeSignatures, "TimeSignatures", "RemoteableTimeSignature")
		x_Envelopes = ET.SubElement(xmltag, "Envelopes")
		ET.SubElement(x_Envelopes, "Envelopes")
		self.ScrollerTimePreserver.write(xmltag)
		self.TimeSelection.write(xmltag)
		add_bool(xmltag, 'Legato', self.Legato)
		add_bool(xmltag, 'Ram', self.Ram)
		self.GrooveSettings.write(xmltag)
		add_bool(xmltag, 'Disabled', self.Disabled)
		add_value(xmltag, 'VelocityAmount', self.VelocityAmount)
		self.FollowAction.write(xmltag)
		self.Grid.write(xmltag)
		add_value(xmltag, 'FreezeStart', self.FreezeStart)
		add_value(xmltag, 'FreezeEnd', self.FreezeEnd)
		add_bool(xmltag, 'IsWarped', self.IsWarped)
		add_value(xmltag, 'TakeId', self.TakeId)
		self.Notes.write(xmltag)

		add_value(xmltag, 'BankSelectCoarse', self.BankSelectCoarse)
		add_value(xmltag, 'BankSelectFine', self.BankSelectFine)
		add_value(xmltag, 'ProgramChange', self.ProgramChange)
		add_value(xmltag, 'NoteEditorFoldInZoom', self.NoteEditorFoldInZoom)
		add_value(xmltag, 'NoteEditorFoldInScroll', self.NoteEditorFoldInScroll)
		add_value(xmltag, 'NoteEditorFoldOutZoom', self.NoteEditorFoldOutZoom)
		add_value(xmltag, 'NoteEditorFoldOutScroll', self.NoteEditorFoldOutScroll)
		add_value(xmltag, 'NoteEditorFoldScaleZoom', self.NoteEditorFoldScaleZoom)
		add_value(xmltag, 'NoteEditorFoldScaleScroll', self.NoteEditorFoldScaleScroll)
		self.ScaleInformation.write(xmltag)
		add_bool(xmltag, 'IsInKey', self.IsInKey)
		add_value(xmltag, 'NoteSpellingPreference', self.NoteSpellingPreference)
		add_bool(xmltag, 'PreferFlatRootNote', self.PreferFlatRootNote)
		self.ExpressionGrid.write(xmltag)

class ableton_Recorder:
	__slots__ = ['IsArmed','TakeCounter','exists']
	def __init__(self, xmltag):
		self.exists = False
		self.IsArmed = False
		self.TakeCounter = 1
		if xmltag:
			x_Recorder = xmltag.findall('Recorder')
			if x_Recorder:
				self.exists = True
				self.IsArmed = get_bool(x_Recorder[0], 'IsArmed', False)
				self.TakeCounter = int(get_value(x_Recorder[0], 'TakeCounter', 0))

	def write(self, xmltag):
		x_Recorder = ET.SubElement(xmltag, "Recorder")
		add_bool(x_Recorder, 'IsArmed', self.IsArmed)
		add_value(x_Recorder, 'TakeCounter', self.TakeCounter)

class ableton_ClipSlot:
	__slots__ = ['HasStop','NeedRefreeze']
	def __init__(self, xmltag):
		self.HasStop = get_bool(xmltag, 'HasStop', True)
		self.NeedRefreeze = get_bool(xmltag, 'NeedRefreeze', True)

	def write(self, xmltag):
		add_value(xmltag, 'LomId', 0)
		x_ClipSlot = ET.SubElement(xmltag, "ClipSlot")
		ET.SubElement(x_ClipSlot, "Value")
		add_bool(xmltag, 'HasStop', self.HasStop)
		add_bool(xmltag, 'NeedRefreeze', self.NeedRefreeze)

class ableton_MainSequencer:
	def __init__(self, xmltag, tracktype):

		self.tracktype = tracktype
		self.ClipSlotList = {}
		self.MidiControllers = {}
		self.LomId = ableton_LomId(xmltag)
		self.IsExpanded = get_bool(xmltag, 'IsExpanded', True)
		self.On = ableton_Param(xmltag, 'On', 'bool')
		self.ModulationSourceCount = int(get_value(xmltag, 'ModulationSourceCount', 0))
		self.Pointee = int(xmltag.findall('Pointee')[0].get('Id') if xmltag else counter_unused_id.get())
		self.LastSelectedTimeableIndex = int(get_value(xmltag, 'LastSelectedTimeableIndex', 0))
		self.LastSelectedClipEnvelopeIndex = int(get_value(xmltag, 'LastSelectedClipEnvelopeIndex', 0))
		self.IsFolded = get_bool(xmltag, 'IsFolded', False)
		self.ShouldShowPresetName = get_bool(xmltag, 'ShouldShowPresetName', False)
		self.UserName = get_value(xmltag, 'UserName', '')
		self.Annotation = get_value(xmltag, 'Annotation', '')
		if not xmltag:
			for n in range(8): self.ClipSlotList[n] = ableton_ClipSlot(None)
		else: self.ClipSlotList = get_list(xmltag, 'ClipSlotList', 'ClipSlot', ableton_ClipSlot)
		self.MonitoringEnum = int(get_value(xmltag, 'MonitoringEnum', 1))

		if self.tracktype == 'midi': 
			x_ClipTimeable = xmltag.findall('ClipTimeable')[0] if xmltag else None
			self.ClipTimeable = ableton_Automation(x_ClipTimeable, 'ArrangerAutomation')
		if self.tracktype == 'audio': 
			x_Sample = xmltag.findall('Sample')[0] if xmltag else None
			self.ClipTimeable = ableton_Automation(x_Sample, 'ArrangerAutomation')
			self.VolumeModulationTarget = ableton_ReceiveTarget(xmltag, 'VolumeModulationTarget')
			self.TranspositionModulationTarget = ableton_ReceiveTarget(xmltag, 'TranspositionModulationTarget')
			self.GrainSizeModulationTarget = ableton_ReceiveTarget(xmltag, 'GrainSizeModulationTarget')
			self.FluxModulationTarget = ableton_ReceiveTarget(xmltag, 'FluxModulationTarget')
			self.SampleOffsetModulationTarget = ableton_ReceiveTarget(xmltag, 'SampleOffsetModulationTarget')
			self.PitchViewScrollPosition = get_value(xmltag, 'PitchViewScrollPosition', -1073741824)
			self.SampleOffsetModulationScrollPosition = get_value(xmltag, 'SampleOffsetModulationScrollPosition', -1073741824)
		self.Recorder = ableton_Recorder(xmltag)
		self.MidiControllers = {}
		if self.tracktype == 'midi': 
			x_MidiControllers = xmltag.findall('MidiControllers')[0] if xmltag else []
			for ControllerTarget in x_MidiControllers:
				name, num = ControllerTarget.tag.split('.')
				if name == 'ControllerTargets': self.MidiControllers[num] = ableton_ReceiveTarget(x_MidiControllers, ControllerTarget.tag)

	def write(self, xmltag):
		x_MainSequencer = ET.SubElement(xmltag, "MainSequencer")
		self.LomId.write(x_MainSequencer)
		add_bool(x_MainSequencer, 'IsExpanded', self.IsExpanded)
		self.On.write(x_MainSequencer)
		add_value(x_MainSequencer, 'ModulationSourceCount', self.ModulationSourceCount)
		add_lomid(x_MainSequencer, 'ParametersListWrapper', 0)
		add_id(x_MainSequencer, 'Pointee', self.Pointee)
		add_value(x_MainSequencer, 'LastSelectedTimeableIndex', self.LastSelectedTimeableIndex)
		add_value(x_MainSequencer, 'LastSelectedClipEnvelopeIndex', self.LastSelectedClipEnvelopeIndex)
		x_LastPresetRef = ET.SubElement(x_MainSequencer, "LastPresetRef")
		ET.SubElement(x_LastPresetRef, "Value")
		ET.SubElement(x_MainSequencer, "LockedScripts")
		add_bool(x_MainSequencer, 'IsFolded', self.IsFolded)
		add_bool(x_MainSequencer, 'ShouldShowPresetName', self.ShouldShowPresetName)
		add_value(x_MainSequencer, 'UserName', self.UserName)
		add_value(x_MainSequencer, 'Annotation', self.Annotation)
		x_SourceContext = ET.SubElement(x_MainSequencer, "SourceContext")
		ET.SubElement(x_SourceContext, "Value")
		x_ClipSlotList = ET.SubElement(x_MainSequencer, "ClipSlotList")
		for nid, data in self.ClipSlotList.items():
			x_ClipSlot = ET.SubElement(x_ClipSlotList, "ClipSlot")
			x_ClipSlot.set('Id', str(nid))
			data.write(x_ClipSlot)
		add_value(x_MainSequencer, 'MonitoringEnum', self.MonitoringEnum)
		if self.tracktype == 'midi': 
			x_ClipTimeable = ET.SubElement(x_MainSequencer, "ClipTimeable")
			self.ClipTimeable.write(x_ClipTimeable)
		if self.tracktype == 'audio': 
			x_Sample = ET.SubElement(x_MainSequencer, "Sample")
			self.ClipTimeable.write(x_Sample)
			self.VolumeModulationTarget.write(x_MainSequencer)
			self.TranspositionModulationTarget.write(x_MainSequencer)
			self.GrainSizeModulationTarget.write(x_MainSequencer)
			self.FluxModulationTarget.write(x_MainSequencer)
			self.SampleOffsetModulationTarget.write(x_MainSequencer)
			add_value(x_MainSequencer, 'PitchViewScrollPosition', self.PitchViewScrollPosition)
			add_value(x_MainSequencer, 'SampleOffsetModulationScrollPosition', self.SampleOffsetModulationScrollPosition)
		self.Recorder.write(x_MainSequencer)
		if self.tracktype == 'midi': 
			x_MidiControllers = ET.SubElement(x_MainSequencer, "MidiControllers")
		for nid, data in self.MidiControllers.items(): data.write(x_MidiControllers)

class ableton_FreezeSequencer:
	def __init__(self, xmltag):
		self.ClipSlotList = {}
		self.MidiControllers = {}
		self.LomId = ableton_LomId(xmltag)
		self.IsExpanded = get_bool_opt(xmltag, 'IsExpanded', True)
		self.On = ableton_Param(xmltag, 'On', 'bool')
		self.ModulationSourceCount = int(get_value(xmltag, 'ModulationSourceCount', 0))
		if xmltag: 
			pointee = xmltag.findall('Pointee')
			if pointee: self.Pointee = int(pointee[0].get('Id') if xmltag else 0)
			else: self.Pointee = None
		else:
			self.Pointee = counter_unused_id.get()
		self.LastSelectedTimeableIndex = int(get_value(xmltag, 'LastSelectedTimeableIndex', 0))
		self.LastSelectedClipEnvelopeIndex = int(get_value(xmltag, 'LastSelectedClipEnvelopeIndex', 0))
		self.IsFolded = get_bool(xmltag, 'IsFolded', False)
		self.ShouldShowPresetName = get_bool(xmltag, 'ShouldShowPresetName', False)
		self.UserName = get_value(xmltag, 'UserName', '')
		self.Annotation = get_value(xmltag, 'Annotation', '')
		if not xmltag:
			for n in range(8): self.ClipSlotList[n] = ableton_ClipSlot(None)
		else: self.ClipSlotList = get_list(xmltag, 'ClipSlotList', 'ClipSlot', ableton_ClipSlot)
		self.MonitoringEnum = int(get_value(xmltag, 'MonitoringEnum', 1))
		x_Sample = xmltag.findall('Sample')[0] if xmltag else None
		self.ClipTimeable = ableton_Automation(x_Sample, 'ArrangerAutomation')
		self.VolumeModulationTarget = ableton_ReceiveTarget(xmltag, 'VolumeModulationTarget')
		self.TranspositionModulationTarget = ableton_ReceiveTarget(xmltag, 'TranspositionModulationTarget')
		self.GrainSizeModulationTarget = ableton_ReceiveTarget(xmltag, 'GrainSizeModulationTarget')
		self.FluxModulationTarget = ableton_ReceiveTarget(xmltag, 'FluxModulationTarget')
		self.SampleOffsetModulationTarget = ableton_ReceiveTarget(xmltag, 'SampleOffsetModulationTarget')
		self.PitchViewScrollPosition = get_value(xmltag, 'PitchViewScrollPosition', -1073741824)
		self.SampleOffsetModulationScrollPosition = get_value(xmltag, 'SampleOffsetModulationScrollPosition', -1073741824)
		self.Recorder = ableton_Recorder(xmltag)


	def write(self, xmltag):
		self.LomId.write(xmltag)
		if self.IsExpanded != None: add_bool(xmltag, 'IsExpanded', self.IsExpanded)
		self.On.write(xmltag)
		add_value(xmltag, 'ModulationSourceCount', self.ModulationSourceCount)
		add_lomid(xmltag, 'ParametersListWrapper', 0)
		if self.Pointee != None: add_id(xmltag, 'Pointee', self.Pointee)
		add_value(xmltag, 'LastSelectedTimeableIndex', self.LastSelectedTimeableIndex)
		add_value(xmltag, 'LastSelectedClipEnvelopeIndex', self.LastSelectedClipEnvelopeIndex)
		x_LastPresetRef = ET.SubElement(xmltag, "LastPresetRef")
		ET.SubElement(x_LastPresetRef, "Value")
		ET.SubElement(xmltag, "LockedScripts")
		add_bool(xmltag, 'IsFolded', self.IsFolded)
		add_bool(xmltag, 'ShouldShowPresetName', self.ShouldShowPresetName)
		add_value(xmltag, 'UserName', self.UserName)
		add_value(xmltag, 'Annotation', self.Annotation)
		x_SourceContext = ET.SubElement(xmltag, "SourceContext")
		ET.SubElement(x_SourceContext, "Value")
		if self.ClipSlotList != None:
			x_ClipSlotList = ET.SubElement(xmltag, "ClipSlotList")
			for nid, data in self.ClipSlotList.items():
				x_ClipSlot = ET.SubElement(x_ClipSlotList, "ClipSlot")
				x_ClipSlot.set('Id', str(nid))
				data.write(x_ClipSlot)
		add_value(xmltag, 'MonitoringEnum', self.MonitoringEnum)
		x_Sample = ET.SubElement(xmltag, "Sample")
		self.ClipTimeable.write(x_Sample)
		self.VolumeModulationTarget.write(xmltag)
		self.TranspositionModulationTarget.write(xmltag)
		self.GrainSizeModulationTarget.write(xmltag)
		self.FluxModulationTarget.write(xmltag)
		self.SampleOffsetModulationTarget.write(xmltag)
		add_value(xmltag, 'PitchViewScrollPosition', self.PitchViewScrollPosition)
		add_value(xmltag, 'SampleOffsetModulationScrollPosition', self.SampleOffsetModulationScrollPosition)
		self.Recorder.write(xmltag)

# --------------------------------------------- DeviceChain ---------------------------------------------

class ableton_TrackDeviceChain:
	def __init__(self, xmltag, tracktype):
		self.MainSequencer = None
		self.FreezeSequencer = None
		self.tracktype = tracktype
		self.devices = []
		if xmltag:
			x_DeviceChain = xmltag.findall('DeviceChain')[0]
			self.AutomationLanes = ableton_AutomationLanes(x_DeviceChain)
			self.ClipEnvelopeChooserViewState = ableton_ClipEnvelopeChooserViewState(x_DeviceChain)
			self.AudioInputRouting = ableton_upperlowertarget(x_DeviceChain, 'AudioInputRouting')
			self.MidiInputRouting = ableton_upperlowertarget(x_DeviceChain, 'MidiInputRouting')
			self.AudioOutputRouting = ableton_upperlowertarget(x_DeviceChain, 'AudioOutputRouting')
			self.MidiOutputRouting = ableton_upperlowertarget(x_DeviceChain, 'MidiOutputRouting')
			x_Mixer = x_DeviceChain.findall('Mixer')[0]
			self.Mixer = ableton_Mixer(x_Mixer, tracktype)
			xm_MainSequencer = x_DeviceChain.findall('MainSequencer')
			if xm_MainSequencer: self.MainSequencer = ableton_MainSequencer(xm_MainSequencer[0], tracktype)
			xm_FreezeSequencer = x_DeviceChain.findall('FreezeSequencer')
			if self.tracktype == 'midi' and xm_FreezeSequencer: self.FreezeSequencer = ableton_FreezeSequencer(xm_FreezeSequencer[0])
			if self.tracktype == 'audio' and xm_FreezeSequencer: self.FreezeSequencer = ableton_FreezeSequencer(xm_FreezeSequencer[0])
			elif self.tracktype == 'master': self.FreezeSequencer = get_list(x_DeviceChain, 'FreezeSequencer', 'AudioSequencer', ableton_FreezeSequencer)

			x_InDeviceChain = x_DeviceChain.findall('DeviceChain')[0]
			x_Devices = x_InDeviceChain.findall('Devices')[0]
			for x_Device in x_Devices:
				self.devices.append(ableton_Device(x_Device))

		else:
			self.AutomationLanes = ableton_AutomationLanes(None)
			AutomationLane = ableton_AutomationLane(None)
			if tracktype == 'prehear': AutomationLane.LaneHeight = 85
			if tracktype == 'master': 
				AutomationLane.LaneHeight = 85
				AutomationLane.SelectedDevice = 1
				AutomationLane.SelectedEnvelope = 2
			self.AutomationLanes.AutomationLanes[0] = AutomationLane
			self.ClipEnvelopeChooserViewState = ableton_ClipEnvelopeChooserViewState(None)
			self.AudioInputRouting = ableton_upperlowertarget(None, 'AudioInputRouting')
			self.MidiInputRouting = ableton_upperlowertarget(None, 'MidiInputRouting')
			self.AudioOutputRouting = ableton_upperlowertarget(None, 'AudioOutputRouting')
			self.MidiOutputRouting = ableton_upperlowertarget(None, 'MidiOutputRouting')
			self.Mixer = ableton_Mixer(None, tracktype)
			self.MainSequencer = None
			self.FreezeSequencer = None

			if tracktype in ['audio']:
				self.AudioInputRouting.set('AudioIn/External/M0', 'Ext. In', '1')
				self.MidiInputRouting.set('MidiIn/External.All/-1', 'Ext: All Ins', '')
				self.AudioOutputRouting.set('AudioOut/Master', 'Master', '')
				self.MidiOutputRouting.set('MidiOut/None', 'None', '')

				FreezeSequencer = ableton_FreezeSequencer(None)
				FreezeSequencer.IsExpanded = True

				FreezeSequencer.On.exists = True
				FreezeSequencer.On.Manual = True
				FreezeSequencer.On.AutomationTarget.set_unused()

				FreezeSequencer.VolumeModulationTarget.set_unused()
				FreezeSequencer.TranspositionModulationTarget.set_unused()
				FreezeSequencer.GrainSizeModulationTarget.set_unused()
				FreezeSequencer.FluxModulationTarget.set_unused()
				FreezeSequencer.SampleOffsetModulationTarget.set_unused()

				self.FreezeSequencer = {}
				self.FreezeSequencer = FreezeSequencer
				
			if tracktype in ['midi']:
				self.AudioInputRouting.set('AudioIn/External/S0', 'Ext. In', '1/2')
				self.MidiInputRouting.set('MidiIn/External.All/-1', 'Ext: All Ins', '')
				self.AudioOutputRouting.set('AudioOut/Master', 'Master', '')
				self.MidiOutputRouting.set('MidiOut/None', 'None', '')

				FreezeSequencer = ableton_FreezeSequencer(None)
				FreezeSequencer.IsExpanded = True

				FreezeSequencer.On.exists = True
				FreezeSequencer.On.Manual = True
				FreezeSequencer.On.AutomationTarget.set_unused()

				FreezeSequencer.VolumeModulationTarget.set_unused()
				FreezeSequencer.TranspositionModulationTarget.set_unused()
				FreezeSequencer.GrainSizeModulationTarget.set_unused()
				FreezeSequencer.FluxModulationTarget.set_unused()
				FreezeSequencer.SampleOffsetModulationTarget.set_unused()

				self.FreezeSequencer = {}
				self.FreezeSequencer = FreezeSequencer
				
			if tracktype in ['prehear', 'master']:
				self.AudioInputRouting.set('AudioIn/External/S0', 'Ext. In', '1/2')
				self.MidiInputRouting.set('MidiIn/External.All/-1', 'Ext: All Ins', '')
				self.AudioOutputRouting.set('AudioOut/External/S0', 'Ext. Out', '1/2')
				self.MidiOutputRouting.set('MidiOut/None', 'None', '')
				FreezeSequencer = ableton_FreezeSequencer(None)
				FreezeSequencer.IsExpanded = True

				FreezeSequencer.On.exists = True
				FreezeSequencer.On.Manual = True

				if tracktype in ['master']:
					FreezeSequencer.Pointee = 19731
					FreezeSequencer.On.AutomationTarget.set_id(15)
					FreezeSequencer.VolumeModulationTarget.set_id(16)
					FreezeSequencer.TranspositionModulationTarget.set_id(17)
					FreezeSequencer.GrainSizeModulationTarget.set_id(18)
					FreezeSequencer.FluxModulationTarget.set_id(19)
					FreezeSequencer.SampleOffsetModulationTarget.set_id(20)
				else:
					FreezeSequencer.On.AutomationTarget.set_unused()
					FreezeSequencer.VolumeModulationTarget.set_unused()
					FreezeSequencer.TranspositionModulationTarget.set_unused()
					FreezeSequencer.GrainSizeModulationTarget.set_unused()
					FreezeSequencer.FluxModulationTarget.set_unused()
					FreezeSequencer.SampleOffsetModulationTarget.set_unused()

				FreezeSequencer.ClipSlotList = {}

				self.FreezeSequencer = {}
				self.FreezeSequencer[0] = FreezeSequencer
				

	def write(self, xmltag):
		x_DeviceChain = ET.SubElement(xmltag, "DeviceChain")
		self.AutomationLanes.write(x_DeviceChain)
		self.ClipEnvelopeChooserViewState.write(x_DeviceChain)
		self.AudioInputRouting.write(x_DeviceChain)
		self.MidiInputRouting.write(x_DeviceChain)
		self.AudioOutputRouting.write(x_DeviceChain)
		self.MidiOutputRouting.write(x_DeviceChain)
		self.Mixer.write(x_DeviceChain)
		if self.MainSequencer: self.MainSequencer.write(x_DeviceChain)
		if self.tracktype == 'midi' and self.FreezeSequencer: 
			x_FreezeSequencer = ET.SubElement(x_DeviceChain, "FreezeSequencer")
			self.FreezeSequencer.write(x_FreezeSequencer)
		if self.tracktype == 'audio' and self.FreezeSequencer: 
			x_FreezeSequencer = ET.SubElement(x_DeviceChain, "FreezeSequencer")
			self.FreezeSequencer.write(x_FreezeSequencer)
		elif self.tracktype == 'master' and self.FreezeSequencer:
			set_list(x_DeviceChain, self.FreezeSequencer, "FreezeSequencer", "AudioSequencer")
		x_InDeviceChain = ET.SubElement(x_DeviceChain, "DeviceChain")
		x_Devices = ET.SubElement(x_InDeviceChain, "Devices")
		for device in self.devices:
			if device.name != 'InstrumentGroupDevice':
				device.write(x_Devices)


		x_SignalModulations = ET.SubElement(x_InDeviceChain, "SignalModulations")

# --------------------------------------------- Tracks ---------------------------------------------

class ableton_AutomationEnvelope:
	def __init__(self, xmltag):
		if xmltag:
			x_EnvelopeTarget = xmltag.findall('EnvelopeTarget')[0]
			self.PointeeId = int(get_value(x_EnvelopeTarget, 'PointeeId', 0))
			self.Automation = ableton_Automation(xmltag, 'Automation')
		else:
			self.PointeeId = 0
			self.Automation = ableton_Automation(None, 'Automation')
	def write(self, xmltag):
		x_EnvelopeTarget = ET.SubElement(xmltag, "EnvelopeTarget")
		add_value(x_EnvelopeTarget, 'PointeeId', self.PointeeId)
		self.Automation.write(xmltag)
		
class ableton_AutomationEnvelopes:
	def __init__(self, xmltag):
		if xmltag:
			x_AutomationEnvelopes = xmltag.findall('AutomationEnvelopes')[0]
			self.Envelopes = get_list(x_AutomationEnvelopes, 'Envelopes', 'AutomationEnvelope', ableton_AutomationEnvelope)
		else:
			self.Envelopes = {}
	def write(self, xmltag):
		x_AutomationEnvelopes = ET.SubElement(xmltag, "AutomationEnvelopes")
		set_list(x_AutomationEnvelopes, self.Envelopes, 'Envelopes', 'AutomationEnvelope')

class ableton_TakeLane:
	def __init__(self, xmltag):
		self.Height = int(get_value(xmltag, 'Height', 51))
		self.IsContentSelectedInDocument = get_bool(xmltag, 'IsContentSelectedInDocument', False)
		self.ClipTimeable = ableton_Automation(xmltag, 'ClipAutomation')
		self.Name = get_value(xmltag, 'Name', '')
		self.Annotation = get_value(xmltag, 'Annotation', '')
		self.Audition = get_bool(xmltag, 'Audition', False)

	def write(self, xmltag):
		add_value(xmltag, 'Height', self.Height)
		add_bool(xmltag, 'IsContentSelectedInDocument', self.IsContentSelectedInDocument)
		self.ClipTimeable.write(xmltag)
		add_value(xmltag, 'Name', self.Name)
		add_value(xmltag, 'Annotation', self.Annotation)
		add_bool(xmltag, 'Audition', self.Audition)

class ableton_MidiTrack:
	def __init__(self, xmltag):
		if xmltag: self.Id = int(xmltag.get('Id'))
		self.LomId = ableton_LomId(xmltag)
		self.IsContentSelectedInDocument = get_bool(xmltag, 'IsContentSelectedInDocument', False)
		self.PreferredContentViewMode = int(get_value(xmltag, 'PreferredContentViewMode', 0))
		self.TrackDelay = ableton_TrackDelay(xmltag)
		self.Name = ableton_Name(xmltag)
		self.Color = int(get_value(xmltag, 'Color', 0))
		self.AutomationEnvelopes = ableton_AutomationEnvelopes(xmltag)

		self.TrackGroupId = int(get_value(xmltag, 'TrackGroupId', -1))
		self.TrackUnfolded = get_bool(xmltag, 'TrackUnfolded', True)
		self.TakeLanes = ableton_TakeLanes(xmltag)

		self.LinkedTrackGroupId = int(get_value(xmltag, 'LinkedTrackGroupId', -1))
		self.SavedPlayingSlot = int(get_value(xmltag, 'SavedPlayingSlot', -1))
		self.SavedPlayingOffset = int(get_value(xmltag, 'SavedPlayingOffset', 0))
		self.Freeze = get_bool(xmltag, 'Freeze', False)
		self.VelocityDetail = int(get_value(xmltag, 'VelocityDetail', 0))
		self.NeedArrangerRefreeze = get_bool(xmltag, 'NeedArrangerRefreeze', True)
		self.PostProcessFreezeClips = int(get_value(xmltag, 'PostProcessFreezeClips', 0))
		self.DeviceChain = ableton_TrackDeviceChain(xmltag, 'midi')
		self.ReWireSlaveMidiTargetId = get_value_opt(xmltag, 'ReWireSlaveMidiTargetId', 0)
		self.PitchbendRange = get_value_opt(xmltag, 'PitchbendRange', 0)

	def write(self, xmltag):
		x_MidiTrack = ET.SubElement(xmltag, "MidiTrack")
		x_MidiTrack.set('Id', str(self.Id))
		self.LomId.write(x_MidiTrack)
		add_bool(x_MidiTrack, 'IsContentSelectedInDocument', self.IsContentSelectedInDocument)
		add_value(x_MidiTrack, 'PreferredContentViewMode', self.PreferredContentViewMode)
		self.TrackDelay.write(x_MidiTrack)
		self.Name.write(x_MidiTrack)
		add_value(x_MidiTrack, 'Color', self.Color)
		self.AutomationEnvelopes.write(x_MidiTrack)
		add_value(x_MidiTrack, 'TrackGroupId', self.TrackGroupId)
		add_bool(x_MidiTrack, 'TrackUnfolded', self.TrackUnfolded)
		add_lomid(x_MidiTrack, 'DevicesListWrapper', 0)
		add_lomid(x_MidiTrack, 'ClipSlotsListWrapper', 0)
		add_value(x_MidiTrack, 'ViewData', {})

		self.TakeLanes.write(x_MidiTrack)

		add_value(x_MidiTrack, 'LinkedTrackGroupId', self.LinkedTrackGroupId)
		add_value(x_MidiTrack, 'SavedPlayingSlot', self.SavedPlayingSlot)
		add_value(x_MidiTrack, 'SavedPlayingOffset', self.SavedPlayingOffset)
		add_bool(x_MidiTrack, 'Freeze', self.Freeze)
		add_value(x_MidiTrack, 'VelocityDetail', self.VelocityDetail)
		add_bool(x_MidiTrack, 'NeedArrangerRefreeze', self.NeedArrangerRefreeze)
		add_value(x_MidiTrack, 'PostProcessFreezeClips', self.PostProcessFreezeClips)
		self.DeviceChain.write(x_MidiTrack)
		add_value_opt(x_MidiTrack, 'ReWireSlaveMidiTargetId', self.ReWireSlaveMidiTargetId)
		add_value_opt(x_MidiTrack, 'PitchbendRange', self.PitchbendRange)

class ableton_AudioTrack:
	def __init__(self, xmltag):
		if xmltag: self.Id = int(xmltag.get('Id'))
		self.LomId = ableton_LomId(xmltag)
		self.IsContentSelectedInDocument = get_bool(xmltag, 'IsContentSelectedInDocument', True)
		self.PreferredContentViewMode = int(get_value(xmltag, 'PreferredContentViewMode', 0))
		self.TrackDelay = ableton_TrackDelay(xmltag)
		self.Name = ableton_Name(xmltag)
		self.Color = int(get_value(xmltag, 'Color', 0))
		self.AutomationEnvelopes = ableton_AutomationEnvelopes(xmltag)

		self.TrackGroupId = int(get_value(xmltag, 'TrackGroupId', -1))
		self.TrackUnfolded = get_bool(xmltag, 'TrackUnfolded', True)

		self.TakeLanes = ableton_TakeLanes(xmltag)

		self.LinkedTrackGroupId = int(get_value(xmltag, 'LinkedTrackGroupId', -1))
		self.SavedPlayingSlot = int(get_value(xmltag, 'SavedPlayingSlot', -1))
		self.SavedPlayingOffset = int(get_value(xmltag, 'SavedPlayingOffset', 0))
		self.Freeze = get_bool(xmltag, 'Freeze', False)
		self.VelocityDetail = int(get_value(xmltag, 'VelocityDetail', 0))
		self.NeedArrangerRefreeze = get_bool(xmltag, 'NeedArrangerRefreeze', True)
		self.PostProcessFreezeClips = int(get_value(xmltag, 'PostProcessFreezeClips', 0))
		self.DeviceChain = ableton_TrackDeviceChain(xmltag, 'audio')

	def write(self, xmltag):
		x_AudioTrack = ET.SubElement(xmltag, "AudioTrack")
		x_AudioTrack.set('Id', str(self.Id))
		self.LomId.write(x_AudioTrack)
		add_bool(x_AudioTrack, 'IsContentSelectedInDocument', self.IsContentSelectedInDocument)
		add_value(x_AudioTrack, 'PreferredContentViewMode', self.PreferredContentViewMode)
		self.TrackDelay.write(x_AudioTrack)
		self.Name.write(x_AudioTrack)
		add_value(x_AudioTrack, 'Color', self.Color)
		self.AutomationEnvelopes.write(x_AudioTrack)
		add_value(x_AudioTrack, 'TrackGroupId', self.TrackGroupId)
		add_bool(x_AudioTrack, 'TrackUnfolded', self.TrackUnfolded)
		add_lomid(x_AudioTrack, 'DevicesListWrapper', 0)
		add_lomid(x_AudioTrack, 'ClipSlotsListWrapper', 0)
		add_value(x_AudioTrack, 'ViewData', {})

		self.TakeLanes.write(x_AudioTrack)

		add_value(x_AudioTrack, 'LinkedTrackGroupId', self.LinkedTrackGroupId)
		add_value(x_AudioTrack, 'SavedPlayingSlot', self.SavedPlayingSlot)
		add_value(x_AudioTrack, 'SavedPlayingOffset', self.SavedPlayingOffset)
		add_bool(x_AudioTrack, 'Freeze', self.Freeze)
		add_value(x_AudioTrack, 'VelocityDetail', self.VelocityDetail)
		add_bool(x_AudioTrack, 'NeedArrangerRefreeze', self.NeedArrangerRefreeze)
		add_value(x_AudioTrack, 'PostProcessFreezeClips', self.PostProcessFreezeClips)
		self.DeviceChain.write(x_AudioTrack)

class ableton_GroupTrack:
	def __init__(self, xmltag):
		if xmltag: self.Id = int(xmltag.get('Id'))
		self.LomId = ableton_LomId(xmltag)
		self.IsContentSelectedInDocument = get_bool(xmltag, 'IsContentSelectedInDocument', True)
		self.PreferredContentViewMode = int(get_value(xmltag, 'PreferredContentViewMode', 0))
		self.TrackDelay = ableton_TrackDelay(xmltag)
		self.Name = ableton_Name(xmltag)
		self.Color = int(get_value(xmltag, 'Color', 0))
		self.AutomationEnvelopes = ableton_AutomationEnvelopes(xmltag)

		self.TrackGroupId = int(get_value(xmltag, 'TrackGroupId', -1))
		self.TrackUnfolded = get_bool(xmltag, 'TrackUnfolded', False)

		self.TakeLanes = ableton_TakeLanes(xmltag)

		self.LinkedTrackGroupId = int(get_value(xmltag, 'LinkedTrackGroupId', -1))
		self.DeviceChain = ableton_TrackDeviceChain(xmltag, 'audio')

	def write(self, xmltag):
		x_AudioTrack = ET.SubElement(xmltag, "GroupTrack")
		x_AudioTrack.set('Id', str(self.Id))
		self.LomId.write(x_AudioTrack)
		add_bool(x_AudioTrack, 'IsContentSelectedInDocument', self.IsContentSelectedInDocument)
		add_value(x_AudioTrack, 'PreferredContentViewMode', self.PreferredContentViewMode)
		self.TrackDelay.write(x_AudioTrack)
		self.Name.write(x_AudioTrack)
		add_value(x_AudioTrack, 'Color', self.Color)
		self.AutomationEnvelopes.write(x_AudioTrack)
		add_value(x_AudioTrack, 'TrackGroupId', self.TrackGroupId)
		add_bool(x_AudioTrack, 'TrackUnfolded', self.TrackUnfolded)
		add_lomid(x_AudioTrack, 'DevicesListWrapper', 0)
		add_lomid(x_AudioTrack, 'ClipSlotsListWrapper', 0)
		add_value(x_AudioTrack, 'ViewData', {})

		self.TakeLanes.write(x_AudioTrack)

		add_value(x_AudioTrack, 'LinkedTrackGroupId', self.LinkedTrackGroupId)

		x_Slots = ET.SubElement(x_AudioTrack, "Slots")
		for n in range(8):
			x_GroupTrackSlot = ET.SubElement(x_Slots, "GroupTrackSlot")
			x_GroupTrackSlot.set('Id', str(n))
			add_value(x_GroupTrackSlot, 'LomId', 0)


		self.DeviceChain.write(x_AudioTrack)

class ableton_ReturnTrack:
	def __init__(self, xmltag):
		if xmltag: self.Id = int(xmltag.get('Id'))
		self.LomId = ableton_LomId(xmltag)
		self.IsContentSelectedInDocument = get_bool(xmltag, 'IsContentSelectedInDocument', True)
		self.PreferredContentViewMode = int(get_value(xmltag, 'PreferredContentViewMode', 0))
		self.TrackDelay = ableton_TrackDelay(xmltag)
		self.Name = ableton_Name(xmltag)
		self.Color = int(get_value(xmltag, 'Color', 0))
		self.AutomationEnvelopes = ableton_AutomationEnvelopes(xmltag)

		self.TrackGroupId = int(get_value(xmltag, 'TrackGroupId', -1))
		self.TrackUnfolded = get_bool(xmltag, 'TrackUnfolded', False)

		self.TakeLanes = ableton_TakeLanes(xmltag)

		self.LinkedTrackGroupId = int(get_value(xmltag, 'LinkedTrackGroupId', -1))
		self.DeviceChain = ableton_TrackDeviceChain(xmltag, 'audio')

	def write(self, xmltag):
		x_AudioTrack = ET.SubElement(xmltag, "ReturnTrack")
		x_AudioTrack.set('Id', str(self.Id))
		self.LomId.write(x_AudioTrack)
		add_bool(x_AudioTrack, 'IsContentSelectedInDocument', self.IsContentSelectedInDocument)
		add_value(x_AudioTrack, 'PreferredContentViewMode', self.PreferredContentViewMode)
		self.TrackDelay.write(x_AudioTrack)
		self.Name.write(x_AudioTrack)
		add_value(x_AudioTrack, 'Color', self.Color)
		self.AutomationEnvelopes.write(x_AudioTrack)
		add_value(x_AudioTrack, 'TrackGroupId', self.TrackGroupId)
		add_bool(x_AudioTrack, 'TrackUnfolded', self.TrackUnfolded)
		add_lomid(x_AudioTrack, 'DevicesListWrapper', 0)
		add_lomid(x_AudioTrack, 'ClipSlotsListWrapper', 0)
		add_value(x_AudioTrack, 'ViewData', {})

		self.TakeLanes.write(x_AudioTrack)

		add_value(x_AudioTrack, 'LinkedTrackGroupId', self.LinkedTrackGroupId)
		self.DeviceChain.write(x_AudioTrack)

class ableton_MasterTrack:
	def __init__(self, xmltag):
		self.LomId = ableton_LomId(xmltag)
		self.IsContentSelectedInDocument = get_bool(xmltag, 'IsContentSelectedInDocument', False)
		self.PreferredContentViewMode = int(get_value(xmltag, 'PreferredContentViewMode', 0))
		self.TrackDelay = ableton_TrackDelay(xmltag)
		self.Name = ableton_Name(xmltag)
		self.Color = int(get_value(xmltag, 'Color', 11))
		self.AutomationEnvelopes = ableton_AutomationEnvelopes(xmltag)
		self.TrackGroupId = int(get_value(xmltag, 'TrackGroupId', -1))
		self.TrackUnfolded = get_bool(xmltag, 'TrackUnfolded', False)

		self.TakeLanes = ableton_TakeLanes(xmltag)

		self.LinkedTrackGroupId = int(get_value(xmltag, 'LinkedTrackGroupId', -1))
		self.DeviceChain = ableton_TrackDeviceChain(xmltag, 'master')

		if not xmltag:
			self.Name.EffectiveName = 'Master'

	def write(self, xmltag):
		x_MasterTrack = ET.SubElement(xmltag, "MasterTrack")
		self.LomId.write(x_MasterTrack)
		add_bool(x_MasterTrack, 'IsContentSelectedInDocument', self.IsContentSelectedInDocument)
		add_value(x_MasterTrack, 'PreferredContentViewMode', self.PreferredContentViewMode)
		self.TrackDelay.write(x_MasterTrack)
		self.Name.write(x_MasterTrack)
		add_value(x_MasterTrack, 'Color', self.Color)
		self.AutomationEnvelopes.write(x_MasterTrack)
		add_value(x_MasterTrack, 'TrackGroupId', self.TrackGroupId)
		add_bool(x_MasterTrack, 'TrackUnfolded', self.TrackUnfolded)
		add_lomid(x_MasterTrack, 'DevicesListWrapper', 0)
		add_lomid(x_MasterTrack, 'ClipSlotsListWrapper', 0)
		add_value(x_MasterTrack, 'ViewData', {})

		self.TakeLanes.write(x_MasterTrack)

		add_value(x_MasterTrack, 'LinkedTrackGroupId', self.LinkedTrackGroupId)
		self.DeviceChain.write(x_MasterTrack)

class ableton_PreHearTrack:
	def __init__(self, xmltag):
		self.LomId = ableton_LomId(xmltag)
		self.IsContentSelectedInDocument = get_bool(xmltag, 'IsContentSelectedInDocument', False)
		self.PreferredContentViewMode = int(get_value(xmltag, 'PreferredContentViewMode', 0))
		self.TrackDelay = ableton_TrackDelay(xmltag)
		self.Name = ableton_Name(xmltag)
		self.Color = int(get_value(xmltag, 'Color', -1))
		self.TrackGroupId = int(get_value(xmltag, 'TrackGroupId', -1))
		self.TrackUnfolded = get_bool(xmltag, 'TrackUnfolded', False)

		self.TakeLanes = ableton_TakeLanes(xmltag)

		self.LinkedTrackGroupId = int(get_value(xmltag, 'LinkedTrackGroupId', -1))
		self.DeviceChain = ableton_TrackDeviceChain(xmltag, 'prehear')

		if not xmltag:
			self.Name.EffectiveName = 'Master'


	def write(self, xmltag):
		x_MasterTrack = ET.SubElement(xmltag, "PreHearTrack")
		self.LomId.write(x_MasterTrack)
		add_bool(x_MasterTrack, 'IsContentSelectedInDocument', self.IsContentSelectedInDocument)
		add_value(x_MasterTrack, 'PreferredContentViewMode', self.PreferredContentViewMode)
		self.TrackDelay.write(x_MasterTrack)
		self.Name.write(x_MasterTrack)
		add_value(x_MasterTrack, 'Color', self.Color)
		x_AutomationEnvelopes = ET.SubElement(x_MasterTrack, "AutomationEnvelopes")
		x_Envelopes = ET.SubElement(x_AutomationEnvelopes, "Envelopes")
		add_value(x_MasterTrack, 'TrackGroupId', self.TrackGroupId)
		add_bool(x_MasterTrack, 'TrackUnfolded', self.TrackUnfolded)
		add_lomid(x_MasterTrack, 'DevicesListWrapper', 0)
		add_lomid(x_MasterTrack, 'ClipSlotsListWrapper', 0)
		add_value(x_MasterTrack, 'ViewData', {})

		self.TakeLanes.write(x_MasterTrack)

		add_value(x_MasterTrack, 'LinkedTrackGroupId', self.LinkedTrackGroupId)
		self.DeviceChain.write(x_MasterTrack)

# --------------------------------------------- Live Set ---------------------------------------------

class ableton_Scene:
	__slots__ = ['FollowAction','Name','Annotation','Color','Tempo','IsTempoEnabled','TimeSignatureId','IsTimeSignatureEnabled','LomId']
	def __init__(self, xmltag):
		self.FollowAction = ableton_FollowAction(xmltag)
		self.Name = get_value(xmltag, 'Name', '')
		self.Annotation = get_value(xmltag, 'Annotation', '')
		self.Color = int(get_value(xmltag, 'Color', -1))
		self.Tempo = int(get_value(xmltag, 'Tempo', 120))
		self.IsTempoEnabled = get_bool(xmltag, 'IsTempoEnabled', False)
		self.TimeSignatureId = int(get_value(xmltag, 'TimeSignatureId', 201))
		self.IsTimeSignatureEnabled = get_bool(xmltag, 'IsTimeSignatureEnabled', False)
		self.LomId = int(get_value(xmltag, 'LomId', 0))

	def write(self, xmltag):
		self.FollowAction.write(xmltag)
		add_value(xmltag, 'Name', self.Name)
		add_value(xmltag, 'Annotation', self.Annotation)
		add_value(xmltag, 'Color', self.Color)
		add_value(xmltag, 'Tempo', self.Tempo)
		add_bool(xmltag, 'IsTempoEnabled', self.IsTempoEnabled)
		add_value(xmltag, 'TimeSignatureId', self.TimeSignatureId)
		add_bool(xmltag, 'IsTimeSignatureEnabled', self.IsTimeSignatureEnabled)
		add_value(xmltag, 'LomId', self.LomId)
		add_lomid(xmltag, 'ClipSlotsListWrapper', 0)

class ableton_xy_value:
	__slots__ = ['X', 'Y', 'name']
	def __init__(self, xmltag, name):
		self.X = 0
		self.Y = 0
		self.name = name
		if xmltag != None:
			x_xy = xmltag.findall(name)
			if x_xy:
				self.X = int(x_xy[0].get('X'))
				self.Y = int(x_xy[0].get('Y'))

	def write(self, xmltag):
		x_xy = ET.SubElement(xmltag, self.name)
		x_xy.set('X', str(self.X))
		x_xy.set('Y', str(self.Y))

class ableton_tlbr_value:
	__slots__ = ['Top', 'Left', 'Bottom', 'Right', 'name']
	def __init__(self, xmltag, name):
		self.Top = -2147483648
		self.Left = -2147483648
		self.Bottom = -2147483648
		self.Right = -2147483648
		self.name = name
		if xmltag != None:
			x_xy = xmltag.findall(name)
			if x_xy:
				self.Top = int(x_xy[0].get('Top'))
				self.Left = int(x_xy[0].get('Left'))
				self.Bottom = int(x_xy[0].get('Bottom'))
				self.Right = int(x_xy[0].get('Right'))

	def write(self, xmltag):
		x_xy = ET.SubElement(xmltag, self.name)
		x_xy.set('Top', str(self.Top))
		x_xy.set('Left', str(self.Left))
		x_xy.set('Bottom', str(self.Bottom))
		x_xy.set('Right', str(self.Right))

class ableton_SongMasterValues:
	__slots__ = ['SessionScrollerPos']
	def __init__(self, xmltag):
		self.SessionScrollerPos = ableton_xy_value(xmltag, 'SessionScrollerPos')

	def write(self, xmltag):
		x_SongMasterValues = ET.SubElement(xmltag, "SongMasterValues")
		self.SessionScrollerPos.write(x_SongMasterValues)

class ableton_Transport:
	__slots__ = ['PhaseNudgeTempo','LoopOn','LoopStart','LoopLength','LoopIsSongStart','CurrentTime','PunchIn','PunchOut','MetronomeTickDuration','DrawMode']
	def __init__(self, xmltag):
		self.PhaseNudgeTempo = int(get_value(xmltag, 'PhaseNudgeTempo', 10))
		self.LoopOn = get_bool(xmltag, 'LoopOn', False)
		self.LoopStart = float(get_value(xmltag, 'LoopStart', 8))
		self.LoopLength = float(get_value(xmltag, 'LoopLength', 16))
		self.LoopIsSongStart = get_bool(xmltag, 'LoopIsSongStart', False)
		self.CurrentTime = float(get_value(xmltag, 'CurrentTime', 0))
		self.PunchIn = get_bool(xmltag, 'PunchIn', False)
		self.PunchOut = get_bool(xmltag, 'PunchOut', False)
		self.MetronomeTickDuration = float(get_value(xmltag, 'MetronomeTickDuration', 0))
		self.DrawMode = get_bool(xmltag, 'DrawMode', False)

	def write(self, xmltag):
		x_Transport = ET.SubElement(xmltag, "Transport")
		add_value(x_Transport, 'PhaseNudgeTempo', self.PhaseNudgeTempo)
		add_bool(x_Transport, 'LoopOn', self.LoopOn)
		add_value(x_Transport, 'LoopStart', self.LoopStart)
		add_value(x_Transport, 'LoopLength', self.LoopLength)
		add_bool(x_Transport, 'LoopIsSongStart', self.LoopIsSongStart)
		add_value(x_Transport, 'CurrentTime', self.CurrentTime)
		add_bool(x_Transport, 'PunchIn', self.PunchIn)
		add_bool(x_Transport, 'PunchOut', self.PunchOut)
		add_value(x_Transport, 'MetronomeTickDuration', self.MetronomeTickDuration)
		add_bool(x_Transport, 'DrawMode', self.DrawMode)

class ableton_SequencerNavigator:
	__slots__ = ['CurrentZoom','ScrollerPos','ClientSize']
	def __init__(self, xmltag):
		if xmltag:
			BeatTimeHelper = xmltag.findall('BeatTimeHelper')[0]
			self.CurrentZoom = float(get_value(BeatTimeHelper, 'CurrentZoom', 0))
			self.ScrollerPos = ableton_xy_value(xmltag, 'ScrollerPos')
			self.ClientSize = ableton_xy_value(xmltag, 'ClientSize')
		else:
			self.CurrentZoom = 0.254945
			self.ScrollerPos = ableton_xy_value(None, 'ScrollerPos')
			self.ClientSize = ableton_xy_value(None, 'ClientSize')

	def write(self, xmltag):
		x_SequencerNavigator = ET.SubElement(xmltag, "SequencerNavigator")
		x_BeatTimeHelper = ET.SubElement(x_SequencerNavigator, "BeatTimeHelper")
		add_value(x_BeatTimeHelper, 'CurrentZoom', self.CurrentZoom)
		self.ScrollerPos.write(x_SequencerNavigator)
		self.ClientSize.write(x_SequencerNavigator)

class ableton_ExpressionLane:
	__slots__ = ['Type','Size','IsMinimized']
	def __init__(self, xmltag):
		self.Type = float(get_value(xmltag, 'Type', 0))
		self.Size = float(get_value(xmltag, 'Size', 0))
		self.IsMinimized = get_bool(xmltag, 'IsMinimized', False)

	def write(self, xmltag):
		add_value(xmltag, 'Type', self.Type)
		add_value(xmltag, 'Size', self.Size)
		add_bool(xmltag, 'IsMinimized', self.IsMinimized)

class ableton_SampleRef:
	def __init__(self, xmltag):
		if xmltag:
			x_SampleRef = xmltag.findall('SampleRef')[0]
			self.FileRef = ableton_FileRef(x_SampleRef.findall('FileRef')[0])
			self.LastModDate = int(get_value(x_SampleRef, 'LastModDate', 0))
			self.SourceContext = get_list(x_SampleRef, 'SourceContext', 'SourceContext', ableton_SourceContext)
			self.SampleUsageHint = int(get_value(x_SampleRef, 'SampleUsageHint', 0))
			self.DefaultDuration = int(get_value(x_SampleRef, 'DefaultDuration', 0))
			self.DefaultSampleRate = int(get_value(x_SampleRef, 'DefaultSampleRate', 0))
		else:
			self.FileRef = ableton_FileRef(None)
			self.LastModDate = 0
			self.SourceContext = {}
			self.SampleUsageHint = 0
			self.DefaultDuration = 0
			self.DefaultSampleRate = 0

	def write(self, xmltag):
		x_SampleRef = ET.SubElement(xmltag, "SampleRef")
		x_FileRef = ET.SubElement(x_SampleRef, "FileRef")
		self.FileRef.write(x_FileRef)
		add_value(x_SampleRef, 'LastModDate', self.LastModDate)
		set_list(x_SampleRef, self.SourceContext, "SourceContext", "SourceContext")
		add_value(x_SampleRef, 'SampleUsageHint', self.SampleUsageHint)
		add_value(x_SampleRef, 'DefaultDuration', self.DefaultDuration)
		add_value(x_SampleRef, 'DefaultSampleRate', self.DefaultSampleRate)

class ableton_FileRef:
	__slots__ = ['RelativePathType','RelativePath','Path','Type','LivePackName','LivePackId','OriginalFileSize','OriginalCrc']
	def __init__(self, xmltag):
		self.RelativePathType = int(get_value(xmltag, 'RelativePathType', 5))
		self.RelativePath = get_value(xmltag, 'RelativePath', '')
		self.Path = get_value(xmltag, 'Path', '')
		self.Type = int(get_value(xmltag, 'Type', 0))
		self.LivePackName = get_value(xmltag, 'LivePackName', '')
		self.LivePackId = get_value(xmltag, 'LivePackId', '')
		self.OriginalFileSize = int(get_value(xmltag, 'OriginalFileSize', 0))
		self.OriginalCrc = int(get_value(xmltag, 'OriginalCrc', 0))

	def write(self, xmltag):
		add_value(xmltag, 'RelativePathType', self.RelativePathType)
		add_value(xmltag, 'RelativePath', self.RelativePath)
		add_value(xmltag, 'Path', self.Path)
		add_value(xmltag, 'Type', self.Type)
		add_value(xmltag, 'LivePackName', self.LivePackName)
		add_value(xmltag, 'LivePackId', self.LivePackId)
		add_value(xmltag, 'OriginalFileSize', self.OriginalFileSize)
		add_value(xmltag, 'OriginalCrc', self.OriginalCrc)

class ableton_SourceContext:
	__slots__ = ['OriginalFileRef','BrowserContentPath']
	def __init__(self, xmltag):
		self.OriginalFileRef = get_list(xmltag, 'OriginalFileRef', 'FileRef', ableton_FileRef)
		self.BrowserContentPath = get_value(xmltag, 'BrowserContentPath', '')

	def write(self, xmltag):
		set_list(xmltag, self.OriginalFileRef, "OriginalFileRef", "FileRef")
		add_value(xmltag, 'BrowserContentPath', self.BrowserContentPath)

class ableton_Groove:
	__slots__ = ['Name','Clips','Grid','QuantizationAmount','TimingAmount','RandomAmount','VelocityAmount','Annotation','Selection','SourceContext']
	def __init__(self, xmltag):
		self.Name = get_value(xmltag, 'Name', '')
		x_Clip = xmltag.findall('Clip')[0]
		self.Clips = get_list(x_Clip, 'Value', 'MidiClip', ableton_MidiClip)
		self.Grid = float(get_value(xmltag, 'Grid', 3))
		self.QuantizationAmount = float(get_value(xmltag, 'QuantizationAmount', 0))
		self.TimingAmount = float(get_value(xmltag, 'TimingAmount', 100))
		self.RandomAmount = float(get_value(xmltag, 'RandomAmount', 0))
		self.VelocityAmount = float(get_value(xmltag, 'VelocityAmount', 100))
		self.Annotation = get_value(xmltag, 'Annotation', '')
		self.Selection = get_bool(xmltag, 'Selection', False)
		self.SourceContext = get_list(xmltag, 'SourceContext', 'SourceContext', ableton_SourceContext)

	def write(self, xmltag):
		add_value(xmltag, 'LomId', 0)
		add_value(xmltag, 'Name', self.Name)
		x_Clip = ET.SubElement(xmltag, "Clip")
		set_list(x_Clip, self.Clips, "Value", "MidiClip")
		add_value(xmltag, 'Grid', self.Grid)
		add_value(xmltag, 'QuantizationAmount', self.QuantizationAmount)
		add_value(xmltag, 'TimingAmount', self.TimingAmount)
		add_value(xmltag, 'RandomAmount', self.RandomAmount)
		add_value(xmltag, 'VelocityAmount', self.VelocityAmount)
		add_value(xmltag, 'Annotation', self.Annotation)
		add_bool(xmltag, 'Selection', self.Selection)
		set_list(xmltag, self.SourceContext, "SourceContext", "SourceContext")

class ableton_ViewStates:
	def __init__(self, xmltag):
		self.SessionIO = get_value(xmltag, 'SessionIO', 1)
		self.SessionSends = get_value(xmltag, 'SessionSends', 1)
		self.SessionReturns = get_value(xmltag, 'SessionReturns', 1)
		self.SessionMixer = get_value(xmltag, 'SessionMixer', 1)
		self.SessionTrackDelay = get_value(xmltag, 'SessionTrackDelay', 0)
		self.SessionCrossFade = get_value(xmltag, 'SessionCrossFade', 0)
		self.SessionShowOverView = get_value(xmltag, 'SessionShowOverView', 0)
		self.ArrangerIO = get_value(xmltag, 'ArrangerIO', 1)
		self.ArrangerReturns = get_value(xmltag, 'ArrangerReturns', 1)
		self.ArrangerMixer = get_value(xmltag, 'ArrangerMixer', 1)
		self.ArrangerTrackDelay = get_value(xmltag, 'ArrangerTrackDelay', 0)
		self.ArrangerShowOverView = get_value(xmltag, 'ArrangerShowOverView', 1)

	def write(self, xmltag):
		x_ViewStates = ET.SubElement(xmltag, "ViewStates")
		add_value(x_ViewStates, 'SessionIO', self.SessionIO)
		add_value(x_ViewStates, 'SessionSends', self.SessionSends)
		add_value(x_ViewStates, 'SessionReturns', self.SessionReturns)
		add_value(x_ViewStates, 'SessionMixer', self.SessionMixer)
		add_value(x_ViewStates, 'SessionTrackDelay', self.SessionTrackDelay)
		add_value(x_ViewStates, 'SessionCrossFade', self.SessionCrossFade)
		add_value(x_ViewStates, 'SessionShowOverView', self.SessionShowOverView)
		add_value(x_ViewStates, 'ArrangerIO', self.ArrangerIO)
		add_value(x_ViewStates, 'ArrangerReturns', self.ArrangerReturns)
		add_value(x_ViewStates, 'ArrangerMixer', self.ArrangerMixer)
		add_value(x_ViewStates, 'ArrangerTrackDelay', self.ArrangerTrackDelay)
		add_value(x_ViewStates, 'ArrangerShowOverView', self.ArrangerShowOverView)

class ableton_Locator:
	def __init__(self, xmltag):
		self.LomId = int(get_value(xmltag, 'LomId', 0))
		self.Time = float(get_value(xmltag, 'Time', 0))
		self.Name = get_value(xmltag, 'Name', '')
		self.Annotation = get_value(xmltag, 'Annotation', '')
		self.IsSongStart = get_bool(xmltag, 'IsSongStart', False)

	def write(self, xmltag):
		add_value(xmltag, 'LomId', self.LomId)
		add_value(xmltag, 'Time', self.Time)
		add_value(xmltag, 'Name', self.Name)
		add_value(xmltag, 'Annotation', self.Annotation)
		add_bool(xmltag, 'IsSongStart', self.IsSongStart)

class ableton_liveset:
	def __init__(self):
		self.NextPointeeId = 0
		self.OverwriteProtectionNumber = 2816
		self.Tracks = []
		self.LomId = ableton_LomId(None)

	def load_from_file(self, input_file):
		xmlstring = ""
		with open(input_file, 'rb') as alsbytes:
			if alsbytes.read(2) == b'\x1f\x8b': 
				alsbytes.seek(0)
				xmlstring = gzip.decompress(alsbytes.read())
			else:
				alsbytes.seek(0)
				xmlstring = alsbytes.read().decode()

		root = ET.fromstring(xmlstring)

		abletonversion = root.get('MinorVersion').split('.')[0]
		if abletonversion != '11':
			print('[error] Ableton version '+abletonversion+' is not supported.')
			exit()

		x_LiveSet = root.findall('LiveSet')[0]
		self.NextPointeeId = int(get_value(x_LiveSet, 'NextPointeeId', 0))
		self.OverwriteProtectionNumber = int(get_value(x_LiveSet, 'OverwriteProtectionNumber', 2816))
		self.LomId = ableton_LomId(x_LiveSet)
		x_Tracks = x_LiveSet.findall('Tracks')[0]
		for x_Track in x_Tracks:
			if x_Track.tag == 'GroupTrack': self.Tracks.append(['group', ableton_GroupTrack(x_Track)])
			if x_Track.tag == 'MidiTrack': self.Tracks.append(['midi', ableton_MidiTrack(x_Track)])
			if x_Track.tag == 'AudioTrack': self.Tracks.append(['audio', ableton_AudioTrack(x_Track)])
			if x_Track.tag == 'ReturnTrack': self.Tracks.append(['return', ableton_ReturnTrack(x_Track)])
			print(x_Track.tag)
		self.MasterTrack = ableton_MasterTrack(x_LiveSet.findall('MasterTrack')[0])
		self.PreHearTrack = ableton_PreHearTrack(x_LiveSet.findall('PreHearTrack')[0])

		self.SendsPre = {}
		x_SendsPre = x_LiveSet.findall('SendsPre')[0]
		for x in x_SendsPre:
			if x.tag == 'SendPreBool': 
				self.SendsPre[int(x.get('Id'))] = bool(['false','true'].index(x.get('Value')))

		self.Scenes = get_list(x_LiveSet, 'Scenes', 'Scene', ableton_Scene)
		self.Transport = ableton_Transport(x_LiveSet.findall('Transport')[0])
		self.SongMasterValues = ableton_SongMasterValues(x_LiveSet.findall('SongMasterValues')[0])
		self.GlobalQuantisation = int(get_value(x_LiveSet, 'GlobalQuantisation', 4))
		self.AutoQuantisation = int(get_value(x_LiveSet, 'AutoQuantisation', 0))
		self.Grid = ableton_Grid(x_LiveSet, 'Grid')
		self.ScaleInformation = ableton_ScaleInformation(x_LiveSet)
		self.InKey = get_bool(x_LiveSet, 'InKey', False)
		self.SmpteFormat = int(get_value(x_LiveSet, 'SmpteFormat', 0))
		self.TimeSelection = ableton_TimeSelection(x_LiveSet)
		self.SequencerNavigator = ableton_SequencerNavigator(x_LiveSet.findall('SequencerNavigator')[0])
		self.ViewStateExtendedClipProperties = get_bool(x_LiveSet, 'ViewStateExtendedClipProperties', False)
		self.IsContentSplitterOpen = get_bool(x_LiveSet, 'IsContentSplitterOpen', True)
		self.IsExpressionSplitterOpen = get_bool(x_LiveSet, 'IsExpressionSplitterOpen', True)
		self.ExpressionLanes = get_list(x_LiveSet, 'ExpressionLanes', 'ExpressionLane', ableton_ExpressionLane)
		self.ContentLanes = get_list(x_LiveSet, 'ContentLanes', 'ExpressionLane', ableton_ExpressionLane)
		self.ViewStateFxSlotCount = int(get_value(x_LiveSet, 'ViewStateFxSlotCount', 4))
		self.ViewStateSessionMixerHeight = int(get_value(x_LiveSet, 'ViewStateSessionMixerHeight', 120))
		x_Locators = x_LiveSet.findall('Locators')[0]
		self.Locators = get_list(x_Locators, 'Locators', 'Locator', ableton_Locator)


		self.ChooserBar = int(get_value(x_LiveSet, 'ChooserBar', 0))
		self.Annotation = get_value(x_LiveSet, 'Annotation', '')
		self.SoloOrPflSavedValue = get_bool(x_LiveSet, 'SoloOrPflSavedValue', True)
		self.SoloInPlace = get_bool(x_LiveSet, 'SoloInPlace', True)
		self.CrossfadeCurve = int(get_value(x_LiveSet, 'CrossfadeCurve', 2))
		self.LatencyCompensation = int(get_value(x_LiveSet, 'LatencyCompensation', 2))
		self.HighlightedTrackIndex = int(get_value(x_LiveSet, 'HighlightedTrackIndex', 1))
		x_GroovePool = x_LiveSet.findall('GroovePool')[0]
		self.Grooves = get_list(x_GroovePool, 'Grooves', 'Groove', ableton_Groove)
		self.AutomationMode = get_bool(x_LiveSet, 'AutomationMode', False)
		self.SnapAutomationToGrid = get_bool(x_LiveSet, 'SnapAutomationToGrid', True)
		self.ArrangementOverdub = get_bool(x_LiveSet, 'ArrangementOverdub', False)
		self.ColorSequenceIndex = int(get_value(x_LiveSet, 'ColorSequenceIndex', 0))
		self.MidiFoldIn = get_bool(x_LiveSet, 'MidiFoldIn', False)
		self.MidiFoldMode = int(get_value(x_LiveSet, 'MidiFoldMode', 0))
		self.MultiClipFocusMode = get_bool(x_LiveSet, 'MultiClipFocusMode', False)
		self.MultiClipLoopBarHeight = int(get_value(x_LiveSet, 'MultiClipLoopBarHeight', 0))
		self.MidiPrelisten = get_bool(x_LiveSet, 'MidiPrelisten', False)
		self.AccidentalSpellingPreference = int(get_value(x_LiveSet, 'AccidentalSpellingPreference', 3))
		self.PreferFlatRootNote = get_bool(x_LiveSet, 'PreferFlatRootNote', False)
		self.UseWarperLegacyHiQMode = get_bool(x_LiveSet, 'UseWarperLegacyHiQMode', False)
		self.VideoWindowRect = ableton_tlbr_value(x_LiveSet, 'VideoWindowRect')
		self.ShowVideoWindow = get_bool(x_LiveSet, 'ShowVideoWindow', True)
		self.TrackHeaderWidth = int(get_value(x_LiveSet, 'TrackHeaderWidth', 93))
		self.ViewStateArrangerHasDetail = get_bool(x_LiveSet, 'ViewStateArrangerHasDetail', True)
		self.ViewStateSessionHasDetail = get_bool(x_LiveSet, 'ViewStateSessionHasDetail', True)
		self.ViewStateDetailIsSample = get_bool(x_LiveSet, 'ViewStateDetailIsSample', False)
		self.ViewStates = ableton_ViewStates(x_LiveSet.findall('ViewStates')[0])

	def make_from_scratch(self):
		self.MasterTrack = ableton_MasterTrack(None)
		self.PreHearTrack = ableton_PreHearTrack(None)
		self.SendsPre = {}
		self.Scenes = {}
		for n in range(8): self.Scenes[n] = ableton_Scene(None)
		self.Transport = ableton_Transport(None)
		self.SongMasterValues = ableton_SongMasterValues(None)
		self.GlobalQuantisation = 4
		self.AutoQuantisation = 0
		self.Grid = ableton_Grid(None, 'Grid')
		self.ScaleInformation = ableton_ScaleInformation(None)
		self.InKey = False
		self.SmpteFormat = int(get_value(None, 'SmpteFormat', 0))
		self.TimeSelection = ableton_TimeSelection(None)
		self.SequencerNavigator = ableton_SequencerNavigator(None)
		self.ViewStateExtendedClipProperties = False
		self.IsContentSplitterOpen = True
		self.IsExpressionSplitterOpen = True
		self.ExpressionLanes = {}
		for n in range(4):
			exp_lane = ableton_ExpressionLane(None)
			exp_lane.Type = n
			exp_lane.Size = 41
			if n>1: exp_lane.IsMinimized = True
			self.ExpressionLanes[n] = exp_lane

		self.ContentLanes = {}
		exp_lane = ableton_ExpressionLane(None)
		exp_lane.Type = 4
		exp_lane.Size = 41
		exp_lane.IsMinimized = False
		self.ContentLanes[0] = exp_lane

		exp_lane = ableton_ExpressionLane(None)
		exp_lane.Type = 5
		exp_lane.Size = 25
		exp_lane.IsMinimized = True
		self.ContentLanes[1] = exp_lane

		self.ViewStateFxSlotCount = 4
		self.ViewStateSessionMixerHeight = 120
		self.Locators = {}

		self.ChooserBar = 0
		self.Annotation = ''
		self.SoloOrPflSavedValue = True
		self.SoloInPlace = True
		self.CrossfadeCurve = 2
		self.LatencyCompensation = 2
		self.HighlightedTrackIndex = 0
		self.Grooves = {}
		self.AutomationMode = False
		self.SnapAutomationToGrid = True
		self.ArrangementOverdub = False
		self.ColorSequenceIndex = 2052373325
		self.MidiFoldIn = False
		self.MidiFoldMode = 0
		self.MultiClipFocusMode = False
		self.MultiClipLoopBarHeight = 0
		self.MidiPrelisten = False
		self.AccidentalSpellingPreference = 3
		self.PreferFlatRootNote = False
		self.UseWarperLegacyHiQMode = False
		self.VideoWindowRect = ableton_tlbr_value(None, 'VideoWindowRect')
		self.ShowVideoWindow = True
		self.TrackHeaderWidth = 93
		self.ViewStateArrangerHasDetail = True
		self.ViewStateSessionHasDetail = True
		self.ViewStateDetailIsSample = False
		self.ViewStates = ableton_ViewStates(None)

		self.SequencerNavigator.ClientSize.X = 528
		self.SequencerNavigator.ClientSize.Y = 437

		self.add_settempotimeig(120, 201)

		self.NextPointeeId = 0

	def add_settempotimeig(self, tempo, timesig):
		autoid_tempo = self.MasterTrack.DeviceChain.Mixer.Tempo.AutomationTarget.id
		autoid_timesig = self.MasterTrack.DeviceChain.Mixer.TimeSignature.AutomationTarget.id

		self.MasterTrack.DeviceChain.Mixer.Tempo.Manual = tempo
		self.MasterTrack.DeviceChain.Mixer.TimeSignature.Manual = timesig

		enumevent = ableton_EnumEvent(None)
		enumevent.Time = -63072000.0
		enumevent.Value = timesig
		tempoauto = ableton_AutomationEnvelope(None)
		tempoauto.PointeeId = autoid_timesig
		tempoauto.Automation.Events.append([0, 'EnumEvent', enumevent])
		self.MasterTrack.AutomationEnvelopes.Envelopes[0] = tempoauto

		enumevent = ableton_FloatEvent(None)
		enumevent.Time = -63072000.0
		enumevent.Value = tempo
		timesigauto = ableton_AutomationEnvelope(None)
		timesigauto.PointeeId = autoid_tempo
		timesigauto.Automation.Events.append([0, 'FloatEvent', enumevent])
		self.MasterTrack.AutomationEnvelopes.Envelopes[1] = timesigauto


	def add_audio_track(self, i_id):
		als_track = ableton_AudioTrack(None)
		als_track.Id = i_id

		MainSequencer = ableton_MainSequencer(None, 'audio')
		MainSequencer.On.exists = True
		MainSequencer.On.Manual = True
		MainSequencer.On.AutomationTarget.set_unused()

		MainSequencer.VolumeModulationTarget.set_unused()
		MainSequencer.TranspositionModulationTarget.set_unused()
		MainSequencer.GrainSizeModulationTarget.set_unused()
		MainSequencer.FluxModulationTarget.set_unused()
		MainSequencer.SampleOffsetModulationTarget.set_unused()

		als_track.DeviceChain.MainSequencer = MainSequencer

		als_track.ReWireSlaveMidiTargetId = 0
		als_track.PitchbendRange = 96

		self.Tracks.append(als_track)
		return als_track


	def add_midi_track(self, i_id):
		als_track = ableton_MidiTrack(None)
		als_track.Id = i_id

		MainSequencer = ableton_MainSequencer(None, 'midi')
		MainSequencer.On.exists = True
		MainSequencer.On.Manual = True
		MainSequencer.On.AutomationTarget.set_unused()
		als_track.DeviceChain.MainSequencer = MainSequencer

		als_track.ReWireSlaveMidiTargetId = 0
		als_track.PitchbendRange = 96

		self.Tracks.append(als_track)
		return als_track

	def nextpointee(self):
		self.NextPointeeId = counter_unused_id.current+1

	def save_to_file(self, output_file):
		x_root = ET.Element("Ableton")
		x_root.set('MajorVersion', "5")
		x_root.set('MinorVersion', "11.0_433")
		x_root.set('Creator', "Ableton Live 11.0")
		x_root.set('Revision', "9dc150af94686f816d2cf27815fcf2907d4b86f8")
		x_LiveSet = ET.SubElement(x_root, "LiveSet")
		
		add_value(x_LiveSet, 'NextPointeeId', self.NextPointeeId)
		add_value(x_LiveSet, 'OverwriteProtectionNumber', self.OverwriteProtectionNumber)
		self.LomId.write(x_LiveSet)
		x_Tracks = ET.SubElement(x_LiveSet, "Tracks")
		for tracktype, track in self.Tracks:
			track.write(x_Tracks)
		self.MasterTrack.write(x_LiveSet)
		self.PreHearTrack.write(x_LiveSet)

		x_SendsPre = ET.SubElement(x_LiveSet, "SendsPre")
		for i, v in self.SendsPre.items():
			x_SendPreBool = ET.SubElement(x_SendsPre, "SendPreBool")
			x_SendPreBool.set('Id', str(i))
			x_SendPreBool.set('Value', str(['false','true'][int(v)]))


		set_list(x_LiveSet, self.Scenes, "Scenes", "Scene")
		self.Transport.write(x_LiveSet)
		self.SongMasterValues.write(x_LiveSet)
		x_SignalModulations = ET.SubElement(x_LiveSet, "SignalModulations")
		add_value(x_LiveSet, 'GlobalQuantisation', self.GlobalQuantisation)
		add_value(x_LiveSet, 'AutoQuantisation', self.AutoQuantisation)
		self.Grid.write(x_LiveSet)
		self.ScaleInformation.write(x_LiveSet)
		add_bool(x_LiveSet, 'InKey', self.InKey)
		add_value(x_LiveSet, 'SmpteFormat', self.SmpteFormat)
		self.TimeSelection.write(x_LiveSet)
		self.SequencerNavigator.write(x_LiveSet)
		add_bool(x_LiveSet, 'ViewStateExtendedClipProperties', self.ViewStateExtendedClipProperties)
		add_bool(x_LiveSet, 'IsContentSplitterOpen', self.IsContentSplitterOpen)
		add_bool(x_LiveSet, 'IsExpressionSplitterOpen', self.IsExpressionSplitterOpen)
		set_list(x_LiveSet, self.ExpressionLanes, "ExpressionLanes", "ExpressionLane")
		set_list(x_LiveSet, self.ContentLanes, "ContentLanes", "ExpressionLane")
		add_value(x_LiveSet, 'ViewStateFxSlotCount', self.ViewStateFxSlotCount)
		add_value(x_LiveSet, 'ViewStateSessionMixerHeight', self.ViewStateSessionMixerHeight)
		x_Locators = ET.SubElement(x_LiveSet, "Locators")
		set_list(x_Locators, self.Locators, "Locators", "Locator")


		x_DetailClipKeyMidis = ET.SubElement(x_LiveSet, "DetailClipKeyMidis")
		add_lomid(x_LiveSet, 'TracksListWrapper', 0)
		add_lomid(x_LiveSet, 'VisibleTracksListWrapper', 0)
		add_lomid(x_LiveSet, 'ReturnTracksListWrapper', 0)
		add_lomid(x_LiveSet, 'ScenesListWrapper', 0)
		add_lomid(x_LiveSet, 'CuePointsListWrapper', 0)
		add_value(x_LiveSet, 'ChooserBar', self.ChooserBar)
		add_value(x_LiveSet, 'Annotation', self.Annotation)
		add_bool(x_LiveSet, 'SoloOrPflSavedValue', self.SoloOrPflSavedValue)
		add_bool(x_LiveSet, 'SoloInPlace', self.SoloInPlace)
		add_value(x_LiveSet, 'CrossfadeCurve', self.CrossfadeCurve)
		add_value(x_LiveSet, 'LatencyCompensation', self.LatencyCompensation)
		add_value(x_LiveSet, 'HighlightedTrackIndex', self.HighlightedTrackIndex)
		x_GroovePool = ET.SubElement(x_LiveSet, "GroovePool")
		add_value(x_GroovePool, 'LomId', 0)
		set_list(x_GroovePool, self.Grooves, "Grooves", "Groove")
		add_bool(x_LiveSet, 'AutomationMode', self.AutomationMode)
		add_bool(x_LiveSet, 'SnapAutomationToGrid', self.SnapAutomationToGrid)
		add_bool(x_LiveSet, 'ArrangementOverdub', self.ArrangementOverdub)
		add_value(x_LiveSet, 'ColorSequenceIndex', self.ColorSequenceIndex)
		x_AutoColorPickerForPlayerAndGroupTracks = ET.SubElement(x_LiveSet, "AutoColorPickerForPlayerAndGroupTracks")
		add_value(x_AutoColorPickerForPlayerAndGroupTracks, 'NextColorIndex', 16)
		x_AutoColorPickerForReturnAndMasterTracks = ET.SubElement(x_LiveSet, "AutoColorPickerForReturnAndMasterTracks")
		add_value(x_AutoColorPickerForReturnAndMasterTracks, 'NextColorIndex', 8)
		add_value(x_LiveSet, 'ViewData', {})
		add_bool(x_LiveSet, 'MidiFoldIn', self.MidiFoldIn)
		add_value(x_LiveSet, 'MidiFoldMode', self.MidiFoldMode)
		add_bool(x_LiveSet, 'MultiClipFocusMode', self.MultiClipFocusMode)
		add_value(x_LiveSet, 'MultiClipLoopBarHeight', self.MultiClipLoopBarHeight)
		add_bool(x_LiveSet, 'MidiPrelisten', self.MidiPrelisten)
		x_LinkedTrackGroups = ET.SubElement(x_LiveSet, "LinkedTrackGroups")
		add_value(x_LiveSet, 'AccidentalSpellingPreference', self.AccidentalSpellingPreference)
		add_bool(x_LiveSet, 'PreferFlatRootNote', self.PreferFlatRootNote)
		add_bool(x_LiveSet, 'UseWarperLegacyHiQMode', self.UseWarperLegacyHiQMode)
		self.VideoWindowRect.write(x_LiveSet)

		add_bool(x_LiveSet, 'ShowVideoWindow', self.ShowVideoWindow)
		add_value(x_LiveSet, 'TrackHeaderWidth', self.TrackHeaderWidth)
		add_bool(x_LiveSet, 'ViewStateArrangerHasDetail', self.ViewStateArrangerHasDetail)
		add_bool(x_LiveSet, 'ViewStateSessionHasDetail', self.ViewStateSessionHasDetail)
		add_bool(x_LiveSet, 'ViewStateDetailIsSample', self.ViewStateDetailIsSample)
		self.ViewStates.write(x_LiveSet)

		xmlstr = minidom.parseString(ET.tostring(x_root)).toprettyxml(indent="\t")
		with open(output_file, "w") as f:
			f.write(xmlstr)