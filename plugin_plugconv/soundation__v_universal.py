# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv
from functions import note_data
from functions import xtramath
import math

def eq_calc_pass(i_dict):
    i_value = i_dict['q'] if 'q' in i_dict else 1
    i_value = xtramath.logpowmul(i_value, 0.5)
    i_value = math.log(i_value / 0.1)
    i_value = i_value / math.log(162)
    return i_value

def eq_calc_shelf(i_dict):
    i_value = i_dict['q'] if 'q' in i_dict else 1
    i_value = math.log(i_value / 0.1)
    i_value = i_value / math.log(162)
    return i_value

def eq_calc_peak(i_dict):
    i_value = i_dict['q'] if 'q' in i_dict else 1

    if i_value == 0: i_value = 1

    i_value = xtramath.logpowmul(i_value, -1)
    i_value = math.log( i_value / 0.1)
    i_value = i_value / math.log(162)
    return i_value

def eq_calc_freq(i_value): return (math.log(i_value/20) / math.log(1000)) if i_value != 0 else 0

def eq_calc_gain(i_dict): 
    i_value = i_dict['gain'] if 'gain' in i_dict else 0
    return (i_value/40)+0.5

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['universal', None, None], ['native-soundation', None, 'soundation'], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == 'eq-bands':
            gain_out = cvpj_plugindata.param_get('gain_out', 0)[0]

            cvpj_plugindata.replace('native-soundation', 'com.soundation.parametric-eq')

            data_LP, data_LS, data_Peaks, data_HS, data_HP, data_reorder = cvpj_plugindata.eqband_get_limited(None)

            if data_LP != None:
                cvpj_plugindata.param_add('lpf_enable', float(data_LP['on']), 'float', '')
                cvpj_plugindata.param_add('lpf_freq', eq_calc_freq(data_LP['freq']), 'float', '')
                cvpj_plugindata.param_add('lpf_res', eq_calc_pass(data_LP), 'float', '')
                cvpj_plugindata.param_add('lpf_slope', 0.25, 'float', 'HP')
                
            if data_LS != None:
                cvpj_plugindata.param_add('lowshelf_enable', float(data_LS['on']), 'float', '')
                cvpj_plugindata.param_add('lowshelf_freq', eq_calc_freq(data_LS['freq']), 'float', '')
                cvpj_plugindata.param_add('lowshelf_gain', eq_calc_gain(data_LS), 'float', '')
                cvpj_plugindata.param_add('lowshelf_res', eq_calc_shelf(data_LS), 'float', '')
                
            for peak_num in range(4):
                if data_Peaks[peak_num] != None:
                    peak_txt = 'peak'+str(peak_num+1)+'_'
                    data_peak = data_Peaks[peak_num]
                    cvpj_plugindata.param_add(peak_txt+'active', int(data_peak['on']), 'float', '')
                    cvpj_plugindata.param_add(peak_txt+'freq', eq_calc_freq(data_peak['freq']), 'float', '')
                    cvpj_plugindata.param_add(peak_txt+'gain', eq_calc_gain(data_peak), 'float', '')
                    cvpj_plugindata.param_add(peak_txt+'res', eq_calc_peak(data_peak), 'float', '')

            if data_HS != None:
                cvpj_plugindata.param_add('highshelf_enable', float(data_HS['on']), 'float', '')
                cvpj_plugindata.param_add('highshelf_freq', eq_calc_freq(data_HS['freq']), 'float', '')
                cvpj_plugindata.param_add('highshelf_gain', eq_calc_gain(data_HS), 'float', '')
                cvpj_plugindata.param_add('highshelf_res', eq_calc_shelf(data_HS), 'float', '')
                
            if data_HP != None:
                cvpj_plugindata.param_add('hpf_enable', float(data_HP['on']), 'float', '')
                cvpj_plugindata.param_add('hpf_freq', eq_calc_freq(data_HP['freq']), 'float', '')
                cvpj_plugindata.param_add('hpf_res', eq_calc_pass(data_LP), 'float', '')
                cvpj_plugindata.param_add('hpf_slope', 0.25, 'float', 'HP')
                
            cvpj_plugindata.param_add('master_gain', (gain_out/40)+0.5,'float', '')
            return True
