# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import base64
import struct
import os
import math
import lxml.etree as ET

from functions import note_data
from functions import data_bytes
from functions import data_values
from functions import plugin_vst2
from functions import plugins

def getparam(paramname):
    global pluginid_g
    global cvpj_l_g
    paramval = plugins.get_plug_param(cvpj_l_g, pluginid_g, paramname, 0)
    return paramval[0]

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['native-ableton', None, 'ableton'], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):

        if plugintype[1] == None: plugintype[1] = ''
    
        if plugintype[1].lower() == 'fruity balance':  
            print('[plug-conv] FL Studio to Ableton: Fruity Balance > StereoGain:',pluginid)
            bal_pan = plugins.get_plug_param(cvpj_l, pluginid, 'pan', 0)[0]
            bal_vol = plugins.get_plug_param(cvpj_l, pluginid, 'vol', 256)[0]

            plugins.replace_plug(cvpj_l, pluginid, 'native-ableton', 'StereoGain')

            plugins.add_plug_param(cvpj_l, pluginid, 'PhaseInvertL', False, 'bool', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'PhaseInvertR', False, 'bool', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'ChannelMode', 1, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'StereoWidth', 1, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'MidSideBalance', 1, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Mono', False, 'bool', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'BassMono', False, 'bool', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'BassMonoFrequency', 120, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Balance', bal_pan/128, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Gain', 0, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'LegacyGain', ((bal_vol/256)-1)*35, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Mute', False, 'bool', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'DcFilter', False, 'bool', "")

            return True
