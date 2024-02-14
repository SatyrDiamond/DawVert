# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-digibooster', None, None], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json):

        if plugin_obj.plugin_subtype == 'pro_echo':
            p_delay = plugin_obj.params.get("delay", 0).value*0.004
            p_fb = plugin_obj.params.get("fb", 0).value/255
            p_wet = plugin_obj.params.get("wet", 0).value/255
            p_cross_echo = plugin_obj.params.get("cross_echo", 0).value/255
            if p_delay == 0: p_delay = 0.334
            print("[plug-conv] DigiBooster to Universal: Pro Echo > Stereo Delay:",pluginid)
            plugin_obj.replace('universal', 'delay-stereo')
            plugin_obj.datavals.add('wet', 1)
            plugin_obj.datavals.add('time_type', 'seconds')
            plugin_obj.datavals.add('l_time', p_delay)
            plugin_obj.datavals.add('r_time', p_delay)
            plugin_obj.datavals.add('fb', p_fb)
            plugin_obj.datavals.add('cross_fb', p_cross_echo)
            plugin_obj.fxdata_add(None, p_wet)
            return 1
            
        return 2