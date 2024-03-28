# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from objects_convproj import wave
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext_nonfree import params_nf_exakt_lite
from functions_plugin_ext import params_os_vital
from functions import errorprint
import math

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['native-ableton', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype, plugtransform):

        if 'shareware' in dv_config.flags_plugins:
            if plugin_obj.plugin_subtype == 'GlueCompressor':
                vst2_use = 'vst2' in extplugtype and plugin_vst2.check_exists('id', 1132024935)
                if vst2_use:
                    plugtransform.transform('./data_plugts/ableton_vst2.pltr', 'glue', convproj_obj, plugin_obj, pluginid, dv_config)
                    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1132024935, 'param', None, 12)
                    pass
                else: errorprint.printerr('ext_notfound', ['Shareware VST2', 'The Glue'])

        #print(plugin_obj.plugin_subtype)

        if plugin_obj.plugin_subtype == 'InstrumentVector':
            if params_os_vital.checksupport(extplugtype):
                #plugin_obj.params.debugtxt()
                params_vital = params_os_vital.vital_data(plugin_obj)

                params_vital.setvalue('env_1_sustain', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Sustain', 0).value)
                params_vital.setvalue_timed('env_1_attack', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Times_Attack', 0).value)
                params_vital.setvalue_timed('env_1_decay', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Times_Decay', 0).value)
                params_vital.setvalue_timed('env_1_release', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Times_Release', 0).value)
                params_vital.setvalue('env_1_attack_power', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Slopes_Attack', 0).value*-4)
                params_vital.setvalue('env_1_decay_power', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Slopes_Decay', 0).value*-4)
                params_vital.setvalue('env_1_release_power', plugin_obj.params.get('Voice_Modulators_AmpEnvelope_Slopes_Release', 0).value*-4)

                params_vital.setvalue('env_2_sustain', plugin_obj.params.get('Voice_Modulators_Envelope2_Values_Sustain', 0).value)
                params_vital.setvalue_timed('env_2_attack', plugin_obj.params.get('Voice_Modulators_Envelope2_Times_Attack', 0).value)
                params_vital.setvalue_timed('env_2_decay', plugin_obj.params.get('Voice_Modulators_Envelope2_Times_Decay', 0).value)
                params_vital.setvalue_timed('env_2_release', plugin_obj.params.get('Voice_Modulators_Envelope2_Times_Release', 0).value)
                params_vital.setvalue('env_2_attack_power', plugin_obj.params.get('Voice_Modulators_Envelope2_Slopes_Attack', 0).value*-4)
                params_vital.setvalue('env_2_decay_power', plugin_obj.params.get('Voice_Modulators_Envelope2_Slopes_Decay', 0).value*-4)
                params_vital.setvalue('env_2_release_power', plugin_obj.params.get('Voice_Modulators_Envelope2_Slopes_Release', 0).value*-4)

                params_vital.setvalue('env_3_sustain', plugin_obj.params.get('Voice_Modulators_Envelope3_Values_Sustain', 0).value)
                params_vital.setvalue_timed('env_3_attack', plugin_obj.params.get('Voice_Modulators_Envelope3_Times_Attack', 0).value)
                params_vital.setvalue_timed('env_3_decay', plugin_obj.params.get('Voice_Modulators_Envelope3_Times_Decay', 0).value)
                params_vital.setvalue_timed('env_3_release', plugin_obj.params.get('Voice_Modulators_Envelope3_Times_Release', 0).value)
                params_vital.setvalue('env_3_attack_power', plugin_obj.params.get('Voice_Modulators_Envelope3_Slopes_Attack', 0).value*-4)
                params_vital.setvalue('env_3_decay_power', plugin_obj.params.get('Voice_Modulators_Envelope3_Slopes_Decay', 0).value*-4)
                params_vital.setvalue('env_3_release_power', plugin_obj.params.get('Voice_Modulators_Envelope3_Slopes_Release', 0).value*-4)

                voice_unison_amount = plugin_obj.params.get('Voice_Unison_Amount', 0).value
                voice_unison_voicecount = plugin_obj.datavals.get('Voice_Unison_VoiceCount', 1)

                isswapped = [False, False]

                for voicenum in range(1,3):
                    SpriteName = plugin_obj.datavals.get('SpriteName'+str(voicenum), None)
                    SpriteName = plugin_obj.datavals.get('SpriteName'+str(voicenum), None)

                    als_starttxt = 'Voice_Oscillator'+str(voicenum)

                    voice_effects_mode = plugin_obj.datavals.get(als_starttxt+'_Effects_EffectMode', 0)
                    voice_effects_fx1 = plugin_obj.params.get(als_starttxt+'_Effects_Effect1', 0).value
                    voice_effects_fx2 = plugin_obj.params.get(als_starttxt+'_Effects_Effect2', 0).value
                    voice_gain = plugin_obj.params.get(als_starttxt+'_Gain', 0).value
                    voice_on = plugin_obj.params.get(als_starttxt+'_On', 0).value
                    voice_pan = plugin_obj.params.get(als_starttxt+'_Pan', 0).value
                    voice_pitch_detune = plugin_obj.params.get(als_starttxt+'_Pitch_Detune', 0).value
                    voice_pitch_transpose = plugin_obj.params.get(als_starttxt+'_Pitch_Transpose', 0).value
                    voice_wavepos = plugin_obj.params.get(als_starttxt+'_Wavetables_WavePosition', 0).value

                    vital_starttxt = 'osc_'+str(voicenum)
    
                    params_vital.setvalue(vital_starttxt+'_level', voice_gain/2)
                    params_vital.setvalue(vital_starttxt+'_pan', voice_pan)
                    params_vital.setvalue(vital_starttxt+'_on', int(voice_on))
                    params_vital.setvalue(vital_starttxt+'_transpose', voice_pitch_transpose)
                    params_vital.setvalue(vital_starttxt+'_tune', voice_pitch_detune)
                    params_vital.setvalue(vital_starttxt+'_wave_frame', int(voice_wavepos*256))

                    if voice_effects_mode == 2:
                        isswapped[voicenum-1] = True
                        params_vital.setvalue(vital_starttxt+'_distortion_amount', 0.5+(voice_effects_fx2/2)/2)
                        params_vital.setvalue(vital_starttxt+'_distortion_type', 1)
                    if voice_effects_mode == 3:
                        params_vital.setvalue(vital_starttxt+'_distortion_amount', 0.5+(voice_effects_fx1)/2)
                        params_vital.setvalue(vital_starttxt+'_distortion_type', 4)
                        params_vital.setvalue(vital_starttxt+'_spectral_morph_amount', 0.5+(voice_effects_fx2)/2)
                        params_vital.setvalue(vital_starttxt+'_spectral_morph_type', 3)

                    params_vital.setvalue(vital_starttxt+'_unison_detune', voice_unison_amount*3)
                    params_vital.setvalue(vital_starttxt+'_unison_voices', voice_unison_voicecount)

                    ref_found, sampleref_obj = plugin_obj.sampleref_fileref('sample'+str(voicenum), convproj_obj)
                    if ref_found: params_vital.wavefromfile(voicenum-1, sampleref_obj, 1024)

                sub_gain = plugin_obj.params.get('Voice_SubOscillator_Gain', 0).value
                sub_on = plugin_obj.params.get('Voice_SubOscillator_On', 0).value
                sub_tone = plugin_obj.params.get('Voice_SubOscillator_Tone', 0).value
                sub_transpose = plugin_obj.params.get('Voice_SubOscillator_Transpose', 0).value

                params_vital.setvalue('osc_3_level', sub_gain)
                params_vital.setvalue('osc_3_on', sub_on)
                params_vital.setvalue('osc_3_transpose', (-sub_transpose)*12)

                wave_obj = wave.cvpj_wave()
                wave_obj.set_numpoints(2048)
                wave_obj.add_wave('sine', 0, 1, 1)
                newpoints = []
                for num in range(len(wave_obj.points)):
                    num = int(((num/2048)**(1+sub_tone))*2048)
                    val = wave_obj.points[num]
                    ispos = 1 if val>0 else -1
                    outval = (abs(val)**(0.1+((1-sub_tone)*0.9)))*ispos
                    newpoints.append(outval)
                wave_obj.points = newpoints

                params_vital.replacewave(2, wave_obj.get_wave(2048))

                for filtnum in range(1,3):
                    als_paramstart = 'Voice_Filter'+str(filtnum)+'_'
                    filt_circuitbpnomo = plugin_obj.params.get(als_paramstart+'CircuitBpNoMo', 0).value
                    filt_circuitlphp = plugin_obj.params.get(als_paramstart+'CircuitLpHp', 0).value
                    filt_drive = plugin_obj.params.get(als_paramstart+'Drive', 0).value
                    filt_frequency = plugin_obj.params.get(als_paramstart+'Frequency', 0).value
                    filt_morph = plugin_obj.params.get(als_paramstart+'Morph', 0).value
                    filt_on = plugin_obj.params.get(als_paramstart+'On', 0).value
                    filt_resonance = plugin_obj.params.get(als_paramstart+'Resonance', 0).value
                    filt_slope = plugin_obj.params.get(als_paramstart+'Slope', 0).value
                    filt_type = plugin_obj.params.get(als_paramstart+'Type', 0).value

                    vital_starttxt = 'filter_'+str(filtnum)
    
                    freq = (filt_frequency/20480)**0.1
                    params_vital.setvalue(vital_starttxt+'_on', int(filt_on))
                    params_vital.setvalue(vital_starttxt+'_cutoff', freq*136)
                    params_vital.setvalue(vital_starttxt+'_resonance', filt_resonance/1.4)
                    if filt_type == 0: params_vital.setvalue(vital_starttxt+'_blend', 0)
                    if filt_type == 1: params_vital.setvalue(vital_starttxt+'_blend', 2)
                    if filt_type == 2: params_vital.setvalue(vital_starttxt+'_blend', 1)
                    if filt_type == 3: 
                        params_vital.setvalue(vital_starttxt+'_blend', 1)
                        params_vital.setvalue(vital_starttxt+'_style', 2)
                    if filt_type == 4: 
                        if filt_morph < 0.5:
                            params_vital.setvalue(vital_starttxt+'_blend', filt_morph*4)
                        else:
                            params_vital.setvalue(vital_starttxt+'_style', 2)
                            params_vital.setvalue(vital_starttxt+'_blend', 2-((filt_morph-0.5)*4))

                for lfonum in range(1,3):
                    lfo_retrigger = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Retrigger', 0).value
                    lfo_shape_amount = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Shape_Amount', 0).value
                    lfo_shape_phaseoffset = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Shape_PhaseOffset', 0).value
                    lfo_shape_shaping = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Shape_Shaping', 0).value
                    lfo_shape_type = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Shape_Type', 0).value
                    lfo_time_attacktime = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Time_AttackTime', 0).value
                    lfo_time_rate = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Time_Rate', 0).value
                    lfo_time_sync = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Time_Sync', 0).value
                    lfo_time_syncedrate = plugin_obj.params.get('Voice_Modulators_Lfo'+str(lfonum)+'_Time_SyncedRate', 0).value

                    vital_starttxt = 'lfo_'+str(lfonum)

                    if lfo_shape_type == 0:
                        params_vital.set_lfo(lfonum, 3, [0.0,1.0,0.5,0.0,1.0,1.0], [0.0,0.0,0.0], True, 'Sine')
                    if lfo_shape_type == 1:
                        params_vital.set_lfo(lfonum, 3, [0.0,1.0,0.5,0.0,1.0,1.0], [0.0,0.0,0.0], False, 'Triangle')
                    if lfo_shape_type == 2:
                        params_vital.set_lfo(lfonum, 2, [0.0,1.0,1.0,0.0], [0.0,0.0], False, 'Saw')
                    if lfo_shape_type == 3:
                        params_vital.set_lfo(lfonum, 5, [0.0,1.0,0.0,0.0,0.5,0.0,0.5,1.0,1.0,1.0], [0.0,0.0,0.0,0.0,0.0], False, 'Square')

                    if lfo_time_sync == 0:
                        params_vital.setvalue(vital_starttxt+'_sync', 0)
                        params_vital.setvalue(vital_starttxt+'_frequency', -math.log2(1/lfo_time_rate))
                    else:
                        params_vital.setvalue(vital_starttxt+'_sync', 1)
                        tempo = 0
                        if lfo_time_syncedrate == 0: tempo = 3
                        if lfo_time_syncedrate == 1: tempo = 4
                        params_vital.setvalue(vital_starttxt+'_tempo', tempo)

                modcons = plugin_obj.datavals.get('ModulationConnections', None)

                modnum = 1

                if modcons:
                    for modcon in modcons:
                        mod_target = modcon['target']
                        mod_name = modcon['name']
                        mod_amounts = modcon['amounts']

                        modto = None
                        modtamt = 1

                        if mod_target == 'Voice_Global_PitchModulation': modto, modtamt = ['osc_1_transpose','osc_2_transpose','osc_3_transpose'], 1
                        if mod_target == 'Voice_Global_AmpModulation': modto, modtamt = ['volume'], 0.5
                        if mod_target == 'Voice_Filter1_Frequency': modto, modtamt = ['filter_1_cutoff'], -0.5
                        if mod_target == 'Voice_Filter2_Frequency': modto, modtamt = ['filter_2_cutoff'], -0.5
                        if mod_target == 'Voice_Filter1_Resonance': modto, modtamt = ['filter_1_resonance'], 0.5
                        if mod_target == 'Voice_Filter2_Resonance': modto, modtamt = ['filter_2_resonance'], 0.5

                        for oscnum in range(1,3):
                            oscnum_txt = str(oscnum)
                            if mod_target == 'Voice_Oscillator'+oscnum_txt+'_Pan':                        modto, modtamt = ['osc_'+oscnum_txt+'_pan'], 2
                            if mod_target == 'Voice_Oscillator'+oscnum_txt+'_Gain':                       modto, modtamt = ['osc_'+oscnum_txt+'_level'], 2
                            if mod_target == 'Voice_Oscillator'+oscnum_txt+'_Effects_Effect1':            modto, modtamt = (['osc_'+oscnum_txt+'_distortion_amount'] if not isswapped else ['osc_'+oscnum_txt+'_spectral_morph_amount']), 2
                            if mod_target == 'Voice_Oscillator'+oscnum_txt+'_Pitch_PitchModulation':      modto, modtamt = ['osc_'+oscnum_txt+'_transpose'], 0.5
                            if mod_target == 'Voice_Oscillator'+oscnum_txt+'_Effects_Effect2':            modto, modtamt = (['osc_'+oscnum_txt+'_spectral_morph_amount'] if not isswapped else ['osc_'+oscnum_txt+'_distortion_amount']), 2
                            if mod_target == 'Voice_Oscillator'+oscnum_txt+'_Wavetables_WavePosition':    modto, modtamt = ['osc_'+oscnum_txt+'_wave_frame'], 2

                        for num, mod_amount in enumerate(mod_amounts):
                            modfrom = None
                            if mod_amount:
                                if num == 0: modfrom = 'env_1'
                                if num == 1: modfrom = 'env_2'
                                if num == 2: modfrom = 'env_3'
                                if num == 3: modfrom = 'lfo_1'
                                if num == 4: modfrom = 'lfo_2'

                                if modfrom and modto:
                                    amountout = mod_amount*modtamt
                                    if 'env' in modfrom: amountout = -amountout
                                    for n in modto:
                                        params_vital.set_modulation(modnum, modfrom, n, amountout, 0, 1, 0, 0)
                                        modnum += 1

                params_vital.to_cvpj_any(convproj_obj, extplugtype)