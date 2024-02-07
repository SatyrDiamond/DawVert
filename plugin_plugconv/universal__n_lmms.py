# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import xtramath

slope_vals = [12,24,48]

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-lmms', None, 'lmms'], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json):
        if plugin_obj.plugin_subtype == 'eq':
            eq_Outputgain = plugin_obj.params.get('Outputgain', 0).value
            eq_Inputgain = plugin_obj.params.get('Inputgain', 0).value

            #HP
            filter_obj = plugin_obj.eq_add()
            filter_obj.on = bool(plugin_obj.params.get('HPactive', 0).value)
            filter_obj.type = 'high_pass'
            filter_obj.freq = plugin_obj.params.get('HPfreq', 0).value
            filter_obj.q = plugin_obj.params.get('HPres', 0).value
            filter_obj.slope = slope_vals[int(plugin_obj.params.get('HP', 0).value)]
            ##auto_data.rename_plugparam(cvpj_l, pluginid, "HPactive", "main/1/on")
            ##auto_data.rename_plugparam(cvpj_l, pluginid, "HPfreq", "main/1/freq")
            ##auto_data.rename_plugparam(cvpj_l, pluginid, "HPres", "main/1/q")

            #low_shelf
            filter_obj = plugin_obj.eq_add()
            filter_obj.on = bool(plugin_obj.params.get('Lowshelfactive', 0).value)
            filter_obj.type = 'low_shelf'
            filter_obj.freq = plugin_obj.params.get('LowShelffreq', 0).value
            filter_obj.q = plugin_obj.params.get('LowShelfres', 0).value
            filter_obj.gain = plugin_obj.params.get('Lowshelfgain', 0).value
            ##auto_data.rename_plugparam(cvpj_l, pluginid, "Lowshelfactive", "main/2/on")
            ##auto_data.rename_plugparam(cvpj_l, pluginid, "LowShelffreq", "main/2/freq")
            ##auto_data.rename_plugparam(cvpj_l, pluginid, "Lowshelfgain", "main/2/gain")
            ##auto_data.rename_plugparam(cvpj_l, pluginid, "LowShelfres", "main/2/q")

            #peak
            for peak_num in range(4):
                eq_Peak_bw = plugin_obj.params.get(peak_txt+'bw', 0).value
                peak_txt = 'Peak'+str(peak_num+1)
                filter_obj = plugin_obj.eq_add()
                filter_obj.on = bool(plugin_obj.params.get(peak_txt+'active', 0).value)
                filter_obj.type = 'peak'
                filter_obj.freq = plugin_obj.params.get(peak_txt+'freq', 0).value
                filter_obj.q = xtramath.logpowmul(eq_Peak_bw, -1)
                filter_obj.gain = plugin_obj.params.get(peak_txt+'gain', 0).value
                peak_autotxt = 'main/'+str(peak_num+3)
                #auto_data.rename_plugparam(cvpj_l, pluginid, peak_txt+'active', peak_autotxt+"/on")
                #auto_data.rename_plugparam(cvpj_l, pluginid, peak_txt+'freq', peak_autotxt+"/freq")
                #auto_data.rename_plugparam(cvpj_l, pluginid, peak_txt+'gain', peak_autotxt+"/gain")
                #auto_data.rename_plugparam(cvpj_l, pluginid, peak_txt+'bw', peak_autotxt+"/q")

            #high_shelf
            filter_obj = plugin_obj.eq_add()
            filter_obj.on = bool(plugin_obj.params.get('Highshelfactive', 0).value)
            filter_obj.type = 'high_shelf'
            filter_obj.freq = plugin_obj.params.get('Highshelffreq', 0).value
            filter_obj.q = plugin_obj.params.get('HighShelfres', 0).value
            filter_obj.gain = plugin_obj.params.get('HighShelfgain', 0).value
            #auto_data.rename_plugparam(cvpj_l, pluginid, "Highshelfactive", "main/7/on")
            #auto_data.rename_plugparam(cvpj_l, pluginid, "Highshelffreq", "main/7/freq")
            #auto_data.rename_plugparam(cvpj_l, pluginid, "HighShelfgain", "main/7/gain")
            #auto_data.rename_plugparam(cvpj_l, pluginid, "HighShelfres", "main/7/q")

            #LP
            filter_obj = plugin_obj.eq_add()
            filter_obj.on = bool(plugin_obj.params.get('LPactive', 0).value)
            filter_obj.type = 'low_pass'
            filter_obj.freq = plugin_obj.params.get('LPfreq', 0).value
            filter_obj.q = plugin_obj.params.get('LPres', 0).value
            filter_obj.slope = slope_vals[int(plugin_obj.params.get('LP', 0).value)]
            #auto_data.rename_plugparam(cvpj_l, pluginid, "LPactive", "main/8/on")
            #auto_data.rename_plugparam(cvpj_l, pluginid, "LPfreq", "main/8/freq")
            #auto_data.rename_plugparam(cvpj_l, pluginid, "LPres", "main/8/q")

            plugin_obj.replace('universal', 'eq-bands')
            plugin_obj.params.add('gain_out', eq_Outputgain, 'float')
            plugin_obj.params.add('gain_in', eq_Inputgain, 'float')
            return 1
            
        return 2