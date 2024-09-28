# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
from objects.data_bytes import bytereader
import xml.etree.ElementTree as ET
import zipfile

def getvalue(xmltag, xmlname, fallbackval): 
	if xmltag.findall(xmlname) != []: return xmltag.findall(xmlname)[0].text.strip()
	else: return fallbackval

class audiosauna_sample_cell:
	def __init__(self, xt_device):
		self.name = getvalue(xt_device, 'name', '') 
		self.url = getvalue(xt_device, 'url', '') 
		self.semitone = float(getvalue(xt_device, 'semitone', '0')) 
		self.finetone = float(getvalue(xt_device, 'finetone', '0')) 
		self.volume = float(getvalue(xt_device, 'volume', '100')) 
		self.pan = float(getvalue(xt_device, 'pan', '0') )
		self.smpStart = float(getvalue(xt_device, 'smpStart', '0'))
		self.smpEnd = float(getvalue(xt_device, 'smpEnd', '100')) 
		self.loopStart = float(getvalue(xt_device, 'loopStart', '0')) 
		self.loopEnd = float(getvalue(xt_device, 'loopEnd', '100')) 
		self.loopMode = getvalue(xt_device, 'loopMode', 'off') 
		self.playMode = getvalue(xt_device, 'playMode', 'forward') 
		self.loKey = int(getvalue(xt_device, 'loKey', '48'))
		self.hiKey = int(getvalue(xt_device, 'hiKey', '48'))
		self.rootKey = int(getvalue(xt_device, 'rootKey', '48'))

class audiosauna_device:
	def __init__(self, xt_device):
		self.deviceType = int(xt_device.get('deviceType'))
		self.visible = xt_device.get('visible') == 'true'
		self.xpos = int(xt_device.get('xpos'))
		self.ypos = int(xt_device.get('ypos'))
		self.childIndex = int(xt_device.get('childIndex'))
		self.samples = {}
		self.params = {}
		d_sound = xt_device.findall('sound')
		if d_sound:
			for param in d_sound[0]: self.params[param.tag] = param.text

		d_sampler = xt_device.findall('sampler')
		if d_sampler:
			for param in d_sampler[0]: 
				if param.tag != 'samples': self.params[param.tag] = param.text
				else:
					for x_cell in param: 
						cell_id = int(x_cell.get('id'))
						self.samples[cell_id] = audiosauna_sample_cell(x_cell)

class audiosauna_note:
	__slots__ = ['startTick', 'endTick', 'noteLength', 'pitch', 'selected', 'patternId', 'noteVolume', 'noteCutoff']
	def __init__(self, xt_note):
		self.startTick = int(xt_note.get('startTick'))
		self.endTick = int(xt_note.get('endTick'))
		self.noteLength = int(xt_note.get('noteLength'))
		self.pitch = int(xt_note.get('pitch'))
		self.selected = xt_note.get('selected') == 'true'
		self.patternId = int(xt_note.get('patternId'))
		self.noteVolume = int(xt_note.get('noteVolume'))
		self.noteCutoff = int(xt_note.get('noteCutoff'))

class audiosauna_pattern:
	__slots__ = ['trackNro', 'patternId', 'patternColor', 'startTick', 'endTick', 'patternLength', 'selected']
	def __init__(self, xt_pattern):
		self.trackNro = int(xt_pattern.get('trackNro'))
		self.patternId = int(xt_pattern.get('patternId'))
		self.patternColor = int(xt_pattern.get('patternColor'))
		self.startTick = int(xt_pattern.get('startTick'))
		self.endTick = int(xt_pattern.get('endTick'))
		self.patternLength = int(xt_pattern.get('patternLength'))
		self.selected = xt_pattern.get('selected') == 'true'

class audiosauna_track:
	def __init__(self, xt_track):
		self.trackIndex = int(xt_track.get('trackIndex'))
		self.deviceType = int(xt_track.get('deviceType'))
		self.noteCount = int(xt_track.get('noteCount'))
		self.notes = {}
		for indata in xt_track:
			if indata.tag == 'seqNote': 
				note = audiosauna_note(indata)
				if note.patternId not in self.notes: self.notes[note.patternId] = []
				self.notes[note.patternId].append(note)

class audiosauna_channel:
	def __init__(self, xt_channel):
		self.channelNro = int(xt_channel.get('channelNro'))
		self.volume = int(xt_channel.get('volume'))
		self.pan = int(xt_channel.get('pan'))
		self.delay = int(xt_channel.get('delay'))
		self.reverb = int(xt_channel.get('reverb'))
		self.mute = xt_channel.get('mute') == 'true'
		self.solo = xt_channel.get('solo') == 'true'
		self.name = xt_channel.get('name')
		self.track = None
		self.device = None
		self.patterns = []

