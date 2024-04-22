# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv
from objects_params import fx_delay

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-symmod', None, None], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):

        if plugin_obj.plugin_subtype == 'echo':
            print("[plug-conv] SymMOD to Universal: Echo > Delay:",pluginid)

            p_type = plugin_obj.params.get("type", 0).value
            p_delay = plugin_obj.params.get("delay", 0).value/50
            p_fb = 1/(plugin_obj.params.get("fb", 0).value+1)

            delay_obj = fx_delay.fx_delay()
            delay_obj.feedback_first = True
            timing_obj = delay_obj.timing_add(0)
            timing_obj.set_seconds(p_delay)
            delay_obj.feedback[0] = p_fb

            if p_type in [2, 3]:
                delay_obj.mode = 'pingpong'
                delay_obj.submode = 'normal'
                delay_obj.feedback[0] = p_fb if p_type == 2 else 1-p_fb

            if p_type: plugin_obj = delay_obj.to_cvpj(convproj_obj, pluginid)
            return 1
            
        return 2