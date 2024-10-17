# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj._ableton.func import *
from objects.file_proj._ableton.tracks import *
from objects.file_proj import proj_ableton

class ableton_Device:
	def __init__(self, xmltag):
		self.params = ableton_paramset()
		self.LomId = ableton_LomId(xmltag)
		self.name = xmltag.tag if xmltag else 'noname'
		self.id = int(xmltag.get('Id')) if xmltag else 0
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
		if xmltag: 
			x_SourceContext = xmltag.findall('SourceContext')[0]
			self.SourceContext = get_list(x_SourceContext, 'Value', 'BranchSourceContext', ableton_SourceContext)
			self.params.scan(xmltag)
		else:
			self.SourceContext = {}

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
		self.params.create(x_DeviceData)
