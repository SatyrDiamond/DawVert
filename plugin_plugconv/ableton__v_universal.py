# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import plugins
from functions import data_bytes
from functions import xtramath
from functions_tracks import auto_data

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['universal', None, None], ['native-ableton', None, 'ableton'], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()
        #print(plugintype[1])

        if plugintype[1] == 'Vibrato':
            print('[plug-conv] Amped to Ableton: Vibrato > Chorus2:',pluginid)  
            auto_data.del_plugin(cvpj_l, pluginid)
            amped_delayLfoDepth = cvpj_plugindata.param_get('delayLfoDepth', 0.15)[0]
            amped_delayLfoRateHz = cvpj_plugindata.param_get('delayLfoRateHz', 0.7585000000000001)[0]
            cvpj_plugindata.replace('native-ableton', 'Chorus2')
            cvpj_plugindata.param_add('Mode', 2, 'int', "")
            cvpj_plugindata.param_add('Width', 1, 'float', "")
            cvpj_plugindata.param_add('OutputGain', 1, 'float', "")
            cvpj_plugindata.param_add('DryWet', 1, 'float', "")
            cvpj_plugindata.param_add('Rate', amped_delayLfoRateHz, 'float', "")
            cvpj_plugindata.param_add('Amount', amped_delayLfoDepth/2, 'float', "")
            return True
            
        if plugintype[1] == 'Tremolo':
            print('[plug-conv] Amped to Ableton: Tremolo > AutoPan:',pluginid)  
            auto_data.del_plugin(cvpj_l, pluginid)
            amped_lfoADepth = cvpj_plugindata.param_get('lfoADepth', 0.15)[0]
            amped_lfoARateHz = cvpj_plugindata.param_get('lfoARateHz', 0.7585000000000001)[0]

            als_lfo_data = {
                "BeatQuantize": 2.0,
                "BeatRate": 4,
                "Frequency": amped_lfoARateHz,
                "IsOn": 1,
                "LfoAmount": amped_lfoADepth,
                "LfoInvert": 0,
                "LfoShape": 0.0,
                "NoiseWidth": 0.5,
                "Offset": 0.0,
                "Phase": 180.0,
                "Quantize": 0,
                "RateType": 0.0,
                "Spin": 0.0,
                "StereoMode": 0,
                "Type": 0
            }
            cvpj_plugindata.replace('native-ableton', 'AutoPan')
            cvpj_plugindata.dataval_add('lfo_data', als_lfo_data)
            return True