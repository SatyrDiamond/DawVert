# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from functions import plugin_vst2

from functions_tracks import auto_data

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['native-onlineseq', None], ['vst2']
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json, extplugtype):
        plugintype = cvpj_plugindata.type_get()
        
        if plugintype[1] == 'distort' and extplugtype == 'vst2':
            print('[plug-conv] Online Sequencer to VST2: Distortion > Airwindows Density2:',pluginid)
            distlevel = 0.5
            distort_type = cvpj_plugindata.param_get('distort_type', 0)[0]
            if distort_type == [10, 6]: distlevel = 0.3
            plugin_vst2.replace_data(cvpj_plugindata, 'name','any', 'Density2', 'chunk', struct.pack('<ffff', distlevel, 0, 1, 1), None)
            return True

        elif plugintype[1] == 'eq' and extplugtype == 'vst2':
            print('[plug-conv] Online Sequencer to VST2: EQ > 3 Band EQ:',pluginid)
            eq_low = cvpj_plugindata.param_get('eq_low', 0)[0]
            eq_mid = cvpj_plugindata.param_get('eq_mid', 0)[0]
            eq_high = cvpj_plugindata.param_get('eq_high', 0)[0]
            plugin_vst2.replace_data(cvpj_plugindata, 'name','any', '3 Band EQ', 'param', None, 6)
            cvpj_plugindata.param_add('ext_param_0', (eq_high/96)+0.5, 'float', "Low")
            cvpj_plugindata.param_add('ext_param_1', (eq_mid/96)+0.5, 'float', "Mid")
            cvpj_plugindata.param_add('ext_param_2', (eq_high/96)+0.5, 'float', "High")
            cvpj_plugindata.param_add('ext_param_3', 0.5, 'float', "Master")
            cvpj_plugindata.param_add('ext_param_4', 0.22, 'float', "Low-Mid Freq")
            cvpj_plugindata.param_add('ext_param_5', 0.3, 'float', "Mid-High Freq")

            auto_data.to_ext_one(cvpj_l, pluginid, 'eq_low', 'ext_param_0', -96, 96)
            auto_data.to_ext_one(cvpj_l, pluginid, 'eq_mid', 'ext_param_1', -96, 96)
            auto_data.to_ext_one(cvpj_l, pluginid, 'eq_high', 'ext_param_2', -96, 96)
            return True

        else: return False