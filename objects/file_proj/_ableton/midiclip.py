# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj._ableton.func import *
from objects.file_proj._ableton.clip import *

class ableton_MidiClip:
	def __init__(self, xmltag):
		self.Time = float(xmltag.get('Time')) if xmltag else 0
		self.LomId = ableton_LomId(xmltag)
		self.CurrentStart = float(get_value(xmltag, 'CurrentStart', 0))
		self.CurrentEnd = float(get_value(xmltag, 'CurrentEnd', 16))
		self.Loop = ableton_Loop(xmltag)
		self.Name = get_value(xmltag, 'Name', '')
		self.Annotation = get_value(xmltag, 'Annotation', '')
		self.Color = int(get_value(xmltag, 'Color', 0))

		self.LaunchMode = int(get_value(xmltag, 'LaunchMode', 0))
		self.LaunchQuantisation = int(get_value(xmltag, 'LaunchQuantisation', 0))
		from objects.file_proj._ableton.automation import ableton_RemoteableTimeSignature
		if xmltag:
			x_TimeSignature = xmltag.findall('TimeSignature')[0]
			self.TimeSignatures = get_list(x_TimeSignature, 'TimeSignatures', 'RemoteableTimeSignature', ableton_RemoteableTimeSignature)
			x_Envelopes = xmltag.findall('Envelopes')[0]
			from objects.file_proj._ableton.automation import ableton_AutomationEnvelope
			self.Envelopes = get_list(x_Envelopes, 'Envelopes', 'ClipEnvelope', ableton_AutomationEnvelope)
		else:
			self.TimeSignatures = {0: ableton_RemoteableTimeSignature(None)}
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

class ableton_x_MidiNoteEvent:
	__slots__ = ['Time','Duration','Velocity','VelocityDeviation','OffVelocity','Probability','IsEnabled','NoteId']
	def __init__(self, xmltag):
		self.VelocityDeviation = 0
		self.Time = 1.25
		self.Duration = 0.75
		self.Velocity = 100
		self.OffVelocity = 64
		self.Probability = 1
		self.IsEnabled = True
		self.NoteId = 0
		if xmltag != None:
			VelocityDeviation = xmltag.get('VelocityDeviation')
			Probability = xmltag.get('Probability')
			self.Time = float(xmltag.get('Time'))
			self.Duration = float(xmltag.get('Duration'))
			self.Velocity = float(xmltag.get('Velocity'))
			if VelocityDeviation != None: self.VelocityDeviation = float(VelocityDeviation)
			if Probability != None: self.Probability = float(Probability)
			self.OffVelocity = int(xmltag.get('OffVelocity'))
			self.IsEnabled = bool(['false','true'].index(xmltag.get('IsEnabled')))
			self.NoteId = int(xmltag.get('NoteId'))

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
		if xmltag:
			self.NoteId = int(xmltag.get('NoteId'))
			self.CC = int(xmltag.get('CC'))
			x_Events = xmltag.findall('Events')[0]
			self.Events = [ableton_x_PerNoteEvent(x) for x in x_Events.findall('PerNoteEvent')]
		else:
			self.NoteId = 0
			self.CC = -2
			self.Events = []

	def write(self, xmltag):
		xmltag.set('NoteId', str(self.NoteId))
		xmltag.set('CC', str(self.CC))
		x_Events = ET.SubElement(xmltag, "Events")
		for x in self.Events:
			x.write(x_Events)
