# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import math
from functions import xtramath
from objects.inst_params import fx_delay
from functions import extpluglog

def get_freq(i_val):
	return 20 * 1000**i_val

def get_gain(i_val):
	return min((math.sqrt(i_val**1.15)*40)-20, 0)

def eq_calc_q(band_type, i_val):
	if band_type in ['low_pass', 'high_pass']:
		q_val = i_val*math.log(162)
		q_val = 0.1 * math.exp(q_val)
		q_val = xtramath.logpowmul(q_val, 0.5)
	elif band_type in ['low_shelf', 'high_shelf']:
		q_val = i_val*math.log(162)
		q_val = 0.1 * math.exp(q_val)
	else:
		q_val = i_val*math.log(162)
		#q_val = 0.1 * math.exp(q_val)
		q_val = xtramath.logpowmul(q_val, -1) if q_val != 0 else q_val
	return q_val

autotune_chords = {
	0: [0,2,4,5,7,9,11],
	1: [0,4,7],
	2: [0,2,4,7,9],
	3: [0,2,3,5,7,8,10],
	4: [0,2,3,5,7,8,11],
	5: [0,2,3,5,7,9,11],
	6: [0,3,7],
	7: [0,3,5,7,10],
	9: [0,3,5,6,7,10],
	10: [0,1,2,3,4,5,6,7,8,9,10,11]
}


