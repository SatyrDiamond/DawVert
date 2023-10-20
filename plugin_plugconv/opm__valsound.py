# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import plugins
from functions import data_bytes
from functions import idvals

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['valsound', None, None], ['fm', 'opm', None], False, True
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):
        print('[plug-conv] Converting Valsound ['+plugintype[1]+'] to OPM:',pluginid)

        idvaldata = None
        if idvaldata == None: idvaldata = idvals.parse_idvalscsv('data_idvals/valsound_opm.csv')

        valsound = plugintype[1]

        opm_main = idvals.get_idval(idvaldata, valsound, 'opm_main')
        opm_op1 = idvals.get_idval(idvaldata, valsound, 'opm_op1')
        opm_op2 = idvals.get_idval(idvaldata, valsound, 'opm_op2')
        opm_op3 = idvals.get_idval(idvaldata, valsound, 'opm_op3')
        opm_op4 = idvals.get_idval(idvaldata, valsound, 'opm_op4')

        opm_main = [int(i) for i in opm_main.split(',')]
        opm_op1 = [int(i) for i in opm_op1.split(',')]
        opm_op2 = [int(i) for i in opm_op2.split(',')]
        opm_op3 = [int(i) for i in opm_op3.split(',')]
        opm_op4 = [int(i) for i in opm_op4.split(',')]

        plugins.add_plug_param(cvpj_l, pluginid, 'algorithm', opm_main[0], 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'feedback', opm_main[1], 'int', "")

        opdata = [opm_op1, opm_op2, opm_op3, opm_op4]

        for opnum in range(4):
            op_data = opdata[opnum]
            op_num = 'op'+str(opnum)

            plugins.add_plug_param(cvpj_l, pluginid, op_num+'_env_attack', op_data[0], 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, op_num+'_env_decay', op_data[1], 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, op_num+'_env_decay2', op_data[2], 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, op_num+'_env_release', op_data[3], 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, op_num+'_env_sustain', op_data[4], 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, op_num+'_level', op_data[5], 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, op_num+'_keyscale', op_data[6], 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, op_num+'_freqmul', op_data[7], 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, op_num+'_detune', op_data[8], 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, op_num+'_detune2', op_data[9], 'int', "")

        return True