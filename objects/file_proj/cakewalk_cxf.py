# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

class cxf_meta:
	def __init__(self):
		self.type = "cxf"
		self.version = "1.0"
		self.clientId = "Next"
		self.clientVersion = "1.0.1.605"

	def read(self, indata):
		if 'type' in indata: self.type = indata['type']
		if 'version' in indata: self.version = indata['version']
		if 'clientId' in indata: self.clientId = indata['clientId']
		if 'clientVersion' in indata: self.clientVersion = indata['clientVersion']

	def write(self):
		outdata = {}
		outdata['type'] = self.type
		outdata['version'] = self.version
		outdata['clientId'] = self.clientId
		outdata['clientVersion'] = self.clientVersion
		return outdata

class cxf_song:
	def __init__(self):
		self.id = ""
		self.stamp = ""
		self.name = ""
		self.forkable = False

	def read(self, indata):
		if 'id' in indata: self.id = indata['id']
		if 'stamp' in indata: self.stamp = indata['stamp']
		if 'name' in indata: self.name = indata['name']
		if 'forkable' in indata: self.forkable = indata['forkable']

	def write(self):
		outdata = {}
		outdata['id'] = self.id
		outdata['stamp'] = self.stamp
		outdata['name'] = self.name
		outdata['forkable'] = self.forkable
		return outdata

class cxf_metronome:
	def __init__(self):
		self.bpm = 120
		self.signature = {"notesCount": 4,"noteValue": 4}

	def read(self, indata):
		if 'bpm' in indata: self.bpm = indata['bpm']
		if 'signature' in indata: self.signature = indata['signature']

	def write(self):
		outdata = {}
		outdata['bpm'] = self.bpm
		outdata['signature'] = self.signature
		return outdata

class cxf_sample:
	def __init__(self, indata):
		self.id = ""
		self.isMidi = False
		self.name = "regions-mix"
		self.file = None
		if indata: self.read(indata)

	def read(self, indata):
		if 'id' in indata: self.id = indata['id']
		if 'isMidi' in indata: self.isMidi = indata['isMidi']
		if 'name' in indata: self.name = indata['name']
		if 'file' in indata: self.file = indata['file']

	def write(self):
		outdata = {}
		outdata['id'] = self.id
		outdata['isMidi'] = self.isMidi
		outdata['name'] = self.name
		outdata['file'] = self.file
		return outdata

class cxf_autopoint:
	def __init__(self, indata):
		self.position = 0
		self.utposition = None
		self.value = 0
		if indata: self.read(indata)

	def read(self, indata):
		if 'position' in indata: self.position = indata['position']
		if 'utposition' in indata: self.utposition = indata['utposition']
		if 'value' in indata: self.value = indata['value']

	def write(self):
		outdata = {}
		outdata['position'] = self.position
		if self.utposition is not None: outdata['utposition'] = self.utposition
		outdata['value'] = self.value
		return outdata

class cxf_automation:
	def __init__(self):
		self.points = []

	def read(self, indata):
		self.points = [cxf_autopoint(x) for x in indata]

	def add_point(self, position, value):
		point = cxf_autopoint(None)
		point.position = position
		point.value = value
		self.points.append(point)

	def write(self):
		return [x.write() for x in self.points]

class cxf_plugin:
	def __init__(self, indata):
		self.format = ""
		self.name = ""
		self.uniqueId = 0
		self.slug = ""
		self.bypass = False
		self.automation = {}
		self.params = {}
		if indata: self.read(indata)

	def read(self, indata):
		if 'format' in indata: self.format = indata['format']
		if 'name' in indata: self.name = indata['name']
		if 'uniqueId' in indata: self.uniqueId = indata['uniqueId']
		if 'slug' in indata: self.slug = indata['slug']
		if 'bypass' in indata: self.bypass = indata['bypass']
		if 'automation' in indata: 
			for n, a in indata['automation'].items():
				auto_obj = cxf_automation()
				auto_obj.read(a)
				self.automation[n] = auto_obj
		if 'params' in indata: self.params = indata['params']

	def write(self):
		outdata = {}
		outdata['format'] = self.format
		outdata['name'] = self.name
		outdata['uniqueId'] = self.uniqueId
		if self.slug: outdata['slug'] = self.slug
		outdata['bypass'] = self.bypass
		automation = outdata['automation'] = {}
		for n, a in self.automation.items(): automation[n] = a.write()
		if self.params: outdata['params'] = self.params
		return outdata

