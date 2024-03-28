# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import params_os_dragonfly_reverb
from functions_plugin_ext import params_os_airwindows
from functions import errorprint
from functions import xtramath

def reverb_calc_freq(freq): return 13.75**(1+(freq*2.821))

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['native-tracktion', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype, plugtransform):

        if plugin_obj.plugin_subtype == 'naturalReverb':
            vst2_use = 'vst2' in extplugtype and plugin_vst2.check_exists('id', 1684435505)
            if vst2_use:
                print("[plug-conv] Waveform to VST2: Natural Reverb > Dragonfly Hall Reverb:",pluginid)
                decay = plugin_obj.params.get('decay', 0).value
                definition = plugin_obj.params.get('definition', 0).value
                diffusion = plugin_obj.params.get('diffusion', 0).value
                highCut = plugin_obj.params.get('highCut', 0).value
                highDamp = plugin_obj.params.get('highDamp', 0).value
                lowCut = plugin_obj.params.get('lowCut', 0).value
                lowDamp = plugin_obj.params.get('lowDamp', 0).value
                mix = plugin_obj.params.get('mix', 0).value
                mixLock = plugin_obj.params.get('mixLock', 0).value
                pan = plugin_obj.params.get('pan', 0).value
                preDelay = plugin_obj.params.get('preDelay', 0).value
                size = plugin_obj.params.get('size', 0).value
                slope = plugin_obj.params.get('slope', 0).value

                lowCut = xtramath.clamp(reverb_calc_freq(lowCut), 0, 200)
                highCut = xtramath.clamp(reverb_calc_freq(highCut), 1000, 16000)
                size = 10+(size*50)
                decay = xtramath.clamp( ((decay*2)**3)*15, 0, 10)
                preDelay = xtramath.clamp(preDelay, 0, 100)

                data_dragonfly = params_os_dragonfly_reverb.dragonfly_hall_data()
                data_dragonfly.set_param('low_cut', lowCut)
                data_dragonfly.set_param('high_cut', highCut)
                data_dragonfly.set_param('size', size)
                data_dragonfly.set_param('decay', decay)
                data_dragonfly.set_param('delay', preDelay)
                data_dragonfly.set_param('diffuse', diffusion*100)
                data_dragonfly.set_param('dry_level',  (1-mix)*100)
                data_dragonfly.set_param('late_level', mix*100)
                data_dragonfly.to_cvpj_vst2(convproj_obj, plugin_obj)

        if plugin_obj.plugin_subtype == 'distortion':
            dtype = plugin_obj.params.get('dtype', 0).value
            drive = plugin_obj.params.get('drive', 0).value
            postGain = plugin_obj.params.get('postGain', 0).value
            if dtype not in [0, 5]:
                if plugin_vst2.check_exists('id', 1835758713):
                    airwindows_obj = params_os_airwindows.airwindows_data()
                    airwindows_obj.paramvals = [drive,postGain]
                    airwindows_obj.paramnames = ["In Trim","Out Pad"]
                    airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1835758713, False, True)
                else: errorprint.printerr('ext_notfound', ['VST2', 'Mackity [Airwindows]'])
            elif dtype == 0:
                if plugin_vst2.check_exists('id', 1685219702):
                    airwindows_obj = params_os_airwindows.airwindows_data()
                    airwindows_obj.paramvals = [drive, 0, postGain, 1]
                    airwindows_obj.paramnames = ["Drive","Highpass","Out Level","Dry/Wet"]
                    airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1685219702, True, True)
                else: errorprint.printerr('ext_notfound', ['VST2', 'Drive [Airwindows]'])
