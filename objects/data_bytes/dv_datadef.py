# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter
import xml.etree.ElementTree as ET
import struct
import traceback

class DataDefException(Exception):
    pass

DEBUGPRINT = False

class datadef_part:
	__slots__ = ['inparts', 'part_size', 'vartype', 'name', 'size_source', 'size_len', 'struct_name', 'type', 'match_value']

	def __init__(self, xml_data):
		self.inparts = []
		self.part_size = None
		self.vartype = None
		self.name = None
		self.size_source = 0
		self.size_len = 1
		self.struct_name = None
		self.type = None
		self.match_value = None

		if xml_data is not None:
			self.type = xml_data.tag
			attrib = xml_data.attrib
			if 'type' in attrib: self.vartype = attrib['type']
			else: raise DataDefException('part has no type')
			if 'name' in attrib: self.name = attrib['name']
			if 'struct_name' in attrib: self.struct_name = attrib['struct_name']
			if 'size' in attrib: self.size_len = int(attrib['size'])
			if 'match_value' in attrib: self.match_value = attrib['match_value']
			if 'size_source' in attrib: 
				size_source = attrib['size_source']
				if size_source == 'part': self.size_source = 1
				if size_source == 'lengthval': self.size_source = 2

			for part in xml_data:
				if part.tag in ['part', 'length']:
					self.inparts.append(datadef_part(part))
				if part.tag == 'size': self.part_size = datadef_part(part)

	def decode_get_size(self, byr_stream, global_vals):
		if self.size_source == 0: return self.size_len
		if self.size_source == 1: 
			if self.part_size:
				return self.part_size.decode(byr_stream, global_vals)
			else:
				raise DataDefException('part size not found: '+str(self.name))
		if self.size_source == 2: return global_vals.lengths[self.name]

	def decode(self, byr_stream, global_vals):

		outval = None

		#if DEBUGPRINT: remain = byr_stream.remaining()

		if self.vartype == 'skip': byr_stream.skip(self.size_len)

		elif self.vartype == 'struct': 
			d_structs = global_vals.structs
			if self.struct_name in d_structs: 
				if self.struct_name in global_vals.using_structs: raise DataDefException('recursion detected: '+self.struct_name)
				outval = d_structs[self.struct_name].decode(byr_stream, global_vals, self.struct_name)
			else: raise DataDefException('struct not found: '+self.struct_name)

		elif self.vartype == 'byte': outval = byr_stream.uint8()
		elif self.vartype == 's_byte': outval = byr_stream.int8()

		elif self.vartype == 'short': outval = byr_stream.uint16()
		elif self.vartype == 'short_b': outval = byr_stream.uint16_b()
		elif self.vartype == 's_short': outval = byr_stream.int16()
		elif self.vartype == 's_short_b': outval = byr_stream.int16_b()

		elif self.vartype == 'int': outval = byr_stream.uint32()
		elif self.vartype == 'int_b': outval = byr_stream.uint32_b()
		elif self.vartype == 's_int': outval = byr_stream.int32()
		elif self.vartype == 's_int_b': outval = byr_stream.int32_b()

		elif self.vartype == 'float': outval = byr_stream.float()
		elif self.vartype == 'float_b': outval = byr_stream.float_b()
		elif self.vartype == 'double': outval = byr_stream.double()
		elif self.vartype == 'double_b': outval = byr_stream.double_b()

		elif self.vartype == 'varint': outval = byr_stream.varint()

		elif self.vartype == 'rest': outval = byr_stream.rest()
		elif self.vartype == 'raw': outval = byr_stream.raw(self.decode_get_size(byr_stream, global_vals))
		elif self.vartype == 'string': outval = byr_stream.string(self.decode_get_size(byr_stream, global_vals))
		elif self.vartype == 'dstring': outval = byr_stream.string16(self.decode_get_size(byr_stream, global_vals))

		elif self.vartype == 'string_t': outval = byr_stream.string_t()

		elif self.vartype == 'list':
			p_num = self.decode_get_size(byr_stream, global_vals)
			if not self.inparts: DataDefException('list requires a part')
			if len(self.inparts)==1:
				firstpart = self.inparts[0]
				if p_num != -1:					
					if firstpart.vartype == 'byte': outval = byr_stream.l_uint8(p_num)
					elif firstpart.vartype == 's_byte': outval = byr_stream.l_int8(p_num)
					elif firstpart.vartype == 'short': outval = byr_stream.l_uint16(p_num)
					elif firstpart.vartype == 'short_b': outval = byr_stream.l_uint16_b(p_num)
					elif firstpart.vartype == 's_short': outval = byr_stream.l_int16(p_num)
					elif firstpart.vartype == 's_short_b': outval = byr_stream.l_int16_b(p_num)
					elif firstpart.vartype == 'int': outval = byr_stream.l_uint32(p_num)
					elif firstpart.vartype == 'int_b': outval = byr_stream.l_uint32_b(p_num)
					elif firstpart.vartype == 's_int': outval = byr_stream.l_int32(p_num)
					elif firstpart.vartype == 's_int_b': outval = byr_stream.l_int32_b(p_num)
					elif firstpart.vartype == 'float': outval = byr_stream.l_float(p_num)
					elif firstpart.vartype == 'float_b': outval = byr_stream.l_float_b(p_num)
					elif firstpart.vartype == 'double': outval = byr_stream.l_double(p_num)
					elif firstpart.vartype == 'double_b': outval = byr_stream.l_double_b(p_num)
					else: outval = [firstpart.decode(byr_stream, global_vals) for _ in range(p_num)]
				else:
					if firstpart.vartype == 'byte': outval = byr_stream.l_uint8(byr_stream.remaining())
					elif firstpart.vartype == 's_byte': outval = byr_stream.l_int8(byr_stream.remaining())
					elif firstpart.vartype == 'short': outval = byr_stream.l_uint16(byr_stream.remaining()//2)
					elif firstpart.vartype == 'short_b': outval = byr_stream.l_uint16_b(byr_stream.remaining()//2)
					elif firstpart.vartype == 's_short': outval = byr_stream.l_int16(byr_stream.remaining()//2)
					elif firstpart.vartype == 's_short_b': outval = byr_stream.l_int16_b(byr_stream.remaining()//2)
					elif firstpart.vartype == 'int': outval = byr_stream.l_uint32(byr_stream.remaining()//4)
					elif firstpart.vartype == 'int_b': outval = byr_stream.l_uint32_b(byr_stream.remaining()//4)
					elif firstpart.vartype == 's_int': outval = byr_stream.l_int32(byr_stream.remaining()//4)
					elif firstpart.vartype == 's_int_b': outval = byr_stream.l_int32_b(byr_stream.remaining()//4)
					elif firstpart.vartype == 'float': outval = byr_stream.l_float(byr_stream.remaining()//4)
					elif firstpart.vartype == 'float_b': outval = byr_stream.l_float_b(byr_stream.remaining()//4)
					elif firstpart.vartype == 'double': outval = byr_stream.l_double(byr_stream.remaining()//8)
					elif firstpart.vartype == 'double_b': outval = byr_stream.l_double_b(byr_stream.remaining()//8)
					else: 
						outval = []
						while byr_stream.remaining():
							outval.append(firstpart.decode(byr_stream, global_vals))


		else: 
			raise DataDefException('unknown vartype: '+str(self.vartype))

		if DEBUGPRINT: 
			debval = outval if type(outval) != dict else '<DICT>'
			if type(debval) == list: debval = '<LIST>'
			print(('    '*global_vals.debug_ne)+self.vartype, '|', self.name, '|', debval, '|')

		return outval

	def match(self, dictdata):
		value = dictdata[self.name] if self.name in dictdata else None

		if self.vartype in ['byte', 's_byte', 'short', 'short_b', 's_short', 's_short_b', 'int', 'int_b', 's_int', 's_int_b', 'varint']:
			value = int(value)
		if self.vartype in ['float', 'float_b', 'double', 'double_b']:
			value = float(value)

		return value==self.match_value

	def encode(self, dictdata, byw_stream, d_structs, is_size):
		value = dictdata[self.name] if self.name in dictdata else None
		if is_size and value is not None: value = len(value)

		if self.size_source == 0: 
			lenv = self.size_len
		if self.size_source == 1: 
			lenv = len(value)
			part_size = self.part_size
			if part_size:
				if part_size.vartype == 'byte': byw_stream.uint8(lenv)
				elif part_size.vartype == 'short': byw_stream.uint16(lenv)
				elif part_size.vartype == 'short_b': byw_stream.uint16_b(lenv)
				elif part_size.vartype == 'int': byw_stream.uint32(lenv)
				elif part_size.vartype == 'int_b': byw_stream.uint32_b(lenv)
				elif part_size.vartype == 'varint': byw_stream.varint(lenv)
			else:
				raise DataDefException('part size not found: '+str(self.name))
		if self.size_source == 2: 
			lenv = len(value)

		if self.vartype == 'skip': byw_stream.raw(b'\0')
		elif self.vartype == 'skip_n': byw_stream.raw(b'\0'*self.p_num)

		elif self.vartype == 'struct': 
			return d_structs[self.struct_name].encode(value if value != None else {}, byw_stream, d_structs)

		elif self.vartype == 'byte': byw_stream.uint8(int(value) if value != None else 0)
		elif self.vartype == 's_byte': byw_stream.int8(int(value) if value != None else 0)

		elif self.vartype == 'short': byw_stream.uint16(int(value) if value != None else 0)
		elif self.vartype == 'short_b': byw_stream.uint16_b(int(value) if value != None else 0)
		elif self.vartype == 's_short': byw_stream.int16(int(value) if value != None else 0)
		elif self.vartype == 's_short_b': byw_stream.int16_b(int(value) if value != None else 0)

		elif self.vartype == 'int': byw_stream.uint32(int(value) if value != None else 0)
		elif self.vartype == 'int_b': byw_stream.uint32_b(int(value) if value != None else 0)
		elif self.vartype == 's_int': byw_stream.int32(int(value) if value != None else 0)
		elif self.vartype == 's_int_b': byw_stream.int32_b(int(value) if value != None else 0)

		elif self.vartype == 'float': byw_stream.float(value if value != None else 0)
		elif self.vartype == 'float_b': byw_stream.float_b(value if value != None else 0)
		elif self.vartype == 'double': byw_stream.double(value if value != None else 0)
		elif self.vartype == 'double_b': byw_stream.double_b(value if value != None else 0)

		elif self.vartype == 'varint': byw_stream.varint(int(value) if value != None else 0)

		elif self.vartype == 'string_t': 
			outstr = value+'\x00'
			return byw_stream.string(outstr, len(outstr))

		elif self.vartype == 'raw': 
			byw_stream.raw_l(value, lenv)
		elif self.vartype == 'string': 
			byw_stream.string(value, lenv)
		elif self.vartype == 'dstring': 
			byw_stream.string16(value, lenv)

		elif self.vartype == 'list': 
			firstpart = self.inparts[0]
			if len(self.inparts)==1:
				firstpart = self.inparts[0]
				if firstpart.vartype == 'byte': byw_stream.l_uint8(value, lenv)
				elif firstpart.vartype == 's_byte': byw_stream.l_int8(value, lenv)
				elif firstpart.vartype == 'short': byw_stream.l_uint16(value, lenv)
				elif firstpart.vartype == 'short_b': byw_stream.l_uint16_b(value, lenv)
				elif firstpart.vartype == 's_short': byw_stream.l_int16(value, lenv)
				elif firstpart.vartype == 's_short_b': byw_stream.l_int16_b(value, lenv)
				elif firstpart.vartype == 'int': byw_stream.l_uint32(value, lenv)
				elif firstpart.vartype == 'int_b': byw_stream.l_uint32_b(value, lenv)
				elif firstpart.vartype == 's_int': byw_stream.l_int32(value, lenv)
				elif firstpart.vartype == 's_int_b': byw_stream.l_int32_b(value, lenv)
				elif firstpart.vartype == 'float': byw_stream.l_float(value, lenv)
				elif firstpart.vartype == 'float_b': byw_stream.l_float_b(value, lenv)
				elif firstpart.vartype == 'double': byw_stream.l_double(value, lenv)
				elif firstpart.vartype == 'double_b': byw_stream.l_double_b(value, lenv)
				else: return [self.inpart.encode(v, byw_stream, d_structs, False) for v in value]

		else: print('unknown vartype:',self.vartype)

class datadef_struct:
	__slots__ = ['parts']

	def __init__(self, xml_data):
		self.parts = []
		if xml_data is not None:
			for part in xml_data:
				if part.tag in ['part', 'length', 'match']:
					self.parts.append(datadef_part(part))

	def decode_parttype(self, byr_stream, part, output, global_vals):
		value = None
		if part.type in ['part', 'length']: 
			value = part.decode(byr_stream, global_vals)

		if part.name: 
			if part.type == 'part': output[part.name] = value
			if part.type == 'length': global_vals.lengths[part.name] = value

		if part.type == 'match': 
			ismatch = part.match(output)
			if ismatch:
				for inpart in part.inparts:
					output[inpart.name] = inpart.decode(byr_stream, global_vals)

	def decode(self, byr_stream, global_vals, name):
		if DEBUGPRINT: 
			print(('    '*global_vals.debug_ne)+'STRUCT', name)
			global_vals.debug_ne += 1
		output = {}

		global_vals.using_structs.append(name)
		for part in self.parts:
			#filepos = byr_stream.tell()
			self.decode_parttype(byr_stream, part, output, global_vals)

			#global_vals.output.append([str(filepos), global_vals.using_structs[-1], part.name, part.vartype, str(value)])

		global_vals.using_structs.pop()

		if DEBUGPRINT: global_vals.debug_ne -= 1

		return output

	def encode(self, in_data, byw_stream, d_structs):

		lengths = {}

		for p_obj in self.parts:
			if p_obj.type == 'part': 
				p_obj.encode(in_data, byw_stream, d_structs, False)
			if p_obj.type == 'length': 
				p_obj.encode(in_data, byw_stream, d_structs, True)


class datadef_global:
	def __init__(self):
		self.output = []
		self.using_structs = []
		self.structs = {}
		self.lengths = {}
		if DEBUGPRINT: 
			self.debug_ne = -1

class datadef:
	__slots__ = ['structs', 'errored', 'errormeg']
	def __init__(self, filepath):
		self.structs = {}
		self.errored = False
		self.errormeg = ''
		if filepath: self.load_file(filepath)

	def parse_file(self, structname, filename):
		byr_stream = bytereader.bytereader()
		byr_stream.load_file(filename)
		return self.parse_internal(structname, byr_stream)

	def parse(self, structname, data):
		byr_stream = bytereader.bytereader()
		byr_stream.load_raw(data)
		return self.parse_internal(structname, byr_stream)

	def parse_internal(self, structname, byr_stream):
		global_obj = datadef_global()
		global_obj.structs = self.structs

		try:
			self.errored = False
			if structname in self.structs:
				return self.structs[structname].decode(byr_stream, global_obj, structname)
			else:
				return None
		except DataDefException as e:
			self.errored = True
			self.errormeg = str(e)
			self.errormegf = traceback.format_exc()
			print(self.errormegf)
			return b''

	def create(self, structname, in_data):
		byw_stream = bytewriter.bytewriter()
		if structname in self.structs:
			self.structs[structname].encode(in_data, byw_stream, self.structs)
			return byw_stream.getvalue()
		else:
			return b''

	def load_file(self, in_datadef):
		self.structs = {}

		if in_datadef != None:
			parser = ET.XMLParser(encoding='utf-8')
			xml_data = ET.parse(in_datadef, parser)
			xml_proj = xml_data.getroot()
			for part in xml_proj:
				if part.tag == 'struct': 
					name = part.get('name')
					struct_obj = datadef_struct(part)
					if name: self.structs[name] = struct_obj
					