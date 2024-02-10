# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from functions_plugin_ext import plugin_vst2

from objects import plugts

loaded_plugtransform = False

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['native-onlineseq', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json, extplugtype):
        global loaded_plugtransform
        global plugts_obj

        if loaded_plugtransform == False:
            plugts_obj = plugts.plugtransform()
            plugts_obj.load_file('./data_plugts/onlineseq_vst2.pltr')
            loaded_plugtransform = True

        if plugin_obj.plugin_subtype == 'distort' and extplugtype == 'vst2':
            print('[plug-conv] Online Sequencer to VST2: Distortion > Airwindows Density2:',pluginid)
            distlevel = 0.5
            distort_type = plugin_obj.params.get('distort_type', 0).value
            if distort_type == [10, 6]: distlevel = 0.3
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name','any','Density2','chunk',struct.pack('<ffff', distlevel, 0, 1, 1), None)
            return True

        elif plugin_obj.plugin_subtype == 'eq' and extplugtype == 'vst2':
            print('[plug-conv] Online Sequencer to VST2: EQ > 3 Band EQ:',pluginid)
            plugts_obj.transform('eq_vst2', convproj_obj, plugin_obj, pluginid, extra_json)
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name','any', '3 Band EQ', 'param', None, 6)
            return True

        else: return False