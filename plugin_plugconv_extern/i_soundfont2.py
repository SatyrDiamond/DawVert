# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

from functions_plugdata import plugin_juicysfplugin

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['soundfont2', None], ['vst2'], None
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json, extplugtype):
        if extplugtype == 'vst2':
            print('[plug-conv] SoundFont2 > juicysfplugin:',pluginid)
            sf2_bank = cvpj_plugindata.dataval_get('bank', 0)
            sf2_patch = cvpj_plugindata.dataval_get('patch', 0)
            sf2_filename = cvpj_plugindata.dataval_get('file', 0)
            jsf2data = plugin_juicysfplugin.juicysfplugin_data(cvpj_plugindata)
            jsf2data.set_bankpatch(sf2_bank, sf2_patch, sf2_filename)
            jsf2data.to_cvpj_vst2(cvpj_plugindata)
            return True