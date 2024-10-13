# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter
import struct
import varint
import json
import traceback

class DataDefException(Exception):
    pass

class datadef_global:
	output = []
	structnames = []
	leftoverbytes = b''

def string_fix(inputtxt):
	return inputtxt.split(b'\x00')[0].decode().translate(dict.fromkeys(range(32)))

class datadef_part:
	__slots__ = ['vartype','inpart','p_num','p_txt']
	def __init__(self, textin):
		self.vartype = None
		self.inpart = None
		self.p_num = 0
		self.p_txt = ''

		if textin != None:
			cut_part = textin[0].split('.')
			if len(cut_part)>0: self.vartype = cut_part[0]

			if self.vartype in ['skip_n','string','dstring','list','raw']: 
				if len(cut_part)>1: self.p_num = int(cut_part[1])
				else:
					raise DataDefException(self.vartype+' requires 2')


			if self.vartype in ['struct', 'getvar']: self.p_txt = cut_part[1]

			if len(textin)>1: self.inpart = datadef_part(textin[1:])

	def decode(self, byr_stream, d_structs, d_vars, inlength):
		p_num = self.p_num

		if self.vartype == 'skip': byr_stream.skip(1)
		elif self.vartype == 'skip_n': byr_stream.skip(p_num)

		elif self.vartype == 'struct': 
			if self.p_txt in d_structs: 
				if self.p_txt in datadef_global.structnames: raise DataDefException('recursion detected: '+self.p_txt)
				return d_structs[self.p_txt].decode(byr_stream, d_structs, d_vars)
			else: raise DataDefException('struct not found: '+self.p_txt)

		elif self.vartype == 'getvar':
			if self.p_txt in d_vars: return d_vars[self.p_txt]
			else: raise DataDefException('var not found: '+self.p_txt)

		elif self.vartype == 'byte': return byr_stream.uint8()
		elif self.vartype == 's_byte': return byr_stream.int8()

		elif self.vartype == 'short': return byr_stream.uint16()
		elif self.vartype == 'short_b': return byr_stream.uint16_b()
		elif self.vartype == 's_short': return byr_stream.int16()
		elif self.vartype == 's_short_b': return byr_stream.int16_b()

		elif self.vartype == 'int': return byr_stream.uint32()
		elif self.vartype == 'int_b': return byr_stream.uint32_b()
		elif self.vartype == 's_int': return byr_stream.int32()
		elif self.vartype == 's_int_b': return byr_stream.int32_b()

		elif self.vartype == 'float': return byr_stream.float()
		elif self.vartype == 'float_b': return byr_stream.float_b()
		elif self.vartype == 'double': return byr_stream.double()
		elif self.vartype == 'double_b': return byr_stream.double_b()

		elif self.vartype == 'varint': return byr_stream.varint()

		elif self.vartype == 'rest': return byr_stream.rest()
		elif self.vartype == 'raw': return byr_stream.raw(p_num)
		elif self.vartype == 'string': return byr_stream.string(p_num)
		elif self.vartype == 'dstring': return byr_stream.string16(p_num)

		elif self.vartype == 'raw_part': return byr_stream.raw(self.inpart.decode(byr_stream, d_structs, d_vars, None))
		elif self.vartype == 'string_part': return byr_stream.string(self.inpart.decode(byr_stream, d_structs, d_vars, None))
		elif self.vartype == 'dstring_part': return byr_stream.string16(self.inpart.decode(byr_stream, d_structs, d_vars, None))

		elif self.vartype == 'string_t': return byr_stream.string_t()

		elif self.vartype == 'list':
			if inlength: p_num = inlength
			if not self.inpart: DataDefException('list requires a part')
			elif not self.inpart.vartype: DataDefException('list requires a part')
			elif self.inpart.vartype == 'byte': return byr_stream.l_uint8(p_num)
			elif self.inpart.vartype == 's_byte': return byr_stream.l_int8(p_num)
			elif self.inpart.vartype == 'short': return byr_stream.l_uint16(p_num)
			elif self.inpart.vartype == 'short_b': return byr_stream.l_uint16_b(p_num)
			elif self.inpart.vartype == 's_short': return byr_stream.l_int16(p_num)
			elif self.inpart.vartype == 's_short_b': return byr_stream.l_int16_b(p_num)
			elif self.inpart.vartype == 'int': return byr_stream.l_uint32(p_num)
			elif self.inpart.vartype == 'int_b': return byr_stream.l_uint32_b(p_num)
			elif self.inpart.vartype == 's_int': return byr_stream.l_int32(p_num)
			elif self.inpart.vartype == 's_int_b': return byr_stream.l_int32_b(p_num)
			elif self.inpart.vartype == 'float': return byr_stream.l_float(p_num)
			elif self.inpart.vartype == 'float_b': return byr_stream.l_float_b(p_num)
			elif self.inpart.vartype == 'double': return byr_stream.l_double(p_num)
			elif self.inpart.vartype == 'double_b': return byr_stream.l_double_b(p_num)
			else: return [self.inpart.decode(byr_stream, d_structs, d_vars, None) for _ in range(p_num)]



		else: 
			raise DataDefException('unknown vartype: '+str(self.vartype))


	def encode(self, value, byw_stream, d_structs, p_name):
		if self.vartype == 'skip': byw_stream.raw(b'\0', 1)
		elif self.vartype == 'skip_n': byw_stream.raw(b'\0'*self.p_num)

		elif self.vartype == 'struct': 
			return d_structs[self.p_txt].encode(value if value != None else {}, byw_stream, d_structs)

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

		elif self.vartype == 'raw': byw_stream.raw_l(value, self.p_num)
		elif self.vartype == 'string': byw_stream.string(value, self.p_num)
		elif self.vartype == 'dstring': byw_stream.string16(value, self.p_num)

		elif self.vartype == 'string_t': 
			outstr = value+'\x00'
			return byw_stream.string(outstr, len(outstr))

		elif self.vartype == 'raw_part':
			self.inpart.encode(len(value), byw_stream, d_structs, p_name)
			return byw_stream.raw_l(value, len(value))

		elif self.vartype == 'string_part':
			self.inpart.encode(len(value), byw_stream, d_structs, p_name)
			return byw_stream.string(value, len(value))

		elif self.vartype == 'dstring_part':
			self.inpart.encode(len(value), byw_stream, d_structs, p_name)
			return byw_stream.string16(value, len(value))

		elif self.vartype == 'list': 
			if self.inpart.vartype == 'byte': byw_stream.l_uint8(value, self.p_num)
			elif self.inpart.vartype == 's_byte': byw_stream.l_int8(value, self.p_num)
			elif self.inpart.vartype == 'short': byw_stream.l_uint16(value, self.p_num)
			elif self.inpart.vartype == 'short_b': byw_stream.l_uint16_b(value, self.p_num)
			elif self.inpart.vartype == 's_short': byw_stream.l_int16(value, self.p_num)
			elif self.inpart.vartype == 's_short_b': byw_stream.l_int16_b(value, self.p_num)
			elif self.inpart.vartype == 'int': byw_stream.l_uint32(value, self.p_num)
			elif self.inpart.vartype == 'int_b': byw_stream.l_uint32_b(value, self.p_num)
			elif self.inpart.vartype == 's_int': byw_stream.l_int32(value, self.p_num)
			elif self.inpart.vartype == 's_int_b': byw_stream.l_int32_b(value, self.p_num)
			elif self.inpart.vartype == 'float': byw_stream.l_float(value, self.p_num)
			elif self.inpart.vartype == 'float_b': byw_stream.l_float_b(value, self.p_num)
			elif self.inpart.vartype == 'double': byw_stream.l_double(value, self.p_num)
			elif self.inpart.vartype == 'double_b': byw_stream.l_double_b(value, self.p_num)
			else: return [self.inpart.encode(v, byw_stream, d_structs, p_name) for v in value]

		else: print('unknown vartype:',self.vartype)






