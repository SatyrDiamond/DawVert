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
		in_dict['in_plugin'] = ['native', 'onlineseq', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype):

		if plugin_obj.type.subtype == 'distort':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Density2', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Density2')
			if exttype:
				extpluglog.extpluglist.success('Online Sequencer', 'Distortion')
				distort_type = plugin_obj.params.get('distort_type', 0).value
				if distort_type == [10, 6]: distlevel = 0.3
				else: distlevel = 0.5

				plugin_obj.replace('user', 'airwindows', 'density2')
				plugin_obj.params.add('density', distlevel, 'float')
				plugin_obj.params.add('highpass', 0, 'float')
				plugin_obj.params.add('output', 1, 'float')
				plugin_obj.params.add('dry_wet', 1, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		else: return False