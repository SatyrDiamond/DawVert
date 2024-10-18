# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
from functions import data_values
from xml.dom import minidom
import gzip
from objects.exceptions import ProjectFileParserException

from objects.file_proj._ableton.func import *
from objects.file_proj._ableton.param import *
from objects.file_proj._ableton.automation import *
from objects.file_proj._ableton.tracks import *

mixerp_unused_id = data_values.counter(1000)
counter_unused_id = data_values.counter(30000)

# --------------------------------------------- Device ---------------------------------------------

def paramprint(itype, tag):
	print(itype, tag)

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
				try:
					alsbytes.seek(0)
					xmlstring = alsbytes.read().decode()
				except:
					raise ProjectFileParserException('ableton: file is not GZIP or XML')

		try: root = ET.fromstring(xmlstring)
		except ET.ParseError as t:
			raise ProjectFileParserException('ableton: XML parsing error: '+str(t))

		abletonversion = root.get('MinorVersion').split('.')[0]
		if abletonversion != '11':
			raise ProjectFileParserException('ableton: Version '+abletonversion+' is not supported.')
		#if abletonversion not in ['10', '11']:
		#	raise ProjectFileParserException('ableton: Version '+abletonversion+' is not supported.')

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
		return True

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

		self.Tracks.append(['audio', als_track])
		return als_track

	def add_return_track(self, i_id):
		als_track = ableton_ReturnTrack(None)
		als_track.Id = i_id

		als_track.DeviceChain.FreezeSequencer.ClipSlotList = {}

		self.Tracks.append(['return', als_track])
		return als_track

	def add_group_track(self, i_id):
		als_track = ableton_GroupTrack(None)
		als_track.Id = i_id

		als_track.DeviceChain.FreezeSequencer.ClipSlotList = {}

		self.Tracks.append(['group', als_track])
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

		self.Tracks.append(['midi', als_track])
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
		with open(output_file, "wb") as f:
			f.write(xmlstr.encode("UTF-8"))