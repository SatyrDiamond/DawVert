# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

from functions import data_bytes
from functions import xtramath
from functions import note_data
from objects.inst_params import fx_delay
from functions import extpluglog

import math

delaytab = [[32, 1, ''], [28, 1, ''], [24, 1, ''], [20, 1, ''], [16, 1, ''], [12, 1, ''], [10, 1, ''], [8, 1, ''], [6, 1, ''], [5, 1, ''], [4, 1, ''], [3, 1, ''], [2, 1, ''], [1, 1, ''], [1, 1, 'd'], [1, 1, ''], [1, 1, 't'], [1, 2, 'd'], [1, 2, ''], [1, 2, 't'], [1, 4, 'd'], [1, 4, ''], [1, 4, 't'], [1, 8, 'd'], [1, 8, ''], [1, 8, 't'], [1, 16, 'd'], [1, 16, ''], [1, 16, 't'], [1, 32, 'd'], [1, 32, ''], [1, 32, 't'], [1, 64, 'd'], [1, 64, ''], [1, 64, 't']]

def djeq_calc_gain(lvl): return math.log2((lvl*2)**13.8) if lvl else -100 

def reverb_calc_freq(freq): return 13.75**(1+(freq*2.821))

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'tracktion', None]]
		in_dict['in_daws'] = ['waveform_edit']
		in_dict['out_plugins'] = [['universal', None, None]]
		in_dict['out_daws'] = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):

		if plugin_obj.type.check_wildmatch('native', 'tracktion', 'chorusEffect'):
			extpluglog.convinternal('Waveform', 'chorusEffect', 'Universal', 'Chorus')
			p_delay = plugin_obj.params.get('delay', 10).value/1000
			p_depth = plugin_obj.params.get('depth', 20).value/1000
			p_mix = plugin_obj.params.get('mix', 1).value
			p_rateSyncOff = plugin_obj.params.get('rateSyncOff', 1).value
			p_rateSyncOn = int(plugin_obj.params.get('rateSyncOn', 1).value)
			p_sync = plugin_obj.params.get('sync', True).value

			plugin_obj.replace('universal', 'chorus', None)
			plugin_obj.params.add('delay', p_delay, 'float')
			plugin_obj.params.add('depth', p_depth, 'float')

			timing_obj = plugin_obj.timing_add('chorus')
			if not p_sync:
				timing_obj.set_hz(p_rateSyncOff)
			else:
				if p_rateSyncOn < 35: 
					num, denum, stxt = delaytab[p_rateSyncOn]
					timing_obj.set_frac(num, denum, stxt, convproj_obj)

			plugin_obj.fxdata_add(None, p_mix/2)

		if plugin_obj.type.check_wildmatch('native', 'tracktion', '1bandEq'):
			extpluglog.convinternal('Waveform', '1bandEq', 'Universal', 'Filter')
			band_freq = plugin_obj.params.get('freq', 30).value
			band_shape = plugin_obj.params.get('shape', 0).value
			band_q = plugin_obj.params.get('q', 1).value
			band_gain = plugin_obj.params.get('gain', 0).value
			band_slope = plugin_obj.params.get('slope', 0).value

			if band_shape == 0: band_shape = 'low_pass'
			if band_shape == 1: band_shape = 'low_shelf'
			if band_shape == 2: band_shape = 'peak'
			if band_shape == 5: band_shape = 'high_shelf'
			if band_shape == 6: band_shape = 'high_pass'

			plugin_obj.replace('universal', 'filter', None)
			plugin_obj.filter.on = True
			plugin_obj.filter.type.set(band_shape, None)
			plugin_obj.filter.freq = note_data.note_to_freq(band_freq-72)
			plugin_obj.filter.q = band_q
			plugin_obj.filter.gain = band_gain
			plugin_obj.filter.slope = band_slope

			convproj_obj.automation.calc(['plugin', pluginid, 'freq'], 'add', -72, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'freq'], 'note2freq', 0, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'freq'], ['filter', pluginid, 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, "gain"], ['filter', pluginid, 'gain'])
			convproj_obj.automation.move(['plugin', pluginid, "q"], ['filter', pluginid, 'q'])
			return 1

		if plugin_obj.type.check_wildmatch('native', 'tracktion', '3bandEq'):
			extpluglog.convinternal('Waveform', '3bandEq', 'Universal', 'EQ Bands')
			freq1 = plugin_obj.params.get('freq1', 43.34996032714844).value
			freq2 = plugin_obj.params.get('freq2', 90.23263549804688).value
			freq3 = plugin_obj.params.get('freq3', 119.2130889892578).value
			gain1 = plugin_obj.params.get('gain1', 0).value
			gain2 = plugin_obj.params.get('gain2', 0).value
			gain3 = plugin_obj.params.get('gain3', 0).value

			filter_obj, filterid = plugin_obj.eq_add()
			filter_obj.type.set('low_shelf', None)
			filter_obj.freq = note_data.note_to_freq(freq1-72)
			filter_obj.gain = gain1
			convproj_obj.automation.calc(['plugin', pluginid, 'freq1'], 'add', -72, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'freq1'], 'note2freq', 0, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'freq1'], ['n_filter', pluginid, filterid, 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, "gain1"], ['n_filter', pluginid, filterid, 'gain'])

			filter_obj, filterid = plugin_obj.eq_add()
			filter_obj.type.set('peak', None)
			filter_obj.freq = note_data.note_to_freq(freq2-72)
			filter_obj.gain = gain2
			convproj_obj.automation.calc(['plugin', pluginid, 'freq2'], 'add', -72, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'freq2'], 'note2freq', 0, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'freq2'], ['n_filter', pluginid, filterid, 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, "gain2"], ['n_filter', pluginid, filterid, 'gain'])

			filter_obj, filterid = plugin_obj.eq_add()
			filter_obj.type.set('high_shelf', None)
			filter_obj.freq = note_data.note_to_freq(freq3-72)
			filter_obj.gain = gain3
			convproj_obj.automation.calc(['plugin', pluginid, 'freq3'], 'add', -72, 0, 0, 0)
			convproj_obj.automation.calc(['plugin', pluginid, 'freq3'], 'note2freq', 0, 0, 0, 0)
			convproj_obj.automation.move(['plugin', pluginid, 'freq3'], ['n_filter', pluginid, filterid, 'freq'])
			convproj_obj.automation.move(['plugin', pluginid, "gain3"], ['n_filter', pluginid, filterid, 'gain'])

			plugin_obj.replace('universal', 'eq', 'bands')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'tracktion', '8bandEq'):
			extpluglog.convinternal('Waveform', '8bandEq', 'Universal', 'EQ Bands')

			for num in range(8):
				eqnumtxt = str(num+1)

				for typenum in range(2):
					typename = ['lm', 'rs'][typenum]
					endtxt = eqnumtxt+typename
					band_enable = int(plugin_obj.params.get("enable"+endtxt, 1).value)
					band_freq = plugin_obj.params.get("freq"+endtxt, 25).value
					band_gain = plugin_obj.params.get("gain"+endtxt, 0).value
					band_q = plugin_obj.params.get("q"+endtxt, 1).value
					band_shape = plugin_obj.params.get("shape"+endtxt, 1).value
					band_slope = plugin_obj.params.get("slope"+endtxt, 12).value

					if band_shape == 0: band_shape = 'low_pass'
					if band_shape == 1: band_shape = 'low_shelf'
					if band_shape == 2: band_shape = 'peak'
					if band_shape == 3: band_shape = 'band_pass'
					if band_shape == 4: band_shape = 'band_stop'
					if band_shape == 5: band_shape = 'high_shelf'
					if band_shape == 6: band_shape = 'high_pass'

					if not typenum: filter_obj, filterid = plugin_obj.eq_add()
					else: filter_obj, filterid = plugin_obj.named_eq_add('alt')

					filter_obj.on = bool(band_enable)
					filter_obj.freq = note_data.note_to_freq(band_freq-72)
					filter_obj.gain = band_gain
					filter_obj.q = band_q
					filter_obj.type.set(band_shape, None)
					filter_obj.slope = band_slope

					convproj_obj.automation.calc(['plugin', pluginid, "freq"+endtxt], 'add', -72, 0, 0, 0)
					convproj_obj.automation.calc(['plugin', pluginid, "freq"+endtxt], 'note2freq', 0, 0, 0, 0)
					convproj_obj.automation.move(['plugin', pluginid, "freq"+endtxt], ['n_filter', pluginid, filterid, 'freq'])
					convproj_obj.automation.move(['plugin', pluginid, "gain"+endtxt], ['n_filter', pluginid, filterid, 'gain'])
					convproj_obj.automation.move(['plugin', pluginid, "q"+endtxt], ['n_filter', pluginid, filterid, 'q'])

			eq_mode = plugin_obj.params.get("mode", 0).value
			cvpj_eq_mode = ['normal', 'l_r', 'm_s'][eq_mode]

			plugin_obj.replace('universal', 'eq', 'bands')
			plugin_obj.datavals.add('mode', cvpj_eq_mode)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'tracktion', 'comp'):
			extpluglog.convinternal('Waveform', 'Compressor', 'Universal', 'Compressor')
			plugin_obj.plugts_transform('./data_main/plugts/waveform_univ.pltr', 'comp', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'tracktion', 'gate'):
			extpluglog.convinternal('Waveform', 'Gate', 'Universal', 'Gate')
			plugin_obj.plugts_transform('./data_main/plugts/waveform_univ.pltr', 'gate', convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'tracktion', 'limiter'):
			extpluglog.convinternal('Waveform', 'Limiter', 'Universal', 'Limiter')
			plugin_obj.plugts_transform('./data_main/plugts/waveform_univ.pltr', 'limiter', convproj_obj, pluginid)
			return 1
			
		if plugin_obj.type.check_wildmatch('native', 'tracktion', 'spectrum'):
			extpluglog.convinternal('Waveform', 'Spectrum Analyzer', 'Universal', 'Spectrum Analyzer')
			plugin_obj.replace('universal', 'spectrum_analyzer', None)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'tracktion', 'djeq'):
			extpluglog.convinternal('Waveform', 'DJ EQ', 'Universal', '3-Band EQ')
			freq1 = plugin_obj.params.get('freq1', 59.213096618652344).value
			freq2 = plugin_obj.params.get('freq2', 99.07624816894531).value
			bass = plugin_obj.params.get('bass', 1).value/1.5
			mid = plugin_obj.params.get('mid', 1).value/1.5
			treble = plugin_obj.params.get('treble', 1).value/1.5

			plugin_obj.replace('universal', 'eq', '3band')
			plugin_obj.params.add('low_gain', djeq_calc_gain(bass), 'float')
			plugin_obj.params.add('mid_gain', djeq_calc_gain(mid), 'float')
			plugin_obj.params.add('high_gain', djeq_calc_gain(treble), 'float')
			plugin_obj.params.add('lowmid_freq', note_data.note_to_freq(freq1-72), 'float')
			plugin_obj.params.add('midhigh_freq', note_data.note_to_freq(freq2-72), 'float')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'tracktion', 'pitchShifter'):
			extpluglog.convinternal('Waveform', 'Pitch Shifter', 'Universal', 'Pitch Shifter')
			pitchmod = plugin_obj.params.get('semitonesUp', 0).value
			plugin_obj.replace('universal', 'pitchshift', None)
			plugin_obj.params.add('pitch', pitchmod, 'float')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'tracktion', 'stereoDelay'):
			extpluglog.convinternal('Waveform', 'Stereo Delay', 'Universal', 'Delay')
			crossL = plugin_obj.params.get('crossL', 0).value
			crossR = plugin_obj.params.get('crossR', 0).value
			delaySyncOffL = plugin_obj.params.get('delaySyncOffL', 0).value
			delaySyncOffR = plugin_obj.params.get('delaySyncOffR', 0).value
			delaySyncOnL = plugin_obj.params.get('delaySyncOnL', 0).value
			delaySyncOnR = plugin_obj.params.get('delaySyncOnR', 0).value
			feedbackL = plugin_obj.params.get('feedbackL', 0).value
			feedbackR = plugin_obj.params.get('feedbackR', 0).value
			highcut = plugin_obj.params.get('highcut', 0).value
			lowcut = plugin_obj.params.get('lowcut', 0).value
			mix = plugin_obj.params.get('mix', 0).value
			mixLock = plugin_obj.params.get('mixLock', 0).value
			panL = plugin_obj.params.get('panL', 0).value
			panR = plugin_obj.params.get('panR', 0).value
			volL = plugin_obj.params.get('volL', 0).value
			volR = plugin_obj.params.get('volR', 0).value

			sync = int(plugin_obj.params.get('sync', 0).value)

			delay_obj = fx_delay.fx_delay()

			time_m = []
			time_m.append(delay_obj.timing_add(0))
			time_m.append(delay_obj.timing_add(1))
			if not sync:
				time_m[0].set_seconds(delaySyncOffL/1000)
				time_m[1].set_seconds(delaySyncOffR/1000)
			else:
				for n, x in enumerate([delaySyncOnL, delaySyncOnR]):
					if x < 35: 
						num, denum, stxt = delaytab[x]
						time_m[n].set_frac(num, denum, stxt, convproj_obj)

			delay_obj.feedback_pan[0] = panL
			delay_obj.feedback_pan[1] = panR
			delay_obj.feedback[0] = feedbackL/100
			delay_obj.feedback[1] = feedbackR/100
			delay_obj.feedback_cross[0] = crossL/100
			delay_obj.feedback_cross[1] = crossR/100
			delay_obj.cut_low = lowcut
			delay_obj.cut_high = highcut
			plugin_obj, pluginid = delay_obj.to_cvpj(convproj_obj, pluginid)
			plugin_obj.fxdata_add(None, mix)

		if plugin_obj.type.check_wildmatch('native', 'tracktion', 'naturalReverb'):
			extpluglog.convinternal('Waveform', 'Natural Reverb', 'Universal', 'Reverb')
			decay = plugin_obj.params.get('decay', 0).value
			definition = plugin_obj.params.get('definition', 0).value
			diffusion = plugin_obj.params.get('diffusion', 0).value
			highCut = plugin_obj.params.get('highCut', 0).value
			highDamp = plugin_obj.params.get('highDamp', 0).value
			lowCut = plugin_obj.params.get('lowCut', 0).value
			lowDamp = plugin_obj.params.get('lowDamp', 0).value
			mix = plugin_obj.params.get('mix', 0).value
			mixLock = plugin_obj.params.get('mixLock', 0).value
			pan = plugin_obj.params.get('pan', 0).value
			preDelay = plugin_obj.params.get('preDelay', 0).value
			size = plugin_obj.params.get('size', 0).value
			slope = plugin_obj.params.get('slope', 0).value

			lowCut = reverb_calc_freq(lowCut)
			highCut = reverb_calc_freq(highCut)
			size = (10+(size*50))/100
			decay = ((decay*2)**3)*15

			plugin_obj.replace('universal', 'reverb', None)
			plugin_obj.params.add('low_cut', lowCut, 'float')
			plugin_obj.params.add('high_cut', highCut, 'float')
			plugin_obj.params.add('size', size, 'float')
			plugin_obj.params.add('decay', decay, 'float')
			plugin_obj.params.add('predelay', preDelay, 'float')
			plugin_obj.params.add('diffusion', diffusion, 'float')
			plugin_obj.params.add('dry', 0, 'float')
			plugin_obj.params.add('wet', 1, 'float')
			plugin_obj.fxdata_add(None, mix)

		return 2