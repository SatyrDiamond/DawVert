# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import params_os_dragonfly_reverb
from functions import xtramath

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['directx', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json, extplugtype):
        fx_on, fx_wet = plugin_obj.fxdata_get()

        if plugin_obj.plugin_subtype == 'Distortion' and extplugtype == 'vst2':
            print('[plug-conv] DirectX to VST2: Distortion > Edge:',pluginid)
            p_gain = plugin_obj.params.get('gain', 0).value
            p_edge = plugin_obj.params.get('edge', 0).value
            p_prelowpasscutoff = plugin_obj.params.get('prelowpasscutoff', 0).value

            a_gain = (p_gain*0.1)+0.1
            a_lo = p_prelowpasscutoff
            a_hi = 0
            airwindows_chunk = struct.pack('<fffff', a_gain, a_lo, a_hi, 1, 1)
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name','any', 'Edge', 'chunk', airwindows_chunk, None)
            return True

        if plugin_obj.plugin_subtype == 'I3DL2Reverb' and extplugtype == 'vst2':
            print("[plug-conv] DirectX to VST2: I3DL2Reverb > Dragonfly Hall Reverb:",pluginid)
            p_decayhfratio = plugin_obj.params.get("decayhfratio", 0).value
            p_decaytime = plugin_obj.params.get("decaytime", 0).value
            p_density = plugin_obj.params.get("density", 0).value
            p_diffusion = plugin_obj.params.get("diffusion", 0).value
            p_hfreference = plugin_obj.params.get("hfreference", 0).value
            p_quality = plugin_obj.params.get("quality", 0).value
            p_reflections = plugin_obj.params.get("reflections", 0).value
            p_reflectionsdelay = plugin_obj.params.get("reflectionsdelay", 0).value
            p_reverb = plugin_obj.params.get("reverb", 0).value
            p_reverbdelay = plugin_obj.params.get("reverbdelay", 0).value
            p_room = plugin_obj.params.get("room", 0).value
            p_roomhf = plugin_obj.params.get("roomhf", 0).value
            p_roomrollofffactor = plugin_obj.params.get("roomrollofffactor", 0).value

            data_dragonfly = params_os_dragonfly_reverb.dragonfly_hall_data()
            data_dragonfly.set_param('dry_level',  p_room*100)
            data_dragonfly.set_param('late_level', (p_reverb*p_room)*100)
            data_dragonfly.set_param('delay',      p_reverbdelay/10)
            data_dragonfly.set_param('diffuse',    p_diffusion*100)
            data_dragonfly.set_param('decay',      p_decaytime*20)

            data_dragonfly.to_cvpj_vst2(convproj_obj, plugin_obj)
            return True

        if plugin_obj.plugin_subtype == 'WavesReverb' and extplugtype == 'vst2':
            print("[plug-conv] DirectX to VST2: WavesReverb > Dragonfly Hall Reverb:",pluginid)
            p_ingain = plugin_obj.params.get('ingain', 0).value
            p_reverbmix = plugin_obj.params.get('reverbmix', 0).value
            p_reverbtime = plugin_obj.params.get('reverbtime', 0).value
            reverbvol = p_ingain**4
            reverbwet = p_reverbmix**18
            reverbdry = 1-reverbwet
            data_dragonfly = params_os_dragonfly_reverb.dragonfly_hall_data()
            data_dragonfly.set_param('dry_level',  (reverbdry*reverbvol)*100)
            data_dragonfly.set_param('late_level', (reverbwet*reverbvol)*100)
            data_dragonfly.set_param('decay',      p_reverbtime*3)
            data_dragonfly.to_cvpj_vst2(convproj_obj, plugin_obj)
            return True

        else: return False