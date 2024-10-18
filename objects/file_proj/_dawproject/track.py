import xml.etree.ElementTree as ET
from objects.file_proj._dawproject import param
from objects.file_proj._dawproject import device

class dawproject_send:
	def __init__(self):
		self.destination = None
		self.type = None
		self.id = None

		self.volume = param.dawproject_param_numeric('Volume')

	def read(self, xml_data):
		if 'destination' in xml_data.attrib: self.destination = xml_data.attrib['destination']
		if 'type' in xml_data.attrib: self.type = xml_data.attrib['type']
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		for x_part in xml_data:
			if x_part.tag == 'Volume': self.volume.read(x_part)

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Send')
		if self.destination != None: tempxml.set('destination', str(self.destination))
		if self.type != None: tempxml.set('type', str(self.type))
		if self.id != None: tempxml.set('id', str(self.id))

		self.volume.write(tempxml)

class dawproject_channel:
	def __init__(self):
		self.audioChannels = None
		self.destination = None
		self.role = None
		self.solo = None
		self.id = None
		self.sends = []
		self.devices = []

		self.mute = param.dawproject_param_bool('Mute')
		self.mute.value = False
		self.mute.name = 'Mute'

		self.pan = param.dawproject_param_numeric('Pan')
		self.pan.max = 1
		self.pan.min = 0
		self.pan.unit = 'normalized'
		self.pan.value = 0.5
		self.pan.name = 'Pan'

		self.volume = param.dawproject_param_numeric('Volume')
		self.volume.max = 2
		self.volume.min = 0
		self.volume.unit = 'linear'
		self.volume.value = 1
		self.volume.name = 'Volume'

	def read(self, xml_data):
		if 'audioChannels' in xml_data.attrib: self.audioChannels = xml_data.attrib['audioChannels']
		if 'destination' in xml_data.attrib: self.destination = xml_data.attrib['destination']
		if 'role' in xml_data.attrib: self.role = xml_data.attrib['role']
		if 'solo' in xml_data.attrib: self.solo = xml_data.attrib['solo']
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		for x_part in xml_data:
			if x_part.tag == 'Mute': self.mute.read(x_part)
			if x_part.tag == 'Pan': self.pan.read(x_part)
			if x_part.tag == 'Volume': self.volume.read(x_part)
			if x_part.tag == 'Sends': 
				for x_sendpart in x_part:
					if x_sendpart.tag == 'Send': 
						send_obj = dawproject_send()
						send_obj.read(x_sendpart)
						self.sends.append(send_obj)
			if x_part.tag == 'Devices': 
				for x_devipart in x_part:
					device_obj = device.dawproject_device(x_devipart.tag)
					device_obj.read(x_devipart)
					self.devices.append(device_obj)

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Channel')
		if self.audioChannels != None: tempxml.set('audioChannels', str(self.audioChannels))
		if self.destination != None: tempxml.set('destination', str(self.destination))
		if self.role != None: tempxml.set('role', str(self.role))
		if self.solo != None: tempxml.set('solo', str(self.solo))
		if self.id != None: tempxml.set('id', str(self.id))

		if self.devices:
			devicesxml = ET.SubElement(tempxml, 'Devices')
			for x in self.devices: x.write(devicesxml)

		self.mute.write(tempxml)
		self.pan.write(tempxml)

		if self.sends:
			sendsxml = ET.SubElement(tempxml, 'Sends')
			for x in self.sends: x.write(sendsxml)

		self.volume.write(tempxml)

class dawproject_track:
	def __init__(self):
		self.contentType = None
		self.loaded = None
		self.id = None
		self.name = None
		self.color = None
		self.channel = dawproject_channel()
		self.tracks = []

	def read(self, xml_data):
		if 'contentType' in xml_data.attrib: self.contentType = xml_data.attrib['contentType']
		if 'loaded' in xml_data.attrib: self.loaded = xml_data.attrib['loaded']
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		if 'name' in xml_data.attrib: self.name = xml_data.attrib['name']
		if 'color' in xml_data.attrib: self.color = xml_data.attrib['color']
		for x_part in xml_data:
			if x_part.tag == 'Channel':
				channel_obj = dawproject_channel()
				channel_obj.read(x_part)
				self.channel = channel_obj
			if x_part.tag == 'Track':
				track_obj = dawproject_track()
				track_obj.read(x_part)
				self.tracks.append(track_obj)

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Track')
		if self.contentType != None: tempxml.set('contentType', str(self.contentType))
		if self.loaded != None: tempxml.set('loaded', 'true' if self.loaded else 'false')
		if self.id != None: tempxml.set('id', str(self.id))
		if self.name != None: tempxml.set('name', str(self.name))
		if self.color != None: tempxml.set('color', str(self.color))
		if self.channel != None: self.channel.write(tempxml)

		for t in self.tracks:
			t.write(tempxml)
