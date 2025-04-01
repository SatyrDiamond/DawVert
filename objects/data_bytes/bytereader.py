import struct
import varint
import os
import zlib
import numpy as np
import mmap
from io import BytesIO
from contextlib import contextmanager

class chunk_size:
	def __init__(self):
		self.size_id = 4
		self.size_id_num = False
		self.size_chunk = 4
		self.endian = False
		self.unpackfunc = struct.Struct('<I').unpack
		self.unpackfunc_id = struct.Struct('4s').unpack

	def set_sizes(self, size_id, size_chunk, endian):
		self.size_id = size_id
		self.size_chunk = size_chunk
		self.endian = endian
		self.size_id_num = False
		self.set_unpackfunc()

	def set_sizes_num(self, size_id, size_chunk, endian):
		self.size_id = size_id
		self.size_chunk = size_chunk
		self.endian = endian
		self.size_id_num = True
		self.set_unpackfunc()

	def set_unpackfunc(self):
		if self.size_chunk == 1: self.unpackfunc = struct.Struct('B').unpack
		if self.size_chunk == 2: self.unpackfunc = struct.Struct('>H' if self.endian else '<H').unpack
		if self.size_chunk == 4: self.unpackfunc = struct.Struct('>I' if self.endian else '<I').unpack
		if not self.size_id_num:
			self.unpackfunc_id = struct.Struct(str(self.size_id)+'s').unpack
		else:
			if self.size_id == 1: self.unpackfunc_id = struct.Struct('B').unpack
			if self.size_id == 2: self.unpackfunc_id = struct.Struct('>H' if self.endian else '<H').unpack
			if self.size_id == 4: self.unpackfunc_id = struct.Struct('>I' if self.endian else '<I').unpack

class chunk_loc:
	def __init__(self, byteread, sizedata):
		self.t_byteread = byteread
		self.t_sizedata = sizedata
		self.id = b''
		self.start = 0
		self.end = 0
		self.size = 0

	def iter(self, offset): 
		subchunk_obj = self.t_byteread.chunk_objmake()
		subchunk_obj.sizedata = self.t_sizedata
		return subchunk_obj.iter(self.start+offset, self.end)

	def debugtxt(self):
		print(self.id, self.start, self.end)

class iff_chunkdata:
	def __init__(self, byteread):
		self.byteread = byteread
		self.sizedata = chunk_size()

	def set_sizes(self, size_id, size_chunk, endian):
		self.sizedata.set_sizes(size_id, size_chunk, endian)

	def set_sizes_num(self, size_id, size_chunk, endian):
		self.sizedata.set_sizes_num(size_id, size_chunk, endian)

	def read(self, end):
		chunk_obj = chunk_loc(self.byteread, self.sizedata)
		sizebytes = self.byteread.read(self.sizedata.size_id)
		if not len(sizebytes): return False, chunk_obj
		chunk_obj.id = self.sizedata.unpackfunc_id(sizebytes)[0]
		if chunk_obj.id or self.sizedata.size_id_num:
			chunk_obj.size = self.sizedata.unpackfunc(self.byteread.read(self.sizedata.size_chunk))[0]
			chunk_obj.start = self.byteread.tell()
			chunk_obj.end = chunk_obj.start+chunk_obj.size
			isvalid = chunk_obj.end <= end
		else:
			isvalid = False
		return isvalid, chunk_obj

	def iter(self, start, end):
		pos = self.byteread.tell()
		if start > -1: self.byteread.seek(start)
		while end > self.byteread.tell():
			isvalid, chunk_obj = self.read(end)
			if not isvalid: break
			bpos = self.byteread.tell()
			yield chunk_obj
			self.byteread.seek(bpos+chunk_obj.size)
		self.byteread.seek(pos)



def get_bitnums_int(x):
	return [i for i in range(x.bit_length()) if ((1 << i) & x)]