class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'

	def get_priority(self):
		return 0

	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'soundation', None]]
		in_dict['in_daws'] = ['soundation']
		in_dict['out_plugins'] = [['universal', None, None]]
		in_dict['out_daws'] = []

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.type.check_wildmatch('native', 'soundation', 'com.soundation.filter'):
			extpluglog.convinternal('Soundation', 'Filter', 'Universal', 'Filter')
			filter_cutoff = plugin_obj.params.get('cutoff', 0).value
			filter_resonance = plugin_obj.params.get('resonance', 0).value+1
			filter_mode = plugin_obj.params.get('mode', 0).value

			plugin_obj.replace('universal', 'filter', None)
			plugin_obj.filter.on = True
			plugin_obj.filter.type.set('low_pass' if filter_mode else 'high_pass', None)
			plugin_obj.filter.freq = get_freq(filter_cutoff)
			plugin_obj.filter.q = filter_resonance

			convproj_obj.automation.move(['plugin', pluginid, "cutoff"], ['filter', pluginid, 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, "resonance"], ['filter', pluginid, 'q'])
			convproj_obj.automation.calc(['filter', pluginid, 'freq'], 'pow_r', 1000, 0, 0, 0)
			convproj_obj.automation.calc(['filter', pluginid, 'freq'], 'mul', 20, 0, 0, 0)
			convproj_obj.automation.calc(['filter', pluginid, 'q'], 'add', 1, 0, 0, 0)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'soundation', 'com.soundation.butterworthfilter'):
			extpluglog.convinternal('Soundation', 'Butterworth Filter', 'Universal', 'Filter')
			filter_cutoff = plugin_obj.params.get('cutoff', 0).value
			filter_resonance = plugin_obj.params.get('resonance', 0).value+15

			plugin_obj.replace('universal', 'filter', None)
			plugin_obj.filter.on = True
			plugin_obj.filter.type.set('low_pass', None)
			plugin_obj.filter.freq = get_freq(filter_cutoff)
			plugin_obj.filter.q = filter_resonance

			convproj_obj.automation.move(['plugin', pluginid, "cutoff"], ['filter', pluginid, 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, "resonance"], ['filter', pluginid, 'q'])
			convproj_obj.automation.calc(['filter', pluginid, 'freq'], 'pow_r', 1000, 0, 0, 0)
			convproj_obj.automation.calc(['filter', pluginid, 'freq'], 'mul', 20, 0, 0, 0)
			convproj_obj.automation.calc(['filter', pluginid, 'q'], 'mul', 15, 0, 0, 0)
			convproj_obj.automation.calc(['filter', pluginid, 'q'], 'add', 1, 0, 0, 0)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'soundation', 'com.soundation.equalizer'):
			extpluglog.convinternal('Soundation', 'Equalizer', 'Universal', '3-Band EQ')
			plugin_obj.plugts_transform('./data_main/plugts/soundation_univ.pltr', 'equalizer', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'soundation', 'com.soundation.parametric-eq'):
			extpluglog.convinternal('Soundation', 'EQ', 'Universal', 'EQ 8-Limited')

			#HP
			filter_obj = plugin_obj.named_filter_add('high_pass')
			filter_obj.type.set('high_pass', None)
			filter_obj.on = bool(plugin_obj.params.get('hpf_enable', 0).value)
			filter_obj.freq = get_freq(plugin_obj.params.get('hpf_freq', 0).value)
			filter_obj.gain = (plugin_obj.params.get('hpf_gain', 0.5).value-0.5)*40
			filter_obj.q = eq_calc_q('hpf', plugin_obj.params.get('hpf_res', 0).value)

			convproj_obj.automation.calc(['plugin', pluginid, 'hpf_freq'], 'pow_r', 1000, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'hpf_freq'], 'mul', 20, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'hpf_freq'], ['n_filter', pluginid, 'high_pass', 'freq'])
			convproj_obj.automation.calc(['plugin', pluginid, 'hpf_gain'], 'add', -0.5, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'hpf_gain'], 'mul', 40, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'hpf_gain'], ['n_filter', pluginid, 'high_pass', 'gain'])
			convproj_obj.automation.move(['plugin', pluginid, 'hpf_enable'], ['n_filter', pluginid, 'high_pass', 'on'])

			#low_shelf
			filter_obj = plugin_obj.named_filter_add('low_shelf')
			filter_obj.type.set('low_shelf', None)
			filter_obj.on = bool(plugin_obj.params.get('lowshelf_enable', 0).value)
			filter_obj.freq = get_freq(plugin_obj.params.get('lowshelf_freq', 0).value)
			filter_obj.gain = (plugin_obj.params.get('lowshelf_gain', 0).value-0.5)*40
			filter_obj.q = eq_calc_q('lowshelf', plugin_obj.params.get('lowshelf_res', 0).value)

			convproj_obj.automation.calc(['plugin', pluginid, 'lowshelf_freq'], 'pow_r', 1000, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'lowshelf_freq'], 'mul', 20, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'lowshelf_freq'], ['n_filter', pluginid, 'low_shelf', 'freq'])
			convproj_obj.automation.calc(['plugin', pluginid, 'lowshelf_gain'], 'add', -0.5, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'lowshelf_gain'], 'mul', 40, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'lowshelf_gain'], ['n_filter', pluginid, 'low_shelf', 'gain'])
			convproj_obj.automation.move(['plugin', pluginid, 'lowshelf_enable'], ['n_filter', pluginid, 'low_shelf', 'on'])

			#peak
			for peak_num in range(4):
				peak_txt = 'peak'+str(peak_num+1)
				cvpj_txt = 'peak_'+str(peak_num+1)
				filter_obj = plugin_obj.named_filter_add(cvpj_txt)
				filter_obj.type.set('peak', None)
				filter_obj.on = bool(plugin_obj.params.get(peak_txt+'_enable', 0).value)
				filter_obj.freq = get_freq(plugin_obj.params.get(peak_txt+'_freq', 0).value)
				filter_obj.gain = (plugin_obj.params.get(peak_txt+'_gain', 0).value-0.5)*40
				filter_obj.q = eq_calc_q('peak', plugin_obj.params.get(peak_txt+'_res', 0).value)

				convproj_obj.automation.calc(['plugin', pluginid, peak_txt+'_freq'], 'pow_r', 1000, 0, 0, 0)
				convproj_obj.automation.calc(['plugin', pluginid, peak_txt+'_freq'], 'mul', 20, 0, 0, 0)
				convproj_obj.automation.move(['plugin', pluginid, peak_txt+'_freq'], ['n_filter', pluginid, cvpj_txt, 'freq'])
				convproj_obj.automation.calc(['plugin', pluginid, peak_txt+'_gain'], 'add', -0.5, 0, 0, 0)
				convproj_obj.automation.calc(['plugin', pluginid, peak_txt+'_gain'], 'mul', 40, 0, 0, 0)
				convproj_obj.automation.move(['plugin', pluginid, peak_txt+'_gain'], ['n_filter', pluginid, cvpj_txt, 'gain'])
				convproj_obj.automation.move(['plugin', pluginid, peak_txt+'_enable'], ['n_filter', pluginid, cvpj_txt, 'on'])

			#low_shelf
			filter_obj = plugin_obj.named_filter_add('high_shelf')
			filter_obj.type.set('high_shelf', None)
			filter_obj.on = bool(plugin_obj.params.get('highshelf_enable', 0).value)
			filter_obj.freq = get_freq(plugin_obj.params.get('highshelf_freq', 0).value)
			filter_obj.gain = (plugin_obj.params.get('highshelf_gain', 0).value-0.5)*40
			filter_obj.q = eq_calc_q('highshelf', plugin_obj.params.get('highshelf_res', 0).value)

			convproj_obj.automation.calc(['plugin', pluginid, 'highshelf_freq'], 'pow_r', 1000, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'highshelf_freq'], 'mul', 20, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'highshelf_freq'], ['n_filter', pluginid, 'high_shelf', 'freq'])
			convproj_obj.automation.calc(['plugin', pluginid, 'highshelf_gain'], 'add', -0.5, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'highshelf_gain'], 'mul', 40, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'highshelf_gain'], ['n_filter', pluginid, 'high_shelf', 'gain'])
			convproj_obj.automation.move(['plugin', pluginid, 'highshelf_enable'], ['n_filter', pluginid, 'high_shelf', 'on'])

			#low_shelf
			filter_obj = plugin_obj.named_filter_add('low_pass')
			filter_obj.type.set('low_pass', None)
			filter_obj.on = bool(plugin_obj.params.get('lpf_enable', 0).value)
			filter_obj.freq = get_freq(plugin_obj.params.get('lpf_freq', 0).value)
			filter_obj.gain = (plugin_obj.params.get('lpf_gain', 0.5).value-0.5)*40
			filter_obj.q = eq_calc_q('lpf', plugin_obj.params.get('lpf_res', 0).value)

			convproj_obj.automation.calc(['plugin', pluginid, 'lpf_freq'], 'pow_r', 1000, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'lpf_freq'], 'mul', 20, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'lpf_freq'], ['n_filter', pluginid, 'low_pass', 'freq'])
			convproj_obj.automation.calc(['plugin', pluginid, 'lpf_gain'], 'add', -0.5, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'lpf_gain'], 'mul', 40, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'lpf_gain'], ['n_filter', pluginid, 'low_pass', 'gain'])
			convproj_obj.automation.move(['plugin', pluginid, 'lpf_enable'], ['n_filter', pluginid, 'low_pass', 'on'])

			master_gain = plugin_obj.params.get('master_gain', 0).value
			master_gain = (master_gain-0.5)*40

			convproj_obj.automation.calc(['plugin', pluginid, 'master_gain'], 'add', -0.5, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'master_gain'], 'mul', 40, 0, 0, 0)
			convproj_obj.automation.move_group(['plugin', pluginid], 'master_gain', 'gain_out')
			
			plugin_obj.replace('universal', 'eq', '8limited')

			plugin_obj.params.add('gain_out', master_gain, 'float')
			return 1
			
		if plugin_obj.type.check_wildmatch('native', 'soundation', 'com.soundation.compressor'):
			extpluglog.convinternal('Soundation', 'Compressor', 'Universal', 'Compressor')

			comp_attack = plugin_obj.params.get('attack', 0).value
			comp_ratio = plugin_obj.params.get('ratio', 0).value
			comp_release = plugin_obj.params.get('release', 0).value
			comp_threshold = plugin_obj.params.get('threshold', 0).value

			comp_gain = plugin_obj.params.get('gain', 0).value

			comp_attack = ((comp_attack**2)*200)/1000
			comp_release = (comp_release**2)*5
			comp_threshold = (comp_threshold*50)-50
			comp_gain = get_gain(comp_gain)
			comp_ratio = 1/(max(1-(comp_ratio**0.25), 0.0001))

			plugin_obj.replace('universal', 'compressor', None)
			plugin_obj.params.add('ratio', comp_ratio, 'float')
			plugin_obj.params.add('threshold', comp_threshold, 'float')
			plugin_obj.params.add('attack', comp_attack, 'float')
			plugin_obj.params.add('release', comp_release, 'float')
			plugin_obj.params.add('postgain', comp_gain, 'float')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'soundation', 'com.soundation.degrader'):
			extpluglog.convinternal('Soundation', 'Degrader', 'Universal', 'Bitcrush')
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('reduction', 'reduction', 0)
			manu_obj.from_param('rate', 'rate', 0)
			manu_obj.from_param('mix', 'mix', 0)
			manu_obj.calc('reduction', 'mul', 50, 0, 0, 0)
			manu_obj.calc('reduction', 'sub_r', 48, 0, 0, 0)
			manu_obj.calc('rate', 'pow', 0.1, 0, 0, 0)
			manu_obj.calc('rate', 'from_one', 44100, 1000, 0, 0)
			plugin_obj.replace('universal', 'bitcrush', None)
			manu_obj.to_param('reduction', 'bits', 0)
			manu_obj.to_param('rate', 'freq', 0)
			manu_obj.to_wet('mix')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'soundation', 'com.soundation.delay'):
			extpluglog.convinternal('Soundation', 'Delay', 'Universal', 'Delay')
			feedback = plugin_obj.params.get('feedback', 0).value
			feedback_filter = plugin_obj.params.get('feedback_filter', 0).value
			timeBpmSync = plugin_obj.params.get('timeBpmSync', 0).value
			timeL = plugin_obj.params.get('timeL', 0).value
			timeLSynced = plugin_obj.params.get('timeLSynced', 0).value
			timeR = plugin_obj.params.get('timeR', 0).value
			timeRSynced = plugin_obj.params.get('timeRSynced', 0).value
			wet = plugin_obj.params.get('wet', 0).value
			dry = plugin_obj.params.get('dry', 0).value

			delay_obj = fx_delay.fx_delay()
			delay_obj.feedback_first = True
			delay_obj.feedback[0] = feedback

			for n in range(2):
				timing_obj = delay_obj.timing_add(n)
				if timeBpmSync: timing_obj.set_steps(16/(1/(timeLSynced if not n else timeRSynced)), convproj_obj)
				else: timing_obj.set_seconds(timeL if not n else timeR)

			delay_obj.cut_high = get_freq(feedback_filter**0.5)
			plugin_obj, pluginid = delay_obj.to_cvpj(convproj_obj, pluginid)
			plugin_obj.params_slot.add('wet', xtramath.wetdry(wet, dry), 'float')
			return 1
			
		if plugin_obj.type.check_wildmatch('native', 'soundation', 'com.soundation.limiter'):
			extpluglog.convinternal('Soundation', 'Limiter', 'Universal', 'Limiter')

			comp_attack = plugin_obj.params.get('attack', 0).value
			comp_gain = plugin_obj.params.get('gain', 0).value
			comp_release = plugin_obj.params.get('release', 0).value
			comp_threshold = plugin_obj.params.get('threshold', 0).value

			comp_attack = ((comp_attack**2)*200)/1000
			comp_release = (comp_release**2)*5
			comp_gain = get_gain(comp_gain)
			comp_threshold = ((1-comp_threshold)**3)*50

			plugin_obj.replace('universal', 'limiter', None)
			plugin_obj.params.add('attack', comp_attack, 'float')
			plugin_obj.params.add('release', comp_release, 'float')
			plugin_obj.params.add('postgain', comp_gain, 'float')
			plugin_obj.params.add('threshold', comp_threshold, 'float')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'soundation', 'com.soundation.pitch-correction'):
			extpluglog.convinternal('Soundation', 'AutoTune', 'Universal', 'AutoTune')
			tune_amount = plugin_obj.params.get('amount', 0).value
			tune_glide = plugin_obj.params.get('glide', 0).value
			tune_key = int(plugin_obj.params.get('key', 0).value)
			tune_mode = int(plugin_obj.params.get('mode', 0).value)
			plugin_obj.replace('universal', 'autotune', None)

			if tune_mode in autotune_chords:
				for p_key in autotune_chords[tune_mode]: 
					plugin_obj.params.add('key_on_'+str((p_key+tune_key)%12), True, 'bool')

		return 2