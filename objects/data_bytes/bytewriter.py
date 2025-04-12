import struct
import varint
import os
import numpy as np
import mmap
from io import BytesIO
from contextlib import contextmanager

class chunk_size:
	def __init__(self):
		self.size_id = 4
		self.size_chunk = 4
		self.endian = False

	def set_sizes(self, size_id, size_chunk, endian):
		self.size_id = size_id
		self.size_chunk = size_chunk
		self.endian = endian

def set_bitnums(x, n):
	outvals = 0
	for v in x: outvals += (1 << v)
	return outvals.to_bytes(n, 'little')

def create_array(value, size, idtype):
	outs = np.zeros(size, dtype=idtype)
	outs[0:min(len(value), size)] = value[0:size]
	return outs.tobytes()

class bytewriter:
	pack_byte = struct.Struct('B').pack
	pack_s_byte = struct.Struct('b').pack

	pack_short = struct.Struct('<H').pack
	pack_short_b = struct.Struct('>H').pack
	pack_s_short = struct.Struct('<h').pack
	pack_s_short_b = struct.Struct('>h').pack
   
	pack_int = struct.Struct('<I').pack
	pack_int_b = struct.Struct('>I').pack
	pack_s_int = struct.Struct('<i').pack
	pack_s_int_b = struct.Struct('>i').pack
   
	pack_long = struct.Struct('<Q').pack
	pack_long_b = struct.Struct('>Q').pack
	pack_s_long = struct.Struct('<q').pack
	pack_s_long_b = struct.Struct('>q').pack
	
	pack_float = struct.Struct('<f').pack
	pack_float_b = struct.Struct('>f').pack
	pack_double = struct.Struct('<d').pack
	pack_double_b = struct.Struct('>d').pack

	dtype_uint16_b = np.dtype('>h')
	dtype_int16_b = np.dtype('>H')

	dtype_uint32_b = np.dtype('>i')
	dtype_int32_b = np.dtype('>I')

	dtype_float_b = np.dtype('>f')
	dtype_double_b = np.dtype('>d')

	def __init__(self):
		self.buf = BytesIO()
		self.end = 0
		self.chunkprop = chunk_size()

	def getvalue(self):
		return self.buf.getvalue()

	def uint8(self, value):
		self.buf.write(self.pack_byte(value))
		self.end += 1
	def int8(self, value):
		self.buf.write(self.pack_s_byte(value))
		self.end += 1

	def uint16(self, value):
		self.buf.write(self.pack_short(value))
		self.end += 2
	def uint16_b(self, value):
		self.buf.write(self.pack_short_b(value))
		self.end += 2
	def int16(self, value):
		self.buf.write(self.pack_s_short(value))
		self.end += 2
	def int16_b(self, value):
		self.buf.write(self.pack_s_short_b(value))
		self.end += 2

	def uint32(self, value):
		self.buf.write(self.pack_int(value))
		self.end += 4
	def uint32_b(self, value):
		self.buf.write(self.pack_int_b(value))
		self.end += 4
	def int32(self, value):
		self.buf.write(self.pack_s_int(value))
		self.end += 4
	def int32_b(self, value):
		self.buf.write(self.pack_s_int_b(value))
		self.end += 4

	def uint64(self, value):
		self.buf.write(self.pack_long(value))
		self.end += 4
	def uint64_b(self, value):
		self.buf.write(self.pack_long_b(value))
		self.end += 4
	def int64(self, value):
		self.buf.write(self.pack_s_long(value))
		self.end += 4
	def int64_b(self, value):
		self.buf.write(self.pack_s_long_b(value))
		self.end += 4

	def float(self, value):
		self.buf.write(self.pack_float(value))
		self.end += 4
	def float_b(self, value):
		self.buf.write(self.pack_float_b(value))
		self.end += 4

	def double(self, value):
		self.buf.write(self.pack_double(value))
		self.end += 8
	def double_b(self, value):
		self.buf.write(self.pack_double_b(value))
		self.end += 8

	def flags8(self, value):
		self.buf.write(set_bitnums(value, 1))
		self.end += 1
	def flags16(self, value):
		self.buf.write(set_bitnums(value, 2))
		self.end += 2
	def flags24(self, value):
		self.buf.write(set_bitnums(value, 3))
		self.end += 3
	def flags32(self, value):
		self.buf.write(set_bitnums(value, 4))
		self.end += 4
	def flags64(self, value):
		self.buf.write(set_bitnums(value, 8))
		self.end += 4

	def bool8(self, value):
		self.int8(int(value))

	def bool16(self, value):
		self.int16(int(value))

	def bool32(self, value):
		self.int32(int(value))

	def varint(self, value):
		outb = varint.encode(value)
		self.buf.write(outb)
		self.end += len(outb)

	def raw_l(self, value, size):
		outb = bytearray(b"\0" * size)
		outb[0:len(value)] = value
		self.buf.write(outb)
		self.end += size

	def write(self, value):
		self.buf.write(value)
		self.end += len(value)

	def raw(self, value):
		self.buf.write(value)
		self.end += len(value)

	def zeros(self, value):
		self.buf.write(b'\x00'*value)
		self.end += value

	def string(self, value, size, **kwargs):
		self.raw(bytearray(value.encode(**kwargs)+b"\0")[0:size].ljust(size, b'\0'))

	def string16(self, value, size, **kwargs):
		self.raw(bytearray(value.encode('utf-16')+b"\0")[0:size].ljust(size, b'\0'))

	def l_uint8(self, value, size): 
		self.raw(create_array(value, size, np.uint8))

	def l_int8(self, value, size): 
		self.raw(create_array(value, size, np.int8))

	def l_uint16(self, value, size): 
		self.raw(create_array(value, size, np.uint16))

	def l_uint16_b(self, value, size): 
		self.raw(create_array(value, size, self.dtype_uint16_b))

	def l_int16(self, value, size): 
		self.raw(create_array(value, size, np.int16))

	def l_int16_b(self, value, size): 
		self.raw(create_array(value, size, self.dtype_int16_b))

	def l_uint32(self, value, size): 
		self.raw(create_array(value, size, np.uint32))

	def l_uint32_b(self, value, size): 
		self.raw(create_array(value, size, self.dtype_uint32_b))

	def l_int32(self, value, size): 
		self.raw(create_array(value, size, np.int32))

	def l_int32_b(self, value, size): 
		self.raw(create_array(value, size, self.dtype_int32_b))

	def l_float(self, value, size): 
		self.raw(create_array(value, size, np.float32))

	def l_float_b(self, value, size): 
		self.raw(create_array(value, size, self.dtype_float_b))

	def l_double(self, value, size): 
		self.raw(create_array(value, size, np.float64))

	def l_double_b(self, value, size): 
		self.raw(create_array(value, size, self.dtype_double_b))

	def l_string(self, value, num, size): 
		self.raw(create_array(value, size, (np.string_, num)))

	def c_string__int8(self, value, **kwargs): 
		outs = value.encode(**kwargs)+b"\0"
		self.int8(len(outs))
		self.raw(outs)

	def c_string__int16(self, value, **kwargs): 
		outs = value.encode(**kwargs)+b"\0"
		self.int16(len(outs))
		self.raw(outs)

	def c_string__int32(self, value, **kwargs): 
		outs = value.encode(**kwargs)+b"\0"
		self.int32(len(outs))
		self.raw(outs)

	def c_string__int32_b(self, value, **kwargs): 
		outs = value.encode(**kwargs)+b"\0"
		self.int32_b(len(outs))
		self.raw(outs)

	def c_string__varint(self, value, **kwargs): 
		outs = value.encode(**kwargs)+b"\0"
		self.varint(len(outs))
		self.raw(outs)

	def c_string__int8__nonull(self, value, **kwargs): 
		outs = value.encode(**kwargs)
		self.int8(len(outs))
		self.raw(outs)

	def c_string__int16__nonull(self, value, **kwargs): 
		outs = value.encode(**kwargs)
		self.int16(len(outs))
		self.raw(outs)

	def c_string__int32__nonull(self, value, **kwargs): 
		outs = value.encode(**kwargs)
		self.int32(len(outs))
		self.raw(outs)

	def c_string__varint__nonull(self, value, **kwargs): 
		outs = value.encode(**kwargs)
		self.varint(len(outs))
		self.raw(outs)

	def string_t(self, value, **kwargs): 
		self.raw(value.encode(**kwargs)+b"\0")

	def c_raw__int8(self, value): 
		self.int8(len(value))
		self.raw(value)

	def c_raw__int16(self, value, endian): 
		if endian: self.int16(len(value))
		else: self.int16_b(len(value))
		self.raw(value)

	def c_raw__int32(self, value, endian): 
		if endian: self.int32(len(value))
		else: self.int32_b(len(value))
		self.raw(value)

	def c_raw__varint(self, value): 
		self.varint(len(value))
		self.raw(value)

	@contextmanager
	def chunk(self, namebytes):
		self.raw(namebytes)
		pos_sizeval = self.buf.tell()
		self.raw(b"\0"*self.chunkprop.size_chunk)
		pos_start = self.buf.tell()
		yield self
		endpos = self.buf.tell()
		self.buf.seek(pos_sizeval)
		size = endpos-pos_start
		if self.chunkprop.size_chunk == 1: self.uint8(size)
		if self.chunkprop.size_chunk == 2: 
			if not self.chunkprop.endian: self.uint16(size)
			else: self.uint16_b(size)
		if self.chunkprop.size_chunk == 4: 
			if not self.chunkprop.endian: self.uint32(size)
			else: self.uint32_b(size)
		self.buf.seek(endpos)
