# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
from objects.data_bytes import bytereader
from functions import data_bytes

class track_tempo:
	def __init__(self): 
		self.name = ''
		self.tempo = 120
		self.events = []

	def load(self, song_file): 
		self.name = song_file.string(15)
		self.tempo = song_file.float()
		self.events = [[song_file.uint16(), song_file.float()] for _ in range(song_file.uint16())]

class track_voice:
	def __init__(self): 
		self.name = ''
		self.events = []

	def load(self, song_file): 
		self.name = song_file.string(15)
		nTicks = song_file.uint16()
		curtickpos = 0
		while curtickpos < nTicks: 
			value = song_file.uint16()
			deltatime = song_file.uint16()
			curtickpos += deltatime
			self.events.append([value, deltatime])

class track_timbre:
	def __init__(self): 
		self.name = ''
		self.events = []

	def load(self, song_file): 
		self.name = song_file.string(15)
		numevents = song_file.uint16()
		for _ in range(numevents):
			timbre_pos = song_file.uint16()
			timbre_name = song_file.string(9)
			song_file.skip(3)
			self.events.append([timbre_pos, timbre_name])

class track_float:
	def __init__(self): 
		self.name = ''
		self.events = []

	def load(self, song_file): 
		self.name = song_file.string(15)
		numevents = song_file.uint16()
		self.events = [[song_file.uint16(), song_file.float()] for _ in range(numevents)]

class adlib_rol_track:
	def __init__(self): 
		self.voice = track_voice()
		self.timbre = track_timbre()
		self.volume = track_float()
		self.pitch = track_float()

	def load(self, song_file): 
		self.voice.load(song_file)
		self.timbre.load(song_file)
		self.volume.load(song_file)
		self.pitch.load(song_file)

class adlib_rol_project:
	def __init__(self): 
		self.majorVersion = 0
		self.minorVersion = 4
		self.tickBeat = 8
		self.beatMeasure = 4
		self.scaleY = 48
		self.scaleX = 48
		self.isMelodic = 0
		self.cTicks = (0,0,0,0,0,0,0,0,0,0,0)
		self.cTimbreEvents = (0,0,0,0,0,0,0,0,0,0,0)
		self.cVolumeEvents = (0,0,0,0,0,0,0,0,0,0,0)
		self.cPitchEvents = (0,0,0,0,0,0,0,0,0,0,0)
		self.cPitchEvents = (0,0,0,0,0,0,0,0,0,0,0)
		self.cTempoEvents = 4
		self.track_tempo = track_tempo()
		self.tracks = [adlib_rol_track() for _ in range(10)]

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)
		self.majorVersion = song_file.uint16()
		self.minorVersion = song_file.uint16()
		
		try: 
			song_file.magic_check(b'\\roll\\default\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		except ValueError as t:
			raise ProjectFileParserException('adlib_rol: '+str(t))

		self.tickBeat = song_file.uint16()
		self.beatMeasure = song_file.uint16()
		self.scaleY = song_file.uint16()
		self.scaleX = song_file.uint16()

		song_file.skip(1)
		self.isMelodic = song_file.uint8()

		self.cTicks = song_file.l_uint16(11)
		self.cTimbreEvents = song_file.l_uint16(11)
		self.cVolumeEvents = song_file.l_uint16(11)
		self.cPitchEvents = song_file.l_uint16(11)

		self.cTempoEvents = song_file.uint16()

		song_file.skip(38)
		self.track_tempo.load(song_file)

		for tracknum in range(10): 
			self.tracks[tracknum].load(song_file)
		return True