class cxf_auxChannel:
	def __init__(self, indata):
		self.type = ""
		self.id = ""
		self.order = 0
		self.name = ""
		self.colorName = ""
		self.color = ""
		self.volume = 1.0
		self.pan = 0.0
		self.isMuted = False
		self.isSolo = False
		self.effects = []
		self.idOutput = ""
		self.automation = {}
		if indata: self.read(indata)

	def add_effect(self):
		o = cxf_plugin(None)
		self.effects.append(o)
		return o

	def read(self, indata):
		if 'type' in indata: self.type = indata['type']
		if 'id' in indata: self.id = indata['id']
		if 'order' in indata: self.order = indata['order']
		if 'name' in indata: self.name = indata['name']
		if 'colorName' in indata: self.colorName = indata['colorName']
		if 'color' in indata: self.color = indata['color']
		if 'volume' in indata: self.volume = indata['volume']
		if 'pan' in indata: self.pan = indata['pan']
		if 'isMuted' in indata: self.isMuted = indata['isMuted']
		if 'isSolo' in indata: self.isSolo = indata['isSolo']
		if 'effects' in indata: self.effects = [cxf_plugin(x) for x in indata['effects']]
		if 'idOutput' in indata: self.idOutput = indata['idOutput']
		if 'automation' in indata: 
			for n, a in indata['automation'].items():
				auto_obj = cxf_automation()
				auto_obj.read(a)
				self.automation[n] = auto_obj

	def write(self):
		outdata = {}
		outdata['type'] = self.type
		outdata['id'] = self.id
		outdata['order'] = self.order
		outdata['name'] = self.name
		outdata['colorName'] = self.colorName
		outdata['color'] = self.color
		outdata['volume'] = self.volume
		outdata['pan'] = self.pan
		outdata['isMuted'] = self.isMuted
		outdata['isSolo'] = self.isSolo
		outdata['effects'] = [x.write() for x in self.effects]
		outdata['idOutput'] = self.idOutput
		automation = outdata['automation'] = {}
		for n, a in self.automation.items(): automation[n] = a.write()
		return outdata

class cxf_region:
	def __init__(self, indata):
		self.file = ""
		self.name = ""
		self.sampleId = ""
		self.sampleOffset = 0
		self.sampleStartPosition = 0
		self.playbackRate = 0
		self.startPosition = 0
		self.endPosition = 0
		self.loopLength = 0
		if indata: self.read(indata)

	def read(self, indata):
		if 'file' in indata: self.file = indata['file']
		if 'name' in indata: self.name = indata['name']
		if 'sampleId' in indata: self.sampleId = indata['sampleId']
		if 'sampleOffset' in indata: self.sampleOffset = indata['sampleOffset']
		if 'sampleStartPosition' in indata: self.sampleStartPosition = indata['sampleStartPosition']
		if 'playbackRate' in indata: self.playbackRate = indata['playbackRate']
		if 'startPosition' in indata: self.startPosition = indata['startPosition']
		if 'endPosition' in indata: self.endPosition = indata['endPosition']
		if 'loopLength' in indata: self.loopLength = indata['loopLength']

	def write(self):
		outdata = {}
		outdata['file'] = self.file
		outdata['name'] = self.name
		outdata['sampleId'] = self.sampleId
		outdata['sampleOffset'] = self.sampleOffset
		outdata['sampleStartPosition'] = self.sampleStartPosition
		outdata['playbackRate'] = self.playbackRate
		outdata['startPosition'] = self.startPosition
		outdata['endPosition'] = self.endPosition
		outdata['loopLength'] = self.loopLength
		return outdata

class cxf_auxSend:
	def __init__(self, indata):
		self.id = ""
		self.bypass = False
		self.sendLevel = 1.0
		self.sendPan = 0.0
		self.automation = {}
		if indata: self.read(indata)

	def read(self, indata):
		if 'id' in indata: self.id = indata['id']
		if 'bypass' in indata: self.bypass = indata['bypass']
		if 'sendLevel' in indata: self.sendLevel = indata['sendLevel']
		if 'sendPan' in indata: self.sendPan = indata['sendPan']
		if 'automation' in indata: 
			for n, a in indata['automation'].items():
				auto_obj = cxf_automation()
				auto_obj.read(a)
				self.automation[n] = auto_obj

	def write(self):
		outdata = {}
		outdata['id'] = self.id
		outdata['bypass'] = self.bypass
		outdata['sendLevel'] = self.sendLevel
		outdata['sendPan'] = self.sendPan
		for n, a in self.automation.items(): automation[n] = a.write()
		return outdata

