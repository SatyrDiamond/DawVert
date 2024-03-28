# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from functions_plugin_ext import params_os_airwindows
from functions_plugin_ext import plugin_vst2
from functions import errorprint

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['simple', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype, plugtransform):
        fx_on, fx_wet = plugin_obj.fxdata_get()

        if plugin_obj.plugin_subtype == 'reverb' and 'vst2' in extplugtype:
            if plugin_vst2.check_exists('id', 1919252066):
                print('[plug-conv] SimpleFX to VST2: Reverb > Reverb [Airwindows]:',pluginid)
                plugin_obj.fxdata_add(fx_on, 1)
                airwindows_obj = params_os_airwindows.airwindows_data()
                airwindows_obj.paramvals = [0.5, fx_wet]
                airwindows_obj.paramnames = ["Big","Wet"]
                airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1919252066, True, True)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'Reverb [Airwindows]'])

        elif plugin_obj.plugin_subtype == 'chorus' and 'vst2' in extplugtype:
            if plugin_vst2.check_exists('id', 1935894643):
                print('[plug-conv] SimpleFX to VST2: Chorus > Chorus [Airwindows]:',pluginid)
                airwindows_obj = params_os_airwindows.airwindows_data()
                airwindows_obj.paramvals = [0.5, plugin_obj.params.get('amount', 0).value/2.5, 1]
                airwindows_obj.paramnames = ["Speed","Range","Dry/Wet"]
                airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1935894643, True, True)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'StereoChorus [Airwindows]'])

        elif plugin_obj.plugin_subtype == 'tremelo' and 'vst2' in extplugtype:
            if plugin_vst2.check_exists('id', 1953654125):
                print('[plug-conv] SimpleFX to VST2: Tremelo > Tremolo [Airwindows]:',pluginid)
                airwindows_obj = params_os_airwindows.airwindows_data()
                airwindows_obj.paramvals = [0.5, 0.5]
                airwindows_obj.paramnames = ["Speed","Depth"]
                airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1953654125, True, True)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'Tremolo [Airwindows]'])

        elif plugin_obj.plugin_subtype == 'distortion' and 'vst2' in extplugtype:
            if plugin_vst2.check_exists('id', 1685219702):
                print('[plug-conv] SimpleFX to VST2: Distortion > Drive [Airwindows]:',pluginid)
                plugin_obj.fxdata_add(fx_on, 1)
                amount = plugin_obj.params.get('amount', 0).value
                airwindows_obj = params_os_airwindows.airwindows_data()
                airwindows_obj.paramvals = [amount, 0, 1-(amount/2), fx_wet]
                airwindows_obj.paramnames = ["Drive","Highpass","Out Level","Dry/Wet"]
                airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1685219702, True, True)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'Drive [Airwindows]'])

        elif plugin_obj.plugin_subtype == 'bassboost' and 'vst2' in extplugtype:
            if plugin_vst2.check_exists('id', 2003265652):
                print('[plug-conv] SimpleFX to VST2: BassBoost > Weight [Airwindows]:',pluginid)
                airwindows_obj = params_os_airwindows.airwindows_data()
                airwindows_obj.paramvals = [1, 1]
                airwindows_obj.paramnames = ["Freq","Weight"]
                airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 2003265652, False, True)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'Weight [Airwindows]'])

        else: return False