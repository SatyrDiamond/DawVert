# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-onlineseq', None, 'onlineseq'], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):
        global loaded_plugtransform
        global plugts_obj

        if plugin_obj.plugin_subtype == 'eq':
            print('[plug-conv] Online Sequencer to Universal: EQ > 3 Band EQ:',pluginid)
            plugtransform.transform('./data_plugts/onlineseq_univ.pltr', 'eq', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        return 2