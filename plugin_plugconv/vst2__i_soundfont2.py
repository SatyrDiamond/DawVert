# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import plugin_vst2
from functions import plugins
from functions_plugparams import data_vc2xml
from functions_plugparams import params_various_inst

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['soundfont2', None, None], ['vst2', None, None], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):
        print('[plug-conv] Converting SF2 to juicysfplugin:',pluginid)
        sf2_bank = plugins.get_plug_dataval(cvpj_l, pluginid, 'bank', 0)
        sf2_patch = plugins.get_plug_dataval(cvpj_l, pluginid, 'patch', 0)
        sf2_filename = plugins.get_plug_dataval(cvpj_l, pluginid, 'file', 0)
        jsfp_xml = params_various_inst.juicysfplugin_create(sf2_bank, sf2_patch, sf2_filename)
        plugin_vst2.replace_data(cvpj_l, pluginid, 'name','any', 'juicysfplugin', 'chunk', data_vc2xml.make(jsfp_xml), None)
        return True