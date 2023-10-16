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
    def getplugconvinfo(self): return ['universal', None, None], ['native-flstudio', None, 'flp'], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):
        global pluginid_g   
        global cvpj_l_g 
        pluginid_g = pluginid   
        cvpj_l_g = cvpj_l

        if plugintype[1] == 'eq-bands':  
            plugins.replace_plug(cvpj_l, pluginid, 'native-flstudio', 'fruity parametric eq 2')

            banddata = plugins.get_eqband(cvpj_l, pluginid, None)

            bandnum = 0
            for s_band in banddata:
                bandtype = s_band['type']

                band_on = s_band['on']
                band_freq = s_band['freq']
                band_gain = s_band['gain']
                band_res = s_band['var']

                part = [True, band_on, band_freq, band_gain, band_res]

                band_shape = 0
                if band_on == 1: 
                    if bandtype == 'low_pass': band_shape = 1
                    if bandtype == 'band_pass': band_shape = 2
                    if bandtype == 'high_pass': band_shape = 3
                    if bandtype == 'notch': band_shape = 4
                    if bandtype == 'low_shelf': band_shape = 5
                    if bandtype == 'peak': band_shape = 6
                    if bandtype == 'high_shelf': band_shape = 7

                    band_freq = math.log(band_freq / 20) / math.log(1000)

                    if band_on == 1:
                        bandstarttxt = str(bandnum+1)
                        plugins.add_plug_param(cvpj_l, pluginid, bandstarttxt+'_gain', band_gain*100, 'int', "")
                        plugins.add_plug_param(cvpj_l, pluginid, bandstarttxt+'_freq', band_freq*65536, 'int', "")
                        plugins.add_plug_param(cvpj_l, pluginid, bandstarttxt+'_width', ((math.sqrt(band_res)/5)*65536)*2, 'int', "")
                        plugins.add_plug_param(cvpj_l, pluginid, bandstarttxt+'_type', band_shape, 'int', "")
                        bandnum += 1