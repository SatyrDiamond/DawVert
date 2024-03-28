# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import xtramath

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):

        if plugin_obj.plugin_subtype == 'fruity parametric eq 2':
            print('[plug-conv] FL Studio to Universal: Fruity Parametric EQ 2 > EQ Bands:',pluginid)
            main_lvl = plugin_obj.params.get('main_lvl', 0).value/100

            for bandnum in range(7):
                bandstarttxt = str(bandnum+1)

                filter_obj = plugin_obj.eq_add()
                filter_obj.type = 'peak'

                filter_obj.gain = plugin_obj.params.get(bandstarttxt+'_gain', 0).value/100

                fl_band_freq = plugin_obj.params.get(bandstarttxt+'_freq', 0).value/65536
                filter_obj.freq = 20 * 1000**fl_band_freq

                fl_band_type = plugin_obj.params.get(bandstarttxt+'_type', 0).value
                fl_band_width = plugin_obj.params.get(bandstarttxt+'_width', 0).value/65536

                filter_obj.type = 'peak'

                if fl_band_type in [5, 7]: 
                    filter_obj.q = (1-fl_band_width)*1.2
                elif fl_band_type in [1, 3]: 
                    fl_band_width = xtramath.between_from_one(1, -1, fl_band_width)
                    filter_obj.q = pow(2, fl_band_width*5)
                else: 
                    outwid = ((fl_band_width+0.01)*3)
                    outwid = xtramath.logpowmul(outwid, -1)
                    filter_obj.q = outwid

                if fl_band_type != 0: filter_obj.on = True
                if fl_band_type == 1: filter_obj.type = 'low_pass'
                if fl_band_type == 2: filter_obj.type = 'band_pass'
                if fl_band_type == 3: filter_obj.type = 'high_pass'
                if fl_band_type == 4: filter_obj.type = 'notch'
                if fl_band_type == 5: filter_obj.type = 'low_shelf'
                if fl_band_type == 6: filter_obj.type = 'peak'
                if fl_band_type == 7: filter_obj.type = 'high_shelf'

            plugin_obj.replace('universal', 'eq-bands')
            param_obj = plugin_obj.params.add('gain_out', main_lvl, 'float')
            return 1

        if plugin_obj.plugin_subtype == 'fruity compressor':
            print('[plug-conv] FL Studio to Universal: Fruity Compressor > Compressor:',pluginid)
            v_threshold = plugin_obj.params.get('threshold', 0).value/10
            v_ratio = plugin_obj.params.get('ratio', 0).value/10
            v_gain = plugin_obj.params.get('gain', 0).value/10
            v_attack = plugin_obj.params.get('attack', 0).value/10000
            v_release = plugin_obj.params.get('release', 0).value/1000
            v_type = plugin_obj.params.get('type', 0).value

            first_type = v_type>>2
            second_type = v_type%4
            if second_type == 0: v_knee = 0
            if second_type == 1: v_knee = 6
            if second_type == 2: v_knee = 7
            if second_type == 3: v_knee = 15
            if first_type == 0: v_tcr = 0
            if first_type == 1: v_tcr = 1

            plugin_obj.replace('universal', 'compressor')
            plugin_obj.datavals.add('tcr', bool(v_tcr) )
            plugin_obj.params.add('pregain', v_gain, 'float')
            plugin_obj.params.add('ratio', v_ratio, 'float')
            plugin_obj.params.add('threshold', v_threshold, 'float')
            plugin_obj.params.add('attack', v_attack, 'float')
            plugin_obj.params.add('release', v_release, 'float')
            plugin_obj.params.add('knee', v_knee, 'float')

        if plugin_obj.plugin_subtype == 'pitcher':
            print('[plug-conv] FL Studio to Universal: Pitcher > AutoTune:',pluginid)
            p_keys = plugin_obj.datavals.get('key_on', 0)
            p_bypass = plugin_obj.datavals.get('bypass', 0)
            p_hz = xtramath.between_from_one(415.3, 466.2, plugin_obj.datavals.get('hz', 0))
            p_min_freq = [220,170,110,80,55,25][int(plugin_obj.datavals.get('min_freq', 0))]
            p_speed = plugin_obj.params.get('correction_speed', 1).value
            p_gender = plugin_obj.params.get('gender', 1).value
            p_formant = bool(plugin_obj.datavals.get('formant', 0))
            plugin_obj.replace('universal', 'autotune')
            for keynum, p_key in enumerate(p_keys): plugin_obj.params.add('key_on_'+str(keynum), p_key, 'bool')
            for keynum, p_key in enumerate(p_bypass): plugin_obj.params.add('key_bypass_'+str(keynum), p_key, 'bool')
            plugin_obj.params.add('calibrate', p_hz, 'float')
            plugin_obj.params.add('speed', p_speed, 'float')
            plugin_obj.params.add('min_freq', p_min_freq, 'float')
            plugin_obj.params.add('formant_gender', p_gender, 'float')
            plugin_obj.params.add('formant_on', p_formant, 'bool')
        
        if 'shareware' not in dv_config.flags_plugins:
            if plugin_obj.plugin_subtype == 'fruity delay 2':
                print('[plug-conv] FL Studio to Universal: Fruity Delay 2 > Delay:',pluginid)
                d_dry = plugin_obj.params.get('dry', 0).value/128
                d_fb_cut = plugin_obj.params.get('fb_cut', 0).value/128
                d_fb_mode = plugin_obj.params.get('fb_mode', 0).value
                d_fb_vol = plugin_obj.params.get('fb_vol', 0).value/128
                d_input_pan = plugin_obj.params.get('input_pan', 0).value/128
                d_input_vol = plugin_obj.params.get('input_vol', 0).value/160
                d_time = plugin_obj.params.get('time', 0).value/48
                d_time_stereo_offset = plugin_obj.params.get('time_stereo_offset', 1).value/512

                plugin_obj.replace('universal', 'delay')
                plugin_obj.datavals.add('traits', ['stereo'])
                plugin_obj.datavals.add('input_vol', d_input_vol)
                plugin_obj.datavals.add('input_pan', d_input_pan)
                plugin_obj.datavals.add('wet', 1)
                plugin_obj.datavals.add('dry', d_dry)
                timing_obj = plugin_obj.timing_add('center')
                timing_obj.set_steps(d_time, convproj_obj)
                plugin_obj.datavals.add('c_invert_feedback', d_fb_mode==1)
                if d_fb_mode==2:
                    plugin_obj.datavals.add('c_fb', 0)
                    plugin_obj.datavals.add('c_cross_fb', d_fb_vol)
                else:
                    plugin_obj.datavals.add('c_fb', d_fb_vol)
                    plugin_obj.datavals.add('c_cross_fb', 0)
                plugin_obj.datavals.add('stereo_offset', d_time_stereo_offset)

        return 2