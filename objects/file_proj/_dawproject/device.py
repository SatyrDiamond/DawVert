import xml.etree.ElementTree as ET
from objects.file_proj._dawproject import param

class dawproject_band:
	def __init__(self):
		self.type = None
		self.gain = param.dawproject_param_numeric('Gain')
		self.freq = param.dawproject_param_numeric('Freq')
		self.q = param.dawproject_param_numeric('Q')
		self.enabled = param.dawproject_param_bool('Enabled')

	def read(self, xml_data):
		if 'type' in xml_data.attrib: self.type = xml_data.attrib['type']
		for x_part in xml_data:
			if x_part.tag == 'Gain': self.gain.read(x_part)
			if x_part.tag == 'Freq': self.freq.read(x_part)
			if x_part.tag == 'Q': self.q.read(x_part)
			if x_part.tag == 'Enabled': self.enabled.read(x_part)

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Band')
		if self.type != None: tempxml.set('type', str(self.type))
		self.gain.write(tempxml)
		self.freq.write(tempxml)
		self.q.write(tempxml)
		self.enabled.write(tempxml)

class dawproject_realparameter:
	def __init__(self):
		self.parameterID = None
		self.id = None
		self.name = None
		self.max = 1
		self.min = 0
		self.unit = "normalized" 
		self.value = None

	def read(self, xml_data):
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		if 'parameterID' in xml_data.attrib: self.parameterID = xml_data.attrib['parameterID']
		if 'name' in xml_data.attrib: self.name = xml_data.attrib['name']
		if 'max' in xml_data.attrib: self.max = float(xml_data.attrib['max'])
		if 'min' in xml_data.attrib: self.min = float(xml_data.attrib['min'])
		if 'value' in xml_data.attrib: self.value = float(xml_data.attrib['value'])
		if 'unit' in xml_data.attrib: self.unit = xml_data.attrib['unit']

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'RealParameter')
		if self.id != None: tempxml.set('id', self.id)
		if self.parameterID != None: tempxml.set('parameterID', str(self.parameterID))
		if self.name != None: tempxml.set('name', self.name)
		if self.max != None: tempxml.set('max', '%.6f' % self.max)
		if self.min != None: tempxml.set('min', '%.6f' % self.min)
		if self.value != None: tempxml.set('value', '%.6f' % self.value)
		if self.unit != None: tempxml.set('unit', self.unit)

class dawproject_device:
	def __init__(self, plugintype):
		self.plugintype = plugintype
		self.deviceID = None
		self.deviceName = None
		self.deviceRole = None
		self.loaded = None
		self.id = None
		self.name = None
		self.enabled = param.dawproject_param_bool('Enabled')
		self.state = param.dawproject_param_path('State')
		self.params = {}
		self.bands = []
		self.realparameter = []

	def read(self, xml_data):
		if 'deviceID' in xml_data.attrib: self.deviceID = xml_data.attrib['deviceID']
		if 'deviceName' in xml_data.attrib: self.deviceName = xml_data.attrib['deviceName']
		if 'deviceRole' in xml_data.attrib: self.deviceRole = xml_data.attrib['deviceRole']
		if 'loaded' in xml_data.attrib: self.loaded = xml_data.attrib['loaded']=='true'
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		if 'name' in xml_data.attrib: self.name = xml_data.attrib['name']
		for x_part in xml_data:
			if x_part.tag == 'Enabled': self.enabled.read(x_part)
			elif x_part.tag == 'State': self.state.read(x_part)
			elif x_part.tag == 'Parameters': 
				for x_rpart in x_part:
					realparameter_obj = dawproject_realparameter()
					realparameter_obj.read(x_rpart)
					self.realparameter.append(realparameter_obj)
			elif x_part.tag == 'Band': 
				band_obj = dawproject_band()
				band_obj.read(x_part)
				self.bands.append(band_obj)
			else:
				if 'unit' in x_part.attrib:
					param_obj = param.dawproject_param_numeric(x_part.tag)
					param_obj.read(x_part)
					self.params[x_part.tag] = param_obj

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, self.plugintype)
		if self.deviceID != None: tempxml.set('deviceID', str(self.deviceID))
		if self.deviceName != None: tempxml.set('deviceName', str(self.deviceName))
		if self.deviceRole != None: tempxml.set('deviceRole', str(self.deviceRole))
		if self.loaded != None: tempxml.set('loaded', 'true' if self.loaded else 'false')
		if self.id != None: tempxml.set('id', str(self.id))
		if self.name != None: tempxml.set('name', str(self.name))
		parameters = ET.SubElement(tempxml, 'Parameters')
		for x in self.realparameter: x.write(parameters)
		self.enabled.write(tempxml)
		self.state.write(tempxml)
		for _, x in self.params.items():
			x.write(tempxml)
		for x in self.bands: x.write(tempxml)
