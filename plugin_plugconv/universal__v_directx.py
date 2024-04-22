# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import xtramath
from objects_params import fx_delay

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

            delay_obj = fx_delay.fx_delay()
            delay_obj.feedback_first = False
            delay_obj.feedback[0] = i_feedback

            timing_obj = delay_obj.timing_add(0)
            timing_obj.set_seconds(i_leftdelay)
            timing_obj = delay_obj.timing_add(1)
            timing_obj.set_seconds(i_rightdelay)

            if i_pandelay: 
                delay_obj.mode = 'pingpong'
                delay_obj.submode = 'normal'

            plugin_obj = delay_obj.to_cvpj(convproj_obj, pluginid)

            return 1

            
        if plugin_obj.plugin_subtype == 'Flanger':
            print("[plug-conv] DirectX to Universal: Flanger:",pluginid)
            p_frequency = plugin_obj.params.get('frequency', 0).value
            p_depth = plugin_obj.params.get('depth', 0).value
            waveshape = 'sine' if bool(plugin_obj.params.get('waveshape', 0).value) else 'triangle'
            plugtransform.transform('./data_plugts/directx.pltr', 'flanger_univ', convproj_obj, plugin_obj, pluginid, dv_config)
            plugin_obj.datavals.add('waveshape', waveshape)
            lfo_obj = plugin_obj.lfo_add('flanger')
            lfo_obj.time.set_hz(p_frequency)
            lfo_obj.amount = p_depth
            lfo_obj.shape = waveshape
            return 1

        if plugin_obj.plugin_subtype == 'Gargle':
            print("[plug-conv] DirectX to Universal: Gargle > Ringmod:",pluginid)
            garg_shape = 'square' if bool(plugin_obj.params.get('waveshape', 0).value) else 'triangle'
            garg_rate = plugin_obj.params.get('rate', 0).value
            garg_rate = xtramath.between_from_one(1, 1000, garg_rate)
            plugin_obj.replace('universal', 'ringmod')
            plugin_obj.datavals.add('shape', garg_shape)
            plugin_obj.params.add('rate', garg_rate, 'float')
            lfo_obj = plugin_obj.lfo_add('amount')
            lfo_obj.time.set_hz(garg_rate)
            lfo_obj.amount = 1
            lfo_obj.shape = garg_shape
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