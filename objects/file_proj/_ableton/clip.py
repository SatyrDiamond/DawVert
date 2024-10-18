# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj._ableton.func import *
from objects.file_proj._ableton.automation import *

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
		self.FixedNumerator = 1
		self.FixedDenominator = 16
		self.GridIntervalPixel = 20
		self.Ntoles = 2
		self.SnapToGrid = True
		self.Fixed = False
		if xmltag:
			x_Grid = xmltag.findall(name)
			if x_Grid:
				x_Grid = x_Grid[0]
				self.FixedNumerator = int(get_value(x_Grid, 'FixedNumerator', 1))
				self.FixedDenominator = int(get_value(x_Grid, 'FixedDenominator', 16))
				self.GridIntervalPixel = int(get_value(x_Grid, 'GridIntervalPixel', 20))
				self.Ntoles = int(get_value(x_Grid, 'Ntoles', 2))
				self.SnapToGrid = get_bool(x_Grid, 'SnapToGrid', True)
				self.Fixed = get_bool(x_Grid, 'Fixed', True)

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

		if xmltag:
			x_FollowAction = xmltag.findall('FollowAction')
			if x_FollowAction:
				x_FollowAction = x_FollowAction[0]
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
		self.RootNote = 0
		self.Name = 'Major'
		if xmltag:
			x_ScaleInformation = xmltag.findall('ScaleInformation')
			if x_ScaleInformation:
				x_ScaleInformation = x_ScaleInformation[0]
				self.RootNote = float(get_value(x_ScaleInformation, 'RootNote', 0))
				self.Name = get_value(x_ScaleInformation, 'Name', '')

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
