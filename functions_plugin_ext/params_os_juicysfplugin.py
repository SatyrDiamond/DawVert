# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import lxml.etree as ET
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import data_vc2xml

class juicysfplugin_data:
	def __init__(self):
		self.program = 0
		self.jsfp_xml = ET.Element("MYPLUGINSETTINGS")
		self.jsfp_params = ET.SubElement(self.jsfp_xml, "params")
		self.jsfp_uiState = ET.SubElement(self.jsfp_xml, "uiState")
		self.jsfp_soundFont = ET.SubElement(self.jsfp_xml, "soundFont")
		self.jsfp_params.set('bank', "0")
		self.jsfp_params.set('preset', "0")
		self.jsfp_params.set('attack', "0.0")
		self.jsfp_params.set('decay', "0.0")
		self.jsfp_params.set('sustain', "0.0")
		self.jsfp_params.set('release', "0.0")
		self.jsfp_params.set('filterCutOff', "0.0")
		self.jsfp_params.set('filterResonance', "0.0")
		self.jsfp_uiState.set('width', "500.0")
		self.jsfp_uiState.set('height', "300.0")
		self.jsfp_soundFont.set('path', '')

	def set_bankpatch(self, bank, patch, filename):
		self.jsfp_params.set('bank', str(bank/128))
		self.jsfp_params.set('preset', str(patch/128))
		self.program = patch
		self.jsfp_soundFont.set('path', filename)

	def set_param(self, name, value):
		self.jsfp_params.set(name, str(value))

	def set_sffile(self, value):
		self.jsfp_soundFont.set('path', value)

	def to_cvpj_vst2(self, convproj_obj, plugin_obj):
		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1249076848, 'chunk', data_vc2xml.make(self.jsfp_xml), None)
		plugin_obj.move_prog(self.program)