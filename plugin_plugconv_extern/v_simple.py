# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from functions_plugin_ext import plugin_vst2

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['simple', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json, extplugtype):
        fx_on, fx_wet = plugin_obj.fxdata_get()

        if plugin_obj.plugin_subtype == 'reverb' and extplugtype == 'vst2':
            print('[plug-conv] SimpleFX to VST2: Reverb > Airwindows Reverb:',pluginid)
            plugin_obj.fxdata_add(fx_on, 1)
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name','any', 'Reverb', 'chunk', struct.pack('<ff', 0.5, fx_wet), None)
            return True

        elif plugin_obj.plugin_subtype == 'chorus' and extplugtype == 'vst2':
            plugin_obj.fxdata_add(fx_on, 1)
            print('[plug-conv] SimpleFX to VST2: Chorus > Airwindows ChorusEnsemble:',pluginid)
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name','any', 'ChorusEnsemble', 'chunk', struct.pack('<fff', 0.5, 0.5, fx_wet), None)
            return True
    
        elif plugin_obj.plugin_subtype == 'tremelo' and extplugtype == 'vst2':
            print('[plug-conv] SimpleFX to VST2: Tremelo > Airwindows Tremolo:',pluginid)
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name','any', 'Tremolo', 'chunk', struct.pack('<ff', 0.5, 0.5), None)
            return True

        elif plugin_obj.plugin_subtype == 'distortion' and extplugtype == 'vst2':
            plugin_obj.fxdata_add(fx_on, 1)
            amount = plugin_obj.params.get('amount', 0).value
            print('[plug-conv] SimpleFX to VST2: Tremelo > Airwindows Drive:',pluginid)
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name','any', 'Drive', 'chunk', struct.pack('<ffff', amount, 0, 1-(amount/2), fx_wet), None)
            return True

        elif plugin_obj.plugin_subtype == 'bassboost' and extplugtype == 'vst2':
            print('[plug-conv] SimpleFX to VST2: BassBoost > Airwindows Weight:',pluginid)
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name','any', 'Weight', 'param', None, 2)
            plugin_obj.params.add('ext_param_0', 1, 'float', "Freq")
            plugin_obj.params.add('ext_param_1', 1, 'float', "Weight")
            return True

        else: return False