class bytereader:
	unpack_byte = struct.Struct('B').unpack
	unpack_s_byte = struct.Struct('b').unpack

	unpack_short = struct.Struct('<H').unpack
	unpack_short_b = struct.Struct('>H').unpack
	unpack_s_short = struct.Struct('<h').unpack
	unpack_s_short_b = struct.Struct('>h').unpack
	
	unpack_int = struct.Struct('<I').unpack
	unpack_int_b = struct.Struct('>I').unpack
	unpack_s_int = struct.Struct('<i').unpack
	unpack_s_int_b = struct.Struct('>i').unpack
	
	unpack_float = struct.Struct('<f').unpack
	unpack_float_b = struct.Struct('>f').unpack
	unpack_double = struct.Struct('<d').unpack
	unpack_double_b = struct.Struct('>d').unpack

	unpack_long = struct.Struct('<Q').unpack
	unpack_long_b = struct.Struct('>Q').unpack
	unpack_s_long = struct.Struct('<q').unpack
	unpack_s_long_b = struct.Struct('>q').unpack
	
	def __init__(self, *argv):
		self.buf = None
		self.start = 0
		self.end = 0
		self.iso_range = []
		if argv:
			self.load_raw(argv[0])

	def chunk_objmake(self): 
		return iff_chunkdata(self)

	def load_file(self, filename):
		if os.path.exists(filename):
			file_stats = os.stat(filename)
			self.end = file_stats.st_size
			f = open(filename)
			self.buf = mmap.mmap(f.fileno(), 0, access = mmap.ACCESS_READ)
			return True
		else:
			#print('File Not Found', filename)
			return False

	def load_raw(self, rawdata):
		self.end = len(rawdata)
		self.buf = BytesIO(rawdata)

	def magic_check(self, headerbytes):
		if self.buf.read(len(headerbytes)) == headerbytes: return True
		else: raise ValueError('Magic Check Failed: '+str(headerbytes))

	def detectheader(self, startloc, headerbytes):
		pos = self.buf.tell()
		return self.buf.read(len(headerbytes)) == headerbytes
		self.buf.seek(pos)

	def read(self, num): return self.buf.read(num)

	def tell(self): return self.buf.tell()-self.start

	def seek(self, num): return self.buf.seek(num+self.start)

	def skip(self, num): return self.buf.seek(self.tell()+num+self.start)

	def tell_real(self): return self.buf.tell()

	def seek_real(self, num): return self.buf.seek(num)

	def skip_real(self, num): return self.buf.seek(self.tell()+num)

	@contextmanager
	def isolate_range(self, start, end, set_end):
		try:
			#print('ENTER', self.start, self.end, self.end-self.start, '>', start, end, end-start, self.iso_range)
			self.iso_range.append([self.start, self.end, self.tell_real()])
			self.start = start
			self.end = end
			self.seek(0)
			yield self
		finally:
			real_start, real_end, real_pos = self.iso_range[-1]
			self.iso_range = self.iso_range[:-1]
			self.start = real_start
			self.end = real_end
			self.seek_real(end if set_end else real_pos)
			#print('EXIT', self.start, self.end, self.end-self.start, '>', real_start, real_end, real_end-real_start, self.iso_range)

	def isolate_size(self, size, set_end):
		start = self.tell_real()
		return self.isolate_range(start, start+size, set_end)

	def remaining(self): return max(0, self.end - self.buf.tell())

	def bytesplit(self):
		value = self.uint8()
		return value >> 4, value & 0x0F

	def bytesplit16(self):
		value1 = self.uint8()
		value2 = self.uint8()
		return value1 >> 4, value1 & 0x0F, value2 >> 4, value2 & 0x0F

	def bool8(self): return bool(self.int8())
	def bool16(self): return bool(self.int16())
	def bool32(self): return bool(self.int32())

	def uint8(self): return self.unpack_byte(self.buf.read(1))[0]
	def int8(self): return self.unpack_s_byte(self.buf.read(1))[0]

	def uint16(self): return self.unpack_short(self.buf.read(2))[0]
	def uint16_b(self): return self.unpack_short_b(self.buf.read(2))[0]
	def int16(self): return self.unpack_s_short(self.buf.read(2))[0]
	def int16_b(self): return self.unpack_s_short_b(self.buf.read(2))[0]

	def uint24(self): return self.unpack_int(self.buf.read(3)+b'\x00')[0]
	def uint24_b(self): return self.unpack_int_b(b'\x00'+self.buf.read(3))[0]

	def uint32(self): return self.unpack_int(self.buf.read(4))[0]
	def uint32_b(self): return self.unpack_int_b(self.buf.read(4))[0]
	def int32(self): return self.unpack_s_int(self.buf.read(4))[0]
	def int32_b(self): return self.unpack_s_int_b(self.buf.read(4))[0]

	def uint64(self): return self.unpack_long(self.buf.read(8))[0]
	def uint64_b(self): return self.unpack_long_b(self.buf.read(8))[0]
	def int64(self): return self.unpack_s_long(self.buf.read(8))[0]
	def int64_b(self): return self.unpack_s_long_b(self.buf.read(8))[0]

	def float(self): return self.unpack_float(self.buf.read(4))[0]
	def float_b(self): return self.unpack_float_b(self.buf.read(4))[0]

	def double(self): return self.unpack_double(self.buf.read(8))[0]
	def double_b(self): return self.unpack_double_b(self.buf.read(8))[0]

	def flags8(self): return get_bitnums_int(self.uint8())
	def flags16(self): return get_bitnums_int(self.uint16())
	def flags24(self): return get_bitnums_int(self.uint24())
	def flags32(self): return get_bitnums_int(self.uint32())
	def flags64(self): return get_bitnums_int(self.uint64())

	def table8(self, tabledata):
		numbytes = np.prod(tabledata)
		return np.frombuffer(self.buf.read(numbytes), np.uint8).reshape(*tabledata)

	def table16(self, tabledata):
		numbytes = np.prod(tabledata)*2
		return np.frombuffer(self.buf.read(numbytes), np.uint16).reshape(*tabledata)

	def stable8(self, tabledata):
		numbytes = np.prod(tabledata)
		return np.frombuffer(self.buf.read(numbytes), np.int8).reshape(*tabledata)

	def stable16(self, tabledata):
		numbytes = np.prod(tabledata)*2
		return np.frombuffer(self.buf.read(numbytes), np.int16).reshape(*tabledata)

	def varint(self): return varint.decode_stream(self.buf)

	def raw(self, size): return self.buf.read(size)

	def debug_peek(self): 
		self.buf.seek(self.buf.tell()-64)
		print(self.buf.read(128)) 

	def rest(self): return self.buf.read(self.end-self.buf.tell())

	def string(self, size, **kwargs): return self.buf.read(size).split(b'\x00')[0].decode(**kwargs)
	def string16(self, size): return self.buf.read(size*2).decode("utf-16").rstrip('\x00')

	def l_int4(self, num): 
		out = []
		for _ in range(num): out += self.bytesplit()
		return out

	def l_uint8(self, num): return np.frombuffer(self.buf.read(num), dtype=np.uint8)
	def l_int8(self, num): return np.frombuffer(self.buf.read(num), dtype=np.int8)

	def l_uint16(self, num): return [self.uint16() for _ in range(num)]
	def l_uint16_b(self, num): return [self.uint16_b() for _ in range(num)]
	def l_int16(self, num): return [self.int16() for _ in range(num)]
	def l_int16_b(self, num): return [self.int16_b() for _ in range(num)]

	def l_uint32(self, num): return [self.uint32() for _ in range(num)]
	def l_uint32_b(self, num): return [self.uint32_b() for _ in range(num)]
	def l_int32(self, num): return [self.int32() for _ in range(num)]
	def l_int32_b(self, num): return [self.int32_b() for _ in range(num)]

	def l_float(self, num): return [self.float() for _ in range(num)]
	def l_float_b(self, num): return [self.float_b() for _ in range(num)]

	def l_double(self, num): return [self.double() for _ in range(num)]
	def l_double_b(self, num): return [self.double_b() for _ in range(num)]

	def l_string(self, num, size): return [self.string(size) for _ in range(num)]

	def c_string__varint(self, **kwargs): return self.string(self.varint(), **kwargs)
	def c_string__int8(self, **kwargs): return self.string(self.uint8(), **kwargs)
	def c_string__int16(self, endian, **kwargs): return self.string(self.uint16_b() if endian else self.uint16(), **kwargs)
	def c_string__int24(self, endian, **kwargs): return self.string(self.uint24_b() if endian else self.uint24(), **kwargs)
	def c_string__int32(self, endian, **kwargs): return self.string(self.uint32_b() if endian else self.uint32(), **kwargs)

	def c_raw__int8(self): return self.raw(self.uint8())
	def c_raw__int16(self, endian): return self.raw(self.uint16_b() if endian else self.uint16())
	def c_raw__int24(self, endian): return self.raw(self.uint24_b() if endian else self.uint24())
	def c_raw__int32(self, endian): return self.raw(self.uint32_b() if endian else self.uint32())

	def c_uint8__int8(self): return self.l_uint8(self.uint8())
	def c_uint8__int16(self, endian): return self.l_uint8(self.uint16_b() if endian else self.uint16())
	def c_uint8__int24(self, endian): return self.l_uint8(self.uint24_b() if endian else self.uint24())
	def c_uint8__int32(self, endian): return self.l_uint8(self.uint32_b() if endian else self.uint32())

	def c_int8__int8(self): return self.l_int8(self.uint8())
	def c_int8__int16(self, endian): return self.l_int8(self.uint16_b() if endian else self.uint16())
	def c_int8__int24(self, endian): return self.l_int8(self.uint24_b() if endian else self.uint24())
	def c_int8__int32(self, endian): return self.l_int8(self.uint32_b() if endian else self.uint32())

	def string_t(self, **kwargs):
		output = b''
		terminated = 0
		while terminated == 0:
			char = self.buf.read(1)
			if char not in [b'\x00', b'']: output += char
			else: terminated = 1
		return output.decode(**kwargs)

	def string16_t(self):
		output = b''
		terminated = 0
		while terminated == 0:
			char = self.buf.read(2)
			if char not in [b'\x00'b'\x00', b'\x00', b'']: output += char
			else: terminated = 1
		return output.decode("utf-16")