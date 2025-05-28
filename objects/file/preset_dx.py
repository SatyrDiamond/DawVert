# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter

class dx_preset:
	def __init__(self):
		self.id = ''
		self.data = b''

	def read_file(self, fxfile):
		byr_stream = self.byr_stream = bytereader.bytereader()
		byr_stream.load_file(fxfile)
		self.parse(byr_stream)

	def read_raw(self, bytesd):
		byr_stream = self.byr_stream = bytereader.bytereader()
		byr_stream.load_raw(bytesd)
		self.parse(byr_stream)

	def parse(self, byr_stream):
		self.id = byr_stream.raw(16).hex()
		dsize = byr_stream.uint32()
		self.data = byr_stream.raw(dsize)

	def write(self, byw_stream):
		byw_stream.raw(bytes.fromhex(self.id))
		byw_stream.uint32(len(self.data))
		byw_stream.raw(self.data)

	def write_to_file(self, output_file):
		byw_stream = bytewriter.bytewriter()
		self.write(byw_stream)
		f = open(output_file, 'wb')
		f.write(byw_stream.getvalue())

	def write_to_raw(self):
		byw_stream = bytewriter.bytewriter()
		self.write(byw_stream)
		return byw_stream.getvalue()
