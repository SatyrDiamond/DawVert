# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import xtramath

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-amped', None, 'amped'], ['native-ableton', None, 'ableton'], True, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):

        if plugin_obj.plugin_subtype == 'Chorus':
            print('[plug-conv] Amped to Ableton: Chorus > Chorus2:',pluginid)  
            amped_delayLfoDepth = plugin_obj.params.get('delayLfoDepth', 0.15).value
            amped_delayLfoRateHz = plugin_obj.params.get('delayLfoRateHz', 0.7585000000000001).value
            amped_mix = plugin_obj.params.get('mix', 0.85).value
            amped_tone = plugin_obj.params.get('tone', 0.2).value
            cvpj_plugindata.replace('native-ableton', 'Chorus2')
            plugin_obj.params.add('Rate', amped_delayLfoRateHz, 'float')
            plugin_obj.params.add('DryWet', amped_mix, 'float')
            plugin_obj.params.add('Amount', xtramath.clamp(amped_delayLfoDepth*2,0,1), 'float')
            plugin_obj.params.add('Mode', 0, 'int')
            plugin_obj.params.add('Width', 1, 'float')
            plugin_obj.params.add('OutputGain', 1, 'float')
            return 0

        if plugin_obj.plugin_subtype == 'Phaser':
            print('[plug-conv] Amped to Ableton: Phaser > PhaserNew:',pluginid)  
            amped_feedback = plugin_obj.params.get('feedback', 0.0).value
            amped_hzmin = plugin_obj.params.get('hzmin', 400.0).value
            amped_hzrange = plugin_obj.params.get('hzrange', 4.0).value
            amped_mix = plugin_obj.params.get('mix', 1.0).value
            amped_rate = plugin_obj.params.get('rate', 1.5).value
            amped_stages = plugin_obj.params.get('stages', 8.0).value
            cvpj_plugindata.replace('native-ableton', 'PhaserNew')
            plugin_obj.params.add('Feedback', amped_feedback/4, 'float')
            plugin_obj.params.add('CenterFrequency', amped_hzmin, 'float')
            plugin_obj.params.add('Spread', amped_hzrange/20, 'float')
            plugin_obj.params.add('DryWet', amped_mix, 'float')
            plugin_obj.params.add('Modulation_Frequency', amped_rate/2, 'float')
            plugin_obj.params.add('Notches', amped_stages, 'float')
            plugin_obj.params.add('Modulation_Amount', 0.20, 'float')
            plugin_obj.params.add('OutputGain', 1, 'float')
            return 0

        return 2