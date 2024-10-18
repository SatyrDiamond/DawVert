# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from lxml import etree

class jummbox_filter:
	def __init__(self, pd, starttxt):
		self.Filter = []
		self.FilterType = False
		self.SimpleCut = 10
		self.SimplePeak = 0
		self.SubFilters0 = []
		if pd and starttxt:
			if starttxt+'Filter' in pd: self.Filter = pd[starttxt+'Filter']
			if starttxt+'FilterType' in pd: self.FilterType = pd[starttxt+'FilterType']
			if starttxt+'SimpleCut' in pd: self.SimpleCut = pd[starttxt+'SimpleCut']
			if starttxt+'SimplePeak' in pd: self.SimplePeak = pd[starttxt+'SimplePeak']
			if starttxt+'SubFilters0' in pd: self.SubFilters0 = pd[starttxt+'SubFilters0']

	def write(self, pd, starttxt):
		pd[starttxt+'Filter'] = self.Filter
		pd[starttxt+'FilterType'] = self.FilterType
		pd[starttxt+'SimpleCut'] = self.SimpleCut
		pd[starttxt+'SimplePeak'] = self.SimplePeak
		pd[starttxt+'SubFilters0'] = self.SubFilters0

class jummbox_instrument_effects:
	def __init__(self):
		self.used = []

		self.pan = 0
		self.panDelay = 10

		self.transition = 'interrupt'
		self.clicklessTransition = False

		self.chord = 'arpeggio'
		self.fastTwoNoteArp = True
		self.arpeggioSpeed = 1

		self.chorus = 100

		self.reverb = 100

		self.echoSustain = 0
		self.echoDelayBeats = 0

		self.distortion = 0

		self.vibrato = 'light'
		self.vibratoDepth = 0.15
		self.vibratoDelay = 0
		self.vibratoSpeed = 10
		self.vibratoType = 0

		self.notefilter = jummbox_filter(None, None)

		self.bitcrusherQuantization = 14
		self.bitcrusherOctave = 8

		self.pitchShiftSemitones = 0

		self.detuneCents = 0

	def write(self, pd):
		pd['effects'] = self.used

		if 'transition type' in self.used:
			pd['transition'] = self.transition
			pd['clicklessTransition'] = self.clicklessTransition
	
		if 'chord type' in self.used:
			pd['chord'] = self.chord
			pd['fastTwoNoteArp'] = self.fastTwoNoteArp
			pd['arpeggioSpeed'] = self.arpeggioSpeed
	
		if 'note filter' in self.used:
			self.notefilter.write(pd, 'note')
	
		if 'pitch shift' in self.used:
			pd['pitchShiftSemitones'] = self.pitchShiftSemitones
	
		if 'detune' in self.used:
			pd['detuneCents'] = self.detuneCents

		if 'vibrato' in self.used:
			pd['vibrato'] = self.vibrato
			pd['vibratoDepth'] = self.vibratoDepth
			pd['vibratoDelay'] = self.vibratoDelay
			pd['vibratoSpeed'] = self.vibratoSpeed
			pd['vibratoType'] = self.vibratoType
	
		if 'distortion' in self.used:
			pd['distortion'] = self.distortion
	
		if 'bitcrusher' in self.used:
			pd['bitcrusherOctave'] = self.bitcrusherOctave
			pd['bitcrusherQuantization'] = self.bitcrusherQuantization
	
		if 'panning' in self.used:
			pd['pan'] = self.pan
			pd['panDelay'] = self.panDelay
	
		if 'chorus' in self.used:
			pd['chorus'] = self.chorus
	
		if 'echo' in self.used:
			pd['echoSustain'] = self.echoSustain
			pd['echoDelayBeats'] = self.echoDelayBeats
	
		if 'reverb' in self.used:
			pd['reverb'] = self.reverb
	
