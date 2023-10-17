# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import base64
import struct
import os
import math

from functions import plugins
from functions import xtramath
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
            main_lvl = plugins.get_plug_param(cvpj_l, pluginid, 'gain_out', 0)[0]*100
            plugins.replace_plug(cvpj_l, pluginid, 'native-flstudio', 'fruity parametric eq 2')
            banddata = plugins.get_eqband(cvpj_l, pluginid, None)
            plugins.add_plug_param(cvpj_l, pluginid, 'main_lvl', main_lvl, 'int', "")

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

                        if bandtype in ['low_shelf', 'high_shelf']: band_res = 1-(band_res/1.2)
                        elif bandtype in ['low_pass', 'high_pass']: 
                            band_res = math.log(band_res, 2) / 10
                            band_res = xtramath.between_to_one(1, -1, band_res)
                        else: 
                            band_res = (band_res*65536)/4

                        plugins.add_plug_param(cvpj_l, pluginid, bandstarttxt+'_gain', band_gain*100, 'int', "")
                        plugins.add_plug_param(cvpj_l, pluginid, bandstarttxt+'_freq', band_freq*65536, 'int', "")
                        plugins.add_plug_param(cvpj_l, pluginid, bandstarttxt+'_width', band_res*65536, 'int', "")
                        plugins.add_plug_param(cvpj_l, pluginid, bandstarttxt+'_type', band_shape, 'int', "")
                        bandnum += 1
