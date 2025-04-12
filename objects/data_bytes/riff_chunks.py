# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects.data_bytes import riff_chunks
from objects.data_bytes import bytewriter

class riff_chunk:
	def __init__(self):
		self.name = None
		self.data = b''
		self.start = 0
		self.end = 0
		self.size = 0
		self.is_list = False
		self.in_data = []

	def __getitem__(self, num):
		return self.in_data[num]

	def iter_wseek(self, byr_stream):
		for x in self.in_data:
			byr_stream.seek(x.start)
			yield x

	def add_part(self, name):
		self.is_list = True
		temp_chunk = riff_chunk()
		temp_chunk.name = name
		self.in_data.append(temp_chunk)
		return temp_chunk

	def dump_list(self, byr_stream):
		byr_stream.seek_real(self.start-4)
		return b'RIFF'+byr_stream.raw(self.end-self.start)

	def read_list(self, byr_stream, headersize, storedata):
		self.is_list = True
		self.start = byr_stream.tell_real()
		self.name = byr_stream.raw(4)
		while byr_stream.tell_real()<byr_stream.end:
			temp_chunk = riff_chunk()
			temp_chunk.name = byr_stream.raw(4)
			chunk_size = byr_stream.uint32()
			if temp_chunk.name == b'LIST':
				temp_chunk.is_list = True
				with byr_stream.isolate_size(chunk_size, True) as bye_stream: 
					temp_chunk.read_list(bye_stream, chunk_size, storedata)
			else: 
				temp_chunk.start = byr_stream.tell_real()
				temp_chunk.end = temp_chunk.start+chunk_size
				temp_chunk.size = chunk_size
				if storedata: temp_chunk.data = byr_stream.raw(chunk_size)
				else: byr_stream.skip(chunk_size)
			if bool(chunk_size & 1): byr_stream.skip(1)
			self.in_data.append(temp_chunk)
		self.end = byr_stream.tell_real()

	def load_from_byr(self, byr_stream, storedata):
		byr_stream.magic_check(b'RIFF')
		headersize = byr_stream.uint32()-4
		self.read_list(byr_stream, headersize, True)
		return byr_stream

	def load_from_bytes(self, inbytes, storedata):
		byr_stream = bytereader.bytereader()
		byr_stream.load_raw(inbytes)
		return self.load_from_byr(byr_stream, storedata)

	def load_from_file(self, input_file, storedata):
		byr_stream = bytereader.bytereader()
		byr_stream.load_file(input_file)
		self.load_from_byr(byr_stream, storedata)
		return byr_stream

	def write(self, byw_stream, writeheader):
		if not self.is_list:
			chunk_size = len(self.data)
			with byw_stream.chunk(self.name) as byc_stream: byc_stream.raw(self.data)
			if bool(chunk_size & 1): byc_stream.zeros(1)
		else:
			if writeheader:
				with byw_stream.chunk(b'RIFF') as byc_stream: 
					byc_stream.raw(self.name)
					for inchunk in self.in_data:
						inchunk.write(byw_stream, False)
			else:
				with byw_stream.chunk(b'LIST') as byc_stream: 
					byc_stream.raw(self.name)
					for inchunk in self.in_data:
						inchunk.write(byw_stream, False)
		return byw_stream

	def write_to_file(self, output_file):
		byw_stream = bytewriter.bytewriter()
		outdata = self.write(byw_stream, True).getvalue()
		f = open(output_file, 'wb')
		f.write(outdata)