class jummbox_instrument:
	def __init__(self, pd):
		self.type = 'pitch'
		self.preset = None
		self.volume = 0
		self.fadeInSeconds = 0
		self.fadeOutTicks = -1
		self.filter = jummbox_filter(pd, 'eq')
		self.envelopes = []
		self.data = {}
		self.fx = jummbox_instrument_effects()
		self.envelopeSpeed = 12
		self.discreteEnvelope = False
		self.envelopes = []
		self.modChannels = [-1, -1, -1, -1, -1, -1]
		self.modInstruments = [0, 0, 0, 0, 0, 0]
		self.modSettings = [0, 0, 0, 0, 0, 0]
		self.modFilterTypes = [0, 0, 0, 0, 0, 0]
		self.modStatuses = []
		self.drums = {}

		if pd != None:
			self.filter = jummbox_filter(pd, 'eq')
			fx_obj = self.fx
			fx_obj.notefilter = jummbox_filter(pd, 'note')
			for n, v in pd.items():
				if n == 'type': self.type = v
				elif n == 'preset': self.preset = v
				elif n == 'volume': self.volume = v
				elif n == 'envelopeSpeed': self.envelopeSpeed = v
				elif n == 'discreteEnvelope': self.discreteEnvelope = v
				elif n == 'drums': self.drums = v
				elif n == 'modChannels': self.modChannels = v
				elif n == 'modInstruments': self.modInstruments = v
				elif n == 'modSettings': self.modSettings = v
				elif n == 'modStatuses': self.modStatuses = v
				elif n == 'modFilterTypes': self.modFilterTypes = v
				elif n == 'octaveScrollBar': self.octaveScrollBar = v
				elif n == 'fadeInSeconds': self.fadeInSeconds = v
				elif n == 'fadeOutTicks': self.fadeOutTicks = v
				elif n == 'effects': fx_obj.used = v
				elif n == 'transition': fx_obj.transition = v
				elif n == 'clicklessTransition': fx_obj.clicklessTransition = v
				elif n == 'pan': fx_obj.pan = v
				elif n == 'panDelay': fx_obj.panDelay = v
				elif n == 'chord': fx_obj.chord = v
				elif n == 'fastTwoNoteArp': fx_obj.fastTwoNoteArp = v
				elif n == 'arpeggioSpeed': fx_obj.arpeggioSpeed = v
				elif n == 'chorus': fx_obj.chorus = v
				elif n == 'reverb': fx_obj.reverb = v
				elif n == 'distortion': fx_obj.distortion = v
				elif n == 'echoSustain': fx_obj.echoSustain = v
				elif n == 'echoDelayBeats': fx_obj.echoDelayBeats = v
				elif n == 'bitcrusherQuantization': fx_obj.bitcrusherQuantization = v
				elif n == 'bitcrusherOctave': fx_obj.bitcrusherOctave = v
				elif n == 'vibrato': fx_obj.vibrato = v
				elif n == 'vibratoDepth': fx_obj.vibratoDepth = v
				elif n == 'vibratoDelay': fx_obj.vibratoDelay = v
				elif n == 'vibratoSpeed': fx_obj.vibratoSpeed = v
				elif n == 'vibratoType': fx_obj.vibratoType = v
				elif n == 'pitchShiftSemitones': fx_obj.pitchShiftSemitones = v
				elif n == 'detuneCents': fx_obj.detuneCents = v
				elif n == 'envelopes': self.envelopes = v
				elif n in ['eqFilter','eqFilterType','eqSimpleCut','eqSimplePeak','noteFilter','noteFilterType','noteSimpleCut','noteSimplePeak']: pass
				elif n.startswith('eqSubFilters') or n.startswith('noteSubFilters'): pass
				else: self.data[n] = v

	def write(self, b_format, b_version):
		jummbox_inst = {}
		jummbox_inst['type'] = self.type
		jummbox_inst['volume'] = self.volume
		self.filter.write(jummbox_inst, 'eq')
		if b_format == 'UltraBox': jummbox_inst['envelopeSpeed'] = self.envelopeSpeed
		if b_format == 'UltraBox': jummbox_inst['discreteEnvelope'] = self.discreteEnvelope
		if self.preset != None: jummbox_inst['preset'] = self.preset
		self.fx.write(jummbox_inst)
		jummbox_inst['volume'] = self.volume
		if self.type == 'drumset': 
			jummbox_inst['drums'] = self.drums
		else:
			jummbox_inst['fadeInSeconds'] = self.fadeInSeconds
			jummbox_inst['fadeOutTicks'] = self.fadeOutTicks
		for n, v in self.data.items(): jummbox_inst[n] = v
		if self.type == 'mod':
			jummbox_inst['modChannels'] = self.modChannels
			jummbox_inst['modInstruments'] = self.modInstruments
			jummbox_inst['modSettings'] = self.modSettings
			if b_format == 'UltraBox': jummbox_inst['modFilterTypes'] = self.modFilterTypes
			else: jummbox_inst['modStatuses'] = self.modStatuses
		jummbox_inst['envelopes'] = self.envelopes

		return jummbox_inst

