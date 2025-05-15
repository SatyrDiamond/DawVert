# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'

	def get_priority(self):
		return 0

	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = 'native:amped'
		in_dict['in_daws'] = ['amped']
		in_dict['out_plugins'] = ['universal']
		in_dict['out_daws'] = []

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Equalizer'):
			filter_obj, filter_id = plugin_obj.eq_add()
			filter_obj.type.set('high_pass', None)
			filter_obj.freq = plugin_obj.params.get("hpfreq", 20).value
			convproj_obj.automation.move(['plugin', pluginid, "hpfreq"], ['n_filter', pluginid, filter_id, 'freq'])

			filter_obj, filter_id = plugin_obj.eq_add()
			filter_obj.type.set('peak', None)
			filter_obj.freq = plugin_obj.params.get("peakfreq", 2000).value
			filter_obj.gain = plugin_obj.params.get("peakgain", 0).value
			filter_obj.q = plugin_obj.params.get("peakq", 1).value
			convproj_obj.automation.move(['plugin', pluginid, "peakfreq"], ['n_filter', pluginid, filter_id, 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, "peakgain"], ['n_filter', pluginid, filter_id, 'gain'])
			convproj_obj.automation.move(['plugin', pluginid, "peakq"], ['n_filter', pluginid, filter_id, 'q'])

			filter_obj, filter_id = plugin_obj.eq_add()
			filter_obj.type.set('low_pass', None)
			filter_obj.freq = plugin_obj.params.get("lpfreq", 10000).value
			convproj_obj.automation.move(['plugin', pluginid, "lpfreq"], ['n_filter', pluginid, filter_id, 'freq'])

			eq_obj = plugin_obj.state.eq
			plugin_obj.replace('universal', 'eq', 'bands')
			plugin_obj.state.eq = eq_obj
			return True

		if plugin_obj.type.check_wildmatch('native', 'amped', 'EqualizerPro'):
			master_gain = plugin_obj.params.get("postGain", 0).value

			for band_num in range(8):
				str_band_num = str(band_num+1)
				starttxt = 'filter/'+str_band_num+'/'
				cvpj_band_txt = 'main/'+str_band_num+'/'

				filter_obj, filter_id = plugin_obj.eq_add()
				filter_obj.on = int(plugin_obj.params.get(starttxt+"active", 0).value)
				filter_obj.freq = plugin_obj.params.get(starttxt+"freq", 20).value
				filter_obj.q = plugin_obj.params.get(starttxt+"q", 0.5).value
				filter_obj.gain = plugin_obj.params.get(starttxt+"gain", 0).value

				band_type = plugin_obj.params.get(starttxt+"type", 0).value
				if band_type == 0: filter_obj.type.set('peak', None)
				if band_type == 2: filter_obj.type.set('low_pass', None)
				if band_type == 1: filter_obj.type.set('high_pass', None)
				if band_type == 3: filter_obj.type.set('low_shelf', None)
				if band_type == 4: filter_obj.type.set('high_shelf', None)

				convproj_obj.automation.move(['plugin', pluginid, starttxt+"active"], ['n_filter', pluginid, filter_id, 'on'])
				convproj_obj.automation.move(['plugin', pluginid, starttxt+"freq"], ['n_filter', pluginid, filter_id, 'freq'])
				convproj_obj.automation.move(['plugin', pluginid, starttxt+"gain"], ['n_filter', pluginid, filter_id, 'gain'])
				convproj_obj.automation.move(['plugin', pluginid, starttxt+"q"], ['n_filter', pluginid, filter_id, 'q'])

			eq_obj = plugin_obj.state.eq
			plugin_obj.replace('universal', 'eq', 'bands')
			plugin_obj.state.eq = eq_obj

			plugin_obj.params.add('gain_out', master_gain, 'float')
			return True