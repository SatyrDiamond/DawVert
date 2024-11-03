# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from lxml import etree as ET
from objects.exceptions import ProjectFileParserException

def metadata_to_dict(xml_proj):
	out_dict = {}
	for xmlpart in xml_proj:
		if xmlpart.tag == 'data': out_dict[xmlpart.get('key')] = xmlpart.get('value')
	return out_dict

def dict_to_metadata(in_dict, xml_proj):
	tempxml = ET.SubElement(xml_proj, "metaData")
	for k, v in in_dict.items():
		metaxml = ET.SubElement(tempxml, "data")
		metaxml.set('key', k)
		metaxml.set('value', str(v))

# --------------------------------------------------------- POOL ---------------------------------------------------------

class soundbridge_audioSource:
	def __init__(self, xml_proj):
		self.fileName = None
		self.sourceFileName = None
		self.channelCount = None
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		self.fileName = xml_proj.get('fileName')
		self.sourceFileName = xml_proj.get('sourceFileName')
		self.channelCount = xml_proj.get('channelCount')

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "audioSource")
		if self.fileName is not None: tempxml.set('fileName', str(self.fileName))
		if self.sourceFileName is not None: tempxml.set('sourceFileName', str(self.sourceFileName))
		if self.channelCount is not None: tempxml.set('channelCount', str(self.channelCount))

class soundbridge_videoSource:
	def __init__(self, xml_proj):
		self.fileName = None
		self.sourceFileName = None
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		self.fileName = xml_proj.get('fileName')
		self.sourceFileName = xml_proj.get('sourceFileName')

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "videoSource")
		if self.fileName is not None: tempxml.set('fileName', str(self.fileName))
		if self.sourceFileName is not None: tempxml.set('sourceFileName', str(self.sourceFileName))

class soundbridge_trackNameExtension:
	def __init__(self, xml_proj):
		self.trackType = None
		self.value = None
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		self.trackType = xml_proj.get('trackType')
		self.value = xml_proj.get('value')

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "trackNameExtension")
		if self.trackType is not None: tempxml.set('trackType', str(self.trackType))
		if self.value is not None: tempxml.set('value', str(self.value))

class soundbridge_blockNameExtension:
	def __init__(self, xml_proj):
		self.trackType = None
		self.value = None
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		self.trackType = xml_proj.get('trackType')
		self.value = xml_proj.get('value')

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "blockNameExtension")
		if self.trackType is not None: tempxml.set('trackType', str(self.trackType))
		if self.value is not None: tempxml.set('value', str(self.value))

class soundbridge_pool:
	def __init__(self, xml_proj):
		self.audioSources = []
		self.videoSources = []
		self.trackNameExtensions = []
		self.blockNameExtensions = []
		self.blockSourceNameExtension = 0
		if xml_proj is not None: self.read(xml_proj)

	def defualts(self):
		for x in range(5):
			tne = soundbridge_trackNameExtension(None)
			tne.trackType = x
			tne.value = 0
			self.trackNameExtensions.append(tne)
		for x in range(5):
			tne = soundbridge_blockNameExtension(None)
			tne.trackType = x
			tne.value = 0
			self.blockNameExtensions.append(tne)

	def read(self, xml_proj):
		for xmlpart in xml_proj:

			if xmlpart.tag == 'audioSources':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'audioSource': self.audioSources.append(soundbridge_audioSource(xmlinpart))

			if xmlpart.tag == 'videoSources':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'videoSource': self.videoSources.append(soundbridge_videoSource(xmlinpart))

			if xmlpart.tag == 'trackNameExtensions':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'trackNameExtension': self.trackNameExtensions.append(soundbridge_trackNameExtension(xmlinpart))

			if xmlpart.tag == 'blockNameExtensions':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'blockNameExtension': self.blockNameExtensions.append(soundbridge_blockNameExtension(xmlinpart))

			if xmlpart.tag == 'blockSourceNameExtension': self.blockSourceNameExtension = xmlpart.get('value')

	def write(self, xml_proj):
		pool_xml = ET.SubElement(xml_proj, "pool")
		audioSources = ET.SubElement(pool_xml, "audioSources")
		for x in self.audioSources: x.write(audioSources)
		videoSources = ET.SubElement(pool_xml, "videoSources")
		for x in self.videoSources: x.write(videoSources)
		trackNameExtensions = ET.SubElement(pool_xml, "trackNameExtensions")
		for x in self.trackNameExtensions: x.write(trackNameExtensions)
		blockNameExtensions = ET.SubElement(pool_xml, "blockNameExtensions")
		for x in self.blockNameExtensions: x.write(blockNameExtensions)

		blockSourceNameExtension = ET.SubElement(pool_xml, "blockSourceNameExtension")
		blockSourceNameExtension.set('value', str(self.blockSourceNameExtension))

# --------------------------------------------------------- AUTOMATION ---------------------------------------------------------

