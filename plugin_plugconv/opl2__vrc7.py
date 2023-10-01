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

        plugins.add_plug_param(cvpj_l, pluginid, "feedback", vrc_fb, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "percussive", 0, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "perctype", 0, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "tremolo_depth", 0, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "vibrato_depth", 0, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "fm", 1, 'int', "")

        plugins.add_plug_param(cvpj_l, pluginid, "mod_scale", vrc_mod_kls, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "mod_freqmul", vrc_mod_mul, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "mod_env_attack", (vrc_mod_att*-1)+15, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "mod_env_sustain", (vrc_mod_sus*-1)+15, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "mod_perc_env", 0, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "mod_env_decay", (vrc_mod_dec*-1)+15, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "mod_env_release", vrc_mod_rel, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "mod_level", (vrc_mod_out*-1)+63, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "mod_tremolo", vrc_mod_trem, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "mod_vibrato", vrc_mod_vib, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "mod_ksr", vrc_mod_krs, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "mod_waveform", vrc_mod_wave, 'int', "")

        plugins.add_plug_param(cvpj_l, pluginid, "car_scale", vrc_car_kls, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "car_freqmul", vrc_car_mul, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "car_env_attack", (vrc_car_att*-1)+15, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "car_env_sustain", (vrc_car_sus*-1)+15, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "car_perc_env", 0, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "car_env_decay", (vrc_car_dec*-1)+15, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "car_env_release", vrc_car_rel, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "car_level", 63, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "car_tremolo", vrc_car_trem, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "car_vibrato", vrc_car_vib, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "car_ksr", vrc_car_krs, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, "car_waveform", vrc_car_wave, 'int', "")
        return True