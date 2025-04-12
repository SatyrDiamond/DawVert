# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.binary_fmt import juce_binaryxml

class sampler_pad:
	def __init__(self):
		self.name = ''
		self.note = 60
		self.icon = 0
		self.colour = 0

	def read(self, bxml):
		attrib = bxml.attrib
		if 'name' in attrib: self.name = str(attrib['name'])
		if 'note' in attrib: self.note = int(attrib['note'])
		if 'icon' in attrib: self.icon = int(attrib['icon'])
		if 'colour' in attrib: self.colour = int(attrib['colour'])

	def write(self, bxml_data):
		bxml_main = bxml_data.add_child('PAD')
		bxml_main.set('name', self.name)
		if self.note: bxml_main.set('note', self.note)
		bxml_main.set('icon', self.icon)
		if self.colour: bxml_main.set('colour', self.colour)

class sampler_soundlayer:
	def __init__(self):
		self.active = 1
		self.name = ""
		self.reverse = 0
		self.sampleDataName = ""
		self.sampleDataHash = ""
		self.sampleIn = 0
		self.sampleLoopIn = 0
		self.sampleOut = 0
		self.sampleLoopOut = 0
		self.fineTune = 0
		self.highNote = 127
		self.lowNote = 0
		self.rootNote = 60
		self.gain = 0.0
		self.fixedPitch = False
		self.pitchShift = False
		self.looped = False
		self.loopMode = 0
		self.solo = False
		self.mute = False
		self.lowVelocity = 0
		self.highVelocity = 127
		self.chokeGroup = None
		self.soundparameters = {}
		self.offlineTimeStretch = 1.0
		self.offlinePitchShift = 0.0

	def read(self, bxml):
		attrib = bxml.attrib
		if 'active' in attrib: self.active = int(attrib['active'])
		if 'name' in attrib: self.name = str(attrib['name'])
		if 'reverse' in attrib: self.reverse = int(attrib['reverse'])
		if 'sampleDataName' in attrib: self.sampleDataName = str(attrib['sampleDataName'])
		if 'sampleDataHash' in attrib: self.sampleDataHash = str(attrib['sampleDataHash'])
		if 'sampleIn' in attrib: self.sampleIn = int(attrib['sampleIn'])
		if 'sampleLoopIn' in attrib: self.sampleLoopIn = int(attrib['sampleLoopIn'])
		if 'sampleOut' in attrib: self.sampleOut = int(attrib['sampleOut'])
		if 'sampleLoopOut' in attrib: self.sampleLoopOut = int(attrib['sampleLoopOut'])
		if 'fineTune' in attrib: self.fineTune = int(attrib['fineTune'])
		if 'highNote' in attrib: self.highNote = int(attrib['highNote'])
		if 'lowNote' in attrib: self.lowNote = int(attrib['lowNote'])
		if 'rootNote' in attrib: self.rootNote = int(attrib['rootNote'])
		if 'gain' in attrib: self.gain = float(attrib['gain'])
		if 'fixedPitch' in attrib: self.fixedPitch = bool(attrib['fixedPitch'])
		if 'pitchShift' in attrib: self.pitchShift = bool(attrib['pitchShift'])
		if 'looped' in attrib: self.looped = bool(attrib['looped'])
		if 'loopMode' in attrib: self.loopMode = int(attrib['loopMode'])
		if 'solo' in attrib: self.solo = bool(attrib['solo'])
		if 'mute' in attrib: self.mute = bool(attrib['mute'])
		if 'lowVelocity' in attrib: self.lowVelocity = int(attrib['lowVelocity'])
		if 'highVelocity' in attrib: self.highVelocity = int(attrib['highVelocity'])
		if 'chokeGroup' in attrib: self.chokeGroup = int(attrib['chokeGroup'])
		if 'offlineTimeStretch' in attrib: self.offlineTimeStretch = float(attrib['offlineTimeStretch'])
		if 'offlinePitchShift' in attrib: self.offlinePitchShift = float(attrib['offlinePitchShift'])
		for x in bxml:
			if x.tag == "SOUNDPARAMETER": 
				attrib = x.attrib
				if 'id' in attrib:
					self.soundparameters[str(attrib['id'])] = float(attrib['value']) if 'value' in attrib else None

	def write(self, bxml_data):
		bxml_main = bxml_data.add_child('SOUNDLAYER')
		bxml_main.set('active', self.active)
		bxml_main.set('name', self.name)
		bxml_main.set('reverse', self.reverse)
		bxml_main.set('sampleDataName', self.sampleDataName)
		if self.sampleDataHash: bxml_main.set('sampleDataHash', self.sampleDataHash)
		bxml_main.set('sampleIn', self.sampleIn)
		if self.sampleLoopIn: bxml_main.set('sampleLoopIn', self.sampleLoopIn)
		bxml_main.set('sampleOut', self.sampleOut)
		if self.sampleLoopOut: bxml_main.set('sampleLoopOut', self.sampleLoopOut)
		if self.fineTune: bxml_main.set('fineTune', self.fineTune)
		bxml_main.set('highNote', self.highNote)
		bxml_main.set('lowNote', self.lowNote)
		bxml_main.set('rootNote', self.rootNote)
		if self.gain: bxml_main.set('gain', self.gain)
		if self.fixedPitch: bxml_main.set('fixedPitch', self.fixedPitch)
		if self.pitchShift: bxml_main.set('pitchShift', self.pitchShift)
		if self.looped: bxml_main.set('looped', self.looped)
		if self.loopMode: bxml_main.set('loopMode', self.loopMode)
		if self.solo: bxml_main.set('solo', self.solo)
		if self.mute: bxml_main.set('mute', self.mute)
		bxml_main.set('lowVelocity', self.lowVelocity)
		bxml_main.set('highVelocity', self.highVelocity)
		if self.chokeGroup: bxml_main.set('chokeGroup', self.chokeGroup)
		if self.offlineTimeStretch != 1: bxml_main.set('offlineTimeStretch', self.offlineTimeStretch)
		if self.offlinePitchShift: bxml_main.set('offlinePitchShift', self.offlinePitchShift)

		for i, v in self.soundparameters.items():
			bxml_param = bxml_main.add_child('SOUNDPARAMETER')
			bxml_param.set('id', i)
			if v is not None: bxml_param.set('value', v)