class soundbridge_automationTrack:
	def __init__(self, xml_proj):
		self.parameterIndex = None
		self.mode = None
		self.enabled = None
		self.defaultValue = None
		self.blocks = []
		self.returnTrackPath = None
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'parameterIndex' in trackattrib: self.parameterIndex = int(xml_proj.get("parameterIndex"))
		if 'mode' in trackattrib: self.mode = int(xml_proj.get("mode"))
		if 'enabled' in trackattrib: self.enabled = int(xml_proj.get("enabled"))
		if 'defaultValue' in trackattrib: self.defaultValue = float(xml_proj.get("defaultValue"))
		if 'returnTrackPath' in trackattrib: self.returnTrackPath = xml_proj.get("returnTrackPath")

		for xmlpart in xml_proj:
			if xmlpart.tag == 'blocks': 
				self.blocks = []
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'block': self.blocks.append(soundbridge_block(xmlinpart))

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, 'automationTrack')
		if self.parameterIndex is not None: tempxml.set('parameterIndex', str(self.parameterIndex))
		if self.mode is not None: tempxml.set('mode', str(self.mode))
		if self.enabled is not None: tempxml.set('enabled', str(self.enabled))
		if self.defaultValue is not None: tempxml.set('defaultValue', str(self.defaultValue))
		if self.returnTrackPath is not None: tempxml.set('returnTrackPath', str(self.returnTrackPath))
		if self.blocks != None:
			blockContainersxml = ET.SubElement(tempxml, 'blocks')
			for x in self.blocks: x.write(blockContainersxml)

class soundbridge_automationContainer:
	def __init__(self, xml_proj):
		self.automationTracks = []
		self.state = None
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		for xmlpart in xml_proj:
			if xmlpart.tag == 'state': self.state = xmlpart.text
			elif xmlpart.tag == 'automationTracks': 
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'automationTrack': self.automationTracks.append(soundbridge_automationTrack(xmlinpart))

	def write(self, xml_proj, tagname):
		tempxml = ET.SubElement(xml_proj, tagname)
		xmlatr = ET.SubElement(tempxml, 'automationTracks')
		for x in self.automationTracks: x.write(xmlatr)
		if self.state is not None: 
			statexml = ET.SubElement(tempxml, 'state')
			statexml.text = self.state

# --------------------------------------------------------- PLUGINS ---------------------------------------------------------

class soundbridge_audioUnit:
	def __init__(self, xml_proj):
		self.uid = ""
		self.vendor = ""
		self.name = ""
		self.sideChainBufferType = 1
		self.state = None
		self.automationContainer = soundbridge_automationContainer(None)
		self.metadata = {}
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'uid' in trackattrib: self.uid = xml_proj.get("uid")
		if 'vendor' in trackattrib: self.vendor = xml_proj.get("vendor")
		if 'name' in trackattrib: self.name = xml_proj.get("name")
		if 'sideChainBufferType' in trackattrib: self.sideChainBufferType = int(xml_proj.get("sideChainBufferType"))
		for xmlpart in xml_proj:
			if xmlpart.tag == 'state': self.state = xmlpart.text
			if xmlpart.tag == 'metaData': self.metadata = metadata_to_dict(xmlpart)
			if xmlpart.tag == 'automationContainer': self.automationContainer = soundbridge_automationContainer(xmlpart)

	def write(self, xml_proj, tagname):
		tempxml = ET.SubElement(xml_proj, tagname)
		tempxml.set('uid', str(self.uid))
		tempxml.set('vendor', str(self.vendor))
		tempxml.set('name', str(self.name))
		tempxml.set('sideChainBufferType', str(self.sideChainBufferType))
		if self.state: 
			statexml = ET.SubElement(tempxml, 'state')
			statexml.text = self.state
		self.automationContainer.write(tempxml, 'automationContainer')
		dict_to_metadata(self.metadata, tempxml)

# --------------------------------------------------------- TRACK DATA ---------------------------------------------------------

class soundbridge_marker:
	def __init__(self, xml_proj):
		self.position = None
		self.tag = None
		self.label = None
		self.comment = None
		self.state = None
		self.left = None
		self.top = None
		self.right = None
		self.bottom = None
		self.linearTimeBase = None
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'position' in trackattrib: self.position = int(xml_proj.get('position'))
		if 'tag' in trackattrib: self.tag = xml_proj.get('tag')
		if 'label' in trackattrib: self.label = xml_proj.get('label')
		if 'comment' in trackattrib: self.comment = xml_proj.get('comment')
		if 'state' in trackattrib: self.state = xml_proj.get('state')
		if 'left' in trackattrib: self.left = xml_proj.get('left')
		if 'top' in trackattrib: self.top = xml_proj.get('top')
		if 'right' in trackattrib: self.right = xml_proj.get('right')
		if 'bottom' in trackattrib: self.bottom = xml_proj.get('bottom')
		if 'linearTimeBase' in trackattrib: self.linearTimeBase = xml_proj.get('linearTimeBase')

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "marker")
		if self.position is not None: tempxml.set('position', str(self.position))
		if self.tag is not None: tempxml.set('tag', str(self.tag))
		if self.label is not None: tempxml.set('label', str(self.label))
		if self.comment is not None: tempxml.set('comment', str(self.comment))
		if self.state is not None: tempxml.set('state', str(self.state))
		if self.left is not None: tempxml.set('left', str(self.left))
		if self.top is not None: tempxml.set('top', str(self.top))
		if self.right is not None: tempxml.set('right', str(self.right))
		if self.bottom is not None: tempxml.set('bottom', str(self.bottom))
		if self.linearTimeBase is not None: tempxml.set('linearTimeBase', str(self.linearTimeBase))

