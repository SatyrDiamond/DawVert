# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import os
import logging
import numpy as np
import lxml.etree as ET
from objects import globalstore
from functions_plugin_ext import data_vc2xml
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import plugin_vst3
from functions_plugin_ext import data_vstw

logger_plugins = logging.getLogger('plugins')

dt_socalabsdb = np.dtype([
		('name', np.str_, 32),
		('vst2_id', np.uint32), 
		('vst3_id', np.str_, 32)
		])

DATASETPATH = './data_ext/dataset/socalabs.dset'
DATASETNAME = 'socalabs'

class socalabsdb():
	dbdata = np.zeros(0, dtype=dt_socalabsdb)
	db_filename = './data_ext/json/socalabs.json'

	def load_db():
		if not len(socalabsdb.dbdata) and os.path.exists(socalabsdb.db_filename):
			f = open(socalabsdb.db_filename, 'rb')
			socalabdict = json.load(f)
			socalabsdb.dbdata = np.zeros(len(socalabdict), dtype=dt_socalabsdb)
			for num, awd in enumerate(socalabdict.items()):
				name, plugind = awd
				entry = socalabsdb.dbdata[num]
				entry['name'] = name
				if 'vst2_id' in plugind: entry['vst2_id'] = plugind['vst2_id']
				if 'vst3_id' in plugind: entry['vst3_id'] = plugind['vst3_id']
			logger_plugins.info('Loaded Socalabs JSON')

class extplugin(plugins.base):
	def __init__(self): 
		self.plugin_data = None
		self.plugin_type = None

	def is_dawvert_plugin(self): return 'extplugin'
	def get_shortname(self): return 'socalabs'
	def get_name(self): return 'Socalabs'
	def get_prop(self, in_dict): 
		in_dict['ext_formats'] = ['vst2', 'vst3']
		in_dict['type'] = 'socalabs'

	def check_exists(self, inplugname):
		socalabsdb.load_db()
		outlist = []
		namefound = np.where(inplugname==socalabsdb.dbdata['name'])
		if len(namefound):
			if plugin_vst2.check_exists('id', int(socalabsdb.dbdata['vst2_id'][namefound[0]])): 
				outlist.append('vst2')
			if plugin_vst3.check_exists('id', socalabsdb.dbdata['vst3_id'][namefound[0]]): 
				outlist.append('vst3')
		return outlist

	def check_plug(self, plugin_obj):
		socalabsdb.load_db()
		if plugin_obj.check_wildmatch('external', 'vst2', None):
			checkvst = plugin_obj.datavals_global.get('fourid', 0)
			if checkvst in socalabsdb.dbdata['vst2_id']: return 'vst2'
		if plugin_obj.check_wildmatch('external', 'vst3', None):
			checkvst = plugin_obj.datavals_global.get('id', '')
			if checkvst in socalabsdb.dbdata['vst3_id']: return 'vst3'
		return None

	def decode_data(self, plugintype, plugin_obj):
		socalabsdb.load_db()
		if plugintype == 'vst2':
			checkvst = plugin_obj.datavals_global.get('fourid', 0)
			namefound = np.where(checkvst==socalabsdb.dbdata['vst2_id'])[0]
			if len(namefound):
				chunkdata = plugin_obj.rawdata_get('chunk')
				dbd = socalabsdb.dbdata[namefound[0]]
				self.plugin_data = [dbd, ET.fromstring(chunkdata)]
				self.plugin_type = 'vst2'
				return True
		if plugintype == 'vst3':
			checkvst = plugin_obj.datavals_global.get('id', '')
			namefound = np.where(checkvst==socalabsdb.dbdata['vst3_id'])[0]
			if len(namefound):
				chunkdata = plugin_obj.rawdata_get('chunk')
				vstw_d = data_vstw.get(chunkdata)
				if vstw_d: 
					dbd = socalabsdb.dbdata[namefound[0]]
					self.plugin_data = [dbd, ET.fromstring(vstw_d)]
					self.plugin_type = 'vst3'
					return True

	def encode_data(self, plugintype, convproj_obj, plugin_obj, extplat):
		if plugintype == 'vst2' and self.plugin_data:
			dbd, paramdata = self.plugin_data
			plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', extplat, int(dbd['vst2_id']), 'chunk', ET.tostring(paramdata, encoding='utf-8'), None)
			return True
		if plugintype == 'vst3' and self.plugin_data:
			dbd, paramdata = self.plugin_data
			plugin_vst3.replace_data(convproj_obj, plugin_obj, 'id', extplat, str(dbd['vst3_id']), ET.tostring(paramdata, encoding='utf-8'))
			return True

	def params_from_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		if self.plugin_data:
			plugname = self.plugin_data[0]['name']
			manufile = '.\\data_ext\\remap\\socalabs\\'+plugname+'.csv'
			manuid = 'socalabs_'+plugname
			if os.path.exists(manufile):
				globalstore.paramremap.load(manuid, manufile)
				manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
				paramsxml = self.plugin_data[1]
				params = {}
				for xmlpart in paramsxml:
					if xmlpart.tag == 'param':
						param_id = xmlpart.get('uid')
						param_value = float(xmlpart.get('val'))
						params[param_id] = param_value

				for valuepack, extparamid, paramnum in manu_obj.remap_ext_to_cvpj__pre(manuid, plugintype):
					if extparamid in params: valuepack.value = params[extparamid]

				plugin_obj.replace('user', 'socalabs', plugname)
				manu_obj.remap_ext_to_cvpj__post(manuid, plugintype)
				return True
		return False

	def params_to_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		socalabsdb.load_db()
		namefound = np.where(plugin_obj.type.subtype==socalabsdb.dbdata['name'])[0]
		if len(namefound):
			dbd = socalabsdb.dbdata[namefound[0]]
			plugname = dbd['name']
			manufile = '.\\data_ext\\remap\\socalabs\\'+plugname+'.csv'
			manuid = 'socalabs_'+plugname
			x_sl_data = ET.Element("state")
			x_sl_data.set('valueTree', '<?xml version="1.0" encoding="UTF-8"?>')
			x_sl_data.set('program', '0')

			if os.path.exists(manufile):
				globalstore.paramremap.load(manuid, manufile)

				manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
				for valuepack, extparamid, paramnum in manu_obj.remap_cvpj_to_ext__pre(manuid, plugintype):
					temp_xml = ET.SubElement(x_sl_data, 'param')
					temp_xml.set('uid', str(extparamid))
					temp_xml.set('val', str(valuepack))
	
				plugin_obj.replace('external', 'vst2', None)
				manu_obj.remap_cvpj_to_ext__post(manuid, plugintype)
			
				self.plugin_data = [dbd, x_sl_data]
			return True
		return False