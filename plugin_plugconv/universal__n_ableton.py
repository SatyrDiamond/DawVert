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
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):

        if plugin_obj.plugin_subtype == 'Redux2':
            print('[plug-conv] Ableton to Universal: Redux2 > Bitcrush:',pluginid)
            plugtransform.transform('./data_plugts/ableton_univ.pltr', 'redux2', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'Limiter':
            print('[plug-conv] Ableton to Universal: Limiter > Limiter:',pluginid)
            plugtransform.transform('./data_plugts/ableton_univ.pltr', 'limiter', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'Gate':
            print('[plug-conv] Ableton to Universal: Gate > Gate:',pluginid)
            plugtransform.transform('./data_plugts/ableton_univ.pltr', 'gate', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'FilterEQ3':
            print('[plug-conv] Ableton to Universal: FilterEQ3 > 3 Band EQ:',pluginid)
            plugtransform.transform('./data_plugts/ableton_univ.pltr', 'filtereq3', convproj_obj, plugin_obj, pluginid, dv_config)

        if plugin_obj.plugin_subtype == 'Compressor2':
            comp_Model = plugin_obj.params.get('Model', 0).value
            modeldata = 'peak'
            if comp_Model == 1: modeldata = 'rms'
            if comp_Model != 2: 
                print('[plug-conv] Ableton to Universal: Compressor2 > Compressor:',pluginid)
                plugtransform.transform('./data_plugts/ableton_univ.pltr', 'compressor2_comp', convproj_obj, plugin_obj, pluginid, dv_config)
            else: 
                print('[plug-conv] Ableton to Universal: Compressor2 > Expander:',pluginid)
                plugtransform.transform('./data_plugts/ableton_univ.pltr', 'compressor2_expand', convproj_obj, plugin_obj, pluginid, dv_config)
            plugin_obj.datavals.add('mode', modeldata)
            return 1

        if plugin_obj.plugin_subtype == 'Eq8':
            print('[plug-conv] Ableton to Universal: EQ8 > EQ Bands:',pluginid)
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

        return 2