class soundbridge_deviceRoute:
	def __init__(self, xml_proj):
		self.externalDeviceIndex = -1
		self.channelIndex = -1
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'externalDeviceIndex' in trackattrib: self.externalDeviceIndex = int(xml_proj.get('externalDeviceIndex'))
		if 'channelIndex' in trackattrib: self.channelIndex = int(xml_proj.get('channelIndex'))

	def write(self, xml_proj, tagname):
		tempxml = ET.SubElement(xml_proj, tagname)
		tempxml.set('externalDeviceIndex', str(self.externalDeviceIndex))
		tempxml.set('channelIndex', str(self.channelIndex))

# --------------------------------------------------------- BLOCKS ---------------------------------------------------------

class soundbridge_crossfade:
	def __init__(self, xml_proj):
		self.eventLeft = None
		self.eventRight = None
		self.leftAlignment = None
		self.curveTypeLeft = None
		self.curveTypeRight = None
		self.convexityLeft = None
		self.convexityRight = None
		self.lengthRatio = None
		self.length = None
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'eventLeft' in trackattrib: self.eventLeft = xml_proj.get('eventLeft')
		if 'eventRight' in trackattrib: self.eventRight = xml_proj.get('eventRight')
		if 'leftAlignment' in trackattrib: self.leftAlignment = xml_proj.get('leftAlignment')
		if 'curveTypeLeft' in trackattrib: self.curveTypeLeft = xml_proj.get('curveTypeLeft')
		if 'curveTypeRight' in trackattrib: self.curveTypeRight = xml_proj.get('curveTypeRight')
		if 'convexityLeft' in trackattrib: self.convexityLeft = xml_proj.get('convexityLeft')
		if 'convexityRight' in trackattrib: self.convexityRight = xml_proj.get('convexityRight')
		if 'lengthRatio' in trackattrib: self.lengthRatio = xml_proj.get('lengthRatio')
		if 'length' in trackattrib: self.length = xml_proj.get('length')

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "crossfade")
		if self.eventLeft: tempxml.set('eventLeft', str(self.eventLeft))
		if self.eventRight: tempxml.set('eventRight', str(self.eventRight))
		if self.leftAlignment: tempxml.set('leftAlignment', str(self.leftAlignment))
		if self.curveTypeLeft: tempxml.set('curveTypeLeft', str(self.curveTypeLeft))
		if self.curveTypeRight: tempxml.set('curveTypeRight', str(self.curveTypeRight))
		if self.convexityLeft: tempxml.set('convexityLeft', str(self.convexityLeft))
		if self.convexityRight: tempxml.set('convexityRight', str(self.convexityRight))
		if self.lengthRatio: tempxml.set('lengthRatio', str(self.lengthRatio))
		if self.length: tempxml.set('length', str(self.length))

class soundbridge_stretchMark:
	def __init__(self, xml_proj):
		self.initPosition = 0
		self.newPosition = 0
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'initPosition' in trackattrib: self.initPosition = int(xml_proj.get('initPosition'))
		if 'newPosition' in trackattrib: self.newPosition = int(xml_proj.get('newPosition'))

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "stretchMark")
		tempxml.set('initPosition', str(self.initPosition))
		tempxml.set('newPosition', str(self.newPosition))

