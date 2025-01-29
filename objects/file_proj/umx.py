# SPDX-FileCopyrightText: 2024 SatyrDiamond and B0ney
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
import logging
from objects.exceptions import ProjectFileParserException

MINIMUM_VERSION = 61

def get_entry(version, song_file):
	if version < 64: return song_file.string_t()
	else: return song_file.c_string__int8()

# https://wiki.beyondunreal.com/Legacy:Package_File_Format/Data_Details
def read_compact_index(song_file):
	output = 0
	signed = False

	for i in range(5):
		x = song_file.uint8()

		if i == 0:
			if (x & 0x80) > 0: signed = True
			output |= x & 0x3F
			if x & 0x40 == 0: break

		elif i == 4:
			output |= (x & 0x1F) << (6 + (3 * 7))
		else:
			output |= (x & 0x7F) << (6 + ((i - 1) * 7))
			if x & 0x80 == 0: break

	if signed: output *= -1

	return output

class umx_file:
	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)

		try: song_file.magic_check(b'\xc1\x83\x2a\x9e')
		except ValueError as t: raise ProjectFileParserException('umx: '+str(t))

		self.version = song_file.uint32()

		if self.version < MINIMUM_VERSION: raise ProjectFileParserException("umx: UMX versions below {MINIMUM_VERSION} are not supported")

		song_file.skip(4)
		name_count = song_file.uint32()
		name_offset = song_file.uint32()
		song_file.skip(4)
		export_offset = song_file.uint32()

		song_file.seek(name_offset) # Jump to the name table

		self.nametable = []
		for _ in range(name_count):
			self.nametable.append(get_entry(self.version, song_file))
			song_file.skip(4)

		song_file.seek(export_offset)
	
		self.classindex = read_compact_index(song_file)
		self.superindex = read_compact_index(song_file)
		self.group = song_file.uint32()
		self.objname = read_compact_index(song_file)
		self.objflags = song_file.flags32()

		serial_size = read_compact_index(song_file)

		if serial_size == 0: raise ProjectFileParserException("umx: UMX doesn't contain anything")
		
		serial_offset = read_compact_index(song_file)
		song_file.seek(serial_offset)  
		self.nameindex = read_compact_index(song_file)
	
		if self.version > MINIMUM_VERSION: song_file.skip(4)
	
		objsizefield = read_compact_index(song_file)
		inner_size = read_compact_index(song_file)
		self.outdata = song_file.raw(inner_size)

		return True