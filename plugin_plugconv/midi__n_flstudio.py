# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import xtramath

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['midi', None, None], False, True
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):
        flpluginname = plugin_obj.plugin_subtype.lower()

        if flpluginname == 'boobass':
            print('[plug-conv] FL Studio to MIDI: BooBass > Electric Bass (finger):',pluginid)
            if not dv_config.path_soundfont_gm:
                plugin_obj.replace('midi', None)
                plugin_obj.datavals.add('bank', 0)
                plugin_obj.datavals.add('patch', 33)
                plugin_obj.datavals.add('is_drum', False)
                print('[plug-conv] No Soundfont Argument Defined:',pluginid)
            else:
                sf2_path = dv_config.path_soundfont_gm
                plugin_obj.replace('soundfont2', None)
                plugin_obj.datavals.add('bank', 0)
                plugin_obj.datavals.add('patch', 33)
                convproj_obj.add_fileref(sf2_path, sf2_path)
                plugin_obj.filerefs['file'] = sf2_path
            return 1

        return 2