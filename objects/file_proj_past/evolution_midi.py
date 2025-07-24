# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
import zlib
import logging

class evo_midi_event:
	def __init__(self, byr_stream):
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.unk1 = byr_stream.uint8()
		self.pos = byr_stream.uint16_b()
		self.type, self.chan = byr_stream.bytesplit()
		self.data = []
		if self.type == 9: #note
			self.data.append(byr_stream.uint8())
			self.data.append(byr_stream.uint8())
			self.data.append(byr_stream.uint16_b())
		elif self.type == 10: #aftertouch
			self.data.append(byr_stream.uint8())
			self.data.append(byr_stream.uint8())
		elif self.type == 11: #control
			self.data.append(byr_stream.uint8())
			self.data.append(byr_stream.uint8())
		elif self.type == 12: #unknown
			self.data.append(byr_stream.uint8())
		elif self.type == 13: #pressure
			self.data.append(byr_stream.uint8())
		elif self.type == 14: #pitch
			self.data.append(byr_stream.uint8())
			self.data.append(byr_stream.uint8())
		elif self.type == 15: #end
			pass
		else:
			print('unknown event', self.type)
			exit()

class evo_midi_track:
	def __init__(self, byr_stream):
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.name = byr_stream.string(21, encoding='windows-1252')
		self.patch = byr_stream.int16()
		self.bank = byr_stream.int8()
		self.bank_type = byr_stream.int8()
		self.channel = byr_stream.int16()
		byr_stream.skip(2)
		self.volume = byr_stream.int16()
		self.pan = byr_stream.int16()
		self.reverb = byr_stream.int16()
		self.chorus = byr_stream.int16()
		self.velocity = byr_stream.int16()
		self.transpose = byr_stream.int16()
		self.time = byr_stream.int16()
		self.mute = byr_stream.int16()
		self.solo = byr_stream.int16()
		self.armed = byr_stream.int16()

		self.unkdata = byr_stream.raw(6)
		byr_stream.skip(500)
		self.unkdata2 = byr_stream.raw(10)

class evo_midi_clip:
	def __init__(self, byr_stream):
		self.name = ''
		self.linked = -1
		self.patch = -1
		self.bank = -1
		self.bank_type = -1
		self.channel = -1
		self.volume = -1
		self.pan = -1
		self.reverb = -1
		self.chorus = -1
		self.velocity = -1
		self.transpose = -1
		self.time = -1
		self.position = 0
		self.duration = 0
		self.events_size = 0
		self.tracknum = 0
		self.events = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.name = byr_stream.string(21, encoding='windows-1252')
		unknowns = []
		self.linked = byr_stream.int16()
		self.patch = byr_stream.int16()
		self.bank = byr_stream.int8()
		self.bank_type = byr_stream.int8()
		self.channel = byr_stream.int16()
		byr_stream.skip(2)
		self.volume = byr_stream.int16()
		self.pan = byr_stream.int16()
		self.reverb = byr_stream.int16()
		self.chorus = byr_stream.int16()
		self.velocity = byr_stream.int16()
		self.transpose = byr_stream.int16()
		self.time = byr_stream.int16()
		unknowns.append(byr_stream.int16())
		unknowns.append(byr_stream.uint32())
		unknowns.append(byr_stream.int16())
		self.position = byr_stream.uint32()
		self.duration = byr_stream.uint32()
		self.events_size = byr_stream.int32()
		self.tracknum = byr_stream.int16()
		unknowns.append(byr_stream.raw(10).hex())

class evo_midi_song:
	def __init__(self):
		self.tracks = []
		self.clips = []

	def load_from_file(self, input_file):
		byr_stream = bytereader.bytereader()
		byr_stream.load_file(input_file)
		byr_stream.magic_check(b'sng2')

		byr_stream.skip(3)

		num_tracks = byr_stream.uint16()
		num_clips = byr_stream.uint16()
		num_unk = byr_stream.uint8()

		byr_stream.seek(0x400)
		self.songinfo = byr_stream.string_t(encoding='windows-1252')

		assert num_unk>1
		byr_stream.skip((num_unk*6)-3)

		self.unk1 = byr_stream.uint16()

		self.unklist2 = byr_stream.l_uint16(num_tracks)
		self.unklist3 = byr_stream.l_uint16(num_clips)


		for x in range(num_tracks):
			self.tracks.append( evo_midi_track(byr_stream) )

		for x in range(num_clips):
			self.clips.append( evo_midi_clip(byr_stream) )

		for clip in self.clips:
			if clip.linked == -1:
				with byr_stream.isolate_size(clip.events_size, True) as bye_stream:
					while bye_stream.remaining():
						clip.events.append(evo_midi_event(bye_stream))

		return True