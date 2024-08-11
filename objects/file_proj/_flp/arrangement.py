# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import struct
from io import BytesIO

def calcaudiopos(i_value):
	i_out = (i_value)/125
	return i_out

def calcaudiopos_enc(i_value):
	i_out = i_value*125
	return i_out

class flp_arrangement_clip:
	def __init__(self):
		self.position = 0
		self.patternbase = 20480
		self.itemindex = 20480
		self.length = 384
		self.trackindex = 499
		self.unknown1 = 120
		self.flags = 64
		self.unknown2 = 2155897920
		self.id = -1
		self.f_in_dur = 0
		self.f_in_tens = 0
		self.f_out_dur = 0
		self.f_out_tens = 0
		self.vol = 1
		self.fade_flags = b''
		self.startoffset = 4294967295
		self.endoffset = 4294967295


	def read(self, event_bio, version_split):
		self.position, self.patternbase, self.itemindex, self.length, self.trackindex, self.unknown1, self.flags, self.unknown2 = struct.unpack('IHHIIHHI', event_bio.read(24))

		startoffset_bytes = event_bio.read(4)
		endoffset_bytes = event_bio.read(4)

		ifextraarr = 0
		if version_split[0] == 20 and version_split[1] >= 99: ifextraarr = 1
		elif version_split[0] > 20: ifextraarr = 1

		if ifextraarr == 1:
			self.id, self.f_in_dur, self.f_in_tens, self.f_out_dur, self.f_out_tens, self.vol = struct.unpack('Ifffff', event_bio.read(24))
			self.fade_flags = event_bio.read(4)
		else:
			self.id = -1
			self.f_in_dur, self.f_in_tens, self.f_out_dur, self.f_out_tens, self.vol, = 0,0,0,0,1
			self.fade_flags = b''

		startoffset = int.from_bytes(startoffset_bytes, "little")
		endoffset = int.from_bytes(endoffset_bytes, "little")
		startoffset_float = struct.unpack('<f', startoffset_bytes)[0]
		endoffset_float = struct.unpack('<f', endoffset_bytes)[0]

		if self.itemindex > self.patternbase:
			if startoffset != 4294967295 and startoffset != 3212836864: self.startoffset = startoffset
			if endoffset != 4294967295 and endoffset != 3212836864: self.endoffset = endoffset
		else:
			self.startoffset = calcaudiopos(startoffset_float)
			self.endoffset = calcaudiopos(endoffset_float)


	def write(self):
		BytesIO_arrangement = BytesIO()

		BytesIO_arrangement.write(self.position.to_bytes(4, 'little'))
		BytesIO_arrangement.write(self.patternbase.to_bytes(2, 'little'))
		BytesIO_arrangement.write(int(self.itemindex).to_bytes(2, 'little'))
		BytesIO_arrangement.write(int(self.length).to_bytes(4, 'little'))
		BytesIO_arrangement.write(self.trackindex.to_bytes(4, 'little'))
		BytesIO_arrangement.write(self.unknown1.to_bytes(2, 'little'))
		BytesIO_arrangement.write(self.flags.to_bytes(2, 'little'))
		BytesIO_arrangement.write(self.unknown2.to_bytes(4, 'little'))

		if self.itemindex > self.patternbase:
			BytesIO_arrangement.write(self.startoffset.to_bytes(4, 'little'))
			BytesIO_arrangement.write(self.endoffset.to_bytes(4, 'little'))
		else:
			BytesIO_arrangement.write(struct.pack('<f', calcaudiopos_enc(self.startoffset)))
			BytesIO_arrangement.write(struct.pack('<f', calcaudiopos_enc(self.endoffset)))

		BytesIO_arrangement.seek(0)

		return BytesIO_arrangement.read()

class flp_arrangement:
	def __init__(self):
		self.tracks = {}
		self.items = []
		self.timemarkers = []
		self.name = None

		for x in range(1,501):
			self.tracks[x] = flp_track()
			self.tracks[x].id = x

class flp_track:
	def __init__(self):
		self.id = 0
		self.color = 5656904
		self.icon = 0
		self.enabled = 1
		self.height = 1.0
		self.lockedtocontent = 255
		self.motion = 16777215
		self.press = 0
		self.triggersync = 0
		self.queued = 5
		self.tolerant = 0
		self.positionSync = 1
		self.grouped = 0
		self.locked = 0
		self.name = ''
		
	def read(self, event_bio, event_len, version_split):
		if event_len >= 44: 
			self.id, self.color, self.icon, self.enabled, self.height, self.lockedtocontent, self.motion, self.press, self.triggersync, self.queued, self.tolerant, self.positionSync, self.grouped, self.locked = struct.unpack('<IIIBfBIIIIIIBB', event_bio.read(44))

	def write(self):
		return struct.pack('<IIIBfBIIIIIIBB', self.id, self.color, self.icon, self.enabled, self.height, self.lockedtocontent, self.motion, self.press, self.triggersync, self.queued, self.tolerant, self.positionSync, self.grouped, self.locked) + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\x01\x00\x00\x00\x00'


class flp_timemarker:
	def __init__(self):
		self.type = 0
		self.pos = 0
		self.name = ''
		self.numerator = 4
		self.denominator = 4