class audiosauna_song:
	def __init__(self):
		pass

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)

		try:
			zip_data = zipfile.ZipFile(input_file, 'r')
		except zipfile.BadZipFile as t:
			raise ProjectFileParserException('audiosauna: Bad ZIP File: '+str(t))
		
		as_songdata = zip_data.read('songdata.xml')

		x_proj = ET.fromstring(as_songdata)
		x_proj_channels = x_proj.findall('channels')[0]
		x_proj_tracks = x_proj.findall('tracks')[0]
		x_proj_songPatterns = x_proj.findall('songPatterns')[0]
		x_proj_devices = x_proj.findall('devices')[0]

		self.mixerVisible = getvalue(x_proj, 'mixerVisible', 'true') == 'true'
		self.appArrangeToolMode = int(getvalue(x_proj, 'appArrangeToolMode', '1'))
		self.appPianoRollToolMode = int(getvalue(x_proj, 'appPianoRollToolMode', '1'))
		self.appFocusMode = int(getvalue(x_proj, 'appFocusMode', '0'))
		self.appPlayHeadPosition = int(getvalue(x_proj, 'appPlayHeadPosition', '128'))
		self.appSongLength = int(getvalue(x_proj, 'appSongLength', '256'))
		self.appSongEnd = int(getvalue(x_proj, 'appSongEnd', '4096'))
		self.appPianoRollSnap = int(getvalue(x_proj, 'appPianoRollSnap', '16'))
		self.appNoteWidth = int(getvalue(x_proj, 'appNoteWidth', '25'))
		self.appNoteHeight = int(getvalue(x_proj, 'appNoteHeight', '15'))
		self.appVOffset = int(getvalue(x_proj, 'appVOffset', '551'))
		self.appHOffset = int(getvalue(x_proj, 'appHOffset', '100'))
		self.appPatternWidth = int(getvalue(x_proj, 'appPatternWidth', '4'))
		self.appPatternHeight = int(getvalue(x_proj, 'appPatternHeight', '40'))
		self.appVOffsetArrange = int(getvalue(x_proj, 'appVOffsetArrange', '0'))
		self.appHOffsetArrange = int(getvalue(x_proj, 'appHOffsetArrange', '0'))
		self.appLoopStart = int(getvalue(x_proj, 'appLoopStart', '0'))
		self.appLoopEnd = int(getvalue(x_proj, 'appLoopEnd', '32'))
		self.appUseLoop = getvalue(x_proj, 'appUseLoop', 'true') == 'true'
		self.appCurrentEnd = int(getvalue(x_proj, 'appCurrentEnd', '32'))
		self.appFmSynthCount = int(getvalue(x_proj, 'appFmSynthCount', '1'))
		self.appVaSynthCount = int(getvalue(x_proj, 'appVaSynthCount', '1'))
		self.appSamplerCount = int(getvalue(x_proj, 'appSamplerCount', '1'))
		self.appPatternCount = int(getvalue(x_proj, 'appPatternCount', '2'))
		self.appActivePatternId = int(getvalue(x_proj, 'appActivePatternId', '2'))
		self.appActiveTrackIndex = int(getvalue(x_proj, 'appActiveTrackIndex', '2'))
		self.appMasterVolume = int(getvalue(x_proj, 'appMasterVolume', '86'))
		self.appTempo = int(getvalue(x_proj, 'appTempo', '120'))
		self.dlyTime = int(getvalue(x_proj, 'dlyTime', '11'))
		self.dlyDamage = int(getvalue(x_proj, 'dlyDamage', '0'))
		self.dlyFeed = int(getvalue(x_proj, 'dlyFeed', '70'))
		self.dlyLevel = int(getvalue(x_proj, 'dlyLevel', '100'))
		self.dlySync = getvalue(x_proj, 'dlySync', 'true') == 'true'
		self.rvbTime = float(getvalue(x_proj, 'rvbTime', '0'))
		self.rvbFeed = int(getvalue(x_proj, 'rvbFeed', '90'))
		self.rvbLevel = int(getvalue(x_proj, 'rvbLevel', '100'))
		self.rvbWidth = int(getvalue(x_proj, 'rvbWidth', '100'))

		self.channels = {}
		xt_channels = x_proj_channels.findall('channel')
		for xt_channel in xt_channels:
			channel_data = audiosauna_channel(xt_channel)
			self.channels[channel_data.channelNro] = channel_data

		xt_tracks = x_proj_tracks.findall('track')
		for xt_track in xt_tracks:
			track_data = audiosauna_track(xt_track)
			self.channels[track_data.trackIndex].track = track_data

		xt_patterns = x_proj_songPatterns.findall('pattern')
		for xt_pattern in xt_patterns:
			pattern_data = audiosauna_pattern(xt_pattern)
			self.channels[pattern_data.trackNro].patterns.append(pattern_data)

		xt_devices = x_proj_devices.findall('audioDevice')
		for num, xt_device in enumerate(xt_devices):
			self.channels[num].device = audiosauna_device(xt_device)

		return zip_data
