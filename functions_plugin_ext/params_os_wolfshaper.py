# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import plugin_vst3
from functions_plugin_ext import data_nullbytegroup

def checksupport(supportedplugs):
	outsupport = []
	#if 'vst3' in supportedplugs and plugin_vst3.check_exists('id', '445046206173636C7073577300000000'):
	#	outsupport.append('vst3')
	if 'vst2' in supportedplugs and plugin_vst2.check_exists('id', 1935111024):
		outsupport.append('vst2')
	return outsupport

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
		for p in cvpj_auto.iter(): self.add_point(p.pos,p.value,p.tension,p.type)

	def to_cvpj_vst2(self, convproj_obj, plugin_obj):
		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1935111024, 'chunk', data_nullbytegroup.make([{'graph': self.graph}, self.params]), None)

	def to_cvpj_any(self, convproj_obj, plugin_obj, supportedplugs):
		chunkdata = data_nullbytegroup.make([{'graph': self.graph}, self.params])
		if 'vst2' in supportedplugs and plugin_vst2.check_exists('id', 1935111024):
			plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id','any', 1935111024, 'chunk', chunkdata, None)

