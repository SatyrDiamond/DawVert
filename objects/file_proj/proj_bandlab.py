# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

# --------------------------------------------------------- AUTOMATION ---------------------------------------------------------

class bandlab_autopoint:
	def __init__(self, indata):
		self.position = 0
		self.value = 0
		if indata: self.read(indata)

	def read(self, indata):
		if 'position' in indata: self.position = indata['position']
		if 'value' in indata: self.value = indata['value']

	def write(self):
		return {'position': self.position, 'value': self.value}

class bandlab_automation:
	def __init__(self):
		self.points = []

	def read(self, indata):
		self.points = [bandlab_autopoint(x) for x in indata]

	def add_point(self, position, value):
		point = bandlab_autopoint(None)
		point.position = position
		point.value = value
		self.points.append(point)

	def write(self):
		return [x.write() for x in self.points]

class bandlab_track_automation:
	def __init__(self, indata):
		self.id = None
		self.pan = bandlab_automation()
		self.volume = bandlab_automation()
		if indata: self.read(indata)

	def read(self, indata):
		if 'id' in indata: self.id = indata['id']
		if 'pan' in indata: self.pan.read(indata['pan'])
		if 'volume' in indata: self.volume.read(indata['volume'])

	def write(self):
		outdata = {}
		if self.id != None: outdata['id'] = self.id
		outdata['pan'] = self.pan.write()
		outdata['volume'] = self.volume.write()
		return outdata

# --------------------------------------------------------- DEVICES ---------------------------------------------------------

class bandlab_effect:
	def __init__(self, indata):
		self.automation = {}
		self.bypass = False
		self.params = {}
		self.slug = ''
		if indata: self.read(indata)

	def read(self, indata):
		if 'automation' in indata: 
			for n, a in indata['automation'].items():
				auto_obj = bandlab_automation()
				auto_obj.read(a)
				self.automation[n] = auto_obj
		if 'bypass' in indata: self.bypass = indata['bypass']
		if 'params' in indata: self.params = indata['params']
		if 'slug' in indata: self.slug = indata['slug']

	def write(self):
		outdata = {}
		automation = outdata['automation'] = {}
		for n, a in self.automation.items(): automation[n] = a.write()
		outdata['bypass'] = self.bypass
		outdata['params'] = self.params
		outdata['slug'] = self.slug
		return outdata

class bandlab_autoPitch:
	def __init__(self, indata):
		self.algorithm = "original"
		self.bypass = True
		self.mix = 1.0
		self.responseTime = 0.0
		self.scale = "scale_chromatic"
		self.slug = ""
		self.targetNotes = []
		self.tonic = "tonic_C"
		self.version = "0.2"
		if indata: self.read(indata)

	def read(self, indata):
		if 'algorithm' in indata: self.algorithm = indata['algorithm']
		if 'bypass' in indata: self.bypass = indata['bypass']
		if 'mix' in indata: self.mix = indata['mix']
		if 'responseTime' in indata: self.responseTime = indata['responseTime']
		if 'scale' in indata: self.scale = indata['scale']
		if 'slug' in indata: self.slug = indata['slug']
		if 'targetNotes' in indata: self.targetNotes = indata['targetNotes']
		if 'tonic' in indata: self.tonic = indata['tonic']
		if 'version' in indata: self.version = indata['version']

	def write(self):
		outdata = {}
		outdata['algorithm'] = self.algorithm
		outdata['bypass'] = self.bypass
		outdata['mix'] = self.mix
		outdata['responseTime'] = self.responseTime
		outdata['scale'] = self.scale
		outdata['slug'] = self.slug
		outdata['targetNotes'] = self.targetNotes
		outdata['tonic'] = self.tonic
		outdata['version'] = self.version
		return outdata

# --------------------------------------------------------- CLIP ---------------------------------------------------------

