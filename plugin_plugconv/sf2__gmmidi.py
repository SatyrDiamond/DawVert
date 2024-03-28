# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv
from functions import data_bytes

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['midi', None, None], ['soundfont2', None, None], False, True
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):
        if dv_config.path_soundfont_gm:
            print('[plug-conv] MIDI to SoundFont2:',pluginid)
            sf2_path = dv_config.path_soundfont_gm
            v_drums = plugin_obj.datavals.get('is_drum', False)
            v_bank = plugin_obj.datavals.get('bank', 0)
            v_inst = plugin_obj.datavals.get('patch', 1)-1
            plugin_obj.replace('soundfont2', None)
            plugin_obj.datavals.add('bank', v_bank if not v_drums else 128)
            plugin_obj.datavals.add('patch', v_inst+1)
            convproj_obj.add_fileref(sf2_path, sf2_path)
            plugin_obj.filerefs['file'] = sf2_path
            return 1
        print('[plug-conv] No Soundfont Argument Defined:',pluginid)
        return 2