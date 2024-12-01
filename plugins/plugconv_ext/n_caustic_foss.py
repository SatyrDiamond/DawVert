# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import struct
from functions import extpluglog
from functions_plugin_ext import plugin_vst2

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv_ext'

	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'caustic', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):

		if plugin_obj.type.subtype == 'ORGN':
			extpluglog.extpluglist.add('FOSS', 'VST2', 'Organ', 'SocaLabs')
			exttype = plugins.base.extplug_exists('socalabs', extplugtype, 'organ')
			if exttype:
				extpluglog.extpluglist.success('Caustic', 'Organ')

				manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
				manu_obj.from_param('24', 'bar1', 0)
				manu_obj.from_param('25', 'bar2', 0)
				manu_obj.from_param('26', 'bar3', 0)
				manu_obj.from_param('27', 'bar4', 0)
				manu_obj.from_param('28', 'bar5', 0)
				manu_obj.from_param('29', 'bar6', 0)
				manu_obj.from_param('30', 'bar7', 0)
				manu_obj.from_param('31', 'bar8', 0)
				manu_obj.from_param('32', 'bar9', 0)

				manu_obj.calc('bar1', 'from_one', -8, 0, 0, 0)
				manu_obj.calc('bar2', 'from_one', -8, 0, 0, 0)
				manu_obj.calc('bar3', 'from_one', -8, 0, 0, 0)
				manu_obj.calc('bar4', 'from_one', -8, 0, 0, 0)
				manu_obj.calc('bar5', 'from_one', -8, 0, 0, 0)
				manu_obj.calc('bar6', 'from_one', -8, 0, 0, 0)
				manu_obj.calc('bar7', 'from_one', -8, 0, 0, 0)
				manu_obj.calc('bar8', 'from_one', -8, 0, 0, 0)
				manu_obj.calc('bar9', 'from_one', -8, 0, 0, 0)

				plugin_obj.replace('user', 'socalabs', 'organ')

				manu_obj.to_param('bar1', 'upper1', 0)
				manu_obj.to_param('bar2', 'upper2', 0)
				manu_obj.to_param('bar3', 'upper3', 0)
				manu_obj.to_param('bar4', 'upper4', 0)
				manu_obj.to_param('bar5', 'upper5', 0)
				manu_obj.to_param('bar6', 'upper6', 0)
				manu_obj.to_param('bar7', 'upper7', 0)
				manu_obj.to_param('bar8', 'upper8', 0)
				manu_obj.to_param('bar9', 'upper9', 0)

				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		return False