class soundbridge_event:
	def __init__(self, xml_proj):
		self.position = None
		self.positionStart = None
		self.positionEnd = None
		self.loopOffset = None
		self.framesCount = None
		self.loopEnabled = None
		self.tempo = None
		self.inverse = None
		self.gain = None
		self.fadeInLength = None
		self.fadeOutLength = None
		self.fadeInCurve = None
		self.fadeOutCurve = None
		self.fadeInConvexity = None
		self.fadeOutConvexity = None
		self.pitch = None
		self.fileName = None
		self.stretchMarks = []
		self.automationBlocks = []
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'position' in trackattrib: self.position = int(xml_proj.get('position'))
		if 'positionStart' in trackattrib: self.positionStart = int(xml_proj.get('positionStart'))
		if 'positionEnd' in trackattrib: self.positionEnd = int(xml_proj.get('positionEnd'))
		if 'loopOffset' in trackattrib: self.loopOffset = int(xml_proj.get('loopOffset'))
		if 'framesCount' in trackattrib: self.framesCount = int(xml_proj.get('framesCount'))
		if 'loopEnabled' in trackattrib: self.loopEnabled = int(xml_proj.get('loopEnabled'))
		if 'tempo' in trackattrib: self.tempo = xml_proj.get('tempo')
		if 'inverse' in trackattrib: self.inverse = xml_proj.get('inverse')
		if 'gain' in trackattrib: self.gain = float(xml_proj.get('gain'))
		if 'fadeInLength' in trackattrib: self.fadeInLength = int(xml_proj.get('fadeInLength'))
		if 'fadeOutLength' in trackattrib: self.fadeOutLength = int(xml_proj.get('fadeOutLength'))
		if 'fadeInCurve' in trackattrib: self.fadeInCurve = xml_proj.get('fadeInCurve')
		if 'fadeOutCurve' in trackattrib: self.fadeOutCurve = xml_proj.get('fadeOutCurve')
		if 'fadeInConvexity' in trackattrib: self.fadeInConvexity = xml_proj.get('fadeInConvexity')
		if 'fadeOutConvexity' in trackattrib: self.fadeOutConvexity = xml_proj.get('fadeOutConvexity')
		if 'pitch' in trackattrib: self.pitch = float(xml_proj.get('pitch'))
		if 'fileName' in trackattrib: self.fileName = xml_proj.get('fileName')
		for xmlpart in xml_proj:
			if xmlpart.tag == 'stretchMarks': 
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'stretchMark': self.stretchMarks.append(soundbridge_stretchMark(xmlinpart))
			elif xmlpart.tag == 'automationBlocks': 
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'block': self.automationBlocks.append(soundbridge_block(xmlinpart))

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "event")
		if self.position is not None: tempxml.set('position', str(self.position))
		if self.positionStart is not None: tempxml.set('positionStart', str(self.positionStart))
		if self.positionEnd is not None: tempxml.set('positionEnd', str(self.positionEnd))
		if self.loopOffset is not None: tempxml.set('loopOffset', str(self.loopOffset))
		if self.framesCount is not None: tempxml.set('framesCount', str(self.framesCount))
		if self.loopEnabled is not None: tempxml.set('loopEnabled', str(self.loopEnabled))
		if self.tempo is not None: tempxml.set('tempo', str(self.tempo))
		if self.inverse is not None: tempxml.set('inverse', str(self.inverse))
		if self.gain is not None: tempxml.set('gain', str(self.gain))
		if self.fadeInLength is not None: tempxml.set('fadeInLength', str(self.fadeInLength))
		if self.fadeOutLength is not None: tempxml.set('fadeOutLength', str(self.fadeOutLength))
		if self.fadeInCurve is not None: tempxml.set('fadeInCurve', str(self.fadeInCurve))
		if self.fadeOutCurve is not None: tempxml.set('fadeOutCurve', str(self.fadeOutCurve))
		if self.fadeInConvexity is not None: tempxml.set('fadeInConvexity', str(self.fadeInConvexity))
		if self.fadeOutConvexity is not None: tempxml.set('fadeOutConvexity', str(self.fadeOutConvexity))
		if self.pitch is not None: tempxml.set('pitch', str(self.pitch))
		if self.fileName is not None: tempxml.set('fileName', str(self.fileName))
		xml_stretchMarks = ET.SubElement(tempxml, 'stretchMarks')
		for x in self.stretchMarks: x.write(xml_stretchMarks)
		xml_automationBlocks = ET.SubElement(tempxml, 'automationBlocks')
		for x in self.automationBlocks: x.write(xml_automationBlocks)

