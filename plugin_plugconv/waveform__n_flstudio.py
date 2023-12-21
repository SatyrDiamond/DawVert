# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['native-tracktion', None, 'waveform_edit'], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == None: plugintype[1] = ''
    
        if plugintype[1].lower() == 'fruity balance':  
            print('[plug-conv] FL Studio to Waveform: Fruity Balance > Volume:',pluginid)
            bal_pan = cvpj_plugindata.dataval_get('pan', 0)[0]
            bal_vol = cvpj_plugindata.dataval_get('vol', 256)[0]
            cvpj_plugindata.replace('native-tracktion', 'volume')
            cvpj_plugindata.param_add('volume', (bal_vol/256), 'float', "")
            cvpj_plugindata.param_add('pan', (bal_pan/128), 'float', "")
            return 1
            
        return 2
