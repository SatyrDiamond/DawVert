# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import plugins
from functions import data_bytes
from functions import xtramath
from functions import note_data
from functions_tracks import auto_data
from dataclasses import dataclass

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-tracktion', None, 'waveform_edit'], ['universal', None, None], False, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == '1bandEq':
            band_freq = cvpj_plugindata.param_get('freq', 30)[0]
            band_shape = cvpj_plugindata.param_get('shape', 0)[0]
            band_q = cvpj_plugindata.param_get('q', 0)[0]
            band_gain = cvpj_plugindata.param_get('gain', 0)[0]
            band_slope = cvpj_plugindata.param_get('slope', 0)[0]

            if band_shape == 0: band_shape = 'high_pass'
            if band_shape == 1: band_shape = 'low_shelf'
            if band_shape == 2: band_shape = 'peak'
            if band_shape == 5: band_shape = 'high_shelf'
            if band_shape == 6: band_shape = 'low_pass'

            cvpj_plugindata.replace('universal', 'eq-bands')
            cvpj_plugindata.dataval_add('num_bands', 1)
            cvpj_plugindata.eqband_add(1, note_data.note_to_freq(band_freq-72), band_shape, None)
            if band_shape in ['high_pass', 'low_pass']: cvpj_plugindata.eqband_add_param('slope', band_slope, None)
            else: cvpj_plugindata.eqband_add_param('gain', band_gain, None)
            cvpj_plugindata.eqband_add_param('q', band_q, None)
            return 1

        if plugintype[1] == '8bandEq':
            eq_bands = []
            for num in range(8):
                eqnumtxt = str(num+1)
                eq_part = []
                for typename in ['lm', 'rs']:
                    band_enable = int(cvpj_plugindata.param_get("enable"+eqnumtxt+typename, 0)[0])
                    band_freq = cvpj_plugindata.param_get("freq"+eqnumtxt+typename, 25)[0]
                    band_gain = cvpj_plugindata.param_get("gain"+eqnumtxt+typename, 0)[0]
                    band_q = cvpj_plugindata.param_get("q"+eqnumtxt+typename, 1)[0]
                    band_shape = cvpj_plugindata.param_get("shape"+eqnumtxt+typename, 1)[0]
                    band_slope = cvpj_plugindata.param_get("slope"+eqnumtxt+typename, 12)[0]

                    if band_shape == 0: band_shape = 'low_pass'
                    if band_shape == 1: band_shape = 'low_shelf'
                    if band_shape == 2: band_shape = 'peak'
                    if band_shape == 3: band_shape = 'band_pass'
                    if band_shape == 4: band_shape = 'band_stop'
                    if band_shape == 5: band_shape = 'high_shelf'
                    if band_shape == 6: band_shape = 'high_pass'

                    #if band_shape in ['low_pass', 'high_pass']: band_q = band_q**2
                    #elif band_shape in ['low_shelf', 'high_shelf']: pass
                    #else: band_q = (10-float(band_q))/10

                    band_freq = note_data.note_to_freq(band_freq-72)
                    eq_part.append([band_enable, band_freq, band_gain, band_q, band_shape, band_slope])
                eq_bands.append(eq_part)

            eq_mode = cvpj_plugindata.param_get("mode", 0)[0]
            cvpj_eq_mode = ['normal', 'l_r', 'm_s'][eq_mode]

            cvpj_plugindata.replace('universal', 'eq-bands')
            cvpj_plugindata.dataval_add('num_bands', 8)
            cvpj_plugindata.dataval_add('mode', cvpj_eq_mode)

            for eq_band in eq_bands:
                cvpj_plugindata.eqband_add(eq_band[0][0], eq_band[0][1], eq_band[0][4], None)
                cvpj_plugindata.eqband_add_param('gain', eq_band[0][2], None)
                cvpj_plugindata.eqband_add_param('q', eq_band[0][3], None)
                cvpj_plugindata.eqband_add_param('slope', eq_band[0][5], None)

                cvpj_plugindata.eqband_add(eq_band[1][0], eq_band[1][1], eq_band[0][4], 'b')
                cvpj_plugindata.eqband_add_param('gain', eq_band[1][2], 'b')
                cvpj_plugindata.eqband_add_param('q', eq_band[1][3], 'b')
                cvpj_plugindata.eqband_add_param('slope', eq_band[1][5], 'b')
            return 1

        if plugintype[1] == 'comp':
            comp_attack = cvpj_plugindata.param_get("attack", 0)[0]/1000
            comp_pregain = cvpj_plugindata.param_get("inputDb", 0)[0]
            comp_knee = cvpj_plugindata.param_get("knee", 0)[0]
            comp_postgain = cvpj_plugindata.param_get("outputDb", 0)[0]
            comp_ratio = cvpj_plugindata.param_get("ratio", 0)[0]
            comp_release = cvpj_plugindata.param_get("release", 0)[0]/1000
            comp_threshold = cvpj_plugindata.param_get("threshold", 0)[0]
            cvpj_plugindata.replace('universal', 'compressor')
            cvpj_plugindata.param_add('attack', comp_attack, 'float', 'attack')
            cvpj_plugindata.param_add('pregain', comp_pregain, 'float', 'pregain')
            cvpj_plugindata.param_add('knee', comp_knee, 'float', 'knee')
            cvpj_plugindata.param_add('postgain', comp_postgain, 'float', 'postgain')
            cvpj_plugindata.param_add('ratio', comp_ratio, 'float', 'ratio')
            cvpj_plugindata.param_add('release', comp_release, 'float', 'release')
            cvpj_plugindata.param_add('threshold', comp_threshold, 'float', 'threshold')
            return 1

        if plugintype[1] == 'gate':
            gate_attack = cvpj_plugindata.param_get("attack", 0)[0]/1000
            gate_hold = cvpj_plugindata.param_get("hold", 0)[0]/1000
            gate_release = cvpj_plugindata.param_get("release", 0)[0]/1000
            gate_threshold = cvpj_plugindata.param_get("threshold", 0)[0]

            cvpj_plugindata.replace('universal', 'gate')

            cvpj_plugindata.param_add('attack', gate_attack, 'float', 'attack')
            cvpj_plugindata.param_add('hold', gate_hold, 'float', 'hold')
            cvpj_plugindata.param_add('release', gate_release, 'float', 'release')
            cvpj_plugindata.param_add('threshold', gate_threshold, 'float', 'threshold')
            return 1

        if plugintype[1] == 'limiter':
            limiter_ceiling = cvpj_plugindata.param_get("ceiling", 0)[0]
            limiter_gain = cvpj_plugindata.param_get("gain", 0)[0]
            limiter_release = cvpj_plugindata.param_get("release", 0)[0]/1000

            cvpj_plugindata.replace('universal', 'limiter')

            cvpj_plugindata.param_add('ceiling', limiter_ceiling, 'float', 'ceiling')
            cvpj_plugindata.param_add('gain', limiter_gain, 'float', 'gain')
            cvpj_plugindata.param_add('release', limiter_release, 'float', 'release')
            return 1
            
        return 2