class bandlab_region:
	def __init__(self, indata):
		self.endPosition = 0
		self.fadeIn = 0.0
		self.fadeOut = 0.0
		self.gain = 1.0
		self.id = ""
		self.key = None
		self.loopLength = 0.0
		self.name = ""
		self.pitchShift = 0.0
		self.playbackRate = 1.0
		self.sampleId = ""
		self.sampleOffset = 0.0
		self.sampleStartPosition = 0.0
		self.startPosition = 0.0
		self.trackId = ""
		self.file = ""
		self.post = {}
		if indata: self.read(indata)

	def read(self, indata):
		if 'endPosition' in indata: self.endPosition = indata['endPosition']
		if 'fadeIn' in indata: self.fadeIn = indata['fadeIn']
		if 'fadeOut' in indata: self.fadeOut = indata['fadeOut']
		if 'gain' in indata: self.gain = indata['gain']
		if 'id' in indata: self.id = indata['id']
		if 'key' in indata: self.key = indata['key']
		if 'loopLength' in indata: self.loopLength = indata['loopLength']
		if 'name' in indata: self.name = indata['name']
		if 'pitchShift' in indata: self.pitchShift = indata['pitchShift']
		if 'playbackRate' in indata: self.playbackRate = indata['playbackRate']
		if 'sampleId' in indata: self.sampleId = indata['sampleId']
		if 'sampleOffset' in indata: self.sampleOffset = indata['sampleOffset']
		if 'sampleStartPosition' in indata: self.sampleStartPosition = indata['sampleStartPosition']
		if 'startPosition' in indata: self.startPosition = indata['startPosition']
		if 'trackId' in indata: self.trackId = indata['trackId']
		if 'file' in indata: self.file = indata['file']

	def write(self):
		outdata = {}
		outdata['endPosition'] = self.endPosition
		outdata['fadeIn'] = self.fadeIn
		outdata['fadeOut'] = self.fadeOut
		outdata['gain'] = self.gain
		outdata['id'] = self.id
		outdata['key'] = self.key
		outdata['loopLength'] = self.loopLength
		outdata['name'] = self.name
		outdata['pitchShift'] = self.pitchShift
		outdata['playbackRate'] = self.playbackRate
		outdata['sampleId'] = self.sampleId
		outdata['sampleOffset'] = self.sampleOffset
		outdata['sampleStartPosition'] = self.sampleStartPosition
		outdata['startPosition'] = self.startPosition
		outdata['trackId'] = self.trackId
		if self.file: outdata['file'] = self.file
		return outdata

class bandlab_pattern:
	def __init__(self, indata):
		self.notes = []
		self.sampleId = ''
		if indata: self.read(indata)

	def read(self, indata):
		if 'notes' in indata: self.notes = indata['notes']
		if 'sampleId' in indata: self.sampleId = indata['sampleId']

	def write(self):
		outdata = {}
		outdata['notes'] = self.notes
		outdata['sampleId'] = self.sampleId
		return outdata

# --------------------------------------------------------- TRACK ---------------------------------------------------------

class bandlab_auxChannel:
	def __init__(self, indata):
		self.effects = None
		self.id = ''
		self.preset = 'sharedReverb'
		self.returnLevel = 1.0
		if indata: self.read(indata)

	def read(self, indata):
		if 'effects' in indata: self.effects = indata['effects']
		if 'id' in indata: self.id = indata['id']
		if 'preset' in indata: self.preset = indata['preset']
		if 'returnLevel' in indata: self.returnLevel = indata['returnLevel']

	def write(self):
		outdata = {}
		outdata['effects'] = self.effects
		outdata['id'] = self.id
		outdata['preset'] = self.preset
		outdata['returnLevel'] = self.returnLevel
		return outdata

class bandlab_auxSend:
	def __init__(self, indata):
		self.automation = bandlab_automation()
		self.id = ''
		self.sendLevel = 0.0
		if indata: self.read(indata)

	def read(self, indata):
		if 'automation' in indata: self.automation.read(indata['automation'])
		if 'id' in indata: self.id = indata['id']
		if 'sendLevel' in indata: self.sendLevel = indata['sendLevel']

	def write(self):
		outdata = {}
		outdata['automation'] = self.automation.write()
		outdata['id'] = self.id
		outdata['sendLevel'] = self.sendLevel
		return outdata

