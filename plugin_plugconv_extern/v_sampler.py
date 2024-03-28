# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import params_os_ninjas2
from functions import errorprint

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['sampler', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype, plugtransform):
        pass
        #fx_on, fx_wet = plugin_obj.fxdata_get()

        #if plugin_obj.plugin_subtype == 'slicer' and 'vst2' in extplugtype:
        #    if plugin_vst2.check_exists('id', 1315524146):
        #        ninjas2_data = params_os_ninjas2.ninjas2_data()

        #        progtable = ['0 0 0 0.001000 0.001000 1.000000 0.001000' for x in range(127)]

        #        ref_found, sampleref_obj = plugin_obj.sampleref_fileref('sample', convproj_obj)
        #        if ref_found: 
        #            ninjas2_data.data_progs['filepathFromUI'] = sampleref_obj.fileref.get_path(None, True)

        #        ninjas2_data.data_main['number_of_slices'] = str(len(plugin_obj.regions.data))
        #        for c, region in enumerate(plugin_obj.regions): 
        #            start, end, data = region

        #            start = max(start, 1)
        #            end = end-1
        #            print(region)

        #            s_reverse = bool(data['reverse']) if 'reverse' in data else False
        #            s_looped = bool(data['looped']) if 'looped' in data else False
        #            ninjas2_loopout = 0
        #            if s_reverse == True: ninjas2_loopout += 1
        #            if s_looped == True: ninjas2_loopout += 2

        #            progtable[c+1] = str(start*2)+' '+str(end*2)+' '+str(ninjas2_loopout)+' 0.001000 0.001000 1.000000 0.001000'

        #        ninjas2_data.data_progs['program00'] = ' '.join(progtable)
        #        ninjas2_data.to_cvpj_vst2(convproj_obj, plugin_obj)
        #        return True
