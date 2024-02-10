# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

from functions_plugin_ext import params_os_juicysfplugin

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['soundfont2', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json, extplugtype):
        if extplugtype == 'vst2':
            print('[plug-conv] SoundFont2 > juicysfplugin:',pluginid)
            sf2_bank = plugin_obj.datavals.get('bank', 0)
            sf2_patch = plugin_obj.datavals.get('patch', 0)
            ref_found, fileref_obj = plugin_obj.get_fileref('file', convproj_obj)
            sf2_filename = fileref_obj.get_path(None, True) if ref_found else ''
            jsf2data = params_os_juicysfplugin.juicysfplugin_data()
            jsf2data.set_bankpatch(sf2_bank, sf2_patch, sf2_filename)
            jsf2data.to_cvpj_vst2(convproj_obj, plugin_obj)
            return True