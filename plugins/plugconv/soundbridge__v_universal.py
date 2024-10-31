# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog
from functions import xtramath
import math
import bisect

limiter_lookahead = [0,3,5,10]

filter_list = ['low_pass','high_pass','band_pass','notch']

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
		
		if plugin_obj.type.check_match('universal', 'limiter', None):
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

		if plugin_obj.type.check_match('universal', 'eq', '8limited'):
			extpluglog.convinternal('Universal', 'EQ 8-Limited', 'SoundBridge', 'EQ')
			fil_ls = plugin_obj.named_filter_get('low_shelf')
			fil_pd = [plugin_obj.named_filter_get('peak_'+str(peak_num+1)) for peak_num in range(4)]
			fil_hs = plugin_obj.named_filter_get('high_shelf')

			plugin_obj.replace('universal', 'soundbridge', "eq")
			eq_get(fil_ls, plugin_obj.params, 'ls_')
			eq_get(fil_pd[0], plugin_obj.params, 'p1_')
			eq_get(fil_pd[1], plugin_obj.params, 'p2_')
			eq_get(fil_pd[2], plugin_obj.params, 'p3_')
			eq_get(fil_pd[3], plugin_obj.params, 'p4_')
			eq_get(fil_hs, plugin_obj.params, 'hs_')
			return 0

		if plugin_obj.type.check_wildmatch('universal', 'filter', None) and plugin_obj.filter.on:
			extpluglog.convinternal('Universal', 'Filter', 'SoundBridge', 'Filter Unit')
			filter_type = 0
			if plugin_obj.filter.type.type in filter_list:
				filter_type = filter_list.index(plugin_obj.filter.type.type)
			plugin_obj.replace('universal', 'soundbridge', "filter_unit")
			plugin_obj.params.add('type', filter_type/3, 'float')
			plugin_obj.params.add('freq', (math.log(max(26, plugin_obj.filter.freq)/26) / math.log((1000*(20/26)))), 'float')
			plugin_obj.params.add('q', xtramath.between_to_one(0.20, 3, plugin_obj.filter.q), 'float')
			return 0

		is_compressor = plugin_obj.type.check_match('universal', 'compressor', None)
		is_expander = plugin_obj.type.check_match('universal', 'expander', None)

		if is_compressor or is_expander:
			if is_compressor: extpluglog.convinternal('Universal', 'Compressor', 'SoundBridge', 'Compressor/Expander')
			if is_expander: extpluglog.convinternal('Universal', 'Expander', 'SoundBridge', 'Compressor/Expander')
			attack = plugin_obj.params.get('attack', 0.002).value*1000
			release = plugin_obj.params.get('release', 0.01).value
			gain = plugin_obj.params.get('gain', 0).value
			ratio = plugin_obj.params.get('ratio', 2).value
			threshold = plugin_obj.params.get('threshold', 0).value
			lookahead = plugin_obj.params.get('lookahead', 0).value*1000
			link_channels = plugin_obj.params.get('link_channels', True).value

			threshold = (80-threshold)/80
			attack = math.log10(attack / 0.1) / math.log10(1000)
			release = (release / 3) ** (1 / 2.4)
			gain = ((gain/36)/2)+0.5
			ratio = 1-(1/ratio)

			lookahead = bisect.bisect_left(limiter_lookahead, lookahead)
			lookahead = min(lookahead, 3)/3

			plugin_obj.replace('universal', 'soundbridge', "compressor_expander")
			plugin_obj.params.add('gain', gain, 'float')
			plugin_obj.params.add('threshold', threshold, 'float')
			plugin_obj.params.add('attack', attack, 'float')
			plugin_obj.params.add('release', release, 'float')
			plugin_obj.params.add('link_channels', int(link_channels), 'float')
			plugin_obj.params.add('ratio', ratio, 'float')
			if is_compressor: plugin_obj.params.add('mode', 0, 'float')
			if is_expander: plugin_obj.params.add('mode', 1, 'float')
			plugin_obj.params.add('lookahead', lookahead, 'float')
			return 0

		if plugin_obj.type.check_wildmatch('universal', 'bitcrush', None):
			extpluglog.convinternal('Universal', 'BitCrusher', 'SoundBridge', 'BitCrusher')
			bits = plugin_obj.params.get('bits', 31).value
			freq = plugin_obj.params.get('freq', 22050).value

			bits -= 1

			plugin_obj.replace('universal', 'soundbridge', "bit_crusher")
			plugin_obj.params.add('bits', xtramath.clamp(bits/30, 0, 1), 'float')
			plugin_obj.params.add('downsample', xtramath.clamp(22050/(freq*40), 0, 1), 'float')
			return 0

		return 2
