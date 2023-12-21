# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from functions import plugin_vst2

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['simple', None], ['vst2'], None
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json, extplugtype):
        plugintype = cvpj_plugindata.type_get()
        fx_on, fx_wet = cvpj_plugindata.fxdata_get()

        if plugintype[1] == 'reverb' and extplugtype == 'vst2':
            print('[plug-conv] SimpleFX to VST2: Reverb > Airwindows Reverb:',pluginid)
            cvpj_plugindata.fxdata_add(fx_on, 1)
            plugin_vst2.replace_data(cvpj_plugindata, 'name','any', 'Reverb', 'chunk', struct.pack('<ff', 0.5, fx_wet), None)
            return True

        elif plugintype[1] == 'chorus' and extplugtype == 'vst2':
            cvpj_plugindata.fxdata_add(fx_on, 1)
            print('[plug-conv] SimpleFX to VST2: Chorus > Airwindows ChorusEnsemble:',pluginid)
            plugin_vst2.replace_data(cvpj_plugindata, 'name','any', 'ChorusEnsemble', 'chunk', struct.pack('<fff', 0.5, 0.5, fx_wet), None)
            return True
    
        elif plugintype[1] == 'tremelo' and extplugtype == 'vst2':
            print('[plug-conv] SimpleFX to VST2: Tremelo > Airwindows Tremolo:',pluginid)
            plugin_vst2.replace_data(cvpj_plugindata, 'name','any', 'Tremolo', 'chunk', struct.pack('<ff', 0.5, 0.5), None)
            return True

        elif plugintype[1] == 'distortion' and extplugtype == 'vst2':
            cvpj_plugindata.fxdata_add(fx_on, 1)
            amount = cvpj_plugindata.param_get('amount', 0)[0]
            print('[plug-conv] SimpleFX to VST2: Tremelo > Airwindows Drive:',pluginid)
            plugin_vst2.replace_data(cvpj_plugindata, 'name','any', 'Drive', 'chunk', struct.pack('<ffff', amount, 0, 1-(amount/2), fx_wet), None)
            return True

        elif plugintype[1] == 'bassboost' and extplugtype == 'vst2':
            print('[plug-conv] SimpleFX to VST2: BassBoost > Airwindows Weight:',pluginid)
            plugin_vst2.replace_data(cvpj_plugindata, 'name','any', 'Weight', 'param', None, 2)
            cvpj_plugindata.param_add('ext_param_0', 1, 'float', "Freq")
            cvpj_plugindata.param_add('ext_param_1', 1, 'float', "Weight")
            return True

        else: return False