class bandlab_track:
	def __init__(self, indata):
		self.automation = None
		self.autoPitch = None
		self.auxSends = []

		self.canEdit = True
		self.color = "#AECA59"
		self.colorName = "Green"

		self.effects = []
		self.effectsData = None

		self.id = ""
		self.inputEffect = 0
		self.isFrozen = False
		self.isMuted = False
		self.isSolo = False
		self.loopPack = None
		self.name = "speed"
		self.order = 0
		self.pan = 0.0
		self.patterns = None
		self.preset = "none"

		self.regions = []
		self.regionsMix = None

		self.revisionId = ""
		self.sampleId = ""
		self.samplerKit = None
		self.soundbank = None
		self.trackGroupId = None
		self.type = ""
		self.volume = 1.0
		self.assetFormat = ""

		if indata: self.read(indata)

	def read(self, indata):
		if 'automation' in indata: self.automation = bandlab_track_automation(indata['automation'])
		if 'autoPitch' in indata: 
			if indata['autoPitch']:
				self.autoPitch = bandlab_autoPitch(indata['autoPitch'])
		if 'auxSends' in indata: self.auxSends = [bandlab_auxSend(x) for x in indata['auxSends']]
		if 'canEdit' in indata: self.canEdit = indata['canEdit']
		if 'color' in indata: self.color = indata['color']
		if 'colorName' in indata: self.colorName = indata['colorName']

		if 'effects' in indata: self.effects = [bandlab_effect(x) for x in indata['effects']]
		if 'effectsData' in indata: self.effectsData = indata['effectsData']

		if 'id' in indata: self.id = indata['id']
		if 'inputEffect' in indata: self.inputEffect = indata['inputEffect']
		if 'isFrozen' in indata: self.isFrozen = indata['isFrozen']
		if 'isMuted' in indata: self.isMuted = indata['isMuted']
		if 'isSolo' in indata: self.isSolo = indata['isSolo']
		if 'loopPack' in indata: self.loopPack = indata['loopPack']
		if 'name' in indata: self.name = indata['name']
		if 'order' in indata: self.order = indata['order']
		if 'pan' in indata: self.pan = indata['pan']
		if 'patterns' in indata: self.patterns = [bandlab_pattern(x) for x in indata['patterns']] if indata['patterns'] else None
		if 'preset' in indata: self.preset = indata['preset']
		if 'regions' in indata: self.regions = [bandlab_region(x) for x in indata['regions']]
		if 'regionsMix' in indata: self.regionsMix = bandlab_region(indata['regionsMix'])

		if 'revisionId' in indata: self.revisionId = indata['revisionId']
		if 'sampleId' in indata: self.sampleId = indata['sampleId']
		if 'samplerKit' in indata: self.samplerKit = indata['samplerKit']
		if 'soundbank' in indata: self.soundbank = indata['soundbank']
		if 'trackGroupId' in indata: self.trackGroupId = indata['trackGroupId']
		if 'type' in indata: self.type = indata['type']
		if 'volume' in indata: self.volume = indata['volume']
		if 'assetFormat' in indata: self.assetFormat = indata['assetFormat']

	def write(self):
		outdata = {}
		if self.automation: outdata['automation'] = self.automation.write()
		outdata['autoPitch'] = self.autoPitch.write() if self.autoPitch else None
		outdata['auxSends'] = [x.write() for x in self.auxSends]
		outdata['canEdit'] = self.canEdit
		outdata['color'] = self.color
		outdata['colorName'] = self.colorName
		outdata['effects'] = [x.write() for x in self.effects] if self.effects != None else None
		outdata['effectsData'] = self.effectsData
		outdata['id'] = self.id
		outdata['inputEffect'] = self.inputEffect
		outdata['isFrozen'] = self.isFrozen
		outdata['isMuted'] = self.isMuted
		outdata['isSolo'] = self.isSolo
		outdata['loopPack'] = self.loopPack
		outdata['name'] = self.name
		outdata['order'] = self.order
		outdata['pan'] = self.pan
		outdata['patterns'] = [x.write() for x in self.patterns] if self.patterns != None else None
		outdata['preset'] = self.preset

		outdata['regions'] = [x.write() for x in self.regions]
		outdata['regionsMix'] = self.regionsMix.write() if self.regionsMix else None

		outdata['revisionId'] = self.revisionId
		outdata['sampleId'] = self.sampleId
		outdata['samplerKit'] = self.samplerKit
		outdata['soundbank'] = self.soundbank
		outdata['trackGroupId'] = self.trackGroupId
		outdata['type'] = self.type
		outdata['volume'] = self.volume
		if self.assetFormat: outdata['assetFormat'] = self.assetFormat

		return outdata

