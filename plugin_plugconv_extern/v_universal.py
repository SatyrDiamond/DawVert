# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import lxml.etree as ET
from functions_tracks import auto_data
from functions_plugdata import plugin_socalabs
from functions_plugdata import plugin_m8bp
from functions_plugdata import plugin_vital
from functions_plugdata import data_wave

def getthree(cvpj_plugindata, env_name):
    env_blocks = cvpj_plugindata.env_blocks_get(env_name)
    env_points = cvpj_plugindata.env_points_get(env_name)
    env_asdr = cvpj_plugindata.env_points_get(env_name)
    env_asdr_tens = cvpj_plugindata.asdr_env_tension_get(env_name)
    return env_blocks, env_points, env_asdr, env_asdr_tens

def blocks_minmax(env_blocks):
    blk_max = None
    if env_blocks != None:
        if 'max' in env_blocks: blk_max = env_blocks['max']
    return blk_max

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['universal', None], ['vst2'], None
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json, extplugtype):
        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == 'compressor' and extplugtype == 'vst2':
            print('[plug-conv] UniV to VST2: Compressor > Compressor:',pluginid)
            auto_data.del_plugin(cvpj_l, pluginid)

            data_socalabs = plugin_socalabs.socalabs_data(cvpj_plugindata)
            data_socalabs.set_param("attack", cvpj_plugindata.param_get('attack', 0)[0]*1000)
            data_socalabs.set_param("release", cvpj_plugindata.param_get('release', 0)[0]*1000)
            data_socalabs.set_param("ratio", cvpj_plugindata.param_get('ratio', 0)[0])
            data_socalabs.set_param("threshold", cvpj_plugindata.param_get('threshold', 0)[0])
            data_socalabs.set_param("knee", cvpj_plugindata.param_get('knee', 0)[0])
            data_socalabs.set_param("input", cvpj_plugindata.param_get('pregain', 0)[0])
            data_socalabs.set_param("output", cvpj_plugindata.param_get('postgain', 0)[0])
            data_socalabs.to_cvpj_vst2(cvpj_plugindata, 1397515120)
            return True

        if plugintype[1] == 'expander' and extplugtype == 'vst2':
            print('[plug-conv] UniV to VST2: Expander > Expander:',pluginid)
            auto_data.del_plugin(cvpj_l, pluginid)

            data_socalabs = plugin_socalabs.socalabs_data(cvpj_plugindata)
            data_socalabs.set_param("attack", cvpj_plugindata.param_get('attack', 0)[0]*2000)
            data_socalabs.set_param("release", cvpj_plugindata.param_get('release', 0)[0]*2000)
            data_socalabs.set_param("ratio", cvpj_plugindata.param_get('ratio', 0)[0])
            data_socalabs.set_param("threshold", cvpj_plugindata.param_get('threshold', 0)[0])
            data_socalabs.set_param("knee", cvpj_plugindata.param_get('knee', 0)[0])
            data_socalabs.set_param("input", cvpj_plugindata.param_get('pregain', 0)[0])
            data_socalabs.set_param("output", cvpj_plugindata.param_get('postgain', 0)[0])
            data_socalabs.to_cvpj_vst2(cvpj_plugindata, 1397515640)
            return True

        if plugintype[1] == 'synth-osc' and extplugtype == 'vst2':
            if 'osc' in cvpj_plugindata.cvpjdata:
                oscops = cvpj_plugindata.cvpjdata['osc']

                env_pitch = getthree(cvpj_plugindata, 'pitch')
                env_duty = getthree(cvpj_plugindata, 'duty')
                env_vol = getthree(cvpj_plugindata, 'vol')

                m8bp_compat = True
                env_pitch_max = blocks_minmax(env_pitch[0])
                env_duty_max = blocks_minmax(env_duty[0])
                env_vol_max = blocks_minmax(env_vol[0])

                if len(oscops) == 1:

                    s_osc = oscops[0]

                    if env_vol_max != None:
                        if env_vol_max != 15: m8bp_compat = False

                    osc_shape = s_osc['shape'] if 'shape' in s_osc else 'square'
                    pulse_width = s_osc['pulse_width'] if 'pulse_width' in s_osc else 0.5

                    if osc_shape in ['square', 'triangle', 'noise', 'pulse'] and m8bp_compat:
                        retroplug_data = plugin_m8bp.m8bp_data(cvpj_plugindata)

                        a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = cvpj_plugindata.asdr_env_get('vol')
                        retroplug_data.set_param("attack", a_attack)
                        retroplug_data.set_param("decay", a_decay)
                        retroplug_data.set_param("suslevel", a_sustain)
                        retroplug_data.set_param("release", a_release)

                        if osc_shape != 'noise':    
                            if pulse_width <= 0.125: retroplug_data.set_param("duty", 0)
                            elif pulse_width <= 0.25: retroplug_data.set_param("duty", 1)
                            elif pulse_width <= 0.5: retroplug_data.set_param("duty", 2)
                        else:
                            r_type = cvpj_plugindata.dataval_get('type', 0)
                            noise_type = s_osc['noise_type'] if 'noise_type' in s_osc else '1bit_short'
                            if noise_type == '1bit_short': retroplug_data.set_param("duty", 0)
                            if noise_type == '4bit': retroplug_data.set_param("duty", 1)

                        if env_pitch[0]:
                            retroplug_data.set_param("isPitchSequenceEnabled_raw", 1.0)
                            retroplug_data.set_env('pitch', env_pitch[0]['values'])

                        if env_duty[0]:
                            retroplug_data.set_param("isDutySequenceEnabled_raw", 1.0)
                            retroplug_data.set_env('duty', env_duty[0]['values'])

                        if env_vol[0]:
                            retroplug_data.set_param("isVolumeSequenceEnabled_raw", 1.0)
                            retroplug_data.set_env('volume', env_vol[0]['values'])

                        if osc_shape == 'square': retroplug_data.set_param("osc", 0.0)
                        if osc_shape == 'triangle': retroplug_data.set_param("osc", 1.0)
                        if osc_shape == 'noise': retroplug_data.set_param("osc", 2.0)

                        retroplug_data.to_cvpj_vst2()
                        return True

                    else:
                        params_vital = plugin_vital.vital_data(cvpj_plugindata)
                        params_vital.setvalue('osc_1_on', 1)
                        params_vital.setvalue('osc_1_level', 1)
                        params_vital.setvalue('volume', 4000)

                        r_duty = cvpj_plugindata.dataval_get('duty', 0)
                        if osc_shape == 'sine': vital_shape = data_wave.create_wave('sine', 0, None)
                        if osc_shape == 'square': vital_shape = data_wave.create_wave('square', 0, pulse_width)
                        if osc_shape == 'pulse': vital_shape = data_wave.create_wave('square', 0, pulse_width)
                        if osc_shape == 'triangle': vital_shape = data_wave.create_wave('triangle', 0, None)
                        if osc_shape == 'saw': vital_shape = data_wave.create_wave('saw', 0, None)
                        if osc_shape == 'custom_wave': 
                            wave_name = s_osc['wave_name'] if 'wave_name' in s_osc else None
                            vital_shape = data_wave.cvpjwave2wave(cvpj_plugindata, wave_name)

                        params_vital.replacewave(0, vital_shape)

                        if env_vol[1] != None:
                            params_vital.setvalue('osc_1_on', 1)
                            params_vital.setvalue('osc_1_level', 0.5)
                            params_vital.importcvpj_env_points(cvpj_plugindata, 1, 'vol')
                            params_vital.setvalue_timed('env_1_release', 20)
                            params_vital.set_modulation(1, 'lfo_1', 'osc_1_level', 1, 0, 1, 0, 0)
                        else:
                            params_vital.importcvpj_env_asdr(cvpj_plugindata, 1, 'vol')

                        params_vital.to_cvpj_vst2()
                        return True