class soundbridge_block:
	def __init__(self, xml_proj):
		self.name = ''
		self.position = 0
		self.framesCount = 0
		self.muted = 0
		self.timeBaseMode = 0
		self.positionStart = None
		self.positionEnd = None
		self.loopOffset = None
		self.muted = None
		self.blockData = None
		self.metadata = {}
		self.crossfades = None
		self.events = None
		self.automationBlocks = None
		self.midiUnits = None
		self.framesCount = None
		self.filename = None
		self.loopEnabled = None
		self.stretchMarks = None
		self.version = None
		self.index = None
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'name' in trackattrib: self.name = xml_proj.get('name')
		if 'position' in trackattrib: self.position = int(xml_proj.get('position'))
		if 'framesCount' in trackattrib: self.framesCount = xml_proj.get('framesCount')
		if 'timeBaseMode' in trackattrib: self.timeBaseMode = int(xml_proj.get('timeBaseMode'))
		if 'positionStart' in trackattrib: self.positionStart = int(xml_proj.get('positionStart'))
		if 'positionEnd' in trackattrib: self.positionEnd = int(xml_proj.get('positionEnd'))
		if 'loopOffset' in trackattrib: self.loopOffset = int(xml_proj.get('loopOffset'))
		if 'loopEnabled' in trackattrib: self.loopEnabled = int(xml_proj.get('loopEnabled'))
		if 'muted' in trackattrib: self.muted = int(xml_proj.get('muted'))
		if 'framesCount' in trackattrib: self.framesCount = int(xml_proj.get('framesCount'))
		if 'index' in trackattrib: self.index = int(xml_proj.get('index'))
		if 'fileName' in trackattrib: self.filename = xml_proj.get('fileName')
		if 'version' in trackattrib: self.version = xml_proj.get('version')
		for xmlpart in xml_proj:
			if xmlpart.tag == 'metaData': self.metadata = metadata_to_dict(xmlpart)
			elif xmlpart.tag == 'blockData': 
				self.blockData = xmlpart.text
				if not xmlpart.text: self.blockData = ''
			elif xmlpart.tag == 'events': 
				self.events = []
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'event': self.events.append(soundbridge_event(xmlinpart))
			elif xmlpart.tag == 'crossfades': 
				self.crossfades = []
			elif xmlpart.tag == 'automationBlocks': 
				self.automationBlocks = []
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'block': self.automationBlocks.append(soundbridge_block(xmlinpart))
			elif xmlpart.tag == 'stretchMarks': 
				self.stretchMarks = []
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'stretchMark': self.stretchMarks.append(soundbridge_stretchMark(xmlinpart))

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "block")
		tempxml.set('name', str(self.name))
		tempxml.set('position', str(self.position))
		tempxml.set('framesCount', str(self.framesCount))
		tempxml.set('muted', str(self.muted))
		tempxml.set('timeBaseMode', str(self.timeBaseMode))
		if self.positionStart is not None: tempxml.set('positionStart', str(self.positionStart))
		if self.positionEnd is not None: tempxml.set('positionEnd', str(self.positionEnd))
		if self.loopOffset is not None: tempxml.set('loopOffset', str(self.loopOffset))
		if self.muted is not None: tempxml.set('muted', str(self.muted))
		if self.framesCount is not None: tempxml.set('framesCount', str(self.framesCount))
		if self.filename is not None: tempxml.set('fileName', str(self.filename))
		if self.loopEnabled is not None: tempxml.set('loopEnabled', str(self.loopEnabled))
		if self.version is not None: tempxml.set('version', str(self.version))
		if self.index is not None: tempxml.set('index', str(self.index))

		dict_to_metadata(self.metadata, tempxml)

		if self.blockData is not None:
			xml_blockData = ET.SubElement(tempxml, 'blockData')
			xml_blockData.text = self.blockData
		if self.crossfades is not None:
			xml_crossfades = ET.SubElement(tempxml, 'crossfades')
		if self.events is not None:
			xml_events = ET.SubElement(tempxml, 'events')
			for x in self.events: x.write(xml_events)
		if self.automationBlocks is not None:
			xml_automationBlocks = ET.SubElement(tempxml, 'automationBlocks')
			for x in self.automationBlocks: x.write(xml_automationBlocks)
		if self.stretchMarks is not None:
			xml_stretchMarks = ET.SubElement(tempxml, 'stretchMarks')
			for x in self.stretchMarks: x.write(xml_stretchMarks)

class soundbridge_blockContainer:
	def __init__(self, xml_proj):
		self.name = ''
		self.blocks = []
		self.crossfades = []
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'name' in trackattrib: self.name = xml_proj.get('name')
		for xmlpart in xml_proj:
			if xmlpart.tag == 'crossfades': 
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'crossfade': self.crossfades.append(soundbridge_crossfade(xmlinpart))
			elif xmlpart.tag == 'blocks': 
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'block': self.blocks.append(soundbridge_block(xmlinpart))

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, 'blockContainer')
		tempxml.set('name', str(self.name))
		xml_crossfades = ET.SubElement(tempxml, 'crossfades')
		for x in self.crossfades: x.write(xml_crossfades)
		xml_blocks = ET.SubElement(tempxml, 'blocks')
		for x in self.blocks: x.write(xml_blocks)

# --------------------------------------------------------- TRACK ---------------------------------------------------------

class soundbridge_videotrack:
	def __init__(self, xml_proj):
		self.name = "Video"
		self.blocks = None
		self.metadata = {}
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		self.tag = xml_proj.tag
		trackattrib = xml_proj.attrib
		if 'name' in trackattrib: self.name = xml_proj.get("name")
		for xmlpart in xml_proj:
			if xmlpart.tag == 'metaData': self.metadata = metadata_to_dict(xmlpart)
			elif xmlpart.tag == 'blocks': 
				self.blocks = []
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'block': self.blocks.append(soundbridge_block(xmlinpart))

	def defualts(self):
		self.metadata['Color'] = "#ff414a"

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, 'videoTrack')
		tempxml.set('name', str(self.name))

		dict_to_metadata(self.metadata, tempxml)

		if self.blocks != None:
			blockContainersxml = ET.SubElement(tempxml, 'blocks')
			for x in self.blocks: x.write(blockContainersxml)

