# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import base64
import struct
import os
import math
import lxml.etree as ET

from functions_plugin import ableton_values
from functions import note_data
from functions import data_bytes
from functions import data_values
from functions import plugin_vst2
from functions import plugins
from functions import tracks

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['native-ableton', None, 'ableton'], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):

        if plugintype[1] == None: plugintype[1] = ''
    
        if plugintype[1].lower() == 'fruity compressor':  
            print('[plug-conv] FL Studio to Ableton: Fruity Compressor > Compressor2:',pluginid)
            tracks.a_del_auto_plugin(cvpj_l, pluginid)
            comp_threshold = plugins.get_plug_param(cvpj_l, pluginid, 'threshold', 0)[0]/10
            comp_ratio = plugins.get_plug_param(cvpj_l, pluginid, 'ratio', 0)[0]/10
            comp_gain = plugins.get_plug_param(cvpj_l, pluginid, 'gain', 0)[0]/10
            comp_attack = plugins.get_plug_param(cvpj_l, pluginid, 'attack', 0)[0]/10000
            comp_release = plugins.get_plug_param(cvpj_l, pluginid, 'release', 0)[0]/1000
            comp_type = plugins.get_plug_param(cvpj_l, pluginid, 'type', 0)[0]
            comp_threshold = ableton_values.compressor_threshold_in(comp_threshold)
            first_type = comp_type>>2
            second_type = comp_type%4
            if second_type == 0: als_knee = 0
            if second_type == 1: als_knee = 6
            if second_type == 2: als_knee = 12
            if second_type == 3: als_knee = 18
            if first_type == 0: als_model = 0
            if first_type == 1: als_model = 1
            plugins.replace_plug(cvpj_l, pluginid, 'native-ableton', 'Compressor2')
            plugins.add_plug_param(cvpj_l, pluginid, 'Threshold', comp_threshold, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Ratio', comp_ratio, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Attack', comp_attack*1000, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Release', comp_release*1000, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Gain', comp_gain, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Model', als_model, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'Knee', als_knee, 'float', "")

        if plugintype[1].lower() == 'fruity balance':  
            print('[plug-conv] FL Studio to Ableton: Fruity Balance > StereoGain:',pluginid)
            tracks.a_del_auto_plugin(cvpj_l, pluginid)
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
