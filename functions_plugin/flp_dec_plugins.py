# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import os
import math
from functions import data_bytes
from functions import data_values
from functions import plugins
from functions import plugin_vst2
from functions_plugin import flstudio_datadef
from functions_plugparams import datadef
from io import BytesIO

def decode_pointdata(fl_plugstr):
    autoheader = struct.unpack('bii', fl_plugstr.read(12))
    pointdata_table = []

    positionlen = 0
    for num in range(autoheader[2]):
        chunkdata = struct.unpack('ddfbbbb', fl_plugstr.read(24))
        positionlen += round(chunkdata[0], 6)
        pointdata_table.append( [positionlen, chunkdata[1:], 0.0, 0] )
        if num != 0:
            pointdata_table[num-1][2] = chunkdata[2]
            pointdata_table[num-1][3] = chunkdata[3]

    fl_plugstr.read(20).hex()
    return pointdata_table

envshapes = {
    0: 'normal',
    1: 'doublecurve',
    2: 'instant',
    3: 'stairs',
    4: 'smooth_stairs',
    5: 'pulse',
    6: 'wave',
    7: 'curve2',
    8: 'doublecurve2',
    9: 'halfsine',
    10: 'smooth',
    11: 'curve3',
    12: 'doublecurve3',
}

def getparams(cvpj_l, pluginid, pluginname, chunkpdata, foldername):
    fl_plugstr = BytesIO(chunkpdata)
    pluginname = pluginname.lower()

    # ------------------------------------------------------------------------------------------- VST
    if pluginname == 'fruity wrapper':
        fl_plugstr.seek(0,2)
        fl_plugstr_size = fl_plugstr.tell()
        fl_plugstr.seek(0)
        fl_plugstr.read(4)


        wrapperdata = {}
        while fl_plugstr.tell() < fl_plugstr_size:


            chunktype = int.from_bytes(fl_plugstr.read(4), "little")
            chunksize = int.from_bytes(fl_plugstr.read(4), "little")
            fl_plugstr.read(4)
            chunkdata = fl_plugstr.read(chunksize)
            if chunktype == 1: wrapperdata['midi'] = chunkdata
            if chunktype == 2: wrapperdata['flags'] = chunkdata
            if chunktype == 30: wrapperdata['io'] = chunkdata
            if chunktype == 32: wrapperdata['outputs'] = chunkdata
            if chunktype == 50: wrapperdata['plugin_info'] = chunkdata
            if chunktype == 51: wrapperdata['fourid'] = int.from_bytes(chunkdata, "little")
            if chunktype == 53: wrapperdata['state'] = chunkdata
            if chunktype == 54: wrapperdata['name'] = chunkdata.decode()
            if chunktype == 55: wrapperdata['file'] = chunkdata.decode()
            if chunktype == 56: wrapperdata['vendor'] = chunkdata.decode()
            if chunktype == 57: wrapperdata['57'] = chunkdata

        if 'plugin_info' in wrapperdata:
            wrapper_vsttype = int.from_bytes(wrapperdata['plugin_info'][0:4], "little")
            if 'fourid' in wrapperdata:
                pluginstate = wrapperdata['state']
                print(wrapperdata['name'], pluginstate)
                wrapper_vststate = pluginstate[0:9]
                wrapper_vstsize = int.from_bytes(pluginstate[9:13], "little")
                wrapper_vstpad = pluginstate[13:17]
                wrapper_vstprogram = int.from_bytes(pluginstate[17:21], "little")
                wrapper_vstdata = pluginstate[21:]

                if wrapper_vststate == b'\xf7\xff\xff\xff\r\xfe\xff\xff\xff':
                    plugin_vst2.replace_data(cvpj_l, pluginid, 'name' ,'win', wrapperdata['name'], 'chunk', wrapper_vstdata, 0)
                    plugins.add_plug_data(cvpj_l, pluginid, 'current_program', wrapper_vstprogram)

                if wrapper_vststate == b'\xf7\xff\xff\xff\x05\xfe\xff\xff\xff':
                    stream_data = BytesIO(wrapper_vstdata)
                    vst_total_params = int.from_bytes(stream_data.read(4), "little")
                    vst_params_data = struct.unpack('f'*vst_total_params, stream_data.read(4*vst_total_params))
                    vst_num_names = int.from_bytes(stream_data.read(4), "little")
                    vst_names = []
                    for _ in range(vst_num_names):
                        vst_names.append( data_bytes.readstring_fixedlen(stream_data, 25, 'utf-8') )

                    numparamseach = vst_total_params//vst_num_names
                    bankparams = data_values.list_chunks(vst_params_data, numparamseach)

                    cvpj_programs = []
                    for num in range(vst_num_names):
                        cvpj_program = {}
                        cvpj_program['datatype'] = 'params'
                        cvpj_program['numparams'] = numparamseach
                        cvpj_program['params'] = {}
                        for paramnum in range(numparamseach):
                            cvpj_program['params'][str(paramnum)] = {'value': bankparams[num][paramnum]}
                        cvpj_program['program_name'] = vst_names[num]
                        cvpj_programs.append(cvpj_program)

                    plugin_vst2.replace_data(cvpj_l, pluginid, 'name' ,'win', wrapperdata['name'], 'bank', cvpj_programs, None)
                    plugins.add_plug_data(cvpj_l, pluginid, 'current_program', wrapper_vstprogram)

        return True

    elif pluginname == 'fruity compressor':
        flplugvals = struct.unpack('i'*8, chunkpdata)
        v_threshold = flplugvals[1]/10
        v_ratio = flplugvals[2]/10
        v_gain = flplugvals[3]/10
        v_attack = flplugvals[4]/10000
        v_release = flplugvals[5]/1000
        v_type = flplugvals[6]
        first_type = v_type>>2
        second_type = v_type%4
        if second_type == 0: v_knee = 0
        if second_type == 1: v_knee = 6
        if second_type == 2: v_knee = 7
        if second_type == 3: v_knee = 15
        if first_type == 0: v_tcr = 0
        if first_type == 1: v_tcr = 1

        plugins.add_plug(cvpj_l, pluginid, 'universal', 'compressor')
        plugins.add_plug_data(cvpj_l, pluginid, 'tcr', bool(v_tcr) )
        plugins.add_plug_param(cvpj_l, pluginid, 'pregain', v_gain, 'float', 'pregain')
        plugins.add_plug_param(cvpj_l, pluginid, 'ratio', v_ratio, 'float', 'ratio')
        plugins.add_plug_param(cvpj_l, pluginid, 'threshold', v_threshold, 'float', 'threshold')
        plugins.add_plug_param(cvpj_l, pluginid, 'attack', v_attack, 'float', 'attack')
        plugins.add_plug_param(cvpj_l, pluginid, 'release', v_release, 'float', 'release')
        plugins.add_plug_param(cvpj_l, pluginid, 'knee', v_knee, 'float', 'knee')
        return True

    # ------------------------------------------------------------------------------------------- Inst

    elif pluginname in ['fruity soundfont player', 'soundfont player']:
        # flsf_asdf_A max 5940 - flsf_asdf_D max 5940 - flsf_asdf_S max 127 - flsf_asdf_R max 5940
        # flsf_lfo_predelay max 5900 - flsf_lfo_amount max 127 - flsf_lfo_speed max 127 - flsf_cutoff max 127
        flsf_vers, flsf_patch, flsf_bank, flsf_reverb_sendlvl, flsf_chorus_sendlvl, flsf_mod = struct.unpack('iiiiii', fl_plugstr.read(24))

        flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R = struct.unpack('iiii', fl_plugstr.read(16))
        flsf_lfo_predelay, flsf_lfo_amount, flsf_lfo_speed, flsf_cutoff = struct.unpack('iiii', fl_plugstr.read(16))
        flsf_filelen = int.from_bytes(fl_plugstr.read(1), "little")
        flsf_filename = fl_plugstr.read(flsf_filelen).decode('utf-8')
        flsf_reverb_sendto, flsf_reverb_builtin = struct.unpack('ib', fl_plugstr.read(5))
        flsf_chorus_sendto, flsf_chorus_builtin = struct.unpack('ib', fl_plugstr.read(5))
        flsf_hqrender = int.from_bytes(fl_plugstr.read(1), "little")

        plugins.add_plug(cvpj_l, pluginid, 'soundfont2', None)

        #plugins.add_plug_data(cvpj_l, pluginid, 'reverb_enabled', flsf_reverb_builtin)
        #plugins.add_plug_data(cvpj_l, pluginid, 'chorus_enabled', flsf_chorus_builtin)

        asdflfo_att = flsf_asdf_A/1024 if flsf_asdf_A != -1 else 0
        asdflfo_dec = flsf_asdf_D/1024 if flsf_asdf_D != -1 else 0
        asdflfo_sus = flsf_asdf_S/127 if flsf_asdf_S != -1 else 1
        asdflfo_rel = flsf_asdf_R/1024 if flsf_asdf_R != -1 else 0
        asdflfo_amt = int( (flsf_asdf_A == flsf_asdf_D == flsf_asdf_S == flsf_asdf_R == -1) == False )

        plugins.add_plug_data(cvpj_l, pluginid, 'file', flsf_filename)

        plugins.add_asdr_env(cvpj_l, pluginid, 'vol', 0, asdflfo_att, 0, asdflfo_dec, asdflfo_sus, asdflfo_rel, asdflfo_amt)

        if flsf_patch > 127:
            plugins.add_plug_data(cvpj_l, pluginid, 'bank', 128)
            plugins.add_plug_data(cvpj_l, pluginid, 'patch', flsf_patch-128)
        else:
            plugins.add_plug_data(cvpj_l, pluginid, 'bank', flsf_bank)
            plugins.add_plug_data(cvpj_l, pluginid, 'patch', flsf_patch)
        
        pitch_amount = flsf_lfo_amount/128 if flsf_lfo_amount != -128 else 0
        pitch_predelay = flsf_lfo_predelay/256 if flsf_lfo_predelay != -1 else 0
        pitch_speed = 1/(flsf_lfo_speed/6) if flsf_lfo_speed != -1 else 1

        #if flsf_vers == 6:
        #    continue
        #    newsf2data = struct.unpack('<bbiii', fl_plugstr.read(14))

        plugins.add_lfo(cvpj_l, pluginid, 'pitch', 'sine', 'seconds', pitch_speed, pitch_predelay, 0, pitch_amount)
        return True

    elif pluginname == 'fruity slicer':
        plugins.add_plug(cvpj_l, pluginid, 'sampler', 'slicer')
        fl_plugstr.read(4)
        slicer_beats = struct.unpack('f', fl_plugstr.read(4))[0]
        slicer_bpm = struct.unpack('f', fl_plugstr.read(4))[0]
        slicer_pitch, slicer_fitlen, slicer_stretchtype, slicer_att, slicer_dec = struct.unpack('iiiii', fl_plugstr.read(20))

        stretch_data = {}
        stretch_data['multiplier'] = pow(2, slicer_fitlen/10000)

        if slicer_stretchtype == 0: stretch_data['stretch_algorithm'] = 'fill_gaps'
        if slicer_stretchtype == 1: stretch_data['stretch_algorithm'] = 'alt_fill_gaps'
        if slicer_stretchtype == 2: stretch_data['stretch_algorithm'] = 'elastique_pro'
        if slicer_stretchtype == 3: stretch_data['stretch_algorithm'] = 'elastique_pro_transient'
        if slicer_stretchtype == 4: stretch_data['stretch_algorithm'] = 'elastique_v2_transient'
        if slicer_stretchtype == 5: stretch_data['stretch_algorithm'] = 'elastique_v2_tonal'
        if slicer_stretchtype == 6: stretch_data['stretch_algorithm'] = 'elastique_v2_mono'
        if slicer_stretchtype == 7: stretch_data['stretch_algorithm'] = 'elastique_v2_speech'

        slicer_filelen = int.from_bytes(fl_plugstr.read(1), "little")

        slicer_filename = fl_plugstr.read(slicer_filelen).decode('utf-8')
        if slicer_filename != "": 
            plugins.add_plug_data(cvpj_l, pluginid, 'file', slicer_filename)
        slicer_numslices = int.from_bytes(fl_plugstr.read(4), "little")

        cvpj_slices = []
        for _ in range(slicer_numslices):
            sd = {}
            slicer_slicenamelen = int.from_bytes(fl_plugstr.read(1), "little")
            slicer_slicename = fl_plugstr.read(slicer_slicenamelen).decode('utf-8')
            slicer_s_slice = struct.unpack('iihBBB', fl_plugstr.read(13))
            if slicer_slicename != "": sd['file'] = slicer_slicename
            sd['pos'] = slicer_s_slice[0]
            if slicer_s_slice[1] != -1: sd['note'] = slicer_s_slice[1]
            sd['reverse'] = slicer_s_slice[5]
            cvpj_slices.append(sd)

        for slicenum in range(len(cvpj_slices)):
            if slicenum-1 >= 0 and slicenum != len(cvpj_slices): cvpj_slices[slicenum-1]['end'] = cvpj_slices[slicenum]['pos']-1
            if slicenum == len(cvpj_slices)-1: cvpj_slices[slicenum]['end'] = cvpj_slices[slicenum]['pos']+100000000

        plugins.add_plug_data(cvpj_l, pluginid, 'trigger', 'oneshot')
        plugins.add_plug_data(cvpj_l, pluginid, 'bpm', slicer_bpm)
        plugins.add_plug_data(cvpj_l, pluginid, 'beats', slicer_beats)
        plugins.add_plug_data(cvpj_l, pluginid, 'slices', cvpj_slices)
        plugins.add_plug_data(cvpj_l, pluginid, 'pitch', slicer_pitch/100)
        plugins.add_plug_data(cvpj_l, pluginid, 'fade_in', slicer_att)
        plugins.add_plug_data(cvpj_l, pluginid, 'fade_out', slicer_dec)
        plugins.add_plug_data(cvpj_l, pluginid, 'stretch', stretch_data)
        return True
        
    # ------------------------------------------------------------------------------------------- FX

    elif pluginname == 'fruity convolver':
        fl_plugstr.read(20)
        fromstorage = fl_plugstr.read(1)[0]
        stringlen = fl_plugstr.read(1)[0]
        filename = fl_plugstr.read(stringlen)
        if fromstorage == 0:
            audiosize = int.from_bytes(fl_plugstr.read(4), "little")
            filename = os.path.join(foldername, pluginid+'_custom_audio.wav')
            with open(filename, "wb") as customconvolverfile:
                customconvolverfile.write(fl_plugstr.read(audiosize))
        plugins.add_plug(cvpj_l, pluginid, 'native-flstudio', pluginname)
        plugins.add_plug_data(cvpj_l, pluginid, 'file', filename.decode())
        fl_plugstr.read(36)
        autodata = {}
        for autoname in ['pan', 'vol', 'stereo', 'allpurpose', 'eq']:
            autodata_table = decode_pointdata(fl_plugstr)
            for point in autodata_table:
                #print(autoname, test)
                plugins.add_env_point(cvpj_l, pluginid, autoname, point[0], point[1][0], tension=point[2], type=envshapes[point[3]])
            autodata[autoname] = autodata_table
        return True

    elif pluginname == 'fruity html notebook':
        plugins.add_plug(cvpj_l, pluginid, 'native-flstudio', pluginname)
        version = int.from_bytes(fl_plugstr.read(4), "little")
        if version == 1: plugins.add_plug_data(cvpj_l, pluginid, 'url', data_bytes.readstring_lenbyte(fl_plugstr, 1, 'little', 'utf-8'))
        return True

    elif pluginname in ['fruity notebook 2', 'fruity notebook']:
        plugins.add_plug(cvpj_l, pluginid, 'native-flstudio', pluginname)
        version = int.from_bytes(fl_plugstr.read(4), "little")
        if version == 0 and pluginname == 'fruity notebook 2' or version == 1000 and pluginname == 'fruity notebook': 
            plugins.add_plug_data(cvpj_l, pluginid, 'currentpage', int.from_bytes(fl_plugstr.read(4), "little"))
            pagesdata = {}
            while True:
                pagenum = int.from_bytes(fl_plugstr.read(4), "little")
                if pagenum == 0 or pagenum > 100: break
                if pluginname == 'fruity notebook 2': 
                    length = varint.decode_stream(fl_plugstr)
                    text = fl_plugstr.read(length*2).decode('utf-16le')
                if pluginname == 'fruity notebook': 
                    length = int.from_bytes(fl_plugstr.read(4), "little")
                    text = fl_plugstr.read(length).decode('ascii')
                pagesdata[pagenum] = text
            plugins.add_plug_data(cvpj_l, pluginid, 'pages', pagesdata)
            plugins.add_plug_data(cvpj_l, pluginid, 'editing_enabled', fl_plugstr.read(1)[0])
        return True

    elif pluginname == 'fruity vocoder':
        plugins.add_plug(cvpj_l, pluginid, 'native-flstudio', pluginname)
        flplugvals = struct.unpack('iiiib', fl_plugstr.read(17))
        vocbands = struct.unpack('f'*flplugvals[1], fl_plugstr.read(flplugvals[1]*4))
        plugins.add_plug_data(cvpj_l, pluginid, 'bands', vocbands)
        plugins.add_plug_data(cvpj_l, pluginid, 'filter', flplugvals[2])
        plugins.add_plug_data(cvpj_l, pluginid, 'left_right', flplugvals[4])
        flplugvalsafter = struct.unpack('i'*12, fl_plugstr.read(12*4))
        #print(flplugvalsafter)
        plugins.add_plug_param(cvpj_l, pluginid, 'freq_min', flplugvalsafter[0], 'int', "Freq Min")
        plugins.add_plug_param(cvpj_l, pluginid, 'freq_max', flplugvalsafter[1], 'int', "Freq Max")
        plugins.add_plug_param(cvpj_l, pluginid, 'freq_scale', flplugvalsafter[2], 'int', "Freq Scale")
        plugins.add_plug_param(cvpj_l, pluginid, 'freq_invert', flplugvalsafter[3], 'bool', "Freq Invert")
        plugins.add_plug_param(cvpj_l, pluginid, 'freq_formant', flplugvalsafter[4], 'int', "Freq Formant")
        plugins.add_plug_param(cvpj_l, pluginid, 'freq_bandwidth', flplugvalsafter[5], 'int', "Freq BandWidth")
        plugins.add_plug_param(cvpj_l, pluginid, 'env_att', flplugvalsafter[6], 'int', "Env Att")
        plugins.add_plug_param(cvpj_l, pluginid, 'env_rel', flplugvalsafter[7], 'int', "Env Rel")
        plugins.add_plug_param(cvpj_l, pluginid, 'mix_mod', flplugvalsafter[9], 'int', "Mix Mod")
        plugins.add_plug_param(cvpj_l, pluginid, 'mix_car', flplugvalsafter[10], 'int', "Mix Car")
        plugins.add_plug_param(cvpj_l, pluginid, 'mix_wet', flplugvalsafter[11], 'int', "Mix Wet")
        return True

    elif pluginname == 'fruity waveshaper':
        plugins.add_plug(cvpj_l, pluginid, 'native-flstudio', pluginname)
        flplugvals = struct.unpack('bHHIIbbbbbb', fl_plugstr.read(22))
        #print(flplugvals)
        plugins.add_plug_param(cvpj_l, pluginid, 'preamp', flplugvals[2], 'int', "Pre Amp")
        plugins.add_plug_param(cvpj_l, pluginid, 'wet', flplugvals[3], 'int', "Wet")
        plugins.add_plug_param(cvpj_l, pluginid, 'postgain', flplugvals[4], 'int', "Post Gain")
        plugins.add_plug_param(cvpj_l, pluginid, 'bipolarmode', flplugvals[5], 'bool', "Bi-polar Mode")
        plugins.add_plug_param(cvpj_l, pluginid, 'removedc', flplugvals[6], 'bool', "Remove DC")

        autodata_table = decode_pointdata(fl_plugstr)
        for point in autodata_table:
            plugins.add_env_point(cvpj_l, pluginid, 'shape', point[0], point[1][0], tension=point[2], type=envshapes[point[3]])
        return True

    else:
        fl_datadef = flstudio_datadef.get_datadef(pluginname)

        if fl_datadef != []:
            plugins.add_plug(cvpj_l, pluginid, 'native-flstudio', pluginname)
            datadef.to_plugdata(cvpj_l, pluginid, fl_datadef, fl_plugstr)
            return True
        #if pluginname == 'simsynth': exit()

    #elif pluginname == 'pitcher': LATER
    #    chunkdata = data_bytes.riff_read(chunkdata, 0)
    #    riffbio = BytesIO(chunkdata[0][1][4:])
    #    flplugvals = struct.unpack('f'*33, riffbio.read(33*4))
    #    flplugflags = struct.unpack('b'*16, riffbio.read(16))
    #    for test in range(len(flplugvals)):
    #        print(test, flplugvals[test])
    #    plugins.add_plug_param(cvpj_l, pluginid, 'speed', flplugvals[0], 'int', "Correction Speed")
    #    plugins.add_plug_param(cvpj_l, pluginid, 'gender', flplugvals[2], 'int', "Gender")
    #    plugins.add_plug_param(cvpj_l, pluginid, 'finetune', flplugvals[3], 'int', "Fine Tune")

    # ------------------------------------------------------------------------------------------- Other

    plugins.add_plug_data(cvpj_l, pluginid, 'chunk', base64.b64encode(chunkpdata).decode('ascii'))
