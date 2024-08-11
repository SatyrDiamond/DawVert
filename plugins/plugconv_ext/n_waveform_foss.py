# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import struct
from functions_plugin_ext import plugin_vst2
from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def getplugconvinfo(self, plugconv_ext_obj): 
		plugconv_ext_obj.in_plugin = ['native-tracktion', None]
		plugconv_ext_obj.ext_formats = ['vst2']
		plugconv_ext_obj.plugincat = ['foss']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype):

		if plugin_obj.type.subtype == 'distortion' and 'vst2' in extplugtype:
			dtype = plugin_obj.params.get('dtype', 0).value
			drive = plugin_obj.params.get('drive', 0).value
			postGain = plugin_obj.params.get('postGain', 0).value
			if dtype not in [0, 5]:
				extpluglog.extpluglist.add('FOSS', 'VST', 'Mackity', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Mackity')
				if exttype:
					extpluglog.extpluglist.success('Waveform', 'Distortion')
					plugin_obj.replace('airwindows', 'mackity')
					plugin_obj.params.add('in_trim', drive, 'float')
					plugin_obj.params.add('out_pad', postGain, 'float')
					plugin_obj.to_ext_plugin(convproj_obj, pluginid, 'vst2', 'any')
					return True
			elif dtype == 0:
				extpluglog.extpluglist.add('FOSS', 'VST', 'Drive', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Drive')
				if exttype:
					extpluglog.extpluglist.success('Waveform', 'Distortion')
					plugin_obj.replace('airwindows', 'drive')
					plugin_obj.params.add('drive', drive, 'float')
					plugin_obj.params.add('highpass', 0, 'float')
					plugin_obj.params.add('out_level', postGain, 'float')
					plugin_obj.params.add('dry_wet', 1, 'float')
					plugin_obj.to_ext_plugin(convproj_obj, pluginid, 'vst2', 'any')
					return True