class soundbridge_track:
	def __init__(self, xml_proj):
		self.name = ""
		self.type = 0
		self.armed = 0
		self.monitored = 0
		self.automationArmed = 0
		self.audioUnitsBypass = 0
		self.latencyOffset = 0
		self.inverse = 0
		self.timeBaseMode = 0
		self.tracks = []
		self.state = None
		self.audioUnits = []
		self.metadata = {}
		self.automationContainer = soundbridge_automationContainer(None)
		self.sendsAutomationContainer = soundbridge_automationContainer(None)
		self.audioOutput = soundbridge_deviceRoute(None)
		self.audioInput = None
		self.midiInput = None
		self.midiOutput = None
		self.markers = []
		self.blockContainers = None
		self.channelCount = None
		self.midiInstrument = None
		self.pitchTempoProcessorMode = None
		self.blocks = None
		self.midiUnits = None
		self.sourceBufferType = None
		self.tag = 'track'
		if xml_proj is not None: self.read(xml_proj)

	def defualts_master(self):
		self.name = 'Master'
		self.type = 0
		self.armed = 0
		self.monitored = 0
		self.automationArmed = 0
		self.audioUnitsBypass = 0
		self.latencyOffset = 0
		self.inverse = 0
		self.timeBaseMode = 0
		self.state = 'PwAAAD9TMzM.UzMzPwAAAA=='
		self.metadata['TrackColor'] = "#ffad41"

	def read(self, xml_proj):
		self.tag = xml_proj.tag
		trackattrib = xml_proj.attrib
		if 'name' in trackattrib: self.name = xml_proj.get("name")
		if 'type' in trackattrib: self.type = int(xml_proj.get("type"))
		if 'armed' in trackattrib: self.armed = int(xml_proj.get("armed"))
		if 'monitored' in trackattrib: self.monitored = int(xml_proj.get("monitored"))
		if 'automationArmed' in trackattrib: self.automationArmed = int(xml_proj.get("automationArmed"))
		if 'audioUnitsBypass' in trackattrib: self.audioUnitsBypass = int(xml_proj.get("audioUnitsBypass"))
		if 'latencyOffset' in trackattrib: self.latencyOffset = int(xml_proj.get("latencyOffset"))
		if 'inverse' in trackattrib: self.inverse = int(xml_proj.get("inverse"))
		if 'timeBaseMode' in trackattrib: self.timeBaseMode = int(xml_proj.get("timeBaseMode"))
		if 'channelCount' in trackattrib: self.channelCount = int(xml_proj.get("channelCount"))
		if 'sourceBufferType' in trackattrib: self.sourceBufferType = int(xml_proj.get("sourceBufferType"))
		if 'pitchTempoProcessorMode' in trackattrib: self.pitchTempoProcessorMode = int(xml_proj.get("pitchTempoProcessorMode"))
		for xmlpart in xml_proj:
			if xmlpart.tag == 'track': self.tracks.append(soundbridge_track(xmlpart))
			elif xmlpart.tag == 'state': self.state = xmlpart.text
			elif xmlpart.tag == 'audioUnits':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'audioUnit': self.audioUnits.append(soundbridge_audioUnit(xmlinpart))
			elif xmlpart.tag == 'automationContainer': self.automationContainer = soundbridge_automationContainer(xmlpart)
			elif xmlpart.tag == 'sendsAutomationContainer': self.sendsAutomationContainer = soundbridge_automationContainer(xmlpart)
			elif xmlpart.tag == 'metaData': self.metadata = metadata_to_dict(xmlpart)
			elif xmlpart.tag == 'audioOutput': self.audioOutput = soundbridge_deviceRoute(xmlpart)
			elif xmlpart.tag == 'markers':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'marker': self.markers.append(soundbridge_marker(xmlinpart))
			elif xmlpart.tag == 'audioInput': self.audioInput = soundbridge_deviceRoute(xmlpart)
			elif xmlpart.tag == 'blockContainers': 
				self.blockContainers = []
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'blockContainer': 
						self.blockContainers.append(soundbridge_blockContainer(xmlinpart))
			elif xmlpart.tag == 'blocks': 
				self.blocks = []
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'block': self.blocks.append(soundbridge_block(xmlinpart))
			elif xmlpart.tag == 'midiUnits': 
				self.midiUnits = []
			elif xmlpart.tag == 'midiInput': self.midiInput = soundbridge_deviceRoute(xmlpart)
			elif xmlpart.tag == 'midiOutput': self.midiOutput = soundbridge_deviceRoute(xmlpart)
			elif xmlpart.tag == 'midiInstrument': self.midiInstrument = soundbridge_audioUnit(xmlpart)

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, self.tag)
		tempxml.set('name', str(self.name))
		tempxml.set('type', str(self.type))
		tempxml.set('armed', str(self.armed))
		tempxml.set('monitored', str(self.monitored))
		tempxml.set('automationArmed', str(self.automationArmed))
		tempxml.set('audioUnitsBypass', str(self.audioUnitsBypass))
		tempxml.set('latencyOffset', str(self.latencyOffset))
		tempxml.set('inverse', str(self.inverse))
		tempxml.set('timeBaseMode', str(self.timeBaseMode))
		if self.channelCount is not None: tempxml.set('channelCount', str(self.channelCount))
		if self.pitchTempoProcessorMode is not None: tempxml.set('pitchTempoProcessorMode', str(self.pitchTempoProcessorMode))
		if self.state: 
			statexml = ET.SubElement(tempxml, 'state')
			statexml.text = self.state
		xmlau = ET.SubElement(tempxml, 'audioUnits')
		for x in self.audioUnits:
			x.write(xmlau, 'audioUnit')
		self.automationContainer.write(tempxml, 'automationContainer')
		self.sendsAutomationContainer.write(tempxml, 'sendsAutomationContainer')
		dict_to_metadata(self.metadata, tempxml)
		if self.markers:
			markersxml = ET.SubElement(tempxml, 'markers')
			for x in self.markers: 
				x.write(markersxml)
		self.audioOutput.write(tempxml, 'audioOutput')

		if self.blockContainers != None:
			blockContainersxml = ET.SubElement(tempxml, 'blockContainers')
			for x in self.blockContainers: x.write(blockContainersxml)

		if self.blocks != None:
			blockContainersxml = ET.SubElement(tempxml, 'blocks')
			for x in self.blocks: x.write(blockContainersxml)

		if self.midiUnits != None:
			blockContainersxml = ET.SubElement(tempxml, 'midiUnits')

		if self.midiInstrument: self.midiInstrument.write(tempxml, 'midiInstrument')

		if self.audioInput: self.audioInput.write(tempxml, 'audioInput')

		if self.midiInput: self.midiInput.write(tempxml, 'midiInput')
		if self.midiOutput: self.midiOutput.write(tempxml, 'midiOutput')

		if self.sourceBufferType is not None: tempxml.set('sourceBufferType', str(self.sourceBufferType))
		
		for x in self.tracks: x.write(tempxml)

