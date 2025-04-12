# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import math
from functions import xtramath
from objects.inst_params import fx_delay
from functions import extpluglog

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'

	def get_priority(self):
		return 0

	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'amped', None]]
		in_dict['in_daws'] = ['amped']
		in_dict['out_plugins'] = [['universal', None, None]]
		in_dict['out_daws'] = []

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.type.check_wildmatch('native', 'amped', 'Delay'):
			extpluglog.convinternal('Amped', 'Delay', 'Universal', 'Delay')
			p_time = plugin_obj.params.get('time', 0).value
			p_fb = plugin_obj.params.get('fb', 0).value
			p_mix = plugin_obj.params.get('mix', 0.5).value
			p_offset = plugin_obj.params.get('offset', 0).value

			delay_obj = fx_delay.fx_delay()
			delay_obj.feedback_first = False
			timing_obj = delay_obj.timing_add(0)
			timing_obj.set_seconds(p_time)
			delay_obj.feedback[0] = p_fb
			delay_obj.stereo_offset = p_offset
			plugin_obj, pluginid = delay_obj.to_cvpj(convproj_obj, pluginid)
			plugin_obj.params_slot.add('wet', p_mix, 'float')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Vibrato'):
			extpluglog.convinternal('Amped', 'Vibrato', 'Universal', 'Vibrato')
			p_delayLfoRateHz = plugin_obj.params.get('delayLfoRateHz', 0).value
			p_delayLfoDepth = plugin_obj.params.get('delayLfoDepth', 0).value
			plugin_obj.plugts_transform('./data_main/plugts/amped_univ.pltr', 'univ_vibrato', convproj_obj, pluginid)
			lfo_obj = plugin_obj.lfo_add('amount')
			lfo_obj.time.set_hz(p_delayLfoRateHz)
			lfo_obj.amount = p_delayLfoDepth
			return 1

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Tremolo'):
			extpluglog.convinternal('Amped', 'Tremolo', 'Universal', 'AutoPan')
			p_lfoARateHz = plugin_obj.params.get('lfoARateHz', 0).value
			p_lfoADepth = plugin_obj.params.get('lfoADepth', 0).value
			plugin_obj.plugts_transform('./data_main/plugts/amped_univ.pltr', 'univ_autopan', convproj_obj, pluginid)
			lfo_obj = plugin_obj.lfo_add('amount')
			lfo_obj.time.set_hz(p_lfoARateHz)
			lfo_obj.amount = p_lfoADepth
			return 1

		if plugin_obj.type.check_wildmatch('native', 'amped', 'BitCrusher'):
			extpluglog.convinternal('Amped', 'BitCrusher', 'Universal', 'BitCrusher')
			plugin_obj.plugts_transform('./data_main/plugts/amped_univ.pltr', 'univ_bitcrush', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Phaser'):
			extpluglog.convinternal('Amped', 'Phaser', 'Universal', 'Phaser')
			p_rate = plugin_obj.params.get('rate', 0).value
			plugin_obj.plugts_transform('./data_main/plugts/amped_univ.pltr', 'univ_phaser', convproj_obj, pluginid)
			lfo_obj = plugin_obj.lfo_add('phaser')
			lfo_obj.time.set_hz(p_rate)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'amped', 'LimiterMini'):
			extpluglog.convinternal('Amped', 'Limiter Mini', 'Universal', 'Limiter')
			plugin_obj.plugts_transform('./data_main/plugts/amped_univ.pltr', 'univ_limitermini', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Limiter'):
			extpluglog.convinternal('Amped', 'Limiter', 'Universal', 'Limiter')
			filter_mode = plugin_obj.params.get('filterMode', 0).value
			if filter_mode == 0: plugin_obj.filter.type.set('low_pass', None)
			if filter_mode == 1: plugin_obj.filter.type.set('high_pass', None)
			if filter_mode == 2: plugin_obj.filter.type.set('band_pass', None)
			plugin_obj.filter.gain = plugin_obj.params.get('filterGainDB', 0).value
			plugin_obj.filter.freq = plugin_obj.params.get('filterFrequency', 44100).value
			plugin_obj.filter.q = plugin_obj.params.get('filterQ', 0).value
			plugin_obj.filter.on = plugin_obj.params.get('filterActive', False).value
			convproj_obj.automation.move(['plugin', pluginid, 'filterGainDB'], ['filter', pluginid, 'gain'])
			convproj_obj.automation.move(['plugin', pluginid, 'filterFrequency'], ['filter', pluginid, 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, 'filterQ'], ['filter', pluginid, 'q'])
			convproj_obj.automation.move(['plugin', pluginid, 'filterActive'], ['filter', pluginid, 'on'])
			plugin_obj.plugts_transform('./data_main/plugts/amped_univ.pltr', 'univ_limiter', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Gate'):
			extpluglog.convinternal('Amped', 'Gate', 'Universal', 'Gate')
			filter_mode = plugin_obj.params.get('filterMode', 0).value
			if filter_mode == 0: plugin_obj.filter.type.set('low_pass', None)
			if filter_mode == 1: plugin_obj.filter.type.set('high_pass', None)
			if filter_mode == 2: plugin_obj.filter.type.set('band_pass', None)
			plugin_obj.filter.gain = plugin_obj.params.get('filterGainDB', 0).value
			plugin_obj.filter.freq = plugin_obj.params.get('filterFrequency', 44100).value
			plugin_obj.filter.q = plugin_obj.params.get('filterQ', 0).value
			plugin_obj.filter.on = plugin_obj.params.get('filterActive', False).value
			convproj_obj.automation.move(['plugin', pluginid, 'filterGainDB'], ['filter', pluginid, 'gain'])
			convproj_obj.automation.move(['plugin', pluginid, 'filterFrequency'], ['filter', pluginid, 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, 'filterQ'], ['filter', pluginid, 'q'])
			convproj_obj.automation.move(['plugin', pluginid, 'filterActive'], ['filter', pluginid, 'on'])
			plugin_obj.plugts_transform('./data_main/plugts/amped_univ.pltr', 'univ_gate', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_matchmulti('native', 'amped', ['Compressor', 'Expander']):
			comp_detect_mode = plugin_obj.params.get('detectMode', 0).value
			comp_circuit_mode = plugin_obj.params.get('circuitMode', 0).value

			filter_mode = plugin_obj.params.get('filterMode', 0).value
			if filter_mode == 0: plugin_obj.filter.type.set('low_pass', None)
			if filter_mode == 1: plugin_obj.filter.type.set('high_pass', None)
			if filter_mode == 2: plugin_obj.filter.type.set('band_pass', None)
			plugin_obj.filter.gain = plugin_obj.params.get('filterGainDB', 0).value
			plugin_obj.filter.freq = plugin_obj.params.get('filterFrequency', 44100).value
			plugin_obj.filter.q = plugin_obj.params.get('filterQ', 0).value
			plugin_obj.filter.on = plugin_obj.params.get('filterActive', False).value
			convproj_obj.automation.move(['plugin', pluginid, 'filterGainDB'], ['filter', pluginid, 'gain'])
			convproj_obj.automation.move(['plugin', pluginid, 'filterFrequency'], ['filter', pluginid, 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, 'filterQ'], ['filter', pluginid, 'q'])
			convproj_obj.automation.move(['plugin', pluginid, 'filterActive'], ['filter', pluginid, 'on'])

			if plugin_obj.type.subtype == 'Compressor':
				extpluglog.convinternal('Amped', 'Compressor', 'Universal', 'Compressor')
				plugin_obj.plugts_transform('./data_main/plugts/amped_univ.pltr', 'univ_compressor', convproj_obj, pluginid)

			if plugin_obj.type.subtype == 'Expander':
				extpluglog.convinternal('Amped', 'Expander', 'Universal', 'Expander')
				plugin_obj.plugts_transform('./data_main/plugts/amped_univ.pltr', 'univ_expander', convproj_obj, pluginid)

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Flanger'):
			extpluglog.convinternal('Amped', 'Flanger', 'Universal', 'Flanger')
			p_delayLfoRateHz = plugin_obj.params.get('delayLfoRateHz', 0).value
			p_delayLfoDepth = plugin_obj.params.get('delayLfoDepth', 0).value
			plugin_obj.plugts_transform('./data_main/plugts/amped_univ.pltr', 'univ_flanger', convproj_obj, pluginid)
			lfo_obj = plugin_obj.lfo_add('flanger')
			lfo_obj.time.set_hz(p_delayLfoRateHz)
			lfo_obj.amount = p_delayLfoDepth

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Equalizer'):
			extpluglog.convinternal('Amped', 'Equalizer', 'Universal', 'EQ Bands')
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

			plugin_obj.replace('universal', 'eq', 'bands')

		if plugin_obj.type.check_wildmatch('native', 'amped', 'EqualizerPro'):
			extpluglog.convinternal('Amped', 'Equalizer Pro', 'Universal', 'EQ Bands')
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

			plugin_obj.replace('universal', 'eq', 'bands')

			plugin_obj.params.add('gain_out', master_gain, 'float')
			return 1

		return 2