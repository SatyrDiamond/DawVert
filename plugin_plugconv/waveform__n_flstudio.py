# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['native-tracktion', None, 'waveform_edit'], True, False
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json):
        if plugin_obj.plugin_subtype == None: plugin_obj.plugin_subtype = ''
    
        if plugin_obj.plugin_subtype.lower() == 'fruity balance':  
            print('[plug-conv] FL Studio to Waveform: Fruity Balance > Volume:',pluginid)
            bal_pan = plugin_obj.datavals.get('pan', 0)[0]
            bal_vol = plugin_obj.datavals.get('vol', 256)[0]
            plugin_obj.replace('native-tracktion', 'volume')
            plugin_obj.params.add('volume', (bal_vol/256), 'float', "")
            plugin_obj.params.add('pan', (bal_pan/128), 'float', "")
            return 1
            
        return 2