# --------------------------------------------------------- SONG ---------------------------------------------------------

class soundbridge_tempo_section:
	def __init__(self, xml_proj):
		self.position = 0
		self.length = 4
		self.startTempo = 120
		self.endTempo = 120
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		self.position = int(xml_proj.get('position'))
		self.length = int(xml_proj.get('length'))
		self.startTempo = int(xml_proj.get('startTempo'))
		self.endTempo = int(xml_proj.get('endTempo'))

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "section")
		tempxml.set('position', str(self.position))
		tempxml.set('length', str(self.length))
		tempxml.set('startTempo', str(self.startTempo))
		tempxml.set('endTempo', str(self.endTempo))

class soundbridge_tempo:
	def __init__(self, xml_proj):
		self.tempo = 120
		self.version = 1
		self.sections = []
		self.metadata = {}
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'tempo' in trackattrib: self.tempo = int(xml_proj.get('tempo'))
		if 'version' in trackattrib: self.version = int(xml_proj.get('version'))
		for xmlpart in xml_proj:
			if xmlpart.tag == 'section': self.sections.append(soundbridge_tempo_section(xmlpart))
			elif xmlpart.tag == 'metaData': self.metadata = metadata_to_dict(xmlpart)

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "tempo")
		tempxml.set('tempo', str(self.tempo))
		tempxml.set('version', str(self.version))
		for x in self.sections: x.write(tempxml)
		if self.metadata: dict_to_metadata(self.metadata, tempxml)

class soundbridge_timeSignature_section:
	def __init__(self, xml_proj):
		self.positionBars = 0
		self.lengthBars = 4
		self.timeSigNumerator = 4
		self.timeSigDenominator = 4
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		self.positionBars = int(xml_proj.get('positionBars'))
		self.lengthBars = int(xml_proj.get('lengthBars'))
		self.timeSigNumerator = int(xml_proj.get('timeSigNumerator'))
		self.timeSigDenominator = int(xml_proj.get('timeSigDenominator'))

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "section")
		tempxml.set('positionBars', str(self.positionBars))
		tempxml.set('lengthBars', str(self.lengthBars))
		tempxml.set('timeSigNumerator', str(self.timeSigNumerator))
		tempxml.set('timeSigDenominator', str(self.timeSigDenominator))

class soundbridge_timeSignature:
	def __init__(self, xml_proj):
		self.timeSigNumerator = 4
		self.timeSigDenominator = 4
		self.sections = []
		self.metadata = {}
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'timeSigNumerator' in trackattrib: self.timeSigNumerator = int(xml_proj.get('timeSigNumerator'))
		if 'timeSigDenominator' in trackattrib: self.timeSigDenominator = int(xml_proj.get('timeSigDenominator'))
		for xmlpart in xml_proj:
			if xmlpart.tag == 'section': self.sections.append(soundbridge_timeSignature_section(xmlpart))
			elif xmlpart.tag == 'metaData': self.metadata = metadata_to_dict(xmlpart)

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "timeSignature")
		tempxml.set('timeSigNumerator', str(self.timeSigNumerator))
		tempxml.set('timeSigDenominator', str(self.timeSigDenominator))
		for x in self.sections: x.write(tempxml)
		if self.metadata: dict_to_metadata(self.metadata, tempxml)

