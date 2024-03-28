# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import os
import math

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-lmms', None, 'lmms'], ['native-flstudio', None, 'flp'], True, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):
        
        if plugin_obj.plugin_subtype == 'stereomatrix':  
            print('[plug-conv] LMMS to FL Studio: Stereo Matrix > Fruity Stereo Shaper:',pluginid)

            fl_r_l = plugin_obj.params.get('r-l', 0).value*12800
            fl_l_l = plugin_obj.params.get('l-l', 0).value*12800
            fl_r_r = plugin_obj.params.get('r-r', 0).value*12800
            fl_l_r = plugin_obj.params.get('l-r', 0).value*12800
            plugin_obj.replace('native-flstudio', 'fruity stereo shaper')
            plugin_obj.params.add('r2l', fl_r_l, 'int')
            plugin_obj.params.add('l2l', fl_l_l, 'int')
            plugin_obj.params.add('r2r', fl_r_r, 'int')
            plugin_obj.params.add('l2r', fl_l_r, 'int')
            plugin_obj.params.add('delay', 0, 'int')
            plugin_obj.params.add('dephase', 0, 'int')
            plugin_obj.params.add('iodiff', 0, 'int')
            plugin_obj.params.add('prepost', 0, 'int')
            return 0

        if plugin_obj.plugin_subtype == 'spectrumanalyzer':  
            print('[plug-conv] LMMS to FL Studio: Spectrum Analyzer > Fruity Spectroman:',pluginid)
            plugin_obj.replace('native-flstudio', 'fruity spectroman')
            plugin_obj.params.add('amp', 128, 'int')
            plugin_obj.params.add('scale', 128, 'int')
            return 0

        if plugin_obj.plugin_subtype == 'stereoenhancer':  
            print('[plug-conv] LMMS to FL Studio: Stereo Enhancer > Fruity Stereo Enhancer:',pluginid)
            width = plugin_obj.params.get('width', 0).value
            plugin_obj.replace('native-flstudio', 'fruity stereo enhancer')
            plugin_obj.params.add('phase_offs', width, 'int') #512 = 500
            return 0

        return 2