class datadef_struct:
	def __init__(self, name):
		self.parts = []
		self.name = name

	def decode(self, byr_stream, d_structs, d_vars, **kwargs):
		if d_vars == None: d_vars = {}
		output = {}
		lengths = {}

		datadef_global.structnames.append(self.name)
		for p_type, p_obj, p_name in self.parts:
			try:
				filepos = byr_stream.tell()
				value = p_obj.decode(byr_stream, d_structs, d_vars, lengths[p_name] if p_name in lengths else None)
				if p_name and p_type == 'part': output[p_name] = value
				if p_name and p_type == 'length': lengths[p_name] = value
				datadef_global.output.append([str(filepos), datadef_global.structnames[-1], p_name, p_obj.vartype, str(value)])
			except:
 				pass

		datadef_global.structnames.pop()

		return output

	def encode(self, in_data, byw_stream, d_structs):

		lengths = {}

		for p_type, p_obj, p_name in self.parts:
			if p_type == 'part': 
				value = in_data[p_name] if p_name in in_data else None
				p_obj.encode(value, byw_stream, d_structs, p_name)
			if p_type == 'length': 
				value = len(in_data[p_name]) if p_name in in_data else 0
				p_obj.encode(value, byw_stream, d_structs, p_name)


class datadef:
	def __init__(self, filepath):
		self.structs = {}
		self.cases = {}
		self.metadata = {}
		self.using_structs = []
		self.errored = False
		self.errormeg = ''
		if filepath: self.load_file(filepath)

