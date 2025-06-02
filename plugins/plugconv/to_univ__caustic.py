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
		if plugin_obj.type.check_wildmatch('native', 'caustic', 'mixer_eq'):
			bass = plugin_obj.params.get('bass', 0).value
			mid = plugin_obj.params.get('mid', 0).value
			high = plugin_obj.params.get('high', 0).value

			plugin_obj.replace('universal', 'eq', 'bands')
			filter_obj, filter_id = plugin_obj.eq_add()
			filter_obj.freq = 200
			filter_obj.type.set('low_shelf', None)
			filter_obj.gain = (bass-1)*6
			convproj_obj.automation.calc(['plugin', pluginid, 'bass'], 'addmul', -1, 6, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'bass'], ['n_filter', pluginid, filter_id, 'gain'])

			filter_obj, filter_id = plugin_obj.eq_add()
			filter_obj.freq = 1000
			filter_obj.type.set('peak', None)
			filter_obj.gain = (mid-1)*6
			convproj_obj.automation.calc(['plugin', pluginid, 'mid'], 'addmul', -1, 6, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'mid'], ['n_filter', pluginid, filter_id, 'gain'])

			filter_obj, filter_id = plugin_obj.eq_add()
			filter_obj.freq = 8000
			filter_obj.type.set('high_shelf', None)
			filter_obj.gain = (high-1)*6
			convproj_obj.automation.calc(['plugin', pluginid, 'high'], 'addmul', -1, 6, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'high'], ['n_filter', pluginid, filter_id, 'gain'])
			return True

		#if plugin_obj.type.check_wildmatch('native', 'caustic', 'master_delay'):
		#	delay_obj = fx_delay.fx_delay()
		#	delay_obj.feedback_first = False
		#	timing_obj = delay_obj.timing_add(0)
		#	timing_obj.set_steps(4, convproj_obj)
		#	delay_obj.feedback[0] = plugin_obj.params.get('2', 0).value
		#	delay_obj.to_cvpj(convproj_obj, pluginid)
		#	return True