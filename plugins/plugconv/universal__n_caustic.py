# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from objects.inst_params import fx_delay
from functions import xtramath
from functions import extpluglog
import math

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'caustic', None]]
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = [['universal', None, None]]
		in_dict['out_daws'] = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):

		if plugin_obj.type.check_wildmatch('native', 'caustic', 'mixer_eq'):
			extpluglog.convinternal('Caustic 3', 'Mixer EQ', 'Universal', 'EQ Bands')
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
			return 1

		if plugin_obj.type.check_wildmatch('native', 'caustic', 'master_eq'):
			extpluglog.convinternal('Caustic 3', 'Master EQ', 'Universal', '3-Band EQ')
			p_low = plugin_obj.params.get('30', 0).value
			p_mid = plugin_obj.params.get('32', 0).value
			p_high = plugin_obj.params.get('34', 0).value

			p_low = p_low-1
			p_mid = p_mid-1
			p_high = p_high-1

			plugin_obj.replace('universal', 'eq', '3band')
			plugin_obj.params.add('low_gain', p_low*6, 'float')
			plugin_obj.params.add('mid_gain', p_mid*6, 'float')
			plugin_obj.params.add('high_gain', p_high*6, 'float')

			plugin_obj.params.add('lowmid_freq', 1000, 'float')
			plugin_obj.params.add('midhigh_freq', 6000, 'float')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'caustic', 'master_limiter'):
			extpluglog.convinternal('Caustic 3', 'Master Limiter', 'Universal', 'Limiter')
			plugin_obj.plugts_transform('./data_main/plugts/caustic_univ.pltr', 'limiter', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'caustic', 'master_reverb'):
			extpluglog.convinternal('Caustic 3', 'Master Reverb', 'Universal', 'Reverb')
			plugin_obj.plugts_transform('./data_main/plugts/caustic_univ.pltr', 'master_reverb', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'caustic', 'master_delay'):
			extpluglog.convinternal('Caustic 3', 'Master Delay', 'Universal', 'Delay')
			delay_obj = fx_delay.fx_delay()
			delay_obj.feedback_first = False
			timing_obj = delay_obj.timing_add(0)
			timing_obj.set_steps(4, convproj_obj)
			delay_obj.feedback[0] = plugin_obj.params.get('2', 0).value
			delay_obj.to_cvpj(convproj_obj, pluginid)
			return 1

		return 2