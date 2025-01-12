# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
from objects.file_proj._zenbeats import func
from objects.file_proj._zenbeats import misc

class zenbeats_automation_point:
	def __init__(self, xml_data):
		self.position = 0.0
		self.value = 0.0
		self.type = 'line'
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'position' in attrib: self.position = float(attrib['position'])
		if 'value' in attrib: self.value = float(attrib['value'])
		if 'type' in attrib: self.type = attrib['type']

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "point")
		tempxml.set('position', str(self.position))
		tempxml.set('value', str(self.value))
		tempxml.set('type', str(self.type))

class zenbeats_automation_curve:
	def __init__(self, xml_data):
		self.version = misc.zenbeats_version()
		self.visual = misc.zenbeats_visual_info()
		self.uid = func.make_uuid()
		self.target_object = "" 
		self.target = ""
		self.function = ""
		self.parameter = 0
		self.low_range = 0.0
		self.high_range = 1.0
		self.unlinked_parameter_name = "" 
		self.unlinked_internal_plugin_type = -1
		self.unlinked_plugin_file = "" 
		self.restore_value = None
		self.points = []
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		self.visual.read(xml_data)
		self.version.read(xml_data)
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'target_object' in attrib: self.target_object = attrib['target_object']
		if 'target' in attrib: self.target = attrib['target']
		if 'function' in attrib: self.function = attrib['function']
		if 'parameter' in attrib: self.parameter = int(attrib['parameter'])
		if 'low_range' in attrib: self.low_range = float(attrib['low_range'])
		if 'high_range' in attrib: self.high_range = float(attrib['high_range'])
		if 'unlinked_parameter_name' in attrib: self.unlinked_parameter_name = attrib['unlinked_parameter_name']
		if 'unlinked_internal_plugin_type' in attrib: self.unlinked_internal_plugin_type = int(attrib['unlinked_internal_plugin_type'])
		if 'unlinked_plugin_file' in attrib: self.unlinked_plugin_file = attrib['unlinked_plugin_file']
		if 'restore_value' in attrib: self.restore_value = float(attrib['restore_value'])
		for x_part in xml_data:
			if x_part.tag == 'point': self.points.append(zenbeats_automation_point(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "automation_curve")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('target_object', str(self.target_object))
		tempxml.set('target', str(self.target))
		tempxml.set('function', str(self.function))
		tempxml.set('parameter', str(self.parameter))
		tempxml.set('low_range', str(self.low_range))
		tempxml.set('high_range', str(self.high_range))
		tempxml.set('unlinked_parameter_name', str(self.unlinked_parameter_name))
		tempxml.set('unlinked_internal_plugin_type', str(self.unlinked_internal_plugin_type))
		tempxml.set('unlinked_plugin_file', str(self.unlinked_plugin_file))
		if self.restore_value is not None: tempxml.set('restore_value', str(self.restore_value))
		for point in self.points: point.write(tempxml)

class zenbeats_automation_set:
	def __init__(self, xml_data):
		self.version = misc.zenbeats_version()
		self.visual = misc.zenbeats_visual_info()
		self.uid = func.make_uuid()
		self.selected_child = -1
		self.target_uid = ""
		self.curves = []
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		self.visual.read(xml_data)
		self.version.read(xml_data)
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'target_uid' in attrib: self.target_uid = attrib['target_uid']
		for x_part in xml_data:
			if x_part.tag == 'automation_curve': self.curves.append(zenbeats_automation_curve(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "automation_set")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('target_uid', str(self.target_uid))
		for curve in self.curves: curve.write(tempxml)
