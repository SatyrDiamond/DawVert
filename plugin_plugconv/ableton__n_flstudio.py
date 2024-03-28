# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import os
import lxml.etree as ET

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['native-ableton', None, 'ableton'], True, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):
        plugintype = plugin_obj.plugin_subtype

        if plugintype == 'fruity balance':  
            print('[plug-conv] FL Studio to Ableton: Fruity Balance > StereoGain:',pluginid)
            bal_pan = plugin_obj.params.get('pan', 0).value
            bal_vol = plugin_obj.params.get('vol', 256).value
            plugin_obj.replace('native-ableton', 'StereoGain')
            plugin_obj.params.add('PhaseInvertL', False, 'bool')
            plugin_obj.params.add('PhaseInvertR', False, 'bool')
            plugin_obj.params.add('ChannelMode', 1, 'int')
            plugin_obj.params.add('StereoWidth', 1, 'float')
            plugin_obj.params.add('MidSideBalance', 1, 'float')
            plugin_obj.params.add('Mono', False, 'bool')
            plugin_obj.params.add('BassMono', False, 'bool')
            plugin_obj.params.add('BassMonoFrequency', 120, 'float')
            plugin_obj.params.add('Balance', bal_pan/128, 'float')
            plugin_obj.params.add('Gain', 0, 'float')
            plugin_obj.params.add('LegacyGain', ((bal_vol/256)-1)*35, 'float')
            plugin_obj.params.add('Mute', False, 'bool')
            plugin_obj.params.add('DcFilter', False, 'bool')
            return 0

        #if plugin_obj.plugin_subtype.lower() == 'fruity convolver':  
        #    print('[plug-conv] FL Studio to Ableton: Fruity convolver > Hybrid:',pluginid)
        #    conv_file = cvpj_plugindata.dataval_get('file', 0)
        #    cvpj_plugindata.replace('native-ableton', 'Hybrid')
        #    cvpj_plugindata.dataval_get('sample', conv_file)
        #    return 0

        return 2