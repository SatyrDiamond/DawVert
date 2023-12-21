# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv
from functions import note_data
from functions import xtramath
from functions import data_values

delaytime = [
    [0, 16*32],
    [1, 16*28],
    [2, 16*24],
    [3, 16*20],
    [4, 16*16],
    [5, 16*12],
    [6, 16*10],
    [7, 16*8],
    [8, 16*6],
    [9, 16*5],
    [10, 16*4],
    [11, 16*3],
    [12, 16*2],
    [13, 16*1],
    [14, 20],
    [15, 16],
    [16, 11],
    [17, 12],
    [18, 8],
    [19, 5],
    [20, 6],
    [21, 4],
    [22, 2.5],
    [23, 3],
    [24, 2],
    [25, 1.5],
    [26, 1.5],
    [27, 1],
    [28, 0.75],
    [29, 0.75],
    [30, 0.5],
    [31, 3/8],
    [32, 0.25],
    [33, 0.125],
    [34, 0],
]

wf_eq_modes = ['normal', 'l_r', 'm_s']

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['universal', None, None], ['native-tracktion', None, 'waveform_edit'], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == 'eq-bands':
            cvpj_eq_mode = cvpj_plugindata.dataval_get('mode', 'normal')

            cvpj_plugindata.replace('native-tracktion', '8bandEq')

            eq_mode = wf_eq_modes.index(cvpj_eq_mode) if cvpj_eq_mode in wf_eq_modes else 0
            cvpj_plugindata.param_add("mode", eq_mode, 'float', '')

            num_bands = cvpj_plugindata.dataval_get('num_bands', 8)
            cvpj_bands_a = cvpj_plugindata.eqband_get(None)
            cvpj_bands_b = cvpj_plugindata.eqband_get('b')

            cvpj_bands_a, reorder = cvpj_plugindata.eqband_get_limitnum(None, 8)
            cvpj_bands_b, reorder = cvpj_plugindata.eqband_get_limitnum('b', 8)

            for eq_num in range(2):
                typename = ['lm', 'rs'][eq_num]
                cvpj_bands = [cvpj_bands_a, cvpj_bands_b][eq_num]
                for index, eq_band in enumerate(cvpj_bands, start=1):
                    if eq_band != None:
                        eqnumtxt = str(index)
                        eq_band_enable = eq_band['on']
                        eq_band_freq = note_data.freq_to_note_noround(eq_band['freq'])+72
                        eq_band_gain = eq_band['gain'] if 'gain' in eq_band else 0
                        eq_band_shape = eq_band['type']
                        eq_band_q = eq_band['q'] if 'q' in eq_band else 1
                        eq_band_slope = eq_band['slope'] if 'slope' in eq_band else 12
            
                        #if eq_band_shape in ['low_pass', 'high_pass']: eq_band_q = xtramath.logpowmul(eq_band_q, 0.5) if eq_band_q != 0 else 0
                        #elif eq_band_shape in ['low_shelf', 'high_shelf']: eq_band_q = xtramath.logpowmul(eq_band_q, 0.5) if eq_band_q != 0 else 0
                        #else: eq_band_q = (10-eq_band_q)*10

                        if eq_band_shape == 'low_pass': wf_shape = 0
                        if eq_band_shape == 'low_shelf': wf_shape = 1
                        if eq_band_shape == 'peak': wf_shape = 2
                        if eq_band_shape == 'band_pass': wf_shape = 3
                        if eq_band_shape == 'band_stop': wf_shape = 4
                        if eq_band_shape == 'high_shelf': wf_shape = 5
                        if eq_band_shape == 'high_pass': wf_shape = 6

                        cvpj_plugindata.param_add("enable"+eqnumtxt+typename, eq_band_enable, 'int', '')
                        cvpj_plugindata.param_add("freq"+eqnumtxt+typename, eq_band_freq, 'float', '')
                        cvpj_plugindata.param_add("gain"+eqnumtxt+typename, eq_band_gain, 'float', '')
                        cvpj_plugindata.param_add("q"+eqnumtxt+typename, eq_band_q, 'float', '')
                        cvpj_plugindata.param_add("shape"+eqnumtxt+typename, wf_shape, 'float', '')
                        cvpj_plugindata.param_add("slope"+eqnumtxt+typename, eq_band_slope, 'float', '')
            return 1

        if plugintype[1] == 'delay-c':
            d_time_type = cvpj_plugindata.dataval_get('time_type', 'seconds')
            d_time = cvpj_plugindata.dataval_get('time', 1)
            d_feedback = cvpj_plugindata.dataval_get('feedback', 0.0)
            fx_on, fx_wet = cvpj_plugindata.fxdata_get()
            cvpj_plugindata.fxdata_add(None, 1)

            cvpj_plugindata.replace('native-tracktion', 'stereoDelay')

            if d_time_type == 'seconds':
                cvpj_plugindata.param_add('sync', '0.0', 'float', "sync")
                cvpj_plugindata.param_add('delaySyncOffL', d_time*1000, 'float', "delaySyncOffL")
                cvpj_plugindata.param_add('delaySyncOffR', d_time*1000, 'float', "delaySyncOffR")

            if d_time_type == 'steps':
                wf_delaySync = data_values.list_tab_closest(delaytime, d_time, 1)
                cvpj_plugindata.param_add('sync', '1.0', 'float', "sync")
                cvpj_plugindata.param_add('delaySyncOnL', wf_delaySync[0][0], 'float', "delaySyncOffL")
                cvpj_plugindata.param_add('delaySyncOnR', wf_delaySync[0][0], 'float', "delaySyncOffR")

            cvpj_plugindata.param_add('feedbackL', d_feedback*100, 'float', "feedbackL")
            cvpj_plugindata.param_add('feedbackR', d_feedback*100, 'float', "feedbackR")
            cvpj_plugindata.param_add('mix', fx_wet, 'float', "mix")
            return 1

        if plugintype[1] == 'compressor':
            v_attack = cvpj_plugindata.param_get('attack', 0)[0]*1000
            v_postgain = cvpj_plugindata.param_get('postgain', 0)[0]
            v_pregain = cvpj_plugindata.param_get('pregain', 0)[0]
            v_ratio = cvpj_plugindata.param_get('ratio', 0)[0]
            v_knee = cvpj_plugindata.param_get('knee', 0)[0]
            v_release = cvpj_plugindata.param_get('release', 0)[0]*1000
            v_threshold = cvpj_plugindata.param_get('threshold', 0)[0]

            cvpj_plugindata.replace('native-tracktion', 'comp')

            cvpj_plugindata.param_add('threshold', v_threshold, 'float', "threshold")
            cvpj_plugindata.param_add('ratio', v_ratio, 'float', "ratio")
            cvpj_plugindata.param_add('attack', v_attack, 'float', "attack")
            cvpj_plugindata.param_add('release', v_release, 'float', "release")
            cvpj_plugindata.param_add('knee', v_knee, 'float', "knee")
            cvpj_plugindata.param_add('outputDb', v_postgain, 'float', "outputDb")
            cvpj_plugindata.param_add('inputDb', v_pregain, 'float', "inputDb")
            return 1

        if plugintype[1] == 'gate':
            gate_attack = cvpj_plugindata.param_get('attack', 0)[0]*1000
            gate_hold = cvpj_plugindata.param_get('hold', 0)[0]*1000
            gate_release = cvpj_plugindata.param_get('release', 0)[0]*1000
            gate_threshold = cvpj_plugindata.param_get('threshold', 0)[0]

            cvpj_plugindata.replace('native-tracktion', 'gate')

            cvpj_plugindata.param_add('attack', gate_attack, 'float', "attack")
            cvpj_plugindata.param_add('hold', gate_hold, 'float', "hold")
            cvpj_plugindata.param_add('release', gate_release, 'float', "release")
            cvpj_plugindata.param_add('threshold', gate_threshold, 'float', "threshold")
            return 1

        if plugintype[1] == 'limiter':
            limiter_ceiling = cvpj_plugindata.param_get('ceiling', 0)[0]
            limiter_gain = cvpj_plugindata.param_get('gain', 0)[0]
            limiter_release = cvpj_plugindata.param_get('release', 0)[0]*1000

            cvpj_plugindata.replace('native-tracktion', 'limiter')

            cvpj_plugindata.param_add('ceiling', limiter_ceiling, 'float', "ceiling")
            cvpj_plugindata.param_add('gain', limiter_gain, 'float', "gain")
            cvpj_plugindata.param_add('release', limiter_release, 'float', "release")
            return 1
            
        return 2
