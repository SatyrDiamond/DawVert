# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import plugins
from functions import xtramath
from functions_tracks import auto_data

slope_vals = [12,24,48]

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-lmms', None, 'lmms'], ['universal', None, None], False, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == 'eq':
            eq_Outputgain = cvpj_plugindata.param_get('Outputgain', 0)[0]
            eq_Inputgain = cvpj_plugindata.param_get('Inputgain', 0)[0]

            #HP
            eq_HPactive = cvpj_plugindata.param_get('HPactive', 0)[0]
            eq_HPfreq = cvpj_plugindata.param_get('HPfreq', 0)[0]
            eq_HPres = cvpj_plugindata.param_get('HPres', 0)[0]
            eq_HP = int(cvpj_plugindata.param_get('HP', 0)[0])
            auto_data.rename_plugparam(cvpj_l, pluginid, "HPactive", "main/1/on")
            auto_data.rename_plugparam(cvpj_l, pluginid, "HPfreq", "main/1/freq")
            auto_data.rename_plugparam(cvpj_l, pluginid, "HPres", "main/1/q")
            cvpj_plugindata.eqband_add(eq_HPactive, eq_HPfreq, 'high_pass', None)
            cvpj_plugindata.eqband_add_param('q', eq_HPres, None)
            cvpj_plugindata.eqband_add_param('slope', slope_vals[eq_HP], None)

            #low_shelf
            eq_Lowshelfactive = cvpj_plugindata.param_get('Lowshelfactive', 0)[0]
            eq_LowShelffreq = cvpj_plugindata.param_get('LowShelffreq', 0)[0]
            eq_Lowshelfgain = cvpj_plugindata.param_get('Lowshelfgain', 0)[0]
            eq_LowShelfres = cvpj_plugindata.param_get('LowShelfres', 0)[0]
            auto_data.rename_plugparam(cvpj_l, pluginid, "Lowshelfactive", "main/2/on")
            auto_data.rename_plugparam(cvpj_l, pluginid, "LowShelffreq", "main/2/freq")
            auto_data.rename_plugparam(cvpj_l, pluginid, "Lowshelfgain", "main/2/gain")
            auto_data.rename_plugparam(cvpj_l, pluginid, "LowShelfres", "main/2/q")
            cvpj_plugindata.eqband_add(eq_Lowshelfactive, eq_LowShelffreq, 'low_shelf', None)
            cvpj_plugindata.eqband_add_param('q', eq_LowShelfres, None)
            cvpj_plugindata.eqband_add_param('gain', eq_Lowshelfgain, None)

            #peak
            for peak_num in range(4):
                peak_txt = 'Peak'+str(peak_num+1)
                peak_autotxt = 'main/'+str(peak_num+3)
                eq_Peak_active = cvpj_plugindata.param_get(peak_txt+'active', 0)[0]
                eq_Peak_bw = cvpj_plugindata.param_get(peak_txt+'bw', 0)[0]
                eq_Peak_freq = cvpj_plugindata.param_get(peak_txt+'freq', 0)[0]
                eq_Peak_gain = cvpj_plugindata.param_get(peak_txt+'gain', 0)[0]
                auto_data.rename_plugparam(cvpj_l, pluginid, peak_txt+'active', peak_autotxt+"/on")
                auto_data.rename_plugparam(cvpj_l, pluginid, peak_txt+'freq', peak_autotxt+"/freq")
                auto_data.rename_plugparam(cvpj_l, pluginid, peak_txt+'gain', peak_autotxt+"/gain")
                auto_data.rename_plugparam(cvpj_l, pluginid, peak_txt+'bw', peak_autotxt+"/q")
                cvpj_plugindata.eqband_add(eq_Peak_active, eq_Peak_freq, 'peak', None)
                cvpj_plugindata.eqband_add_param('q', xtramath.logpowmul(eq_Peak_bw, -1), None)
                cvpj_plugindata.eqband_add_param('gain', eq_Peak_gain, None)

            #high_shelf
            eq_Highshelfactive = cvpj_plugindata.param_get('Highshelfactive', 0)[0]
            eq_Highshelffreq = cvpj_plugindata.param_get('Highshelffreq', 0)[0]
            eq_HighShelfgain = cvpj_plugindata.param_get('HighShelfgain', 0)[0]
            eq_HighShelfres = cvpj_plugindata.param_get('HighShelfres', 0)[0]
            auto_data.rename_plugparam(cvpj_l, pluginid, "Highshelfactive", "main/7/on")
            auto_data.rename_plugparam(cvpj_l, pluginid, "Highshelffreq", "main/7/freq")
            auto_data.rename_plugparam(cvpj_l, pluginid, "HighShelfgain", "main/7/gain")
            auto_data.rename_plugparam(cvpj_l, pluginid, "HighShelfres", "main/7/q")
            cvpj_plugindata.eqband_add(eq_Highshelfactive, eq_Highshelffreq, 'high_shelf', None)
            cvpj_plugindata.eqband_add_param('q', eq_HighShelfres, None)
            cvpj_plugindata.eqband_add_param('gain', eq_HighShelfgain, None)

            #LP
            eq_LPactive = cvpj_plugindata.param_get('LPactive', 0)[0]
            eq_LPfreq = cvpj_plugindata.param_get('LPfreq', 0)[0]
            eq_LPres = cvpj_plugindata.param_get('LPres', 0)[0]
            eq_LP = int(cvpj_plugindata.param_get('LP', 0)[0])
            auto_data.rename_plugparam(cvpj_l, pluginid, "LPactive", "main/8/on")
            auto_data.rename_plugparam(cvpj_l, pluginid, "LPfreq", "main/8/freq")
            auto_data.rename_plugparam(cvpj_l, pluginid, "LPres", "main/8/q")
            cvpj_plugindata.eqband_add(eq_HPactive, eq_LPfreq, 'low_pass', None)
            cvpj_plugindata.eqband_add_param('q', eq_LPres, None)
            cvpj_plugindata.eqband_add_param('slope', slope_vals[eq_LP], None)

            cvpj_plugindata.replace('universal', 'eq-bands')
            cvpj_plugindata.param_add('gain_out', eq_Outputgain, 'float', 'Out Gain')
            cvpj_plugindata.param_add('gain_in', eq_Inputgain, 'float', 'In Gain')
            return 1
            
        return 2