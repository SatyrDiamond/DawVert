# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-symmod', None, None], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):

        if plugin_obj.plugin_subtype == 'echo':
            p_type = plugin_obj.params.get("type", 0).value
            p_delay = plugin_obj.params.get("delay", 0).value/50
            p_fb = 1/(plugin_obj.params.get("fb", 0).value+1)

            if p_type in [1, 4]:
                print("[plug-conv] SymMOD to Universal: Echo > Delay:",pluginid)
                plugin_obj.replace('universal', 'delay')
                plugin_obj.datavals.add('traits', [])
                plugin_obj.datavals.add('c_fb', p_fb)
            
                timing_obj = plugin_obj.timing_add('center')
                timing_obj.set_seconds(convproj_obj, p_delay)

            if p_type in [2, 3]:
                print("[plug-conv] SymMOD to Universal: Echo > Delay:",pluginid)
                plugin_obj.replace('universal', 'delay')
                plugin_obj.datavals.add('traits', ['stereo'])
                plugin_obj.datavals.add('c_cross_fb', p_fb)

                timing_obj = plugin_obj.timing_add('center')
                timing_obj.set_seconds(convproj_obj, p_delay)

            return 1
            
        return 2