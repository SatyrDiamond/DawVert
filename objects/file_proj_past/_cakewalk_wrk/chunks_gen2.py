# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj_past._cakewalk_wrk import events
from objects.file_proj_past._cakewalk_wrk import chunks

class cakewalk_effect:
	def __init__(self, byr_stream):
		self.id = None
		self.name = ''
		self.unk1 = 1
		self.unk2 = 1
		self.data = b''
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.id = byr_stream.raw(16)
		self.name = byr_stream.string(128)
		self.unk1 = byr_stream.uint32()
		self.unk2 = byr_stream.uint32()
		datasize = byr_stream.uint32()
		self.data = byr_stream.raw(datasize)

	#def write(self, byw_stream):
	#	byw_stream.raw_l(self.id, 16)
	#	byw_stream.string(self.name, 128)
	#	byw_stream.uint32(self.unk1)
	#	byw_stream.uint32(self.unk2)
	#	byw_stream.uint32(len(self.data))
	#	byw_stream.raw(self.data)




class chunk_gen2_track_header:
	def __init__(self, byr_stream):
		self.trackno = 0
		self.name = ''
		self.bank = -1
		self.patch = 0
		self.vol = 0
		self.pan = 0
		self.key = 0
		self.vel = 0
		self.port = -1
		self.channel = 0
		self.muted = True
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.trackno = byr_stream.uint16()
		self.name = byr_stream.c_raw__int8()
		self.bank = byr_stream.int16()
		self.patch = byr_stream.uint16()
		self.vol = byr_stream.uint16()
		self.pan = byr_stream.int16()
		self.key = byr_stream.int8()
		self.vel = byr_stream.uint8()
		byr_stream.skip(7) # b'\x00\x00\x00\x00\x00\x81\x00'
		self.port = byr_stream.int8()
		self.channel = byr_stream.uint8()
		self.muted = byr_stream.uint8() != 0

	#def write(self, byw_stream):
	#	byr_stream.uint16(self.trackno) 
	#	byw_stream.c_string__int8(self.name)
	#	byr_stream.int16(self.bank) 
	#	byr_stream.uint16(self.patch) 
	#	byr_stream.uint16(self.vol) 
	#	byr_stream.int16(self.pan) 
	#	byr_stream.int8(self.key) 
	#	byr_stream.uint8(self.vel) 
	#	byr_stream.raw(b'\x00\x00\x00\x00\x00\x81\x00')
	#	byr_stream.int8(self.port) 
	#	byr_stream.uint8(self.channel) 
	#	byr_stream.uint8(self.muted) 

class chunk_gen2_track_events:
	def __init__(self, byr_stream):
		self.trackno = 0
		self.events = []
		self.name = b''
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.trackno = byr_stream.uint16()
		self.name = byr_stream.c_raw__int8()
		numevents = byr_stream.uint32()
		for _ in range(numevents):
			event = events.cakewalk_event()
			event.read_new(byr_stream)
			self.events.append(event)

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.c_string__int8(self.name)
	#	byw_stream.uint32(len(self.events))
	#	for x in self.events: x.write_new(byw_stream)

class chunk_gen2_track_effects:
	def __init__(self, byr_stream):
		self.trackno = 0
		self.effects = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.trackno = byr_stream.uint32()
		num_fx = byr_stream.uint32()
		for _ in range(num_fx): cakewalk_effect(byr_stream)

	#def write(self, byw_stream):
	#	byw_stream.uint32(self.trackno)
	#	byw_stream.uint32(len(self.effects))
	#	for x in self.effects: x.write(byw_stream)

class chunk_gen2_track_segment:
	def __init__(self, byr_stream):
		self.trackno = 0
		self.offset = 0
		self.events = []
		self.name = b''
		self.id = 0
		self.is_nonlinked = 1
		self.color = None
		self.other3 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.trackno = byr_stream.uint16()
		self.offset = byr_stream.uint32()
		self.id = byr_stream.uint32()
		self.is_nonlinked = byr_stream.uint32()
		if self.is_nonlinked:
			self.name = byr_stream.c_raw__int8()
			self.color = byr_stream.l_uint8(3)
			self.other3 = byr_stream.raw(17)
			numevents = byr_stream.uint32()
			for _ in range(numevents):
				event = events.cakewalk_event()
				event.read_new(byr_stream)
				self.events.append(event)

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.uint32(self.offset)
	#	byw_stream.uint32(self.id)
	#	byw_stream.uint32(self.is_nonlinked)
	#	if self.is_nonlinked:
	#		byw_stream.c_string__int8(self.name)
	#		byw_stream.l_uint8(self.color)
	#		byw_stream.raw_l(self.other2, 17)
	#		byw_stream.uint32(len(self.events))
	#		for x in self.events: x.write_new(byw_stream)

