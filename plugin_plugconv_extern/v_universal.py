# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import lxml.etree as ET
from functions_plugin_ext import params_os_socalabs
from functions_plugin_ext import params_os_m8bp
from functions_plugin_ext import params_os_vital
from functions_plugin_ext import params_os_airwindows
from functions_plugin_ext import plugin_vst2
from functions import errorprint
from functions import xtramath
from objects_convproj import wave

def getthree(plugin_obj, env_name):
    env_blocks = plugin_obj.env_blocks_get_exists(env_name)
    env_points = plugin_obj.env_points_get_exists(env_name)
    env_asdr = plugin_obj.env_asdr_get_exists(env_name)
    return env_blocks, env_points, env_asdr

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['universal', None], ['vst2', 'ladspa'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype, plugtransform):

        if plugin_obj.plugin_subtype == 'autotune':
            if 'vst2' in extplugtype:
                if 'nonfree' in dv_config.flags_plugins:
                    if plugin_vst2.check_exists('id', 1735999862):
                        print("[plug-conv] Universal to VST2: AutoTune > GSnap [GVST]:",pluginid)
                        keysdata = []
                        for x in range(12):
                            realkey = (x+9)%12
                            keysdata.append( int(plugin_obj.params.get('key_on_'+str(realkey), 0).value) )
                        speed = plugin_obj.params.get('speed', 1).value
                        calibrate = plugin_obj.params.get('calibrate', 440).value
                        amount = plugin_obj.params.get('amount', 1).value
                        attack = plugin_obj.params.get('attack', 0.001).value
                        release = plugin_obj.params.get('release', 0.001).value

                        plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1735999862, 'param', None, 25)
                        plugin_obj.params.add_named('ext_param_0', 0, 'float', "MinFreq")
                        plugin_obj.params.add_named('ext_param_1', 1, 'float', "MaxFreq")
                        plugin_obj.params.add_named('ext_param_2', 0, 'float', "Gate")
                        plugin_obj.params.add_named('ext_param_3', 1-speed, 'float', "Speed")
                        plugin_obj.params.add_named('ext_param_4', 1, 'float', "CorThrsh")
                        plugin_obj.params.add_named('ext_param_5', amount, 'float', "CorAmt")
                        plugin_obj.params.add_named('ext_param_6', xtramath.between_to_one(0.001, 0.3, attack), 'float', "CorAtk")
                        plugin_obj.params.add_named('ext_param_7', xtramath.between_to_one(0.001, 0.3, release), 'float', "CorRel")
                        plugin_obj.params.add_named('ext_param_8', keysdata[0], 'float', "Note00")
                        plugin_obj.params.add_named('ext_param_9', keysdata[1], 'float', "Note01")
                        plugin_obj.params.add_named('ext_param_10', keysdata[2], 'float', "Note02")
                        plugin_obj.params.add_named('ext_param_11', keysdata[3], 'float', "Note03")
                        plugin_obj.params.add_named('ext_param_12', keysdata[4], 'float', "Note04")
                        plugin_obj.params.add_named('ext_param_13', keysdata[5], 'float', "Note05")
                        plugin_obj.params.add_named('ext_param_14', keysdata[6], 'float', "Note06")
                        plugin_obj.params.add_named('ext_param_15', keysdata[7], 'float', "Note07")
                        plugin_obj.params.add_named('ext_param_16', keysdata[8], 'float', "Note08")
                        plugin_obj.params.add_named('ext_param_17', keysdata[9], 'float', "Note09")
                        plugin_obj.params.add_named('ext_param_18', keysdata[10], 'float', "Note10")
                        plugin_obj.params.add_named('ext_param_19', keysdata[11], 'float', "Note11")
                        plugin_obj.params.add_named('ext_param_20', 0, 'float', "MidiMode")
                        plugin_obj.params.add_named('ext_param_21', 0, 'float', "BendAmt")
                        plugin_obj.params.add_named('ext_param_22', 0, 'float', "VibAmt")
                        plugin_obj.params.add_named('ext_param_23', 0.090909, 'float', "VibSpeed")
                        plugin_obj.params.add_named('ext_param_24', xtramath.between_to_one(430, 450, calibrate), 'float', "Calib")
                        return True
                    else: errorprint.printerr('ext_notfound', ['Nonfree VST2', 'GSnap [GVST]'])

        if plugin_obj.plugin_subtype == 'eq-3band':
            if 'vst2' in extplugtype:
                if plugin_vst2.check_exists('id', 1144210769):
                    print("[plug-conv] Universal to VST2: 3-Band EQ > 3 Band EQ [DISTRHO]:",pluginid)
                    plugtransform.transform('./data_plugts/univ_ext.pltr', '3band_vst2', convproj_obj, plugin_obj, pluginid, dv_config)
                    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1144210769, 'param', None, 6)
                    return True
                else: errorprint.printerr('ext_notfound', ['VST2', '3 Band EQ [DISTRHO]'])

        if plugin_obj.plugin_subtype == 'compressor':
            if 'vst2' in extplugtype:
                if plugin_vst2.check_exists('id', 1397515120):
                    print("[plug-conv] Universal to VST2: Compressor > Compressor [SocaLabs]:",pluginid)
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
                else: errorprint.printerr('ext_notfound', ['VST2', 'Compressor [SocaLabs]'])

        if plugin_obj.plugin_subtype == 'expander': 
            if 'vst2' in extplugtype:
                if plugin_vst2.check_exists('id', 1397515640):
                    print("[plug-conv] Universal to VST2: Expander > Expander [SocaLabs]:",pluginid)
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
                else: errorprint.printerr('ext_notfound', ['VST2', 'Expander [SocaLabs]'])

        if plugin_obj.plugin_subtype == 'limiter':
            if 'vst2' in extplugtype:
                if plugin_vst2.check_exists('id', 1397517421):
                    print("[plug-conv] Universal to VST2: Limiter > Limiter [SocaLabs]:",pluginid)
                    data_socalabs = params_os_socalabs.socalabs_data()
                    data_socalabs.set_param("attack", plugin_obj.params.get('attack', 0).value*1000)
                    data_socalabs.set_param("release", plugin_obj.params.get('release', 0).value*1000)
                    data_socalabs.set_param("threshold", plugin_obj.params.get('threshold', 0).value)
                    data_socalabs.set_param("input", plugin_obj.params.get('pregain', 0).value)
                    data_socalabs.set_param("output", plugin_obj.params.get('postgain', 0).value)
                    data_socalabs.to_cvpj_vst2(convproj_obj, plugin_obj, 1397517421)
                    return True
                else: errorprint.printerr('ext_notfound', ['VST2', 'Limiter [SocaLabs]'])

        if plugin_obj.plugin_subtype == 'gate':
            if 'vst2' in extplugtype:
                if plugin_vst2.check_exists('id', 1397516148):
                    print("[plug-conv] Universal to VST2: Gate > Gate [SocaLabs]:",pluginid)
                    data_socalabs = params_os_socalabs.socalabs_data()
                    data_socalabs.set_param("attack", plugin_obj.params.get('attack', 0).value*1000)
                    data_socalabs.set_param("hold", plugin_obj.params.get('hold', 0).value*1000)
                    data_socalabs.set_param("release", plugin_obj.params.get('release', 0).value*1000)
                    data_socalabs.set_param("threshold", plugin_obj.params.get('threshold', 0).value)
                    data_socalabs.set_param("knee", 0)
                    data_socalabs.set_param("input", plugin_obj.params.get('pregain', 0).value)
                    data_socalabs.set_param("output", plugin_obj.params.get('postgain', 0).value)
                    data_socalabs.to_cvpj_vst2(convproj_obj, plugin_obj, 1397516148)
                    return True
                else: errorprint.printerr('ext_notfound', ['VST2', 'Gate [SocaLabs]'])

        if plugin_obj.plugin_subtype == 'flanger':
            if 'ladspa' in extplugtype:
                print("[plug-conv] Universal to LADSPA: Flanger > Calf Flanger:",pluginid)
                plugtransform.transform('./data_plugts/univ_ext.pltr', 'ladspa_flanger', convproj_obj, plugin_obj, pluginid, dv_config)
                plugin_obj.datavals.add('path', 'veal')
                plugin_obj.datavals.add('plugin', 'Flanger')
                return True

        if plugin_obj.plugin_subtype == 'vibrato':
            if 'vst2' in extplugtype:
                if plugin_vst2.check_exists('id', 1986617970):
                    print("[plug-conv] Universal to VST2: Vibrato > Vibrato [Airwindows]:",pluginid)
                    plugtransform.transform('./data_plugts/univ_ext.pltr', 'vst2_vibrato', convproj_obj, plugin_obj, pluginid, dv_config)
                    airwindows_obj = params_os_airwindows.airwindows_data()
                    airwindows_obj.paramvals = [plugtransform.get_storedval('freq'), plugtransform.get_storedval('depth'), 0, 0, 0]
                    airwindows_obj.paramnames = ["Speed","Depth","FMSpeed","FMDepth","Inv/Wet"]
                    airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1986617970, True, False)
                    return True
                else: errorprint.printerr('ext_notfound', ['VST2', 'Vibrato [Airwindows]'])
            if 'ladspa' in extplugtype:
                print("[plug-conv] Universal to LADSPA: Vibrato > TAP Vibrato:",pluginid)
                plugtransform.transform('./data_plugts/univ_ext.pltr', 'ladspa_vibrato', convproj_obj, plugin_obj, pluginid, dv_config)
                plugin_obj.datavals.add('path', 'tap_vibrato')
                plugin_obj.datavals.add('plugin', 'tap_vibrato')
                return True

        if plugin_obj.plugin_subtype == 'autopan':
            if 'vst2' in extplugtype:
                if plugin_vst2.check_exists('id', 1635087472):
                    print("[plug-conv] Universal to VST2: AutoPan > AutoPan [Airwindows]:",pluginid)
                    plugtransform.transform('./data_plugts/univ_ext.pltr', 'vst2_autopan', convproj_obj, plugin_obj, pluginid, dv_config)
                    airwindows_obj = params_os_airwindows.airwindows_data()
                    airwindows_obj.paramvals = [plugtransform.get_storedval('freq'), 1, 0, plugtransform.get_storedval('depth')]
                    airwindows_obj.paramnames = ["Rate","Phase","Wide","Dry/Wet"]
                    airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1635087472, True, False)
                    return True
                else: errorprint.printerr('ext_notfound', ['VST2', 'AutoPan [Airwindows]'])
            if 'ladspa' in extplugtype:
                print("[plug-conv] Universal to LADSPA: Vibrato > TAP AutoPanner:",pluginid)
                plugtransform.transform('./data_plugts/univ_ext.pltr', 'ladspa_autopan', convproj_obj, plugin_obj, pluginid, dv_config)
                plugin_obj.datavals.add('path', 'tap_autopan')
                plugin_obj.datavals.add('plugin', 'tap_autopan')
                return True

        if plugin_obj.plugin_subtype == 'synth-osc' and 'vst2' in extplugtype:
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
                        if plugin_vst2.check_exists('id', 1937337962):
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
                        else: errorprint.printerr('ext_notfound', ['VST2', 'Magical 8bit Plug 2'])

                    else:
                        if params_os_vital.checksupport(extplugtype):
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

                            params_vital.to_cvpj_any(convproj_obj, extplugtype)
                            return True

                        else: errorprint.printerr('ext_notfound', ['VST', 'Vital'])