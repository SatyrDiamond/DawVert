# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
from functions import data_bytes

class track_tempo:
	def __init__(self, file_stream): 
		if file_stream != None:
			self.name = data_bytes.readstring_fixedlen(file_stream, 15, 'ascii')
			self.tempo, numevents = struct.unpack("fH", file_stream.read(6))
			self.events = [struct.unpack("<Hf", file_stream.read(6)) for _ in range(numevents)]
		else:
			self.name = ''
			self.tempo = 120
			self.events = []

class track_voice:
	def __init__(self, file_stream): 
		self.events = []
		if file_stream != None:
			self.name = data_bytes.readstring_fixedlen(file_stream, 15, 'ascii')
			nTicks = int.from_bytes(file_stream.read(2), 'little')
			curtickpos = 0
			while curtickpos < nTicks: 
				rol_note_data = struct.unpack("HH", file_stream.read(4))
				self.events.append(rol_note_data)
				curtickpos += rol_note_data[1]
		else:
			self.name = ''

class track_timbre:
	def __init__(self, file_stream): 
		self.events = []
		if file_stream != None:
			self.name = data_bytes.readstring_fixedlen(file_stream, 15, 'ascii')
			numevents = int.from_bytes(file_stream.read(2), 'little')
			for _ in range(numevents):
				timbre_pos = int.from_bytes(file_stream.read(2), 'little')
				timbre_name = data_bytes.readstring_fixedlen(file_stream, 9, 'ascii')
				file_stream.read(3)
				self.events.append([timbre_pos, timbre_name])
		else:
			self.name = ''

class track_float:
	def __init__(self, file_stream): 
		if file_stream != None:
			self.name = data_bytes.readstring_fixedlen(file_stream, 15, 'ascii')
			numevents = int.from_bytes(file_stream.read(2), 'little')
			self.events = [struct.unpack("<Hf", file_stream.read(6)) for _ in range(numevents)]
		else:
			self.name = ''
			self.events = []

class adlib_rol_track:
	def __init__(self, file_stream): 
		self.voice = track_voice(file_stream)
		self.timbre = track_timbre(file_stream)
		self.volume = track_float(file_stream)
		self.pitch = track_float(file_stream)

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
		self.track_tempo = track_tempo(None)
		self.tracks = []

	def load_from_file(self, input_file):
		song_file = open(input_file, 'rb')
		self.majorVersion, self.minorVersion = struct.unpack("HH", song_file.read(4))
		if song_file.read(40) != b'\\roll\\default\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
			exit('[error] magic mismatch')
		self.tickBeat, self.beatMeasure, self.scaleY, self.scaleX = struct.unpack("HHHH", song_file.read(8))
		song_file.read(1)
		self.isMelodic = song_file.read(1)[0]

		self.cTicks = struct.unpack(">HHHHHHHHHHH", song_file.read(22))
		self.cTimbreEvents = struct.unpack(">HHHHHHHHHHH", song_file.read(22))
		self.cVolumeEvents = struct.unpack(">HHHHHHHHHHH", song_file.read(22))
		self.cPitchEvents = struct.unpack(">HHHHHHHHHHH", song_file.read(22))
		self.cTempoEvents = struct.unpack(">H", song_file.read(2))[0]
		song_file.read(38)
		self.track_tempo = track_tempo(song_file)
		for tracknum in range(10): self.tracks.append(adlib_rol_track(song_file))