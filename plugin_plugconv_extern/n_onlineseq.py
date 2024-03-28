# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import params_os_airwindows

loaded_plugtransform = False

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['native-onlineseq', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype, plugtransform):

        if plugin_obj.plugin_subtype == 'distort' and 'vst2' in extplugtype:
            if plugin_vst2.check_exists('id', 1684368946):
                print('[plug-conv] Online Sequencer to VST2: Distortion > Density2 [Airwindows]:',pluginid)
                distort_type = plugin_obj.params.get('distort_type', 0).value
                if distort_type == [10, 6]: distlevel = 0.3
                else: distlevel = 0.5

                airwindows_obj = params_os_airwindows.airwindows_data()
                airwindows_obj.paramvals = [distlevel, 0, 1, 1]
                airwindows_obj.paramnames = ["Density","Highpass","Output","Dry/Wet"]
                airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1684368946, True, True)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'Density2 [Airwindows]'])

        else: return False