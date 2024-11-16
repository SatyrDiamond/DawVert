# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import os
import math
import bisect

from functions import extpluglog
from objects.convproj import wave

fl_voc_bandnums = [4,8,16,32,64,128]
als_voc_bandnums = [4,8,12,16,20,24,28,32,36,40]

def eq2q_freq(freq):
	return (math.log(max(20, freq)/20) / math.log(1000)) if freq != 0 else 0

def fl_to_freq(value): 
	preval = (math.log(value/10) / math.log(1000))
	return int((preval**2)*32768)

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return -100
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'ableton', None]]
		in_dict['in_daws'] = ['ableton']
		in_dict['out_plugins'] = [['native', 'flstudio', None]]
		in_dict['out_daws'] = ['flp']

	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):

		if plugin_obj.type.check_wildmatch('native', 'ableton', 'Vocoder'):
			extpluglog.convinternal('Ableton', 'Vocoder', 'FL Studio', 'Fruity Vocoder')
			als_BandCount = als_voc_bandnums[int(plugin_obj.datavals.get('FilterBank/BandCount', 4))]
			band_lvls = [float(plugin_obj.datavals.get('FilterBank/BandLevel.'+str(n), 1)) for n in range(als_BandCount)]
			fl_BandCount = fl_voc_bandnums[bisect.bisect_left(fl_voc_bandnums, als_BandCount)]
			plugin_obj.array_add('bands', band_lvls)
			if als_BandCount != fl_BandCount: plugin_obj.array_resize('bands', fl_BandCount)

			EnvelopeRate = plugin_obj.params.get('EnvelopeRate', 0).value
			EnvelopeRelease = plugin_obj.params.get('EnvelopeRelease', 0).value
			FormantShift = plugin_obj.params.get('FormantShift', 0).value
			FilterBandWidth = plugin_obj.params.get('FilterBandWidth', 0).value
			plugin_obj.replace('native', 'flstudio', 'fruity vocoder')
			plugin_obj.params.add('env_att', int(EnvelopeRate), 'int')
			plugin_obj.params.add('env_rel', int(EnvelopeRelease), 'int')
			plugin_obj.params.add('freq_bandwidth', int(FilterBandWidth*200), 'int')
			plugin_obj.params.add('freq_formant', int(FormantShift*100), 'int')
			return 0

		#if plugin_obj.type.check_wildmatch('native', 'ableton', 'FilterDelay'):
		#	plugin_obj.params.debugtxt()
		#	EnvelopeRate = plugin_obj.params.get('EnvelopeRate', 0).value
#
		#	filterparts = []
		#	for num in range(3):
		#		endnum = str(num+1)
		#		p_BandWidth = plugin_obj.params.get('BandWidth'+endnum, 0).value
		#		p_BeatDelayEnum = plugin_obj.params.get('BeatDelayEnum'+endnum, 0).value
		#		p_BeatDelayOffset = plugin_obj.params.get('BeatDelayOffset'+endnum, 0).value
		#		p_DelayTime = plugin_obj.params.get('DelayTime'+endnum, 0).value
		#		p_DelayTimeSwitch = plugin_obj.params.get('DelayTimeSwitch'+endnum, 0).value
		#		p_Feedback = plugin_obj.params.get('Feedback'+endnum, 0).value
		#		p_FilterOn = plugin_obj.params.get('FilterOn'+endnum, 0).value
		#		p_MidFreq = plugin_obj.params.get('MidFreq'+endnum, 0).value
		#		p_On = plugin_obj.params.get('On'+endnum, 0).value
		#		p_Pan = plugin_obj.params.get('Pan'+endnum, 0).value
		#		p_Volume = plugin_obj.params.get('Volume'+endnum, 0).value
		#		filterparts.append([p_BandWidth,p_BeatDelayEnum,p_BeatDelayOffset,p_DelayTime,p_DelayTimeSwitch,p_Feedback,p_FilterOn,p_MidFreq,p_On,p_Pan,p_Volume])
#
		#	plugin_obj.replace('native', 'flstudio', 'fruity delay bank')
#
		#	plugin_obj.datavals.add('version', 16)
		#	plugin_obj.params.add('dry', 128, 'int')
		#	plugin_obj.params.add('wet', 128, 'int')
		#	plugin_obj.params.add('bank_1_v/pan', -128, 'int')
		#	plugin_obj.params.add('bank_2_v/pan', 0, 'int')
		#	plugin_obj.params.add('bank_3_v/pan', 128, 'int')
#
		#	for num, fddata in enumerate(filterparts):
		#		p_BandWidth,p_BeatDelayEnum,p_BeatDelayOffset,p_DelayTime,p_DelayTimeSwitch,p_Feedback,p_FilterOn,p_MidFreq,p_On,p_Pan,p_Volume = fddata
		#		starttxtv = 'bank_'+str(num+1)+'_v'
		#		starttxte = 'bank_'+str(num+1)+'_e'
#
		#		plugin_obj.params.add(starttxte+'/enabled', p_On, 'int')
		#		plugin_obj.params.add(starttxtv+'/out_pan', p_Pan*128, 'int')
		#		plugin_obj.params.add(starttxtv+'/out_vol', p_Volume*128, 'int')
		#		plugin_obj.params.add(starttxtv+'/fbfilter_cut', eq2q_freq(p_MidFreq)*65536, 'int')
		#		plugin_obj.params.add(starttxtv+'/fbfilter_res', (p_BandWidth/9)*65536, 'int')
		#		plugin_obj.params.add(starttxtv+'/feedback_vol', p_Feedback*128, 'int')

		return 2

