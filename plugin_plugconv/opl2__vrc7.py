# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

vrc7patch = {}
vrc7patch[1] = [3,33,5,6,232,129,66,39]
vrc7patch[2] = [19,65,20,13,216,246,35,18]
vrc7patch[3] = [17,17,8,8,250,178,32,18]
vrc7patch[4] = [49,97,12,7,168,100,97,39]
vrc7patch[5] = [50,33,30,6,225,118,1,40]
vrc7patch[6] = [2,1,6,0,163,226,244,244]
vrc7patch[7] = [33,97,29,7,130,129,17,7]
vrc7patch[8] = [35,33,34,23,162,114,1,23]
vrc7patch[9] = [53,17,37,0,64,115,114,1]
vrc7patch[10] = [181,1,15,15,168,165,81,2]
vrc7patch[11] = [23,193,36,7,248,248,34,18]
vrc7patch[12] = [113,35,17,6,101,116,24,22]
vrc7patch[13] = [1,2,211,5,201,149,3,2]
vrc7patch[14] = [97,99,12,0,148,192,51,246]
vrc7patch[15] = [33,114,13,0,193,213,86,6]

import plugin_plugconv

from functions import plugins
from functions import data_bytes
from functions_plugparams import params_fm
import math
import struct

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['fm', 'vrc7', None], ['fm', 'opl2', None], False, True
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):
        print('[plug-conv] Converting VRC7 to OPL2:',pluginid)
        use_patch = plugins.get_plug_dataval(cvpj_l, pluginid, 'use_patch', False)
        patch = plugins.get_plug_dataval(cvpj_l, pluginid, 'patch', 0)
        vrcregs = plugins.get_plug_dataval(cvpj_l, pluginid, 'regs', [0,0,0,0,0,0,0,0])

        if use_patch == True: vrcregs = vrc7patch[patch]
        else: vrcregs = plugins.get_plug_dataval(cvpj_l, pluginid, 'regs', [0,0,0,0,0,0,0,0])

        vrc_mod_flags, vrc_mod_mul = data_bytes.splitbyte(vrcregs[0]) 
        vrc_mod_trem, vrc_mod_vib, vrc_mod_sust, vrc_mod_krs = data_bytes.to_bin(vrc_mod_flags, 4)
        vrc_car_flags, vrc_car_mul = data_bytes.splitbyte(vrcregs[1])
        vrc_car_trem, vrc_car_vib, vrc_car_sust, vrc_car_krs = data_bytes.to_bin(vrc_car_flags, 4)
        vrc_mod_kls = vrcregs[2] >> 6
        vrc_mod_out = vrcregs[2] & 0x3F
        vrc_car_kls = vrcregs[3] >> 6
        vrc_fb = vrcregs[3] & 0x07
        vrc_mod_wave = int(bool(vrcregs[3] & 0x08))
        vrc_car_wave = int(bool(vrcregs[3] & 0x10))
        vrc_mod_att, vrc_mod_dec = data_bytes.splitbyte(vrcregs[4]) 
        vrc_car_att, vrc_car_dec = data_bytes.splitbyte(vrcregs[5]) 
        vrc_mod_sus, vrc_mod_rel = data_bytes.splitbyte(vrcregs[6]) 
        vrc_car_sus, vrc_car_rel = data_bytes.splitbyte(vrcregs[7])

        plugins.replace_plug(cvpj_l, pluginid, 'fm', 'opl2')
        fmdata = params_fm.fm_data('opl2')

        fmdata.set_param('fm', 0)
        fmdata.set_param('feedback', vrc_fb)

        fmdata.set_op_param(0, 'env_attack', vrc_mod_att)
        fmdata.set_op_param(0, 'env_decay', vrc_mod_dec)
        fmdata.set_op_param(0, 'env_release', vrc_mod_rel)
        fmdata.set_op_param(0, 'env_sustain', vrc_mod_sus)
        fmdata.set_op_param(0, 'freqmul', vrc_mod_mul)
        fmdata.set_op_param(0, 'ksl', vrc_mod_kls)
        fmdata.set_op_param(0, 'ksr', vrc_mod_krs)
        fmdata.set_op_param(0, 'level', vrc_mod_out)
        fmdata.set_op_param(0, 'tremolo', vrc_mod_trem)
        fmdata.set_op_param(0, 'vibrato', vrc_mod_vib)
        fmdata.set_op_param(0, 'waveform', vrc_mod_wave)
        fmdata.set_op_param(0, 'sustained', vrc_mod_sust)

        fmdata.set_op_param(1, 'env_attack', vrc_car_att)
        fmdata.set_op_param(1, 'env_decay', (vrc_car_dec*-1)+15)
        fmdata.set_op_param(1, 'env_release', (vrc_car_rel*-1)+15)
        fmdata.set_op_param(1, 'env_sustain', vrc_car_sus)
        fmdata.set_op_param(1, 'freqmul', vrc_car_mul)
        fmdata.set_op_param(1, 'ksl', vrc_car_kls)
        fmdata.set_op_param(1, 'ksr', vrc_car_krs)
        fmdata.set_op_param(1, 'tremolo', vrc_car_trem)
        fmdata.set_op_param(1, 'vibrato', vrc_car_vib)
        fmdata.set_op_param(1, 'waveform', vrc_car_wave)
        fmdata.set_op_param(1, 'sustained', vrc_car_sust)

        fmdata.to_cvpj(cvpj_l, pluginid)

        return True