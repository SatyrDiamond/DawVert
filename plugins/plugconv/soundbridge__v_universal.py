# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog
from functions import xtramath
import math
import bisect

limiter_lookahead = [0,3,5,10]

def calc_freq(in_freq): return (math.log(max(30, in_freq)/30) / math.log((2/3)*1000))

def calc_q(q): return xtramath.between_to_one(0.1, 24, q)

def calc_gain(gain): return xtramath.between_to_one(-24, 24, gain)

def eq_get(filter_obj, params_obj, starttxt): 
	params_obj.add(starttxt+'hz', calc_freq(filter_obj.freq), 'float')
	params_obj.add(starttxt+'q', calc_q(filter_obj.q), 'float')
	params_obj.add(starttxt+'gain', calc_gain(filter_obj.gain), 'float')
	params_obj.add(starttxt+'on', int(filter_obj.on), 'float')

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return 100
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['universal', None, None]]
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = [['native', 'soundbridge', None]]
		in_dict['out_daws'] = ['soundbridge']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):
		
		if plugin_obj.type.check_wildmatch('universal', 'limiter', None):
			extpluglog.convinternal('Universal', 'Limiter', 'SoundBridge', 'Limiter')

			threshold = plugin_obj.params.get('threshold', 1).value
			attack = plugin_obj.params.get('attack', 0).value*1000
			release = plugin_obj.params.get('release', 0).value
			gain = plugin_obj.params.get('gain', 0).value
			lookahead = plugin_obj.params.get('lookahead', 0).value*1000
			link_channels = plugin_obj.params.get('link_channels', True).value

			threshold = (80-threshold)/80
			attack = math.log10(attack / 0.1) / math.log10(1000)
			release = (release / 3) ** (1 / 2.4)
			gain = ((gain/36)/2)+0.5
			lookahead = bisect.bisect_left(limiter_lookahead, lookahead)
			lookahead = min(lookahead, 3)/3

			plugin_obj.replace('native', 'soundbridge', 'limiter')

			threshold = xtramath.clamp(threshold, 0, 1)
			attack = xtramath.clamp(attack, 0, 1)
			release = xtramath.clamp(release, 0, 1)
			gain = xtramath.clamp(gain, 0, 1)

			plugin_obj.params.add('threshold', threshold, 'float')
			plugin_obj.params.add('attack', attack, 'float')
			plugin_obj.params.add('release', release, 'float')
			plugin_obj.params.add('gain', gain, 'float')
			plugin_obj.params.add('lookahead', lookahead, 'float')
			plugin_obj.params.add('link_channels', int(link_channels), 'float')
			return 0

		if plugin_obj.type.check_wildmatch('universal', 'eq', '8limited'):
			fil_ls = plugin_obj.named_filter_get('low_shelf')
			fil_pd = [plugin_obj.named_filter_get('peak_'+str(peak_num+1)) for peak_num in range(4)]
			fil_hs = plugin_obj.named_filter_get('high_shelf')

			eq_get(fil_ls, plugin_obj.params, 'ls_')
			eq_get(fil_pd[0], plugin_obj.params, 'p1_')
			eq_get(fil_pd[1], plugin_obj.params, 'p2_')
			eq_get(fil_pd[2], plugin_obj.params, 'p3_')
			eq_get(fil_pd[3], plugin_obj.params, 'p4_')
			eq_get(fil_hs, plugin_obj.params, 'hs_')
			return 0

		return 2
