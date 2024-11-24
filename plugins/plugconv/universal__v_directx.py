# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import math
from functions import xtramath
from objects.inst_params import fx_delay
from functions import extpluglog
from objects import globalstore

slope_vals = [12,24,48]

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'directx', None]]
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = [['universal', None, None]]
		in_dict['out_daws'] = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):

		if plugin_obj.type.check_wildmatch('native', 'directx', 'Chorus'):
			extpluglog.convinternal('DirectX', 'Chorus', 'Universal', 'Chorus')
			waveshape = 'sine' if bool(plugin_obj.params.get('waveshape', 0).value) else 'triangle'
			plugin_obj.plugts_transform('./data_main/plugts/directx.pltr', 'chorus_univ', convproj_obj, pluginid)
			plugin_obj.datavals.add('waveshape', waveshape)
			return 1
			
		if plugin_obj.type.check_wildmatch('native', 'directx', 'Compressor'):
			extpluglog.convinternal('DirectX', 'Compressor', 'Universal', 'Compressor')
			plugin_obj.plugts_transform('./data_main/plugts/directx.pltr', 'compressor_univ', convproj_obj, pluginid)
			return 1
			
		if plugin_obj.type.check_wildmatch('native', 'directx', 'Echo'):
			extpluglog.convinternal('DirectX', 'Echo', 'Universal', 'Delay')
			i_feedback = plugin_obj.params.get('feedback', 0).value
			i_leftdelay = plugin_obj.params.get('leftdelay', 0).value
			i_rightdelay = plugin_obj.params.get('rightdelay', 0).value
			i_pandelay = bool(plugin_obj.params.get('pandelay', 0).value)
			i_leftdelay = xtramath.between_from_one(0.001, 2, i_leftdelay)
			i_rightdelay = xtramath.between_from_one(0.001, 2, i_rightdelay)

			delay_obj = fx_delay.fx_delay()
			delay_obj.feedback_first = False
			delay_obj.feedback[0] = i_feedback

			timing_obj = delay_obj.timing_add(0)
			timing_obj.set_seconds(i_leftdelay)
			timing_obj = delay_obj.timing_add(1)
			timing_obj.set_seconds(i_rightdelay)

			if i_pandelay: 
				delay_obj.mode = 'pingpong'
				delay_obj.submode = 'normal'

			plugin_obj = delay_obj.to_cvpj(convproj_obj, pluginid)
			return 1

		if plugin_obj.type.check_wildmatch('native', 'directx', 'Flanger'):
			extpluglog.convinternal('DirectX', 'Flanger', 'Universal', 'Flanger')
			p_frequency = plugin_obj.params.get('frequency', 0).value
			p_depth = plugin_obj.params.get('depth', 0).value
			waveshape = 'sine' if bool(plugin_obj.params.get('waveshape', 0).value) else 'triangle'
			plugin_obj.plugts_transform('./data_main/plugts/directx.pltr', 'flanger_univ', convproj_obj, pluginid)
			plugin_obj.datavals.add('waveshape', waveshape)
			lfo_obj = plugin_obj.lfo_add('flanger')
			lfo_obj.time.set_hz(p_frequency)
			lfo_obj.amount = p_depth
			lfo_obj.prop.shape = waveshape
			return 1

		if plugin_obj.type.check_wildmatch('native', 'directx', 'Gargle'):
			extpluglog.convinternal('DirectX', 'Gargle', 'Universal', 'Ringmod')
			garg_shape = 'square' if bool(plugin_obj.params.get('waveshape', 0).value) else 'triangle'
			garg_rate = plugin_obj.params.get('rate', 0).value
			garg_rate = xtramath.between_from_one(1, 1000, garg_rate)
			plugin_obj.replace('universal', 'ringmod', None)
			plugin_obj.datavals.add('shape', garg_shape)
			plugin_obj.params.add('rate', garg_rate, 'float')
			lfo_obj = plugin_obj.lfo_add('amount')
			lfo_obj.time.set_hz(garg_rate)
			lfo_obj.amount = 1
			lfo_obj.prop.shape = garg_shape
			return 1

		if plugin_obj.type.check_wildmatch('native', 'directx', 'ParamEq'):
			extpluglog.convinternal('DirectX', 'ParamEq', 'Universal', 'Filter')
			eq_bandwidth = plugin_obj.params.get('bandwidth', 0).value
			eq_center = plugin_obj.params.get('center', 0).value
			eq_eqgain = plugin_obj.params.get('eqgain', 0).value
			eq_center = xtramath.between_from_one(80, 16000, eq_center)
			eq_bandwidth = xtramath.between_from_one(1, 36, eq_bandwidth)
			plugin_obj.replace('universal', 'filter', None)
			plugin_obj.filter.on = True
			plugin_obj.filter.type.set('peak', None)
			plugin_obj.filter.freq = eq_center
			plugin_obj.filter.q = eq_bandwidth/36
			return 1

		if plugin_obj.type.check_wildmatch('native', 'directx', 'I3DL2Reverb'):
			extpluglog.convinternal('DirectX', 'I3DL2Reverb', 'Universal', 'Reverb')
			#p_decayhfratio = plugin_obj.params.get("decayhfratio", 0).value
			#p_density = plugin_obj.params.get("density", 0).value
			#p_hfreference = plugin_obj.params.get("hfreference", 0).value
			#p_quality = plugin_obj.params.get("quality", 0).value
			#p_reflections = plugin_obj.params.get("reflections", 0).value
			#p_reflectionsdelay = plugin_obj.params.get("reflectionsdelay", 0).value
			#p_roomhf = plugin_obj.params.get("roomhf", 0).value
			#p_roomrollofffactor = plugin_obj.params.get("roomrollofffactor", 0).value
			p_decaytime = plugin_obj.params.get("decaytime", 0).value
			p_diffusion = plugin_obj.params.get("diffusion", 0).value
			p_reverb = plugin_obj.params.get("reverb", 0).value
			p_reverbdelay = plugin_obj.params.get("reverbdelay", 0).value
			p_room = plugin_obj.params.get("room", 0).value

			plugin_obj.replace('universal', 'reverb', None)
			plugin_obj.params.add('dry', p_room, 'float')
			plugin_obj.params.add('wet', (p_reverb*p_room), 'float')
			plugin_obj.params.add('predelay', p_reverbdelay/100, 'float')
			plugin_obj.params.add('diffusion', p_diffusion, 'float')
			plugin_obj.params.add('decay', p_decaytime*20, 'float')
			return 1

		if plugin_obj.type.check_wildmatch('native', 'directx', 'WavesReverb'):
			extpluglog.convinternal('DirectX', 'WavesReverb', 'Universal', 'Reverb')
			p_ingain = plugin_obj.params.get('ingain', 0).value
			p_reverbmix = plugin_obj.params.get('reverbmix', 0).value
			p_reverbtime = plugin_obj.params.get('reverbtime', 0).value
			reverbvol = p_ingain**4
			reverbwet = p_reverbmix**18
			reverbdry = 1-reverbwet

			plugin_obj.replace('universal', 'reverb', None)
			plugin_obj.params.add('dry', (reverbdry*reverbvol), 'float')
			plugin_obj.params.add('wet', (reverbwet*reverbvol), 'float')
			plugin_obj.params.add('decay', p_reverbtime*3, 'float')
			return 1

		return 2