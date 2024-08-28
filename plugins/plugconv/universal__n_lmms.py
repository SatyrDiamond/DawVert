# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import math
from functions import xtramath
from functions import extpluglog

slope_vals = [12,24,48]

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self, plugconv_obj): 
		plugconv_obj.priority = 50
		plugconv_obj.in_plugins = [['native-lmms', None]]
		plugconv_obj.in_daws = ['lmms']
		plugconv_obj.out_plugins = [['universal', None]]
		plugconv_obj.out_daws = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):

		if plugin_obj.type.subtype == 'eq':
			extpluglog.convinternal('LMMS', 'EQ', 'Universal', 'EQ 8-Limited')
			eq_Outputgain = plugin_obj.params.get('Outputgain', 0).value
			eq_Inputgain = plugin_obj.params.get('Inputgain', 0).value

			#HP
			filter_obj = plugin_obj.named_filter_add('high_pass')
			filter_obj.on = bool(plugin_obj.params.get('HPactive', 0).value)
			filter_obj.type.set('high_pass', None)
			filter_obj.freq = plugin_obj.params.get('HPfreq', 0).value
			filter_obj.q = plugin_obj.params.get('HPres', 0).value
			filter_obj.slope = slope_vals[int(plugin_obj.params.get('HP', 0).value)]

			#low_shelf
			filter_obj = plugin_obj.named_filter_add('low_shelf')
			filter_obj.on = bool(plugin_obj.params.get('Lowshelfactive', 0).value)
			filter_obj.type.set('low_shelf', None)
			filter_obj.freq = plugin_obj.params.get('LowShelffreq', 0).value
			filter_obj.q = plugin_obj.params.get('LowShelfres', 0).value
			filter_obj.gain = plugin_obj.params.get('Lowshelfgain', 0).value

			#peak
			for peak_num in range(4):
				peak_txt = 'Peak'+str(peak_num+1)
				cvpj_txt = 'peak_'+str(peak_num+1)
				eq_Peak_bw = plugin_obj.params.get(peak_txt+'bw', 0.1).value
				filter_obj = plugin_obj.named_filter_add(cvpj_txt)
				filter_obj.on = bool(plugin_obj.params.get(peak_txt+'active', 0).value)
				filter_obj.type.set('peak', None)
				filter_obj.freq = plugin_obj.params.get(peak_txt+'freq', 0).value
				filter_obj.q = xtramath.logpowmul(eq_Peak_bw, -1) 
				filter_obj.gain = plugin_obj.params.get(peak_txt+'gain', 0).value

			#high_shelf
			filter_obj = plugin_obj.named_filter_add('high_shelf')
			filter_obj.on = bool(plugin_obj.params.get('Highshelfactive', 0).value)
			filter_obj.type.set('high_shelf', None)
			filter_obj.freq = plugin_obj.params.get('Highshelffreq', 0).value
			filter_obj.q = plugin_obj.params.get('HighShelfres', 0).value
			filter_obj.gain = plugin_obj.params.get('HighShelfgain', 0).value

			#LP
			filter_obj = plugin_obj.named_filter_add('low_pass')
			filter_obj.on = bool(plugin_obj.params.get('LPactive', 0).value)
			filter_obj.type.set('low_pass', None)
			filter_obj.freq = plugin_obj.params.get('LPfreq', 0).value
			filter_obj.q = plugin_obj.params.get('LPres', 0).value
			filter_obj.slope = slope_vals[int(plugin_obj.params.get('LP', 0).value)]

			plugin_obj.replace('universal', 'eq-8limited')
			plugin_obj.params.add('gain_out', eq_Outputgain, 'float')
			plugin_obj.params.add('gain_in', eq_Inputgain, 'float')
			return 1
			
		return 2