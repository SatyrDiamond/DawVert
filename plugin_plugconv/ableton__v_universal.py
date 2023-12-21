# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv
from functions import data_values
from functions import xtramath
from functions_tracks import auto_data
import math

delaytime = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 4],
    [4, 5],
    [5, 6],
    [6, 8],
    [7, 16],
    ]

eq_types = ['high_pass', 'low_shelf', 'peak', 'notch', 'high_shelf', 'low_pass']

def comp_threshold(i_val):
    return math.pow(0.8913,(-i_val))

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['universal', None, None], ['native-ableton', None, 'ableton'], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        fx_on, fx_wet = cvpj_plugindata.fxdata_get()

        if plugintype[1] == 'delay-c':
            d_time_type = cvpj_plugindata.dataval_get('time_type', 'seconds')
            d_time = cvpj_plugindata.dataval_get('time', 1)
            d_feedback = cvpj_plugindata.dataval_get('feedback', 0.0)

            cvpj_plugindata.replace('native-ableton', 'Delay')

            cvpj_plugindata.param_add('DelayLine_Link', True, 'bool', "DelayLine_Link")
            cvpj_plugindata.param_add('Feedback', d_feedback, 'float', "Feedback")
            cvpj_plugindata.param_add('DryWet', fx_wet, 'float', "DryWet")

            if d_time_type == 'seconds':
                cvpj_plugindata.param_add('DelayLine_SyncL', False, 'bool', "DelayLine_SyncL")
                cvpj_plugindata.param_add('DelayLine_SyncR', False, 'bool', "DelayLine_SyncR")
                cvpj_plugindata.param_add('DelayLine_TimeL', d_time/1000, 'float', "DelayLine_TimeL")
                cvpj_plugindata.param_add('DelayLine_TimeR', d_time/1000, 'float', "DelayLine_TimeR")

            if d_time_type == 'steps':
                d_delay_sync = data_values.list_tab_closest(delaytime, d_time, 1)[0][0]
                cvpj_plugindata.param_add('DelayLine_SyncL', True, 'bool', "DelayLine_SyncL")
                cvpj_plugindata.param_add('DelayLine_SyncR', True, 'bool', "DelayLine_SyncR")
                cvpj_plugindata.param_add('DelayLine_SyncedSixteenthL', d_delay_sync, 'float', "DelayLine_SyncedSixteenthL")
                cvpj_plugindata.param_add('DelayLine_SyncedSixteenthR', d_delay_sync, 'float', "DelayLine_SyncedSixteenthR")

            auto_data.move(cvpj_l, ['slot', pluginid, 'wet'], ['plugin', pluginid, 'DryWet'])
            return 0

        if plugintype[1] in ['compressor','expander']:
            v_threshold = cvpj_plugindata.param_get('threshold', 0)[0]
            v_gain = cvpj_plugindata.param_get('postgain', 0)[0]
            v_attack = cvpj_plugindata.param_get('attack', 0)[0]
            v_release = cvpj_plugindata.param_get('release', 0)[0]
            v_knee = cvpj_plugindata.param_get('knee', 0)[0]
            v_ratio = cvpj_plugindata.param_get('ratio', 0)[0]
            detect_mode = cvpj_plugindata.dataval_get('detect_mode', 'peak')
            v_model = 1 if detect_mode == 'rms' else 0
            if plugintype[1] == 'expander': v_model = 2

            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'attack'], 0, 1000)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'release'], 0, 1000)
            auto_data.function_value(cvpj_l, ['plugin', pluginid, 'threshold'], comp_threshold)
            
            auto_data.move(cvpj_l, ['slot', pluginid, 'wet'], ['plugin', pluginid, 'DryWet'])
            auto_data.rename_plugparam(cvpj_l, pluginid, 'threshold', 'Threshold')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'attack', 'Attack')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'release', 'Release')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'postgain', 'Gain')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'knee', 'Knee')

            cvpj_plugindata.replace('native-ableton', 'Compressor2')

            cvpj_plugindata.param_add('Threshold', comp_threshold(v_threshold), 'float', "")
            cvpj_plugindata.param_add('Ratio', v_ratio, 'float', "")
            cvpj_plugindata.param_add('ExpansionRatio', v_ratio, 'float', "")
            cvpj_plugindata.param_add('Attack', v_attack*1000, 'float', "")
            cvpj_plugindata.param_add('Release', v_release*1000, 'float', "")
            cvpj_plugindata.param_add('Gain', v_gain, 'float', "")
            cvpj_plugindata.param_add('Knee', v_knee, 'float', "")
            cvpj_plugindata.param_add('Model', v_model, 'float', "")
            cvpj_plugindata.param_add('DryWet', fx_wet, 'float', "")
            return 0

        if plugintype[1] == 'gate':
            gate_attack = cvpj_plugindata.param_get('attack', 0)[0]*1000
            gate_hold = cvpj_plugindata.param_get('hold', 0)[0]*1000
            gate_release = cvpj_plugindata.param_get('release', 0)[0]*1000
            gate_threshold = comp_threshold(cvpj_plugindata.param_get('threshold', 0)[0])
            gate_flip = cvpj_plugindata.param_get('flip', 0)[0]
            gate_return = cvpj_plugindata.param_get('return', 0)[0]*1000

            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'attack'], 0, 1000)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'hold'], 0, 1000)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'release'], 0, 1000)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'return'], 0, 1000)
            auto_data.rename_plugparam(cvpj_l, pluginid, 'attack', 'Attack')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'hold', 'Hold')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'release', 'Release')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'threshold', 'Threshold')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'flip', 'FlipMode')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'return', 'Return')
            auto_data.move(cvpj_l, ['slot', pluginid, 'wet'], ['plugin', pluginid, 'DryWet'])

            cvpj_plugindata.replace('native-ableton', 'Gate')

            cvpj_plugindata.param_add('Attack', gate_attack, 'float', "")
            cvpj_plugindata.param_add('Hold', gate_hold, 'float', "")
            cvpj_plugindata.param_add('Release', gate_release, 'float', "")
            cvpj_plugindata.param_add('Threshold', gate_threshold, 'float', "")
            cvpj_plugindata.param_add('FlipMode', gate_flip, 'float', "")
            cvpj_plugindata.param_add('Return', gate_return, 'float', "")
            return 0

        if plugintype[1] == 'limiter':
            limiter_ceiling = cvpj_plugindata.param_get('ceiling', 0)[0]
            limiter_gain = cvpj_plugindata.param_get('gain', 0)[0]
            limiter_release = cvpj_plugindata.param_get('release', 0)[0]*1000
            limiter_release_auto = cvpj_plugindata.param_get('release_auto', 0)[0]

            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'release'], 0, 1000)
            auto_data.rename_plugparam(cvpj_l, pluginid, 'ceiling', 'Ceiling')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'gain', 'Gain')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'release', 'Release')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'release_auto', 'AutoRelease')

            cvpj_plugindata.replace('native-ableton', 'Limiter')

            cvpj_plugindata.param_add('Ceiling', limiter_ceiling, 'float', "")
            cvpj_plugindata.param_add('Gain', limiter_gain, 'float', "")
            cvpj_plugindata.param_add('Release', limiter_release, 'float', "")
            cvpj_plugindata.param_add('AutoRelease', limiter_release_auto, 'bool', "")
            return 0


        if plugintype[1] == 'bitcrush':
            bitcrush_BitDepth = cvpj_plugindata.param_get('bits', 0)[0]
            bitcrush_SampleRate = cvpj_plugindata.param_get('freq', 0)[0]

            cvpj_plugindata.replace('native-ableton', 'Redux2')

            cvpj_plugindata.param_add('BitDepth', bitcrush_BitDepth, 'float', "")
            cvpj_plugindata.param_add('SampleRate', bitcrush_SampleRate, 'float', "")
            auto_data.rename_plugparam(cvpj_l, pluginid, 'bits', 'BitDepth')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'freq', 'SampleRate')
            return 0

        if plugintype[1] == 'eq-bands':
            cvpj_plugindata.replace('native-ableton', 'Eq8')
            auto_data.del_plugin(cvpj_l, pluginid)

            groupname = ['main', 'b']
            cvpj_plugindata.param_add('AdaptiveQ', True, 'bool', "")

            for group_num in range(2):
                cvpj_bands, reorder = cvpj_plugindata.eqband_get_limitnum(groupname[group_num], 8)
                for band_num in range(8):
                    abe_starttxt = "Bands."+str(band_num)+"/Parameter"+['A', 'B'][group_num]+"/"

                    eq_band = cvpj_bands[band_num]
                    if eq_band != None:

                        eq_band_enable = eq_band['on']
                        eq_band_freq = eq_band['freq']
                        eq_band_gain = eq_band['gain'] if 'gain' in eq_band else 0
                        eq_band_shape = eq_band['type']
                        eq_band_q = eq_band['q'] if 'q' in eq_band else 1
                        eq_band_slope = eq_band['slope'] if 'slope' in eq_band else 12

                        als_shape = eq_types.index(eq_band_shape)+1 if eq_band_shape in eq_types else 3

                        if als_shape == 1 and eq_band_slope > 36: als_shape = 0
                        if als_shape == 6 and eq_band_slope > 36: als_shape = 7

                        cvpj_plugindata.param_add(abe_starttxt+'Freq', eq_band_freq, 'float', "")
                        cvpj_plugindata.param_add(abe_starttxt+'Gain', eq_band_gain, 'float', "")
                        cvpj_plugindata.param_add(abe_starttxt+'IsOn', bool(eq_band_enable), 'bool', "")
                        cvpj_plugindata.param_add(abe_starttxt+'Mode', als_shape, 'float', "")
                        cvpj_plugindata.param_add(abe_starttxt+'Q', eq_band_q, 'float', "")

                        cvpj_band = cvpj_bands[band_num]
                        #print(groupname[group_num], band_num, cvpj_band, als_shape)
            return 0

        if plugintype[1] == 'tremolo':
            lfo_freq = cvpj_plugindata.param_get('freq', 0)[0]
            lfo_depth = cvpj_plugindata.param_get('depth', 0)[0]
            cvpj_plugindata.replace('native-ableton', 'AutoPan')
            cvpj_plugindata.param_add('Lfo/Frequency', lfo_freq, 'float', "")
            cvpj_plugindata.param_add('Lfo/IsOn', True, 'bool', "")
            cvpj_plugindata.param_add('Lfo/LfoAmount', lfo_depth, 'float', "")
            auto_data.rename_plugparam(cvpj_l, pluginid, 'freq', 'Lfo/Frequency')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'depth', 'Lfo/LfoAmount')
            return 0

        if plugintype[1] == 'vibrato':
            lfo_freq = cvpj_plugindata.param_get('freq', 0)[0]
            lfo_depth = cvpj_plugindata.param_get('depth', 0)[0]
            cvpj_plugindata.replace('native-ableton', 'Chorus2')
            cvpj_plugindata.param_add('Mode', 2, 'int', "")
            cvpj_plugindata.param_add('Width', 1, 'float', "")
            cvpj_plugindata.param_add('OutputGain', 1, 'float', "")
            cvpj_plugindata.param_add('DryWet', 1, 'float', "")
            cvpj_plugindata.param_add('Rate', lfo_freq, 'float', "")
            cvpj_plugindata.param_add('Amount', lfo_depth/2, 'float', "")

            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'depth'], 0, 0.5)
            auto_data.rename_plugparam(cvpj_l, pluginid, 'freq', 'Rate')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'depth', 'Amount')
            return 0
            
        return 2