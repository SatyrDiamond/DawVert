# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import plugins
from functions import data_bytes

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['namco163_famistudio', None, None], ['vst2', None, None], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):
        print('[plug-conv] Converting N163-Famistudio to Vital:',pluginid)
        params_vital.create()
        params_vital.setvalue('volume', 4000)
        params_vital.setvalue('osc_1_level', 0.5)
        params_vital.setvalue('osc_1_on', 1)
        params_vital.setvalue('osc_1_wave_frame', 128)
        params_vital.setvalue_timed('env_1_release', 0)
        params_vital.importcvpj_wavetable(cvpj_l, pluginid, 0, 1, None)

        params_vital.set_lfo(1, 2, [0, 1, 1, 0], [0, 0], False, '')
        params_vital.setvalue('lfo_1_frequency', 1.8)
        params_vital.setvalue('lfo_1_sync', 0.0)
        params_vital.setvalue('lfo_1_sync_type', 4.0)
        params_vital.set_modulation(1, 'lfo_1', 'osc_1_wave_frame', 1, 0, 1, 0, 0)

        ifvol = params_vital.importcvpj_env_block(cvpj_l, pluginid, 2, 'vol')
        params_vital.setvalue('lfo_2_sync', 0.0)
        if ifvol: params_vital.set_modulation(2, 'lfo_2', 'osc_1_level', 1, 0, 1, 0, 0)

        vitaldata = params_vital.getdata()
        plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Vital', 'chunk', vitaldata.encode('utf-8'), None)
        return True