class chunk_gen2_audiosource:
	def __init__(self, byr_stream):
		self.data = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.data = byr_stream.l_uint32(byr_stream.remaining()//4)

	#def write(self, byw_stream):
	#	byr_stream.l_uint32(self.data)

class chunk_gen2_midichans:
	def __init__(self, byr_stream):
		self.data = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.data = byr_stream.l_uint32(byr_stream.remaining()//4)

	#def write(self, byw_stream):
	#	byr_stream.l_uint32(self.data)

#class chunk_gen2_track_audiostretch:
#	def __init__(self, byr_stream):
#		self.data = []
#		if byr_stream: self.read(byr_stream)

	#def read(self, byr_stream):
	#	self.unkdata = []
	#	self.tracknum = byr_stream.uint32()
	#	self.unkdata.append( byr_stream.uint32() )
	#	self.unkdata.append( byr_stream.uint32() )
	#	self.unkdata.append( byr_stream.uint8() )
	#	self.unkdata.append( byr_stream.uint8() )
	#	self.pos = byr_stream.uint32()
	#	self.unkdata.append( byr_stream.uint16() )
	#	self.unkdata.append( byr_stream.uint32() )
	#	self.offset = byr_stream.double()
	#	self.unkdata.append( byr_stream.uint32() )
	#	self.seconds = byr_stream.double()
	#	self.id = byr_stream.raw(16).hex()
	#	self.unkdata.append( byr_stream.raw(4).hex() )
	#	self.name = byr_stream.c_raw__int8()
	#	self.unkdata.append( byr_stream.raw(4).hex() )
	#	self.unkdata.append( byr_stream.uint32() )
	#	self.unkdata.append( byr_stream.raw(8).hex() )
	#	self.unkdata.append( byr_stream.raw(8).hex() )
	#	self.unkdata.append( byr_stream.raw(16).hex() )
	#	self.unkdata = []
	#	typesomething = byr_stream.uint16()





		#somethingdata = []
		#self.unkdata.append( byr_stream.uint16() )
#
#
		#if typesomething == 1:
		#	somethingdata.append( list(byr_stream.l_uint8(4)) )
#
		#	somethingdata.append( byr_stream.uint32() )
		#	somethingdata.append( byr_stream.uint32() )
		#	somethingdata.append( byr_stream.uint32() )
		#	somethingdata.append( byr_stream.uint32() )
		#	numsomething = byr_stream.uint16()
		#	somethingdata.append( numsomething )
		#	remainingest = byr_stream.remaining()/38
		#	somethingdata.append( remainingest )
#
#
		#self.unkdata.append( somethingdata )









		#self.color = byr_stream.l_uint8(4)



		#self.unkdata.append( byr_stream.uint32() )
		#self.unkdata.append( byr_stream.c_raw__int8() )
		#print(self.id, self.unkdata)

		#self.unkdata.append( byr_stream.raw(32) )
		#if byr_stream.remaining(): self.unkdata.append( byr_stream.raw(32) )
#
		#self.unkdata.append(['REMAIGINING', byr_stream.remaining()] )
		#self.unkdata.append( byr_stream.raw(32).hex() )
		#print( byr_stream.raw(byr_stream.remaining()).hex() )

		#self.data = byr_stream.raw(byr_stream.remaining())
		#print(self.unkdata)
		#print()
		#print()

	#def write(self, byw_stream):
	#	byr_stream.l_uint32(self.data)

#class chunk_gen2_consoleparams:
#	def __init__(self, byr_stream):
#		self.data = []
#		if byr_stream: self.read(byr_stream)
#
#	def read(self, byr_stream):
#		numparams = byr_stream.uint32()
#		print(numparams)
#		for x in range(numparams):
#			print(byr_stream.raw(8).hex())
#
#		print(byr_stream.rest())

	#def write(self, byw_stream):
	#	byr_stream.l_uint32(self.data)
