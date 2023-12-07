# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import plugins
from functions import xtramath
from functions_tracks import auto_data

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['universal', None, None], False, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == 'fruity parametric eq 2':
            main_lvl = cvpj_plugindata.param_get('main_lvl', 0)[0]/100

            for bandnum in range(7):
                bandstarttxt = str(bandnum+1)

                fl_band_gain = cvpj_plugindata.param_get(bandstarttxt+'_gain', 0)[0]/100
                fl_band_freq = cvpj_plugindata.param_get(bandstarttxt+'_freq', 0)[0]/65536
                fl_band_width = cvpj_plugindata.param_get(bandstarttxt+'_width', 0)[0]/65536
                fl_band_type = cvpj_plugindata.param_get(bandstarttxt+'_type', 0)[0]

                fl_band_freq = 20 * 1000**fl_band_freq

                c_band_shape = 'peak'
                c_band_enable = 0

                if fl_band_type in [5, 7]: eq_res = (1-fl_band_width)*1.2
                elif fl_band_type in [1, 3]: 
                    fl_band_width = xtramath.between_from_one(1, -1, fl_band_width)
                    fl_band_width = pow(2, fl_band_width*10)
                else: 
                    fl_band_width = fl_band_width*4

                if fl_band_type != 0: c_band_enable = 1
                if fl_band_type == 1: c_band_shape = 'low_pass'
                if fl_band_type == 2: c_band_shape = 'band_pass'
                if fl_band_type == 3: c_band_shape = 'high_pass'
                if fl_band_type == 4: c_band_shape = 'notch'
                if fl_band_type == 5: c_band_shape = 'low_shelf'
                if fl_band_type == 6: c_band_shape = 'peak'
                if fl_band_type == 7: c_band_shape = 'high_shelf'

                cvpj_plugindata.eqband_add(c_band_enable, fl_band_freq, c_band_shape, None)
                cvpj_plugindata.eqband_add_param('q', fl_band_width, None)
                cvpj_plugindata.eqband_add_param('gain', fl_band_gain, None)

            cvpj_plugindata.replace('universal', 'eq-bands')
            cvpj_plugindata.param_add('gain_out', main_lvl, 'float', 'Out Gain')