class bandlab_sample:
	def __init__(self, indata):
		self.creatorId = ""
		self.device = None
		self.duration = 0.0
		self.file = None
		self.id = ""
		self.isMidi = False
		self.name = "regions-mix"
		self.source = "BandLabWeb-10.1.135"
		self.status = "Empty"
		self.waveform = None
		if indata: self.read(indata)

	def read(self, indata):
		if 'creatorId' in indata: self.creatorId = indata['creatorId']
		if 'device' in indata: self.device = indata['device']
		if 'duration' in indata: self.duration = indata['duration']
		if 'file' in indata: self.file = indata['file']
		if 'id' in indata: self.id = indata['id']
		if 'isMidi' in indata: self.isMidi = indata['isMidi']
		if 'name' in indata: self.name = indata['name']
		if 'source' in indata: self.source = indata['source']
		if 'status' in indata: self.status = indata['status']
		if 'waveform' in indata: self.waveform = indata['waveform']

	def write(self):
		outdata = {}
		outdata['creatorId'] = self.creatorId
		outdata['device'] = self.device
		outdata['duration'] = self.duration
		outdata['file'] = self.file
		outdata['id'] = self.id
		outdata['isMidi'] = self.isMidi
		outdata['name'] = self.name
		outdata['source'] = self.source
		outdata['status'] = self.status
		outdata['waveform'] = self.waveform
		return outdata

class bandlab_samplerKits_sample:
	def __init__(self, indata):
		self.file = ''
		self.id = ''
		self.status = 'Ready'
		if indata: self.read(indata)

	def read(self, indata):
		if 'file' in indata: self.file = indata['file']
		if 'id' in indata: self.id = indata['id']
		if 'status' in indata: self.status = indata['status']

	def write(self):
		outdata = {}
		outdata['file'] = self.file
		outdata['id'] = self.id
		outdata['status'] = self.status
		return outdata

class bandlab_samplerKits:
	def __init__(self, indata):
		self.samples = []
		if indata: self.read(indata)

	def read(self, indata):
		self.samples = [bandlab_samplerKits_sample(x) for x in indata['samples']]

	def write(self):
		outdata = {}
		outdata['samples'] = [x.write() for x in self.samples]
		return outdata

