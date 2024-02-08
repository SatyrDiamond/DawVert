# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import xtramath

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json):
        if plugin_obj.plugin_subtype == 'fruity parametric eq 2':
            print('[plug-conv] FL Studio to Universal: Fruity Parametric EQ 2 > EQ Bands:',pluginid)
            main_lvl = plugin_obj.params.get('main_lvl', 0).value/100

            for bandnum in range(7):
                bandstarttxt = str(bandnum+1)

                filter_obj = plugin_obj.eq_add()
                filter_obj.type = 'peak'

                filter_obj.gain = plugin_obj.params.get(bandstarttxt+'_gain', 0).value/100

                fl_band_freq = plugin_obj.params.get(bandstarttxt+'_freq', 0).value/65536
                filter_obj.freq = 20 * 1000**fl_band_freq

                fl_band_type = plugin_obj.params.get(bandstarttxt+'_type', 0).value
                fl_band_width = plugin_obj.params.get(bandstarttxt+'_width', 0).value/65536

                filter_obj.type = 'peak'

                if fl_band_type in [5, 7]: 
                    filter_obj.q = (1-fl_band_width)*1.2
                elif fl_band_type in [1, 3]: 
                    fl_band_width = xtramath.between_from_one(1, -1, fl_band_width)
                    filter_obj.q = pow(2, fl_band_width*5)
                else: 
                    outwid = ((fl_band_width+0.01)*3)
                    outwid = xtramath.logpowmul(outwid, -1)
                    filter_obj.q = outwid

                if fl_band_type != 0: filter_obj.on = True
                if fl_band_type == 1: filter_obj.type = 'low_pass'
                if fl_band_type == 2: filter_obj.type = 'band_pass'
                if fl_band_type == 3: filter_obj.type = 'high_pass'
                if fl_band_type == 4: filter_obj.type = 'notch'
                if fl_band_type == 5: filter_obj.type = 'low_shelf'
                if fl_band_type == 6: filter_obj.type = 'peak'
                if fl_band_type == 7: filter_obj.type = 'high_shelf'

            plugin_obj.replace('universal', 'eq-bands')
            param_obj = plugin_obj.params.add('gain_out', main_lvl, 'float')
            return 1

        return 2