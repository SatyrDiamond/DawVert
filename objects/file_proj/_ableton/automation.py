# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj._ableton.func import *
from objects.file_proj._ableton.clip import *
from objects.file_proj._ableton.fileref import *
from objects.file_proj._ableton.midiclip import *
from objects.file_proj._ableton.audioclip import *
from objects.file_proj import proj_ableton

import xml.etree.ElementTree as ET

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
		if not self.exists:
			self.exists = True
			self.id = proj_ableton.counter_unused_id.get()

	def write(self, xmltag):
		if self.exists:
			x_ReceiveTarget = ET.SubElement(xmltag, self.name)
			x_ReceiveTarget.set('Id', str(self.id))
			add_value(x_ReceiveTarget, 'LockEnvelope', self.lock)

# --------------------------------------------- AutomationLane ---------------------------------------------

class ableton_AutomationLane:
	__slots__ = ['SelectedDevice','SelectedEnvelope','IsContentSelectedInDocument','LaneHeight']
	def __init__(self, xmltag):
		self.SelectedDevice = int(get_value(xmltag, 'SelectedDevice', 0))
		self.SelectedEnvelope = int(get_value(xmltag, 'SelectedEnvelope', 0))
		self.IsContentSelectedInDocument = get_bool_multi(xmltag, ['IsContentSelectedInDocument', 'IsContentSelected'], False)
		self.LaneHeight = int(get_value(xmltag, 'LaneHeight', 68))
		# 11: IsContentSelectedInDocument
		# 10: IsContentSelected

	def write(self, xmltag):
		add_value(xmltag, 'SelectedDevice', self.SelectedDevice)
		add_value(xmltag, 'SelectedEnvelope', self.SelectedEnvelope)
		add_bool(xmltag, 'IsContentSelectedInDocument', self.IsContentSelectedInDocument)
		add_value(xmltag, 'LaneHeight', self.LaneHeight)

class ableton_AutomationLanes:
	__slots__ = ['AutomationLanes','AreAdditionalAutomationLanesFolded']
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
		xmltag.set('Value', str(['false','true'][int(bool(self.Value))]))

class ableton_Automation:
	__slots__ = ['Events', 'name']
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
	def add(self, PointeeId):
		envnum = len(self.Envelopes)
		AutomationEnvelope_obj = ableton_AutomationEnvelope(None)
		AutomationEnvelope_obj.PointeeId = PointeeId
		self.Envelopes[envnum] = AutomationEnvelope_obj
		return AutomationEnvelope_obj
	def write(self, xmltag):
		x_AutomationEnvelopes = ET.SubElement(xmltag, "AutomationEnvelopes")
		set_list(x_AutomationEnvelopes, self.Envelopes, 'Envelopes', 'AutomationEnvelope')
