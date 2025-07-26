# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj_past._cakewalk_wrk import events
from objects.file_proj_past._cakewalk_wrk import chunks

class gen3_track_evn_part:
	def __init__(self, byr_stream):
		self.headerdata = []
		self.envdata = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		time1 = byr_stream.uint16()
		time2 = byr_stream.uint16()
		self.headerdata.append( time2+(time1/65535) )
		self.headerdata.append( byr_stream.uint8() )
		self.headerdata.append( byr_stream.uint8() )
		self.headerdata.append( byr_stream.int16() )
		self.cmdnum, self.channum = byr_stream.bytesplit()

		if self.cmdnum == 0 and self.channum == 4:
			self.envdata.append( byr_stream.uint8() )
			self.envdata.append( byr_stream.uint8() )
			self.envdata.append( byr_stream.uint8() )
			self.envdata.append( byr_stream.raw(4).hex() )
			self.envdata.append( byr_stream.uint8() )
			d = byr_stream.uint32()
			self.envdata.append( byr_stream.raw(d) )
			self.envdata.append( byr_stream.uint32() )
			self.envdata.append( byr_stream.raw(4).hex() )
		elif self.cmdnum == 6: # rpn
			self.envdata.append( byr_stream.uint32() )
			self.envdata.append( byr_stream.uint32() )
			self.envdata.append( byr_stream.uint32() )
		elif self.cmdnum == 7: # nrpn
			self.envdata.append( byr_stream.uint32() )
			self.envdata.append( byr_stream.uint32() )
			self.envdata.append( byr_stream.uint32() )
		elif self.cmdnum == 9: # note
			self.envdata.append( byr_stream.uint32() )
			self.envdata.append( byr_stream.uint32() )
			self.envdata.append( byr_stream.uint32() )
			self.envdata.append( byr_stream.uint32() )
			self.envdata.append( byr_stream.uint32() )
			self.envdata.append( byr_stream.uint32() )
			self.envdata.append( byr_stream.uint32() )
		elif self.cmdnum == 11: # control
			self.envdata.append( byr_stream.uint32() )
			self.envdata.append( byr_stream.uint32() )
		elif self.cmdnum == 14: # wheel
			self.envdata.append( byr_stream.uint32() )
		elif self.cmdnum == 13: # aftertouch
			self.envdata.append( byr_stream.uint32() )
		else:
			print('unknown event ', self.channum, channum)
			exit()

		#print('part', self.headerdata, self.envdata)

class chunk_gen3_track_events:
	def __init__(self, byr_stream):
		self.parts = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.unkdata = []
		self.tracknum = byr_stream.uint32()
		self.unkdata.append( byr_stream.uint32() )
		self.unkdata.append( byr_stream.uint32() )
		self.unkdata.append( byr_stream.uint8() )
		self.unkdata.append( byr_stream.uint8() )
		self.pos = byr_stream.uint32()
		self.unkdata.append( byr_stream.uint16() )
		self.unkdata.append( byr_stream.uint32() )
		self.offset = byr_stream.double()
		self.unkdata.append( byr_stream.uint32() )
		self.seconds = byr_stream.double()
		self.id = byr_stream.raw(16).hex()
		self.unkdata.append( byr_stream.raw(4).hex() )
		self.name = byr_stream.c_raw__int8()
		self.unkdata.append( byr_stream.raw(4).hex() )
		self.unkdata.append( byr_stream.uint32() )
		self.unkdata.append( byr_stream.raw(8).hex() )
		self.unkdata.append( byr_stream.raw(8).hex() )
		self.unkdata.append( byr_stream.raw(16).hex() )

		self.unkdata.append( byr_stream.uint32() )
		self.unkdata.append( byr_stream.int32() )
		self.unkdata.append( byr_stream.uint32() )
		self.unkdata.append( byr_stream.uint32() )
		self.unkdata.append( byr_stream.uint32() )
		self.unkdata.append( byr_stream.uint32() )

		num_something = byr_stream.uint32()

		for x in range(num_something):
			self.parts.append(gen3_track_evn_part(byr_stream))

	def viewchunks(byr_stream):

		print( 'tracknum', byr_stream.uint32() )
		print( '?', byr_stream.uint32() )
		print( '?', byr_stream.uint32() )
		print( '?', byr_stream.uint8() )
		print( '?', byr_stream.uint8() )
		print( 'pos', byr_stream.uint32() )
		print( '?', byr_stream.uint16() )
		print( '?', byr_stream.uint32() )
		print( 'offset', byr_stream.double() )
		print( '?', byr_stream.uint32() )
		print( 'seconds', byr_stream.double() )
		print( 'id', byr_stream.raw(16).hex() )
		print( '?', byr_stream.raw(4).hex() )
		print( 'name', byr_stream.c_raw__int8() )
		print( '?', byr_stream.raw(4).hex() )
		print( '?', byr_stream.uint32() )
		print( '?', byr_stream.raw(8).hex() )
		print( '?', byr_stream.raw(8).hex() )
		print( '?', byr_stream.raw(16).hex() )

		print( '?', byr_stream.uint32() )
		print( '?', byr_stream.int32() )
		print( '?', byr_stream.uint32() )
		print( '?', byr_stream.uint32() )
		print( '?', byr_stream.uint32() )
		print( '?', byr_stream.uint32() )

		num_something = byr_stream.uint32()

		for x in range(num_something):
			T = gen3_track_evn_part(byr_stream)

			print(T.headerdata, T.envdata)