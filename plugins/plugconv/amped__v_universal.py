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
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self, plugconv_obj): 
		plugconv_obj.in_plugins = [['universal', None]]
		plugconv_obj.in_daws = []
		plugconv_obj.out_plugins = [['native-amped', None]]
		plugconv_obj.out_daws = ['amped']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):
		
		if plugin_obj.type.subtype == 'filter':
			extpluglog.convinternal('Universal', 'Filter', 'Amped', 'EqualizerPro')
			plugin_obj.replace('native-amped', 'EqualizerPro')

			plugin_obj.params.add('filter/1/active', int(plugin_obj.filter.on), 'float')
			plugin_obj.params.add('filter/1/freq', plugin_obj.filter.freq, 'float')
			plugin_obj.params.add('filter/1/type', eqpro_filterid(plugin_obj.filter.type), 'float')
			plugin_obj.params.add('filter/1/q', plugin_obj.filter.q, 'float')
			plugin_obj.params.add('filter/1/gain', plugin_obj.filter.gain, 'float')

			convproj_obj.automation.move(['filter', pluginid, 'freq'], ['plugin', pluginid, "filter/1/freq"])
			convproj_obj.automation.move(['filter', pluginid, 'gain'], ['plugin', pluginid, "filter/1/gain"])
			convproj_obj.automation.move(['filter', pluginid, 'q'], ['plugin', pluginid, "filter/1/q"])
			return 0

		if plugin_obj.type.subtype == 'eq-bands':
			extpluglog.convinternal('Universal', 'EQ Bands', 'Amped', 'EqualizerPro')
			gain_out = plugin_obj.params.get("gain_out", 0).value

			plugin_obj.replace('native-amped', 'EqualizerPro')

			for n, f in enumerate(plugin_obj.eq):
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
			return 0

		return 2
