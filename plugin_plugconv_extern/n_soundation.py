# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import params_os_tal_filter
from functions_plugin_ext import params_os_airwindows
from functions import errorprint
from functions import xtramath

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['native-soundation', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype, plugtransform):

        if plugin_obj.plugin_subtype == 'com.soundation.distortion' and 'vst2' in extplugtype:
            mode = int(plugin_obj.params.get('mode', 0).value)
            gain = plugin_obj.params.get('gain', 0).value

            if mode in [0,4]:
                if plugin_vst2.check_exists('id', 1685219702):
                    print('[plug-conv] Soundation to VST2: Distortion > Drive [Airwindows]:',pluginid)
                    driveval = ((gain**0.2)*2)-1
                    drive = max(driveval, 0)
                    vol = min(driveval, 0)+1

                    airwindows_obj = params_os_airwindows.airwindows_data()
                    airwindows_obj.paramvals = [drive, 0, vol, 1]
                    airwindows_obj.paramnames = ["Drive","Highpass","Out Level","Dry/Wet"]
                    airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1685219702, True, True)
                    return True
                else: errorprint.printerr('ext_notfound', ['VST2', 'Drive [Airwindows]'])

            if mode in [1]:
                if plugin_vst2.check_exists('id', 1718772068):
                    print('[plug-conv] Soundation to VST2: Distortion > Fracture2 [Airwindows]:',pluginid)
                    airwindows_obj = params_os_airwindows.airwindows_data()
                    airwindows_obj.paramvals = [gain, 0.2, 0.5, 1, 1]
                    airwindows_obj.paramnames = ["Drive","Fractre","Thresh","Output","Dry/Wet"]
                    airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1718772068, True, True)
                    return True
                else: errorprint.printerr('ext_notfound', ['VST2', 'Fracture2 [Airwindows]'])

            if mode in [2,3]:
                if plugin_vst2.check_exists('id', 1685219702):
                    print('[plug-conv] Soundation to VST2: Distortion > Drive [Airwindows]:',pluginid)
                    airwindows_obj = params_os_airwindows.airwindows_data()
                    airwindows_obj.paramvals = [gain, 0, 1, 1]
                    airwindows_obj.paramnames = ["Drive","Highpass","Out Level","Dry/Wet"]
                    airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1685219702, True, True)
                    return True
                else: errorprint.printerr('ext_notfound', ['VST2', 'Drive [Airwindows]'])

        if plugin_obj.plugin_subtype == 'com.soundation.fakie' and 'vst2' in extplugtype:
            if plugin_vst2.check_exists('id', 808596837):
                print('[plug-conv] Soundation to VST2: Fakie > TAL-Filter-2:',pluginid)
                attack = plugin_obj.params.get('attack', 0).value
                depth = plugin_obj.params.get('depth', 0).value
                hold = plugin_obj.params.get('hold', 0).value
                release = plugin_obj.params.get('release', 0).value

                start_end = xtramath.clamp(attack, 0.001, 1)
                end_start = xtramath.clamp(attack+hold, 0.001, 1)
                end_end = xtramath.clamp(attack+hold+release, 0.001, 1)

                tal_obj = params_os_tal_filter.tal_filter_data()

                tal_obj.set_param('filtertypeNew', 0.2)
                tal_obj.set_param('speedFactor', 5)

                tal_obj.add_point(0, 1, 1, 0)
                tal_obj.add_point(start_end, 1-depth, 0, 0)
                tal_obj.add_point(end_start, 1-depth, 0, 0)
                tal_obj.add_point(end_end, 1, 0, 0)
                tal_obj.add_point(1, 1, 0, 1)
                tal_obj.to_cvpj_vst2(convproj_obj, plugin_obj)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'TAL-Filter-2'])

        if plugin_obj.plugin_subtype == 'com.soundation.reverb' and 'vst2' in extplugtype:
            if plugin_vst2.check_exists('id', 1836611170):
                print('[plug-conv] Soundation to VST2: Reverb > MatrixVerb [Airwindows]:',pluginid)
                damp = plugin_obj.params.get('damp', 0).value
                dry = plugin_obj.params.get('dry', 0).value
                size = plugin_obj.params.get('size', 0).value
                wet = plugin_obj.params.get('wet', 0).value
                mix = xtramath.wetdry(wet, dry)
                airwindows_obj = params_os_airwindows.airwindows_data()
                airwindows_obj.paramvals = [1, damp, 0, 0, 0.5, (size**2)/2, mix]
                airwindows_obj.paramnames = ["Filter","Damping","Speed","Vibrato","RmSize","Flavor","Dry/Wet"]
                airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1836611170, True, True)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'MatrixVerb [Airwindows]'])

        if plugin_obj.plugin_subtype == 'com.soundation.tremolo' and 'vst2' in extplugtype:
            if plugin_vst2.check_exists('id', 1635087472):
                print('[plug-conv] Soundation to VST2: Tremolo > AutoPan [Airwindows]:',pluginid)
                depth = plugin_obj.params.get('depth', 0).value
                phase = plugin_obj.params.get('phase', 0).value
                speed = plugin_obj.params.get('speed', 0).value
                airwindows_obj = params_os_airwindows.airwindows_data()
                airwindows_obj.paramvals = [speed**0.8, phase/2, 0, depth]
                airwindows_obj.paramnames = ["Rate","Phase","Wide","Dry/Wet"]
                airwindows_obj.to_cvpj_vst2(convproj_obj, plugin_obj, 1635087472, True, True)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'AutoPan [Airwindows]'])

        return False