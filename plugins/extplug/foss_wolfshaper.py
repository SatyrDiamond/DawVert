# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from objects import globalstore
from functions_plugin_ext import data_nullbytegroup
from functions_plugin_ext import plugin_vst2

DATASETPATH = './data_ext/dataset/wolf_plugins.dset'
DATASETNAME = 'wolf_plugins'

class extplugin(plugins.base):
	def __init__(self): 
		self.plugin_data = None
		self.plugin_type = None

	def is_dawvert_plugin(self): return 'extplugin'
	def get_shortname(self): return 'wolfshaper'
	def get_name(self): return 'Wolf Shaper'
	def get_prop(self, in_dict): 
		in_dict['ext_formats'] = ['vst2']
		in_dict['type'] = 'wolf-plugins'
		in_dict['subtype'] = 'wolfshaper'

	def check_exists(self, inplugname):
		outlist = []
		if plugin_vst2.check_exists('id', 1935111024): outlist.append('vst2')
		return outlist

	def check_plug(self, plugin_obj): 
		if plugin_obj.check_wildmatch('external', 'vst2', None):
			if plugin_obj.datavals_global.match('fourid', 1935111024): return 'vst2'
		return None

	def decode_data(self, plugintype, plugin_obj):
		if plugintype == 'vst2':
			chunkdata = plugin_obj.rawdata_get('chunk')
			self.plugin_data = data_nullbytegroup.get(chunkdata)
			self.plugin_type = 'vst2'
			return True

	def encode_data(self, plugintype, convproj_obj, plugin_obj, extplat):
		if plugintype == 'vst2':
			chunkdata = data_nullbytegroup.make(self.plugin_data)
			plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', extplat, 1935111024, 'chunk', chunkdata, None)
			return True

	def params_from_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)

		if self.plugin_data:
			if len(self.plugin_data)>1:
				ws_graph = self.plugin_data[0]
				ws_params = self.plugin_data[1]
				for valuepack, extparamid, paramnum in manu_obj.dset_remap_ext_to_cvpj__pre(DATASETNAME, 'plugin', 'wolfshaper', plugintype):
					if extparamid in ws_params: valuepack.value = float(ws_params[extparamid])

				plugin_obj.replace('user', 'wolf-plugins', 'wolfshaper')

				manu_obj.dset_remap_ext_to_cvpj__post(DATASETNAME, 'plugin', 'wolfshaper', plugintype)

				p_graph = [x.split(',') for x in (ws_graph['graph'].split(';'))]

				autopoints_obj = plugin_obj.env_points_add('shape', 1, True, 'float')
				for posX,posY,tension,pointtype in p_graph[:-1]:
					tension = float.fromhex(tension)
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = float.fromhex(posX)
					autopoint_obj.value = float.fromhex(posY)
					if pointtype == 2: autopoint_obj.tension = (-tension)/-100
					elif pointtype == 3: autopoint_obj.tension = (tension-100)/0.2
					else: autopoint_obj.tension = tension/-100
					autopoint_obj.type = ['normal','doublecurve','stairs','wave'][int(pointtype)]
				return True
		return False


	def params_to_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)

		graph = ''
		params = {}

		for valuepack, extparamid, paramnum in manu_obj.dset_remap_cvpj_to_ext__pre(DATASETNAME, 'plugin', 'wolfshaper', plugintype):
			params[extparamid] = float(valuepack)
		
		plugin_obj.replace('external', 'vst2', None)
		manu_obj.dset_remap_cvpj_to_ext__post(DATASETNAME, 'plugin', 'wolfshaper', plugintype)
		for p in plugin_obj.env_points_get('shape'):
			tension = p.tension
			if p.type == 'normal': pointtype = 0
			elif p.type in ['doublecurve', 'doublecurve2', 'doublecurve3']: pointtype = 1
			elif p.type == 'stairs': 
				pointtype = 2
				tension *= -1
			elif p.type == 'wave': 
				pointtype = 3
				tension = ((abs(tension)*-1)+100)*0.2
			else: 
				pointtype = 1
			graph += float.hex(p.pos)+','+float.hex(p.value)+','+float.hex(tension*-100)+','+str(int(pointtype))+';'
		self.plugin_data = [{'graph': graph}, params]
		return True