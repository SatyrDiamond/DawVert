# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj._ableton.func import *
from objects.file_proj._ableton.fileref import *
from objects.file_proj._ableton.audioclip import *

class ableton_SlicePoint:
	def __init__(self, xmltag):
		if xmltag != None:
			self.TimeInSeconds = float(xmltag.get('TimeInSeconds'))
			self.Rank = float(xmltag.get('Rank'))
			self.NormalizedEnergy = float(xmltag.get('NormalizedEnergy'))
		else:
			self.TimeInSeconds = 0
			self.Rank = 0
			self.NormalizedEnergy = 0

	def write(self, xmltag):
		xmltag.set('TimeInSeconds', str(self.TimeInSeconds))
		xmltag.set('Rank', str(int(self.Rank)))
		xmltag.set('NormalizedEnergy', str(self.NormalizedEnergy))

class ableton_SampleRange:
	def __init__(self, xmltag, name):
		self.name = name
		if xmltag:
			x_range = xmltag.findall(self.name)[0]
			self.Min = float(get_value(x_range, 'Min', 0))
			self.Max = float(get_value(x_range, 'Max', 127))
			self.CrossfadeMin = float(get_value(x_range, 'CrossfadeMin', 0))
			self.CrossfadeMax = float(get_value(x_range, 'CrossfadeMax', 127))
		else:
			self.Min = 0
			self.Max = 127
			self.CrossfadeMin = 0
			self.CrossfadeMax = 127

	def write(self, xmltag):
		x_range = ET.SubElement(xmltag, self.name)
		add_value(x_range, 'Min', self.Min)
		add_value(x_range, 'Max', self.Max)
		add_value(x_range, 'CrossfadeMin', self.CrossfadeMin)
		add_value(x_range, 'CrossfadeMax', self.CrossfadeMax)

class ableton_SampleLoop:
	def __init__(self, xmltag, name):
		self.name = name
		if xmltag:
			x_range = xmltag.findall(self.name)[0]
			self.Start = float(get_value(x_range, 'Start', 0))
			self.End = float(get_value(x_range, 'End', 1))
			self.Mode = float(get_value(x_range, 'Mode', 3))
			self.Crossfade = float(get_value(x_range, 'Crossfade', 0))
			self.Detune = float(get_value(x_range, 'Detune', 0))
		else:
			self.Start = 0
			self.End = 1
			self.Mode = 3
			self.Crossfade = 0
			self.Detune = 0

	def write(self, xmltag):
		x_range = ET.SubElement(xmltag, self.name)
		add_value(x_range, 'Start', self.Start)
		add_value(x_range, 'End', self.End)
		add_value(x_range, 'Mode', self.Mode)
		add_value(x_range, 'Crossfade', self.Crossfade)
		add_value(x_range, 'Detune', self.Detune)

class ableton_SampleWarpProperties:
	def __init__(self, xmltag):
		self.WarpMarkers = get_list(xmltag, 'WarpMarkers', 'WarpMarker', ableton_WarpMarker)
		self.WarpMode = int(get_value(xmltag, 'WarpMode', 0))
		self.GranularityTones = float(get_value(xmltag, 'GranularityTones', 30))
		self.GranularityTexture = float(get_value(xmltag, 'GranularityTexture', 65))
		self.FluctuationTexture = float(get_value(xmltag, 'FluctuationTexture', 25))
		self.TransientResolution = int(get_value(xmltag, 'TransientResolution', 6))
		self.TransientLoopMode = int(get_value(xmltag, 'TransientLoopMode', 2))
		self.TransientEnvelope = int(get_value(xmltag, 'TransientEnvelope', 100))
		self.ComplexProFormants = float(get_value(xmltag, 'ComplexProFormants', 100))
		self.ComplexProEnvelope = int(get_value(xmltag, 'ComplexProEnvelope', 128))
		self.IsWarped = get_bool(xmltag, 'IsWarped', False)
		self.Onsets = ableton_Onsets(xmltag.findall('Onsets')[0] if xmltag else None)
		if xmltag:
			x_TimeSignature = xmltag.findall('TimeSignature')[0]
			self.TimeSignatures = get_list(x_TimeSignature, 'TimeSignatures', 'RemoteableTimeSignature', ableton_RemoteableTimeSignature)
		else:
			self.TimeSignatures = {0: ableton_RemoteableTimeSignature(None)}
			self.Envelopes = {}
		self.Grid = ableton_Grid(xmltag, 'BeatGrid')

	def write(self, xmlin):
		xmltag = ET.SubElement(xmlin, 'SampleWarpProperties')
		set_list(xmltag, self.WarpMarkers, 'WarpMarkers', 'WarpMarker')
		add_value(xmltag, 'WarpMode', self.WarpMode)
		add_value(xmltag, 'GranularityTones', self.GranularityTones)
		add_value(xmltag, 'GranularityTexture', self.GranularityTexture)
		add_value(xmltag, 'FluctuationTexture', self.FluctuationTexture)
		add_value(xmltag, 'ComplexProFormants', self.ComplexProFormants)
		add_value(xmltag, 'ComplexProEnvelope', self.ComplexProEnvelope)
		add_value(xmltag, 'TransientResolution', self.TransientResolution)
		add_value(xmltag, 'TransientLoopMode', self.TransientLoopMode)
		add_value(xmltag, 'TransientEnvelope', self.TransientEnvelope)
		add_bool(xmltag, 'IsWarped', self.IsWarped)
		x_Onsets = ET.SubElement(xmltag, "Onsets")
		self.Onsets.write(x_Onsets)
		x_TimeSignature = ET.SubElement(xmltag, "TimeSignature")
		set_list(x_TimeSignature, self.TimeSignatures, "TimeSignatures", "RemoteableTimeSignature")
		self.Grid.write(xmltag)
		
