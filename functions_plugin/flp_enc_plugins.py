# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import os
import math
import base64
from functions import data_bytes
from functions import plugins
from functions import plugin_vst2
from functions_plugin import flstudio_datadef
from functions_plugparams import datadef


def wrapper_addchunk(chunkid, chunkdata):
    return chunkid.to_bytes(4, "little") + len(chunkdata).to_bytes(4, "little") + b'\x00\x00\x00\x00' + chunkdata

def setparams(cvpj_l, pluginid):
    fl_plugin, fl_pluginparams = None, None
    plug_type = plugins.get_plug_type(cvpj_l, pluginid)

    if plug_type[0] == 'native-flstudio':
        fl_datadef = flstudio_datadef.get_datadef(plug_type[1])
        if fl_datadef != []:
            fl_plugin = plug_type[1]
            fl_pluginparams = datadef.from_plugdata(cvpj_l, pluginid, fl_datadef)

    if plug_type[0] == 'soundfont2':
        fl_plugin = 'fruity soundfont player'

        v_predelay, v_attack, v_hold, v_decay, v_sustain, v_release, v_amount = plugins.get_asdr_env(cvpj_l, pluginid, 'vol')
        p_predelay, p_attack, p_shape, p_speed_type, p_speed_time, p_amount = plugins.get_lfo(cvpj_l, pluginid, 'pitch')
        sf2_file = plugins.get_plug_dataval(cvpj_l, pluginid, 'file', '')
        sf2_bank = plugins.get_plug_dataval(cvpj_l, pluginid, 'bank', 0)
        sf2_patch = plugins.get_plug_dataval(cvpj_l, pluginid, 'patch', 0)

        if p_speed_type == 'seconds':
            flsf_lfo_predelay = int(p_predelay*256) if p_predelay != 0 else -1
            flsf_lfo_amount = int(p_amount*128) if p_amount != 0 else -1
            flsf_lfo_speed = int(6/p_speed_time)
        else:
            flsf_lfo_predelay = -1
            flsf_lfo_amount = -1
            flsf_lfo_speed = -1

        if v_amount == 0: flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R = -1, -1, -1, -1
        else: flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R = int(v_attack/1024), int(v_decay/1024), int(v_sustain/127), int(v_release/1024)

        fl_pluginparams = b''
        fl_pluginparams += struct.pack('iiiiii', *(2, sf2_patch+1, sf2_bank, 128, 128, 0) )
        fl_pluginparams += struct.pack('iiii', *(flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R) )
        fl_pluginparams += struct.pack('iiii', *(flsf_lfo_predelay, flsf_lfo_amount, flsf_lfo_speed, -1) )
        fl_pluginparams += len(sf2_file).to_bytes(1, "little")
        fl_pluginparams += sf2_file.encode('utf-8')
        fl_pluginparams += b'\xff\xff\xff\xff\x00\xff\xff\xff\xff\x00\x00'

    if plug_type[0] == 'vst2':
        vst_chunk = plugins.get_plug_dataval(cvpj_l, pluginid, 'chunk', '')
        vst_current_program = plugins.get_plug_dataval(cvpj_l, pluginid, 'current_program', 0)
        vst_datatype = plugins.get_plug_dataval(cvpj_l, pluginid, 'datatype', None)
        vst_fourid = plugins.get_plug_dataval(cvpj_l, pluginid, 'fourid', None)
        vst_name = plugins.get_plug_dataval(cvpj_l, pluginid, 'name', None)
        vst_path = plugins.get_plug_dataval(cvpj_l, pluginid, 'path', None)

        vstdata_bytes = base64.b64decode(vst_chunk)

        wrapper_state = b'\xf7\xff\xff\xff\r\xfe\xff\xff\xff' + len(vstdata_bytes).to_bytes(4, "little") + b'\x00\x00\x00\x00' + vst_current_program.to_bytes(4, "little") + vstdata_bytes

        wrapper_data = b'\n\x00\x00\x00'
        if vst_fourid != None: wrapper_data += wrapper_addchunk(51, data_bytes.swap32(vst_fourid).to_bytes(4, "little") )
        wrapper_data += wrapper_addchunk(57, b'`\t\x00\x00' )
        if vst_name != None: wrapper_data += wrapper_addchunk(54, vst_name.encode() )
        wrapper_data += wrapper_addchunk(55, vst_path.encode() )
        wrapper_data += wrapper_addchunk(53, wrapper_state )

        fl_plugin = 'fruity wrapper'
        fl_pluginparams = wrapper_data

    return fl_plugin, fl_pluginparams