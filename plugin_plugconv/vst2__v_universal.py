# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import base64
import struct
import os
import math
import lxml.etree as ET

from functions import note_data
from functions import data_bytes
from functions import data_values
from functions import plugin_vst2
from functions import plugins
from functions_tracks import auto_data

from functions_plugparams import params_various_inst

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['universal', None, None], ['vst2', None, None], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):

        fxtype = plugintype[1]

        if fxtype == 'compressor':  
            print('[plug-conv] UniV to VST2: Compressor > Compressor:',pluginid)
            auto_data.del_plugin(cvpj_l, pluginid)
            comp_threshold = plugins.get_plug_param(cvpj_l, pluginid, 'threshold', 0)[0]
            comp_ratio = plugins.get_plug_param(cvpj_l, pluginid, 'ratio', 0)[0]
            comp_gain = plugins.get_plug_param(cvpj_l, pluginid, 'gain', 0)[0]
            comp_attack = plugins.get_plug_param(cvpj_l, pluginid, 'attack', 0)[0]
            comp_release = plugins.get_plug_param(cvpj_l, pluginid, 'release', 0)[0]
            comp_knee = plugins.get_plug_param(cvpj_l, pluginid, 'knee', 0)[0]
            comp_pregain = plugins.get_plug_param(cvpj_l, pluginid, 'pregain', 0)[0]
            comp_postgain = plugins.get_plug_param(cvpj_l, pluginid, 'postgain', 0)[0]

            x_compressor = ET.Element("state")
            x_compressor.set('valueTree', '<?xml version="1.0" encoding="UTF-8"?>\n<state width="400" height="328"/>')
            x_compressor.set('program', '0')
            params_various_inst.socalabs_addparam(x_compressor, "attack", comp_attack*1000)
            params_various_inst.socalabs_addparam(x_compressor, "release", comp_release*1000)
            params_various_inst.socalabs_addparam(x_compressor, "ratio", comp_ratio)
            params_various_inst.socalabs_addparam(x_compressor, "threshold", comp_threshold)
            params_various_inst.socalabs_addparam(x_compressor, "knee", comp_knee)
            params_various_inst.socalabs_addparam(x_compressor, "input", comp_pregain)
            params_various_inst.socalabs_addparam(x_compressor, "output", comp_postgain)
            plugin_vst2.replace_data(cvpj_l, pluginid, 'id','any', 1397515120, 'chunk', ET.tostring(x_compressor, encoding='utf-8'), None)
            return True

        if fxtype == 'expander':  
            print('[plug-conv] UniV to VST2: Expander > Expander:',pluginid)
            auto_data.del_plugin(cvpj_l, pluginid)
            comp_threshold = plugins.get_plug_param(cvpj_l, pluginid, 'threshold', 0)[0]
            comp_ratio = plugins.get_plug_param(cvpj_l, pluginid, 'ratio', 0)[0]
            comp_gain = plugins.get_plug_param(cvpj_l, pluginid, 'gain', 0)[0]
            comp_attack = plugins.get_plug_param(cvpj_l, pluginid, 'attack', 0)[0]
            comp_release = plugins.get_plug_param(cvpj_l, pluginid, 'release', 0)[0]
            comp_knee = plugins.get_plug_param(cvpj_l, pluginid, 'knee', 0)[0]
            comp_pregain = plugins.get_plug_param(cvpj_l, pluginid, 'pregain', 0)[0]
            comp_postgain = plugins.get_plug_param(cvpj_l, pluginid, 'postgain', 0)[0]

            x_compressor = ET.Element("state")
            x_compressor.set('valueTree', '<?xml version="1.0" encoding="UTF-8"?>\n<state width="400" height="328"/>')
            x_compressor.set('program', '0')
            params_various_inst.socalabs_addparam(x_compressor, "attack", comp_attack*2000)
            params_various_inst.socalabs_addparam(x_compressor, "release", comp_release*2000)
            params_various_inst.socalabs_addparam(x_compressor, "ratio", comp_ratio)
            params_various_inst.socalabs_addparam(x_compressor, "threshold", comp_threshold)
            params_various_inst.socalabs_addparam(x_compressor, "knee", comp_knee)
            params_various_inst.socalabs_addparam(x_compressor, "input", comp_pregain)
            params_various_inst.socalabs_addparam(x_compressor, "output", comp_postgain)
            plugin_vst2.replace_data(cvpj_l, pluginid, 'id','any', 1397515640, 'chunk', ET.tostring(x_compressor, encoding='utf-8'), None)
            return True