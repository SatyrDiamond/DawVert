# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import plugins
from functions import xtramath
from functions_tracks import auto_data

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
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == 'com.soundation.filter':
            filter_cutoff = cvpj_plugindata.param_get('cutoff', 0)[0]
            filter_resonance = cvpj_plugindata.param_get('resonance', 0)[0]
            filter_mode = cvpj_plugindata.param_get('mode', 0)[0]
            eq_bandtype = 'low_pass' if filter_mode else 'high_pass'
            cvpj_plugindata.replace('universal', 'eq-bands')
            cvpj_plugindata.dataval_add('num_bands', 1)
            cvpj_plugindata.eqband_add(1, get_freq(filter_cutoff), eq_bandtype, None)
            cvpj_plugindata.eqband_add_param('q', filter_resonance, None)
            return True

        if plugintype[1] == 'com.soundation.parametric-eq':
            for eqname in ["highshelf","hpf","lowshelf","lpf","peak1","peak2","peak3","peak4"]:

                eq_bandtype = 'peak'
                if eqname == 'highshelf': eq_bandtype = 'high_shelf'
                if eqname == 'hpf': eq_bandtype = 'high_pass'
                if eqname == 'lowshelf': eq_bandtype = 'low_shelf'
                if eqname == 'lpf': eq_bandtype = 'low_pass'

                band_enable = cvpj_plugindata.param_get(eqname+'_enable', 0)[0]
                band_freq = cvpj_plugindata.param_get(eqname+'_freq', 0)[0]
                band_gain = cvpj_plugindata.param_get(eqname+'_gain', 0)[0]
                band_res = cvpj_plugindata.param_get(eqname+'_q', 0)[0]

                band_freq = 20 * 1000**band_freq
                band_gain = (band_gain-0.5)*40
                band_res = eq_calc_q(eq_bandtype, band_res)
                
                cvpj_plugindata.eqband_add(int(band_enable), band_freq, eq_bandtype, None)
                cvpj_plugindata.eqband_add_param('gain', eq_bandtype, None)
                cvpj_plugindata.eqband_add_param('q', band_res, None)

            master_gain = cvpj_plugindata.param_get('master_gain', 0)[0]
            master_gain = (master_gain-0.5)*40

            cvpj_plugindata.replace('universal', 'eq-bands')

            cvpj_plugindata.param_add('gain_out', master_gain, 'float', 'Out Gain')
