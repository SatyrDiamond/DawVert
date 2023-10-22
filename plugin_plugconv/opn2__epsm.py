# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import plugins
from functions import idvals
from functions_plugparams import params_fm

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['fm', 'epsm', None], ['fm', 'opn2', None], False, True
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):
        epsmregs = plugins.get_plug_dataval(cvpj_l, pluginid, 'regs', None)

        if epsmregs != None:
            print('[plug-conv] Converting EPSM to OPN2:',pluginid)
            epsmopregs = [epsmregs[2:9], epsmregs[9:16], epsmregs[16:23], epsmregs[23:30]]

            plugins.replace_plug(cvpj_l, pluginid, 'fm', 'opn2')
            fmdata = params_fm.fm_data('opn2')

            fmdata.set_param('algorithm', epsmregs[0]&0x0F)
            fmdata.set_param('feedback', ((epsmregs[0]>>3)*2)+1)
            fmdata.set_param('fms', epsmregs[1]&0x0F)
            fmdata.set_param('ams', (epsmregs[1]>>4)&0x03)
            fmdata.set_param('lfo_enable', epsmregs[30]>>3)
            fmdata.set_param('lfo_frequency', epsmregs[30]&0x07)

            for opnum in range(4):
                op_reg = epsmopregs[opnum]
                fmdata.set_op_param(opnum, 'am', op_reg[3] >> 7)
                fmdata.set_op_param(opnum, 'detune', op_reg[0] >> 4)
                fmdata.set_op_param(opnum, 'env_attack', op_reg[2] & 0x3F)
                fmdata.set_op_param(opnum, 'env_decay', op_reg[3] & 0x3F)
                fmdata.set_op_param(opnum, 'env_decay2', op_reg[4])
                fmdata.set_op_param(opnum, 'env_release', op_reg[5] & 0x0F)
                fmdata.set_op_param(opnum, 'env_sustain', op_reg[5] >> 4)
                fmdata.set_op_param(opnum, 'freqmul', op_reg[0] & 0x0F)
                fmdata.set_op_param(opnum, 'level', (op_reg[1]*-1)+127)
                fmdata.set_op_param(opnum, 'ratescale', op_reg[2] >> 6)
                fmdata.set_op_param(opnum, 'ssg_enable', op_reg[6] >> 3)
                fmdata.set_op_param(opnum, 'ssg_mode', op_reg[6] & 0x08)

            fmdata.to_cvpj(cvpj_l, pluginid)

        return True