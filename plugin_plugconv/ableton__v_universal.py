# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv
from functions import data_values
from functions import xtramath
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
            return True

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
            return True

        if plugintype[1] == 'gate':
            gate_attack = cvpj_plugindata.param_get('attack', 0)[0]*1000
            gate_hold = cvpj_plugindata.param_get('hold', 0)[0]*1000
            gate_release = cvpj_plugindata.param_get('release', 0)[0]*1000
            gate_threshold = comp_threshold(cvpj_plugindata.param_get('threshold', 0)[0])
            gate_flip = cvpj_plugindata.param_get('flip', 0)[0]*1000
            gate_return = cvpj_plugindata.param_get('return', 0)[0]*1000

            cvpj_plugindata.replace('native-ableton', 'Gate')

            cvpj_plugindata.param_add('Attack', gate_attack, 'float', "")
            cvpj_plugindata.param_add('Hold', gate_hold, 'float', "")
            cvpj_plugindata.param_add('Release', gate_release, 'float', "")
            cvpj_plugindata.param_add('Threshold', gate_threshold, 'float', "")
            cvpj_plugindata.param_add('FlipMode', gate_flip, 'float', "")
            cvpj_plugindata.param_add('Return', gate_return, 'float', "")
            return True

        if plugintype[1] == 'limiter':
            limiter_ceiling = cvpj_plugindata.param_get('ceiling', 0)[0]
            limiter_gain = cvpj_plugindata.param_get('gain', 0)[0]
            limiter_release = cvpj_plugindata.param_get('release', 0)[0]*1000
            limiter_release_auto = cvpj_plugindata.param_get('release_auto', 0)[0]

            cvpj_plugindata.replace('native-ableton', 'Limiter')

            cvpj_plugindata.param_add('Ceiling', limiter_ceiling, 'float', "")
            cvpj_plugindata.param_add('Gain', limiter_gain, 'float', "")
            cvpj_plugindata.param_add('Release', limiter_release, 'float', "")
            cvpj_plugindata.param_add('AutoRelease', limiter_release_auto, 'bool', "")
            return True