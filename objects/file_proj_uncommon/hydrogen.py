# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import logging

def getbool(v): return v=='true'

# ============================================= drumkit ============================================= 

class hydrogen_drumkitComponent:
	def __init__(self, xmldata):
		self.id = 0
		self.name = ''
		self.volume = 1
		if xmldata: self.read(xmldata)

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'id': self.id = x_part.text
			if name == 'name': self.name = x_part.text
			if name == 'volume': self.volume = x_part.text

# ============================================= instrument ============================================= 

class hydrogen_layer:
	def __init__(self, xmldata):
		self.filename = ''
		self.min = 0
		self.max = 0
		self.gain = 1
		self.pitch = 0
		self.ismodified = False
		self.smode = 'forward'
		self.startframe = 0
		self.loopframe = 0
		self.loops = 0
		self.endframe = 0
		self.userubber = 0
		self.rubberdivider = 1
		self.rubberCsettings = 0
		self.rubberPitch = 1
		if xmldata: self.read(xmldata)

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'filename': self.filename = x_part.text
			if name == 'min': self.min = float(x_part.text)
			if name == 'max': self.max = float(x_part.text)
			if name == 'gain': self.gain = float(x_part.text)
			if name == 'pitch': self.pitch = float(x_part.text)
			if name == 'ismodified': self.ismodified = getbool(x_part.text)
			if name == 'smode': self.smode = x_part.text
			if name == 'startframe': self.startframe = float(x_part.text)
			if name == 'loopframe': self.loopframe = float(x_part.text)
			if name == 'loops': self.loops = float(x_part.text)
			if name == 'endframe': self.endframe = float(x_part.text)
			if name == 'userubber': self.userubber = float(x_part.text)
			if name == 'rubberdivider': self.rubberdivider = float(x_part.text)
			if name == 'rubberCsettings': self.rubberCsettings = float(x_part.text)
			if name == 'rubberPitch': self.rubberPitch = float(x_part.text)

class hydrogen_instrumentComponent:
	def __init__(self, xmldata):
		self.component_id = 0
		self.gain = 1
		self.layers = []
		if xmldata: self.read(xmldata)

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'component_id': self.component_id = int(x_part.text)
			if name == 'gain': self.gain = float(x_part.text)
			if name == 'layer': self.layers.append(hydrogen_layer(x_part))

class hydrogen_instrument:
	def __init__(self, xmldata):
		self.id = 0
		self.name = ''
		self.drumkitPath = ''
		self.drumkit = ''
		self.volume = 1
		self.isMuted = False
		self.isSoloed = False
		self.pan_L = 1
		self.pan_R = 1
		self.pitchOffset = 0
		self.randomPitchFactor = 0
		self.gain = 1
		self.applyVelocity = True
		self.filterActive = False
		self.filterCutoff = 1
		self.filterResonance = 0
		self.Attack = 0
		self.Decay = 0
		self.Sustain = 1
		self.Release = 1000
		self.muteGroup = -1
		self.midiOutChannel = -1
		self.midiOutNote = 36
		self.isStopNote = False
		self.sampleSelectionAlgo = 'VELOCITY'
		self.isHihat = -1
		self.lower_cc = 0
		self.higher_cc = 127
		self.FX1Level = 0
		self.FX2Level = 0
		self.FX3Level = 0
		self.FX4Level = 0
		self.instrumentComponent = hydrogen_instrumentComponent(None)
		if xmldata: self.read(xmldata)

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'id': self.id = int(x_part.text)
			if name == 'name': self.name = x_part.text
			if name == 'drumkitPath': self.drumkitPath = x_part.text
			if name == 'drumkit': self.drumkit = x_part.text
			if name == 'volume': self.volume = float(x_part.text)
			if name == 'isMuted': self.isMuted = getbool(x_part.text)
			if name == 'isSoloed': self.isSoloed = getbool(x_part.text)
			if name == 'pan_L': self.pan_L = float(x_part.text)
			if name == 'pan_R': self.pan_R = float(x_part.text)
			if name == 'pitchOffset': self.pitchOffset = float(x_part.text)
			if name == 'randomPitchFactor': self.randomPitchFactor = float(x_part.text)
			if name == 'gain': self.gain = float(x_part.text)
			if name == 'applyVelocity': self.applyVelocity = getbool(x_part.text)
			if name == 'filterActive': self.filterActive = getbool(x_part.text)
			if name == 'filterCutoff': self.filterCutoff = float(x_part.text)
			if name == 'filterResonance': self.filterResonance = float(x_part.text)
			if name == 'Attack': self.Attack = float(x_part.text)
			if name == 'Decay': self.Decay = float(x_part.text)
			if name == 'Sustain': self.Sustain = float(x_part.text)
			if name == 'Release': self.Release = float(x_part.text)
			if name == 'muteGroup': self.muteGroup = float(x_part.text)
			if name == 'midiOutChannel': self.midiOutChannel = float(x_part.text)
			if name == 'midiOutNote': self.midiOutNote = float(x_part.text)
			if name == 'isStopNote': self.isStopNote = getbool(x_part.text)
			if name == 'sampleSelectionAlgo': self.sampleSelectionAlgo = x_part.text
			if name == 'isHihat': self.isHihat = float(x_part.text)
			if name == 'lower_cc': self.lower_cc = float(x_part.text)
			if name == 'higher_cc': self.higher_cc = float(x_part.text)
			if name == 'FX1Level': self.FX1Level = float(x_part.text)
			if name == 'FX2Level': self.FX2Level = float(x_part.text)
			if name == 'FX3Level': self.FX3Level = float(x_part.text)
			if name == 'FX4Level': self.FX4Level = float(x_part.text)
			if name == 'instrumentComponent': self.instrumentComponent.read(x_part)

