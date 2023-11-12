# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv
from functions_plugdata import plugin_vital

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-piyopiyo', None, 'piyopiyo'], ['vst2', None, None], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        print('[plug-conv] Converting PiyoPiyo to Vital:',pluginid)
        vital_data = plugin_vital.vital_data(cvpj_plugindata)
        vital_data.setvalue('osc_1_on', 1)
        vital_data.setvalue('osc_1_level', 0.5)
        vital_data.setvalue('volume', 4000)
        vital_data.setvalue_timed('env_1_release', 20)
        vital_data.importcvpj_wave(cvpj_plugindata, 1, None)
        #vital_data.importcvpj_env_block(cvpj_plugindata, 1, 'vol')
        vital_data.importcvpj_env_points(cvpj_plugindata, 1, 'vol')
        vital_data.set_modulation(1, 'lfo_1', 'osc_1_level', 1, 0, 1, 0, 0)
        vital_data.to_cvpj_vst2()
        return True