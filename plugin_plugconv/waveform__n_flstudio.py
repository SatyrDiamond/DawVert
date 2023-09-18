# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import plugins
from functions import tracks

def getparam(paramname):
    global pluginid_g
    global cvpj_l_g
    paramval = plugins.get_plug_param(cvpj_l_g, pluginid_g, paramname, 0)
    return paramval[0]

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['native-tracktion', None, 'waveform_edit'], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):

        if plugintype[1] == None: plugintype[1] = ''
    
        if plugintype[1].lower() == 'fruity balance':  
            print('[plug-conv] FL Studio to Waveform: Fruity Balance > Volume:',pluginid)
            tracks.a_del_auto_plugin(cvpj_l, pluginid)
            bal_pan = plugins.get_plug_param(cvpj_l, pluginid, 'pan', 0)[0]
            bal_vol = plugins.get_plug_param(cvpj_l, pluginid, 'vol', 256)[0]
            plugins.replace_plug(cvpj_l, pluginid, 'native-tracktion', 'volume')
            plugins.add_plug_param(cvpj_l, pluginid, 'volume', (bal_vol/256), 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'pan', (bal_pan/128), 'float', "")
            return True
