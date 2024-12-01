# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'

	def get_priority(self):
		return 0

	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'serato-fx', None]]
		in_dict['in_daws'] = ['serato']
		in_dict['out_plugins'] = [['universal', None, None]]
		in_dict['out_daws'] = []

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.type.check_wildmatch('native', 'serato-fx', 'Limiter.serato-effect-definition'):
			extpluglog.convinternal('Serato Studio', 'Limiter', 'Universal', 'Limiter')
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('amount', 'amount', 0)
			manu_obj.calc('amount', 'mul', 12, 0, 0, 0)
			plugin_obj.replace('universal', 'limiter', None)
			manu_obj.to_param('amount', 'gain', None)
			manu_obj.to_value(0, 'threshold', None, 'float')
			manu_obj.to_value(0.1, 'release', None, 'float')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'serato-fx', 'Decimate Crusher.serato-effect-definition'):
			extpluglog.convinternal('Serato Studio', 'Decimate Crusher', 'Universal', 'Bitcrush')
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('amount', 'amount', 0)
			manu_obj.calc('amount', 'pow', 0.1, 0, 0, 0)
			manu_obj.calc('amount', 'mul', 15500, 0, 0, 0)
			manu_obj.calc('amount', 'sub_r', 16000, 0, 0, 0)
			plugin_obj.replace('universal', 'bitcrush', None)
			manu_obj.to_param('amount', 'freq', None)
			manu_obj.to_value(16, 'bits', None, 'float')
			return 1

		return 2