# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import struct
import math
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext_nonfree import params_nf_serato_sampler

loaded_plugtransform = False

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'serato-inst', 'sampler']
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['shareware']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype):

		if 'vst2' in extplugtype:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'Serato Sample', 'Serato')
			if plugin_vst2.check_exists('id', 1399681132):
				extpluglog.extpluglist.success('Serato', 'Sampler')
				params_serato = params_nf_serato_sampler.serato_sampler_data()
	
				sp_obj = plugin_obj.samplepart_get('sample')
				_, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)
	
				slicepad = params_serato.slicePalette["slicePad"]
	
				original_bpm = plugin_obj.datavals.get('original_bpm', 120)
				bpm = plugin_obj.datavals.get('bpm', 120)
	
				samplefilename = sp_obj.get_filepath(convproj_obj, 'win')
	
				params_serato.sourceSong['Name'] = plugin_obj.datavals.get('name', 'None')
				params_serato.sourceSong['File'] = samplefilename
				params_serato.sourceSong['OriginalBPM'] = original_bpm
				params_serato.sourceSong['BPM'] = plugin_obj.datavals.get('bpm', 120)
				params_serato.sourceSong['TempoMap'] = plugin_obj.datavals.get('tempo_map', '')
				params_serato.sourceSong['PlaybackSpeed'] = sp_obj.stretch.calc_real_speed
				params_serato.sourceSong['BpmMultiplier'] = sp_obj.stretch.calc_real_speed
				params_serato.sourceSong['PitchShiftingMethod'] = '0' if plugin_obj.datavals.get('bar_mode_enabled', False) else '2'
	
				for start, end, rdata in plugin_obj.regions:
					#print(start, end, rdata)
	
					slicedata = {
						"StartPosition": rdata['start'],
						"EndPosition": rdata['end'],
						"Color": "#eeff00ff",
						"KeySemitoneOffset": 0.0,
						"PlaybackSpeed": 1.0,
						"Level": 0.0,
						"Attack": 0.0,
						"Release": 0.0,
						"FilterFrequency": 1166.19,
						"Reverse": False,
						"OutputChannel": 0,
						"Name": ""
					}
	
					realnote = 24+(start%8)-((start//8)*8)
	
					slicepad[realnote]['slice'] = slicedata
	
				params_serato.to_cvpj_vst2(convproj_obj, plugin_obj)
				return True
		else: return False