# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
from functions import data_bytes
from objects.data_bytes import bytewriter

def il_vst_chunk(i_outdata, i_type, i_data): 
	i_outdata.uint32(i_type)
	i_outdata.uint32(len(i_data))
	i_outdata.uint32(0)
	i_outdata.raw(i_data)

class imageline_vststate():
	def __init__(self): 
		self.headertype = 0

		self.startchunk_data = b''

		self.otherp1_data = [-1 for _ in range(128)]
		self.otherp2_data = [-1 for _ in range(16)]
		self.otherp3_data = [-1 for _ in range(16)]

		self.state_data = b''

		self.preset_name = 'Default'

	def read(self, f):
		f.read(5)
		self.headertype = int.from_bytes(f.read(4), 'little')

		#chunk start
		startchunk_size = int.from_bytes(f.read(4), 'little')
		self.startchunk_data = f.read(startchunk_size)[12:]
		if self.headertype != 4: 
			assert f.read(4) == b'\x01\x00\x00\x00'
			self.preset_name = data_bytes.readstring_fixedlen(f, 20, 'utf8')
			f.read(4)

		#chunk other
		assert f.read(4) == b'\x01\x00\x00\x00'
		otherchunk_size = int.from_bytes(f.read(4), 'little')
		f.read(4)
		end_pos = f.tell() + otherchunk_size
		while end_pos > f.tell():
			ctype = int.from_bytes(f.read(4), 'little')
			csize = int.from_bytes(f.read(4), 'little')
			f.read(4)
			cdata = f.read(csize)
			if ctype == 1: self.otherp1_data = struct.unpack('i'*128, cdata)
			if ctype == 2: self.otherp2_data = struct.unpack('i'*16, cdata)
			if ctype == 3: self.otherp3_data = struct.unpack('i'*16, cdata)

		f.read(4)
		if self.headertype in [1,4]:
			state_size = int.from_bytes(f.read(4), 'little')
			self.state_data = f.read(state_size)
		else:
			state_size = -1
			self.state_data = f.read()

	def write(self):
		outdata = bytewriter.bytewriter()
		outdata.raw(b'\xfa\xff\xff\x7f\x01')
		outdata.uint32(self.headertype)
		outdata.uint32(len(self.startchunk_data)+12)
		il_vst_chunk(outdata, 5, self.startchunk_data)
		if self.headertype != 4: 
			outdata.raw(b'\x01\x00\x00\x00')
			outdata.string(self.preset_name, 20)
			outdata.raw(b'\x00\x00\x00\x00')

		subdata = bytewriter.bytewriter()
		il_vst_chunk(subdata, 1, struct.pack('i'*128, *self.otherp1_data))
		il_vst_chunk(subdata, 2, struct.pack('i'*16, *self.otherp2_data))
		il_vst_chunk(subdata, 3, struct.pack('i'*16, *self.otherp3_data))

		il_vst_chunk(outdata, 1, subdata.getvalue())
		outdata.raw(b'\x00\x00\x00\x00')

		if self.headertype in [1,4]:
			outdata.uint32(len(self.state_data))
			outdata.raw(self.state_data)
		else:
			outdata.raw(self.state_data)

		return outdata.getvalue()
