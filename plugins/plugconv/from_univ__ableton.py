# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import math

eq_types = ['high_pass', 'low_shelf', 'peak', 'notch', 'high_shelf', 'low_pass']

delay_steps = [1,2,3,4,5,6,8,16]

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'
	
	def get_priority(self):
		return 100
	
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = 'universal'
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = ['native:ableton']
		in_dict['out_daws'] = ['ableton']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		#if plugin_obj.type.check_wildmatch('universal', 'delay', None):
		#	fx_on, fx_wet = plugin_obj.fxdata_get()
		#	seperated = plugin_obj.datavals.get('seperated', [])
#
		#	timing_left = plugin_obj.timing_get('left') if 'time' in seperated else plugin_obj.timing_get('center')
		#	timing_right = plugin_obj.timing_get('right') if 'time' in seperated else plugin_obj.timing_get('center')
#
		#	feedback = (plugin_obj.datavals.get('l_feedback', 0)*plugin_obj.datavals.get('r_feedback', 0)) if 'feedback' in seperated else plugin_obj.datavals.get('c_feedback', 0)
#
		#	plugin_obj.replace('native', 'ableton', 'Delay')
#
		#	plugin_obj.fxdata_add(fx_on, 1)
#
		#	plugin_obj.params.add('Feedback', feedback/2, 'float')
		#	plugin_obj.params.add('DryWet', feedback/2, 'float')
#
		#	for endtxt, timing_obj in [['L', timing_left],['R', timing_right]]:
		#		use_seconds = True
#
		#		if timing_obj.type == 'steps':
		#			if not timing_obj.speed_steps%1 and 1<=timing_obj.speed_steps<=16:
		#				delidx, offset = timing_obj.get_step_offset([1,2,3,4,5,6,8,16])
		#				if abs(offset)<0.33:
		#					use_seconds = False
		#					plugin_obj.params.add('DelayLine_SyncedSixteenth'+endtxt, delidx, 'float')
		#					plugin_obj.params.add('DelayLine_Offset'+endtxt, offset, 'float')
#
		#		if use_seconds:
		#			plugin_obj.params.add('DelayLine_Sync'+endtxt, use_seconds, 'float')
		#			plugin_obj.params.add('DelayLine_Time'+endtxt, timing_obj.speed_seconds, 'float')
 #
		#	return True

		if plugin_obj.type.check_wildmatch('universal', 'filter', None):
			abe_starttxt = "Bands.0/ParameterA/"

			filter_obj = plugin_obj.filter

			plugin_obj.replace('native', 'ableton', 'Eq8')
			
			als_shape = eq_types.index(filter_obj.type.type)+1 if filter_obj.type.type in eq_types else 3

			if als_shape == 1 and filter_obj.slope > 36: als_shape = 0
			if als_shape == 6 and filter_obj.slope > 36: als_shape = 7

			plugin_obj.params.add(abe_starttxt+'Freq', filter_obj.freq, 'float')
			plugin_obj.params.add(abe_starttxt+'Gain', filter_obj.gain, 'float')
			plugin_obj.params.add(abe_starttxt+'IsOn', bool(filter_obj.on), 'bool')
			plugin_obj.params.add(abe_starttxt+'Mode', als_shape, 'float')
			plugin_obj.params.add(abe_starttxt+'Q', filter_obj.q, 'float')

			convproj_obj.automation.move(['filter', pluginid, 'on'], ['plugin', pluginid, abe_starttxt+'IsOn'])
			convproj_obj.automation.move(['filter', pluginid, 'freq'], ['plugin', pluginid, abe_starttxt+'Freq'])
			convproj_obj.automation.move(['filter', pluginid, 'gain'], ['plugin', pluginid, abe_starttxt+'Gain'])
			convproj_obj.automation.move(['filter', pluginid, 'q'], ['plugin', pluginid, abe_starttxt+'Q'])
			return True

		if plugin_obj.eq_to_bands(convproj_obj, pluginid):
			eqbands = [x for x in plugin_obj.state.eq]
			plugin_obj.replace('native', 'ableton', 'Eq8')
			for band_num, f in enumerate(eqbands):
				filter_id, filter_obj = f

				abe_starttxt = "Bands."+str(band_num)+"/ParameterA/"

				als_shape = eq_types.index(filter_obj.type.type)+1 if filter_obj.type.type in eq_types else 3

				if als_shape == 1 and filter_obj.slope > 36: als_shape = 0
				if als_shape == 6 and filter_obj.slope > 36: als_shape = 7

				plugin_obj.params.add(abe_starttxt+'Freq', filter_obj.freq, 'float')
				plugin_obj.params.add(abe_starttxt+'Gain', filter_obj.gain, 'float')
				plugin_obj.params.add(abe_starttxt+'IsOn', bool(filter_obj.on), 'bool')
				plugin_obj.params.add(abe_starttxt+'Mode', als_shape, 'int')
				plugin_obj.params.add(abe_starttxt+'Q', filter_obj.q, 'float')

				convproj_obj.automation.move(['n_filter', pluginid, filter_id, 'on'], ['plugin', pluginid, abe_starttxt+'IsOn'])
				convproj_obj.automation.move(['n_filter', pluginid, filter_id, 'freq'], ['plugin', pluginid, abe_starttxt+'Freq'])
				convproj_obj.automation.move(['n_filter', pluginid, filter_id, 'gain'], ['plugin', pluginid, abe_starttxt+'Gain'])
			return True