# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter

class vst3_main:
	def __init__(self):
		self.version = 1
		self.uuid = '00000000000000000000000000000000'
		self.data = b''

	def read_file(self, fxfile):
		byr_stream = self.byr_stream = bytereader.bytereader()
		byr_stream.load_file(fxfile)
		self.parse(byr_stream)

	def parse(self, byr_stream):
		byr_stream.magic_check(b'VST3')
		self.version = byr_stream.uint32()
		self.uuid = byr_stream.string(32)
		size = byr_stream.uint32()
		byr_stream.skip(4)
		self.data = byr_stream.raw(size)

	def write(self, byw_stream):
		byw_stream.raw(b'VST3')
		byw_stream.uint32(self.version)
		byw_stream.string(self.uuid, 32)
		byw_stream.uint32(len(self.data))
		byw_stream.zeros(4)
		byw_stream.raw(self.data)

	def write_to_file(self, output_file):
		byw_stream = bytewriter.bytewriter()
		self.write(byw_stream)
		f = open(output_file, 'wb')
		f.write(byw_stream.getvalue())
