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
		return 'wavtool'
	
	def get_name(self):
		return 'Wavtool'
	
	def is_dawvert_plugin(self):
		return 'externalsearch'
	
	def get_prop(self, in_dict): 
		in_dict['supported_os'] = ['win']

	def import_plugins(self):
		path_wavtool = os.path.join(globalstore.home_folder, "AppData", "Roaming", "WavTool Bridge", 'WavTool Bridge.settings')
		vst2count = 0

		if os.path.exists(path_wavtool):
			vstxmldata = ET.parse(path_wavtool)
			vstxmlroot = vstxmldata.getroot()
			for x in vstxmlroot:
				if x.tag and x.get('name') == 'pluginLists':
					x_PluginLists = x.findall('PluginLists')
					if x_PluginLists:
						x_PluginListByArchitecture = x_PluginLists[0].findall('PluginListByArchitecture')
						if x_PluginListByArchitecture:
							x_KNOWNPLUGINS = x_PluginListByArchitecture[0].findall('KNOWNPLUGINS')
							for p in x_KNOWNPLUGINS[0]:
								if p.tag == 'PLUGIN' and p.get('format') == 'VST':
									descriptiveName = p.get('descriptiveName')

									with globalstore.extplug.add('vst2', globalstore.os_platform) as pluginfo_obj:
										pluginfo_obj.id = int(p.get('uniqueId'), 16)
										pluginfo_obj.name = descriptiveName if descriptiveName else p.get('name')
										pluginfo_obj.creator = p.get('manufacturer')
										pluginfo_obj.version = p.get('version')
										pluginfo_obj.path_64bit = p.get('file')
										pluginfo_obj.audio_num_inputs = int(p.get('numInputs'))
										pluginfo_obj.audio_num_outputs = int(p.get('numOutputs'))
									vst2count += 1

		print('[wavtool_bridge] VST2: '+str(vst2count))
