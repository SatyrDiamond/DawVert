# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import os
import lxml.etree as ET

from functions_tracks import auto_data

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['native-ableton', None, 'ableton'], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == None: plugintype[1] = ''
    
        if plugintype[1].lower() == 'fruity balance':  
            print('[plug-conv] FL Studio to Ableton: Fruity Balance > StereoGain:',pluginid)
            auto_data.del_plugin(cvpj_l, pluginid)
            bal_pan = cvpj_plugindata.param_get('pan', 0)[0]
            bal_vol = cvpj_plugindata.param_get('vol', 256)[0]

            cvpj_plugindata.replace('native-ableton', 'StereoGain')

            cvpj_plugindata.param_add('PhaseInvertL', False, 'bool', "")
            cvpj_plugindata.param_add('PhaseInvertR', False, 'bool', "")
            cvpj_plugindata.param_add('ChannelMode', 1, 'int', "")
            cvpj_plugindata.param_add('StereoWidth', 1, 'float', "")
            cvpj_plugindata.param_add('MidSideBalance', 1, 'float', "")
            cvpj_plugindata.param_add('Mono', False, 'bool', "")
            cvpj_plugindata.param_add('BassMono', False, 'bool', "")
            cvpj_plugindata.param_add('BassMonoFrequency', 120, 'float', "")
            cvpj_plugindata.param_add('Balance', bal_pan/128, 'float', "")
            cvpj_plugindata.param_add('Gain', 0, 'float', "")
            cvpj_plugindata.param_add('LegacyGain', ((bal_vol/256)-1)*35, 'float', "")
            cvpj_plugindata.param_add('Mute', False, 'bool', "")
            cvpj_plugindata.param_add('DcFilter', False, 'bool', "")
            return True

        if plugintype[1].lower() == 'fruity convolver':  
            print('[plug-conv] FL Studio to Ableton: Fruity convolver > Hybrid:',pluginid)
            auto_data.del_plugin(cvpj_l, pluginid)
            conv_file = cvpj_plugindata.dataval_get('file', 0)
            cvpj_plugindata.replace('native-ableton', 'Hybrid')
            cvpj_plugindata.dataval_get('sample', conv_file)
            return True
