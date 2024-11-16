# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

from functions_plugin_ext import plugin_vst2
from functions import extpluglog
from functions import xtramath
from objects.convproj import wave

def getthree(plugin_obj, env_name):
	env_blocks = plugin_obj.env_blocks_get_exists(env_name)
	env_points = plugin_obj.env_points_get_exists(env_name)
	env_asdr = plugin_obj.env_asdr_get_exists(env_name)
	return env_blocks, env_points, env_asdr

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['universal', None, None]
		in_dict['ext_formats'] = ['vst2', 'ladspa']
		in_dict['plugincat'] = ['foss']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype):
		if plugin_obj.type.check_wildmatch('universal', 'eq', '3band'):
			if 'vst2' in extplugtype:
				extpluglog.extpluglist.add('FOSS', 'VST2', '3 Band EQ', 'DISTRHO')
				if plugin_vst2.check_exists('id', 1144210769):
					extpluglog.extpluglist.success('Universal', '3-Band EQ')
					plugin_obj.plugts_transform('./data_ext/plugts/univ_ext.pltr', '3band_vst2', convproj_obj, pluginid)
					plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1144210769, 'param', None, 6)
					return True

		if plugin_obj.type.check_wildmatch('universal', 'compressor', None):
			extpluglog.extpluglist.add('FOSS', 'VST2', 'Compressor', 'SocaLabs')
			exttype = plugins.base.extplug_exists('socalabs', extplugtype, 'compressor')
			if exttype:
				extpluglog.extpluglist.success('Universal', 'Compressor')
				plugin_obj.plugts_transform('./data_ext/plugts/univ_ext.pltr', 'socalabs_compressor', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		if plugin_obj.type.check_wildmatch('universal', 'expander', None): 
			extpluglog.extpluglist.add('FOSS', 'VST2', 'Expander', 'SocaLabs')
			exttype = plugins.base.extplug_exists('socalabs', extplugtype, 'expander')
			if exttype:
				extpluglog.extpluglist.success('Universal', 'Expander')
				plugin_obj.plugts_transform('./data_ext/plugts/univ_ext.pltr', 'socalabs_expander', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		if plugin_obj.type.check_wildmatch('universal', 'limiter', None):
			extpluglog.extpluglist.add('FOSS', 'VST2', 'Limiter', 'SocaLabs')
			exttype = plugins.base.extplug_exists('socalabs', extplugtype, 'limiter')
			if exttype:
				extpluglog.extpluglist.success('Universal', 'Limiter')
				plugin_obj.plugts_transform('./data_ext/plugts/univ_ext.pltr', 'socalabs_limiter', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		if plugin_obj.type.check_wildmatch('universal', 'gate', None):
			extpluglog.extpluglist.add('FOSS', 'VST2', 'Gate', 'SocaLabs')
			exttype = plugins.base.extplug_exists('socalabs', extplugtype, 'gate')
			if exttype:
				extpluglog.extpluglist.success('Universal', 'Gate')
				plugin_obj.plugts_transform('./data_ext/plugts/univ_ext.pltr', 'socalabs_gate', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		if plugin_obj.type.check_wildmatch('universal', 'flanger', None):
			if 'ladspa' in extplugtype:
				extpluglog.extpluglist.add('FOSS', 'LADSPA', 'Calf Flanger', 'Calf')
				extpluglog.extpluglist.success('Universal', 'Flanger')
				plugin_obj.plugts_transform('./data_ext/plugts/univ_ext.pltr', 'ladspa_flanger', convproj_obj, pluginid)
				plugin_obj.datavals.add('path', 'veal')
				plugin_obj.datavals.add('plugin', 'Flanger')
				return True

		if plugin_obj.type.check_wildmatch('universal', 'vibrato', None):
			extpluglog.extpluglist.add('FOSS', 'VST2', 'Vibrato', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Vibrato')
			if exttype:
				extpluglog.extpluglist.success('Universal', 'Vibrato')
				plugin_obj.plugts_transform('./data_ext/plugts/univ_ext.pltr', 'airwindows_vibrato', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True
			if 'ladspa' in extplugtype:
				extpluglog.extpluglist.add('FOSS', 'LADSPA', 'TAP Vibrato', 'TAP')
				extpluglog.extpluglist.success('Universal', 'Vibrato')
				plugin_obj.plugts_transform('./data_ext/plugts/univ_ext.pltr', 'ladspa_vibrato', convproj_obj, pluginid)
				plugin_obj.datavals.add('path', 'tap_vibrato')
				plugin_obj.datavals.add('plugin', 'tap_vibrato')
				return True

		if plugin_obj.type.check_wildmatch('universal', 'autopan', None):
			extpluglog.extpluglist.add('FOSS', 'VST2', 'AutoPan', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'AutoPan')
			if exttype:
				extpluglog.extpluglist.success('Universal', 'AutoPan')
				plugin_obj.plugts_transform('./data_ext/plugts/univ_ext.pltr', 'vst2_autopan', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True
			if 'ladspa' in extplugtype:
				extpluglog.extpluglist.add('FOSS', 'LADSPA', 'TAP AutoPanner', 'TAP')
				extpluglog.extpluglist.success('Universal', 'AutoPan')
				plugtransform.transform('./data_ext/plugts/univ_ext.pltr', 'ladspa_autopan', convproj_obj, plugin_obj, pluginid, dv_config)
				plugin_obj.datavals.add('path', 'tap_autopan')
				plugin_obj.datavals.add('plugin', 'tap_autopan')
				return True

		if plugin_obj.type.check_wildmatch('universal', 'reverb', None):
			extpluglog.extpluglist.add('FOSS', 'VST2', 'Dragonfly Hall Reverb', '')
			exttype = plugins.base.extplug_exists('dragonfly_hall', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('Universal', 'Reverb')
				plugin_obj.plugts_transform('./data_ext/plugts/univ_ext.pltr', 'dragonfly_hall', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		if plugin_obj.type.check_wildmatch('universal', 'spectrumanalyzer', None):
			extpluglog.extpluglist.add('FOSS', 'VST2', 'SpectrumAnalyzer', 'SocaLabs')
			exttype = plugins.base.extplug_exists('socalabs', extplugtype, 'spectrumanalyzer')
			if exttype:
				extpluglog.extpluglist.success('Universal', 'Spectrum Analyzer')
				plugin_obj.replace('user', 'socalabs', 'spectrumanalyzer')
				plugin_obj.params.add('mode', 0.0, 'float')
				plugin_obj.params.add('log', 1.0, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		if plugin_obj.type.check_wildmatch('universal', 'synth-osc', None):
			if plugin_obj.oscs:
				osc_obj = plugin_obj.oscs[0]

				env_b_pitch, env_p_pitch, env_a_pitch = getthree(plugin_obj, 'pitch')
				env_b_duty, env_p_duty, env_a_duty = getthree(plugin_obj, 'duty')
				env_b_vol, env_p_vol, env_a_vol = getthree(plugin_obj, 'vol')

				m8bp_compat = True
				env_vol_max = env_b_vol[1].max

				if len(plugin_obj.oscs) == 1:
					s_osc = plugin_obj.oscs[0]
					if env_vol_max != 15 and env_b_vol[0]: m8bp_compat = False
					if env_p_vol[0]: m8bp_compat = False

					pulse_width = s_osc.params['pulse_width'] if 'pulse_width' in s_osc.params else 0.5

					if s_osc.prop.shape in ['square', 'triangle', 'noise', 'pulse'] and m8bp_compat:
						extpluglog.extpluglist.add('FOSS', 'VST2', 'Magical 8bit Plug 2', '')

						if plugins.base.extplug_exists('magical8bitplug2', extplugtype, None):
							extpluglog.extpluglist.success('Universal', 'Synth-OSC')

							plugin_obj.replace('user', 'yokemura', 'magical8bitplug2')

							if env_a_vol[0]:
								plugin_obj.params.add("attack", env_a_vol[1].attack, 'float')
								plugin_obj.params.add("decay", env_a_vol[1].decay, 'float')
								plugin_obj.params.add("suslevel", env_a_vol[1].sustain, 'float')
								plugin_obj.params.add("release", env_a_vol[1].release, 'float')

							if s_osc.prop.shape != 'noise':	
								if pulse_width <= 0.125: plugin_obj.params.add("duty", 0, 'float')
								elif pulse_width <= 0.25: plugin_obj.params.add("duty", 1, 'float')
								elif pulse_width <= 0.5: plugin_obj.params.add("duty", 2, 'float')
							else:
								noise_type = s_osc.prop.random_type
								if noise_type == '1bit_short': plugin_obj.params.add("duty", 0, 'float')
								if noise_type == '4bit': plugin_obj.params.add("duty", 1, 'float')

							if env_b_pitch[0]:
								plugin_obj.params.add("ispitchsequenceenabled_raw", 1.0, 'float')
								plugin_obj.array_add('pitchEnv', env_b_pitch[1].values)

							if env_b_duty[0]:
								plugin_obj.params.add("isdutysequenceenabled_raw", 1.0, 'float')
								plugin_obj.array_add('dutyEnv', env_b_duty[1].values)

							if env_b_vol[0]:
								plugin_obj.params.add("isvolumesequenceenabled_raw", 1.0, 'float')
								plugin_obj.array_add('volumeEnv', env_b_vol[1].values)

							if s_osc.prop.shape == 'square': plugin_obj.params.add("osc", 0.0, 'float')
							if s_osc.prop.shape == 'triangle': plugin_obj.params.add("osc", 1.0, 'float')
							if s_osc.prop.shape == 'noise': plugin_obj.params.add("osc", 2.0, 'float')

							plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
							return True
					else:

						extpluglog.extpluglist.add('FOSS', 'VST2', 'Vital', '')

						exttype = plugins.base.extplug_exists('vital', extplugtype, None)
						if exttype:
							extpluglog.extpluglist.success('Universal', 'Synth-OSC')

							plugin_obj.replace('user', 'matt_tytel', 'vital')
							plugin_obj.params.add('osc_1_on', 1, 'float')
							plugin_obj.params.add('osc_1_level', 1, 'float')
							plugin_obj.params.add('volume', 4000, 'float')

							if env_b_vol[0]:
								plugin_obj.env_asdr_add('vital_env_1', 0, 0, 0, 0, 1, 0, 1)
								plugin_obj.env_points_copy('vol', 'vital_import_lfo_2')
							elif env_p_vol[0]:
								plugin_obj.params.add('osc_1_on', 1, 'float')
								plugin_obj.env_asdr_add('vital_env_1', 0, 0, 0, 0, 1, 0, 1)
								plugin_obj.env_points_copy('vol', 'vital_import_lfo_1')
							elif env_a_vol[0]:
								plugin_obj.env_asdr_copy('vol', 'vital_env_1')
							else:
								plugin_obj.env_asdr_add('vital_env_1', 0, 0, 0, 0, 1, 0, 1)

							plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
							return True