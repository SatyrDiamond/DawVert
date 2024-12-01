# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import struct
from functions import extpluglog
from functions import xtramath
from functions_plugin_ext import plugin_vst2
from objects.convproj import wave
import math

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv_ext'

	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'ableton', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']
		
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):

		if plugin_obj.type.subtype == 'Reverb':
			extpluglog.extpluglist.add('FOSS', 'VST2', 'Dragonfly Hall Reverb', '')
			exttype = plugins.base.extplug_exists('dragonfly_hall', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('Ableton', 'Reverb')
				manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)

				manu_obj.from_param('RoomSize', 'RoomSize', 0)
				manu_obj.from_param('PreDelay', 'PreDelay', 0)
				manu_obj.from_param('DecayTime', 'DecayTime', 0)
				manu_obj.from_param('DiffuseDelay', 'DiffuseDelay', 0)
				manu_obj.from_param('StereoSeparation', 'StereoSeparation', 0)
				manu_obj.from_param('EarlyReflectModFreq', 'EarlyReflectModFreq', 0)
				manu_obj.from_param('EarlyReflectModDepth', 'EarlyReflectModDepth', 0)
				manu_obj.from_param('ShelfLoFreq', 'ShelfLoFreq', 0)
				manu_obj.from_param('ShelfLoGain', 'ShelfLoGain', 0)
				manu_obj.from_param('ShelfHiFreq', 'ShelfHiFreq', 0)
				manu_obj.from_param('ShelfHiGain', 'ShelfHiGain', 0)

				p_SpinOn = plugin_obj.params.get("SpinOn", 0).value
				p_ShelfLowOn = plugin_obj.params.get("ShelfLowOn", False).value
				p_ShelfHighOn = plugin_obj.params.get("ShelfHighOn", False).value

				manu_obj.from_param('MixDirect', 'MixDirect', 1)
				manu_obj.calc('RoomSize', 'div', 100, 0, 0, 0)
				manu_obj.calc_clamp('RoomSize', 10, 60)
				manu_obj.calc('DecayTime', 'div', 1000, 0, 0, 0)
				manu_obj.calc('DiffuseDelay', 'mul', 100, 0, 0, 0)
				manu_obj.from_param('EarlyReflectModFreq', 'EarlyReflectModFreq', 0)
				manu_obj.from_param('EarlyReflectModDepth', 'EarlyReflectModDepth', 0)

				plugin_obj.replace('user', 'michaelwillis', 'dragonfly_hall')

				manu_obj.to_param('RoomSize', 'size', None)
				manu_obj.to_param('PreDelay', 'delay', None)
				manu_obj.to_param('DecayTime', 'decay', None)
				manu_obj.to_param('DiffuseDelay', 'diffuse', None)
				manu_obj.to_param('StereoSeparation', 'width', None)

				if p_SpinOn:
					manu_obj.to_param('EarlyReflectModFreq', 'spin', None)
					manu_obj.to_param('EarlyReflectModDepth', 'modulation', None)

				if p_ShelfLowOn:
					manu_obj.to_param('ShelfLoFreq', 'low_cut', None)
					manu_obj.to_param('ShelfLoFreq', 'low_xo', None)
					manu_obj.to_param('ShelfLoGain', 'low_mult', None)

				if p_ShelfHighOn:
					manu_obj.to_param('ShelfHiFreq', 'high_cut', None)
					manu_obj.to_param('ShelfHiFreq', 'high_xo', None)
					manu_obj.to_param('ShelfHiGain', 'high_mult', None)

				manu_obj.to_wet('MixDirect')
				manu_obj.to_value(0, 'dry_level', None, 'float')
				manu_obj.to_value(0, 'early_level', None, 'float')
				manu_obj.to_value(0, 'early_send', None, 'float')
				manu_obj.to_value(15, 'late_level', None, 'float')

				plugin_obj.user_to_external(convproj_obj, pluginid, 'vst2', 'any')
				return True

		if plugin_obj.type.subtype == 'Amp':
			p_AmpType = plugin_obj.params.get("AmpType", 0).value

			p_DryWet = plugin_obj.params.get("DryWet", 1).value

			if p_AmpType == 0:
				extpluglog.extpluglist.add('FOSS', 'VST2', 'BassAmp', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'BassAmp')
				if exttype:
					extpluglog.extpluglist.success('Ableton', 'Amp')
					plugin_obj.replace('user', 'airwindows', 'BassAmp')
					plugin_obj.params.add('high', 0.7, 'float')
					plugin_obj.params.add('dry', 0, 'float')
					plugin_obj.params.add('dub', 0, 'float')
					plugin_obj.params.add('sub', 0, 'float')
					plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
					plugin_obj.fxdata_add(None, p_DryWet)
					return True

			if p_AmpType == 1:
				extpluglog.extpluglist.add('FOSS', 'VST2', 'BassAmp', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'BassAmp')
				if exttype:
					extpluglog.extpluglist.success('Ableton', 'Amp')
					plugin_obj.replace('user', 'airwindows', 'BassAmp')
					plugin_obj.params.add('high', 0.7, 'float')
					plugin_obj.params.add('dry', 0, 'float')
					plugin_obj.params.add('dub', 1, 'float')
					plugin_obj.params.add('sub', 1, 'float')
					plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
					plugin_obj.fxdata_add(None, p_DryWet)
					return True

			if p_AmpType == 2:
				extpluglog.extpluglist.add('FOSS', 'VST2', 'BassAmp', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'BassAmp')
				if exttype:
					extpluglog.extpluglist.success('Ableton', 'Amp')
					plugin_obj.replace('user', 'airwindows', 'BassAmp')
					plugin_obj.params.add('high', 0.7, 'float')
					plugin_obj.params.add('dry', 0, 'float')
					plugin_obj.params.add('dub', 0.5, 'float')
					plugin_obj.params.add('sub', 0.5, 'float')
					plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
					plugin_obj.fxdata_add(None, p_DryWet)
					return True

			if p_AmpType == 3:
				extpluglog.extpluglist.add('FOSS', 'VST2', 'BassAmp', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'BassAmp')
				if exttype:
					extpluglog.extpluglist.success('Ableton', 'Amp')
					plugin_obj.replace('user', 'airwindows', 'BassAmp')
					plugin_obj.params.add('high', 0.7, 'float')
					plugin_obj.params.add('dry', 1, 'float')
					plugin_obj.params.add('dub', 0.5, 'float')
					plugin_obj.params.add('sub', 0.5, 'float')
					plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
					plugin_obj.fxdata_add(None, p_DryWet)
					return True

			if p_AmpType in [4,5]:
				extpluglog.extpluglist.add('FOSS', 'VST2', 'MidAmp', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'MidAmp')
				if exttype:
					extpluglog.extpluglist.success('Ableton', 'Amp')
					plugin_obj.replace('user', 'airwindows', 'MidAmp')
					plugin_obj.params.add('gain', 0.8, 'float')
					plugin_obj.params.add('tone', 1, 'float')
					plugin_obj.params.add('output', 0.8, 'float')
					plugin_obj.params.add('dry_wet', 1, 'float')
					plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
					plugin_obj.fxdata_add(None, p_DryWet)
					return True

			if p_AmpType == 6:
				extpluglog.extpluglist.add('FOSS', 'VST2', 'BassAmp', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'BassAmp')
				if exttype:
					extpluglog.extpluglist.success('Ableton', 'Amp')
					plugin_obj.replace('user', 'airwindows', 'BassAmp')
					plugin_obj.params.add('high', 0.5, 'float')
					plugin_obj.params.add('dry', 0, 'float')
					plugin_obj.params.add('dub', 0.5, 'float')
					plugin_obj.params.add('sub', 0.5, 'float')
					plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
					plugin_obj.fxdata_add(None, p_DryWet)
					return True

		if plugin_obj.type.subtype == 'DrumBuss':
			extpluglog.extpluglist.add('FOSS', 'VST2', 'DrumSlam', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'DrumSlam')
			if exttype:
				extpluglog.extpluglist.success('Ableton', 'Drum Buss')
				p_DriveAmount = plugin_obj.params.get("DriveAmount", 0).value
				p_DryWet = plugin_obj.params.get("DryWet", 1).value
				plugin_obj.replace('user', 'airwindows', 'DrumSlam')
				plugin_obj.params.add('drive', p_DriveAmount/2, 'float')
				plugin_obj.params.add('output', 1, 'float')
				plugin_obj.params.add('dry_wet', 1, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				plugin_obj.fxdata_add(None, p_DryWet)
				return True

		if plugin_obj.type.subtype == 'Tube':
			extpluglog.extpluglist.add('FOSS', 'VST2', 'Tube2', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Tube2')
			if exttype:
				extpluglog.extpluglist.success('Ableton', 'Tube')
				PreDrive = plugin_obj.params.get("PreDrive", 0).value/3
				AutoBias = plugin_obj.params.get("AutoBias", 0).value
				p_DryWet = plugin_obj.params.get("DryWet", 1).value

				plugin_obj.replace('user', 'airwindows', 'Tube2')
				plugin_obj.params.add('input', xtramath.from_db(PreDrive)/2, 'float')
				plugin_obj.params.add('tube', xtramath.between_to_one(-3, 3, AutoBias), 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				plugin_obj.fxdata_add(None, p_DryWet)
				return True

		if plugin_obj.type.subtype == 'Overdrive':
			extpluglog.extpluglist.add('FOSS', 'VST2', 'Drive', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Drive')
			if exttype:
				extpluglog.extpluglist.success('Ableton', 'Overdrive')
				p_Drive = plugin_obj.params.get("Drive", 0).value
				p_Tone = plugin_obj.params.get("Tone", 0).value

				p_DryWet = plugin_obj.params.get("DryWet", 1).value
				plugin_obj.fxdata_add(None, p_DryWet)

				plugin_obj.replace('user', 'airwindows', 'Drive')
				plugin_obj.params.add('drive', p_Drive/200, 'float')
				plugin_obj.params.add('highpass', 0.1+(p_Tone/300), 'float')
				plugin_obj.params.add('out_level', 1, 'float')
				plugin_obj.params.add('dry_wet', 0.2, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				plugin_obj.fxdata_add(None, p_DryWet)
				return True

		#if plugin_obj.type.subtype == 'InstrumentVector':
		#	if params_os_vital.checksupport(extplugtype):
		#		#plugin_obj.params.debugtxt()
		#		params_vital = params_os_vital.vital_data(plugin_obj)
#
		#		params_vital.setvalue('env_1_sustain', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Sustain', 0).value)
		#		params_vital.setvalue_timed('env_1_attack', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Times_Attack', 0).value)
		#		params_vital.setvalue_timed('env_1_decay', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Times_Decay', 0).value)
		#		params_vital.setvalue_timed('env_1_release', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Times_Release', 0).value)
		#		params_vital.setvalue('env_1_attack_power', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Slopes_Attack', 0).value*-4)
		#		params_vital.setvalue('env_1_decay_power', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Slopes_Decay', 0).value*-4)
		#		params_vital.setvalue('env_1_release_power', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Slopes_Release', 0).value*-4)
#
		#		params_vital.setvalue('env_2_sustain', plugin_obj.params.get('Voice_Modulators_Envelope2_Values_Sustain', 0).value)
		#		params_vital.setvalue_timed('env_2_attack', plugin_obj.params.get('Voice_Modulators_Envelope2_Times_Attack', 0).value)
		#		params_vital.setvalue_timed('env_2_decay', plugin_obj.params.get('Voice_Modulators_Envelope2_Times_Decay', 0).value)
		#		params_vital.setvalue_timed('env_2_release', plugin_obj.params.get('Voice_Modulators_Envelope2_Times_Release', 0).value)
		#		params_vital.setvalue('env_2_attack_power', plugin_obj.params.get('Voice_Modulators_Envelope2_Slopes_Attack', 0).value*-4)
		#		params_vital.setvalue('env_2_decay_power', plugin_obj.params.get('Voice_Modulators_Envelope2_Slopes_Decay', 0).value*-4)
		#		params_vital.setvalue('env_2_release_power', plugin_obj.params.get('Voice_Modulators_Envelope2_Slopes_Release', 0).value*-4)
#
		#		params_vital.setvalue('env_3_sustain', plugin_obj.params.get('Voice_Modulators_Envelope3_Values_Sustain', 0).value)
		#		params_vital.setvalue_timed('env_3_attack', plugin_obj.params.get('Voice_Modulators_Envelope3_Times_Attack', 0).value)
		#		params_vital.setvalue_timed('env_3_decay', plugin_obj.params.get('Voice_Modulators_Envelope3_Times_Decay', 0).value)
		#		params_vital.setvalue_timed('env_3_release', plugin_obj.params.get('Voice_Modulators_Envelope3_Times_Release', 0).value)
		#		params_vital.setvalue('env_3_attack_power', plugin_obj.params.get('Voice_Modulators_Envelope3_Slopes_Attack', 0).value*-4)
		#		params_vital.setvalue('env_3_decay_power', plugin_obj.params.get('Voice_Modulators_Envelope3_Slopes_Decay', 0).value*-4)
		#		params_vital.setvalue('env_3_release_power', plugin_obj.params.get('Voice_Modulators_Envelope3_Slopes_Release', 0).value*-4)
#
		#		voice_unison_amount = plugin_obj.params.get('Voice_Unison_Amount', 0).value
		#		voice_unison_voicecount = plugin_obj.datavals.get('Voice_Unison_VoiceCount', 1)
#
		#		isswapped = [False, False]
#
		#		for voicenum in range(1,3):
		#			als_starttxt = 'Voice_Oscillator'+str(voicenum)
#
		#			voice_effects_mode = plugin_obj.datavals.get(als_starttxt+'_Effects_EffectMode', 0)
		#			voice_effects_fx1 = plugin_obj.params.get(als_starttxt+'_Effects_Effect1', 0).value
		#			voice_effects_fx2 = plugin_obj.params.get(als_starttxt+'_Effects_Effect2', 0).value
		#			voice_gain = plugin_obj.params.get(als_starttxt+'_Gain', 0).value
		#			voice_on = plugin_obj.params.get(als_starttxt+'_On', 0).value
		#			voice_pan = plugin_obj.params.get(als_starttxt+'_Pan', 0).value
		#			voice_pitch_detune = plugin_obj.params.get(als_starttxt+'_Pitch_Detune', 0).value
		#			voice_pitch_transpose = plugin_obj.params.get(als_starttxt+'_Pitch_Transpose', 0).value
		#			voice_wavepos = plugin_obj.params.get(als_starttxt+'_Wavetables_WavePosition', 0).value
#
		#			vital_starttxt = 'osc_'+str(voicenum)
	#
		#			params_vital.setvalue(vital_starttxt+'_level', voice_gain/2)
		#			params_vital.setvalue(vital_starttxt+'_pan', voice_pan)
		#			params_vital.setvalue(vital_starttxt+'_on', int(voice_on))
		#			params_vital.setvalue(vital_starttxt+'_transpose', voice_pitch_transpose)
		#			params_vital.setvalue(vital_starttxt+'_tune', voice_pitch_detune)
		#			params_vital.setvalue(vital_starttxt+'_wave_frame', int(voice_wavepos*256))
#
		#			if voice_effects_mode == 2:
		#				isswapped[voicenum-1] = True
		#				params_vital.setvalue(vital_starttxt+'_distortion_amount', 0.5+(voice_effects_fx2/2)/2)
		#				params_vital.setvalue(vital_starttxt+'_distortion_type', 1)
		#			if voice_effects_mode == 3:
		#				params_vital.setvalue(vital_starttxt+'_distortion_amount', 0.5+(voice_effects_fx1)/2)
		#				params_vital.setvalue(vital_starttxt+'_distortion_type', 4)
		#				params_vital.setvalue(vital_starttxt+'_spectral_morph_amount', 0.5+(voice_effects_fx2)/2)
		#				params_vital.setvalue(vital_starttxt+'_spectral_morph_type', 3)
#
		#			params_vital.setvalue(vital_starttxt+'_unison_detune', voice_unison_amount*3)
		#			params_vital.setvalue(vital_starttxt+'_unison_voices', voice_unison_voicecount)
#
		#			ref_found, sampleref_obj = plugin_obj.sampleref_fileref('sample'+str(voicenum), convproj_obj)
		#			if ref_found: params_vital.wavefromfile(voicenum-1, sampleref_obj, 1024)
#
		#		sub_gain = plugin_obj.params.get('Voice_SubOscillator_Gain', 0).value
		#		sub_on = plugin_obj.params.get('Voice_SubOscillator_On', 0).value
		#		sub_tone = plugin_obj.params.get('Voice_SubOscillator_Tone', 0).value
		#		sub_transpose = plugin_obj.params.get('Voice_SubOscillator_Transpose', 0).value
#
		#		params_vital.setvalue('osc_3_level', sub_gain)
		#		params_vital.setvalue('osc_3_on', sub_on)
		#		params_vital.setvalue('osc_3_transpose', (-sub_transpose)*12)
#
		#		wave_obj = wave.cvpj_wave()
		#		wave_obj.set_numpoints(2048)
		#		wave_obj.add_wave('sine', 0, 1, 1)
		#		newpoints = []
		#		for num in range(len(wave_obj.points)):
		#			num = int(((num/2048)**(1+sub_tone))*2048)
		#			val = wave_obj.points[num]
		#			ispos = 1 if val>0 else -1
		#			outval = (abs(val)**(0.1+((1-sub_tone)*0.9)))*ispos
		#			newpoints.append(outval)
		#		wave_obj.points = newpoints
#
		#		params_vital.replacewave(2, wave_obj.get_wave(2048))
#
		#		for filtnum in range(1,3):
		#			als_paramstart = 'Voice_Filter'+str(filtnum)+'_'
		#			filt_circuitbpnomo = plugin_obj.params.get(als_paramstart+'CircuitBpNoMo', 0).value
		#			filt_circuitlphp = plugin_obj.params.get(als_paramstart+'CircuitLpHp', 0).value
		#			filt_drive = plugin_obj.params.get(als_paramstart+'Drive', 0).value
		#			filt_frequency = plugin_obj.params.get(als_paramstart+'Frequency', 0).value
		#			filt_morph = plugin_obj.params.get(als_paramstart+'Morph', 0).value
		#			filt_on = plugin_obj.params.get(als_paramstart+'On', 0).value
		#			filt_resonance = plugin_obj.params.get(als_paramstart+'Resonance', 0).value
		#			filt_slope = plugin_obj.params.get(als_paramstart+'Slope', 0).value
		#			filt_type = plugin_obj.params.get(als_paramstart+'Type', 0).value
#
		#			vital_starttxt = 'filter_'+str(filtnum)
	#
		#			freq = (filt_frequency/20480)**0.1
		#			params_vital.setvalue(vital_starttxt+'_on', int(filt_on))
		#			params_vital.setvalue(vital_starttxt+'_cutoff', freq*136)
		#			params_vital.setvalue(vital_starttxt+'_resonance', filt_resonance/1.4)
		#			if filt_type == 0: params_vital.setvalue(vital_starttxt+'_blend', 0)
		#			if filt_type == 1: params_vital.setvalue(vital_starttxt+'_blend', 2)
		#			if filt_type == 2: params_vital.setvalue(vital_starttxt+'_blend', 1)
		#			if filt_type == 3: 
		#				params_vital.setvalue(vital_starttxt+'_blend', 1)
		#				params_vital.setvalue(vital_starttxt+'_style', 2)
		#			if filt_type == 4: 
		#				if filt_morph < 0.5:
		#					params_vital.setvalue(vital_starttxt+'_blend', filt_morph*4)
		#				else:
		#					params_vital.setvalue(vital_starttxt+'_style', 2)
		#					params_vital.setvalue(vital_starttxt+'_blend', 2-((filt_morph-0.5)*4))
#
		#		for lfonum in range(1,3):
		#			lfo_retrigger = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Retrigger', 0).value
		#			lfo_shape_amount = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Shape_Amount', 0).value
		#			lfo_shape_phaseoffset = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Shape_PhaseOffset', 0).value
		#			lfo_shape_shaping = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Shape_Shaping', 0).value
		#			lfo_shape_type = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Shape_Type', 0).value
		#			lfo_time_attacktime = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Time_AttackTime', 0).value
		#			lfo_time_rate = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Time_Rate', 0).value
		#			lfo_time_sync = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Time_Sync', 0).value
		#			lfo_time_syncedrate = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Time_SyncedRate', 0).value
#
		#			vital_starttxt = 'lfo_'+str(lfonum)
#
		#			if lfo_shape_type == 0:
		#				params_vital.set_lfo(lfonum, 3, [0.0,1.0,0.5,0.0,1.0,1.0], [0.0,0.0,0.0], True, 'Sine')
		#			if lfo_shape_type == 1:
		#				params_vital.set_lfo(lfonum, 3, [0.0,1.0,0.5,0.0,1.0,1.0], [0.0,0.0,0.0], False, 'Triangle')
		#			if lfo_shape_type == 2:
		#				params_vital.set_lfo(lfonum, 2, [0.0,1.0,1.0,0.0], [0.0,0.0], False, 'Saw')
		#			if lfo_shape_type == 3:
		#				params_vital.set_lfo(lfonum, 5, [0.0,1.0,0.0,0.0,0.5,0.0,0.5,1.0,1.0,1.0], [0.0,0.0,0.0,0.0,0.0], False, 'Square')
#
		#			if lfo_time_sync == 0:
		#				params_vital.setvalue(vital_starttxt+'_sync', 0)
		#				params_vital.setvalue(vital_starttxt+'_frequency', -math.log2(1/lfo_time_rate))
		#			else:
		#				params_vital.setvalue(vital_starttxt+'_sync', 1)
		#				tempo = 0
		#				if lfo_time_syncedrate == 0: tempo = 3
		#				if lfo_time_syncedrate == 1: tempo = 4
		#				params_vital.setvalue(vital_starttxt+'_tempo', tempo)
#
		#		modcons = plugin_obj.datavals.get('ModulationConnections', None)
#
		#		modnum = 1
#
		#		if modcons:
		#			for modcon in modcons:
		#				mod_target = modcon['target']
		#				mod_name = modcon['name']
		#				mod_amounts = modcon['amounts']
#
		#				modto = None
		#				modtamt = 1
#
		#				if mod_target == 'Voice_Global_PitchModulation': modto, modtamt = ['osc_1_transpose','osc_2_transpose','osc_3_transpose'], 1
		#				if mod_target == 'Voice_Global_AmpModulation': modto, modtamt = ['volume'], 0.5
		#				if mod_target == 'Voice_Filter1_Frequency': modto, modtamt = ['filter_1_cutoff'], -0.5
		#				if mod_target == 'Voice_Filter2_Frequency': modto, modtamt = ['filter_2_cutoff'], -0.5
		#				if mod_target == 'Voice_Filter1_Resonance': modto, modtamt = ['filter_1_resonance'], 0.5
		#				if mod_target == 'Voice_Filter2_Resonance': modto, modtamt = ['filter_2_resonance'], 0.5
#
		#				for oscnum in range(1,3):
		#					oscnum_txt = str(oscnum)
		#					if mod_target == 'Voice_Oscillator'+oscnum_txt+'_Pan':						modto, modtamt = ['osc_'+oscnum_txt+'_pan'], 2
		#					if mod_target == 'Voice_Oscillator'+oscnum_txt+'_Gain':					   modto, modtamt = ['osc_'+oscnum_txt+'_level'], 2
		#					if mod_target == 'Voice_Oscillator'+oscnum_txt+'_Effects_Effect1':			modto, modtamt = (['osc_'+oscnum_txt+'_distortion_amount'] if not isswapped else ['osc_'+oscnum_txt+'_spectral_morph_amount']), 2
		#					if mod_target == 'Voice_Oscillator'+oscnum_txt+'_Pitch_PitchModulation':	  modto, modtamt = ['osc_'+oscnum_txt+'_transpose'], 0.5
		#					if mod_target == 'Voice_Oscillator'+oscnum_txt+'_Effects_Effect2':			modto, modtamt = (['osc_'+oscnum_txt+'_spectral_morph_amount'] if not isswapped else ['osc_'+oscnum_txt+'_distortion_amount']), 2
		#					if mod_target == 'Voice_Oscillator'+oscnum_txt+'_Wavetables_WavePosition':	modto, modtamt = ['osc_'+oscnum_txt+'_wave_frame'], 2
#
		#				for num, mod_amount in enumerate(mod_amounts):
		#					modfrom = None
		#					if mod_amount:
		#						if num == 0: modfrom = 'env_1'
		#						if num == 1: modfrom = 'env_2'
		#						if num == 2: modfrom = 'env_3'
		#						if num == 3: modfrom = 'lfo_1'
		#						if num == 4: modfrom = 'lfo_2'
#
		#						if modfrom and modto:
		#							amountout = mod_amount*modtamt
		#							if 'env' in modfrom: amountout = -amountout
		#							for n in modto:
		#								params_vital.set_modulation(modnum, modfrom, n, amountout, 0, 1, 0, 0)
		#								modnum += 1
#
		#		params_vital.to_cvpj_any(convproj_obj, extplugtype)