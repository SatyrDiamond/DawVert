# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from objects import globalstore
from functions import data_xml
from functions_plugin_ext import data_nullbytegroup
from functions_plugin_ext import plugin_vst2

DATASETPATH = './data_ext/dataset/castello_reverb.dset'
DATASETNAME = 'castello_reverb'

class extplugin(plugins.base):
	def __init__(self): 
		self.plugin_data = None
		self.plugin_type = None

	def is_dawvert_plugin(self): return 'extplugin'
	def get_shortname(self): return 'castello'
	def get_name(self): return 'Castello Reverb'
	def get_prop(self, in_dict): 
		in_dict['ext_formats'] = ['vst2']
		in_dict['type'] = 'lucianoiam'
		in_dict['subtype'] = 'castello'

	def check_exists(self, inplugname):
		outlist = []
		if plugin_vst2.check_exists('id', 1279878002): outlist.append('vst2')
		return outlist

	def check_plug(self, plugin_obj): 
		if plugin_obj.check_wildmatch('external', 'vst2', None):
			if plugin_obj.datavals_global.match('fourid', 1279878002): return 'vst2'
		return None

	def decode_data(self, plugintype, plugin_obj):
		if plugintype in ['vst2']:
			chunkdata = plugin_obj.rawdata_get('chunk')
			self.plugin_data = data_nullbytegroup.get(chunkdata)
			self.plugin_type = chunkdata
			return True

	def encode_data(self, plugintype, convproj_obj, plugin_obj, extplat):
		if not (self.plugin_data is None):
			if plugintype == 'vst2':
				chunkdata = data_nullbytegroup.make(self.plugin_data)
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', extplat, 1279878002, 'chunk', chunkdata, None)
				return True

	def params_from_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
		if not (self.plugin_data is None):
			if len(self.plugin_data)>1:
				cr_params = self.plugin_data[1]
				for valuepack, extparamid, paramnum in manu_obj.dset_remap_ext_to_cvpj__pre(DATASETNAME, 'plugin', 'main', plugintype):
					if extparamid in cr_params: valuepack.value = float(cr_params[extparamid])
			plugin_obj.replace('user', 'lucianoiam', 'castello')
			manu_obj.dset_remap_ext_to_cvpj__post(DATASETNAME, 'plugin', 'main', plugintype)
			return True
		return False

	def params_to_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
		params = {}
		for valuepack, extparamid, paramnum in manu_obj.dset_remap_cvpj_to_ext__pre(DATASETNAME, 'plugin', 'main', plugintype):
			params[extparamid] = float(valuepack)
		plugin_obj.replace('external', 'vst2', None)
		manu_obj.dset_remap_cvpj_to_ext__post(DATASETNAME, 'plugin', 'main', plugintype)
		self.plugin_data = [{'ui_size': ''}, params]
		return True