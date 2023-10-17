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
    def getplugconvinfo(self): return ['native-amped', None, 'amped'], ['native-ableton', None, 'ableton'], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):
        #print(plugintype[1])

        if plugintype[1] == 'Chorus':
            print('[plug-conv] Amped to Ableton: Chorus > Chorus2:',pluginid)  
            auto_data.del_plugin(cvpj_l, pluginid)
            amped_delayLfoDepth = plugins.get_plug_param(cvpj_l, pluginid, 'delayLfoDepth', 0.15)[0]
            amped_delayLfoRateHz = plugins.get_plug_param(cvpj_l, pluginid, 'delayLfoRateHz', 0.7585000000000001)[0]
            amped_mix = plugins.get_plug_param(cvpj_l, pluginid, 'mix', 0.85)[0]
            amped_tone = plugins.get_plug_param(cvpj_l, pluginid, 'tone', 0.2)[0]
            plugins.replace_plug(cvpj_l, pluginid, 'native-ableton', 'Chorus2')
            plugins.add_plug_param(cvpj_l, pluginid, 'Rate', amped_delayLfoRateHz, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'DryWet', amped_mix, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Amount', xtramath.clamp(amped_delayLfoDepth*2,0,1), 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Mode', 0, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Width', 1, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'OutputGain', 1, 'float', "")
            return True

        if plugintype[1] == 'Phaser':
            print('[plug-conv] Amped to Ableton: Phaser > PhaserNew:',pluginid)  
            auto_data.del_plugin(cvpj_l, pluginid)
            amped_feedback = plugins.get_plug_param(cvpj_l, pluginid, 'feedback', 0.0)[0]
            amped_hzmin = plugins.get_plug_param(cvpj_l, pluginid, 'hzmin', 400.0)[0]
            amped_hzrange = plugins.get_plug_param(cvpj_l, pluginid, 'hzrange', 4.0)[0]
            amped_mix = plugins.get_plug_param(cvpj_l, pluginid, 'mix', 1.0)[0]
            amped_rate = plugins.get_plug_param(cvpj_l, pluginid, 'rate', 1.5)[0]
            amped_stages = plugins.get_plug_param(cvpj_l, pluginid, 'stages', 8.0)[0]
            plugins.replace_plug(cvpj_l, pluginid, 'native-ableton', 'PhaserNew')
            plugins.add_plug_param(cvpj_l, pluginid, 'Feedback', amped_feedback/4, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'CenterFrequency', amped_hzmin, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Spread', amped_hzrange/20, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'DryWet', amped_mix, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Modulation_Frequency', amped_rate/2, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Notches', amped_stages, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Modulation_Amount', 0.20, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'OutputGain', 1, 'float', "")
            return True