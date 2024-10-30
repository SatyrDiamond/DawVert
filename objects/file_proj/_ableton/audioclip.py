# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj._ableton.func import *
from objects.file_proj._ableton.clip import *

class ableton_AudioClip:
	def __init__(self, xmltag):
		from objects.file_proj._ableton.fileref import ableton_SampleRef
		self.Time = float(xmltag.get('Time')) if xmltag != None else 0
		self.LomId = ableton_LomId(xmltag)
		self.CurrentStart = float(get_value(xmltag, 'CurrentStart', 0))
		self.CurrentEnd = float(get_value(xmltag, 'CurrentEnd', 16))
		self.Loop = ableton_Loop(xmltag)
		self.Name = get_value(xmltag, 'Name', '')
		self.Annotation = get_value(xmltag, 'Annotation', '')
		self.Color = int(get_value(xmltag, 'Color', 2))

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
		self.SampleRef = ableton_SampleRef(xmltag)
		self.Onsets = ableton_Onsets(xmltag.findall('Onsets')[0] if xmltag else None)

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
		self.Fades = ableton_Fades(xmltag.findall('Fades')[0] if xmltag else None)
		self.PitchCoarse = float(get_value(xmltag, 'PitchCoarse', 0))
		self.PitchFine = float(get_value(xmltag, 'PitchFine', 0))
		self.SampleVolume = float(get_value(xmltag, 'SampleVolume', 1))
		self.MarkerDensity = float(get_value(xmltag, 'MarkerDensity', 2))
		self.AutoWarpTolerance = int(get_value(xmltag, 'AutoWarpTolerance', 4))
		self.WarpMarkers = get_list(xmltag, 'WarpMarkers', 'WarpMarker', ableton_WarpMarker)
		self.SavedWarpMarkersForStretched = get_list(xmltag, 'SavedWarpMarkersForStretched', 'WarpMarker', ableton_WarpMarker)
		self.MarkersGenerated = get_bool(xmltag, 'MarkersGenerated', False)
		self.IsSongTempoMaster = get_bool(xmltag, 'IsSongTempoMaster', False)

	def set_dur(self, duration):
		self.CurrentStart = float(get_value(xmltag, 'CurrentStart', 0))
		self.CurrentEnd = self.CurrentStart*duration

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
		if xmltag:
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
		self.IsDefaultFadeIn = get_bool(xmltag, 'IsDefaultFadeIn', False)
		self.IsDefaultFadeOut = get_bool(xmltag, 'IsDefaultFadeOut', False)

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
