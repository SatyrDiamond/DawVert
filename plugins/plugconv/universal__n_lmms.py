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
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'lmms', None]]
		in_dict['in_daws'] = ['lmms']
		in_dict['out_plugins'] = [['universal', None, None]]
		in_dict['out_daws'] = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):

		if plugin_obj.type.check_wildmatch('native', 'lmms', 'eq'):
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
			convproj_obj.automation.move(['plugin', pluginid, 'HPactive'], ['n_filter', pluginid, 'high_pass', 'on'])
			convproj_obj.automation.move(['plugin', pluginid, 'HPfreq'], ['n_filter', pluginid, 'high_pass', 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, 'HPres'], ['n_filter', pluginid, 'high_pass', 'q'])

			#low_shelf
			filter_obj = plugin_obj.named_filter_add('low_shelf')
			filter_obj.on = bool(plugin_obj.params.get('Lowshelfactive', 0).value)
			filter_obj.type.set('low_shelf', None)
			filter_obj.freq = plugin_obj.params.get('LowShelffreq', 0).value
			filter_obj.q = plugin_obj.params.get('LowShelfres', 0).value
			filter_obj.gain = plugin_obj.params.get('Lowshelfgain', 0).value
			convproj_obj.automation.move(['plugin', pluginid, 'Lowshelfactive'], ['n_filter', pluginid, 'low_shelf', 'on'])
			convproj_obj.automation.move(['plugin', pluginid, 'LowShelffreq'], ['n_filter', pluginid, 'low_shelf', 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, 'LowShelfres'], ['n_filter', pluginid, 'low_shelf', 'q'])
			convproj_obj.automation.move(['plugin', pluginid, 'Lowshelfgain'], ['n_filter', pluginid, 'low_shelf', 'gain'])

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
				convproj_obj.automation.move(['plugin', pluginid, peak_txt+'active'], ['n_filter', pluginid, cvpj_txt, 'on'])
				convproj_obj.automation.move(['plugin', pluginid, peak_txt+'freq'], ['n_filter', pluginid, cvpj_txt, 'freq'])
				convproj_obj.automation.move(['plugin', pluginid, peak_txt+'gain'], ['n_filter', pluginid, cvpj_txt, 'gain'])

			#high_shelf
			filter_obj = plugin_obj.named_filter_add('high_shelf')
			filter_obj.on = bool(plugin_obj.params.get('Highshelfactive', 0).value)
			filter_obj.type.set('high_shelf', None)
			filter_obj.freq = plugin_obj.params.get('Highshelffreq', 0).value
			filter_obj.q = plugin_obj.params.get('HighShelfres', 0).value
			filter_obj.gain = plugin_obj.params.get('HighShelfgain', 0).value
			convproj_obj.automation.move(['plugin', pluginid, 'Highshelfactive'], ['n_filter', pluginid, 'high_shelf', 'on'])
			convproj_obj.automation.move(['plugin', pluginid, 'Highshelffreq'], ['n_filter', pluginid, 'high_shelf', 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, 'Highshelfres'], ['n_filter', pluginid, 'high_shelf', 'q'])
			convproj_obj.automation.move(['plugin', pluginid, 'Highshelfgain'], ['n_filter', pluginid, 'high_shelf', 'gain'])

			#LP
			filter_obj = plugin_obj.named_filter_add('low_pass')
			filter_obj.on = bool(plugin_obj.params.get('LPactive', 0).value)
			filter_obj.type.set('low_pass', None)
			filter_obj.freq = plugin_obj.params.get('LPfreq', 0).value
			filter_obj.q = plugin_obj.params.get('LPres', 0).value
			filter_obj.slope = slope_vals[int(plugin_obj.params.get('LP', 0).value)]
			convproj_obj.automation.move(['plugin', pluginid, 'LPactive'], ['n_filter', pluginid, 'low_pass', 'on'])
			convproj_obj.automation.move(['plugin', pluginid, 'LPfreq'], ['n_filter', pluginid, 'low_pass', 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, 'LPres'], ['n_filter', pluginid, 'low_pass', 'q'])

			plugin_obj.replace('universal', 'eq', '8limited')
			plugin_obj.params.add('gain_out', eq_Outputgain, 'float')
			plugin_obj.params.add('gain_in', eq_Inputgain, 'float')
			return 1
			
		if plugin_obj.type.check_wildmatch('native', 'lmms', 'spectrumanalyzer'):
			extpluglog.convinternal('LMMS', 'SpectrumAnalyzer', 'Universal', 'Spectrum Analyzer')
			plugin_obj.replace('universal', 'spectrum_analyzer', None)
			return 1

		return 2