# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class cakewalk_event:
	def __init__(self):
		self.time = 0
		self.type = None
		self.data = None

	def read_old(self, byr_stream):
		self.time = byr_stream.uint24()
		self.type = byr_stream.uint8()
		self.type = self.type & 0xf0
		channel = self.type & 0x0f
		data1 = byr_stream.uint8()
		data2 = byr_stream.uint8()
		dur = byr_stream.uint16()
		if self.type == 0x90: self.data = cakewalk_event_note(channel, data1, data2, dur)
		elif self.type == 0xA0: self.data = cakewalk_event_key_press(channel, data1, data2)
		elif self.type == 0xB0: self.data = cakewalk_event_control(channel, data1, data2)
		elif self.type == 0xC0: self.data = cakewalk_event_program(channel, data1)
		elif self.type == 0xD0: self.data = cakewalk_event_pressure(channel, data1)
		elif self.type == 0xE0: self.data = cakewalk_event_pitch(channel, data1, data2)
		elif self.type == 0xF0: self.data = cakewalk_event_sysex_id(data1)

	def read_new(self, byr_stream):
		self.time = byr_stream.uint24()
		self.type = byr_stream.uint8()

		if (self.type >= 0x90):
			self.type = self.type & 0xf0
			channel = self.type & 0x0f
			data1 = byr_stream.uint8()
			if (self.type == 0x90 or self.type == 0xA0  or self.type == 0xB0 or self.type == 0xE0):
				data2 = byr_stream.uint8()
			if (self.type == 0x90):
				dur = byr_stream.uint16()

			if self.type == 0x90: self.data = cakewalk_event_note(channel, data1, data2, dur)
			elif self.type == 0xA0: self.data = cakewalk_event_key_press(channel, data1, data2)
			elif self.type == 0xB0: self.data = cakewalk_event_control(channel, data1, data2)
			elif self.type == 0xC0: self.data = cakewalk_event_program(channel, data1)
			elif self.type == 0xD0: self.data = cakewalk_event_pressure(channel, data1)
			elif self.type == 0xE0: self.data = cakewalk_event_pitch(channel, data1, data2)
			elif self.type == 0xF0: self.data = cakewalk_event_sysex_id(data1)

		elif (self.type == 2):
			data = byr_stream.c_raw__int32(False)
			self.data = cakewalk_event_lyrics(data)

		elif (self.type == 5):
			code = byr_stream.uint16()
			data = byr_stream.c_raw__int32(False)
			self.data = cakewalk_event_expression(code, data)

		elif (self.type == 6):
			code = byr_stream.uint16()
			dur = byr_stream.uint16()
			byr_stream.skip(4)
			self.data = cakewalk_event_hairpin(code, dur)

		elif (self.type == 7):
			text = byr_stream.c_raw__int32()
			data = byr_stream.l_uint8(12)
			self.data = cakewalk_event_chord(text, data)

		elif (self.type == 8):
			self.data = cakewalk_event_sysex(byr_stream.c_raw__int16(False))

		elif (self.type == 4):
			self.data = cakewalk_event_audioclip()
			self.data.unk1 = byr_stream.uint32()
			self.data.unk2 = byr_stream.uint32()
			self.data.name = byr_stream.c_raw__int32(False)
			self.data.unk3 = byr_stream.raw(4)
			self.data.id = byr_stream.raw(4)

		else:
			self.data = cakewalk_event_data(byr_stream.c_raw__int32(False))


class cakewalk_event_note:
	def __init__(self, channel, data1, data2, dur):
		self.channel = channel
		self.data1 = data1
		self.data2 = data2
		self.dur = dur

	#def write_old(self, byw_stream):
	#	byw_stream.uint8(0x90+self.channel)
	#	byw_stream.uint8(self.data1)
	#	byw_stream.uint8(self.data2)
	#	byw_stream.uint16(self.dur)

class cakewalk_event_key_press:
	def __init__(self, channel, data1, data2):
		self.channel = channel
		self.data1 = data1
		self.data2 = data2

	#def write_old(self, byw_stream):
	#	byw_stream.uint8(0xA0+self.channel)
	#	byw_stream.uint8(self.data1)
	#	byw_stream.uint8(self.data2)
	#	byw_stream.uint16(0)

class cakewalk_event_control:
	def __init__(self, channel, data1, data2):
		self.channel = channel
		self.data1 = data1
		self.data2 = data2

	#def write_old(self, byw_stream):
	#	byw_stream.uint8(0xB0+self.channel)
	#	byw_stream.uint8(self.data1)
	#	byw_stream.uint8(self.data2)
	#	byw_stream.uint16(0)

class cakewalk_event_program:
	def __init__(self, channel, data1):
		self.channel = channel
		self.data1 = data1

	#def write_old(self, byw_stream):
	#	byw_stream.uint8(0xC0+self.channel)
	#	byw_stream.uint8(self.data1)
	#	byw_stream.uint8(0)
	#	byw_stream.uint16(0)

class cakewalk_event_pressure:
	def __init__(self, channel, data1):
		self.channel = channel
		self.data1 = data1

	#def write_old(self, byw_stream):
	#	byw_stream.uint8(0xD0+self.channel)
	#	byw_stream.uint8(self.data1)
	#	byw_stream.uint8(0)
	#	byw_stream.uint16(0)

class cakewalk_event_pitch:
	def __init__(self, channel, data1, data2):
		self.channel = channel
		self.data1 = data1
		self.data2 = data2

	#def write_old(self, byw_stream):
	#	byw_stream.uint8(0xE0+self.channel)
	#	byw_stream.uint8(self.data1)
	#	byw_stream.uint8(self.data2)
	#	byw_stream.uint16(0)

class cakewalk_event_sysex_id:
	def __init__(self, data1):
		self.data1 = data1

	#def write_old(self, byw_stream):
	#	byw_stream.uint8(0xF0)
	#	byw_stream.uint8(self.data1)
	#	byw_stream.uint8(0)
	#	byw_stream.uint16(0)

class cakewalk_event_expression:
	def __init__(self, code, data):
		self.code = code
		self.data = data

class cakewalk_event_hairpin:
	def __init__(self, code, dur):
		self.code = code
		self.dur = dur

class cakewalk_event_chord:
	def __init__(self, text, data):
		self.text = text
		self.data = data

class cakewalk_event_sysex:
	def __init__(self, data):
		self.data = data

class cakewalk_event_data:
	def __init__(self, data):
		self.data = data

class cakewalk_event_lyrics:
	def __init__(self, data):
		self.data = data

class cakewalk_event_audioclip:
	def __init__(self):
		self.unk1 = 0
		self.unk2 = 0
		self.name = ''
		self.unk3 = 0
		self.id = 0