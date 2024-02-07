# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import data_nullbytegroup

class wolfshaper_data:
	def __init__(self):
		self.graph = ''
		self.params = {}
		self.params['pregain'] = 2.000000
		self.params['wet'] = 1.000000
		self.params['postgain'] = 1.000000
		self.params['removedc'] = 1.000000
		self.params['oversample'] = 0.000000
		self.params['bipolarmode'] = 0.000000
		self.params['warptype'] = 0.000000
		self.params['warpamount'] = 0.000000
		self.params['vwarptype'] = 0.000000
		self.params['vwarpamount'] = 0.000000

	def set_param(self, name, value):
		self.params[name] = value
	
	def add_point(self,posX,posY,tension,pointtype):
		if pointtype == 'normal': pointtype = 0
		elif pointtype in ['doublecurve', 'doublecurve2', 'doublecurve3']: pointtype = 1
		elif pointtype == 'stairs': 
			pointtype = 2
			tension *= -1
		elif pointtype == 'wave': 
			pointtype = 3
			tension = ((abs(tension)*-1)+100)*0.2
		else: 
			pointtype = 1

		self.graph += float.hex(posX)+','+float.hex(posY)+','+float.hex(tension*-100)+','+str(int(pointtype))+';'

	def add_env(self, cvpj_auto):
		for cvpj_point in cvpj_auto['points']:
			tension = cvpj_point['tension'] if 'tension' in cvpj_point else 0
			pointtype = cvpj_point['type'] if 'type' in cvpj_point else 'normal'
			self.add_point(cvpj_point['position'],cvpj_point['value'],tension,pointtype)

	def to_cvpj_vst2(self, plugin_obj):
		plugin_vst2.replace_data(plugin_obj, 'name', 'any', 'Wolf Shaper', 'chunk', data_nullbytegroup.make([{'graph': self.graph}, self.params]), None)