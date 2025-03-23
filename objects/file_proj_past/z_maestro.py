# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import base64

def getbool(val): return val=='true'

def read_timeline(x_part):
	out = []
	for x_inpart in x_part:
		if x_inpart.tag == 'TimelineEvent':
			timelinee_obj = zmaestro_TimelineEvent()
			timelinee_obj.read(x_inpart)
			out.append(timelinee_obj)
	return out

class zmaestro_TimelineEvent:
	def __init__(self):
		self.value = 0
		self.position = 0
		self.fade = ''

	def read(self, xpart):
		attrib = xpart.attrib
		if 'Value' in attrib: self.value = float(attrib['Value'])
		if 'Position' in attrib: self.position = float(attrib['Position'])
		if 'Fade' in attrib: self.fade = attrib['Fade']

class zmaestro_Note:
	def __init__(self):
		self.pitch = 0
		self.velocity = 0
		self.length = 0
		self.start = 0

	def read(self, xpart):
		attrib = xpart.attrib
		if 'Pitch' in attrib: self.pitch = int(attrib['Pitch'])
		if 'Velocity' in attrib: self.velocity = float(attrib['Velocity'])
		if 'Length' in attrib: self.length = float(attrib['Length'])
		if 'Start' in attrib: self.start = float(attrib['Start'])

# ============================================= MIDIDrumTrack =============================================

class zmaestro_MIDIDrumPart:
	def __init__(self):
		self.name = ''
		self.start = 0
		self.length = 0
		self.repeats = 0
		self.id = ''
		self.notes = []

	def read(self, xpart):
		attrib = xpart.attrib
		if 'Name' in attrib: self.name = attrib['Name']
		if 'Start' in attrib: self.start = float(attrib['Start'])
		if 'Length' in attrib: self.length = float(attrib['Length'])
		if 'Repeats' in attrib: self.repeats = float(attrib['Repeats'])
		if 'Id' in attrib: self.id = attrib['Id']
		for x_part in xpart:
			if x_part.tag == 'Notes':
				for x_inpart in x_part:
					if x_inpart.tag == 'Note':
						note_obj = zmaestro_Note()
						note_obj.read(x_inpart)
						self.notes.append(note_obj)

class zmaestro_MIDIDrumTrack:
	def __init__(self):
		self.volume = 75
		self.usevolumetimeline = False
		self.pan = 50
		self.usepantimeline = False
		self.headphones = False
		self.name = ""
		self.icon = 'generic'
		self.instrumentcode = 0
		self.instrumentbank = 0
		self.soundfont = ''
		self.volumetimeline = []
		self.pantimeline = []
		self.parts = []

	def read(self, xpart):
		attrib = xpart.attrib
		if 'Volume' in attrib: self.volume = int(attrib['Volume'])
		if 'UseVolumeTimeline' in attrib: self.usevolumetimeline = getbool(attrib['UseVolumeTimeline'])
		if 'Pan' in attrib: self.pan = int(attrib['Pan'])
		if 'UsePanTimeline' in attrib: self.usepantimeline = getbool(attrib['UsePanTimeline'])
		if 'Headphones' in attrib: self.headphones = getbool(attrib['Headphones'])
		if 'Name' in attrib: self.name = attrib['Name']
		if 'Icon' in attrib: self.icon = attrib['Icon']
		if 'InstrumentCode' in attrib: self.instrumentcode = int(attrib['InstrumentCode'])
		if 'InstrumentBank' in attrib: self.instrumentbank = int(attrib['InstrumentBank'])
		if 'SoundFont' in attrib: self.soundfont = attrib['SoundFont']
 
		for x_part in xpart:
			if x_part.tag == 'VolumeTimeline': self.volumetimeline = read_timeline(x_part)
			if x_part.tag == 'PanTimeline': self.pantimeline = read_timeline(x_part)
			if x_part.tag == 'Parts': 
				for x_inpart in x_part:
					if x_inpart.tag == 'MIDIDrumPart':
						part_obj = zmaestro_MIDIPart()
						part_obj.read(x_inpart)
						self.parts.append(part_obj)

# ============================================= MIDITrack =============================================

class zmaestro_MIDIPart:
	def __init__(self):
		self.name = ''
		self.start = 0
		self.length = 0
		self.repeats = 0
		self.id = ''
		self.notes = []

	def read(self, xpart):
		attrib = xpart.attrib
		if 'Name' in attrib: self.name = attrib['Name']
		if 'Start' in attrib: self.start = float(attrib['Start'])
		if 'Length' in attrib: self.length = float(attrib['Length'])
		if 'Repeats' in attrib: self.repeats = float(attrib['Repeats'])
		if 'Id' in attrib: self.id = attrib['Id']
		for x_part in xpart:
			if x_part.tag == 'Notes':
				for x_inpart in x_part:
					if x_inpart.tag == 'Note':
						note_obj = zmaestro_Note()
						note_obj.read(x_inpart)
						self.notes.append(note_obj)

