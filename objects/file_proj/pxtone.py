# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects.data_bytes import structalloc
from objects.exceptions import ProjectFileParserException
import numpy as np
import struct
import logging

logger_projparse = logging.getLogger('projparse')

class ptcop_delay:
	def __init__(self):
		self.delay_voice = 0
		self.delay_group = 0
		self.delay_rate = 0
		self.delay_freq = 0

class ptcop_overdrive:
	def __init__(self):
		self.xxx = 0
		self.group = 0
		self.cut = 0
		self.amp = 0
		self.yyy = 0

class ptcop_voice:
	def __init__(self):
		self.type = None
		self.name = ''

		self.ch = None
		self.bits = None
		self.basic_key_field = 60
		self.sps2 = None
		self.key_correct = None
		self.samples = None
		self.hz = None
		self.channels = None
		self.data = None

class ptcop_unit:
	def __init__(self):
		self.name = None

event_premake = structalloc.dynarray_premake([
	('position', np.uint32),
	('unitnum', np.uint8),
	('eventnum', np.uint8),
	('value', np.uint32),
	('d_position', np.uint32),
	])

class ptcop_song:
	def __init__(self):
		self.comment = ''
		self.title = ''
		self.events = event_premake.create()
		self.units = []
		self.voices = {}
		self.delays = []
		self.overdrives = []

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)

		self.header = song_file.raw(16)

		song_file.skip(4)

		voicenum = 0

		while song_file.end>song_file.tell():
			chunk_id = song_file.raw(8)
			chunk_size = song_file.uint32()

			if chunk_id == b'MasterV5':
				self.unk1 = song_file.uint16()
				self.beat = song_file.uint8()
				self.unk2 = song_file.uint16()
				self.beattempo = struct.unpack(">f", struct.pack("I", int.from_bytes(song_file.read(2), "big")))[0]
				self.repeat = song_file.uint32()
				self.last = song_file.uint32()
			elif chunk_id == b'Event V5':
				for _ in range(song_file.uint32()):
					self.events.add()
					self.events['position'] = song_file.varint()
					self.events['unitnum'] = song_file.uint8()
					self.events['eventnum'] = song_file.uint8()
					self.events['value'] = song_file.varint()
			elif chunk_id == b'effeDELA':
				song_file.skip(2)
				delay_obj = ptcop_delay()
				delay_obj.unit = song_file.uint16()
				delay_obj.group = song_file.uint16()
				delay_obj.rate = song_file.uint16()
				delay_obj.freq = song_file.float()
				self.delays.append(delay_obj)
			elif chunk_id == b'effeOVER':
				overdrive_obj = ptcop_overdrive()
				overdrive_obj.xxx = song_file.uint16()
				overdrive_obj.group = song_file.uint16()
				overdrive_obj.cut = song_file.float()
				overdrive_obj.amp = song_file.float()
				overdrive_obj.yyy = song_file.float()
				self.overdrives.append(overdrive_obj)
			elif chunk_id == b'mateOGGV':
				voice_obj = ptcop_voice()
				song_file.skip(3)
				voice_obj.type = 'ogg'
				voice_obj.basic_key_field = song_file.uint8()
				voice_obj.sps2 = song_file.flags32()
				voice_obj.key_correct = song_file.float()
				voice_obj.channels = song_file.uint32()
				voice_obj.hz = song_file.uint32()
				voice_obj.samples = song_file.uint32()
				voice_obj.data = song_file.raw(song_file.uint32())
				self.voices[voicenum] = voice_obj
				voicenum += 1
			elif chunk_id == b'matePCM ':
				voice_obj = ptcop_voice()
				song_file.skip(3)
				voice_obj.type = 'pcm'
				voice_obj.basic_key_field = song_file.uint8()
				voice_obj.sps2 = song_file.flags32()
				voice_obj.ch = song_file.uint16()
				voice_obj.bits = song_file.uint16()
				voice_obj.hz = song_file.uint32()
				voice_obj.key_correct = song_file.float()
				voice_obj.samples = song_file.uint32()//(voice_obj.bits//8)
				voice_obj.data = song_file.raw((voice_obj.bits//8) * voice_obj.samples)
				self.voices[voicenum] = voice_obj
				voicenum += 1
			elif chunk_id == b'matePTV ':
				voice_obj = ptcop_voice()
				voice_obj.type = 'ptvoice'
				song_file.skip(4)
				voice_obj.key_correct = song_file.float()
				datasize = song_file.uint32()
				voice_obj.data = song_file.raw(datasize)
				self.voices[voicenum] = voice_obj
				voicenum += 1
			elif chunk_id == b'matePTN ':
				voice_obj = ptcop_voice()
				voice_obj.type = 'ptnoise'
				song_file.skip(8)
				voice_obj.key_correct = song_file.float()
				song_file.skip(4)
				voice_obj.data = song_file.raw(chunk_size-16)
				self.voices[voicenum] = voice_obj
				voicenum += 1
			elif chunk_id == b'assiWOIC':
				voice_num = song_file.uint32()
				self.voices[voice_num].name = song_file.string(chunk_size-4, encoding="shift-jis")
			elif chunk_id == b'assiUNIT':
				unit_num = song_file.uint32()
				self.units[unit_num].name = song_file.string(chunk_size-4, encoding="shift-jis")
			elif chunk_id == b'num UNIT':
				self.units = [ptcop_unit() for _ in range(song_file.uint32())]
			elif chunk_id == b'textCOMM':
				self.comment = song_file.string(chunk_size, encoding="shift-jis")
			elif chunk_id == b'textNAME':
				self.title = song_file.string(chunk_size, encoding="shift-jis")
			elif chunk_id == b'pxtoneND':
				break
			else: raise ProjectFileParserException('pxtone: unknown chunk: '+str(chunk_id))

		self.events.clean()

		return True

	def postprocess(self):
		curpos = 0
		for x in self.events:
			curpos += x['position']
			x['d_position'] = curpos