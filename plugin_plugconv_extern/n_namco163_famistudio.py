# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern
from functions_plugin_ext import params_os_vital

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['namco163_famistudio', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json, extplugtype):
        print('[plug-conv] N163-Famistudio > Vital:',pluginid)
        vital_data = params_os_vital.vital_data(plugin_obj)

        if extplugtype == 'vst2':
            vital_data.setvalue('volume', 4000)
            vital_data.setvalue('osc_1_level', 0.5)
            vital_data.setvalue('osc_1_on', 1)
            vital_data.setvalue('osc_1_wave_frame', 128)
            vital_data.setvalue_timed('env_1_release', 0)
            vital_data.importcvpj_wavetable(0, 1, 'N163')
            vital_data.set_lfo(1, 2, [0, 1, 1, 0], [0, 0], False, '')
            vital_data.setvalue('lfo_1_frequency', 1.8)
            vital_data.setvalue('lfo_1_sync', 0.0)
            vital_data.setvalue('lfo_1_sync_type', 4.0)
            vital_data.set_modulation(1, 'lfo_1', 'osc_1_wave_frame', 1, 0, 1, 0, 0)
            ifvol = vital_data.importcvpj_env_block(2, 'vol')
            vital_data.setvalue('lfo_2_sync', 0.0)
            if ifvol: vital_data.set_modulation(2, 'lfo_2', 'osc_1_level', 1, 0, 1, 0, 0)
            vital_data.to_cvpj_vst2(convproj_obj)
            return True
