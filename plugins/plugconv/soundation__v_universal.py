# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog
from functions import note_data

import math

def eq_freq(filter_obj):
	return (math.log(max(20, filter_obj.freq)/20) / math.log(1000)) if filter_obj.freq != 0 else 0

def eq_gain(gain):
	return (gain/40)+0.5

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return 100
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['universal', None, None]]
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = [['native', 'soundation', None]]
		in_dict['out_daws'] = ['soundation']
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		
		is_eq_bands = plugin_obj.type.check_wildmatch('universal', 'eq', 'bands')
		is_eq_8limited = plugin_obj.type.check_wildmatch('universal', 'eq', '8limited')

		if is_eq_bands or is_eq_8limited:
			if is_eq_bands:
				extpluglog.convinternal('Universal', 'EQ Bands', 'Soundation', 'EQ')
				plugin_obj.eq.to_8limited(convproj_obj, pluginid)
			if is_eq_8limited:
				extpluglog.convinternal('Universal', 'EQ 8-Limited', 'Soundation', 'EQ')
				
			fil_hp = plugin_obj.named_filter_get('high_pass')
			fil_ls = plugin_obj.named_filter_get('low_shelf')
			fil_pd = [plugin_obj.named_filter_get('peak_'+str(peak_num+1)) for peak_num in range(4)]
			fil_hs = plugin_obj.named_filter_get('high_shelf')
			fil_lp = plugin_obj.named_filter_get('low_pass')

			gain_out = plugin_obj.params.get('gain_out', 0).value

			plugin_obj.replace('native', 'soundation', 'com.soundation.parametric-eq')

			plugin_obj.params.add('hpf_enable', int(fil_hp.on), 'float')
			plugin_obj.params.add('hpf_freq', eq_freq(fil_hp), 'float')

			plugin_obj.params.add('lowshelf_enable', int(fil_ls.on), 'float')
			plugin_obj.params.add('lowshelf_freq', eq_freq(fil_ls), 'float')
			plugin_obj.params.add('lowshelf_gain', eq_gain(fil_ls.gain), 'float')

			for peak_num, fil_p in enumerate(fil_pd):
				filt_txt = 'peak'+str(peak_num+1)+'_'
				plugin_obj.params.add(filt_txt+'enable', int(fil_p.on), 'float')
				plugin_obj.params.add(filt_txt+'freq', eq_freq(fil_p), 'float')
				plugin_obj.params.add(filt_txt+'gain', eq_gain(fil_p.gain), 'float')

			plugin_obj.params.add('highshelf_enable', int(fil_hs.on), 'float')
			plugin_obj.params.add('highshelf_freq', eq_freq(fil_hs), 'float')
			plugin_obj.params.add('highshelf_gain', eq_gain(fil_hs.gain), 'float')

			plugin_obj.params.add('lpf_enable', int(fil_lp.on), 'float')
			plugin_obj.params.add('lpf_freq', eq_freq(fil_lp), 'float')

			plugin_obj.params.add('master_gain', eq_gain(gain_out), 'float')
			return 0

		return 2
