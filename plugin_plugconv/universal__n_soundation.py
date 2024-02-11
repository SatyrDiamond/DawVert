# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import xtramath

def get_freq(i_val):
    return 20 * 1000**i_val

def eq_calc_q(band_type, q_val):
    if band_type in ['low_pass', 'high_pass']:
        q_val = q_val*math.log(162)
        q_val = 0.1 * math.exp(q_val)
        q_val = xtramath.logpowmul(q_val, 0.5)
    elif band_type in ['low_shelf', 'high_shelf']:
        q_val = q_val*math.log(162)
        q_val = 0.1 * math.exp(q_val)
    else:
        q_val = q_val*math.log(162)
        #q_val = 0.1 * math.exp(q_val)
        q_val = xtramath.logpowmul(q_val, -1) if q_val != 0 else q_val
    return q_val

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-soundation', None, 'soundation'], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json):

        print(plugin_obj.plugin_subtype)

        if plugin_obj.plugin_subtype == 'com.soundation.filter':
            filter_cutoff = plugin_obj.params.get('cutoff', 0).value
            filter_resonance = plugin_obj.params.get('resonance', 0).value
            filter_mode = plugin_obj.params.get('mode', 0).value

            plugin_obj.replace('universal', 'filter')
            plugin_obj.filter.on = True
            plugin_obj.filter.type = 'low_pass' if filter_mode else 'high_pass'
            plugin_obj.filter.freq = get_freq(filter_cutoff)
            plugin_obj.filter.q = filter_resonance
            return 1

        if plugin_obj.plugin_subtype == 'com.soundation.parametric-eq':
            for eqname in ["hpf","lowshelf","peak1","peak2","peak3","peak4","highshelf","lpf"]:

                eq_bandtype = 'peak'
                if eqname == 'highshelf': eq_bandtype = 'high_shelf'
                if eqname == 'hpf': eq_bandtype = 'high_pass'
                if eqname == 'lowshelf': eq_bandtype = 'low_shelf'
                if eqname == 'lpf': eq_bandtype = 'low_pass'

                band_enable = plugin_obj.params.get(eqname+'_enable', 0).value
                band_freq = plugin_obj.params.get(eqname+'_freq', 0).value
                band_gain = plugin_obj.params.get(eqname+'_gain', 0).value
                band_res = plugin_obj.params.get(eqname+'_q', 0).value

                filter_obj = plugin_obj.eq_add()
                filter_obj.type = eq_bandtype
                filter_obj.freq = get_freq(band_freq)
                filter_obj.q = eq_calc_q(eq_bandtype, band_res)
                filter_obj.gain = (band_gain-0.5)*40

            master_gain = plugin_obj.params.get('master_gain', 0).value
            master_gain = (master_gain-0.5)*40

            plugin_obj.replace('universal', 'eq-bands')

            plugin_obj.params.add('gain_out', master_gain, 'float')
            return 1
            
        return 2