# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import xtramath

def comp_threshold(i_val):
    return -math.log(i_val, 0.8913)

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-ableton', None, 'ableton'], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json):
        if plugin_obj.plugin_subtype == 'Redux2':
            bitcrush_BitDepth = plugin_obj.params.get('BitDepth', 0).value
            bitcrush_SampleRate = plugin_obj.params.get('SampleRate', 0).value
            bitcrush_DryWet = plugin_obj.params.get('DryWet', 0).value

            plugin_obj.replace('universal', 'bitcrush')
            plugin_obj.fxdata_add(None, bitcrush_DryWet)
            convproj_obj.move_automation(['plugin', pluginid, 'DryWet'], ['slot', pluginid, 'wet'])

            plugin_obj.params.add('bits', bitcrush_BitDepth, 'float')
            plugin_obj.params.add('freq', bitcrush_SampleRate, 'float')
            convproj_obj.moveg_automation(['plugin', pluginid], 'BitDepth', 'bits')
            convproj_obj.moveg_automation(['plugin', pluginid], 'SampleRate', 'freq')
            return 1

        if plugin_obj.plugin_subtype == 'Compressor2':
            comp_Threshold = plugin_obj.params.get('Threshold', 0).value
            comp_Ratio = plugin_obj.params.get('Ratio', 0).value
            comp_ExpansionRatio = plugin_obj.params.get('ExpansionRatio', 0).value
            comp_Attack = plugin_obj.params.get('Attack', 0).value
            comp_Release = plugin_obj.params.get('Release', 0).value
            comp_Gain = plugin_obj.params.get('Gain', 0).value
            comp_DryWet = plugin_obj.params.get('DryWet', 0).value
            comp_Model = plugin_obj.params.get('Model', 0).value
            comp_Knee = plugin_obj.params.get('Knee', 0).value

            comp_Threshold = comp_threshold(comp_Threshold)

            modeldata = 'peak'
            if comp_Model == 1: modeldata = 'rms'

            if comp_Model != 2: 
                plugin_obj.replace('universal', 'compressor')
                plugin_obj.params.add('ratio', comp_Ratio, 'float')
                convproj_obj.moveg_automation(['plugin', pluginid], 'Ratio', 'ratio')
            else: 
                plugin_obj.replace('universal', 'expander')
                plugin_obj.params.add('ratio', comp_ExpansionRatio, 'float')
                convproj_obj.moveg_automation(['plugin', pluginid], 'ExpansionRatio', 'ratio')

            plugin_obj.fxdata_add(None, comp_DryWet)

            plugin_obj.params.add('threshold', comp_Threshold, 'float')
            plugin_obj.params.add('attack', comp_Attack/1000, 'float')
            plugin_obj.params.add('release', comp_Release/1000, 'float')
            plugin_obj.params.add('postgain', comp_Gain, 'float')
            plugin_obj.params.add('knee', comp_Knee, 'float')
            
            convproj_obj.move_automation(['plugin', pluginid, 'DryWet'], ['slot', pluginid, 'wet'])
            convproj_obj.moveg_automation(['plugin', pluginid], 'Threshold', 'threshold')
            convproj_obj.moveg_automation(['plugin', pluginid], 'Attack', 'attack')
            convproj_obj.moveg_automation(['plugin', pluginid], 'Release', 'release')
            convproj_obj.moveg_automation(['plugin', pluginid], 'Gain', 'postgain')
            convproj_obj.moveg_automation(['plugin', pluginid], 'Knee', 'knee')

            convproj_obj.addmul_automation(['plugin', pluginid, 'attack'], 0, 0.001)
            convproj_obj.addmul_automation(['plugin', pluginid, 'release'], 0, 0.001)
            convproj_obj.funcval_automation(['plugin', pluginid, 'threshold'], comp_threshold)
            return 1


        if plugin_obj.plugin_subtype == 'Eq8':
            for band_num in range(8):
                groupname = ['main', 'b']
                abe_starttxt = "Bands."+str(band_num)+"/ParameterA/"
                abe_starttxt_alt = "Bands."+str(band_num)+"/ParameterB/"
                    
                band_mode = plugin_obj.params.get(abe_starttxt+"Mode", 0).value
                band_mode_alt = plugin_obj.params.get(abe_starttxt_alt+"Mode", 0).value

                cvpj_bandtype = ['high_pass', 'high_pass', 'low_shelf', 'peak', 'notch', 'high_shelf', 'low_pass', 'low_pass'][band_mode]
                cvpj_bandtype_alt = ['high_pass', 'high_pass', 'low_shelf', 'peak', 'notch', 'high_shelf', 'low_pass', 'low_pass'][band_mode_alt]

                cvpj_slope = 12 if band_mode not in [0,7] else 48
                cvpj_slope_alt = 12 if band_mode_alt not in [0,7] else 48

                filter_obj = plugin_obj.eq_add()
                filter_obj.on = bool(plugin_obj.params.get(abe_starttxt+"IsOn", 0).value)
                filter_obj.freq = int(plugin_obj.params.get(abe_starttxt+"Freq", 0).value)
                filter_obj.gain = plugin_obj.params.get(abe_starttxt+"Gain", 0).value
                filter_obj.q = plugin_obj.params.get(abe_starttxt+"Q", 0).value
                filter_obj.type = cvpj_bandtype
                filter_obj.slope = cvpj_slope

                filter_obj = plugin_obj.named_eq_add('alt')
                filter_obj.on = bool(plugin_obj.params.get(abe_starttxt_alt+"IsOn", 0).value)
                filter_obj.freq = int(plugin_obj.params.get(abe_starttxt_alt+"Freq", 0).value)
                filter_obj.gain = plugin_obj.params.get(abe_starttxt_alt+"Gain", 0).value
                filter_obj.q = plugin_obj.params.get(abe_starttxt_alt+"Q", 0).value
                filter_obj.type = cvpj_bandtype_alt
                filter_obj.slope = cvpj_slope_alt

            plugin_obj.replace('universal', 'eq-bands')
            return 1

        if plugin_obj.plugin_subtype == 'Limiter':
            limiter_ceiling = plugin_obj.params.get("Ceiling", 0).value
            limiter_gain = plugin_obj.params.get("Gain", 0).value
            limiter_release = plugin_obj.params.get("Release", 0).value/1000
            limiter_release_auto = plugin_obj.params.get("AutoRelease", False).value

            plugin_obj.replace('universal', 'limiter')

            plugin_obj.params.add('ceiling', limiter_ceiling, 'float')
            plugin_obj.params.add('gain', limiter_gain, 'float')
            plugin_obj.params.add('release', limiter_release, 'float')
            plugin_obj.params.add('release_auto', limiter_release_auto, 'bool')

            convproj_obj.moveg_automation(['plugin', pluginid], 'Ceiling', 'ceiling')
            convproj_obj.moveg_automation(['plugin', pluginid], 'Gain', 'gain')
            convproj_obj.moveg_automation(['plugin', pluginid], 'Release', 'release')
            convproj_obj.moveg_automation(['plugin', pluginid], 'AutoRelease', 'release_auto')

            convproj_obj.addmul_automation(['plugin', pluginid, 'release'], 0, 0.001)
            return 1

        if plugin_obj.plugin_subtype == 'Gate':
            gate_attack = plugin_obj.params.get("Attack", 0).value/1000
            gate_hold = plugin_obj.params.get("Hold", 0).value/1000
            gate_release = plugin_obj.params.get("Release", 0).value/1000
            gate_threshold = comp_threshold(plugin_obj.params.get("Threshold", 0).value)
            gate_flip = plugin_obj.params.get("FlipMode", 0).value
            gate_return = plugin_obj.params.get("Return", 0).value/1000

            plugin_obj.replace('universal', 'gate')

            plugin_obj.params.add('attack', gate_attack, 'float')
            plugin_obj.params.add('hold', gate_hold, 'float')
            plugin_obj.params.add('release', gate_release, 'float')
            plugin_obj.params.add('threshold', gate_threshold, 'float')
            plugin_obj.params.add('flip', gate_flip, 'float')
            plugin_obj.params.add('return', gate_return, 'float')

            convproj_obj.moveg_automation(['plugin', pluginid], 'Attack', 'attack')
            convproj_obj.moveg_automation(['plugin', pluginid], 'Hold', 'hold')
            convproj_obj.moveg_automation(['plugin', pluginid], 'Release', 'release')
            convproj_obj.moveg_automation(['plugin', pluginid], 'Threshold', 'threshold')
            convproj_obj.moveg_automation(['plugin', pluginid], 'FlipMode', 'flip')
            convproj_obj.moveg_automation(['plugin', pluginid], 'Return', 'return')

            convproj_obj.addmul_automation(['plugin', pluginid, 'attack'], 0, 0.001)
            convproj_obj.addmul_automation(['plugin', pluginid, 'hold'], 0, 0.001)
            convproj_obj.addmul_automation(['plugin', pluginid, 'release'], 0, 0.001)
            convproj_obj.addmul_automation(['plugin', pluginid, 'return'], 0, 0.001)
            convproj_obj.addmul_automation(['plugin', pluginid, 'knee'], 0, 6)

            convproj_obj.funcval_automation(['plugin', pluginid, 'threshold'], comp_threshold)
            return 1

        return 2