# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import xtramath
from functions_tracks import auto_data

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-amped', None, 'amped'], ['native-ableton', None, 'ableton'], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()
        #print(plugintype[1])

        if plugintype[1] == 'Chorus':
            print('[plug-conv] Amped to Ableton: Chorus > Chorus2:',pluginid)  
            auto_data.del_plugin(cvpj_l, pluginid)
            amped_delayLfoDepth = cvpj_plugindata.param_get('delayLfoDepth', 0.15)[0]
            amped_delayLfoRateHz = cvpj_plugindata.param_get('delayLfoRateHz', 0.7585000000000001)[0]
            amped_mix = cvpj_plugindata.param_get('mix', 0.85)[0]
            amped_tone = cvpj_plugindata.param_get('tone', 0.2)[0]
            cvpj_plugindata.replace('native-ableton', 'Chorus2')
            cvpj_plugindata.param_add('Rate', amped_delayLfoRateHz, 'float', "")
            cvpj_plugindata.param_add('DryWet', amped_mix, 'float', "")
            cvpj_plugindata.param_add('Amount', xtramath.clamp(amped_delayLfoDepth*2,0,1), 'float', "")
            cvpj_plugindata.param_add('Mode', 0, 'int', "")
            cvpj_plugindata.param_add('Width', 1, 'float', "")
            cvpj_plugindata.param_add('OutputGain', 1, 'float', "")
            return 0

        if plugintype[1] == 'Phaser':
            print('[plug-conv] Amped to Ableton: Phaser > PhaserNew:',pluginid)  
            auto_data.del_plugin(cvpj_l, pluginid)
            amped_feedback = cvpj_plugindata.param_get('feedback', 0.0)[0]
            amped_hzmin = cvpj_plugindata.param_get('hzmin', 400.0)[0]
            amped_hzrange = cvpj_plugindata.param_get('hzrange', 4.0)[0]
            amped_mix = cvpj_plugindata.param_get('mix', 1.0)[0]
            amped_rate = cvpj_plugindata.param_get('rate', 1.5)[0]
            amped_stages = cvpj_plugindata.param_get('stages', 8.0)[0]
            cvpj_plugindata.replace('native-ableton', 'PhaserNew')
            cvpj_plugindata.param_add('Feedback', amped_feedback/4, 'float', "")
            cvpj_plugindata.param_add('CenterFrequency', amped_hzmin, 'float', "")
            cvpj_plugindata.param_add('Spread', amped_hzrange/20, 'float', "")
            cvpj_plugindata.param_add('DryWet', amped_mix, 'float', "")
            cvpj_plugindata.param_add('Modulation_Frequency', amped_rate/2, 'float', "")
            cvpj_plugindata.param_add('Notches', amped_stages, 'float', "")
            cvpj_plugindata.param_add('Modulation_Amount', 0.20, 'float', "")
            cvpj_plugindata.param_add('OutputGain', 1, 'float', "")
            return 0

        return 2