# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj._ableton.param import *
from objects.file_proj._ableton.func import *
from objects.file_proj._ableton.automation import *
from objects.file_proj._ableton.visual import *
from objects.file_proj._ableton.device import *
from objects.file_proj import proj_ableton

import xml.etree.ElementTree as ET

class ableton_MainSequencer:
	def __init__(self, xmltag, tracktype):
		self.tracktype = tracktype
		self.ClipSlotList = {}
		self.MidiControllers = {}
		self.LomId = ableton_LomId(xmltag)
		self.IsExpanded = get_bool(xmltag, 'IsExpanded', True)
		self.On = ableton_Param(xmltag, 'On', 'bool')
		self.ModulationSourceCount = int(get_value(xmltag, 'ModulationSourceCount', 0))
		self.Pointee = get_pointee(xmltag, proj_ableton.counter_unused_id)

		self.LastSelectedTimeableIndex = int(get_value(xmltag, 'LastSelectedTimeableIndex', 0))
		self.LastSelectedClipEnvelopeIndex = int(get_value(xmltag, 'LastSelectedClipEnvelopeIndex', 0))
		self.IsFolded = get_bool(xmltag, 'IsFolded', False)
		self.ShouldShowPresetName = get_bool(xmltag, 'ShouldShowPresetName', False)
		self.UserName = get_value(xmltag, 'UserName', '')
		self.Annotation = get_value(xmltag, 'Annotation', '')
		if not xmltag:
			if tracktype != 'return':
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
			self.Pointee = proj_ableton.counter_unused_id.get()
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
		self.Pointee = get_pointee(xmltag, None)
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
				self.Pointee = proj_ableton.mixerp_unused_id.get()
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

class ableton_TakeLanes:
	def __init__(self, xmltag):
		self.AreTakeLanesFolded = True
		self.TakeLanes = {}
		if xmltag:
			takelanes = xmltag.findall('TakeLanes')
			if takelanes:
				x_TakeLanes = takelanes[0]
				self.AreTakeLanesFolded = get_bool(x_TakeLanes, 'AreTakeLanesFolded', False)
				self.TakeLanes = get_list(x_TakeLanes, 'TakeLanes', 'TakeLane', ableton_TakeLane)

	def write(self, xmltag):
		x_TakeLanes = ET.SubElement(xmltag, "TakeLanes")
		set_list(x_TakeLanes, self.TakeLanes, "TakeLanes", "TakeLane")
		add_bool(x_TakeLanes, 'AreTakeLanesFolded', self.AreTakeLanesFolded)

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
		self.Color = int(get_value_multi(xmltag, ['Color', 'ColorIndex'], 0))
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

	def add_midiclip(self, clipid):
		ClipTimeable = self.DeviceChain.MainSequencer.ClipTimeable
		midiclip_obj = ableton_MidiClip(None)
		ClipTimeable.Events.append([clipid, 'MidiClip', midiclip_obj])
		return midiclip_obj

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
		self.Color = int(get_value_multi(xmltag, ['Color', 'ColorIndex'], 0))
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

	def add_audioclip(self, clipid):
		ClipTimeable = self.DeviceChain.MainSequencer.ClipTimeable
		audioclip_obj = ableton_AudioClip(None)
		ClipTimeable.Events.append([clipid, 'AudioClip', audioclip_obj])
		return audioclip_obj

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
		self.Color = int(get_value_multi(xmltag, ['Color', 'ColorIndex'], 0))
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
		self.Color = int(get_value_multi(xmltag, ['Color', 'ColorIndex'], 0))
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
		self.Color = int(get_value_multi(xmltag, ['Color', 'ColorIndex'], 13))
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
		self.Color = int(get_value_multi(xmltag, ['Color', 'ColorIndex'], -1))
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
			AutomationLane.LaneHeight = 85
			if tracktype == 'master': 
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
				
	def add_device(self, devicename):
		devicenum = len(self.devices)+2
		device_obj = ableton_Device(None)
		device_obj.id = devicenum
		device_obj.name = devicename
		device_obj.On.setvalue(True)
		self.devices.append(device_obj)
		return device_obj

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
