# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import xtramath

slope_vals = [12,24,48]

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['directx', None, None], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):

        if plugin_obj.plugin_subtype == 'Chorus':
            print("[plug-conv] DirectX to Universal: Chorus:",pluginid)
            waveshape = 'sine' if bool(plugin_obj.params.get('waveshape', 0).value) else 'triangle'
            plugtransform.transform('./data_plugts/directx.pltr', 'chorus_univ', convproj_obj, plugin_obj, pluginid, dv_config)
            plugin_obj.datavals.add('waveshape', waveshape)
            return 1
            
        if plugin_obj.plugin_subtype == 'Compressor':
            print("[plug-conv] DirectX to Universal: Compressor:",pluginid)
            plugtransform.transform('./data_plugts/directx.pltr', 'compressor_univ', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1
            
        if plugin_obj.plugin_subtype == 'Echo':
            print("[plug-conv] DirectX to Universal: Echo > Delay:",pluginid)
            i_feedback = plugin_obj.params.get('feedback', 0).value
            i_leftdelay = plugin_obj.params.get('leftdelay', 0).value
            i_rightdelay = plugin_obj.params.get('rightdelay', 0).value
            i_pandelay = bool(plugin_obj.params.get('pandelay', 0).value)
            i_leftdelay = xtramath.between_from_one(0.001, 2, i_leftdelay)
            i_rightdelay = xtramath.between_from_one(0.001, 2, i_rightdelay)

            plugin_obj.replace('universal', 'delay')
            plugin_obj.datavals.add('traits', ['stereo'])
            plugin_obj.datavals.add('traits_seperated', ['time'])

            timing_obj = plugin_obj.timing_add('left')
            timing_obj.set_seconds(i_leftdelay)
            timing_obj = plugin_obj.timing_add('right')
            timing_obj.set_seconds(i_rightdelay)

            plugin_obj.datavals.add('c_fb', i_feedback if i_pandelay else 0)
            plugin_obj.datavals.add('c_cross_fb', 0 if i_pandelay else i_feedback)
            return 1
            
        if plugin_obj.plugin_subtype == 'Flanger':
            print("[plug-conv] DirectX to Universal: Flanger:",pluginid)
            waveshape = 'sine' if bool(plugin_obj.params.get('waveshape', 0).value) else 'triangle'
            plugtransform.transform('./data_plugts/directx.pltr', 'flanger_univ', convproj_obj, plugin_obj, pluginid, dv_config)
            plugin_obj.datavals.add('waveshape', waveshape)
            return 1

        if plugin_obj.plugin_subtype == 'Gargle':
            print("[plug-conv] DirectX to Universal: Gargle > Ringmod:",pluginid)
            garg_shape = 'square' if bool(plugin_obj.params.get('waveshape', 0).value) else 'triangle'
            garg_rate = plugin_obj.params.get('rate', 0).value
            garg_rate = xtramath.between_from_one(1, 1000, garg_rate)
            plugin_obj.replace('universal', 'ringmod')
            plugin_obj.datavals.add('shape', garg_shape)
            plugin_obj.params.add('rate', garg_rate, 'float')
            return 1

        if plugin_obj.plugin_subtype == 'ParamEq':
            eq_bandwidth = plugin_obj.params.get('bandwidth', 0).value
            eq_center = plugin_obj.params.get('center', 0).value
            eq_eqgain = plugin_obj.params.get('eqgain', 0).value
            eq_center = xtramath.between_from_one(80, 16000, eq_center)
            eq_bandwidth = xtramath.between_from_one(1, 36, eq_bandwidth)
            plugin_obj.replace('universal', 'filter')
            plugin_obj.filter.on = True
            plugin_obj.filter.type = 'peak'
            plugin_obj.filter.freq = eq_center
            plugin_obj.filter.q = eq_bandwidth/36
            return 1

        return 2