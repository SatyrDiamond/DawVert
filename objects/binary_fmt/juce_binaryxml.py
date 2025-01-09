# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from lxml import etree as ET
from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter

VERBOSE = False

def read_number(byr_stream):
	intlen = byr_stream.uint8()
	out = 0
	if intlen == 1: out = byr_stream.uint8()
	if intlen == 2: out = byr_stream.uint16()
	if intlen == 3: out = byr_stream.uint24()
	if intlen == 4: out = byr_stream.uint32()
	if VERBOSE: print(intlen, out)
	return out

def write_number(byw_stream, val):
	if val>0xFFFFFF: 
		byw_stream.uint8(4)
		byw_stream.uint32(val)
	elif val>0xFFFF: 
		byw_stream.uint8(3)
		byw_stream.uint16(val&0xFFFF)
		byw_stream.uint8(val>>16)
	elif val>0xFF: 
		byw_stream.uint8(2)
		byw_stream.uint16(val)
	elif val:
		byw_stream.uint8(1)
		byw_stream.uint8(val)
	else:
		byw_stream.uint8(0)



class juce_binaryxml_object:
	__slots__ = ['type', 'data']
	def __init__(self):
		self.type = 0
		self.data = None

	def __repr__(self):
		return '<BinXML Object - Type: %s, Value:"%s">' % (str(self.type), str(self.data))

	def __int__(self): return int(self.data)
	def __float__(self): return float(self.data)
	def __bool__(self): return bool(self.data)
	def __str__(self): 
		if self.type == 1: return str(self.data)
		elif self.type == 2: return 'true'
		elif self.type == 3: return 'false'
		elif self.type == 4: return str(self.data)
		elif self.type == 5: return self.data
		elif self.type == 6: return str(self.data)
		elif self.type == 8: return str(self.data)
		return str(self.data)

	def read_byr(self, byr_stream):
		with byr_stream.isolate_size(read_number(byr_stream), True) as bye_stream:
			self.type = bye_stream.uint8()
			if self.type == 1: self.data = bye_stream.uint32()
			elif self.type == 2: self.data = True
			elif self.type == 3: self.data = False
			elif self.type == 4: self.data = bye_stream.double()
			elif self.type == 5: self.data = bye_stream.string_t()
			elif self.type == 6: self.data = bye_stream.uint64()
			elif self.type == 8: self.data = bye_stream.rest()
				
			else:
				if VERBOSE: print('error |', valtype)
				#byr_stream.debug__peek()
				exit()

	def write_byw(self, byw_stream):
		if self.type:
			outs_stream = bytewriter.bytewriter()
			outs_stream.uint8(self.type)
			if self.type == 1: outs_stream.uint32(min(self.data, 2147483647))
			elif self.type == 4: outs_stream.double(self.data)
			elif self.type == 5: outs_stream.string_t(self.data)
			elif self.type == 6: outs_stream.uint64(self.data)
			elif self.type == 8: outs_stream.raw(self.data)
			outdata = outs_stream.getvalue()
			write_number(byw_stream, len(outdata))
			byw_stream.raw(outdata)

	def set(self, value):
		if isinstance(value, str):
			self.type = 5
			self.data = value

		if isinstance(value, bool):
			self.type = 2 if value else 3
			self.data = value

		if isinstance(value, int):
			self.type = 1
			self.data = value
			
		if isinstance(value, float):
			self.type = 4
			self.data = value
			
	def to_xml_attrib(self, name, xmldata):
		if self.type: xmldata.set(name, str(self))
			
class juce_binaryxml_element:
	__slots__ = ['tag', 'attrib', 'children']
	def __init__(self):
		self.tag = ''
		self.attrib = {}
		self.children = []

	def get_attrib_native(self):
		return dict([(k, v.data) for (k, v) in self.attrib.items()])

	def add_child(self, tag):
		jg_child = juce_binaryxml_element()
		jg_child.tag = tag
		self.children.append(jg_child)
		return jg_child

	def set(self, name, value):
		jobj = juce_binaryxml_object()
		jobj.set(value)
		self.attrib[name] = jobj

	def __repr__(self):
		return '<BinXML Group - "%s">' % (str(self.tag))

	def __bool__(self):
		return bool(self.children)

	def __iter__(self):
		for x in self.children: yield x

	def __len__(self):
		return len(self.children)

	def read_bytes(self, inbytes):
		byr_stream = bytereader.bytereader(inbytes)
		try: self.read_byr(byr_stream)
		except: pass

	def read_byr(self, byr_stream):
		self.tag = byr_stream.string_t()
		for _ in range(read_number(byr_stream)):
			aname = byr_stream.string_t()
			b_obj = juce_binaryxml_object()
			b_obj.read_byr(byr_stream)

			if aname == 'data': print(aname, b_obj.type)

			self.attrib[aname] = b_obj

		for _ in range(read_number(byr_stream)):
			subele = juce_binaryxml_element()
			subele.read_byr(byr_stream)
			self.children.append(subele)

	def write_byw(self, byw_stream):
		byw_stream.string_t(self.tag)
		write_number(byw_stream, len(self.attrib))
		for k, v in self.attrib.items():
			byw_stream.string_t(k)
			v.write_byw(byw_stream)

		write_number(byw_stream, len(self.children))
		for x in self.children:
			x.write_byw(byw_stream)

	def to_bytes(self):
		byw_stream = bytewriter.bytewriter()
		self.write_byw(byw_stream)
		return byw_stream.getvalue()

	def to_xml(self, xmldata):
		xml_part = ET.SubElement(xmldata, self.tag)
		for k, v in self.attrib.items(): v.to_xml_attrib(k, xml_part)
		for x in self.children: x.to_xml(xml_part)

	def to_xml_root(self):
		xml_part = ET.Element(self.tag)
		for k, v in self.attrib.items(): v.to_xml_attrib(k, xml_part)
		for x in self.children: x.to_xml(xml_part)
		return xml_part

	def output_file(self, filename):
		outfile = ET.ElementTree(self.to_xml_root())
		ET.indent(outfile)
		outfile.write(filename, encoding='utf-8', xml_declaration = True)
