# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern
from functions_plugin_ext import params_os_vital
from functions import errorprint

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['namco163_famistudio', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype, plugtransform):
        print('[plug-conv] N163-Famistudio > Vital:',pluginid)
        if params_os_vital.checksupport(extplugtype):
            params_vital = params_os_vital.vital_data(plugin_obj)
            params_vital.setvalue('volume', 4000)
            params_vital.setvalue('osc_1_level', 0.5)
            params_vital.setvalue('osc_1_on', 1)
            params_vital.setvalue('osc_1_wave_frame', 128)
            params_vital.setvalue_timed('env_1_release', 0)
            params_vital.importcvpj_wavetable(0, 1, 'N163')
            params_vital.set_lfo(1, 2, [0, 1, 1, 0], [0, 0], False, '')
            params_vital.setvalue('lfo_1_frequency', 1.8)
            params_vital.setvalue('lfo_1_sync', 0.0)
            params_vital.setvalue('lfo_1_sync_type', 4.0)
            params_vital.set_modulation(1, 'lfo_1', 'osc_1_wave_frame', 1, 0, 1, 0, 0)
            ifvol = params_vital.importcvpj_env_block(2, 'vol')
            params_vital.setvalue('lfo_2_sync', 0.0)
            if ifvol: params_vital.set_modulation(2, 'lfo_2', 'osc_1_level', 1, 0, 1, 0, 0)
            params_vital.to_cvpj_any(convproj_obj, extplugtype)
            return True
        else: errorprint.printerr('ext_notfound', ['VST', 'Vital'])
