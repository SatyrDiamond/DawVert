# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-symmod', None, None], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json):

        if plugin_obj.plugin_subtype == 'echo':
            p_type = plugin_obj.params.get("type", 0).value
            p_delay = plugin_obj.params.get("delay", 0).value/50
            p_fb = 1/(plugin_obj.params.get("fb", 0).value+1)

            if p_type in [1, 4]:
                print("[plug-conv] SymMOD to Universal: Echo > Delay:",pluginid)
                plugin_obj = convproj_obj.add_plugin(pluginid, 'universal', 'delay-c')
                plugin_obj.datavals.add('time_type', 'seconds')
                plugin_obj.datavals.add('time', p_delay)
                plugin_obj.datavals.add('feedback', p_fb)
                
            if p_type in [2, 3]:
                print("[plug-conv] SymMOD to Universal: Echo > Stereo Delay:",pluginid)
                plugin_obj.replace('universal', 'delay-stereo')
                plugin_obj.datavals.add('wet', 1)
                plugin_obj.datavals.add('time_type', 'seconds')
                plugin_obj.datavals.add('l_time', p_delay)
                plugin_obj.datavals.add('r_time', p_delay)
                plugin_obj.datavals.add('cross_feedback', p_fb)
            return 1
            
        return 2