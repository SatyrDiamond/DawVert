# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import struct
from functions_plugin_ext import plugin_vst2
from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'tracktion', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):

		if plugin_obj.type.check_match('native', 'tracktion', 'distortion') and 'vst2' in extplugtype:
			dtype = plugin_obj.params.get('dtype', 0).value
			drive = plugin_obj.params.get('drive', 0).value
			postGain = plugin_obj.params.get('postGain', 0).value
			if dtype not in [0, 5]:
				extpluglog.extpluglist.add('FOSS', 'VST', 'Mackity', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Mackity')
				if exttype:
					extpluglog.extpluglist.success('Waveform', 'Distortion')
					plugin_obj.replace('user', 'airwindows', 'mackity')
					plugin_obj.params.add('in_trim', drive, 'float')
					plugin_obj.params.add('out_pad', postGain, 'float')
					plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
					return True
			elif dtype == 0:
				extpluglog.extpluglist.add('FOSS', 'VST', 'Drive', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Drive')
				if exttype:
					extpluglog.extpluglist.success('Waveform', 'Distortion')
					plugin_obj.replace('user', 'airwindows', 'drive')
					plugin_obj.params.add('drive', drive, 'float')
					plugin_obj.params.add('highpass', 0, 'float')
					plugin_obj.params.add('out_level', postGain, 'float')
					plugin_obj.params.add('dry_wet', 1, 'float')
					plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
					return True
