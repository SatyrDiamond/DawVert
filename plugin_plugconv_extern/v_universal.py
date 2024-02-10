# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import lxml.etree as ET
from functions_plugin_ext import params_os_socalabs
from functions_plugin_ext import params_os_m8bp
from functions_plugin_ext import params_os_vital
from objects_convproj import wave

def getthree(plugin_obj, env_name):
    env_blocks = plugin_obj.env_blocks_get_exists(env_name)
    env_points = plugin_obj.env_points_get_exists(env_name)
    env_asdr = plugin_obj.env_asdr_get_exists(env_name)
    return env_blocks, env_points, env_asdr

def blocks_minmax(env_blocks):
    blk_max = None
    if env_blocks != None:
        if 'max' in env_blocks: blk_max = env_blocks['max']
    return blk_max

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['universal', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json, extplugtype):

        if plugin_obj.plugin_subtype == 'compressor' and extplugtype == 'vst2':
            print('[plug-conv] UniV to VST2: Compressor > Compressor:',pluginid)
            data_socalabs = params_os_socalabs.socalabs_data()
            data_socalabs.set_param("attack", plugin_obj.params.get('attack', 0).value*1000)
            data_socalabs.set_param("release", plugin_obj.params.get('release', 0).value*1000)
            data_socalabs.set_param("ratio", plugin_obj.params.get('ratio', 0).value)
            data_socalabs.set_param("threshold", plugin_obj.params.get('threshold', 0).value)
            data_socalabs.set_param("knee", plugin_obj.params.get('knee', 0).value)
            data_socalabs.set_param("input", plugin_obj.params.get('pregain', 0).value)
            data_socalabs.set_param("output", plugin_obj.params.get('postgain', 0).value)
            data_socalabs.to_cvpj_vst2(convproj_obj, plugin_obj, 1397515120)
            return True

        if plugin_obj.plugin_subtype == 'expander' and extplugtype == 'vst2':
            print('[plug-conv] UniV to VST2: Expander > Expander:',pluginid)
            data_socalabs = params_os_socalabs.socalabs_data()
            data_socalabs.set_param("attack", plugin_obj.params.get('attack', 0).value*2000)
            data_socalabs.set_param("release", plugin_obj.params.get('release', 0).value*2000)
            data_socalabs.set_param("ratio", plugin_obj.params.get('ratio', 0).value)
            data_socalabs.set_param("threshold", plugin_obj.params.get('threshold', 0).value)
            data_socalabs.set_param("knee", plugin_obj.params.get('knee', 0).value)
            data_socalabs.set_param("input", plugin_obj.params.get('pregain', 0).value)
            data_socalabs.set_param("output", plugin_obj.params.get('postgain', 0).value)
            data_socalabs.to_cvpj_vst2(convproj_obj, plugin_obj, 1397515640)
            return True

        if plugin_obj.plugin_subtype == 'synth-osc' and extplugtype == 'vst2':
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

                    pulse_width = s_osc.params['pulse_width'] if 'pulse_width' in s_osc.params else 0.5

                    if s_osc.shape in ['square', 'triangle', 'noise', 'pulse'] and m8bp_compat:
                        retroplug_data = params_os_m8bp.m8bp_data()

                        if env_a_vol[0]:
                            retroplug_data.set_param("attack", env_a_vol[1].attack)
                            retroplug_data.set_param("decay", env_a_vol[1].decay)
                            retroplug_data.set_param("suslevel", env_a_vol[1].sustain)
                            retroplug_data.set_param("release", env_a_vol[1].release)

                        if s_osc.shape != 'noise':    
                            if pulse_width <= 0.125: retroplug_data.set_param("duty", 0)
                            elif pulse_width <= 0.25: retroplug_data.set_param("duty", 1)
                            elif pulse_width <= 0.5: retroplug_data.set_param("duty", 2)
                        else:
                            noise_type = s_osc.params['noise_type'] if 'noise_type' in s_osc.params else '1bit_short'
                            if noise_type == '1bit_short': retroplug_data.set_param("duty", 0)
                            if noise_type == '4bit': retroplug_data.set_param("duty", 1)

                        if env_b_pitch[0]:
                            retroplug_data.set_param("isPitchSequenceEnabled_raw", 1.0)
                            retroplug_data.set_env('pitch', env_b_pitch[1].values)

                        if env_b_duty[0]:
                            retroplug_data.set_param("isDutySequenceEnabled_raw", 1.0)
                            retroplug_data.set_env('duty', env_b_duty[1].values)

                        if env_b_vol[0]:
                            retroplug_data.set_param("isVolumeSequenceEnabled_raw", 1.0)
                            retroplug_data.set_env('volume', env_b_vol[1].values)

                        if s_osc.shape == 'square': retroplug_data.set_param("osc", 0.0)
                        if s_osc.shape == 'triangle': retroplug_data.set_param("osc", 1.0)
                        if s_osc.shape == 'noise': retroplug_data.set_param("osc", 2.0)

                        retroplug_data.to_cvpj_vst2(convproj_obj, plugin_obj)
                        return True

                    else:
                        params_vital = params_os_vital.vital_data(plugin_obj)
                        params_vital.setvalue('osc_1_on', 1)
                        params_vital.setvalue('osc_1_level', 1)
                        params_vital.setvalue('volume', 4000)

                        wave_obj = wave.cvpj_wave()
                        wave_obj.set_numpoints(2048)

                        if s_osc.shape == 'sine': wave_obj.add_wave('sine', 0, 1, 1)
                        if s_osc.shape == 'square': wave_obj.add_wave('square', 0.5, 1, 1)
                        if s_osc.shape == 'pulse': wave_obj.add_wave('square', 0.5, 1, 1)
                        if s_osc.shape == 'triangle': wave_obj.add_wave('triangle', 0, 1, 1)
                        if s_osc.shape == 'saw': wave_obj.add_wave('saw', 0, 1, 1)
                        if s_osc.shape == 'custom_wave': wave_obj = plugin_obj.wave_get(s_osc.name_id)

                        params_vital.replacewave(0, wave_obj.get_wave(2048))

                        if env_p_vol[0]:
                            params_vital.setvalue('osc_1_on', 1)
                            params_vital.setvalue('osc_1_level', 0.5)
                            params_vital.importcvpj_env_points(1, 'vol')
                            params_vital.setvalue_timed('env_1_release', 20)
                            params_vital.set_modulation(1, 'lfo_1', 'osc_1_level', 1, 0, 1, 0, 0)
                        else:
                            params_vital.importcvpj_env_asdr(1, 'vol')

                        params_vital.to_cvpj_vst2(convproj_obj)
                        return True
