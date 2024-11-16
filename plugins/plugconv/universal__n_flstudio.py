# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import math
from functions import xtramath
from objects.inst_params import fx_delay
from functions import extpluglog

def oldcalc_filterfreq_1(value):
	filter_cutoff = value**0.6
	filter_cutoff = 10 * 1600**(filter_cutoff)
	return filter_cutoff

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'flstudio', None]]
		in_dict['in_daws'] = ['flp']
		in_dict['out_plugins'] = [['universal', None, None]]
		in_dict['out_daws'] = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity 7 band eq'):
			extpluglog.convinternal('FL Studio', 'Fruity 7 Band Equalizer', 'Universal', 'EQ Bands')

			bandsdata = max([plugin_obj.params.get('band_'+str(bandnum+1), 0).value for bandnum in range(7)])

			if bandsdata<=1800:
				for bandnum, bandfreq in enumerate([63,250,500,1500,3000,5000,8000]):
					bandstarttxt = str(bandnum+1)
					gain_txt = 'band_'+bandstarttxt

					filter_obj, filterid = plugin_obj.eq_add()
					filter_obj.freq = bandfreq
					filter_obj.gain = plugin_obj.params.get(gain_txt, 0).value/100
					filter_obj.type.set('peak', None)

					convproj_obj.automation.calc(['plugin', pluginid, gain_txt], 'div', 100, 0, 0, 0)
					convproj_obj.automation.move(['plugin', pluginid, gain_txt], ['n_filter', pluginid, filterid, 'gain'])

				plugin_obj.replace('universal', 'eq', 'bands')
				return 1
			else:
				return 2

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity parametric eq'):
			extpluglog.convinternal('FL Studio', 'Fruity Parametric EQ', 'Universal', 'EQ Bands')

			for bandnum in range(7):
				bandstarttxt = str(bandnum+1)

				filter_obj, _ = plugin_obj.eq_add()

				filter_obj.gain = plugin_obj.params.get(bandstarttxt+'_gain', 0).value/100

				fl_band_freq = plugin_obj.params.get(bandstarttxt+'_freq', 0).value/65536
				filter_obj.freq = 10 * 1600**(fl_band_freq**0.6)

				fl_band_type = plugin_obj.params.get(bandstarttxt+'_type', 0).value
				fl_band_width = plugin_obj.params.get(bandstarttxt+'_width', 0).value/65536

				filter_obj.type.set('peak', None)

				if fl_band_type in [5, 7]: 
					filter_obj.q = (1-fl_band_width)*1.2
				elif fl_band_type in [1, 3]: 
					fl_band_width = xtramath.between_from_one(1, -1, fl_band_width)
					filter_obj.q = pow(2, fl_band_width*5)
				else: 
					outwid = ((fl_band_width+0.01)*3)
					outwid = xtramath.logpowmul(outwid, -1)
					filter_obj.q = outwid

				if fl_band_type != 0: filter_obj.on = True
				if fl_band_type == 1: filter_obj.type.set('low_pass', None)
				if fl_band_type == 2: filter_obj.type.set('band_pass', None)
				if fl_band_type == 3: filter_obj.type.set('high_pass', None)
				if fl_band_type == 4: filter_obj.type.set('notch', None)
				if fl_band_type == 5: filter_obj.type.set('low_shelf', None)
				if fl_band_type == 6: filter_obj.type.set('peak', None)
				if fl_band_type == 7: filter_obj.type.set('high_shelf', None)

			plugin_obj.replace('universal', 'eq', 'bands')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity parametric eq 2'):
			extpluglog.convinternal('FL Studio', 'Fruity Parametric EQ 2', 'Universal', 'EQ Bands')
			main_lvl = plugin_obj.params.get('main_lvl', 0).value/100

			for bandnum in range(7):
				bandstarttxt = str(bandnum+1)

				filter_obj, filterid = plugin_obj.eq_add()
				filter_obj.type.set('peak', None)

				filter_obj.gain = plugin_obj.params.get(bandstarttxt+'_gain', 0).value/100

				fl_band_freq = plugin_obj.params.get(bandstarttxt+'_freq', 0).value/65536
				filter_obj.freq = 20 * 1000**fl_band_freq

				fl_band_type = plugin_obj.params.get(bandstarttxt+'_type', 0).value
				fl_band_width = plugin_obj.params.get(bandstarttxt+'_width', 0).value/65536

				if fl_band_type in [5, 7]: 
					filter_obj.q = (1-fl_band_width)*1.2
				elif fl_band_type in [1, 3]: 
					fl_band_width = xtramath.between_from_one(1, -1, fl_band_width)
					filter_obj.q = pow(2, fl_band_width*5)
				else: 
					outwid = ((fl_band_width+0.01)*3)
					outwid = xtramath.logpowmul(outwid, -1)
					filter_obj.q = outwid

				if fl_band_type != 0: filter_obj.on = True
				if fl_band_type == 1: filter_obj.type.set('low_pass', None)
				if fl_band_type == 2: filter_obj.type.set('band_pass', None)
				if fl_band_type == 3: filter_obj.type.set('high_pass', None)
				if fl_band_type == 4: filter_obj.type.set('notch', None)
				if fl_band_type == 5: filter_obj.type.set('low_shelf', None)
				if fl_band_type == 6: filter_obj.type.set('peak', None)
				if fl_band_type == 7: filter_obj.type.set('high_shelf', None)

				txt_freq = bandstarttxt+'_freq'
				convproj_obj.automation.calc(['plugin', pluginid, txt_freq], 'div', 65536, 0, 0, 0)
				convproj_obj.automation.calc(['plugin', pluginid, txt_freq], 'pow_r', 1000, 0, 0, 0)
				convproj_obj.automation.calc(['plugin', pluginid, txt_freq], 'mul', 20, 0, 0, 0)
				convproj_obj.automation.move(['plugin', pluginid, txt_freq], ['n_filter', pluginid, filterid, 'freq'])

				txt_gain = bandstarttxt+'_gain'
				convproj_obj.automation.calc(['plugin', pluginid, txt_gain], 'div', 100, 0, 0, 0)
				convproj_obj.automation.move(['plugin', pluginid, txt_gain], ['n_filter', pluginid, filterid, 'gain'])

			plugin_obj.replace('universal', 'eq', 'bands')
			param_obj = plugin_obj.params.add('gain_out', main_lvl, 'float')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity compressor'):
			extpluglog.convinternal('FL Studio', 'Fruity Compressor', 'Universal', 'Compressor')
			v_threshold = plugin_obj.params.get('threshold', 0).value/10
			v_ratio = plugin_obj.params.get('ratio', 0).value/10
			v_gain = plugin_obj.params.get('gain', 0).value/10
			v_attack = plugin_obj.params.get('attack', 0).value/10000
			v_release = plugin_obj.params.get('release', 0).value/1000

			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('threshold', 'threshold', 0)
			manu_obj.from_param('ratio', 'ratio', 0)
			manu_obj.from_param('gain', 'gain', 0)
			manu_obj.from_param('attack', 'attack', 0)
			manu_obj.from_param('release', 'release', 0)
			manu_obj.calc('threshold', 'div', 10, 0, 0, 0)
			manu_obj.calc('ratio', 'div', 10, 0, 0, 0)
			manu_obj.calc('gain', 'div', 10, 0, 0, 0)
			manu_obj.calc('attack', 'div', 10000, 0, 0, 0)
			manu_obj.calc('release', 'div', 1000, 0, 0, 0)

			v_type = plugin_obj.params.get('type', 0).value
			first_type = v_type>>2
			second_type = v_type%4
			if second_type == 0: v_knee = 0
			if second_type == 1: v_knee = 6
			if second_type == 2: v_knee = 7
			if second_type == 3: v_knee = 15
			if first_type == 0: v_tcr = 0
			if first_type == 1: v_tcr = 1

			plugin_obj.replace('universal', 'compressor', None)
			plugin_obj.datavals.add('tcr', bool(v_tcr) )
			manu_obj.to_param('gain', 'pregain', None)
			manu_obj.to_param('ratio', 'ratio', None)
			manu_obj.to_param('threshold', 'threshold', None)
			manu_obj.to_param('attack', 'attack', None)
			manu_obj.to_param('release', 'release', None)
			plugin_obj.params.add('knee', v_knee, 'float')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'pitcher'):
			extpluglog.convinternal('FL Studio', 'Pitcher', 'Universal', 'AutoTune')
			p_hz = xtramath.between_from_one(415.3, 466.2, plugin_obj.datavals.get('hz', 0))
			p_min_freq = [220,170,110,80,55,25][int(plugin_obj.datavals.get('min_freq', 0))]
			p_speed = plugin_obj.params.get('correction_speed', 1).value
			p_gender = plugin_obj.params.get('gender', 1).value
			p_formant = bool(plugin_obj.datavals.get('formant', 0))
			plugin_obj.replace('universal', 'autotune', None)
			for keynum, p_key in enumerate(plugin_obj.array_get('key_on', 12)):
				plugin_obj.params.add('key_on_'+str(keynum), p_key, 'bool')
			for keynum, p_key in enumerate(plugin_obj.array_get('bypass', 12)):
				plugin_obj.params.add('key_bypass_'+str(keynum), p_key, 'bool')
			plugin_obj.params.add('calibrate', p_hz, 'float')
			plugin_obj.params.add('speed', p_speed, 'float')
			plugin_obj.params.add('min_freq', p_min_freq, 'float')
			plugin_obj.params.add('formant_gender', p_gender, 'float')
			plugin_obj.params.add('formant_on', p_formant, 'bool')
			return 1
		
		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity delay'):
			extpluglog.convinternal('FL Studio', 'Fruity Delay', 'Universal', 'Delay')
			d_fb = plugin_obj.params.get('fb', 0).value/1024
			d_input = plugin_obj.params.get('input', 0).value/1024
			d_tempo = plugin_obj.params.get('tempo', 0).value/1024
			d_steps = plugin_obj.params.get('steps', 1).value
			d_mode = plugin_obj.params.get('mode', 0).value

			delay_obj = fx_delay.fx_delay()
			delay_obj.feedback_first = False
			delay_obj.feedback[0] = d_fb**2
			delay_obj.feedback_invert = d_mode==1
			if d_mode==2: 
				delay_obj.mode = 'pingpong'
				delay_obj.submode = 'normal'
			timing_obj = delay_obj.timing_add(0)
			if not d_tempo: timing_obj.set_steps(d_steps, convproj_obj)
			else: timing_obj.set_steps_nonsync(d_steps, (d_tempo*220)+60)
			delay_obj.to_cvpj(convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity fast lp'):
			extpluglog.convinternal('FL Studio', 'Fruity Fast LP', 'Universal', 'Filter')
			filter_cutoff = plugin_obj.params.get('cutoff', 0).value/1024
			filter_resonance = plugin_obj.params.get('reso', 0).value/1024
			filter_cutoff = 0.2+(filter_cutoff*1.0)
			plugin_obj.replace('universal', 'filter', None)
			plugin_obj.filter.on = True
			plugin_obj.filter.type.set('low_pass', None)
			plugin_obj.filter.freq = xtramath.midi_filter(filter_cutoff**1.5)
			plugin_obj.filter.q = (filter_resonance*6)+1
			return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity filter'):
			extpluglog.convinternal('FL Studio', 'Fruity Filter', 'Universal', 'Filter')
			filter_cutoff = plugin_obj.params.get('cutoff', 0).value/1024
			filter_resonance = plugin_obj.params.get('reso', 0).value/1024

			filter_cutoff = (filter_cutoff*2)**0.95
			filter_cutoff = filter_cutoff**3.325

			plugin_obj.replace('universal', 'filter', None)
			plugin_obj.filter.on = True
			plugin_obj.filter.type.set('low_pass', None)
			plugin_obj.filter.freq = filter_cutoff*1000
			plugin_obj.filter.q = (filter_resonance*6)+1
			return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity flanger'):
			extpluglog.convinternal('FL Studio', 'Fruity Flanger', 'Universal', 'Flanger')

			p_rate = plugin_obj.params.get('rate', 0).value/5000
			p_depth = plugin_obj.params.get('depth', 0).value/5000
			p_delay = plugin_obj.params.get('delay', 0).value/5000
			p_feed = plugin_obj.params.get('feed', 0).value/100
			p_inv_feedback = plugin_obj.params.get('inv_feedback', 0).value>512

			p_rate = (p_rate**7)*5
			p_delay = p_delay**2.58495

			plugin_obj.replace('universal', 'flanger', None)
			plugin_obj.params.add('delay', p_delay*0.020, 'float')
			plugin_obj.params.add('rate', p_rate, 'float')
			plugin_obj.params.add('depth', p_depth, 'float')
			plugin_obj.params.add('feedback', p_feed, 'float')
			plugin_obj.params.add('feedback_invert', p_inv_feedback, 'bool')

			lfo_obj = plugin_obj.lfo_add('flanger')
			lfo_obj.time.set_hz(p_rate)
			lfo_obj.amount = p_depth
			return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity free filter'):
			extpluglog.convinternal('FL Studio', 'Fruity Free Filter', 'Universal', 'Filter')
			filter_cutoff = plugin_obj.params.get('freq', 0).value/1024
			filter_resonance = plugin_obj.params.get('q', 0).value/1024
			filter_type = plugin_obj.params.get('type', 0).value/700
			filter_gain = plugin_obj.params.get('gain', 0).value/1024 

			filter_resonance = 0.01+(filter_resonance*0.99)
			filter_resonance = filter_resonance/0.1

			plugin_obj.replace('universal', 'filter', None)
			plugin_obj.filter.on = True
			plugin_obj.filter.type.set(['low_pass','band_pass','high_pass','notch','low_shelf','peak','high_shelf'][min(int(filter_type/0.125)-1, 6)], None)
			plugin_obj.filter.gain = filter_gain*18
			plugin_obj.filter.freq = oldcalc_filterfreq_1(min(filter_cutoff, 1024))
			plugin_obj.filter.q = filter_resonance**0.8
			return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity limiter'):
			extpluglog.convinternal('FL Studio', 'Fruity Limiter', 'Universal', 'Limiter')
			plugin_obj.replace('universal', 'limiter', None)
			plugin_obj.params.add('attack', 0.002, 'float')
			plugin_obj.params.add('release', 0.1, 'float')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity reeverb'):
			extpluglog.convinternal('FL Studio', 'Fruity Reeverb', 'Universal', 'Reverb')
			plugin_obj.plugts_transform('./data_main/plugts/flstudio_univ.pltr', 'fruity_reeverb', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity reeverb 2'):
			extpluglog.convinternal('FL Studio', 'Fruity Reeverb 2', 'Universal', 'Reverb')
			plugin_obj.plugts_transform('./data_main/plugts/flstudio_univ.pltr', 'fruity_reeverb_2', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity balance'):
			extpluglog.convinternal('FL Studio', 'Fruity Balance', 'Universal', 'Vol/Pan')
			plugin_obj.plugts_transform('./data_main/plugts/flstudio_univ.pltr', 'fruity_balance', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'frequency shifter'):
			extpluglog.convinternal('FL Studio', 'Frequency Shifter', 'Universal', 'Frequency Shifter')
			p_frequency = plugin_obj.params.get('frequency', 0).value/70000
			p_freqtype = plugin_obj.params.get('freqtype', 0).value
			p_frequency = ((p_frequency**7)*(200 if p_freqtype else 20000))

			plugin_obj.replace('universal', 'frequency_shifter', None)
			plugin_obj.params.add('pitch', p_frequency, 'float')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'tuner'):
			extpluglog.convinternal('FL Studio', 'Tuner', 'Universal', 'Tuner')
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('refrence', 'refrence', 440)
			manu_obj.calc('refrence', 'valrange', 0, 6000, 400, 480)
			plugin_obj.replace('universal', 'tuner', None)
			manu_obj.to_param('refrence', 'refrence', None)
			return 1

		if 'shareware' not in dv_config.extplug_cat:
			if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity delay 2'):
				extpluglog.convinternal('FL Studio', 'Fruity Delay 2', 'Universal', 'Delay')
				d_dry = plugin_obj.params.get('dry', 0).value/128
				d_fb_cut = plugin_obj.params.get('fb_cut', 0).value/128
				d_fb_mode = plugin_obj.params.get('fb_mode', 0).value
				d_fb_vol = plugin_obj.params.get('fb_vol', 0).value/128
				d_input_pan = plugin_obj.params.get('input_pan', 0).value/128
				d_input_vol = plugin_obj.params.get('input_vol', 0).value/160
				d_time = plugin_obj.params.get('time', 0).value/48
				d_time_stereo_offset = plugin_obj.params.get('time_stereo_offset', 1).value/512

				delay_obj = fx_delay.fx_delay()
				delay_obj.feedback_first = False
				delay_obj.input = d_input_vol
				delay_obj.input_pan = d_input_pan
				delay_obj.dry = d_dry
				delay_obj.stereo_offset = d_time_stereo_offset
				delay_obj.feedback[0] = d_fb_vol**2
				delay_obj.feedback_invert = d_fb_mode==1
				if d_fb_mode==2: 
					delay_obj.mode = 'pingpong'
					delay_obj.submode = 'normal'
				timing_obj = delay_obj.timing_add(0)
				timing_obj.set_steps(d_time, convproj_obj)
				plugin_obj = delay_obj.to_cvpj(convproj_obj, pluginid)
				return 1

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity spectroman'):
			extpluglog.convinternal('FL Studio', 'Fruity Spectroman', 'Universal', 'Spectrum Analyzer')
			plugin_obj.replace('universal', 'spectrum_analyzer', None)
			return 1

		return 2