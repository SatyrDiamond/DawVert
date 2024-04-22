# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import struct
from io import BytesIO
from functions import data_bytes

class vst2_fxBank:
	def __init__(self, fid):
		self.fourid = 0
		self.version = 0
		self.num_programs = 0
		self.current_program = 0
		self.programs = []
		if fid:
			self.fourid, _, self.num_programs, self.current_program = struct.unpack('>IIII', fid.read(16))
			fid.read(124)
			for _ in range(self.num_programs):
				vers = int.from_bytes(fid.read(4), "big")
				size = int.from_bytes(fid.read(4), "big")
				data = fid.read(size)
				program_obj = vst2_program()
				program_obj.parse(BytesIO(data))
				self.programs.append([vers, program_obj])

	def write(self):
		data = struct.pack('>IIII', self.fourid, 1, len(self.programs), self.current_program) + b'\x00'*124
		for vers, program_obj in self.programs:
			progd = program_obj.write()
			data += struct.pack('>II', vers, len(progd)) + progd
		return data

class vst2_fxChunkSet:
	def __init__(self, fid):
		self.fourid = 0
		self.version = 0
		self.num_programs = 0
		self.prgname = ''
		self.chunk = b''
		if fid:
			self.fourid, self.version, self.num_programs, prgname_bytes, chunk_size = struct.unpack('>III28sI', fid.read(44))
			self.chunk = fid.read(chunk_size)
			self.prgname = prgname_bytes.split(b'\x00')[0].decode()

	def write(self):
		return struct.pack('>III28sI', self.fourid, self.version, self.num_programs, self.prgname.encode(), len(self.chunk)) + self.chunk

class vst2_fxProgram:
	def __init__(self, fid):
		self.fourid = 0
		self.version = 0
		self.num_params = 0
		self.prgname = ''
		self.params = []
		if fid:
			self.fourid, self.version, self.num_params = struct.unpack('>III', fid.read(12))
			self.prgname = data_bytes.readstring_fixedlen_nofix(fid, 20, None)
			self.params = struct.unpack('>'+('f'*self.num_params), fid.read(4*self.num_params))

	def write(self):
		return struct.pack('>III28s', self.fourid, self.version, self.num_params, self.prgname.encode()) + struct.pack('>'+('f'*self.num_params), *self.params)

class vst2_program:
	def __init__(self):
		self.type = 0
		self.data = None

	def parse(self, fid):
		ccnk_type = fid.read(4)
		ccnk_size = int.from_bytes(fid.read(4), "big")

		if ccnk_type == b'FPCh':
			self.type = 1
			self.data = vst2_fxChunkSet(fid)
		if ccnk_type == b'FxCk':
			self.type = 2
			self.data = vst2_fxProgram(fid)
		if ccnk_type == b'FxBk':
			self.type = 3
			self.data = vst2_fxBank(fid)
		if ccnk_type == b'FBCh':
			self.type = 4
			self.data = vst2_fxChunkSet(fid)

	def write(self):
		if self.type == 1: 
			ccnk_type = b'FPCh'
			ccnk_data = self.data.write()
		if self.type == 2: 
			ccnk_type = b'FxCk'
			ccnk_data = self.data.write()
		if self.type == 3: 
			ccnk_type = b'FxBk'
			ccnk_data = self.data.write()
		if self.type == 4: 
			ccnk_type = b'FBCh'
			ccnk_data = self.data.write()
		return struct.pack('>4sI', ccnk_type, 1) + ccnk_data

class vst2_main:
	def __init__(self):
		self.program = vst2_program()

	def read_file(self, fxfile):
		fid = open(fxfile, 'rb')
		self.parse(fid)

	def parse(self, fid):
		if fid.read(4) == b'CcnK':
			size = int.from_bytes(fid.read(4), "big")
			self.program.parse(fid)

	def write(self):
		progdata = self.program.write()
		return struct.pack('>4sI', b'CcnK', len(progdata)) + progdata