# ============================================= pattern ============================================= 

class hydrogen_note:
	def __init__(self, xmldata):
		self.position = 0
		self.leadlag = 0
		self.velocity = 0.8
		self.pan = 0
		self.pitch = 0
		self.key = ''
		self.length = -1
		self.instrument = 0
		self.note_off = False
		self.probability = 1
		if xmldata: self.read(xmldata)

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'position': self.position = float(x_part.text)
			if name == 'leadlag': self.leadlag = float(x_part.text)
			if name == 'velocity': self.velocity = float(x_part.text)
			if name == 'pan': self.pan = float(x_part.text)
			if name == 'pitch': self.pitch = float(x_part.text)
			if name == 'key': self.key = x_part.text
			if name == 'length': self.length = float(x_part.text)
			if name == 'instrument': self.instrument = int(x_part.text)
			if name == 'note_off': self.note_off = getbool(x_part.text)
			if name == 'probability': self.probability = float(x_part.text)

class hydrogen_pattern:
	def __init__(self, xmldata):
		self.name = ''
		self.info = ''
		self.category = ''
		self.size = 192
		self.denominator = 4
		self.noteList = []
		if xmldata: self.read(xmldata)

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'name': self.name = x_part.text
			if name == 'info': self.info = x_part.text
			if name == 'category': self.category = x_part.text
			if name == 'size': self.size = int(x_part.text)
			if name == 'denominator': self.denominator = int(x_part.text)
			if name == 'noteList': 
				for x_inpart in x_part:
					if x_inpart.tag == 'note': 
						self.noteList.append(hydrogen_note(x_inpart))

# ============================================= main ============================================= 

class hydrogen_virtualpattern:
	def __init__(self, xmldata):
		self.name = ''
		self.virtual = ''
		if xmldata: self.read(xmldata)

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'name': self.name = x_part.text
			if name == 'virtual': self.info = x_part.text

class hydrogen_path:
	def __init__(self, xmldata):
		self.adjust = None
		self.points = {}
		if xmldata: self.read(xmldata)

	def read(self, xmldata):
		self.adjust = xmldata.get('adjust')
		for x_part in xmldata:
			name = x_part.tag
			if name == 'point': self.points[float(x_part.get('x'))] = float(x_part.get('y'))

class hydrogen_newBPM:
	def __init__(self, xmldata):
		self.bar = 0
		self.bpm = 120
		if xmldata: self.read(xmldata)

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'BAR': self.bar = int(x_part.text)
			if name == 'BPM': self.bpm = float(x_part.text)

class hydrogen_newTAG:
	def __init__(self, xmldata):
		self.bar = 0
		self.tag = ''
		if xmldata: self.read(xmldata)

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'BAR': self.bar = int(x_part.text)
			if name == 'TAG': self.tag = x_part.text

