# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import plugins
from functions import idvals
from functions import xtramath
from functions import note_data
import math

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['universal', None, None], False, True
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):

        if 'nonfree-plugins' not in extra_json:
            if plugintype[1].lower() == 'fruity parametric eq 2': 

                main_lvl = plugins.get_plug_param(cvpj_l, pluginid, 'main_lvl', 0)[0]/100

                fl_eq_bands = []
                for bandnum in range(7):
                    bandstarttxt = str(bandnum+1)
                    band_gain = plugins.get_plug_param(cvpj_l, pluginid, bandstarttxt+'_gain', 0)[0]
                    band_freq = plugins.get_plug_param(cvpj_l, pluginid, bandstarttxt+'_freq', 0)[0]
                    band_width = plugins.get_plug_param(cvpj_l, pluginid, bandstarttxt+'_width', 0)[0]
                    band_type = plugins.get_plug_param(cvpj_l, pluginid, bandstarttxt+'_type', 0)[0]
                    band_freq /= 65536
                    fl_eq_bands.append([20 * 1000**band_freq, band_gain/100, (band_width/65536), band_type])

                plugins.replace_plug(cvpj_l, pluginid, 'universal', 'eq-bands')
                plugins.add_plug_data(cvpj_l, pluginid, 'num_bands', 7)
                plugins.add_plug_param(cvpj_l, pluginid, 'gain_out', main_lvl, 'float', 'Out Gain')

                for fl_eq_band in fl_eq_bands:
                    band_shape = 'peak'
                    band_enable = 0

                    if fl_eq_band[3] in [5, 7]: eq_res = (1-fl_eq_band[2])*1.2
                    elif fl_eq_band[3] in [1, 3]: 
                        eq_res = xtramath.between_from_one(1, -1, fl_eq_band[2])
                        eq_res = pow(2, eq_res*10)
                    else: 
                        eq_res = fl_eq_band[2]*4

                    if fl_eq_band[3] != 0: band_enable = 1
                    if fl_eq_band[3] == 1: band_shape = 'low_pass'
                    if fl_eq_band[3] == 2: band_shape = 'band_pass'
                    if fl_eq_band[3] == 3: band_shape = 'high_pass'
                    if fl_eq_band[3] == 4: band_shape = 'notch'
                    if fl_eq_band[3] == 5: band_shape = 'low_shelf'
                    if fl_eq_band[3] == 6: band_shape = 'peak'
                    if fl_eq_band[3] == 7: band_shape = 'high_shelf'
                    plugins.add_eqband(cvpj_l, pluginid, band_enable, fl_eq_band[0], fl_eq_band[1], band_shape, eq_res, None)

            return True
