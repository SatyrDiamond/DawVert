# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import os
import logging
import numpy as np
from functions_plugin_ext import plugin_vst2
from objects import globalstore

DATASETPATH = './data_ext/dataset/airwindows.dset'
DATASETNAME = 'airwindows'

logger_plugins = logging.getLogger('plugins')

dt_cvpj = np.dtype([
		('name', np.str_, 32),
		('vst2_id', np.uint32), 
		('numparams', np.uint8), 
		('params', [
			('def', np.float32),
			('visname', np.str_, 16),
			('paramid', np.str_, 16)]
			, 16),
		])

class arwindb():
	dbdata = np.zeros(0, dtype=dt_cvpj)
	db_filename = './data_ext/json/airwindows.json'

	def load_db():
		if not len(arwindb.dbdata) and os.path.exists(arwindb.db_filename):
			f = open(arwindb.db_filename, 'rb')
			airwindowdict = json.load(f)
			arwindb.dbdata = np.zeros(len(airwindowdict), dtype=dt_cvpj)
			for num, awd in enumerate(airwindowdict.items()):
				name, plugind = awd
				entry = arwindb.dbdata[num]
				params = entry['params']
				entry['name'] = name
				if 'vst2_id' in plugind: entry['vst2_id'] = plugind['vst2_id']
				if 'vals' in plugind: entry['numparams'] = len(plugind['vals'])
				for pn, val in enumerate(plugind['vals']): params[pn][0] = val
				for pn, val in enumerate(plugind['names']): params[pn][1] = val
				for pn, val in enumerate(plugind['cvpjparams']): params[pn][2] = val
			logger_plugins.info('Loaded Airwindows JSON')

class extplugin(plugins.base):
	def __init__(self): 
		self.plugin_data = None
		self.plugin_type = None

	def is_dawvert_plugin(self): return 'extplugin'
	def get_shortname(self): return 'airwindows'
	def get_name(self): return 'Airwindows'
	def get_prop(self, in_dict): 
		in_dict['ext_formats'] = ['vst2']
		in_dict['type'] = 'airwindows'

	def check_exists(self, inplugname):
		arwindb.load_db()
		outlist = []
		namefound = np.where(inplugname==arwindb.dbdata['name'])
		if len(namefound):
			vstid = int(arwindb.dbdata['vst2_id'][namefound[0]][0])
			if plugin_vst2.check_exists('id', vstid): 
				outlist.append('vst2')
		return outlist

	def check_plug(self, plugin_obj): 
		if plugin_obj.check_wildmatch('external', 'vst2', None):
			arwindb.load_db()
			checkvst = plugin_obj.datavals_global.get('fourid', 0)
			if checkvst in arwindb.dbdata['vst2_id']: return 'vst2'
		return None

	# ----------------------------------------- PARAMS DATA -----------------------------------------

	def decode_data(self, plugintype, plugin_obj):
		arwindb.load_db()
		if plugintype == 'vst2':
			checkvst = plugin_obj.datavals_global.get('fourid', 0)
			namefound = np.where(checkvst==arwindb.dbdata['vst2_id'])[0]
			if len(namefound):
				chunkdata = plugin_obj.rawdata_get('chunk')
				dbd = arwindb.dbdata[namefound[0]]
				params = np.asarray(dbd['params']['def'].copy(), dtype=np.float32)
				if chunkdata: params[0:len(chunkdata)//4] = np.frombuffer(chunkdata, dtype=np.float32)
				self.plugin_data = [dbd, params]
				self.plugin_type = 'vst2'

	def encode_data(self, plugintype, convproj_obj, plugin_obj, extplat):
		if plugintype == 'vst2' and self.plugin_data:
			dbd, paramdata = self.plugin_data
			plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', extplat, int(dbd['vst2_id']), 'chunk', paramdata[0:dbd['numparams']].tobytes(), None)
			for n in range(dbd['numparams']):
				param_obj = plugin_obj.params.add('ext_param_'+str(n), paramdata[n], 'float')
				param_obj.visual.name = dbd['params']['visname'][n]

	def params_from_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		if not (self.plugin_data is None):
			dbd, paramdata = self.plugin_data
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			for n in range(dbd['numparams']):
				manu_obj.from_param(str(n), 'ext_param_'+str(n), float(paramdata[n]))
			plugin_obj.replace('user', 'airwindows', dbd['name'])
			for n in range(dbd['numparams']):
				manu_obj.to_param(str(n), dbd['params'][n][2], dbd['params'][n][1])
			return True
		return False

	def params_to_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		arwindb.load_db()
		namefound = np.where(plugin_obj.type.subtype==arwindb.dbdata['name'])[0]
		if len(namefound):
			dbd = arwindb.dbdata[namefound[0]]
			paramdata = np.zeros(16, dtype=np.float32)
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			for n in range(dbd['numparams']):
				aw_paramname = dbd['params']['paramid'][n]
				aw_paramdef = dbd['params']['def'][n]
				aw_paramval = float(plugin_obj.params.get(aw_paramname, aw_paramdef))
				manu_obj.from_param(str(n), dbd['params'][n][2], dbd['params'][n][0])
				paramdata[n] = aw_paramval
			for n in range(dbd['numparams']):
				manu_obj.to_param(str(n), 'ext_param_'+str(n), dbd['params']['visname'][n])
			self.plugin_data = [dbd, paramdata]
			return True
		return False