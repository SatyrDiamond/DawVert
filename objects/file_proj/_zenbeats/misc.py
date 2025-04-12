# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
from objects.file_proj._zenbeats import func

class zenbeats_version:
	def __init__(self):
		self.version = 6
		self.build_number = 9399

	def read(self, xml_proj):
		attrib = xml_proj.attrib
		if 'version' in attrib: self.version = int(attrib['version'])
		if 'build_number' in attrib: self.build_number = int(attrib['build_number'])

	def write(self, tempxml):
		tempxml.set('version', str(self.version))
		tempxml.set('build_number', str(self.build_number))

class zenbeats_visual_info:
	def __init__(self):
		self.name = ""
		self.name_set_by_user = 0
		self.description = ""
		self.color = "ffffffff"

	def read(self, xml_proj):
		attrib = xml_proj.attrib
		if 'name' in attrib: self.name = attrib['name']
		if 'name_set_by_user' in attrib: self.name_set_by_user = int(attrib['name_set_by_user'])
		if 'description' in attrib: self.description = attrib['description']
		if 'color' in attrib: self.color = attrib['color']

	def write(self, tempxml):
		tempxml.set('name', str(self.name))
		tempxml.set('name_set_by_user', str(self.name_set_by_user))
		tempxml.set('description', str(self.description))
		tempxml.set('color', str(self.color))

class zenbeats_scale_lock:
	def __init__(self, xml_proj):
		self.active = 0
		self.key = 0
		self.mode = 0
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		attrib = xml_proj.attrib
		if 'active' in attrib: self.active = int(attrib['active'])
		if 'key' in attrib: self.key = int(attrib['key'])
		if 'mode' in attrib: self.mode = int(attrib['mode'])

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "scale_lock")
		tempxml.set('active', str(self.active))
		tempxml.set('key', str(self.key))
		tempxml.set('mode', str(self.mode))
