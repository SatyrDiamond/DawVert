# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import lxml.etree as ET
from objects import globalstore
from functions import data_xml
from functions_plugin_ext import data_vc2xml
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import plugin_vst3

DATASETPATH = './data_ext/dataset/magical8bitplug2.dset'
DATASETNAME = 'magical8bitplug2'

class extplugin(plugins.base):
	def __init__(self): 
		self.plugin_data = None
		self.plugin_type = None

	def is_dawvert_plugin(self): return 'extplugin'
	def get_shortname(self): return 'magical8bitplug2'
	def get_name(self): return 'Magical8bitplug2'
	def get_prop(self, in_dict): 
		in_dict['ext_formats'] = ['vst2', 'vst3']
		in_dict['type'] = 'yokemura'
		in_dict['subtype'] = 'magical8bitplug2'

	def check_exists(self, inplugname):
		outlist = []
		if plugin_vst2.check_exists('id', 1937337962): outlist.append('vst2')
		if plugin_vst3.check_exists('id', 'ABCDEF019182FAEB596D636B73796E6A'): outlist.append('vst3')
		return outlist

	def check_plug(self, plugin_obj): 
		if plugin_obj.check_wildmatch('external', 'vst2', None):
			if plugin_obj.datavals_global.match('fourid', 1937337962): return 'vst2'
		if plugin_obj.check_wildmatch('external', 'vst3', None):
			if plugin_obj.datavals_global.match('id', 'ABCDEF019182FAEB596D636B73796E6A'): return 'vst3'
		return None

	def decode_data(self, plugintype, plugin_obj):
		if plugintype in ['vst2', 'vst3']:
			chunkdata = plugin_obj.rawdata_get('chunk')
			self.plugin_data = data_vc2xml.get(chunkdata)
			self.plugin_type = plugintype
			return True

	def encode_data(self, plugintype, convproj_obj, plugin_obj, extplat):
		if not (self.plugin_data is None):
			chunkdata = data_vc2xml.make(self.plugin_data)
			if plugintype == 'vst2':
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', extplat, 1937337962, 'chunk', chunkdata, None)
				return True
			if plugintype == 'vst3':
				plugin_vst3.replace_data(convproj_obj, plugin_obj, 'id', None, 'ABCDEF019182FAEB596D636B73796E6A', chunkdata)
				return True

	def params_from_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)

		if self.plugin_data:
			paramsxml = data_xml.find_first(self.plugin_data, 'Params')
			if paramsxml:
				params = {}
				for xmlpart in paramsxml:
					param_id = xmlpart.get('id')
					param_value = float(xmlpart.get('value'))
					params[param_id] = param_value

				for valuepack, extparamid, paramnum in manu_obj.dset_remap_ext_to_cvpj__pre(DATASETNAME, 'plugin', 'main', plugintype):
					if extparamid in params: valuepack.value = params[extparamid]
				plugin_obj.replace('user', 'yokemura', 'magical8bitplug2')
				manu_obj.dset_remap_ext_to_cvpj__post(DATASETNAME, 'plugin', 'main', plugintype)
			volumeEnv = data_xml.find_first(self.plugin_data, 'volumeEnv')
			pitchEnv = data_xml.find_first(self.plugin_data, 'pitchEnv')
			dutyEnv = data_xml.find_first(self.plugin_data, 'dutyEnv')

			for n, v in [["volumeEnv", volumeEnv], ["pitchEnv", pitchEnv], ["dutyEnv", dutyEnv]]:
				if not (v is None): 
					if v.text:
						outval = [int(x) for x in v.text.split(',')]
						plugin_obj.array_add(n, outval)
				return True
		return False

	def params_to_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
		params = {}
		xml_m8p_root = ET.Element("root")
		xml_m8p_params = ET.SubElement(xml_m8p_root, "Params")
		for valuepack, extparamid, paramnum in manu_obj.dset_remap_cvpj_to_ext__pre(DATASETNAME, 'plugin', 'main', plugintype):
			temp_xml = ET.SubElement(xml_m8p_params, 'PARAM')
			temp_xml.set('id', str(extparamid))
			temp_xml.set('value', str(valuepack))
		xml_m8p_dutyEnv = ET.SubElement(xml_m8p_root, "dutyEnv")
		xml_m8p_pitchEnv = ET.SubElement(xml_m8p_root, "pitchEnv")
		xml_m8p_volumeEnv = ET.SubElement(xml_m8p_root, "volumeEnv")

		plugin_obj.replace('external', 'vst2', None)
		manu_obj.dset_remap_cvpj_to_ext__post(DATASETNAME, 'plugin', 'main', plugintype)
		
		for n, x in [["volumeEnv", xml_m8p_volumeEnv], ["pitchEnv", xml_m8p_pitchEnv], ["dutyEnv", xml_m8p_dutyEnv]]:
			outdata = plugin_obj.array_get_vl(n)
			x.text = ','.join([str(p) for p in outdata])
		self.plugin_data = xml_m8p_root
		return True