class cxf_track:
	def __init__(self, indata):
		self.type = "Instrument"
		self.id = ""
		self.order = 0
		self.parentId = None
		self.synth = None
		self.soundbank = None
		self.name = ""
		self.colorName = ""
		self.color = ""
		self.volume = 1.0
		self.pan = 0.0
		self.isMuted = False
		self.isSolo = False
		self.regions = None
		self.effects = []
		self.idOutput = ""
		self.automation = {}
		self.auxSends = []
		if indata: self.read(indata)

	def add_auxSend(self):
		o = cxf_auxSend(None)
		self.auxSends.append(o)
		return o

	def add_effect(self):
		o = cxf_plugin(None)
		self.effects.append(o)
		return o

	def add_synth(self, indata):
		o = cxf_plugin(None)
		self.synth = o
		return o

	def read(self, indata):
		if 'type' in indata: self.type = indata['type']
		if 'id' in indata: self.id = indata['id']
		if 'order' in indata: self.order = indata['order']
		if 'parentId' in indata: self.parentId = indata['parentId']
		if 'synth' in indata: self.synth = cxf_plugin(indata['synth'])
		if 'soundbank' in indata: self.soundbank = indata['soundbank']
		if 'name' in indata: self.name = indata['name']
		if 'colorName' in indata: self.colorName = indata['colorName']
		if 'color' in indata: self.color = indata['color']
		if 'volume' in indata: self.volume = indata['volume']
		if 'pan' in indata: self.pan = indata['pan']
		if 'isMuted' in indata: self.isMuted = indata['isMuted']
		if 'isSolo' in indata: self.isSolo = indata['isSolo']
		if 'regions' in indata: self.regions = [cxf_region(x) for x in indata['regions']]
		if 'effects' in indata: self.effects = [cxf_plugin(x) for x in indata['effects']]
		if 'auxSends' in indata: self.auxSends = [cxf_auxSend(x) for x in indata['auxSends']]
		if 'idOutput' in indata: self.idOutput = indata['idOutput']
		if 'automation' in indata: 
			for n, a in indata['automation'].items():
				auto_obj = cxf_automation()
				auto_obj.read(a)
				self.automation[n] = auto_obj

	def add_region(self):
		if self.regions is None: self.regions = []
		o = cxf_region(None)
		self.regions.append(o)
		return o

	def write(self):
		outdata = {}
		outdata['type'] = self.type
		outdata['id'] = self.id
		outdata['order'] = self.order
		if self.parentId is not None: outdata['parentId'] = self.parentId
		if self.synth is not None: outdata['synth'] = self.synth
		if self.soundbank is not None: outdata['soundbank'] = self.soundbank
		outdata['name'] = self.name
		outdata['colorName'] = self.colorName
		outdata['color'] = self.color
		outdata['volume'] = self.volume
		outdata['pan'] = self.pan
		outdata['isMuted'] = self.isMuted
		outdata['isSolo'] = self.isSolo
		if self.regions is not None: outdata['regions'] = [x.write() for x in self.regions]
		outdata['effects'] = [x.write() for x in self.effects]
		if self.auxSends is not None: outdata['auxSends'] = [x.write() for x in self.auxSends]
		outdata['idOutput'] = self.idOutput
		automation = outdata['automation'] = {}
		for n, a in self.automation.items(): automation[n] = a.write()
		return outdata

class cxf_arrangertrack_section:
	def __init__(self, indata):
		self.id = 1
		self.name = ""
		self.typeId = 0
		self.color = 0
		self.startTimeArrTicks = 0
		self.endTimeArrTicks = 0
		if indata: self.read(indata)

	def read(self, indata):
		if 'id' in indata: self.id = indata['id']
		if 'name' in indata: self.name = indata['name']
		if 'typeId' in indata: self.typeId = indata['typeId']
		if 'color' in indata: self.color = indata['color']
		if 'startTimeArrTicks' in indata: self.startTimeArrTicks = indata['startTimeArrTicks']
		if 'endTimeArrTicks' in indata: self.endTimeArrTicks = indata['endTimeArrTicks']

	def write(self):
		outdata = {}
		outdata['id'] = self.id
		outdata['name'] = self.name
		outdata['typeId'] = self.typeId
		outdata['color'] = self.color
		outdata['startTimeArrTicks'] = self.startTimeArrTicks
		outdata['endTimeArrTicks'] = self.endTimeArrTicks
		return outdata

