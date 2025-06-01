# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import note_data

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'

	def get_priority(self):
		return 100

	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = 'universal'
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = ['native:tracktion']
		in_dict['out_daws'] = ['waveform']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.eq_to_bands(convproj_obj, pluginid):
			eqbands = [x for x in plugin_obj.state.eq]
			plugin_obj.replace('native', 'tracktion', '8bandEq')
			for n, f in enumerate(eqbands):
				filter_id, filter_obj = f
				eqnumtxt = str(n+1)+'lm'

				band_shape = 0
				if filter_obj.type.type == 'low_pass': band_shape = 0
				if filter_obj.type.type == 'low_shelf': band_shape = 1
				if filter_obj.type.type == 'peak': band_shape = 2
				if filter_obj.type.type == 'band_pass': band_shape = 3
				if filter_obj.type.type == 'notch': band_shape = 4
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
			return True
			