class jummbox_note:
	__slots__ = ['pitches','points','continuesLastPattern']
	def __init__(self, pd):
		self.pitches = []
		self.points = []
		self.continuesLastPattern = None
		if pd:
			self.pitches = pd['pitches']
			self.points = [[x['tick'],x['pitchBend'],x['volume'],x['forMod']] for x in pd['points']]
			if 'continuesLastPattern' in pd: self.continuesLastPattern = pd['continuesLastPattern']

	def write(self):
		pat = {}
		pat['pitches'] = self.pitches
		pat['points'] = [{'tick': x[0],'pitchBend': x[1],'volume': x[2],'forMod': x[3]} for x in self.points]
		if self.continuesLastPattern != None: pat['continuesLastPattern'] = self.continuesLastPattern
		return pat


class jummbox_pattern:
	def __init__(self, pd):
		self.notes = []
		if pd:
			if 'notes' in pd: self.notes = [jummbox_note(x) for x in pd['notes']]

	def write(self):
		return {'notes': [x.write() for x in self.notes]}

class jummbox_channel:
	def __init__(self, pd):
		self.type = "pitch"
		self.name = ''
		self.instruments = []
		self.patterns = []
		self.sequence = []
		self.octaveScrollBar = 4
		if pd != None:
			if 'type' in pd: self.type = pd['type']
			if 'name' in pd: self.name = pd['name']
			if 'instruments' in pd: self.instruments = [jummbox_instrument(x) for x in pd['instruments']]
			if 'patterns' in pd: self.patterns = [jummbox_pattern(x) for x in pd['patterns']]
			if 'sequence' in pd: self.sequence = pd['sequence']
			if 'octaveScrollBar' in pd: self.octaveScrollBar = pd['octaveScrollBar']

	def write(self, b_format, b_version):
		jummbox_chan = {}
		jummbox_chan['type'] = self.type
		jummbox_chan['name'] = self.name
		jummbox_chan['instruments'] = [x.write(b_format, b_version) for x in self.instruments]
		jummbox_chan['patterns'] = [x.write() for x in self.patterns]
		jummbox_chan['sequence'] = self.sequence
		if self.type != 'drum': jummbox_chan['octaveScrollBar'] = self.octaveScrollBar
		return jummbox_chan


