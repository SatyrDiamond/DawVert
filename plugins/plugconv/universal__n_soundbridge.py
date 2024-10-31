# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog
from functions import xtramath

def calc_freq(in_freq): return 30 * ((2/3)*1000)**in_freq

def calc_q(q): return xtramath.between_from_one(0.1, 24, q)

def calc_gain(gain): return xtramath.between_from_one(-24, 24, gain)

def eq_get(params_obj, starttxt, filter_obj): 
	eq_hz = params_obj.get(starttxt+'hz', 0.35304760932922363).value
	eq_q = params_obj.get(starttxt+'q', 0.03765690326690674).value
	eq_gain = params_obj.get(starttxt+'gain', 0.5).value
	eq_on = params_obj.get(starttxt+'on', 0).value

	filter_obj.on = bool(eq_on)
	filter_obj.freq = calc_freq(eq_hz)
	filter_obj.q = calc_q(eq_q)
	filter_obj.gain = calc_gain(eq_gain)

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'soundbridge', None]]
		in_dict['in_daws'] = ['soundbridge']
		in_dict['out_plugins'] = [['universal', None, None]]
		in_dict['out_daws'] = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):
		
		if plugin_obj.type.check_wildmatch('native', 'soundbridge', 'limiter'):
			extpluglog.convinternal('SoundBridge', 'Limiter', 'Universal', 'Limiter')
			threshold = plugin_obj.params.get('threshold', 1).value
			attack = plugin_obj.params.get('attack', 0).value
			release = plugin_obj.params.get('release', 0).value
			gain = plugin_obj.params.get('gain', 0.5).value
			lookahead = plugin_obj.params.get('lookahead', 0).value*3
			link_channels = plugin_obj.params.get('link_channels', 1).value

			threshold = (1-threshold)*80
			attack = 0.1 * 1000**(attack)
			release = (release**2.4)*3
			gain = ((gain-0.5)*2)*36
			lookahead = [0,3,5,10][min(int(lookahead), 3)]

			plugin_obj.replace('universal', 'limiter', None)
			plugin_obj.params.add('attack', attack/1000, 'float')
			plugin_obj.params.add('release', release, 'float')
			plugin_obj.params.add('postgain', gain, 'float')
			plugin_obj.params.add('threshold', threshold, 'float')
			plugin_obj.params.add('lookahead', lookahead/1000, 'float')
			plugin_obj.params.add('link_channels', bool(link_channels), 'bool')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'soundbridge', 'eq'):
			extpluglog.convinternal('SoundBridge', 'EQ', 'Universal', 'EQ 8-Limited')

			#low_shelf
			filter_obj = plugin_obj.named_filter_add('low_shelf')
			filter_obj.type.set('low_shelf', None)
			eq_get(plugin_obj.params, 'ls_', filter_obj)

			#peak
			for peak_num in range(4):
				peak_txt = 'p'+str(peak_num+1)+'_'
				cvpj_txt = 'peak_'+str(peak_num+1)
				filter_obj = plugin_obj.named_filter_add(cvpj_txt)
				filter_obj.type.set('peak', None)
				eq_get(plugin_obj.params, peak_txt, filter_obj)

			#high_shelf
			filter_obj = plugin_obj.named_filter_add('high_shelf')
			filter_obj.type.set('high_shelf', None)
			eq_get(plugin_obj.params, 'hs_', filter_obj)

			plugin_obj.replace('universal', 'eq', '8limited')
			return 1

		return 2