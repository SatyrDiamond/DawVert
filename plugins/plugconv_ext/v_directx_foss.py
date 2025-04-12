# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import struct
from functions_plugin_ext import plugin_vst2
from functions import extpluglog
from functions import xtramath

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv_ext'

	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'directx', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']
		
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):
		fx_on, fx_wet = plugin_obj.fxdata_get()

		if plugin_obj.type.check_match('native', 'directx', 'Distortion'):
			extpluglog.extpluglist.add('FOSS', 'VST', 'Edge', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Edge')
			if exttype:
				extpluglog.extpluglist.success('DirectX', 'Distortion')
				p_gain = plugin_obj.params.get('gain', 0).value
				p_edge = plugin_obj.params.get('edge', 0).value
				p_prelowpasscutoff = plugin_obj.params.get('prelowpasscutoff', 0).value
				plugin_obj.replace('user', 'airwindows', 'edge')
				plugin_obj.params.add('gain', (p_gain*0.1)+0.1, 'float')
				plugin_obj.params.add('lowpass', p_prelowpasscutoff, 'float')
				plugin_obj.params.add('highpass', 0, 'float')
				plugin_obj.params.add('output', 1, 'float')
				plugin_obj.params.add('dry_wet', 1, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		else: return False