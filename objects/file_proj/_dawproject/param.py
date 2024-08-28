
import xml.etree.ElementTree as ET

class dawproject_param_path:
	def __init__(self, name):
		self.xmlname = name
		self.used = False
		self.path = None
		self.external = None

	def __str__(self):
		return self.path if self.path else ''

	def set(self, path):
		self.used = True
		self.path = path

	def read(self, xml_data):
		self.used = True
		if 'path' in xml_data.attrib: self.path = xml_data.attrib['path']
		if 'external' in xml_data.attrib: self.external = xml_data.attrib['external']

	def write(self, xmltag):
		if self.used:
			tempxml = ET.SubElement(xmltag, self.xmlname)
			if self.external != None: tempxml.set('external', str(self.external))
			if self.path != None: tempxml.set('path', str(self.path))

class dawproject_param_numeric:
	def __init__(self, name):
		self.xmlname = name
		self.used = False
		self.max = None
		self.min = None
		self.unit = None
		self.value = 0
		self.id = None
		self.name = None

	def __float__(self):
		return float(self.value)

	def __int__(self):
		return int(self.value)
		
	def __bool__(self):
		return bool(float(self.value))

	def read(self, xml_data):
		self.used = True
		if 'max' in xml_data.attrib: self.max = float(xml_data.attrib['max'])
		if 'min' in xml_data.attrib: self.min = float(xml_data.attrib['min'])
		if 'unit' in xml_data.attrib: self.unit = xml_data.attrib['unit']
		if 'value' in xml_data.attrib: self.value = float(xml_data.attrib['value'])
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		if 'name' in xml_data.attrib: self.name = xml_data.attrib['name']

	def write(self, xmltag):
		if self.used:
			tempxml = ET.SubElement(xmltag, self.xmlname)
			if self.max != None: tempxml.set('max', '%.6f' % self.max)
			if self.min != None: tempxml.set('min', '%.6f' % self.min)
			if self.unit != None: tempxml.set('unit', str(self.unit))
			if self.value != None: tempxml.set('value', '%.6f' % self.value)
			if self.id != None: tempxml.set('id', str(self.id))
			if self.name != None: tempxml.set('name', str(self.name))

class dawproject_param_bool:
	def __init__(self, name):
		self.xmlname = name
		self.used = False
		self.name = None
		self.unit = None
		self.value = False
		self.id = None

	def __bool__(self):
		return self.value=='true'

	def read(self, xml_data):
		self.used = True
		if 'name' in xml_data.attrib: self.name = xml_data.attrib['name']
		if 'value' in xml_data.attrib: self.value = xml_data.attrib['value']
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']

	def write(self, xmltag):
		if self.used:
			tempxml = ET.SubElement(xmltag, self.xmlname)
			if self.value != None: tempxml.set('value', 'true' if self.value else 'false')
			if self.id != None: tempxml.set('id', str(self.id))
			if self.name != None: tempxml.set('name', str(self.name))

class dawproject_param_timesignature:
	def __init__(self, name):
		self.xmlname = name
		self.used = False
		self.denominator = False
		self.numerator = None
		self.id = None

	def read(self, xml_data):
		self.used = True
		if 'denominator' in xml_data.attrib: self.denominator = xml_data.attrib['denominator']
		if 'numerator' in xml_data.attrib: self.numerator = xml_data.attrib['numerator']
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']

	def write(self, xmltag):
		if self.used:
			tempxml = ET.SubElement(xmltag, self.xmlname)
			if self.denominator != None: tempxml.set('denominator', str(self.denominator))
			if self.numerator != None: tempxml.set('numerator', str(self.numerator))
			if self.id != None: tempxml.set('id', str(self.id))
