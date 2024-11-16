# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog
from functions import note_data

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return 100
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['universal', None, None]]
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = [['native', 'tracktion', None]]
		in_dict['out_daws'] = ['waveform_edit']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):
		
		if plugin_obj.type.check_wildmatch('universal', 'filter', None):
			extpluglog.convinternal('Universal', 'Filter', 'Waveform', '1bandEq')
			plugin_obj.replace('native', 'tracktion', '1bandEq')

			filter_obj = plugin_obj.filter

			band_shape = 6
			if filter_obj.type.type == 'low_pass': band_shape = 0
			if filter_obj.type.type == 'low_shelf': band_shape = 1
			if filter_obj.type.type == 'peak': band_shape = 2
			if filter_obj.type.type == 'high_shelf': band_shape = 5
			if filter_obj.type.type == 'high_pass': band_shape = 6

			plugin_obj.params.add('freq', note_data.freq_to_note(plugin_obj.filter.freq)+72, 'float')
			plugin_obj.params.add('shape', band_shape, 'float')
			plugin_obj.params.add('q', plugin_obj.filter.q, 'float')
			plugin_obj.params.add('gain', plugin_obj.filter.gain, 'float')
			plugin_obj.params.add('slope', plugin_obj.filter.slope, 'float')
			
			convproj_obj.automation.move(['filter', pluginid, 'freq'], ['plugin', pluginid, 'freq'])
			convproj_obj.automation.calc(['plugin', pluginid, 'freq'], 'freq2note', 0, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'freq'], 'add', 72, 0, 0, 0)
			return 0

		if plugin_obj.type.check_wildmatch('universal', 'compressor', None):
			extpluglog.convinternal('Universal', 'Compressor', 'Waveform', 'Compressor')
			plugin_obj.plugts_transform('./data_main/plugts/univ_waveform.pltr', 'comp', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.check_wildmatch('universal', 'limiter', None):
			extpluglog.convinternal('Universal', 'Limiter', 'Waveform', 'Limiter')
			plugin_obj.plugts_transform('./data_main/plugts/univ_waveform.pltr', 'limiter', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.check_wildmatch('universal', 'gate', None):
			extpluglog.convinternal('Universal', 'Gate', 'Waveform', 'Gate')
			plugin_obj.plugts_transform('./data_main/plugts/univ_waveform.pltr', 'gate', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.check_wildmatch('universal', 'spectrum_analyzer', None):
			extpluglog.convinternal('Universal', 'Spectrum Analyzer', 'Waveform', 'Spectrum Analyzer')
			plugin_obj.replace('native', 'tracktion', 'spectrum')
			return 1

		is_eq_bands = plugin_obj.type.check_wildmatch('universal', 'eq', 'bands')
		is_eq_8limited = plugin_obj.type.check_wildmatch('universal', 'eq', '8limited')

		if is_eq_bands or is_eq_8limited:
			if is_eq_bands:
				extpluglog.convinternal('Universal', 'EQ Bands', 'Waveform', '8bandEq')
			if is_eq_8limited:
				extpluglog.convinternal('Universal', 'EQ 8-Limited', 'Waveform', '8bandEq')
				plugin_obj.eq.from_8limited(pluginid)

			plugin_obj.replace('native', 'tracktion', '8bandEq')
			for n, f in enumerate(plugin_obj.eq):
				filter_id, filter_obj = f
				eqnumtxt = str(n+1)+'lm'

				band_shape = 0
				if filter_obj.type.type == 'low_pass': band_shape = 0
				if filter_obj.type.type == 'low_shelf': band_shape = 1
				if filter_obj.type.type == 'peak': band_shape = 2
				if filter_obj.type.type == 'band_pass': band_shape = 3
				if filter_obj.type.type == 'band_stop': band_shape = 4
				if filter_obj.type.type == 'high_shelf': band_shape = 5
				if filter_obj.type.type == 'high_pass': band_shape = 6

				band_freq = note_data.freq_to_note(filter_obj.freq)+72

				plugin_obj.params.add("enable"+eqnumtxt, filter_obj.on, 'float')
				plugin_obj.params.add("freq"+eqnumtxt, band_freq, 'float')
				plugin_obj.params.add("gain"+eqnumtxt, filter_obj.gain, 'float')
				plugin_obj.params.add("q"+eqnumtxt, filter_obj.q, 'float')
				plugin_obj.params.add("shape"+eqnumtxt, band_shape, 'float')
				plugin_obj.params.add("slope"+eqnumtxt, filter_obj.slope, 'float')

				convproj_obj.automation.move(['n_filter', pluginid, filter_id, 'on'], ['plugin', pluginid, "enable"+eqnumtxt])
				convproj_obj.automation.move(['n_filter', pluginid, filter_id, 'freq'], ['plugin', pluginid, "freq"+eqnumtxt])
				convproj_obj.automation.move(['n_filter', pluginid, filter_id, 'gain'], ['plugin', pluginid, "gain"+eqnumtxt])
				convproj_obj.automation.calc(['plugin', pluginid, "freq"+eqnumtxt], 'freq2note', 0, 0, 0, 0)
				convproj_obj.automation.calc(['plugin', pluginid, "freq"+eqnumtxt], 'add', 72, 0, 0, 0)

			return 0
			
		return 2
