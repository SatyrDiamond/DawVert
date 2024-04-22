# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import struct
from io import BytesIO
from functions import data_bytes

class vst3_main:
	def __init__(self):
		self.version = 1
		self.uuid = '00000000000000000000000000000000'
		self.data = b''

	def read_file(self, fxfile):
		bio_in = open(fxfile, 'rb')
		self.parse(bio_in)

	def parse(self, bio_in):
		if bio_in.read(4) != b'VST3': exit('[error] VST3 magic mismatch')
		self.version, self.uuid, size = struct.unpack('I32sIxxxx', bio_in.read(44))
		self.data = bio_in.read(size)

	def write(self):
		return b'VST3'+struct.pack('I32sIxxxx', self.version, self.uuid, len(self.data))+self.data