# ==================================== TINYSAMPLER ====================================

class tinysampler:
	def __init__(self):
		self.version = 2
		self.fxOrder1 = 'reverb,delay,comp,filter,eq,dist,chorus'
		self.fxOrder2 = 'delay,reverb,comp,filter,eq,dist,chorus'
		self.currentPage = 0
		self.showScratchPad = False
		self.soundparameters = {}
		self.mpe = False
		self.voiceStealing = False
		self.mono = False
		self.playMode = 0
		self.soundlayers = []
		self.pads = {}

	def add_layer(self):
		soundlayer_obj = sampler_soundlayer()
		self.soundlayers.append(soundlayer_obj)
		return soundlayer_obj

	def read(self, bxml):
		attrib = bxml.attrib
		if 'version' in attrib: self.version = int(attrib['version'])
		if 'fxOrder1' in attrib: self.fxOrder1 = str(attrib['fxOrder1'])
		if 'fxOrder2' in attrib: self.fxOrder2 = str(attrib['fxOrder2'])
		if 'currentPage' in attrib: self.currentPage = int(attrib['currentPage'])
		if 'showScratchPad' in attrib: self.showScratchPad = bool(attrib['showScratchPad'])
		if 'mpe' in attrib: self.mpe = bool(attrib['mpe'])
		if 'voiceStealing' in attrib: self.voiceStealing = bool(attrib['voiceStealing'])
		if 'mono' in attrib: self.mono = bool(attrib['mono'])
		if 'playMode' in attrib: self.playMode = int(attrib['playMode'])
		for x in bxml:
			if x.tag == "SOUNDPARAMETER": 
				attrib = x.attrib
				if 'id' in attrib:
					self.soundparameters[str(attrib['id'])] = float(attrib['value']) if 'value' in attrib else None
			elif x.tag == "SOUNDLAYER": 
				soundlayer_obj = sampler_soundlayer()
				soundlayer_obj.read(x)
				self.soundlayers.append(soundlayer_obj)

	def write(self, bxml_data):
		bxml_main = bxml_data.add_child('TINYSAMPLER')
		bxml_main.set('version', self.version)
		if self.fxOrder1 is not None: bxml_main.set('fxOrder1', self.fxOrder1)
		if self.fxOrder2 is not None: bxml_main.set('fxOrder2', self.fxOrder2)
		if self.currentPage is not None: bxml_main.set('currentPage', self.currentPage)
		if self.showScratchPad == True: bxml_main.set('showScratchPad', self.showScratchPad)
		if self.playMode: bxml_main.set('playMode', self.playMode)
		if self.mpe == True: bxml_main.set('mpe', self.mpe)
		if self.voiceStealing == True: bxml_main.set('voiceStealing', self.voiceStealing)
		if self.mono == True: bxml_main.set('mono', self.mono)
		for i, v in self.soundparameters.items():
			bxml_param = bxml_main.add_child('SOUNDPARAMETER')
			bxml_param.set('id', i)
			if v is not None: bxml_param.set('value', v)
		for x in self.soundlayers: x.write(bxml_main)

