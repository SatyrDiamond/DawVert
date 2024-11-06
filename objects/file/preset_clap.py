# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter

class clap_preset:
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
		byr_stream.magic_check(b'clap')
		self.id = byr_stream.c_string__int32(True)
		self.data = byr_stream.rest()

	def write(self, byw_stream):
		byw_stream.raw(b'clap')
		byw_stream.c_string__int32_b(self.id)
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
