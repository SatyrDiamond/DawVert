# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog
from functions import note_data

def eqpro_filterid(filter_type):
	band_type = 2
	if filter_type.check_wildmatch('peak', None): band_type = 0
	if filter_type.check_wildmatch('low_pass', None): band_type = 2
	if filter_type.check_wildmatch('high_pass', None): band_type = 1
	if filter_type.check_wildmatch('low_shelf', None): band_type = 3
	if filter_type.check_wildmatch('high_shelf', None): band_type = 4
	return band_type

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'
	
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = 'universal:eq'
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = ['native:amped:EqualizerPro']
		in_dict['out_daws'] = ['amped']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		is_eq_bands = plugin_obj.type.check_wildmatch('universal', 'eq', 'bands')
		is_eq_8limited = plugin_obj.type.check_wildmatch('universal', 'eq', '8limited')

		if is_eq_bands or is_eq_8limited:
			if is_eq_8limited: plugin_obj.state.eq.from_8limited(pluginid)
				
			eq_obj = plugin_obj.state.eq
			named_filter = plugin_obj.state.named_filter
			plugin_obj.replace('native', 'amped', 'EqualizerPro')
			plugin_obj.state.named_filter = named_filter
			plugin_obj.state.eq = eq_obj
			gain_out = plugin_obj.params.get("gain_out", 0).value

			for n, f in enumerate(plugin_obj.state.eq):
				filter_id, filter_obj = f
				starttxt = 'filter/'+str(n+1)+'/'

				plugin_obj.params.add(starttxt+'active', int(filter_obj.on), 'float')
				plugin_obj.params.add(starttxt+'freq', filter_obj.freq, 'float')
				plugin_obj.params.add(starttxt+'type', eqpro_filterid(filter_obj.type), 'float')
				plugin_obj.params.add(starttxt+'q', filter_obj.q, 'float')
				plugin_obj.params.add(starttxt+'gain', filter_obj.gain, 'float')

				convproj_obj.automation.move(['n_filter', pluginid, filter_id, 'on'], ['plugin', pluginid, starttxt+'active'])
				convproj_obj.automation.move(['n_filter', pluginid, filter_id, 'freq'], ['plugin', pluginid, starttxt+'freq'])
				convproj_obj.automation.move(['n_filter', pluginid, filter_id, 'gain'], ['plugin', pluginid, starttxt+'gain'])

			convproj_obj.automation.move_group(['plugin', pluginid], 'gain_out', 'postGain')
			plugin_obj.params.add('postGain', gain_out, 'float')
			return True