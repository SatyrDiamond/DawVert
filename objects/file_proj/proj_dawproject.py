# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
from xml.dom import minidom
from objects.file_proj._dawproject import clips
from objects.file_proj._dawproject import param
from objects.file_proj._dawproject import points
from objects.file_proj._dawproject import track

class dawproject_transport:
	def __init__(self):
		self.Tempo = param.dawproject_param_numeric('Tempo')
		self.Tempo.max = 600
		self.Tempo.min = 20
		self.Tempo.unit = 'bpm'
		self.Tempo.value = 120
		self.Tempo.name = 'Tempo'

		self.TimeSignature = param.dawproject_param_timesignature('TimeSignature')
		self.TimeSignature.denominator = 4
		self.TimeSignature.numerator = 4

	def read(self, xml_data):
		for x_part in xml_data:
			if x_part.tag == 'Tempo': self.Tempo.read(x_part)
			if x_part.tag == 'TimeSignature': self.TimeSignature.read(x_part)

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Transport')
		self.Tempo.write(tempxml)
		self.TimeSignature.write(tempxml)

class dawproject_application:
	def __init__(self):
		self.name = ''
		self.version = ''

	def read(self, xml_data):
		if 'name' in xml_data.attrib: self.name = xml_data.attrib['name']
		if 'version' in xml_data.attrib: self.version = xml_data.attrib['version']

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Application')
		tempxml.set('name', self.name)
		tempxml.set('version', self.version)

# ----------------------------------------- ARRANGEMENT -----------------------------------------

class dawproject_lanecontainer:
	def __init__(self):
		self.lanes = []
		self.id = ''
		self.timeUnit = ''

	def read(self, xml_data):
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		if 'timeUnit' in xml_data.attrib: self.timeUnit = xml_data.attrib['timeUnit']
		for x_part in xml_data:
			if x_part.tag == 'Lanes':
				lane_obj = clips.dawproject_lane()
				lane_obj.read(x_part)
				self.lanes.append(lane_obj)

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Lanes')
		if self.timeUnit: tempxml.set('timeUnit', self.timeUnit)
		if self.id: tempxml.set('id', self.id)

		for x in self.lanes: x.write(tempxml)

class dawproject_marker:
	def __init__(self):
		self.time = None
		self.name = None
		self.color = None

	def read(self, xml_data):
		if 'time' in xml_data.attrib: self.time = float(xml_data.attrib['time'])
		if 'name' in xml_data.attrib: self.name = xml_data.attrib['name']
		if 'color' in xml_data.attrib: self.color = xml_data.attrib['color']

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Marker')
		if self.time: tempxml.set('time', str(self.time))
		if self.name: tempxml.set('name', self.name)
		if self.color: tempxml.set('color', self.color)

class dawproject_markers:
	def __init__(self):
		self.markers = []
		self.id = ''

	def read(self, xml_data):
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		for x_part in xml_data:
			marker_obj = dawproject_marker()
			marker_obj.read(x_part)
			self.markers.append(marker_obj)

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Markers')
		if self.id: tempxml.set('id', self.id)
		for x in self.markers: x.write(tempxml)

class dawproject_arrangement:
	def __init__(self):
		self.id = ''
		self.lanes = dawproject_lanecontainer()
		self.tempoautomation = None
		self.timesignatureautomation = None
		self.markers = None

	def read(self, xml_data):
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		for x_part in xml_data:
			if x_part.tag == 'Lanes': 
				self.lanes.read(x_part)
			if x_part.tag == 'TempoAutomation': 
				self.tempoautomation = points.dawproject_points()
				self.tempoautomation.read(x_part)
			if x_part.tag == 'TimeSignatureAutomation': 
				self.timesignatureautomation = points.dawproject_points_timesig()
				self.timesignatureautomation.read(x_part)
			if x_part.tag == 'Markers': 
				self.markers = dawproject_markers()
				self.markers.read(x_part)

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Arrangement')
		tempxml.set('id', self.id)
		self.lanes.write(tempxml)
		if self.tempoautomation: self.tempoautomation.write(tempxml, 'TempoAutomation')
		if self.timesignatureautomation: self.timesignatureautomation.write(tempxml, 'TimeSignatureAutomation')
		if self.markers: self.markers.write(tempxml)

class dawproject_song:
	def __init__(self):
		self.tracks = []
		self.application = dawproject_application()
		self.transport = dawproject_transport()
		self.arrangement = dawproject_arrangement()
		self.metadata = {}

	def load_from_data(self, input_data):
		x_root = ET.fromstring(input_data)
		for x_part in x_root:
			if x_part.tag == 'Application': self.application.read(x_part)
			if x_part.tag == 'Transport': self.transport.read(x_part)
			if x_part.tag == 'Arrangement': self.arrangement.read(x_part)
			if x_part.tag == 'Structure': 
				for x_trackpart in x_part:
					if x_trackpart.tag == 'Track': 
						track_obj = track.dawproject_track()
						track_obj.read(x_trackpart)
						self.tracks.append(track_obj)

	def load_metadata(self, input_data):
		x_root = ET.fromstring(input_data)
		for x_part in x_root:
			if x_part.text:
				self.metadata[x_part.tag] = x_part.text

	def save_metadata(self):
		x_metadata = ET.Element("MetaData")
		x_metadata.set('version', '1.0')
		for x, v in self.metadata.items():
			vp = ET.SubElement(x_metadata, x)
			vp.text = v

		xmlstr = minidom.parseString(ET.tostring(x_metadata)).toprettyxml(indent="\t")
		return xmlstr.encode("UTF-8")

	def save_to_file(self, output_file):
		with open(output_file, "wb") as f: 
			f.write(self.save_to_text())

	def save_to_text(self):
		x_root = ET.Element("Project")
		x_root.set('version', '1.0')

		self.application.write(x_root)
		self.transport.write(x_root)
		xstructure = ET.SubElement(x_root, 'Structure')
		for t in self.tracks: t.write(xstructure)
		self.arrangement.write(x_root)

		xmlstr = minidom.parseString(ET.tostring(x_root)).toprettyxml(indent="\t")
		return xmlstr.encode("UTF-8")