class hydrogen_song:
	def __init__(self):
		self.version = "1.2.4"
		self.bpm = 120
		self.volume = 0.5
		self.isMuted = False
		self.metronomeVolume = 0.5
		self.name = "Untitled Song"
		self.author = "hydrogen"
		self.notes = "..."
		self.license = "undefined license"
		self.loopEnabled = False
		self.patternModeMode = True
		self.playbackTrackFilename = ""
		self.playbackTrackEnabled = False
		self.playbackTrackVolume = 0
		self.action_mode = 0
		self.isPatternEditorLocked = False
		self.isTimelineActivated = False
		self.mode = "pattern"
		self.pan_law_type = "RATIO_STRAIGHT_POLYGONAL"
		self.pan_law_k_norm = 1.33333
		self.humanize_time = 0
		self.humanize_velocity = 0
		self.swing_factor = 0
		self.last_loaded_drumkit = "C:/Program Files/Hydrogen/data/drumkits/GMRockKit"
		self.last_loaded_drumkit_name = "GMRockKit"
		self.drumkitComponent = []
		self.instrumentList = []
		self.patternList = []
		self.virtualPatternList = []
		self.patternSequence = []
		self.timeLineTag = []
		self.automationPaths = []
		self.BPMTimeLine = []

	def load_from_file(self, input_file):
		x_root = ET.parse(input_file).getroot()
		for x_part in x_root:
			name = x_part.tag
			if name == 'version': self.version = x_part.text
			if name == 'bpm': self.bpm = float(x_part.text)
			if name == 'volume': self.volume = float(x_part.text)
			if name == 'isMuted': self.isMuted = getbool(x_part.text)
			if name == 'metronomeVolume': self.metronomeVolume = float(x_part.text)
			if name == 'name': self.name = x_part.text
			if name == 'author': self.author = x_part.text
			if name == 'notes': self.notes = x_part.text
			if name == 'license': self.license = x_part.text
			if name == 'loopEnabled': self.loopEnabled = getbool(x_part.text)
			if name == 'patternModeMode': self.patternModeMode = getbool(x_part.text)
			if name == 'playbackTrackFilename': self.playbackTrackFilename = x_part.text
			if name == 'playbackTrackEnabled': self.playbackTrackEnabled = getbool(x_part.text)
			if name == 'playbackTrackVolume': self.playbackTrackVolume = float(x_part.text)
			if name == 'action_mode': self.action_mode = int(x_part.text)
			if name == 'isPatternEditorLocked': self.isPatternEditorLocked = getbool(x_part.text)
			if name == 'isTimelineActivated': self.isTimelineActivated = getbool(x_part.text)
			if name == 'mode': self.mode = x_part.text
			if name == 'pan_law_type': self.pan_law_type = x_part.text
			if name == 'pan_law_k_norm': self.pan_law_k_norm = float(x_part.text)
			if name == 'humanize_time': self.humanize_time = float(x_part.text)
			if name == 'humanize_velocity': self.humanize_velocity = float(x_part.text)
			if name == 'swing_factor': self.swing_factor = float(x_part.text)
			if name == 'last_loaded_drumkit': self.last_loaded_drumkit = x_part.text
			if name == 'last_loaded_drumkit_name': self.last_loaded_drumkit_name = x_part.text
			if name == 'componentList': 
				for x_inpart in x_part:
					if x_inpart.tag == 'drumkitComponent': 
						self.drumkitComponent.append(hydrogen_drumkitComponent(x_inpart))
			if name == 'instrumentList': 
				for x_inpart in x_part:
					if x_inpart.tag == 'instrument': 
						self.instrumentList.append(hydrogen_instrument(x_inpart))
			if name == 'patternList': 
				for x_inpart in x_part:
					if x_inpart.tag == 'pattern': 
						self.patternList.append(hydrogen_pattern(x_inpart))
			if name == 'virtualPatternList': 
				for x_inpart in x_part:
					if x_inpart.tag == 'pattern': 
						self.virtualPatternList.append(hydrogen_virtualpattern(x_inpart))
			if name == 'patternSequence': 
				for x_inpart in x_part:
					if x_inpart.tag == 'group': 
						patpl = []
						self.patternSequence.append(patpl)
						for x_sinpart in x_inpart:
							if x_sinpart.tag == 'patternID': patpl.append(x_sinpart.text)
			if name == 'timeLineTag': 
				for x_inpart in x_part:
					if x_inpart.tag == 'newTAG': 
						self.timeLineTag.append(hydrogen_newTAG(x_inpart))
			if name == 'BPMTimeLine': 
				for x_inpart in x_part:
					if x_inpart.tag == 'newBPM': 
						self.BPMTimeLine.append(hydrogen_newBPM(x_inpart))
			if name == 'automationPaths': 
				for x_inpart in x_part:
					if x_inpart.tag == 'path': 
						self.automationPaths.append(hydrogen_path(x_inpart))
		return True