# ==================================== MICROSAMPLER ====================================

class microsampler:
	def __init__(self):
		self.version = 2
		self.currentPage = 0
		self.soundparameters = {}
		self.voiceStealing = False
		self.playMode = 0
		self.soundlayers = []
		self.pads = {}

	def add_layer(self):
		soundlayer_obj = sampler_soundlayer()
		self.soundlayers.append(soundlayer_obj)
		return soundlayer_obj

	def add_pad(self, key):
		pad_obj = sampler_pad()
		pad_obj.note = key
		self.pads[key] = pad_obj
		return pad_obj

	def read(self, bxml):
		attrib = bxml.attrib
		if 'version' in attrib: self.version = int(attrib['version'])
		if 'currentPage' in attrib: self.currentPage = int(attrib['currentPage'])
		if 'voiceStealing' in attrib: self.voiceStealing = bool(attrib['voiceStealing'])
		if 'playMode' in attrib: self.playMode = int(attrib['playMode'])
		for x in bxml:
			if x.tag == "SOUNDPARAMETER": 
				attrib = x.attrib
				if 'id' in attrib:
					self.soundparameters[str(attrib['id'])] = float(attrib['value']) if 'value' in attrib else None
			elif x.tag == "SOUNDLAYER": 
				soundlayer_obj = sampler_soundlayer()
				soundlayer_obj.read(x)
				self.soundlayers.append(soundlayer_obj)
			elif x.tag == "PAD": 
				pad_obj = sampler_pad()
				pad_obj.read(x)
				self.pads[pad_obj.note] = pad_obj

	def write(self, bxml_data):
		bxml_main = bxml_data.add_child('MICROSAMPLER')
		if self.version is not None: bxml_main.set('version', self.version)
		if self.playMode is not None: bxml_main.set('playMode', self.playMode)
		if self.currentPage is not None: bxml_main.set('currentPage', self.currentPage)
		if self.voiceStealing == True: bxml_main.set('voiceStealing', self.voiceStealing)
		for _, d in self.pads.items(): d.write(bxml_main)
		for x in self.soundlayers: x.write(bxml_main)
		for i, v in self.soundparameters.items():
			bxml_param = bxml_main.add_child('SOUNDPARAMETER')
			bxml_param.set('id', i)
			if v is not None: bxml_param.set('value', v)

# ==================================== SAMPLER ====================================

