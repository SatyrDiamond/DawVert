# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import data_bytes
from functions import xtramath
from functions import note_data
from dataclasses import dataclass

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-tracktion', None, 'waveform_edit'], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json):

        if plugin_obj.plugin_subtype == '1bandEq':
            band_freq = plugin_obj.params.get('freq', 30).value
            band_shape = plugin_obj.params.get('shape', 0).value
            band_q = plugin_obj.params.get('q', 0).value
            band_gain = plugin_obj.params.get('gain', 0).value
            band_slope = plugin_obj.params.get('slope', 0).value

            if band_shape == 0: band_shape = 'high_pass'
            if band_shape == 1: band_shape = 'low_shelf'
            if band_shape == 2: band_shape = 'peak'
            if band_shape == 5: band_shape = 'high_shelf'
            if band_shape == 6: band_shape = 'low_pass'

            plugin_obj.replace('universal', 'eq-bands')
            filter_obj = plugin_obj.eq_add()
            filter_obj.type = band_shape
            filter_obj.freq = note_data.note_to_freq(band_freq-72)
            filter_obj.q = band_q
            filter_obj.gain = band_gain
            filter_obj.slope = band_slope
            return 1

        if plugin_obj.plugin_subtype == '8bandEq':
            eq_bands = []
            for num in range(8):
                eqnumtxt = str(num+1)
                eq_part = []
                for typename in ['lm', 'rs']:
                    band_enable = int(plugin_obj.params.get("enable"+eqnumtxt+typename, 0).value)
                    band_freq = plugin_obj.params.get("freq"+eqnumtxt+typename, 25).value
                    band_gain = plugin_obj.params.get("gain"+eqnumtxt+typename, 0).value
                    band_q = plugin_obj.params.get("q"+eqnumtxt+typename, 1).value
                    band_shape = plugin_obj.params.get("shape"+eqnumtxt+typename, 1).value
                    band_slope = plugin_obj.params.get("slope"+eqnumtxt+typename, 12).value

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

            eq_mode = plugin_obj.params.get("mode", 0).value
            cvpj_eq_mode = ['normal', 'l_r', 'm_s'][eq_mode]

            plugin_obj.replace('universal', 'eq-bands')
            plugin_obj.datavals.add('mode', cvpj_eq_mode)

            for eq_band in eq_bands:
                filter_obj = plugin_obj.eq_add()
                filter_obj.on = bool(eq_band[0][0])
                filter_obj.freq = eq_band[0][1]
                filter_obj.gain = eq_band[0][2]
                filter_obj.q = eq_band[0][3]
                filter_obj.type = eq_band[0][4]
                filter_obj.slope = eq_band[0][5]

                filter_obj = plugin_obj.named_eq_add('alt')
                filter_obj.on = bool(eq_band[1][0])
                filter_obj.freq = eq_band[1][1]
                filter_obj.gain = eq_band[1][2]
                filter_obj.q = eq_band[1][3]
                filter_obj.type = eq_band[1][4]
                filter_obj.slope = eq_band[1][5]
            return 1

        if plugin_obj.plugin_subtype == 'comp':
            comp_attack = plugin_obj.params.get("attack", 0).value/1000
            comp_pregain = plugin_obj.params.get("inputDb", 0).value
            comp_knee = plugin_obj.params.get("knee", 0).value
            comp_postgain = plugin_obj.params.get("outputDb", 0).value
            comp_ratio = plugin_obj.params.get("ratio", 0).value
            comp_release = plugin_obj.params.get("release", 0).value/1000
            comp_threshold = plugin_obj.params.get("threshold", 0).value
            plugin_obj.replace('universal', 'compressor')
            plugin_obj.params.add('attack', comp_attack, 'float')
            plugin_obj.params.add('pregain', comp_pregain, 'float')
            plugin_obj.params.add('knee', comp_knee, 'float')
            plugin_obj.params.add('postgain', comp_postgain, 'float')
            plugin_obj.params.add('ratio', comp_ratio, 'float')
            plugin_obj.params.add('release', comp_release, 'float')
            plugin_obj.params.add('threshold', comp_threshold, 'float')
            return 1

        if plugin_obj.plugin_subtype == 'gate':
            gate_attack = plugin_obj.params.get("attack", 0).value/1000
            gate_hold = plugin_obj.params.get("hold", 0).value/1000
            gate_release = plugin_obj.params.get("release", 0).value/1000
            gate_threshold = plugin_obj.params.get("threshold", 0).value

            plugin_obj.replace('universal', 'gate')

            plugin_obj.params.add('attack', gate_attack, 'float')
            plugin_obj.params.add('hold', gate_hold, 'float')
            plugin_obj.params.add('release', gate_release, 'float')
            plugin_obj.params.add('threshold', gate_threshold, 'float')
            return 1

        if plugin_obj.plugin_subtype == 'limiter':
            limiter_ceiling = plugin_obj.params.get("ceiling", 0).value
            limiter_gain = plugin_obj.params.get("gain", 0).value
            limiter_release = plugin_obj.params.get("release", 0).value/1000

            plugin_obj.replace('universal', 'limiter')

            plugin_obj.params.add('ceiling', limiter_ceiling, 'float')
            plugin_obj.params.add('gain', limiter_gain, 'float')
            plugin_obj.params.add('release', limiter_release, 'float')
            return 1
            
        return 2