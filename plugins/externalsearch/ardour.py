# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import plugins
from os.path import exists
from pathlib import Path
import xml.etree.ElementTree as ET
from objects import globalstore

class plugsearch(plugins.base):
	def __init__(self): pass
	def get_shortname(self): return 'ardour'
	def get_name(self): return 'Ardour'
	def is_dawvert_plugin(self): return 'externalsearch'
	def get_prop(self, in_dict): in_dict['supported_os'] = ['win', 'lin']
	def import_plugins(self):
		searchpath = None
		if globalstore.os_platform == 'win': searchpath = os.path.join(globalstore.home_folder, "AppData", "Local", "Ardour8", "cache", "vst")
		if globalstore.os_platform == 'lin': searchpath = os.path.join(globalstore.home_folder, ".cache", "ardour6", "vst")
		if searchpath:
			vst2count = 0
			vst3count = 0
			if os.path.exists(searchpath):
				vstcachelist = os.listdir(searchpath)
				for vstcache in vstcachelist:
					vstxmlfile = vstcache
					vstxmlpath = os.path.join(searchpath, vstxmlfile)
					vstxmlext = Path(vstxmlfile).suffix
					vstxmldata = ET.parse(vstxmlpath)
					vstxmlroot = vstxmldata.getroot()

					if vstxmlext == '.v2i':
						x_pluginfo = vstxmlroot.findall('VST2Info')[0]
						vst_arch = vstxmlroot.get('arch')
						vst_category = x_pluginfo.get('category')

						if vst_arch == 'x86_64' and exists(vstxmlroot.get('binary')):
							vst2data_fourid = int(x_pluginfo.get('id'))
							if vst2data_fourid < 0: vst2data_fourid = int(x_pluginfo.get('id')) + 2**32

							if vst_category == 'Instrument': vst2data_type = 'synth'
							elif vst_category == 'Effect': vst2data_type = 'fx'
							else: vst2data_type = None

							if vst2data_type:
								with globalstore.extplug.add('vst2', globalstore.os_platform) as pluginfo_obj: 
									pluginfo_obj.id = vst2data_fourid
									pluginfo_obj.name = x_pluginfo.get('name')
									pluginfo_obj.creator = x_pluginfo.get('creator')
									pluginfo_obj.path_64bit = vstxmlroot.get('binary')
									pluginfo_obj.type = vst2data_type
									pluginfo_obj.version = x_pluginfo.get('version')
									pluginfo_obj.audio_num_inputs = x_pluginfo.get('n_inputs')
									pluginfo_obj.audio_num_outputs = x_pluginfo.get('n_outputs')
									pluginfo_obj.midi_num_inputs = x_pluginfo.get('n_midi_inputs')
									pluginfo_obj.midi_num_outputs = x_pluginfo.get('n_midi_outputs')
									vst2count += 1

					if vstxmlext == '.v3i':
						VST3Info = vstxmlroot.findall('VST3Info')[0]
						vst3data_id = VST3Info.get('uid')
						if exists(vstxmlroot.get('bundle')):
							with globalstore.extplug.add('vst3', globalstore.os_platform) as pluginfo_obj: 
								pluginfo_obj.id = vst3data_id
								pluginfo_obj.path_64bit = vstxmlroot.get('bundle')
								pluginfo_obj.name = VST3Info.get('name')
								pluginfo_obj.creator = VST3Info.get('vendor')
								pluginfo_obj.category = VST3Info.get('category')
								pluginfo_obj.version = VST3Info.get('version')
								pluginfo_obj.sdk_version = VST3Info.get('sdk-version')
								pluginfo_obj.url = VST3Info.get('url')
								pluginfo_obj.email = VST3Info.get('email')
								pluginfo_obj.audio_num_inputs = VST3Info.get('n_inputs')
								pluginfo_obj.audio_num_outputs = VST3Info.get('n_outputs')
								pluginfo_obj.midi_num_inputs = VST3Info.get('n_midi_inputs')
								pluginfo_obj.midi_num_outputs = VST3Info.get('n_midi_outputs')
								vst3count += 1
				print('[ardour] VST2: '+str(vst2count)+', VST3: '+str(vst3count))

		else:
			return False