class prosampler:
	def __init__(self):
		self.version = 2
		self.fxOrder1 = 'reverb,delay,comp,filter,eq,dist,chorus'
		self.fxOrder2 = 'delay,reverb,comp,filter,eq,dist,chorus'
		self.currentPage = 0
		self.showScratchPad = False
		self.soundparameters = {}
		self.mpe = False
		self.voiceStealing = False
		self.mono = False
		self.playMode = 0
		self.soundlayers = []
		self.pads = {}

	def add_layer(self):
		soundlayer_obj = sampler_soundlayer()
		self.soundlayers.append(soundlayer_obj)
		return soundlayer_obj

	def add_pad(self, key):
		pad_obj = sampler_pad()
		pad_obj.note = key
		self.pads[key] = pad_obj
		return pad_obj

	def read(self, bxml):
		attrib = bxml.attrib
		if 'version' in attrib: self.version = int(attrib['version'])
		if 'fxOrder1' in attrib: self.fxOrder1 = str(attrib['fxOrder1'])
		if 'fxOrder2' in attrib: self.fxOrder2 = str(attrib['fxOrder2'])
		if 'currentPage' in attrib: self.currentPage = int(attrib['currentPage'])
		if 'showScratchPad' in attrib: self.showScratchPad = bool(attrib['showScratchPad'])
		if 'mpe' in attrib: self.mpe = bool(attrib['mpe'])
		if 'voiceStealing' in attrib: self.voiceStealing = bool(attrib['voiceStealing'])
		if 'mono' in attrib: self.mono = bool(attrib['mono'])
		if 'playMode' in attrib: self.playMode = int(attrib['playMode'])
		for x in bxml:
			if x.tag == "SOUNDPARAMETER": 
				attrib = x.attrib
				if 'id' in attrib:
					self.soundparameters[str(attrib['id'])] = float(attrib['value']) if 'value' in attrib else None
			elif x.tag == "SOUNDLAYER": 
				soundlayer_obj = sampler_soundlayer()
				soundlayer_obj.read(x)
				self.soundlayers.append(soundlayer_obj)
			elif x.tag == "PAD": 
				pad_obj = sampler_pad()
				pad_obj.read(x)
				self.pads[pad_obj.note] = pad_obj

	def write(self, bxml_data):
		bxml_main = bxml_data.add_child('SAMPLER')
		bxml_main.set('version', self.version)
		if self.fxOrder1 is not None: bxml_main.set('fxOrder1', self.fxOrder1)
		if self.fxOrder2 is not None: bxml_main.set('fxOrder2', self.fxOrder2)
		if self.currentPage is not None: bxml_main.set('currentPage', self.currentPage)
		if self.showScratchPad == True: bxml_main.set('showScratchPad', self.showScratchPad)
		if self.playMode: bxml_main.set('playMode', self.playMode)
		if self.mpe == True: bxml_main.set('mpe', self.mpe)
		if self.voiceStealing == True: bxml_main.set('voiceStealing', self.voiceStealing)
		if self.mono == True: bxml_main.set('mono', self.mono)
		for i, v in self.soundparameters.items():
			bxml_param = bxml_main.add_child('SOUNDPARAMETER')
			bxml_param.set('id', i)
			if v is not None: bxml_param.set('value', v)
		for _, d in self.pads.items(): d.write(bxml_main)
		for x in self.soundlayers: x.write(bxml_main)

# ==================================== MAIN ====================================

class sampler_program:
	def __init__(self):
		self.presetDirty = None
		self.presetName = None
		self.width = None
		self.height = None
		self.programdata = None

	def read(self, bxml):
		attrib = bxml.attrib
		if 'presetDirty' in attrib: self.presetDirty = bool(attrib['presetDirty'])
		if 'presetName' in attrib: self.presetName = str(attrib['presetName'])
		if 'width' in attrib: self.width = int(attrib['width'])
		if 'height' in attrib: self.height = int(attrib['height'])
		for x in bxml:
			if x.tag == "TINYSAMPLER": 
				progdata = tinysampler()
				progdata.read(x)
				self.programdata = progdata
			if x.tag == "MICROSAMPLER": 
				progdata = microsampler()
				progdata.read(x)
				self.programdata = progdata
			if x.tag == "SAMPLER": 
				progdata = prosampler()
				progdata.read(x)
				self.programdata = progdata

	def write(self, bxml_data):
		if self.presetDirty is not None: bxml_data.set('presetDirty', self.presetDirty)
		if self.presetName is not None: bxml_data.set('presetName', self.presetName)
		if self.width is not None: bxml_data.set('width', self.width)
		if self.height is not None: bxml_data.set('height', self.height)
		if isinstance(self.programdata, tinysampler): self.programdata.write(bxml_data)
		if isinstance(self.programdata, microsampler): self.programdata.write(bxml_data)
		if isinstance(self.programdata, prosampler): self.programdata.write(bxml_data)

class waveform_sampler_main:
	def __init__(self):
		self.program = sampler_program()

	def set_tinysampler(self):
		programdata = self.program.programdata = tinysampler()
		return programdata

	def set_microsampler(self):
		programdata = self.program.programdata = microsampler()
		return programdata

	def set_prosampler(self):
		programdata = self.program.programdata = prosampler()
		return programdata

	def read(self, bstate):
		bxml_data = juce_binaryxml.juce_binaryxml_element()
		bxml_data.read_bytes(bstate)
		bxml_data.output_file('sampler_input.xml')
		if bxml_data.tag == 'PROGRAM': self.program.read(bxml_data)

	def write(self):
		bxml_data = juce_binaryxml.juce_binaryxml_element()
		bxml_data.tag = 'PROGRAM'
		self.program.write(bxml_data)
		bxml_data.output_file('sampler_output.xml')
		return bxml_data.to_bytes()