# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
#from objects.data_bytes import bytewriter
from objects.file_proj_past._cakewalk_wrk import chunks

class cakewalk_wrk_file:
	def __init__(self):
		self.version = 0

	def load_from_file(self, input_file):
		byr_stream = bytereader.bytereader()
		byr_stream.load_file(input_file)

		byr_stream.magic_check(b'CAKEWALK\x1a\x00')
		self.version = byr_stream.uint8()

		self.chunks = []
		while byr_stream.remaining():
			chunk = chunks.cakewalk_wrk_chunk(byr_stream)
			self.chunks.append(chunk)
		return True

	def viewchunks(self, input_file):
		byr_stream = bytereader.bytereader()
		byr_stream.load_file(input_file)

		byr_stream.magic_check(b'CAKEWALK\x1a\x00')
		self.version = byr_stream.uint8()

		while byr_stream.remaining():
			self.id = byr_stream.uint8()
			if self.id != 255: 
				csize = byr_stream.uint32()
				name = '?? Unknown ?? '
				if self.id in chunks.chunkids: name = chunks.chunkids[self.id]
				if self.id in chunks.chunkobjects: name = chunks.chunkids[self.id]

				name = ('# ' if self.id in chunks.chunkobjects else '  ') + name
				data = byr_stream.raw(csize)
				print(str(self.id).rjust(4), '|', name.ljust(32), data)


	#def write_to_file(self, output_file):
	#	byw_stream = bytewriter.bytewriter()
#
	#	byw_stream.raw(b'CAKEWALK\x1a\x00')
	#	byw_stream.uint8(self.version)
#
	#	f = open(output_file, 'wb')
	#	f.write(byw_stream.getvalue())
