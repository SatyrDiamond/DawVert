# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import plugins
from functions import xtramath
from functions_tracks import auto_data

def comp_threshold(i_val):
    return -math.log(i_val, 0.8913)

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-ableton', None, 'ableton'], ['universal', None, None], False, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == 'Redux2':
            bitcrush_BitDepth = cvpj_plugindata.param_get('BitDepth', 0)[0]
            bitcrush_SampleRate = cvpj_plugindata.param_get('SampleRate', 0)[0]
            bitcrush_DryWet = cvpj_plugindata.param_get('DryWet', 0)[0]
            cvpj_plugindata.replace('universal', 'bitcrush')

            cvpj_plugindata.fxdata_add(None, bitcrush_DryWet)
            auto_data.move(cvpj_l, ['plugin', pluginid, 'DryWet'], ['slot', pluginid, 'wet'])

            cvpj_plugindata.param_add('bits', bitcrush_BitDepth, 'float', 'bits')
            cvpj_plugindata.param_add('freq', bitcrush_SampleRate, 'float', 'freq')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'BitDepth', 'bits')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'SampleRate', 'freq')
            return 1

        if plugintype[1] == 'Compressor2':
            comp_Threshold = cvpj_plugindata.param_get('Threshold', 0)[0]
            comp_Ratio = cvpj_plugindata.param_get('Ratio', 0)[0]
            comp_ExpansionRatio = cvpj_plugindata.param_get('ExpansionRatio', 0)[0]
            comp_Attack = cvpj_plugindata.param_get('Attack', 0)[0]
            comp_Release = cvpj_plugindata.param_get('Release', 0)[0]
            comp_Gain = cvpj_plugindata.param_get('Gain', 0)[0]
            comp_DryWet = cvpj_plugindata.param_get('DryWet', 0)[0]
            comp_Model = cvpj_plugindata.param_get('Model', 0)[0]
            comp_Knee = cvpj_plugindata.param_get('Knee', 0)[0]

            comp_Threshold = comp_threshold(comp_Threshold)

            modeldata = 'peak'
            if comp_Model == 1: modeldata = 'rms'

            if comp_Model != 2: 
                cvpj_plugindata.replace('universal', 'compressor')
                cvpj_plugindata.param_add('ratio', comp_Ratio, 'float', 'ratio')
                auto_data.rename_plugparam(cvpj_l, pluginid, 'Ratio', 'ratio')
            else: 
                cvpj_plugindata.replace('universal', 'expander')
                cvpj_plugindata.param_add('ratio', comp_ExpansionRatio, 'float', 'ratio')
                auto_data.rename_plugparam(cvpj_l, pluginid, 'ExpansionRatio', 'ratio')

            cvpj_plugindata.fxdata_add(None, comp_DryWet)

            cvpj_plugindata.param_add('threshold', comp_Threshold, 'float', 'threshold')
            cvpj_plugindata.param_add('attack', comp_Attack/1000, 'float', 'attack')
            cvpj_plugindata.param_add('release', comp_Release/1000, 'float', 'release')
            cvpj_plugindata.param_add('postgain', comp_Gain, 'float', 'postgain')
            cvpj_plugindata.param_add('knee', comp_Knee, 'float', 'knee')
            
            auto_data.move(cvpj_l, ['plugin', pluginid, 'DryWet'], ['slot', pluginid, 'wet'])
            auto_data.rename_plugparam(cvpj_l, pluginid, 'Threshold', 'threshold')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'Attack', 'attack')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'Release', 'release')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'Gain', 'postgain')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'Knee', 'knee')

            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'attack'], 0, 0.001)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'release'], 0, 0.001)
            auto_data.function_value(cvpj_l, ['plugin', pluginid, 'threshold'], comp_threshold)
            return 1


        if plugintype[1] == 'Eq8':
            for group_num in range(2):
                for band_num in range(8):
                    groupname = ['main', 'b'][group_num]
                    abe_starttxt = "Bands."+str(band_num)+"/Parameter"+['A', 'B'][group_num]+"/"
                    
                    band_Freq = int(cvpj_plugindata.param_get(abe_starttxt+"Freq", 0)[0])
                    band_Gain = cvpj_plugindata.param_get(abe_starttxt+"Gain", 0)[0]
                    band_IsOn = cvpj_plugindata.param_get(abe_starttxt+"IsOn", 0)[0]
                    band_Mode = cvpj_plugindata.param_get(abe_starttxt+"Mode", 0)[0]
                    band_Q = cvpj_plugindata.param_get(abe_starttxt+"Q", 0)[0]

                    cvpj_bandtype = ['high_pass', 'high_pass', 'low_shelf', 'peak', 'notch', 'high_shelf', 'low_pass', 'low_pass'][band_Mode]

                    cvpj_slope = 12 if band_Mode not in [0,7] else 48

                    cvpj_plugindata.eqband_add(int(band_IsOn), band_Freq, cvpj_bandtype, groupname)
                    cvpj_plugindata.eqband_add_param('q', band_Q, groupname)
                    if cvpj_bandtype not in ['low_pass', 'high_pass']:
                        cvpj_plugindata.eqband_add_param('gain', band_Gain, groupname)
                    else:
                        cvpj_plugindata.eqband_add_param('slope', cvpj_slope, groupname)

            cvpj_plugindata.replace('universal', 'eq-bands')
            cvpj_plugindata.dataval_add('num_bands', 8)
            return 1

        if plugintype[1] == 'Limiter':
            limiter_ceiling = cvpj_plugindata.param_get("Ceiling", 0)[0]
            limiter_gain = cvpj_plugindata.param_get("Gain", 0)[0]
            limiter_release = cvpj_plugindata.param_get("Release", 0)[0]/1000
            limiter_release_auto = cvpj_plugindata.param_get("AutoRelease", False)[0]

            cvpj_plugindata.replace('universal', 'limiter')

            cvpj_plugindata.param_add('ceiling', limiter_ceiling, 'float', 'ceiling')
            cvpj_plugindata.param_add('gain', limiter_gain, 'float', 'gain')
            cvpj_plugindata.param_add('release', limiter_release, 'float', 'release')
            cvpj_plugindata.param_add('release_auto', limiter_release_auto, 'bool', 'release_auto')

            auto_data.rename_plugparam(cvpj_l, pluginid, 'Ceiling', 'ceiling')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'Gain', 'gain')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'Release', 'release')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'AutoRelease', 'release_auto')

            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'release'], 0, 0.001)
            return 1

        if plugintype[1] == 'Gate':
            gate_attack = cvpj_plugindata.param_get("Attack", 0)[0]/1000
            gate_hold = cvpj_plugindata.param_get("Hold", 0)[0]/1000
            gate_release = cvpj_plugindata.param_get("Release", 0)[0]/1000
            gate_threshold = comp_threshold(cvpj_plugindata.param_get("Threshold", 0)[0])
            gate_flip = cvpj_plugindata.param_get("FlipMode", 0)[0]
            gate_return = cvpj_plugindata.param_get("Return", 0)[0]/1000

            cvpj_plugindata.replace('universal', 'gate')

            cvpj_plugindata.param_add('attack', gate_attack, 'float', 'attack')
            cvpj_plugindata.param_add('hold', gate_hold, 'float', 'hold')
            cvpj_plugindata.param_add('release', gate_release, 'float', 'release')
            cvpj_plugindata.param_add('threshold', gate_threshold, 'float', 'threshold')
            cvpj_plugindata.param_add('flip', gate_flip, 'float', 'flip')
            cvpj_plugindata.param_add('return', gate_return, 'float', 'return')

            auto_data.rename_plugparam(cvpj_l, pluginid, 'Attack', 'attack')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'Hold', 'hold')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'Release', 'release')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'Threshold', 'threshold')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'FlipMode', 'flip')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'Return', 'return')

            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'attack'], 0, 0.001)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'hold'], 0, 0.001)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'release'], 0, 0.001)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'return'], 0, 0.001)
            auto_data.function_value(cvpj_l, ['plugin', pluginid, 'threshold'], comp_threshold)
            return 1

        return 2