# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import audio_wav
from functions import plugin_vst2
from functions import plugins

from functions_plugdata import plugin_m8bp
from functions_plugdata import plugin_vital

from functions_plugdata import data_wave

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['retro', None, None], ['vst2', None, None], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()
        
        blk_env_pitch = cvpj_plugindata.env_blocks_get('pitch')
        blk_env_duty = cvpj_plugindata.env_blocks_get('duty')
        blk_env_vol = cvpj_plugindata.env_blocks_get('vol')

        m8bp_out = True
        if blk_env_vol != None:
            if blk_env_vol['max'] != 15: m8bp_out = False

        if plugintype[1] in ['square', 'triangle', 'noise', 'pulse'] and m8bp_out == True:
            retroplug_data = plugin_m8bp.m8bp_data(cvpj_plugindata)

            a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = cvpj_plugindata.asdr_env_get('vol')
            retroplug_data.set_param("attack", a_attack)
            retroplug_data.set_param("decay", a_decay)
            retroplug_data.set_param("suslevel", a_sustain)
            retroplug_data.set_param("release", a_release)

            if plugintype[1] != 'noise':    
                r_duty = cvpj_plugindata.dataval_get('duty', 0)
                if r_duty == 0: retroplug_data.set_param("duty", 2)
                if r_duty == 1: retroplug_data.set_param("duty", 1)
                if r_duty == 2: retroplug_data.set_param("duty", 0)
            else:
                r_type = cvpj_plugindata.dataval_get('type', 0)
                if r_type == '1bit_short': retroplug_data.set_param("duty", 0)
                if r_type == '4bit': retroplug_data.set_param("duty", 1)

            if blk_env_pitch:
                retroplug_data.set_param("isPitchSequenceEnabled_raw", 1.0)
                retroplug_data.set_env('pitch', blk_env_pitch['values'])

            if blk_env_duty:
                retroplug_data.set_param("isDutySequenceEnabled_raw", 1.0)
                retroplug_data.set_env('duty', blk_env_duty['values'])

            if blk_env_vol:
                retroplug_data.set_param("isVolumeSequenceEnabled_raw", 1.0)
                retroplug_data.set_env('volume', blk_env_vol['values'])

            if plugintype[1] == 'square': retroplug_data.set_param("osc", 0.0)
            if plugintype[1] == 'triangle': retroplug_data.set_param("osc", 1.0)
            if plugintype[1] == 'noise': retroplug_data.set_param("osc", 2.0)

            retroplug_data.to_cvpj_vst2()
            return True
        else:
            params_vital = plugin_vital.vital_data(cvpj_plugindata)
            params_vital.setvalue('osc_1_on', 1)
            params_vital.setvalue('osc_1_level', 1)
            params_vital.setvalue('volume', 5000)

            r_duty = cvpj_plugindata.dataval_get('duty', 0)
            if r_duty == 0: vital_duty = 0.5
            if r_duty == 1: vital_duty = 0.25
            if r_duty == 2: vital_duty = 0.125

            if plugintype[1] == 'sine': vital_shape = data_wave.create_wave('sine', 0, None)
            if plugintype[1] == 'square': vital_shape = data_wave.create_wave('square', 0, vital_duty)
            if plugintype[1] == 'pulse': vital_shape = data_wave.create_wave('square', 0, vital_duty)
            if plugintype[1] == 'triangle': vital_shape = data_wave.create_wave('triangle', 0, None)
            if plugintype[1] == 'saw': vital_shape = data_wave.create_wave('saw', 0, None)
            if plugintype[1] == 'wavetable': vital_shape = data_wave.cvpjwave2wave(cvpj_plugindata, None)

            params_vital.replacewave(0, vital_shape)

            env_found = params_vital.importcvpj_env_block(cvpj_plugindata, 1, 'vol')
            if env_found: params_vital.set_modulation(1, 'lfo_1', 'osc_1_level', 1, 0, 1, 0, 0)

            #env_found = params_vital.importcvpj_env_block(cvpj_l, pluginid, 2, 'pitch')
            #if env_found: params_vital.set_modulation(1, 'lfo_1', 'osc_1_level', 1, 0, 1, 0, 0)

            params_vital.to_cvpj_vst2()
            return True