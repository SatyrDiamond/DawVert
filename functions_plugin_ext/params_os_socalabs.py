# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import lxml.etree as ET
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import data_vc2xml

class socalabs_data:
	def __init__(self):
		self.x_sl_data = ET.Element("state")
		self.x_sl_data.set('valueTree', '<?xml version="1.0" encoding="UTF-8"?>\n<state width="400" height="328"/>')
		self.x_sl_data.set('program', '0')

	def set_param(self, name, value):
		x_temp = ET.SubElement(self.x_sl_data, 'param')
		x_temp.set('uid', name)
		x_temp.set('val', str(value))

	def to_cvpj_vst2(self, fourid):
		plugin_vst2.replace_data(plugin_obj, 'id','any', fourid, 'chunk', ET.tostring(self.x_sl_data, encoding='utf-8'), None)