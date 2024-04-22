# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv
from objects_params import fx_delay
 
class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-digibooster', None, None], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):

        if plugin_obj.plugin_subtype == 'pro_echo':
            print("[plug-conv] DigiBooster to Universal: Pro Echo > Delay:",pluginid)
            p_delay = plugin_obj.params.get("delay", 0).value*0.004
            p_fb = plugin_obj.params.get("fb", 0).value/255
            p_wet = plugin_obj.params.get("wet", 0).value/255
            p_cross_echo = plugin_obj.params.get("cross_echo", 0).value/255
            if p_delay == 0: p_delay = 0.334

            delay_obj = fx_delay.fx_delay()
            delay_obj.feedback_first = False
            delay_obj.dry = 0
            delay_obj.feedback[0] = p_fb*(1-p_cross_echo)
            delay_obj.feedback_cross[0] = p_cross_echo
            timing_obj = delay_obj.timing_add(0)
            timing_obj.set_seconds(convproj_obj, p_delay)
            plugin_obj = delay_obj.to_cvpj(convproj_obj, pluginid)

            plugin_obj.fxdata_add(None, p_wet)
            return 1
            
        return 2