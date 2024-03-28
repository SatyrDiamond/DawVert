# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import data_nullbytegroup
from functions import errorprint

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['native-amped', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype, plugtransform):
        global loaded_plugtransform
        global plugts_obj

        if plugin_obj.plugin_subtype == 'Reverb' and 'vst2' in extplugtype:
            if plugin_vst2.check_exists('id', 1279878002):
                print("[plug-conv] Amped to VST2: Reverb > Castello Reverb:",pluginid)
                plugtransform.transform('./data_plugts/amped_vst2.pltr', 'vst2_reverb', convproj_obj, plugin_obj, pluginid, dv_config)
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1279878002, 'chunk', 
                    data_nullbytegroup.make(
                        [{'ui_size': ''}, 
                        {
                        'mix': str(plugtransform.get_storedval('mix')), 
                        'size': str(plugtransform.get_storedval('fb')), 
                        'brightness': str(plugtransform.get_storedval('lpf'))
                        }]), 
                    None)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'Castello Reverb'])

        elif plugin_obj.plugin_subtype == 'Distortion' and 'vst2' in extplugtype:
            distmode = plugin_obj.params.get('mode', 0).value
            boost = plugin_obj.params.get('boost', 0).value
            mix = plugin_obj.params.get('mix', 0).value

            if distmode in [0,1,4,5,6,7,8]:
                if plugin_vst2.check_exists('id', 1685219702):
                    print('[plug-conv] Amped to VST2: Density > Airwindows Density:',pluginid)
                    p_density = 0.2+(boost*0.3)
                    p_outlvl = 1-(boost*(0.3 if distmode != 5 else 0.2))
                    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1685219702, 'chunk', struct.pack('<ffff', p_density, 0, p_outlvl, 1), 0)
                else: errorprint.printerr('ext_notfound', ['VST2', 'Density [Airwindows]'])

            if distmode in [2,3]:
                if plugin_vst2.check_exists('id', 1685219702):
                    print('[plug-conv] Amped to VST2: Distortion > Airwindows Drive:',pluginid)
                    p_drive = [0.6,0.8,1][int(boost)]
                    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1685219702, 'chunk', struct.pack('<ffff', p_drive, 0, 0.5, 1), 0)
                else: errorprint.printerr('ext_notfound', ['VST2', 'Drive [Airwindows]'])

            plugin_obj.params_slot.add('wet', mix, 'float')

        elif plugin_obj.plugin_subtype == 'CompressorMini':
            if plugin_vst2.check_exists('id', 1886745457):
                print('[plug-conv] Amped to VST2: CompressorMini > Airwindows PurestSquish:',pluginid)
                squash = plugin_obj.params.get('squash', 0).value
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1886745457, 'chunk', struct.pack('<ffff', squash/2, 0, 1, 1), 0)
            else: errorprint.printerr('ext_notfound', ['VST2', 'PurestSquish [Airwindows]'])

        else: return False