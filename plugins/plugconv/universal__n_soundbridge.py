# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog
from functions import xtramath
import math

def calc_eq_freq(in_freq): return 30 * ((2/3)*1000)**in_freq

def calc_eq_q(q): return xtramath.between_from_one(0.1, 24, q)

def calc_eq_gain(gain): return xtramath.between_from_one(-24, 24, gain)

def eq_get(params_obj, starttxt, filter_obj): 
	eq_hz = params_obj.get(starttxt+'hz', 0.35304760932922363).value
	eq_q = params_obj.get(starttxt+'q', 0.03765690326690674).value
	eq_gain = params_obj.get(starttxt+'gain', 0.5).value
	eq_on = params_obj.get(starttxt+'on', 0).value

	filter_obj.on = bool(eq_on)
	filter_obj.freq = calc_eq_freq(eq_hz)
	filter_obj.q = calc_eq_q(eq_q)
	filter_obj.gain = calc_eq_gain(eq_gain)

def calc_gain(gain): return ((gain-0.5)*2)*36

def calc_attack(attack): return (0.1 * 1000**(attack))/1000

def calc_release(release): return (release**2.4)*3

def calc_threshold(threshold): return (1-threshold)*80

def calc_ratio(ratio): 
	ratio = 1-ratio
	ratio = 1/ratio if ratio else 10000
	return ratio

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

			lookahead = [0,3,5,10][min(int(lookahead), 3)]

			plugin_obj.replace('universal', 'limiter', None)
			plugin_obj.params.add('attack', calc_attack(attack), 'float')
			plugin_obj.params.add('release', calc_release(release), 'float')
			plugin_obj.params.add('postgain', calc_gain(gain), 'float')
			plugin_obj.params.add('threshold', calc_threshold(threshold), 'float')
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

		if plugin_obj.type.check_wildmatch('native', 'soundbridge', 'filter_unit'):
			extpluglog.convinternal('SoundBridge', 'Filter Unit', 'Universal', 'Filter')
			f_type = plugin_obj.params.get('type', 0).value*3
			f_freq = plugin_obj.params.get('freq', 1).value
			f_q = plugin_obj.params.get('q', 0.5).value

			filter_type = ['low_pass','high_pass','band_pass','notch'][min(int(f_q), 3)]

			plugin_obj.replace('universal', 'filter', None)
			plugin_obj.filter.on = True
			plugin_obj.filter.type.set(filter_type, None)
			plugin_obj.filter.freq = 26 * (1000*(20/26))**f_freq
			plugin_obj.filter.q = xtramath.between_from_one(0.20, 3, f_q)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'soundbridge', 'compressor_expander'):
			gain = plugin_obj.params.get('gain', 0.5).value
			threshold = plugin_obj.params.get('threshold', 1).value
			attack = plugin_obj.params.get('attack', 0).value
			release = plugin_obj.params.get('release', 0).value
			link_channels = plugin_obj.params.get('link_channels', 1).value
			ratio = plugin_obj.params.get('ratio', 0).value
			mode = plugin_obj.params.get('mode', 0).value
			lookahead = plugin_obj.params.get('lookahead', 0).value*3
			lookahead = [0,3,5,10][min(int(lookahead), 3)]

			if not mode:
				extpluglog.convinternal('SoundBridge', 'Compressor/Expander', 'Universal', 'Compressor')
				plugin_obj.replace('universal', 'compressor', None)
			else:
				extpluglog.convinternal('SoundBridge', 'Compressor/Expander', 'Universal', 'Expander')
				plugin_obj.replace('universal', 'expander', None)

			plugin_obj.params.add('attack', calc_attack(attack), 'float')
			plugin_obj.params.add('release', calc_release(release), 'float')
			plugin_obj.params.add('gain', calc_gain(gain), 'float')
			plugin_obj.params.add('ratio', calc_ratio(ratio), 'float')
			plugin_obj.params.add('threshold', calc_threshold(threshold), 'float')
			plugin_obj.params.add('lookahead', lookahead/1000, 'float')
			plugin_obj.params.add('link_channels', int(link_channels), 'bool')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'soundbridge', 'bit_crusher'):
			extpluglog.convinternal('SoundBridge', 'BitCrusher', 'Universal', 'BitCrusher')
			bits = plugin_obj.params.get('bits', 1).value
			downsample = plugin_obj.params.get('downsample', 0).value
			plugin_obj.replace('universal', 'bitcrush', None)
			plugin_obj.params.add('bits', bits*30 + 1, 'float')
			plugin_obj.params.add('freq', 22050/(downsample*40), 'float')
			return 1

		return 2