# ####################################################################################################
# ####################################################################################################
# --- file
# ####################################################################################################
# ####################################################################################################

	def parse_file(self, structname, filename):
		in_data = bytereader.bytereader()
		in_data.load_file(filename)
		return self.parse_internal(structname, in_data)

	def parse(self, structname, data):
		in_data = bytereader.bytereader()
		in_data.load_raw(data)
		return self.parse_internal(structname, in_data)


	def create(self, structname, in_data):
		byw_stream = bytewriter.bytewriter()
		if structname in self.structs:
			self.structs[structname].encode(in_data, byw_stream, self.structs)
			return byw_stream.getvalue()
		else:
			return b''

	def parse_internal(self, structname, in_data):
		datadef_global.output = []
		datadef_global.structnames = []

		try:
			self.errored = False
			if structname in self.structs:
				return self.structs[structname].decode(in_data, self.structs, None)
			else:
				return None
		except DataDefException as e:
			self.errored = True
			self.errormeg = str(e)
			self.errormegf = traceback.format_exc()
			print(self.errormegf)
			return b''

		datadef_global.leftoverbytes = in_data.rest()



	def load_file(self, in_datadef):
		self.structs = {}
		self.metadata = {}
		self.cases = {}

		if in_datadef != None:
			f = open(in_datadef, "r")
			ddlines = [x.strip().split('#')[0].split('|') for x in f.readlines()]
			ddlines = [[p.strip() for p in l] for l in ddlines]
			current_struct = None
			for ddline in ddlines:
				if ddline != ['']:
					if ddline[0] == 'meta':
						self.metadata[ddline[1]] = ddline[2]
					if ddline[0] == 'area_struct':
						current_struct = ddline[1]
						self.structs[ddline[1]] = datadef_struct(ddline[1])
					if ddline[0] in ['part', 'length']:
						self.structs[current_struct].parts.append([ddline[0], datadef_part(ddline[1].split('/')), ddline[2]])
			#print('[datadef] Loaded '+in_datadef)


	def save_file(self, file_name):
		linesdata = []

		for key, value in self.metadata.items():
			linesdata.append('meta|'+key+'|'+value)

		for structname in self.structs:
			linesdata.append('')
			linesdata.append('area_struct|'+structname)
			for structpart in self.structs[structname]:
				subvals = structpart[1]
				subvals = [x[0] if x[1] == '' else x[0]+'.'+x[1] for x in subvals]
				subvals = '/'.join(subvals).replace(' ','')
				linesdata.append(structpart[0]+'|'+subvals+'|'+structpart[2])

		with open(file_name, "w") as fileout:
			for line in linesdata:
				fileout.write(line+'\n')
