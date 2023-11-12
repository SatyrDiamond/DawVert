# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import lxml.etree as ET
from functions_tracks import auto_data
from functions_plugdata import plugin_socalabs

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['universal', None, None], ['vst2', None, None], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        fxtype = plugintype[1]

        if fxtype == 'compressor':
            print('[plug-conv] UniV to VST2: Compressor > Compressor:',pluginid)
            auto_data.del_plugin(cvpj_l, pluginid)

            data_socalabs = plugin_socalabs.socalabs_data(cvpj_plugindata)
            data_socalabs.set_param("attack", cvpj_plugindata.param_get('attack', 0)[0]*1000)
            data_socalabs.set_param("release", cvpj_plugindata.param_get('release', 0)[0]*1000)
            data_socalabs.set_param("ratio", cvpj_plugindata.param_get('ratio', 0)[0])
            data_socalabs.set_param("threshold", cvpj_plugindata.param_get('threshold', 0)[0])
            data_socalabs.set_param("knee", cvpj_plugindata.param_get('knee', 0)[0])
            data_socalabs.set_param("input", cvpj_plugindata.param_get('pregain', 0)[0])
            data_socalabs.set_param("output", cvpj_plugindata.param_get('postgain', 0)[0])
            data_socalabs.to_cvpj_vst2(cvpj_plugindata, 1397515120)
            return True

        if fxtype == 'expander':  
            print('[plug-conv] UniV to VST2: Expander > Expander:',pluginid)
            auto_data.del_plugin(cvpj_l, pluginid)

            data_socalabs = plugin_socalabs.socalabs_data(cvpj_plugindata)
            data_socalabs.set_param("attack", cvpj_plugindata.param_get('attack', 0)[0]*2000)
            data_socalabs.set_param("release", cvpj_plugindata.param_get('release', 0)[0]*2000)
            data_socalabs.set_param("ratio", cvpj_plugindata.param_get('ratio', 0)[0])
            data_socalabs.set_param("threshold", cvpj_plugindata.param_get('threshold', 0)[0])
            data_socalabs.set_param("knee", cvpj_plugindata.param_get('knee', 0)[0])
            data_socalabs.set_param("input", cvpj_plugindata.param_get('pregain', 0)[0])
            data_socalabs.set_param("output", cvpj_plugindata.param_get('postgain', 0)[0])
            data_socalabs.to_cvpj_vst2(cvpj_plugindata, 1397515640)
            return True