class zmaestro_MIDITrack:
	def __init__(self):
		self.volume = 75
		self.usevolumetimeline = False
		self.pan = 50
		self.usepantimeline = False
		self.headphones = False
		self.name = ""
		self.icon = 'generic'
		self.instrumentcode = 0
		self.instrumentbank = 0
		self.soundfont = ''
		self.volumetimeline = []
		self.pantimeline = []
		self.parts = []

	def read(self, xpart):
		attrib = xpart.attrib
		if 'Volume' in attrib: self.volume = int(attrib['Volume'])
		if 'UseVolumeTimeline' in attrib: self.usevolumetimeline = getbool(attrib['UseVolumeTimeline'])
		if 'Pan' in attrib: self.pan = int(attrib['Pan'])
		if 'UsePanTimeline' in attrib: self.usepantimeline = getbool(attrib['UsePanTimeline'])
		if 'Headphones' in attrib: self.headphones = getbool(attrib['Headphones'])
		if 'Name' in attrib: self.name = attrib['Name']
		if 'Icon' in attrib: self.icon = attrib['Icon']
		if 'InstrumentCode' in attrib: self.instrumentcode = int(attrib['InstrumentCode'])
		if 'InstrumentBank' in attrib: self.instrumentbank = int(attrib['InstrumentBank'])
		if 'SoundFont' in attrib: self.soundfont = attrib['SoundFont']
 
		for x_part in xpart:
			if x_part.tag == 'VolumeTimeline': self.volumetimeline = read_timeline(x_part)
			if x_part.tag == 'PanTimeline': self.pantimeline = read_timeline(x_part)
			if x_part.tag == 'Parts': 
				for x_inpart in x_part:
					if x_inpart.tag == 'MIDIPart':
						part_obj = zmaestro_MIDIPart()
						part_obj.read(x_inpart)
						self.parts.append(part_obj)

# ============================================= AudioTrack =============================================

class zmaestro_LiveAudioEffect:
	def __init__(self):
		self.type = ''
		self.params = {}

	def read(self, xpart):
		attrib = xpart.attrib
		typetxt = '{http://www.w3.org/2001/XMLSchema-instance}type'
		if typetxt in attrib: self.type = attrib[typetxt]
		for x_inpart in xpart: self.params[x_inpart.tag] = x_inpart.text

class zmaestro_AudioPart:
	def __init__(self):
		self.currenttempo = 120
		self.id = None
		self.length = 0
		self.name = ''
		self.oneshot = False
		self.originalfile = None
		self.recordedtempo = 120
		self.repeats = 0
		self.start = 0
		self.channels = None
		self.format = {}

	def read(self, xpart):
		attrib = xpart.attrib

		if 'CurrentTempo' in attrib: self.currenttempo = float(attrib['CurrentTempo'])
		if 'Id' in attrib: self.id = attrib['Id']
		if 'Length' in attrib: self.length = float(attrib['Length'])
		if 'Name' in attrib: self.name = attrib['Name']
		if 'OneShot' in attrib: self.oneshot = getbool(attrib['OneShot'])
		if 'OriginalFile' in attrib: self.originalfile = attrib['OriginalFile']
		if 'RecordedTempo' in attrib: self.recordedtempo = float(attrib['RecordedTempo'])
		if 'Repeats' in attrib: self.repeats = float(attrib['Repeats'])
		if 'Start' in attrib: self.start = float(attrib['Start'])

		for x_part in xpart:
			if x_part.tag == 'Channels': self.channels = base64.b64decode(x_part.text)
			if x_part.tag == 'Format': 
				for x_inpart in x_part:
					self.format[x_inpart.tag] = x_inpart.text

