# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import io
from objects import globalstore
from functions_plugin_ext import plugin_vst2
from functions import data_values

DATASETPATH = './data_ext/dataset/kickmess.dset'
DATASETNAME = 'kickmess'

class extplugin(plugins.base):
	def __init__(self): 
		self.plugin_data = None
		self.plugin_type = None

	def is_dawvert_plugin(self): return 'extplugin'
	def get_shortname(self): return 'kickmess'
	def get_name(self): return 'Kickmess'
	def get_prop(self, in_dict): 
		in_dict['ext_formats'] = ['vst2']
		in_dict['type'] = 'weirdconstructor'
		in_dict['subtype'] = 'kickmess'

	def check_exists(self, inplugname):
		outlist = []
		if plugin_vst2.check_exists('id', 934843292): outlist.append('vst2')
		return outlist

	def check_plug(self, plugin_obj): 
		if plugin_obj.check_wildmatch('external', 'vst2', None):
			if plugin_obj.datavals_global.match('fourid', 934843292): return 'vst2'
		return None

	def decode_data(self, plugintype, plugin_obj):
		if plugintype == 'vst2':
			chunkdata = plugin_obj.rawdata_get('chunk')
			if chunkdata.startswith(b'!PARAMS;'):
				splitdata = chunkdata.split(b';')
				self.plugin_type = 'vst2'
				self.plugin_data = {}
				for x in splitdata:
					x = x.decode()
					if ':' in x:
						splittedtxt = x.strip().split(':')
						if len(splittedtxt)==2:
							v_group = splittedtxt[0].strip()
							if v_group not in self.plugin_data: self.plugin_data[v_group] = {}
							v_paramval = splittedtxt[1].strip()
							if '=' in v_paramval:
								v_name, v_value = v_paramval.split('=')
								self.plugin_data[v_group][v_name] = float(v_value)

	def encode_data(self, plugintype, convproj_obj, plugin_obj, extplat):
		if plugintype == 'vst2' and self.plugin_data:
			out = io.BytesIO()
			out.write(b'!PARAMS;\n')
			for g in self.plugin_data:
				for n, v in self.plugin_data[g].items():
					out.write(str.encode(g+' : '+n+'='+str(round(v, 4))+';\n'))
			chunkdata = out.getvalue()

			plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', extplat, 934843292, 'chunk', chunkdata, None)

	def params_from_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)

		if self.plugin_data:
			for valuepack, extparamid, paramnum in manu_obj.dset_remap_ext_to_cvpj__pre__one(DATASETNAME, 'plugin', 'main', plugintype):
				outval = data_values.dict__nested_get_value(self.plugin_data, extparamid.split('/'))
				if not (outval is None): valuepack.value = float(outval)
			plugin_obj.replace('user', 'weirdconstructor', 'kickmess')
			manu_obj.dset_remap_ext_to_cvpj__post(DATASETNAME, 'plugin', 'main', plugintype)
			return True
		return False

	def params_to_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
		self.plugin_data = {}
		for valuepack, extparamid, paramnum in manu_obj.dset_remap_cvpj_to_ext__pre__one(DATASETNAME, 'plugin', 'main', plugintype):
			data_values.dict__nested_add_value(self.plugin_data, extparamid.split('/'), valuepack.value)

		plugin_obj.replace('external', 'vst2', None)
		manu_obj.dset_remap_cvpj_to_ext__post(DATASETNAME, 'plugin', 'main', plugintype)
		return True