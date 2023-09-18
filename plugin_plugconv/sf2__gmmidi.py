# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import plugins
from functions import data_bytes

class plugconv_vrc7_opl2(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['midi', None, None], ['soundfont2', None, None], False, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):
        if 'soundfont' in extra_json:
            print('[plug-conv] MIDI to SoundFont2:',pluginid)
            sffile = extra_json['soundfont']
            v_bank = plugins.get_plug_dataval(cvpj_l, pluginid, 'bank', 0)
            v_inst = plugins.get_plug_dataval(cvpj_l, pluginid, 'inst', 0)
            plugins.replace_plug(cvpj_l, pluginid, 'soundfont2', None)
            plugins.add_plug_data(cvpj_l, pluginid, 'bank', v_bank)
            plugins.add_plug_data(cvpj_l, pluginid, 'patch', v_inst)
            plugins.add_plug_data(cvpj_l, pluginid, 'file', sffile)
            return True
        print('[plug-conv] No Soundfont Argument Defined:',pluginid)
        return False