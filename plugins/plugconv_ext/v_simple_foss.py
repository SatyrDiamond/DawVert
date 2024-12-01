# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import struct
from functions_plugin_ext import plugin_vst2
from functions import extpluglog

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv_ext'

	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['simple', None, None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):
		fx_on, fx_wet = plugin_obj.fxdata_get()

		if plugin_obj.type.check_wildmatch('simple', 'reverb', None):
			extpluglog.extpluglist.add('FOSS', 'VST', 'Reverb', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Reverb')
			if exttype:
				extpluglog.extpluglist.success('SimpleFX', 'Reverb')
				plugin_obj.fxdata_add(fx_on, 1)
				
				plugin_obj.replace('user', 'airwindows', 'reverb')
				plugin_obj.params.add('big', 0.5, 'float')
				plugin_obj.params.add('wet', fx_wet, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		if plugin_obj.type.check_wildmatch('simple', 'chorus', None):
			extpluglog.extpluglist.add('FOSS', 'VST', 'Chorus', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Chorus')
			if exttype:
				extpluglog.extpluglist.success('SimpleFX', 'Chorus')
				amount = plugin_obj.params.get('amount', 0).value/2.5

				plugin_obj.replace('user', 'airwindows', 'chorus')
				plugin_obj.params.add('speed', 0.5, 'float')
				plugin_obj.params.add('range', amount/2.5, 'float')
				plugin_obj.params.add('dry_wet', 1, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		if plugin_obj.type.check_wildmatch('simple', 'tremelo', None):
			extpluglog.extpluglist.add('FOSS', 'VST', 'Tremolo', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Tremolo')
			if exttype:
				extpluglog.extpluglist.success('SimpleFX', 'Tremolo')

				plugin_obj.replace('user', 'airwindows', 'tremolo')
				plugin_obj.params.add('speed', 0.5, 'float')
				plugin_obj.params.add('depth', 0.5, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		if plugin_obj.type.check_wildmatch('simple', 'distortion', None):
			extpluglog.extpluglist.add('FOSS', 'VST', 'Drive', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Drive')
			if exttype:
				extpluglog.extpluglist.success('SimpleFX', 'Distortion')
				plugin_obj.fxdata_add(fx_on, 1)
				amount = plugin_obj.params.get('amount', 0).value

				plugin_obj.replace('user', 'airwindows', 'drive')
				plugin_obj.params.add('drive', amount, 'float')
				plugin_obj.params.add('highpass', 0, 'float')
				plugin_obj.params.add('out_level', 1-(amount/2), 'float')
				plugin_obj.params.add('dry_wet', fx_wet, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		if plugin_obj.type.check_wildmatch('simple', 'bassboost', None):
			extpluglog.extpluglist.add('FOSS', 'VST', 'Weight', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Weight')
			if exttype:
				extpluglog.extpluglist.success('SimpleFX', 'BassBoost')

				plugin_obj.replace('user', 'airwindows', 'weight')
				plugin_obj.params.add('freq', 1, 'float')
				plugin_obj.params.add('weight', 1, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		return False