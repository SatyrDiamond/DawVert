# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog
import math

eq_types = ['high_pass', 'low_shelf', 'peak', 'notch', 'high_shelf', 'low_pass']

delay_steps = [1,2,3,4,5,6,8,16]

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return 100
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['universal', None, None]]
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = [['native', 'ableton', None]]
		in_dict['out_daws'] = ['ableton']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):
		
		if plugin_obj.type.check_wildmatch('universal', 'delay', None):
			fx_on, fx_wet = plugin_obj.fxdata_get()
			seperated = plugin_obj.datavals.get('seperated', [])

			timing_left = plugin_obj.timing_get('left') if 'time' in seperated else plugin_obj.timing_get('center')
			timing_right = plugin_obj.timing_get('right') if 'time' in seperated else plugin_obj.timing_get('center')

			feedback = (plugin_obj.datavals.get('l_feedback', 0)*plugin_obj.datavals.get('r_feedback', 0)) if 'feedback' in seperated else plugin_obj.datavals.get('c_feedback', 0)

			plugin_obj.replace('native', 'ableton', 'Delay')

			plugin_obj.fxdata_add(fx_on, 1)

			plugin_obj.params.add('Feedback', feedback/2, 'float')
			plugin_obj.params.add('DryWet', feedback/2, 'float')

			for endtxt, timing_obj in [['L', timing_left],['R', timing_right]]:
				use_seconds = True

				if timing_obj.type == 'steps':
					if not timing_obj.speed_steps%1 and 1<=timing_obj.speed_steps<=16:
						delidx, offset = timing_obj.get_step_offset([1,2,3,4,5,6,8,16])
						if abs(offset)<0.33:
							use_seconds = False
							plugin_obj.params.add('DelayLine_SyncedSixteenth'+endtxt, delidx, 'float')
							plugin_obj.params.add('DelayLine_Offset'+endtxt, offset, 'float')

				if use_seconds:
					plugin_obj.params.add('DelayLine_Sync'+endtxt, use_seconds, 'float')
					plugin_obj.params.add('DelayLine_Time'+endtxt, timing_obj.speed_seconds, 'float')

		if plugin_obj.type.check_wildmatch('universal', 'bitcrush', None):
			extpluglog.convinternal('Universal', 'Bitcrush', 'Ableton', 'Redux2')
			plugin_obj.plugts_transform('./data_main/plugts/univ_ableton.pltr', 'bitcrush', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('universal', 'volpan', None):
			extpluglog.convinternal('Universal', 'Vol/Pan', 'Ableton', 'StereoGain')
			plugin_obj.plugts_transform('./data_main/plugts/univ_ableton.pltr', 'volpan', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('universal', 'limiter', None):
			extpluglog.convinternal('Universal', 'Limiter', 'Ableton', 'Limiter')
			plugin_obj.plugts_transform('./data_main/plugts/univ_ableton.pltr', 'limiter', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('universal', 'compressor', None):
			extpluglog.convinternal('Universal', 'Compressor', 'Ableton', 'Compressor')
			plugin_obj.plugts_transform('./data_main/plugts/univ_ableton.pltr', 'compressor', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('universal', 'expander', None):
			extpluglog.convinternal('Universal', 'Expander', 'Ableton', 'Compressor')
			plugin_obj.plugts_transform('./data_main/plugts/univ_ableton.pltr', 'expander', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('universal', 'gate', None):
			extpluglog.convinternal('Universal', 'Expander', 'Ableton', 'Gate')
			plugin_obj.plugts_transform('./data_main/plugts/univ_ableton.pltr', 'gate', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('universal', 'vibrato', None):
			extpluglog.convinternal('Universal', 'Vibrato', 'Ableton', 'Chorus2')
			plugin_obj.plugts_transform('./data_main/plugts/univ_ableton.pltr', 'vibrato', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('universal', 'tremolo', None):
			extpluglog.convinternal('Universal', 'Tremolo', 'Ableton', 'Chorus2')
			plugin_obj.plugts_transform('./data_main/plugts/univ_ableton.pltr', 'tremolo', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('universal', 'tuner', None):
			extpluglog.convinternal('Universal', 'Tuner', 'Ableton', 'Tuner')
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('refrence', 'refrence', 440)
			plugin_obj.replace('native', 'ableton', 'Tuner')
			manu_obj.to_param('refrence', 'TuningFreq', None)
			return 1

		if plugin_obj.type.check_wildmatch('universal', 'spectrum_analyzer', None):
			extpluglog.convinternal('Universal', 'Spectrum Analyzer', 'Ableton', 'Spectrum Analyzer')
			plugin_obj.replace('native', 'ableton', 'SpectrumAnalyzer')
			return 1

		if plugin_obj.type.check_wildmatch('universal', 'filter', None):
			extpluglog.convinternal('Universal', 'Filter', 'Ableton', 'Eq8')
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
			return 1

		is_eq_bands = plugin_obj.type.check_wildmatch('universal', 'eq', 'bands')
		is_eq_8limited = plugin_obj.type.check_wildmatch('universal', 'eq', '8limited')

		if is_eq_bands or is_eq_8limited:
			if is_eq_bands:
				extpluglog.convinternal('Universal', 'EQ Bands', 'Ableton', 'Eq8')
			if is_eq_8limited:
				extpluglog.convinternal('Universal', 'EQ 8-Limited', 'Ableton', 'Eq8')
				plugin_obj.eq.from_8limited(pluginid)

			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('gain_out', 'gain_out', 0)
			plugin_obj.replace('native', 'ableton', 'Eq8')

			for band_num, f in enumerate(plugin_obj.eq):
				filter_id, filter_obj = f

				abe_starttxt = "Bands."+str(band_num)+"/ParameterA/"

				als_shape = eq_types.index(filter_obj.type.type)+1 if filter_obj.type.type in eq_types else 3

				if als_shape == 1 and filter_obj.slope > 36: als_shape = 0
				if als_shape == 6 and filter_obj.slope > 36: als_shape = 7

				plugin_obj.params.add(abe_starttxt+'Freq', filter_obj.freq, 'float')
				plugin_obj.params.add(abe_starttxt+'Gain', filter_obj.gain, 'float')
				plugin_obj.params.add(abe_starttxt+'IsOn', bool(filter_obj.on), 'bool')
				plugin_obj.params.add(abe_starttxt+'Mode', als_shape, 'float')
				plugin_obj.params.add(abe_starttxt+'Q', filter_obj.q, 'float')

				convproj_obj.automation.move(['n_filter', pluginid, filter_id, 'on'], ['plugin', pluginid, abe_starttxt+'IsOn'])
				convproj_obj.automation.move(['n_filter', pluginid, filter_id, 'freq'], ['plugin', pluginid, abe_starttxt+'Freq'])
				convproj_obj.automation.move(['n_filter', pluginid, filter_id, 'gain'], ['plugin', pluginid, abe_starttxt+'Gain'])

			manu_obj.to_param('gain_out', 'GlobalGain', 0)
			return 0

		return 2
