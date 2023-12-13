# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv
from functions import note_data
from functions import xtramath
import math

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['universal', None, None], ['native-flstudio', None, 'flp'], True, True
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == 'eq-bands':
            main_lvl  = cvpj_plugindata.dataval_get('mode', 'gain_out')*100

            cvpj_plugindata.replace('native-flstudio', 'fruity parametric eq 2')

            cvpj_bands, reorder = cvpj_plugindata.eqband_get_limitnum(None, 7)

            for index, eq_band in enumerate(cvpj_bands, start=1):
                if eq_band != None:
                    bandstarttxt = str(index)
                    eq_band_enable = eq_band['on']
                    eq_band_freq = eq_band['freq']
                    eq_band_gain = eq_band['gain'] if 'gain' in eq_band else 0
                    eq_band_shape = eq_band['type']
                    eq_band_q = eq_band['q'] if 'q' in eq_band else 1
                    eq_band_slope = eq_band['slope'] if 'slope' in eq_band else 12

                    eq_band_freq = math.log(eq_band_freq / 20) / math.log(1000)

                    if eq_band_shape in ['low_shelf', 'high_shelf']: 
                        eq_band_q = 1-(eq_band_q/1.2)
                    elif eq_band_shape in ['low_pass', 'high_pass']: 
                        eq_band_q = math.log(eq_band_q, 2) / 5
                        eq_band_q = xtramath.between_to_one(1, -1, eq_band_q)
                    else: 
                        eq_band_q = xtramath.logpowmul(eq_band_q, -1)
                        eq_band_q = (eq_band_q-0.01)/3
                        eq_band_q = xtramath.clamp(eq_band_q, 0, 1)

                    band_shape = 0
                    if eq_band_shape == 'low_pass': band_shape = 1
                    if eq_band_shape == 'band_pass': band_shape = 2
                    if eq_band_shape == 'high_pass': band_shape = 3
                    if eq_band_shape == 'notch': band_shape = 4
                    if eq_band_shape == 'low_shelf': band_shape = 5
                    if eq_band_shape == 'peak': band_shape = 6
                    if eq_band_shape == 'high_shelf': band_shape = 7

                    cvpj_plugindata.param_add(bandstarttxt+'_gain', eq_band_gain*100, 'int', "")
                    cvpj_plugindata.param_add(bandstarttxt+'_freq', eq_band_freq*65536, 'int', "")
                    cvpj_plugindata.param_add(bandstarttxt+'_width', eq_band_q*65536, 'int', "")
                    cvpj_plugindata.param_add(bandstarttxt+'_type', band_shape, 'int', "")
            return True
