# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import base64
import struct
import os
import math

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-lmms', None, 'lmms'], ['native-flstudio', None, 'flp'], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == 'stereomatrix':  
            print('[plug-conv] LMMS to FL Studio: Stereo Matrix > Fruity Stereo Shaper:',pluginid)

            fl_r_l = cvpj_plugindata.param_get('r-l', 0)[0]*12800
            fl_l_l = cvpj_plugindata.param_get('l-l', 0)[0]*12800
            fl_r_r = cvpj_plugindata.param_get('r-r', 0)[0]*12800
            fl_l_r = cvpj_plugindata.param_get('l-r', 0)[0]*12800

            cvpj_plugindata.replace('native-flstudio', 'fruity stereo shaper')
            cvpj_plugindata.param_add('r2l', fl_r_l, 'int', "")
            cvpj_plugindata.param_add('l2l', fl_l_l, 'int', "")
            cvpj_plugindata.param_add('r2r', fl_r_r, 'int', "")
            cvpj_plugindata.param_add('l2r', fl_l_r, 'int', "")
            cvpj_plugindata.param_add('delay', 0, 'int', "")
            cvpj_plugindata.param_add('dephase', 0, 'int', "")
            cvpj_plugindata.param_add('iodiff', 0, 'int', "")
            cvpj_plugindata.param_add('prepost', 0, 'int', "")
            return True

        if plugintype[1] == 'spectrumanalyzer':  
            print('[plug-conv] LMMS to FL Studio: Spectrum Analyzer > Fruity Spectroman:',pluginid)
            cvpj_plugindata.replace('native-flstudio', 'fruity spectroman')
            cvpj_plugindata.param_add('amp', 128, 'int', "")
            cvpj_plugindata.param_add('scale', 128, 'int', "")
            return True