class bandlab_project:
	def __init__(self):
		self.auxChannels = []
		self.samplerKits = None
		self.samples = []
		self.tracks = []

		self.canEdit = True
		self.canEditSettings = True
		self.canMaster = True
		self.canPublish = True
		self.clientId = "DawVert"
		self.createdOn = ''
		self.stamp = ''
		self.mixdown = None
		self.trackGroups = ''
		self.modifiedOn = ''
		self.parentId = ''
		self.place = None
		self.post = {}
		self.postId = ''

		self.counters = {}
		self.id = ''
		self.isFork = False
		self.isLiked = False
		self.isPublic = False
		self.key = None
		self.lyrics = None
		self.mastering = None
		self.metronome = {}
		self.song = {}

		self.creator = {}
		self.description = None
		self.genres = []

		self.volume = 1.0
		self.blxVersion = '1.0'

	def read(self, indata):
		if 'canEdit' in indata: self.canEdit = indata['canEdit']
		if 'canEditSettings' in indata: self.canEditSettings = indata['canEditSettings']
		if 'canMaster' in indata: self.canMaster = indata['canMaster']
		if 'canPublish' in indata: self.canPublish = indata['canPublish']
		if 'clientId' in indata: self.clientId = indata['clientId']
		if 'counters' in indata: self.counters = indata['counters']
		if 'createdOn' in indata: self.createdOn = indata['createdOn']
		if 'stamp' in indata: self.stamp = indata['stamp']
		if 'modifiedOn' in indata: self.modifiedOn = indata['modifiedOn']
		if 'parentId' in indata: self.parentId = indata['parentId']
		if 'place' in indata: self.place = indata['place']
		if 'trackGroups' in indata: self.trackGroups = indata['trackGroups']
		if 'volume' in indata: self.volume = indata['volume']
		if 'blxVersion' in indata: self.blxVersion = indata['blxVersion']
		if 'postId' in indata: self.postId = indata['postId']
		if 'post' in indata: self.post = indata['post']
		if 'mixdown' in indata: 
			self.mixdown = bandlab_sample(None)
			self.mixdown.read(indata['mixdown'])

		if 'id' in indata: self.id = indata['id']
		if 'isFork' in indata: self.isFork = indata['isFork']
		if 'isLiked' in indata: self.isLiked = indata['isLiked']
		if 'isPublic' in indata: self.isPublic = indata['isPublic']
		if 'key' in indata: self.key = indata['key']
		if 'lyrics' in indata: self.lyrics = indata['lyrics']
		if 'mastering' in indata: self.mastering = indata['mastering']
		if 'metronome' in indata: self.metronome = indata['metronome']
		if 'song' in indata: self.song = indata['song']

		if 'creator' in indata: self.creator = indata['creator']
		if 'description' in indata: self.description = indata['description']
		if 'genres' in indata: self.genres = indata['genres']

		self.auxChannels = [bandlab_auxChannel(x) for x in indata['auxChannels']]
		self.tracks = [bandlab_track(x) for x in indata['tracks']]
		self.samples = [bandlab_sample(x) for x in indata['samples']]
		self.samplerKits = bandlab_samplerKits(indata['samplerKits'])

	def load_from_file(self, input_file):
		f = open(input_file, 'rb')
		jsontxt = f.read().decode().split('\0')[0]
		projectdata = json.loads(jsontxt)
		self.read(projectdata)
		return True

	def write(self):
		outdata = {}
		outdata['auxChannels'] = [x.write() for x in self.auxChannels]
		outdata['canEdit'] = self.canEdit
		outdata['canEditSettings'] = self.canEditSettings
		outdata['canMaster'] = self.canMaster
		outdata['canPublish'] = self.canPublish
		outdata['clientId'] = self.clientId
		outdata['counters'] = self.counters
		outdata['createdOn'] = self.createdOn

		outdata['creator'] = self.creator
		outdata['description'] = self.description
		outdata['genres'] = self.genres

		outdata['id'] = self.id
		outdata['isFork'] = self.isFork
		outdata['isLiked'] = self.isLiked
		outdata['isPublic'] = self.isPublic
		outdata['key'] = self.key
		outdata['lyrics'] = self.lyrics
		outdata['mastering'] = self.mastering
		outdata['metronome'] = self.metronome

		outdata['mixdown'] = self.mixdown.write() if self.mixdown else {}
		outdata['modifiedOn'] = self.modifiedOn
		outdata['parentId'] = self.parentId
		outdata['place'] = self.place
		outdata['post'] = self.post
		outdata['postId'] = self.postId

		outdata['samplerKits'] = self.samplerKits.write() if self.samplerKits else {}
		outdata['samples'] = [x.write() for x in self.samples]
		outdata['song'] = self.song
		outdata['stamp'] = self.stamp
		outdata['trackGroups'] = self.trackGroups
		outdata['tracks'] = [x.write() for x in self.tracks]
		outdata['volume'] = self.volume
		outdata['blxVersion'] = self.blxVersion
		return outdata

	def save_to_file(self, output_file):
		f = open(output_file, 'wb')
		f.write(json.dumps(self.write(), indent = 2).encode()+b'\0')
