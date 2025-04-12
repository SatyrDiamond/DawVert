# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import struct
from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter
from functions import data_bytes

class vst2_fxBank:
	def __init__(self, byr_stream):
		self.fourid = 0
		self.version = 0
		self.num_programs = 0
		self.current_program = 0
		self.programs = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.fourid = byr_stream.uint32_b()
		byr_stream.skip(4)
		self.num_programs = byr_stream.uint32_b()
		self.current_program = byr_stream.uint32_b()
		byr_stream.skip(124)
		for _ in range(self.num_programs):
			vers = byr_stream.uint32_b()
			size = byr_stream.uint32_b()
			program_obj = vst2_program()
			program_obj.parse(byr_stream, size)
			self.programs.append([vers, program_obj])

	def write(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint32_b(self.fourid)
		byw_stream.uint32_b(1)
		byw_stream.uint32_b(len(self.programs))
		byw_stream.uint32_b(self.current_program)
		byw_stream.raw(b'\x00'*124)
		for vers, program_obj in self.programs:
			progd = program_obj.write()
			byw_stream.uint32_b(vers)
			byw_stream.uint32_b(len(progd))
			byw_stream.raw(progd)
		return byw_stream.getvalue()

class vst2_fxChunkSet_bank:
	def __init__(self, byr_stream):
		self.fourid = 0
		self.version = 0
		self.num_programs = 0
		self.chunk = b''
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.fourid = byr_stream.uint32_b()
		self.version = byr_stream.uint32_b()
		self.num_programs = byr_stream.uint32_b()
		byr_stream.skip(128)
		self.chunk = byr_stream.raw(byr_stream.uint32_b())

	def write(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint32_b(self.fourid)
		byw_stream.uint32_b(self.version)
		byw_stream.uint32_b(self.num_programs)
		byw_stream.raw(b'\x00'*128)
		byw_stream.uint32_b(len(self.chunk))
		byw_stream.raw(self.chunk)
		return byw_stream.getvalue()

class vst2_fxChunkSet:
	def __init__(self, byr_stream):
		self.fourid = 0
		self.version = 0
		self.num_programs = 0
		self.prgname = ''
		self.chunk = b''
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.fourid = byr_stream.uint32_b()
		self.version = byr_stream.uint32_b()
		self.num_programs = byr_stream.uint32_b()
		try:
			self.prgname = byr_stream.string(28)
		except:
			pass
		self.chunk = byr_stream.raw(byr_stream.uint32_b())

	def write(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint32_b(self.fourid)
		byw_stream.uint32_b(self.version)
		byw_stream.uint32_b(self.num_programs)
		byw_stream.string(self.prgname, 28)
		byw_stream.uint32_b(len(self.chunk))
		byw_stream.raw(self.chunk)
		return byw_stream.getvalue()

class vst2_fxProgram:
	def __init__(self, byr_stream):
		self.fourid = 0
		self.version = 0
		self.num_params = 0
		self.prgname = ''
		self.params = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.fourid = byr_stream.uint32_b()
		self.version = byr_stream.uint32_b()
		self.num_params = byr_stream.uint32_b()
		self.prgname = byr_stream.string(28)
		self.params = byr_stream.l_float_b(self.num_params)

	def write(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint32_b(self.fourid)
		byw_stream.uint32_b(self.version)
		byw_stream.uint32_b(self.num_params)
		byw_stream.string(self.prgname, 28)
		byw_stream.l_float_b(self.params, self.num_params)
		return byw_stream.getvalue()

class vst2_program:
	def __init__(self):
		self.type = 0
		self.data = None

	def set_fxChunkSet(self, bye_stream):
		self.type = 1
		self.data = vst2_fxChunkSet(bye_stream)
		return self.data

	def set_fxProgram(self, bye_stream):
		self.type = 2
		self.data = vst2_fxProgram(bye_stream)
		return self.data

	def set_fxBank(self, bye_stream):
		self.type = 3
		self.data = vst2_fxBank(bye_stream)
		return self.data

	def set_fxChunkSet_bank(self, bye_stream):
		self.type = 4
		self.data = vst2_fxChunkSet_bank(bye_stream)
		return self.data

	def parse(self, byr_stream, size):
		if size:
			with byr_stream.isolate_size(size, False) as bye_stream: 
				ccnk_type = bye_stream.raw(4)
				ccnk_size = bye_stream.uint32_b()
				if ccnk_type == b'FPCh': self.set_fxChunkSet(bye_stream)
				if ccnk_type == b'FxCk': self.set_fxProgram(bye_stream)
				if ccnk_type == b'FxBk': self.set_fxBank(bye_stream)
				if ccnk_type == b'FBCh': self.set_fxChunkSet_bank(bye_stream)
		else:
			ccnk_type = byr_stream.raw(4)
			ccnk_size = byr_stream.uint32_b()
			if ccnk_type == b'FPCh': self.set_fxChunkSet(byr_stream)
			if ccnk_type == b'FxCk': self.set_fxProgram(byr_stream)
			if ccnk_type == b'FxBk': self.set_fxBank(byr_stream)
			if ccnk_type == b'FBCh': self.set_fxChunkSet_bank(byr_stream)

	def write(self):
		ccnk_type = b'    '
		ccnk_data = b''
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

	def load_from_file(self, fxfile):
		self.byr_stream = bytereader.bytereader()
		self.byr_stream.load_file(fxfile)
		self.parse(byr_stream)

	def load_raw(self, in_bytes):
		self.byr_stream = bytereader.bytereader()
		self.byr_stream.load_raw(in_bytes)
		self.parse(self.byr_stream)

	def parse(self, byr_stream):
		if byr_stream.read(4) == b'CcnK':
			size = byr_stream.uint32_b()
			self.program.parse(byr_stream, size)

	def write(self, byw_stream):
		byw_stream.chunkprop.endian = True
		with byw_stream.chunk(b'CcnK') as byc_stream: 
			progdata = self.program.write()
			byc_stream.raw(progdata)
			
	def write_to_file(self, output_file):
		byw_stream = bytewriter.bytewriter()
		self.write(byw_stream)
		f = open(output_file, 'wb')
		f.write(byw_stream.getvalue())
