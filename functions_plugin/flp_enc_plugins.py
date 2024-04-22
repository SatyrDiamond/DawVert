# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import os
import math
import base64
from functions import data_bytes
from functions import data_values

def wrapper_addchunk(chunkid, chunkdata):
    return chunkid.to_bytes(4, "little") + len(chunkdata).to_bytes(4, "little") + b'\x00\x00\x00\x00' + chunkdata

def setparams(convproj_obj, plugin_obj, datadef, dataset):
    fl_plugin, fl_pluginparams = None, None
    plug_type = plugin_obj.type_get()

    if plugin_obj.check_wildmatch('native-flstudio', 'fruity vocoder'):
        fl_plugin = 'fruity vocoder'

        p_bands = plugin_obj.datavals.get('bands', [1,1,1,1])
        p_filter = plugin_obj.datavals.get('filter', 2)
        p_left_right = plugin_obj.datavals.get('left_right', 0)

        p_freq_min = plugin_obj.params.get('freq_min', 0).value
        p_freq_max = plugin_obj.params.get('freq_max', 65536).value
        p_freq_scale = plugin_obj.params.get('freq_scale', 64).value
        p_freq_invert = int(plugin_obj.params.get('freq_invert', 0).value)
        p_freq_formant = plugin_obj.params.get('freq_formant', 0).value
        p_freq_bandwidth = plugin_obj.params.get('freq_bandwidth', 50).value
        p_env_att = plugin_obj.params.get('env_att', 1000).value
        p_env_rel = plugin_obj.params.get('env_rel', 100).value
        p_mix_mod = plugin_obj.params.get('mix_mod', 0).value
        p_mix_car = plugin_obj.params.get('mix_car', 0).value
        p_mix_wet = plugin_obj.params.get('mix_wet', 128).value

        fl_pluginparams = b''
        fl_pluginparams += struct.pack('iiiib', 2, len(p_bands), p_filter, 2, p_left_right)
        fl_pluginparams += struct.pack('f'*len(p_bands), *p_bands)
        fl_pluginparams += struct.pack('i'*12, p_freq_min, p_freq_max, p_freq_scale, p_freq_invert, p_freq_formant, p_freq_bandwidth, p_env_att, p_env_rel, 0, p_mix_mod, p_mix_car, p_mix_wet)

    if plugin_obj.check_wildmatch('native-flstudio', None):
        datadef_struct = dataset.object_var_get('datadef_struct', 'plugin', plug_type[1])
        if datadef_struct[0]:
            dictdata = plugin_obj.param_dict_dataset_set(dataset, 'plugin', plug_type[1])
            fl_plugin = plug_type[1]
            datadef.create(datadef_struct[1], dictdata)
            fl_pluginparams = datadef.bytestream.getvalue()
        #else:
        #    fl_pluginparams = plugin_obj.rawdata_get('fl')

    if plugin_obj.check_wildmatch('soundfont2', None):
        fl_plugin = 'fruity soundfont player'

        asdr_vol = plugin_obj.env_asdr_get('vol')
        lfo_pitch = plugin_obj.lfo_get('pitch')

        ref_found, fileref_obj = plugin_obj.get_fileref('file', convproj_obj)
        sf2_file = fileref_obj.get_path('win', True) if ref_found else ''
        sf2_bank, sf2_patch = plugin_obj.midi.to_sf2()

        flsf_lfo_predelay = int(lfo_pitch.predelay*256) if lfo_pitch.predelay != 0 else -1
        flsf_lfo_amount = int(lfo_pitch.amount*128) if lfo_pitch.amount != 0 else -1
        flsf_lfo_speed = int(6/lfo_pitch.time.speed_seconds)

        if asdr_vol.amount == 0: flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R = -1, -1, -1, -1
        else: flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R = int(asdr_vol.attack/1024), int(asdr_vol.decay/1024), int(asdr_vol.sustain/127), int(asdr_vol.release/1024)

        fl_pluginparams = b''
        fl_pluginparams += struct.pack('iiiiii', *(2, sf2_patch+1, sf2_bank, 128, 128, 0) )
        fl_pluginparams += struct.pack('iiii', *(flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R) )
        fl_pluginparams += struct.pack('iiii', *(flsf_lfo_predelay, flsf_lfo_amount, flsf_lfo_speed, -1) )
        fl_pluginparams += len(sf2_file).to_bytes(1, "little")
        fl_pluginparams += sf2_file.encode('utf-8')
        fl_pluginparams += b'\xff\xff\xff\xff\x00\xff\xff\xff\xff\x00\x00'

    if plugin_obj.check_wildmatch('vst2', None):
        vst_programs = plugin_obj.datavals.get('programs', '')
        vst_numparams = plugin_obj.datavals.get('numparams', 0)
        vst_current_program = plugin_obj.datavals.get('current_program', -1)
        vst_use_program = plugin_obj.datavals.get('use_program', True)
        vst_datatype = plugin_obj.datavals.get('datatype', 'chunk')
        vst_fourid = plugin_obj.datavals.get('fourid', None)
        vst_name = plugin_obj.datavals.get('name', None)

        ref_found, fileref_obj = plugin_obj.get_fileref('plugin', convproj_obj)
        vst_path = fileref_obj.get_path('win', True) if ref_found else None

        vstdata_bytes = plugin_obj.rawdata_get('chunk')

        if vst_datatype == 'chunk':

            if vst_current_program >= 0:
                wrapper_state = b'\xf7\xff\xff\xff\r\xfe\xff\xff\xff' + len(vstdata_bytes).to_bytes(4, "little") + b'\x00\x00\x00\x00' + vst_current_program.to_bytes(4, "little") + vstdata_bytes
            else:
                wrapper_state = b'\xf7\xff\xff\xff\x0c\xfe\xff\xff\xff' + len(vstdata_bytes).to_bytes(4, "little") + b'\x00\x00\x00\x00\xfe\xff\xff\xff' + vstdata_bytes

        if vst_datatype == 'bank':
            wrapper_state = b'\xf7\xff\xff\xff\x05\xfe\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

            vst_total_params = 0
            vst_params_data = b''
            vst_num_names = len(vst_programs)
            vst_names = b''

            for vst_program in vst_programs:
                vst_total_params += vst_program['numparams']
                for num in range(vst_program['numparams']):
                    vst_params_data += struct.pack('f', vst_program['params'][str(num)]['value'])
                vst_names += data_bytes.makestring_fixedlen(vst_program['program_name'], 25)

            wrapper_state += vst_total_params.to_bytes(4, "little")
            wrapper_state += vst_params_data
            wrapper_state += vst_num_names.to_bytes(4, "little")
            wrapper_state += vst_names

        if vst_datatype == 'param':
            wrapper_state = b'\xf7\xff\xff\xff\x05\xfe\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

            vst_total_params = vst_numparams
            vst_params_data = b''
            
            for num in range(vst_numparams):
                param_obj = plugin_obj.params.get('ext_param_'+str(num), 0)
                vst_params_data += struct.pack('f', param_obj.value)
            vst_num_names = 1
            vst_names = data_bytes.makestring_fixedlen('Converted', 25)

            wrapper_state += vst_total_params.to_bytes(4, "little")
            wrapper_state += vst_params_data
            wrapper_state += vst_num_names.to_bytes(4, "little")
            wrapper_state += vst_names


        wrapper_data = b'\n\x00\x00\x00'
        #if vst_fourid != None: wrapper_data += wrapper_addchunk(51, data_bytes.swap32(vst_fourid).to_bytes(4, "little") )
        wrapper_data += wrapper_addchunk(57, b'`\t\x00\x00' )
        #if vst_name != None: wrapper_data += wrapper_addchunk(54, vst_name.encode() )
        if vst_path != None: wrapper_data += wrapper_addchunk(55, vst_path.encode() )
        wrapper_data += wrapper_addchunk(53, wrapper_state )

        fl_plugin = 'fruity wrapper'
        fl_pluginparams = wrapper_data

    #if plug_type[0] == 'vst3':
    #    vst_chunk = plugin_obj.rawdata_get()
    #    vst_id = plugin_obj.datavals.get('guid', None)
    #    vst_name = plugin_obj.datavals.get('name', None)
    #    vst_path = plugin_obj.datavals.get('path', None)
    #    vst_numparams = plugin_obj.datavals.get('numparams', None)

    #    if vst_numparams != None:
    #        wrapper_state = b'\x01\x00\x00\x00\x01\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    #        wrapper_state += wrapper_addchunk(3, vst_chunk)
    #        fourchunkdata = vst_numparams.to_bytes(4, "little")
    #        for paramnum in range(vst_numparams):
    #            fourchunkdata += paramnum.to_bytes(4, "little")
    #        wrapper_state += wrapper_addchunk(4, fourchunkdata)
    #        wrapper_data = b'\n\x00\x00\x00'

    #        print(54, vst_name.encode())
    #        print(55, vst_path.encode())

    #        if vst_name != None: wrapper_data += wrapper_addchunk(54, vst_name.encode() )
    #        if vst_path != None: wrapper_data += wrapper_addchunk(55, vst_path.encode() )

    #        wrapper_data += wrapper_addchunk(53, wrapper_state )
    #        #print(wrapper_state.hex())
    #        fl_plugin = 'fruity wrapper'
    #        fl_pluginparams = wrapper_data

    return fl_plugin, fl_pluginparams