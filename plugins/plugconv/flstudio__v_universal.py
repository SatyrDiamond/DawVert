# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import math
from functions import note_data
from functions import extpluglog
from functions import xtramath

def eq2q_calc(filter_obj):
	eq_band_q = filter_obj.q
	filter_type = filter_obj.type.type
	if filter_type in ['low_shelf', 'high_shelf']: 
		eq_band_q = 1-(eq_band_q/1.2)
	elif filter_type in ['low_pass', 'high_pass']:
		eq_band_q = (eq_band_q**-2)/2
	else: 
		eq_band_q = eq_band_q**-1
		eq_band_q = (eq_band_q-0.01)/3
	eq_band_q = xtramath.clamp(eq_band_q, 0, 1)
	return eq_band_q

def eq2q_filtype(filter_obj):
	fl_band_type = 0
	if filter_obj.on:
		if filter_obj.type.check_wildmatch('low_pass', None): fl_band_type = 1
		if filter_obj.type.check_wildmatch('band_pass', None): fl_band_type = 2
		if filter_obj.type.check_wildmatch('high_pass', None): fl_band_type = 3
		if filter_obj.type.check_wildmatch('notch', None): fl_band_type = 4
		if filter_obj.type.check_wildmatch('low_shelf', None): fl_band_type = 5
		if filter_obj.type.check_wildmatch('peak', None): fl_band_type = 6
		if filter_obj.type.check_wildmatch('high_shelf', None): fl_band_type = 7
	return fl_band_type

def eq2q_freq(filter_obj):
	return (math.log(max(20, filter_obj.freq)/20) / math.log(1000)) if filter_obj.freq != 0 else 0

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return 100
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['universal', None, None]]
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = [['native', 'flstudio', None]]
		in_dict['out_daws'] = ['flp']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):
		
		if plugin_obj.type.check_wildmatch('universal', 'filter', None):
			extpluglog.convinternal('Universal', 'Filter', 'FL Studio', 'Fruity Parametric EQ 2')
			plugin_obj.replace('native', 'flstudio', 'fruity parametric eq 2')
			plugin_obj.params.add('4_type', eq2q_filtype(plugin_obj.filter), 'int')
			plugin_obj.params.add('4_width', int(eq2q_calc(plugin_obj.filter)*65536), 'int')
			plugin_obj.params.add('4_freq', int(eq2q_freq(plugin_obj.filter)*65536), 'int')
			return 0

		is_eq_bands = plugin_obj.type.check_wildmatch('universal', 'eq', 'bands')
		is_eq_8limited = plugin_obj.type.check_wildmatch('universal', 'eq', '8limited')

		if is_eq_bands or is_eq_8limited:
			if is_eq_bands:
				extpluglog.convinternal('Universal', 'EQ Bands', 'FL Studio', 'Fruity Parametric EQ 2')
			if is_eq_8limited:
				extpluglog.convinternal('Universal', 'EQ 8-Limited', 'FL Studio', 'Fruity Parametric EQ 2')
				plugin_obj.eq.from_8limited(pluginid)
				
			gain_out = plugin_obj.params.get("gain_out", 0).value
			plugin_obj.replace('native', 'flstudio', 'fruity parametric eq 2')
			for n, f in enumerate(plugin_obj.eq):
				filter_id, filter_obj = f

				starttxt = str(n)+'_'
				plugin_obj.params.add(starttxt+'type', eq2q_filtype(filter_obj), 'int')
				plugin_obj.params.add(starttxt+'width', int(eq2q_calc(filter_obj)*65536), 'int')
				plugin_obj.params.add(starttxt+'freq', int(eq2q_freq(filter_obj)*65536), 'int')
				plugin_obj.params.add(starttxt+'gain', filter_obj.gain*100, 'int')

			plugin_obj.params.add('main_lvl', gain_out*100, 'int')
			return 0

		if plugin_obj.type.check_wildmatch('universal', 'tuner', None):
			extpluglog.convinternal('Universal', 'Tuner', 'FL Studio', 'Tuner')
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('refrence', 'refrence', 440)
			manu_obj.calc('refrence', 'valrange', 400, 480, 0, 6000)
			plugin_obj.replace('native', 'flstudio', 'tuner')
			manu_obj.to_param('refrence', 'refrence', None)
			return 0

		if plugin_obj.type.check_wildmatch('universal', 'frequency_shifter', None):
			extpluglog.convinternal('Universal', 'Frequency Shifter', 'FL Studio', 'Frequency Shifter')
			p_pitch = plugin_obj.params.get('pitch', 0).value
			p_freqtype = p_pitch>200
			p_frequency = (p_pitch/200)**(1/7.0707) if not p_freqtype else (p_pitch/20000)**(1/12)
			plugin_obj.replace('native', 'flstudio', 'frequency shifter')
			plugin_obj.params.add('frequency', p_frequency*70000, 'int')
			plugin_obj.params.add('freqtype', not p_freqtype, 'int')

		if plugin_obj.type.check_wildmatch('universal', 'spectrum_analyzer', None):
			extpluglog.convinternal('Universal', 'Spectrum Analyzer', 'FL Studio', 'Fruity Spectroman')
			plugin_obj.replace('native', 'flstudio', 'fruity spectroman')
			return 0

		return 2