class soundbridge_timeline:
	def __init__(self):
		self.timeSignature = soundbridge_timeSignature(None)
		self.tempo = soundbridge_tempo(None)
		self.markers = []

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'timeSignature': self.timeSignature = soundbridge_timeSignature(xmlpart)
			elif xmlpart.tag == 'tempo': self.tempo = soundbridge_tempo(xmlpart)
			elif xmlpart.tag == 'marker': self.markers.append(soundbridge_marker(xmlpart))

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, 'timeline')
		self.timeSignature.write(tempxml)
		self.tempo.write(tempxml)
		for x in self.markers: x.write(tempxml)

# --------------------------------------------------------- TIMELINE ---------------------------------------------------------

class soundbridge_song:
	def __init__(self):
		self.name = ""
		self.version = 1
		self.revision = 0
		self.sampleRate = 44100
		self.sampleFormat = 5
		self.tempo = 140
		self.timesigNumerator = 4
		self.timesigDenominator = 4

		self.pool = soundbridge_pool(None)
		self.masterTrack = soundbridge_track(None)
		self.masterTrack.tag = 'masterTrack'
		self.videoTrack = soundbridge_videotrack(None)
		self.videoTrack.tag = 'videoTrack'
		self.videoTrack.blocks = []
		self.timeline = soundbridge_timeline()
		self.metadata = {}
		self.metadata["SequencerHorizontalZoom"] = "85.435113"
		self.metadata["SequencerMarkerRadius"] = "7"
		self.metadata["SequencerTrackControlsWidth"] = "220"
		self.metadata["SequencerVerticalZoom"] = "1.948717"
		self.metadata["SequencerWaveformScale"] = "1.000000"
		self.metadata["TrackColor"] = "#91b0ff"
		self.metadata["TransportCount"] = "false"
		self.metadata["TransportFollow"] = "false"
		self.metadata["TransportLoop"] = "false"
		self.metadata["TransportMetronome"] = "false"
		self.metadata["TransportPlayPositionL"] = "0"
		self.metadata["TransportPlayPositionR"] = "88200"
		self.metadata["TransportSnap"] = "true"
		self.metadata["TransportSnapIndex"] = "2"

	def load_from_file(self, input_file):
		self.metadata = {}
		parser = ET.XMLParser(recover=True, encoding='utf-8')
		xml_data = ET.parse(input_file, parser)
		xml_proj = xml_data.getroot()
		if xml_proj == None: raise ProjectFileParserException('temper: no XML root found')

		projattrib = xml_proj.attrib

		if 'name' in projattrib: self.name = xml_proj.get("name")
		if 'version' in projattrib: self.version = int(xml_proj.get("version"))
		if 'revision' in projattrib: self.revision = int(xml_proj.get("revision"))
		if 'sampleRate' in projattrib: self.sampleRate = int(xml_proj.get("sampleRate"))
		if 'sampleFormat' in projattrib: self.sampleFormat = int(xml_proj.get("sampleFormat"))
		if 'tempo' in projattrib: self.tempo = int(xml_proj.get("tempo"))
		if 'timesigNumerator' in projattrib: self.timesigNumerator = int(xml_proj.get("timesigNumerator"))
		if 'timesigDenominator' in projattrib: self.timesigDenominator = int(xml_proj.get("timesigDenominator"))

		for xmlpart in xml_proj:
			if xmlpart.tag == 'pool': self.pool = soundbridge_pool(xmlpart)
			elif xmlpart.tag == 'masterTrack': self.masterTrack = soundbridge_track(xmlpart)
			elif xmlpart.tag == 'videoTrack': self.videoTrack = soundbridge_videotrack(xmlpart)
			elif xmlpart.tag == 'metaData': self.metadata = metadata_to_dict(xmlpart)
			elif xmlpart.tag == 'timeline': self.timeline.read(xmlpart)

		return True

	def write_to_file(self, output_file):
		xml_proj = ET.Element("project")

		xml_proj.set('name', str(self.name))
		xml_proj.set('version', str(self.version))
		xml_proj.set('revision', str(self.revision))
		xml_proj.set('sampleRate', str(self.sampleRate))
		xml_proj.set('sampleFormat', str(self.sampleFormat))
		xml_proj.set('tempo', str(self.tempo))
		xml_proj.set('timesigNumerator', str(self.timesigNumerator))
		xml_proj.set('timesigDenominator', str(self.timesigDenominator))

		if self.pool: self.pool.write(xml_proj)
		if self.masterTrack: self.masterTrack.write(xml_proj)
		if self.videoTrack: self.videoTrack.write(xml_proj)
		dict_to_metadata(self.metadata, xml_proj)
		self.timeline.write(xml_proj)

		outfile = ET.ElementTree(xml_proj)
		ET.indent(outfile, space="    ", level=0)
		outfile.write(output_file, encoding='utf-8', xml_declaration = True)

#test_obj = soundbridge_song()
#test_obj.load_from_file('daw.soundbridge\\project.xml')
#test_obj.write_to_file('project_out.xml')