class cxf_arrangertrack:
	def __init__(self, indata):
		self.id = 1
		self.name = ""
		self.index = 0
		self.visibleIndex = 0
		self.isVisible = 1
		self.isActive = 1
		self.timeFormat = "musical"
		self.sections = []
		if indata: self.read(indata)

	def read(self, indata):
		if 'id' in indata: self.id = indata['id']
		if 'name' in indata: self.name = indata['name']
		if 'index' in indata: self.index = indata['index']
		if 'visibleIndex' in indata: self.visibleIndex = indata['visibleIndex']
		if 'isVisible' in indata: self.isVisible = indata['isVisible']
		if 'isActive' in indata: self.isActive = indata['isActive']
		if 'timeFormat' in indata: self.timeFormat = indata['timeFormat']
		if 'sections' in indata: self.sections = [cxf_arrangertrack_section(x) for x in indata['sections']]

	def write(self):
		outdata = {}
		outdata['id'] = self.id
		outdata['name'] = self.name
		outdata['index'] = self.index
		outdata['visibleIndex'] = self.visibleIndex
		outdata['isVisible'] = self.isVisible
		outdata['isActive'] = self.isActive
		outdata['timeFormat'] = self.timeFormat
		outdata['sections'] = [x.write() for x in self.sections]
		return outdata

class cxf_arranger:
	def __init__(self):
		self.arrangerTracks = []
		self.used = False

	def read(self, indata):
		if 'arrangerTracks' in indata: 
			self.arrangerTracks = [cxf_arrangertrack(x) for x in indata['arrangerTracks']]
			self.used = True

	def write(self):
		outdata = {}
		outdata['arrangerTracks'] = [x.write() for x in self.arrangerTracks]
		return outdata

class cxf_project:
	def __init__(self):
		self.meta = cxf_meta()
		self.stamp = ""
		self.song = cxf_song()
		self.description = ""
		self.metronome = cxf_metronome()
		self.description = ""
		self.tempoTrack = None
		self.mainBusId = None
		self.samples = []
		self.auxChannels = []
		self.tracks = []
		self.arranger = cxf_arranger()

	def add_sample(self):
		o = cxf_sample(None)
		self.samples.append(o)
		return o

	def add_auxChannel(self):
		o = cxf_auxChannel(None)
		self.auxChannels.append(o)
		return o

	def add_track(self):
		o = cxf_track(None)
		self.tracks.append(o)
		return o

	def read(self, indata):
		if 'meta' in indata: self.meta.read(indata['meta'])
		if 'stamp' in indata: self.stamp = indata['stamp']
		if 'song' in indata: self.song.read(indata['song'])
		if 'description' in indata: self.description = indata['description']
		if 'metronome' in indata: self.metronome.read(indata['metronome'])
		if 'mainBusId' in indata: self.mainBusId = indata['mainBusId']
		if 'tempoTrack' in indata: self.tempoTrack = indata['tempoTrack']
		self.samples = [cxf_sample(x) for x in indata['samples']]
		self.auxChannels = [cxf_auxChannel(x) for x in indata['auxChannels']]
		self.tracks = [cxf_track(x) for x in indata['tracks']]
		if 'arranger' in indata: self.arranger.read(indata['arranger'])
		return True

	def load_from_file(self, input_file):
		f = open(input_file, 'rb')
		jsontxt = f.read().decode()
		projectdata = json.loads(jsontxt)
		self.read(projectdata)
		return True

	def write(self):
		outdata = {}
		outdata['meta'] = self.meta.write()
		outdata['stamp'] = self.stamp
		outdata['song'] = self.song.write()
		outdata['description'] = self.description
		outdata['metronome'] = self.metronome.write()
		outdata['mainBusId'] = self.mainBusId
		if self.tempoTrack is not None: outdata['tempoTrack'] = self.tempoTrack
		outdata['samples'] = [x.write() for x in self.samples]
		outdata['auxChannels'] = [x.write() for x in self.auxChannels]
		outdata['tracks'] = [x.write() for x in self.tracks]
		if self.arranger.used: outdata['arranger'] = self.arranger.write()
		return outdata

	def save_to_file(self, output_file):
		f = open(output_file, 'wb')
		f.write(json.dumps(self.write(), indent = 2).encode())
