# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import base64
import struct
import os
import math

from functions import plugins
from functions_tracks import auto_data

def getparam(paramname):
    global pluginid_g
    global cvpj_l_g
    paramval = plugins.get_plug_param(cvpj_l_g, pluginid_g, paramname, 0)
    return paramval[0]

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-lmms', None, 'lmms'], ['native-flstudio', None, 'flp'], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):
        global pluginid_g   
        global cvpj_l_g 
        pluginid_g = pluginid   
        cvpj_l_g = cvpj_l

        print(plugintype[1])

        if plugintype[1] == 'stereomatrix':  
            print('[plug-conv] LMMS to FL Studio: Stereo Matrix > Fruity Stereo Shaper:',pluginid)

            fl_r_l = getparam('r-l')*12800
            fl_l_l = getparam('l-l')*12800
            fl_r_r = getparam('r-r')*12800
            fl_l_r = getparam('l-r')*12800

            plugins.replace_plug(cvpj_l, pluginid, 'native-flstudio', 'fruity stereo shaper')
            plugins.add_plug_param(cvpj_l, pluginid, 'r2l', fl_r_l, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'l2l', fl_l_l, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'r2r', fl_r_r, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'l2r', fl_l_r, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'delay', 0, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'dephase', 0, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'iodiff', 0, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'prepost', 0, 'int', "")
            return True

        if plugintype[1] == 'spectrumanalyzer':  
            print('[plug-conv] LMMS to FL Studio: Spectrum Analyzer > Fruity Spectroman:',pluginid)
            plugins.replace_plug(cvpj_l, pluginid, 'native-flstudio', 'fruity spectroman')
            plugins.add_plug_param(cvpj_l, pluginid, 'amp', 128, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'scale', 128, 'int', "")
            return True


