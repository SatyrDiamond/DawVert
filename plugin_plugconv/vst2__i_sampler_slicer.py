# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import plugin_vst2
from functions_plugparams import params_ninjas2
from functions_plugparams import data_nullbytegroup

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['sampler', 'slicer', None], ['vst2', None, None], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):
        print('[plug-conv] Converting Slicer to Ninjas 2:',pluginid)
        params_ninjas2.initparams()
        params_ninjas2.slicerdata(cvpj_l, pluginid)
        ninjas2out = params_ninjas2.getparams()
        plugin_vst2.replace_data(cvpj_l, pluginid, 'name','any', 'Ninjas 2', 'chunk', data_nullbytegroup.make(ninjas2out), None)
        return True