# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
from functions import data_bytes

def il_vst_chunk(i_type, i_data): 
    return struct.pack('iii', i_type, len(i_data), 0)+i_data

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
		outdata = b'\xfa\xff\xff\x7f\x01'
		outdata += struct.pack('II', self.headertype, len(self.startchunk_data)+12 )
		outdata += il_vst_chunk(5, self.startchunk_data)
		if self.headertype != 4:  outdata += b'\x01\x00\x00\x00'+data_bytes.makestring_fixedlen(self.preset_name, 20)+b'\x00\x00\x00\x00'

		subdata = il_vst_chunk(1, struct.pack('i'*128, *self.otherp1_data))
		subdata += il_vst_chunk(2, struct.pack('i'*16, *self.otherp2_data))
		subdata += il_vst_chunk(3, struct.pack('i'*16, *self.otherp3_data))

		outdata += il_vst_chunk(1, subdata)+b'\x00\x00\x00\x00'

		if self.headertype in [1,4]:
			outdata += struct.pack('i', len(self.state_data))
			outdata += self.state_data
		else:
			outdata += self.state_data

		return outdata
