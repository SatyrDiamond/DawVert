# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import plugins
from os.path import exists
from pathlib import Path
import xml.etree.ElementTree as ET
from objects import globalstore

def muse_getvalue(fallback, xmldata, name):
		outval = xmldata.findall(name)
		if outval == []: return fallback
		else: return outval[0].text

class plugsearch(plugins.base):
	def get_shortname(self):
		return 'muse'
	
	def get_name(self):
		return 'MusE'
	
	def is_dawvert_plugin(self):
		return 'externalsearch'
	
	def get_prop(self, in_dict):
		in_dict['supported_os'] = ['lin']
	
	def import_plugins(self):
		l_path_muse = os.path.join(globalstore.home_folder,".cache", "MusE", "MusE", "scanner")
		vst2count = 0
		ladspacount = 0

		muse_g_path_vst = l_path_muse+'/linux_vst_plugins.scan'
		muse_g_path_ladspa = l_path_muse+'/ladspa_plugins.scan'
		muse_g_path_dssi = l_path_muse+'/dssi_plugins.scan'

		if os.path.exists(muse_g_path_vst):
			path_vst_linux = muse_g_path_vst
			vstxmldata = ET.parse(path_vst_linux)
			vstxmlroot = vstxmldata.getroot()
			for x_vst_plug_cache in vstxmlroot:
				muse_file = x_vst_plug_cache.get('file')
				if os.path.exists(muse_file):
					with globalstore.extplug.add('vst2', globalstore.os_platform) as pluginfo_obj: 
						pluginfo_obj.id = muse_getvalue(None, x_vst_plug_cache, 'uniqueID')
						pluginfo_obj.name = muse_getvalue(None, x_vst_plug_cache, 'name')
						pluginfo_obj.creator = muse_getvalue(None, x_vst_plug_cache, 'maker')
						pluginfo_obj.audio_num_inputs = muse_getvalue(0, x_vst_plug_cache, 'inports')
						pluginfo_obj.audio_num_outputs = muse_getvalue(0, x_vst_plug_cache, 'outports')
						pluginfo_obj.num_params = muse_getvalue(0, x_vst_plug_cache, 'ctlInports')
						vst2count += 1

		if os.path.exists(muse_g_path_ladspa):
			path_ladspa_linux = muse_g_path_ladspa
			ladspaxmldata = ET.parse(path_ladspa_linux)
			ladspaxmlroot = ladspaxmldata.getroot()
			for x_ladspa_plug_cache in ladspaxmlroot:
				muse_file = x_ladspa_plug_cache.get('file')
				muse_label = x_ladspa_plug_cache.get('label')
				if os.path.exists(muse_file):
					with globalstore.extplug.add('ladspa', globalstore.os_platform) as pluginfo_obj: 
						pluginfo_obj.id = muse_getvalue(None, x_ladspa_plug_cache, 'uniqueID')
						pluginfo_obj.name = muse_getvalue(None, x_ladspa_plug_cache, 'name')
						pluginfo_obj.inside_id = muse_label
						pluginfo_obj.creator = muse_getvalue(None, x_ladspa_plug_cache, 'maker')
						pluginfo_obj.audio_num_inputs = muse_getvalue(0, x_ladspa_plug_cache, 'inports')
						pluginfo_obj.audio_num_outputs = muse_getvalue(0, x_ladspa_plug_cache, 'outports')
						pluginfo_obj.num_params = muse_getvalue(0, x_ladspa_plug_cache, 'ctlInports')
						pluginfo_obj.num_params_out = muse_getvalue(0, x_ladspa_plug_cache, 'ctlOutports')
						pluginfo_obj.path_unix = muse_file
						ladspacount += 1

		print('[muse] VST2: '+str(vst2count)+', LADSPA: '+str(ladspacount))
