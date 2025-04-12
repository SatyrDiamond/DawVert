# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import struct
import math
from functions import extpluglog

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv_ext'

	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'serato-fx', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):
		if plugin_obj.type.subtype == 'Amphitheatre Reverb.serato-effect-definition':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Galactic', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Galactic')
			if exttype:
				extpluglog.extpluglist.success('Serato Studio', 'Amphitheatre Reverb')
				manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
				manu_obj.from_param('amount', 'amount', 0)
				manu_obj.calc('amount', 'div', 3, 0, 0, 0)
				plugin_obj.replace('user', 'airwindows', 'Galactic')
				manu_obj.to_value(0.5, 'replace', None, 'float')
				manu_obj.to_value(0.3, 'brightne', None, 'float')
				manu_obj.to_value(0.8, 'detune', None, 'float')
				manu_obj.to_value(0.5, 'bigness', None, 'float')
				manu_obj.to_param('amount', 'dry_wet', None)
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')

		if plugin_obj.type.subtype == 'Light Tail Reverb.serato-effect-definition':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Galactic', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Galactic')
			if exttype:
				extpluglog.extpluglist.success('Serato Studio', 'Light Tail Reverb')
				manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
				manu_obj.from_param('amount', 'amount', 0)
				manu_obj.calc('amount', 'div', 5, 0, 0, 0)
				plugin_obj.replace('user', 'airwindows', 'Galactic')
				manu_obj.to_value(0.6, 'replace', None, 'float')
				manu_obj.to_value(1, 'brightne', None, 'float')
				manu_obj.to_value(0.5, 'detune', None, 'float')
				manu_obj.to_value(0.7, 'bigness', None, 'float')
				manu_obj.to_param('amount', 'dry_wet', None)
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')

		if plugin_obj.type.subtype == 'Dry Reverb.serato-effect-definition':
			extpluglog.extpluglist.add('FOSS', 'VST', 'MatrixVerb', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'MatrixVerb')
			if exttype:
				extpluglog.extpluglist.success('Serato Studio', 'Dry Reverb')
				manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
				manu_obj.from_param('amount', 'amount', 0)
				manu_obj.calc('amount', 'pow', 2, 0, 0, 0)
				plugin_obj.replace('user', 'airwindows', 'MatrixVerb')
				manu_obj.to_value(1, 'filter', None, 'float')
				manu_obj.to_value(0.5, 'damping', None, 'float')
				manu_obj.to_value(0, 'speed', None, 'float')
				manu_obj.to_value(0, 'vibrato', None, 'float')
				manu_obj.to_value(0.2, 'rmsize', None, 'float')
				manu_obj.to_value(0, 'flavor', None, 'float')
				manu_obj.to_param('amount', 'dry_wet', None)
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')


		#else: return False