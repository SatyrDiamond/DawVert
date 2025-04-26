# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import json

class coolbeat_auto_main:
	def __init__(self, indata):
		self.state = False
		self.sections = []
		if indata is not None: self.read(indata)

	def read(self, indata):
		if 'state' in indata: self.state = indata['state']
		if 'sections' in indata: self.sections = [coolbeat_auto_section(x) for x in indata['sections']]

class coolbeat_auto_section:
	def __init__(self, indata):
		self.startTick = 0
		self.length = 0
		self.nodes = []
		if indata is not None: self.read(indata)

	def read(self, indata):
		if 'startTick' in indata: self.startTick = indata['startTick']
		if 'length' in indata: self.length = indata['length']
		if 'nodes' in indata: self.nodes = [coolbeat_auto_node(x) for x in indata['nodes']]

class coolbeat_auto_node:
	def __init__(self, indata):
		self.position = 0
		self.value = 0
		if indata is not None: self.read(indata)

	def read(self, indata):
		if 'position' in indata: self.position = indata['position']
		if 'value' in indata: self.value = indata['value']

# --------------------------------------------------------- TRACK ---------------------------------------------------------

class coolbeat_track:
	def __init__(self, indata):
		self.type = 0
		self.label = ""
		self.volume = 0.5
		self.pan = 0.5
		self.muteState = 0
		self.solo = False
		self.showingAuto = True
		self.currentAutoIndex = 0
		self.scTrackIndex = -1
		self.fileName = ""
		self.soundPack = ""
		self.isSample = False
		self.param = []
		self.sections = []
		self.autos = []
		self.fx = []
		self.fxState = []
		self.tempo = 0
		self.channels = []
		self.filePath = ""
		self.presetIndex = 0
		self.pitchRange = 1
		if indata is not None: self.read(indata)

	def read(self, indata):
		if 'type' in indata: self.type = indata['type']
		if 'label' in indata: self.label = indata['label']
		if 'volume' in indata: self.volume = indata['volume']
		if 'pan' in indata: self.pan = indata['pan']
		if 'muteState' in indata: self.muteState = indata['muteState']
		if 'solo' in indata: self.solo = indata['solo']
		if 'showingAuto' in indata: self.showingAuto = indata['showingAuto']
		if 'currentAutoIndex' in indata: self.currentAutoIndex = indata['currentAutoIndex']
		if 'scTrackIndex' in indata: self.scTrackIndex = indata['scTrackIndex']
		if 'fileName' in indata: self.fileName = indata['fileName']
		if 'soundPack' in indata: self.soundPack = indata['soundPack']
		if 'isSample' in indata: self.isSample = indata['isSample']
		if 'sections' in indata: self.sections = [coolbeat_section(x) for x in indata['sections']]
		if 'autos' in indata: self.autos = [coolbeat_auto_main(x) for x in indata['autos']]
		if 'tempo' in indata: self.tempo = indata['tempo']
		if 'channels' in indata: self.channels = [coolbeat_track_channel(x) for x in indata['channels']]
		if 'filePath' in indata: self.filePath = indata['filePath']
		if 'presetIndex' in indata: self.presetIndex = indata['presetIndex']
		if 'pitchRange' in indata: self.pitchRange = indata['pitchRange']

class coolbeat_section:
	def __init__(self, indata):
		self.startTick = 0
		self.length = 0
		self.startOffsetTick = 0
		self.endOffsetTick = 0
		self.notes = []
		self.label = ""
		if indata is not None: self.read(indata)

	def read(self, indata):
		if 'startTick' in indata: self.startTick = indata['startTick']
		if 'length' in indata: self.length = indata['length']
		if 'startOffsetTick' in indata: self.startOffsetTick = indata['startOffsetTick']
		if 'endOffsetTick' in indata: self.endOffsetTick = indata['endOffsetTick']
		if 'notes' in indata: self.notes = [coolbeat_note(x) for x in indata['notes']]
		if 'label' in indata: self.label = indata['label']

class coolbeat_note:
	def __init__(self, indata):
		self.startTick = 0
		self.length = 120
		self.key = 67
		self.volume = 1
		if indata is not None: self.read(indata)

	def read(self, indata):
		if 'startTick' in indata: self.startTick = indata['startTick']
		if 'length' in indata: self.length = indata['length']
		if 'key' in indata: self.key = indata['key']
		if 'volume' in indata: self.volume = indata['volume']

class coolbeat_track_channel:
	def __init__(self, indata):
		self.fileName = ""
		self.soundPack = "BasicSoundPack"
		self.volume = 1
		self.pan = 0.5
		if indata is not None: self.read(indata)

	def read(self, indata):
		if 'fileName' in indata: self.fileName = indata['fileName']
		if 'soundPack' in indata: self.soundPack = indata['soundPack']
		if 'volume' in indata: self.volume = indata['volume']
		if 'pan' in indata: self.pan = indata['pan']

# --------------------------------------------------------- MAIN ---------------------------------------------------------

class coolbeat_root:
	def __init__(self):
		self.version = 4
		self.tempo = 120
		self.timeSigType = 0
		self.masterVolume = 0.5
		self.masterPan = 0.5
		self.masterAutos = []
		self.tracks = []

	def load_from_file(self, input_file):
		f = open(input_file, 'rb')
		projectdata = json.load(f)
		self.read(projectdata)
		return True

	def read(self, indata):
		self.__init__()
		if 'version' in indata: self.version = indata['version']
		if 'tempo' in indata: self.tempo = indata['tempo']
		if 'timeSigType' in indata: self.timeSigType = indata['timeSigType']
		if 'masterVolume' in indata: self.masterVolume = indata['masterVolume']
		if 'masterPan' in indata: self.masterPan = indata['masterPan']
		if 'masterAutos' in indata: self.masterAutos = [coolbeat_auto_main(x) for x in indata['masterAutos']]
		if 'tracks' in indata: self.tracks = [coolbeat_track(x) for x in indata['tracks']]