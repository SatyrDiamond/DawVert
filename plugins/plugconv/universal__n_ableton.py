# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import math
from functions import xtramath
from functions import note_data
from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'ableton', None]]
		in_dict['in_daws'] = ['ableton']
		in_dict['out_plugins'] = [['universal', None, None]]
		in_dict['out_daws'] = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):

		if plugin_obj.type.check_wildmatch('native', 'ableton', 'AutoFilter'):
			extpluglog.convinternal('Ableton', 'AutoFilter', 'Universal', 'Filter')
			
			p_Cutoff = plugin_obj.params.get('Cutoff', 60).value-72
			p_Resonance = plugin_obj.params.get('Resonance', 1).value
			p_FilterType = plugin_obj.params.get('FilterType', 1).value
			p_Slope = plugin_obj.params.get('Slope', 0).value

			plugin_obj.replace('universal', 'filter', None)
			filter_obj = plugin_obj.filter
			filter_obj.on = True
			if p_FilterType == 0: filter_obj.type.set('low_pass', None)
			if p_FilterType == 1: filter_obj.type.set('high_pass', None)
			if p_FilterType == 2: filter_obj.type.set('band_pass', None)
			if p_FilterType == 3: filter_obj.type.set('notch', None)
			filter_obj.freq = note_data.note_to_freq(p_Cutoff)
			filter_obj.q = (1+(p_Resonance-0.12))**3
			filter_obj.slope = 24 if p_Slope else 12

			convproj_obj.automation.calc(['plugin', pluginid, 'Resonance'], 'add', 1-0.12, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'Resonance'], 'pow', 3, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'Resonance'], ['filter', pluginid, 'q'])

			convproj_obj.automation.calc(['plugin', pluginid, 'Cutoff'], 'add', -72, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'Cutoff'], 'note2freq', 0, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'Cutoff'], ['filter', pluginid, 'freq'])
			return 1

		if plugin_obj.type.check_wildmatch('native', 'ableton', 'ChannelEq'):
			extpluglog.convinternal('Ableton', 'Channel EQ', 'Universal', 'EQ Bands')
			p_HighpassOn = plugin_obj.params.get("HighpassOn", 0).value
			p_HighShelfGain = plugin_obj.params.get("HighShelfGain", 0).value
			p_LowShelfGain = plugin_obj.params.get("LowShelfGain", 0).value
			p_MidFrequency = plugin_obj.params.get("MidFrequency", 0).value
			p_MidGain = plugin_obj.params.get("MidGain", 0).value
			p_Gain = plugin_obj.params.get("Gain", 0).value

			filter_obj, filter_id = plugin_obj.eq_add()
			filter_obj.on = p_HighpassOn
			filter_obj.type.set('high_pass', None)
			filter_obj.freq = 80

			filter_obj, filter_id = plugin_obj.eq_add()
			filter_obj.on = True
			filter_obj.type.set('low_shelf', None)
			filter_obj.freq = 100
			filter_obj.gain = xtramath.to_db(p_LowShelfGain)
			convproj_obj.automation.calc(['plugin', pluginid, 'LowShelfGain'], 'to_db', 0, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, "LowShelfGain"], ['n_filter', pluginid, filter_id, 'gain'])

			filter_obj, filter_id = plugin_obj.eq_add()
			filter_obj.on = True
			filter_obj.type.set('peak', None)
			filter_obj.freq = p_MidFrequency
			filter_obj.q = 1
			filter_obj.gain = xtramath.to_db(p_MidGain)
			convproj_obj.automation.calc(['plugin', pluginid, 'MidGain'], 'to_db', 0, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, "MidGain"], ['n_filter', pluginid, filter_id, 'gain'])
			convproj_obj.automation.move(['plugin', pluginid, "MidFrequency"], ['n_filter', pluginid, filter_id, 'freq'])

			filter_obj, filter_id = plugin_obj.eq_add()
			filter_obj.on = True
			filter_obj.type.set('high_shelf', None)
			filter_obj.freq = 5000
			filter_obj.gain = xtramath.to_db(p_HighShelfGain)
			convproj_obj.automation.calc(['plugin', pluginid, 'HighShelfGain'], 'to_db', 0, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, "HighShelfGain"], ['n_filter', pluginid, filter_id, 'gain'])

			plugin_obj.replace('universal', 'eq', 'bands')
			plugin_obj.params.add('gain_out', xtramath.to_db(p_Gain), 'float')
			convproj_obj.automation.calc(['plugin', pluginid, 'Gain'], 'to_db', 0, 0, 0, 0)
			convproj_obj.automation.move_group(['plugin', pluginid], 'Gain', 'gain_out')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'ableton', 'AutoPan'):
			extpluglog.convinternal('Ableton', 'AutoPan', 'Universal', 'Auto Pan')
			p_LfoAmount = plugin_obj.params.get('Lfo/LfoAmount', 1).value
			p_Frequency = plugin_obj.params.get('Lfo/Frequency', 1).value
			p_Type = plugin_obj.params.get('Lfo/Type', 0).value
			p_Phase = plugin_obj.params.get('Lfo/Phase', 0).value
			plugin_obj.replace('universal', 'autopan', None)
			lfo_obj = plugin_obj.lfo_add('amount')
			lfo_obj.time.set_hz(p_Frequency)
			lfo_obj.amount = p_LfoAmount
			lfo_obj.prop.shape = ['sine','triangle','saw','random'][p_Type]
			lfo_obj.phase = p_Phase
			return 1

		if plugin_obj.type.check_wildmatch('native', 'ableton', 'Tuner'):
			extpluglog.convinternal('Ableton', 'Tuner', 'Universal', 'Tuner')
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('TuningFreq', 'TuningFreq', 440)
			plugin_obj.replace('universal', 'tuner', None)
			manu_obj.to_param('TuningFreq', 'refrence', None)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'ableton', 'Redux2'):
			extpluglog.convinternal('Ableton', 'Redux2', 'Universal', 'Bitcrush')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_univ.pltr', 'redux2', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'ableton', 'Limiter'):
			extpluglog.convinternal('Ableton', 'Limiter', 'Universal', 'Limiter')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_univ.pltr', 'limiter', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'ableton', 'Gate'):
			extpluglog.convinternal('Ableton', 'Gate', 'Universal', 'Gate')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_univ.pltr', 'gate', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'ableton', 'FilterEQ3'):
			extpluglog.convinternal('Ableton', 'FilterEQ3', 'Universal', '3 Band EQ')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_univ.pltr', 'filtereq3', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'ableton', 'SpectrumAnalyzer'):
			extpluglog.convinternal('Ableton', 'SpectrumAnalyzer', 'Universal', 'Spectrum Analyzer')
			plugin_obj.replace('universal', 'spectrum_analyzer', None)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'ableton', 'FrequencyShifter'):
			p_Coarse = plugin_obj.params.get("Coarse", 0).value
			p_Fine = plugin_obj.params.get("Fine", 0).value
			p_ModulationMode = plugin_obj.params.get("ModulationMode", 0).value
			p_RingModCoarse = plugin_obj.params.get("RingModCoarse", 0).value

			if p_ModulationMode == 0:
				extpluglog.convinternal('Ableton', 'Frequency Shifter', 'Universal', 'Frequency Shifter')
				f = p_Coarse+p_Fine
				plugin_obj.replace('universal', 'frequency_shifter', None)
				plugin_obj.params.add('pitch', f, 'float')
				return 1

			if p_ModulationMode == 1:
				extpluglog.convinternal('Ableton', 'Ringmod', 'Universal', 'Ringmod')
				f = abs(p_RingModCoarse+p_Fine)
				plugin_obj.replace('universal', 'ringmod', None)
				plugin_obj.params.add('rate', f, 'float')
				lfo_obj = plugin_obj.lfo_add('amount')
				lfo_obj.time.set_hz(f)
				lfo_obj.amount = 1
				return 1

		if plugin_obj.type.check_wildmatch('native', 'ableton', 'Compressor2'):
			p_Model = plugin_obj.params.get('Model', 0).value
			if p_Model != 2: 
				extpluglog.convinternal('Ableton', 'Compressor2', 'Universal', 'Compressor')
				plugin_obj.plugts_transform('./data_main/plugts/ableton_univ.pltr', 'compressor2_comp', convproj_obj, pluginid)
			else: 
				extpluglog.convinternal('Ableton', 'Compressor2', 'Universal', 'Expander')
				plugin_obj.plugts_transform('./data_main/plugts/ableton_univ.pltr', 'compressor2_expand', convproj_obj, pluginid)
			plugin_obj.datavals.add('mode', 'rms' if p_Model == 1 else 'peak')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'ableton', 'Eq8'):
			extpluglog.convinternal('Ableton', 'EQ8', 'Universal', 'EQ Bands')
			for band_num in range(8):
				groupname = ['main', 'b']
				abe_starttxt = "Bands."+str(band_num)+"/ParameterA/"
				abe_starttxt_alt = "Bands."+str(band_num)+"/ParameterB/"
					
				band_mode = plugin_obj.params.get(abe_starttxt+"Mode", 0).value
				band_mode_alt = plugin_obj.params.get(abe_starttxt_alt+"Mode", 0).value

				cvpj_bandtype = ['high_pass', 'high_pass', 'low_shelf', 'peak', 'notch', 'high_shelf', 'low_pass', 'low_pass'][band_mode]
				cvpj_bandtype_alt = ['high_pass', 'high_pass', 'low_shelf', 'peak', 'notch', 'high_shelf', 'low_pass', 'low_pass'][band_mode_alt]

				cvpj_slope = 12 if band_mode not in [0,7] else 48
				cvpj_slope_alt = 12 if band_mode_alt not in [0,7] else 48

				filter_obj, filter_id = plugin_obj.eq_add()
				filter_obj.on = bool(plugin_obj.params.get(abe_starttxt+"IsOn", 0).value)
				filter_obj.freq = int(plugin_obj.params.get(abe_starttxt+"Freq", 0).value)
				filter_obj.gain = plugin_obj.params.get(abe_starttxt+"Gain", 0).value
				filter_obj.q = plugin_obj.params.get(abe_starttxt+"Q", 0).value
				filter_obj.type.set(cvpj_bandtype, None)
				filter_obj.slope = cvpj_slope

				convproj_obj.automation.move(['plugin', pluginid, abe_starttxt+"IsOn"], ['n_filter', pluginid, filter_id, 'on'])
				convproj_obj.automation.move(['plugin', pluginid, abe_starttxt+"Freq"], ['n_filter', pluginid, filter_id, 'freq'])
				convproj_obj.automation.move(['plugin', pluginid, abe_starttxt+"Gain"], ['n_filter', pluginid, filter_id, 'gain'])
				convproj_obj.automation.move(['plugin', pluginid, abe_starttxt+"Q"], ['n_filter', pluginid, filter_id, 'q'])

				filter_obj, filter_id = plugin_obj.named_eq_add('alt')
				filter_obj.on = bool(plugin_obj.params.get(abe_starttxt_alt+"IsOn", 0).value)
				filter_obj.freq = int(plugin_obj.params.get(abe_starttxt_alt+"Freq", 0).value)
				filter_obj.gain = plugin_obj.params.get(abe_starttxt_alt+"Gain", 0).value
				filter_obj.q = plugin_obj.params.get(abe_starttxt_alt+"Q", 0).value
				filter_obj.type.set(cvpj_bandtype_alt, None)
				filter_obj.slope = cvpj_slope_alt

				convproj_obj.automation.move(['plugin', pluginid, abe_starttxt_alt+"IsOn"], ['n_filter', pluginid, filter_id, 'on'])
				convproj_obj.automation.move(['plugin', pluginid, abe_starttxt_alt+"Freq"], ['n_filter', pluginid, filter_id, 'freq'])
				convproj_obj.automation.move(['plugin', pluginid, abe_starttxt_alt+"Gain"], ['n_filter', pluginid, filter_id, 'gain'])
				convproj_obj.automation.move(['plugin', pluginid, abe_starttxt_alt+"Q"], ['n_filter', pluginid, filter_id, 'q'])

			plugin_obj.replace('universal', 'eq', 'bands')
			return 1

		return 2