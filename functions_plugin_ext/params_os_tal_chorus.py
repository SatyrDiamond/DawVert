# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import lxml.etree as ET
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import data_vc2xml

class tal_chorus_data:
	def __init__(self):
		self.talc_data = ET.Element("tal")
		self.talc_data.set('curprogram', "0")
		self.talc_data.set('version', "1.0")
		self.talc_progs = ET.SubElement(self.talc_data, 'programs')
		self.talc_prog = ET.SubElement(self.talc_progs, 'program')

	def set_param(self, name, value):
		self.talc_prog.set(name, str(value))

	def to_cvpj_vst2(self, convproj_obj, plugin_obj):
		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id','any', 1665682481, 'chunk', data_vc2xml.make(self.talc_data), None)