class jummbox_project:
	def __init__(self, pd):
		self.name = ""
		self.format = "BeepBox"
		self.version = 5
		self.scale = "Free"
		self.customScale = [True,False,False,False,False,False,False,False,False,False,False,False]
		self.keyOctave = 0
		self.key = "C"
		self.introBars = 0
		self.loopBars = 4
		self.beatsPerBar = 8
		self.ticksPerBeat = 4
		self.beatsPerMinute = 150
		self.reverb = 0
		self.masterGain = 1
		self.compressionThreshold = 1
		self.limitThreshold = 1
		self.limitDecay = 4
		self.limitRise = 4000
		self.limitRatio = 1
		self.compressionRatio = 1
		self.layeredInstruments = False
		self.patternInstruments = False
		self.channels = []

		if pd != None:
			if 'name' in pd: self.name = pd['name']
			if 'format' in pd: self.format = pd['format']
			if 'version' in pd: self.version = pd['version']
			if 'scale' in pd: self.scale = pd['scale']
			if 'key' in pd: self.key = pd['key']
			if 'keyOctave' in pd: self.keyOctave = pd['keyOctave']
			if 'customScale' in pd: self.customScale = pd['customScale']
			if 'introBars' in pd: self.introBars = pd['introBars']
			if 'loopBars' in pd: self.loopBars = pd['loopBars']
			if 'beatsPerBar' in pd: self.beatsPerBar = pd['beatsPerBar']
			if 'ticksPerBeat' in pd: self.ticksPerBeat = pd['ticksPerBeat']
			if 'beatsPerMinute' in pd: self.beatsPerMinute = pd['beatsPerMinute']
			if 'reverb' in pd: self.reverb = pd['reverb']
			if 'masterGain' in pd: self.masterGain = pd['masterGain']
			if 'compressionThreshold' in pd: self.compressionThreshold = pd['compressionThreshold']
			if 'limitThreshold' in pd: self.limitThreshold = pd['limitThreshold']
			if 'limitDecay' in pd: self.limitDecay = pd['limitDecay']
			if 'limitRise' in pd: self.limitRise = pd['limitRise']
			if 'limitRatio' in pd: self.limitRatio = pd['limitRatio']
			if 'compressionRatio' in pd: self.compressionRatio = pd['compressionRatio']
			if 'layeredInstruments' in pd: self.layeredInstruments = pd['layeredInstruments']
			if 'patternInstruments' in pd: self.patternInstruments = pd['patternInstruments']
			if 'channels' in pd: self.channels = [jummbox_channel(x) for x in pd['channels']]

	def get_durpos(self):
		autodur = {}
		sequencelen = [self.beatsPerBar*self.ticksPerBeat for _ in range(len(self.channels[0].sequence))]
		for channel in self.channels:
			if channel.type == 'mod':
				nextbarfound = None
				modinst = channel.instruments[0]
				for num in range(6):
					autodef = [modinst.modChannels[num],modinst.modInstruments[num],modinst.modSettings[num]]
					if autodef == [-1, 0, 4]:
						nextbarfound = num
						break

				if nextbarfound != None:
					for n, p in enumerate(channel.patterns):
						for a in p.notes:
							if a.pitches[0] == 5-num: autodur[n+1] = a.points[0][0]

					for n, p in enumerate(channel.sequence):
						if p in autodur: sequencelen[n] = autodur[p]

		return sequencelen

	def write(self):
		jummbox_proj = {}
		jummbox_proj['name'] = self.name
		jummbox_proj['format'] = self.format
		jummbox_proj['version'] = self.version
		jummbox_proj['scale'] = self.scale
		if self.format == 'UltraBox': jummbox_proj['customScale'] = self.customScale
		jummbox_proj['key'] = self.key
		if self.format == 'UltraBox': jummbox_proj['keyOctave'] = self.keyOctave
		jummbox_proj['introBars'] = self.introBars
		jummbox_proj['loopBars'] = self.loopBars
		jummbox_proj['beatsPerBar'] = self.beatsPerBar
		jummbox_proj['ticksPerBeat'] = self.ticksPerBeat
		jummbox_proj['beatsPerMinute'] = self.beatsPerMinute
		jummbox_proj['reverb'] = self.reverb
		jummbox_proj['masterGain'] = self.masterGain
		jummbox_proj['compressionThreshold'] = self.compressionThreshold
		jummbox_proj['limitThreshold'] = self.limitThreshold
		jummbox_proj['limitDecay'] = self.limitDecay
		jummbox_proj['limitRise'] = self.limitRise
		jummbox_proj['limitRatio'] = self.limitRatio
		jummbox_proj['compressionRatio'] = self.compressionRatio
		jummbox_proj['layeredInstruments'] = self.layeredInstruments
		jummbox_proj['patternInstruments'] = self.patternInstruments
		jummbox_proj['channels'] = [x.write(self.format, self.version) for x in self.channels]
		return jummbox_proj