import xml.etree.ElementTree as ET

class dawproject_pointtarget:
	def __init__(self):
		self.expression = None
		self.parameter = None

	def read(self, xml_data):
		if 'expression' in xml_data.attrib: self.expression = xml_data.attrib['expression']
		if 'parameter' in xml_data.attrib: self.parameter = xml_data.attrib['parameter']

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Target')
		if self.expression != None: tempxml.set('expression', self.expression)
		if self.parameter != None: tempxml.set('parameter', self.parameter)

class dawproject_realpoint:
	def __init__(self):
		self.time = None
		self.interpolation = None
		self.value = None

	def read(self, xml_data):
		if 'time' in xml_data.attrib: self.time = float(xml_data.attrib['time'])
		if 'interpolation' in xml_data.attrib: self.interpolation = xml_data.attrib['interpolation']
		if 'value' in xml_data.attrib: self.value = float(xml_data.attrib['value'])
	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'RealPoint')
		if self.value != None: tempxml.set('value',  '%.6f' % self.value)
		if self.interpolation != None: tempxml.set('interpolation', self.interpolation)
		if self.time != None: tempxml.set('time',  '%.6f' % self.time)

class dawproject_boolpoint:
	def __init__(self):
		self.time = None
		self.value = None

	def read(self, xml_data):
		if 'time' in xml_data.attrib: self.time = float(xml_data.attrib['time'])
		if 'value' in xml_data.attrib: self.value = xml_data.attrib['value']=='true'

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'BoolPoint')
		if self.value != None: tempxml.set('value', 'true' if self.value else 'false')
		if self.time != None: tempxml.set('time', '%.6f' % self.time)

class dawproject_points:
	def __init__(self):
		self.id = None
		self.unit = None
		self.points = []
		self.points_bool = []
		self.target = None

	def read(self, xml_data):
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		if 'unit' in xml_data.attrib: self.unit = xml_data.attrib['unit']
		for x_part in xml_data:
			if x_part.tag == 'RealPoint': 
				point_obj = dawproject_realpoint()
				point_obj.read(x_part)
				self.points.append(point_obj)
			if x_part.tag == 'BoolPoint': 
				point_obj = dawproject_boolpoint()
				point_obj.read(x_part)
				self.points_bool.append(point_obj)
			if x_part.tag == 'Target': 
				self.target = dawproject_pointtarget()
				self.target.read(x_part)

	def write(self, xmltag, name):
		tempxml = ET.SubElement(xmltag, name)
		if self.unit: tempxml.set('unit', self.unit)
		if self.id: tempxml.set('id', self.id)
		if self.target: self.target.write(tempxml)
		for x in self.points: x.write(tempxml)
		for x in self.points_bool: x.write(tempxml)

class dawproject_timesigpoint:
	def __init__(self):
		self.time = None
		self.numerator = 4
		self.denominator = 4

	def read(self, xml_data):
		if 'time' in xml_data.attrib: self.time = float(xml_data.attrib['time'])
		if 'numerator' in xml_data.attrib: self.numerator = int(xml_data.attrib['numerator'])
		if 'denominator' in xml_data.attrib: self.denominator = int(xml_data.attrib['denominator'])

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'TimeSignaturePoint')
		if self.numerator != None: tempxml.set('numerator',  str(self.numerator))
		if self.denominator != None: tempxml.set('denominator',  str(self.denominator))
		if self.time != None: tempxml.set('time',  '%.6f' % self.time)

class dawproject_points_timesig:
	def __init__(self):
		self.id = None
		self.unit = None
		self.points = []
		self.target = None

	def read(self, xml_data):
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		if 'unit' in xml_data.attrib: self.unit = xml_data.attrib['unit']
		for x_part in xml_data:
			if x_part.tag == 'TimeSignaturePoint': 
				point_obj = dawproject_timesigpoint()
				point_obj.read(x_part)
				self.points.append(point_obj)
			if x_part.tag == 'Target': 
				self.target = dawproject_pointtarget()
				self.target.read(x_part)

	def write(self, xmltag, name):
		tempxml = ET.SubElement(xmltag, name)
		if self.unit: tempxml.set('unit', self.unit)
		if self.id: tempxml.set('id', self.id)
		if self.target: self.target.write(tempxml)
		for x in self.points: x.write(tempxml)
