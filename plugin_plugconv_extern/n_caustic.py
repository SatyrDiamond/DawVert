# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from functions_plugin_ext import plugin_vst2

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['native-caustic', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json, extplugtype):

        #print(extplugtype, plugin_obj.plugin_subtype)

        if plugin_obj.plugin_subtype == 'auto_wah':
            pass

        if plugin_obj.plugin_subtype == 'autopan':
            pass

        if plugin_obj.plugin_subtype == 'bitcrush':
            pass

        if plugin_obj.plugin_subtype == 'cabsim':
            pass

        if plugin_obj.plugin_subtype == 'chorus':
            pass

        if plugin_obj.plugin_subtype == 'comb':
            pass

        if plugin_obj.plugin_subtype == 'compresser':
            pass

        if plugin_obj.plugin_subtype == 'delay':
            pass

        if plugin_obj.plugin_subtype == 'distortion':
            pass

        if plugin_obj.plugin_subtype == 'filter':
            pass

        if plugin_obj.plugin_subtype == 'flanger':
            pass

        if plugin_obj.plugin_subtype == 'limiter':
            pass

        if plugin_obj.plugin_subtype == 'octaver':
            pass

        if plugin_obj.plugin_subtype == 'parameq':
            pass

        if plugin_obj.plugin_subtype == 'phaser':
            pass

        if plugin_obj.plugin_subtype == 'reverb':
            pass

        if plugin_obj.plugin_subtype == 'staticflanger':
            pass

        if plugin_obj.plugin_subtype == 'tremolo':
            pass

        if plugin_obj.plugin_subtype == 'vibrato':
            pass

        if plugin_obj.plugin_subtype == 'vinylsim':
            pass


        #exit()

        return False