class ableton_MultiSamplePart:
	def __init__(self, xmltag):
		self.LomId = ableton_LomId(xmltag)
		self.Name = get_value(xmltag, 'Name', '')
		self.Selection = get_bool(xmltag, 'Selection', False)
		self.IsActive = get_bool(xmltag, 'IsActive', True)
		self.Solo = get_bool(xmltag, 'Solo', False)
		self.KeyRange = ableton_SampleRange(xmltag, 'KeyRange')
		self.VelocityRange = ableton_SampleRange(xmltag, 'VelocityRange')
		self.SelectorRange = ableton_SampleRange(xmltag, 'SelectorRange')
		self.RootKey = get_value(xmltag, 'RootKey', 60)
		self.Detune = get_value(xmltag, 'Detune', 0)
		self.TuneScale = get_value(xmltag, 'TuneScale', 100)
		self.Panorama = get_value(xmltag, 'Panorama', 0)
		self.Volume = get_value(xmltag, 'Volume', 1)
		self.Link = get_bool(xmltag, 'Link', False)
		self.SampleStart = get_value(xmltag, 'SampleStart', 0)
		self.SampleEnd = get_value(xmltag, 'SampleEnd', 1)
		self.SustainLoop = ableton_SampleLoop(xmltag, 'SustainLoop')
		self.ReleaseLoop = ableton_SampleLoop(xmltag, 'ReleaseLoop')
		self.SampleRef = ableton_SampleRef(xmltag)
		self.SlicingThreshold = get_value(xmltag, 'SlicingThreshold', 100)
		self.SlicingBeatGrid = get_value(xmltag, 'SlicingBeatGrid', 4)
		self.SlicingRegions = get_value(xmltag, 'SlicingRegions', 8)
		self.SlicingStyle = get_value(xmltag, 'SlicingStyle', 0)
		x_SampleWarpProperties = xmltag.findall('SampleWarpProperties') if xmltag else []
		self.SampleWarpProperties = ableton_SampleWarpProperties(x_SampleWarpProperties[0] if x_SampleWarpProperties else None)
		x_Slicepoints = xmltag.findall('SlicePoints') if xmltag else []
		self.SlicePoints = []
		if x_Slicepoints:
			for slicex in x_Slicepoints[0]:
				if slicex.tag == 'SlicePoint':
					self.SlicePoints.append(ableton_SlicePoint(slicex))

	def add_slice(self):
		s_obj = ableton_SlicePoint(None)
		self.SlicePoints.append(s_obj)
		return s_obj

	def write(self, xmltag):
		xmltag.set('HasImportedSlicePoints', 'true')
		xmltag.set('NeedsAnalysisData', 'false')
		self.LomId.write(xmltag)
		add_value(xmltag, 'Name', self.Name)
		add_bool(xmltag, 'Selection', self.Selection)
		add_bool(xmltag, 'IsActive', self.IsActive)
		add_bool(xmltag, 'Solo', self.Solo)
		self.KeyRange.write(xmltag)
		self.VelocityRange.write(xmltag)
		self.SelectorRange.write(xmltag)
		add_value(xmltag, 'RootKey', self.RootKey)
		add_value(xmltag, 'Detune', self.Detune)
		add_value(xmltag, 'TuneScale', self.TuneScale)
		add_value(xmltag, 'Panorama', self.Panorama)
		add_value(xmltag, 'Volume', self.Volume)
		add_bool(xmltag, 'Link', self.Link)
		add_value(xmltag, 'SampleStart', self.SampleStart)
		add_value(xmltag, 'SampleEnd', self.SampleEnd)
		self.SustainLoop.write(xmltag)
		self.ReleaseLoop.write(xmltag)
		self.SampleRef.write(xmltag)
		add_value(xmltag, 'SlicingThreshold', self.SlicingThreshold)
		add_value(xmltag, 'SlicingBeatGrid', self.SlicingBeatGrid)
		add_value(xmltag, 'SlicingRegions', self.SlicingRegions)
		add_value(xmltag, 'SlicingStyle', self.SlicingStyle)
		self.SampleWarpProperties.write(xmltag)
		x_SlicePoints = ET.SubElement(xmltag, "SlicePoints")
		for slicex in self.SlicePoints:
			slicep = ET.SubElement(x_SlicePoints, "SlicePoint")
			slicex.write(slicep)
		ET.SubElement(xmltag, "ManualSlicePoints")
		ET.SubElement(xmltag, "BeatSlicePoints")
		ET.SubElement(xmltag, "RegionSlicePoints")
		add_bool(xmltag, 'UseDynamicBeatSlices', False)
		add_bool(xmltag, 'UseDynamicRegionSlices', False)
