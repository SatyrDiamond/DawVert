# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import struct
from functions import plugin_vst2

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['simple', None, None], ['vst2', None, None], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):

        if plugintype[1] == 'reverb': 
            print('[plug-conv] Converting Simple Reverb to Airwindows Reverb:',pluginid)
            plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Reverb', 'chunk', struct.pack('<ff', 0.5, 0.5), None)
            return True
        elif plugintype[1] == 'reverb-send': 
            print('[plug-conv] Converting Simple Reverb (Send) to Airwindows Reverb:',pluginid)
            plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Reverb', 'chunk', struct.pack('<ff', 0.5, 1), None)
            return True

        elif plugintype[1] == 'chorus': 
            print('[plug-conv] Converting Simple Chorus to Airwindows ChorusEnsemble:',pluginid)
            plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'ChorusEnsemble', 'chunk', struct.pack('<fff', 0.5, 0.5, 0.5), None)
            return True
        elif plugintype[1] == 'chorus-send': 
            print('[plug-conv] Converting Simple Chorus (Send) to Airwindows ChorusEnsemble:',pluginid)
            plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'ChorusEnsemble', 'chunk', struct.pack('<fff', 0.5, 0.5, 1), None)
            return True
    
        elif plugintype[1] == 'tremelo': 
            print('[plug-conv] Converting Simple Tremelo to Airwindows Tremolo:',pluginid)
            plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Tremolo', 'chunk', struct.pack('<ff', 0.5, 0.5), None)
            return True
        else: return False