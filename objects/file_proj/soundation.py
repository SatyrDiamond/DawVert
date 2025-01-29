# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class soundation_param:
	def __init__(self, pd):
		self.value = 0
		self.automation = []
		self.has_auto = False

		if pd != None:
			if 'value' in pd: self.value = pd['value']
			if 'automation' in pd: 
				self.automation = pd['automation']
				self.has_auto = True

class soundation_paramset:
	def __init__(self):
		self.data = {}

	def add(self, name, value, automation):
		param_obj = soundation_param(None)
		param_obj.value = value
		param_obj.automation = automation
		param_obj.has_auto = True
		param_obj.exists = True
		self.data[name] = param_obj

	def add_from_sng(self, name, dictin):
		param_obj = soundation_param(dictin)
		self.data[name] = param_obj

	def get(self, name):
		if name in self.data:
			return self.data[name]
		else:
			param_obj = soundation_param(None)
			param_obj.value = 0
			param_obj.automation = []
			return param_obj

	def write(self, dictin):
		for n, x in self.data.items():
			param_data = {}
			param_data['value'] = x.value
			if x.has_auto: param_data['automation'] = x.automation
			dictin[n] = param_data

class soundation_device:
	def __init__(self, pd):
		self.rackName = None
		self.identifier = None
		self.bypass = None
		self.params = soundation_paramset()
		self.data = {}

		if pd != None:
			for n, v in pd.items():
				if n == 'bypass': self.bypass = v
				elif n == 'rackName': self.rackName = v
				elif n == 'identifier': self.identifier = v
				else: 
					if isinstance(v, dict) and 'value' in v: 
						self.params.add_from_sng(n, v)
					else: 
						self.data[n] = v

	def write(self):
		sng_device = {}
		if self.rackName != None: sng_device['rackName'] = self.rackName
		sng_device['identifier'] = self.identifier
		if self.bypass != None: sng_device['bypass'] = self.bypass
		self.params.write(sng_device)
		for name, param in self.data.items(): sng_device[name] = param
		return sng_device

class soundation_region:
	def __init__(self, pd):
		self.color = None
		self.position = 0
		self.autoStretchBpm = None
		self.contentPosition = 0
		self.file = None
		self.isAutoStretched = None
		self.isPattern = None
		self.length = 0
		self.loopcount = None
		self.muted = False
		self.name = ''
		self.notes = None
		self.reversed = None
		self.stretchMode = None
		self.stretchRate = None
		self.type = None

		if pd != None:
			if 'color' in pd: self.color = pd['color']
			if 'position' in pd: self.position = pd['position']
			if 'autoStretchBpm' in pd: self.autoStretchBpm = pd['autoStretchBpm']
			if 'contentPosition' in pd: self.contentPosition = pd['contentPosition']
			if 'file' in pd: self.file = pd['file']
			if 'isAutoStretched' in pd: self.isAutoStretched = pd['isAutoStretched']
			if 'isPattern' in pd: self.isPattern = pd['isPattern']
			if 'length' in pd: self.length = pd['length']
			if 'loopcount' in pd: self.loopcount = pd['loopcount']
			if 'muted' in pd: self.muted = pd['muted']
			if 'name' in pd: self.name = pd['name']
			if 'notes' in pd: self.notes = pd['notes']
			if 'reversed' in pd: self.reversed = pd['reversed']
			if 'stretchMode' in pd: self.stretchMode = pd['stretchMode']
			if 'stretchRate' in pd: self.stretchRate = pd['stretchRate']
			if 'type' in pd: self.type = pd['type']

	def write(self):
		sng_region = {}
		if self.color != None: sng_region['color'] = self.color
		sng_region['position'] = self.position
		sng_region['length'] = self.length
		if self.loopcount != None: sng_region['loopcount'] = self.loopcount
		sng_region['contentPosition'] = self.contentPosition
		sng_region['muted'] = self.muted
		sng_region['name'] = self.name
		if self.type != None: sng_region['type'] = self.type
		if self.type == 1: sng_region['autoStretchBpm'] = self.autoStretchBpm
		if self.isAutoStretched != None: sng_region['isAutoStretched'] = self.isAutoStretched
		if self.file != None: sng_region['file'] = self.file
		if self.notes != None: sng_region['notes'] = self.notes
		if self.reversed != None: sng_region['reversed'] = self.reversed
		if self.stretchMode != None: sng_region['stretchMode'] = self.stretchMode
		if self.stretchRate != None: sng_region['stretchRate'] = self.stretchRate
		if self.isPattern != None: sng_region['isPattern'] = self.isPattern
		return sng_region

