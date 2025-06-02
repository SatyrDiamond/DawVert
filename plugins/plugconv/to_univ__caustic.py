# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from objects.inst_params import fx_delay
import math

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'

	def get_priority(self):
		return 0

	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = 'native:caustic'
		in_dict['in_daws'] = ['caustic']
		in_dict['out_plugins'] = ['universal']
		in_dict['out_daws'] = []

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		return False

		#if plugin_obj.type.check_wildmatch('native', 'caustic', 'master_delay'):
		#	delay_obj = fx_delay.fx_delay()
		#	delay_obj.feedback_first = False
		#	timing_obj = delay_obj.timing_add(0)
		#	timing_obj.set_steps(4, convproj_obj)
		#	delay_obj.feedback[0] = plugin_obj.params.get('2', 0).value
		#	delay_obj.to_cvpj(convproj_obj, pluginid)
		#	return True