class zmaestro_AudioTrack:
	def __init__(self):
		self.volume = 75
		self.usevolumetimeline = False
		self.pan = 50
		self.usepantimeline = False
		self.headphones = False
		self.name = ""
		self.icon = 'generic'
		self.frequency = 1
		self.volumetimeline = []
		self.pantimeline = []
		self.parts = []
		self.fx = []

	def read(self, xpart):
		attrib = xpart.attrib
		if 'Volume' in attrib: self.volume = int(attrib['Volume'])
		if 'UseVolumeTimeline' in attrib: self.usevolumetimeline = getbool(attrib['UseVolumeTimeline'])
		if 'Pan' in attrib: self.pan = int(attrib['Pan'])
		if 'UsePanTimeline' in attrib: self.usepantimeline = getbool(attrib['UsePanTimeline'])
		if 'Headphones' in attrib: self.headphones = getbool(attrib['Headphones'])
		if 'Name' in attrib: self.name = attrib['Name']
		if 'Icon' in attrib: self.icon = attrib['Icon']
		if 'Frequency' in attrib: self.frequency = int(attrib['Frequency'])
 
		for x_part in xpart:
			if x_part.tag == 'VolumeTimeline': self.volumetimeline = read_timeline(x_part)
			if x_part.tag == 'PanTimeline': self.pantimeline = read_timeline(x_part)
			if x_part.tag == 'Parts': 
				for x_inpart in x_part:
					if x_inpart.tag == 'AudioPart':
						part_obj = zmaestro_AudioPart()
						part_obj.read(x_inpart)
						self.parts.append(part_obj)
			if x_part.tag == 'LiveEffects': 
				for x_inpart in x_part:
					if x_inpart.tag == 'LiveAudioEffect':
						fx_obj = zmaestro_LiveAudioEffect()
						fx_obj.read(x_inpart)
						self.fx.append(fx_obj)

# ============================================= MAIN =============================================

import gzip
import zipfile

class zmaestro_song:
	def __init__(self):
		self.tracks = []
		self.soundfonts = []
		self.compformat = None
		self.zipfile = None
		self.name = ''
		self.author = ''
		self.comments = ''
		self.tempo = 120
		self.key = 'C'
		self.loopstart = 0
		self.looplength = 0
		self.loopenabled = False
		self.version = 0
		self.usevolumetimeline = False
		self.usepantimeline = False
		self.volumetimeline = []
		self.pantimeline = []

	def load_from_file(self, input_file):
		headerfound = False

		if not headerfound:
			try:
				self.load_gzip(input_file)
				headerfound = True
				self.compformat = 'gz'
				return True
			except gzip.BadGzipFile: pass

		if not headerfound:
			try:
				self.load_pkzip(input_file)
				headerfound = True
				self.compformat = 'zip'
				return True
			except zipfile.BadZipFile: pass

		if not headerfound:
			self.parse_xml(ET.parse(input_file).getroot())
			return True

		return False

	def load_gzip(self, input_file):
		f = gzip.open(input_file, 'rb')
		file_content = f.read()
		self.parse_xml(ET.fromstring(file_content.decode()))

	def load_pkzip(self, input_file):
		self.zipfile = zipfile.ZipFile(input_file, 'r')
		if 'ZMaestroProject.xml' in self.zipfile.namelist():
			readdata = self.zipfile.read('ZMaestroProject.xml').decode()
			self.parse_xml(ET.fromstring(readdata))

	def parse_xml(self, x_root):
		attrib = x_root.attrib
		if 'Name' in attrib: self.name = attrib['Name']
		if 'Author' in attrib: self.author = attrib['Author']
		if 'Comments' in attrib: self.comments = attrib['Comments']
		if 'Tempo' in attrib: self.tempo = float(attrib['Tempo'])
		if 'Key' in attrib: self.key = attrib['Key']
		if 'LoopStart' in attrib: self.loopstart = float(attrib['LoopStart'])
		if 'LoopLength' in attrib: self.looplength = float(attrib['LoopLength'])
		if 'LoopEnabled' in attrib: self.loopenabled = getbool(attrib['LoopEnabled'])
		if 'Version' in attrib: self.version = int(attrib['Version'])
		if 'UseVolumeTimeline' in attrib: self.usevolumetimeline = getbool(attrib['UseVolumeTimeline'])
		if 'UsePanTimeline' in attrib: self.usepantimeline = getbool(attrib['UsePanTimeline'])

		for x_part in x_root:
			if x_part.tag == 'Tracks':
				for x_inpart in x_part:
					if x_inpart.tag == 'MIDITrack':
						track_obj = zmaestro_MIDITrack()
						track_obj.read(x_inpart)
						self.tracks.append(['MIDITrack', track_obj])
					if x_inpart.tag == 'MIDIDrumTrack':
						track_obj = zmaestro_MIDIDrumTrack()
						track_obj.read(x_inpart)
						self.tracks.append(['MIDIDrumTrack', track_obj])
					if x_inpart.tag == 'AudioTrack':
						track_obj = zmaestro_AudioTrack()
						track_obj.read(x_inpart)
						self.tracks.append(['AudioTrack', track_obj])
			if x_part.tag == 'VolumeTimeline': self.volumetimeline = read_timeline(x_part)
			if x_part.tag == 'PanTimeline': self.pantimeline = read_timeline(x_part)