class soundation_channel:
	def __init__(self, pd):
		self.name = ''
		self.type = ''
		self.mute = False
		self.solo = False
		self.volume = 1
		self.pan = 0.5
		self.color = None
		self.volumeAutomation = []
		self.panAutomation = []
		self.effects = []
		self.regions = []
		self.instrument = None
		self.userSetName = None

		if pd != None:
			if 'name' in pd: self.name = pd['name']
			if 'type' in pd: self.type = pd['type']
			if 'color' in pd: self.color = pd['color']
			if 'mute' in pd: self.mute = pd['mute']
			if 'solo' in pd: self.solo = pd['solo']
			if 'volume' in pd: self.volume = pd['volume']
			if 'pan' in pd: self.pan = pd['pan']
			if 'volumeAutomation' in pd: self.volumeAutomation = pd['volumeAutomation']
			if 'panAutomation' in pd: self.panAutomation = pd['panAutomation']
			if 'effects' in pd: self.effects = [soundation_device(x) for x in pd['effects']]
			if 'instrument' in pd: self.instrument = soundation_device(pd['instrument'])
			if 'userSetName' in pd: self.userSetName = pd['userSetName']
			if 'regions' in pd: self.regions = [soundation_region(x) for x in pd['regions']]


	def write(self):
		sng_channel = {}
		sng_channel['name'] = self.name
		sng_channel['type'] = self.type
		if self.color: sng_channel['color'] = self.color
		sng_channel['mute'] = self.mute
		sng_channel['solo'] = self.solo
		sng_channel['volume'] = self.volume
		sng_channel['pan'] = self.pan
		sng_channel['volumeAutomation'] = self.volumeAutomation
		sng_channel['panAutomation'] = self.panAutomation
		sng_channel['effects'] = [x.write() for x in self.effects]
		if self.instrument: sng_channel['instrument'] = self.instrument.write()
		if self.userSetName != None: sng_channel['userSetName'] = self.userSetName
		sng_channel['regions'] = [x.write() for x in self.regions]
		return sng_channel

class soundation_project:
	def __init__(self, pd):
		self.version = 2.3
		self.studio = "3.124.5"
		self.bpm = 120
		self.timeSignature = "4/4"
		self.looping = False
		self.loopStart = 0
		self.loopEnd = 4102
		self.channels = []

		if pd != None:
			if 'version' in pd: self.version = pd['version']
			if 'studio' in pd: self.studio = pd['studio']
			if 'bpm' in pd: self.bpm = pd['bpm']
			if 'timeSignature' in pd: self.timeSignature = pd['timeSignature']
			if 'looping' in pd: self.looping = pd['looping']
			if 'loopStart' in pd: self.loopStart = pd['loopStart']
			if 'loopEnd' in pd: self.loopEnd = pd['loopEnd']
			if 'channels' in pd: 
				for channel in pd['channels']:
					self.channels.append(soundation_channel(channel))

	def write(self):
		sng_proj = {}
		sng_proj['version'] = self.version
		sng_proj['studio'] = self.studio
		sng_proj['bpm'] = self.bpm
		sng_proj['timeSignature'] = self.timeSignature
		sng_proj['looping'] = self.looping
		sng_proj['loopStart'] = self.loopStart
		sng_proj['loopEnd'] = self.loopEnd
		sng_proj['channels'] = [x.write() for x in self.channels]
		return sng_proj