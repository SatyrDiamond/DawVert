# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv
from functions import data_bytes

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['midi', None, None], ['soundfont2', None, None], False, True
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json):
        if 'soundfont' in extra_json:
            print('[plug-conv] MIDI to SoundFont2:',pluginid)
            sffile = extra_json['soundfont']
            v_bank = plugin_obj.datavals.get('bank', 0)
            v_inst = plugin_obj.datavals.get('inst', 0)
            plugin_obj.replace('soundfont2', None)
            plugin_obj.datavals.add('bank', v_bank)
            plugin_obj.datavals.add('patch', v_inst)
            plugin_obj.datavals.add('file', sffile)
            return 1
        print('[plug-conv] No Soundfont Argument Defined:',pluginid)
        return 2