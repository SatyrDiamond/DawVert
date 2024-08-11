# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import struct
from functions_plugin_ext import plugin_vst2

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def getplugconvinfo(self, plugconv_ext_obj): 
		plugconv_ext_obj.in_plugin = ['native-onlineseq', None]
		plugconv_ext_obj.ext_formats = ['vst2']
		plugconv_ext_obj.plugincat = ['foss']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype):

		if plugin_obj.type.subtype == 'distort' and 'vst2' in extplugtype:
			extpluglog.extpluglist.add('FOSS', 'VST', 'Density2', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Density2')
			if exttype:
				extpluglog.extpluglist.success('Online Sequencer', 'Distortion')
				distort_type = plugin_obj.params.get('distort_type', 0).value
				if distort_type == [10, 6]: distlevel = 0.3
				else: distlevel = 0.5

				plugin_obj.replace('airwindows', 'density2')
				plugin_obj.params.add('density', distlevel, 'float')
				plugin_obj.params.add('highpass', 0, 'float')
				plugin_obj.params.add('output', 1, 'float')
				plugin_obj.params.add('dry_wet', 1, 'float')
				plugin_obj.to_ext_plugin(convproj_obj, pluginid, 'vst2', 'any')
				return True

		else: return False