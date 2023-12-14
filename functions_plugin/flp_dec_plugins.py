# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import os
import math
import varint
from functions import data_bytes
from functions import data_values
from functions import plugins
from functions import plugin_vst2
from functions import plugin_vst3
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

def getparams(cvpj_l, pluginid, pluginname, chunkpdata, foldername, datadef, dataset):
    fl_plugstr = BytesIO(chunkpdata if chunkpdata else b'')
    pluginname = pluginname.lower()
    cvpj_plugindata = plugins.cvpj_plugin('deftype', 'native-flstudio', pluginname)

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
            if chunktype == 52: wrapperdata['16id'] = chunkdata
            if chunktype == 53: wrapperdata['state'] = chunkdata
            if chunktype == 54: wrapperdata['name'] = chunkdata.decode()
            if chunktype == 55: wrapperdata['file'] = chunkdata.decode()
            if chunktype == 56: wrapperdata['vendor'] = chunkdata.decode()
            if chunktype == 57: wrapperdata['57'] = chunkdata

        if 'plugin_info' in wrapperdata:

            wrapper_vsttype = int.from_bytes(wrapperdata['plugin_info'][0:4], "little")
            if 'fourid' in wrapperdata:
                cvpj_plugindata = plugins.cvpj_plugin('deftype', 'vst2', 'win')
                pluginstate = wrapperdata['state']
                wrapper_vststate = pluginstate[0:9]
                wrapper_vstsize = int.from_bytes(pluginstate[9:13], "little")
                wrapper_vstpad = pluginstate[13:17]
                wrapper_vstprogram = int.from_bytes(pluginstate[17:21], "little")
                wrapper_vstdata = pluginstate[21:]

                if wrapper_vststate[0:4] == b'\xf7\xff\xff\xff' and wrapper_vststate[5:9] == b'\xfe\xff\xff\xff':

                    if wrapper_vststate[4] == 13:
                        plugin_vst2.replace_data(cvpj_plugindata, 'name' ,'win', wrapperdata['name'], 'chunk', wrapper_vstdata, 0)
                        cvpj_plugindata.dataval_add('current_program', wrapper_vstprogram)

                    if wrapper_vststate[4] == 5:
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
                            for paramnum in range(numparamseach): cvpj_program['params'][str(paramnum)] = {'value': bankparams[num][paramnum]}
                            cvpj_program['program_name'] = vst_names[num]
                            cvpj_programs.append(cvpj_program)

                        plugin_vst2.replace_data(cvpj_plugindata, 'name' ,'win', wrapperdata['name'], 'bank', cvpj_programs, None)
                        cvpj_plugindata.dataval_add('current_program', wrapper_vstprogram)

            #elif '16id' in wrapperdata:
            #    pluginstate = wrapperdata['state']
            #    pluginstate_str = BytesIO(pluginstate)
            #    stateheader = pluginstate_str.read(80)

            #    vststatedata = {}

            #    while pluginstate_str.tell() < len(pluginstate):
            #        chunktype = int.from_bytes(pluginstate_str.read(4), 'little')
            #        chunksize = int.from_bytes(pluginstate_str.read(4), 'little')
            #        pluginstate_str.read(4)
            #        chunkdata = pluginstate_str.read(chunksize)
            #        vststatedata[chunktype] = chunkdata

                #print(vststatedata[3])

            #    somedata = BytesIO(vststatedata[4])
            #    somedata_num = int.from_bytes(somedata.read(4), 'little')

                #print(wrapperdata['name'])

                #for _ in range(somedata_num):
                #    somedata_b = somedata.read(4)
                #    somedata_p = int.from_bytes(somedata_b, 'little')
                #    print(somedata_b.hex(), end=' ')

                #exit()

            #    plugin_vst3.replace_data(cvpj_plugindata, 'name', 'win', wrapperdata['name'], vststatedata[3] if 3 in vststatedata else b'')


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

        cvpj_plugindata = plugins.cvpj_plugin('deftype', 'universal', 'compressor')
        cvpj_plugindata.dataval_add('tcr', bool(v_tcr) )
        cvpj_plugindata.param_add('pregain', v_gain, 'float', 'pregain')
        cvpj_plugindata.param_add('ratio', v_ratio, 'float', 'ratio')
        cvpj_plugindata.param_add('threshold', v_threshold, 'float', 'threshold')
        cvpj_plugindata.param_add('attack', v_attack, 'float', 'attack')
        cvpj_plugindata.param_add('release', v_release, 'float', 'release')
        cvpj_plugindata.param_add('knee', v_knee, 'float', 'knee')
        

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

        cvpj_plugindata = plugins.cvpj_plugin('deftype', 'soundfont2', None)

        #cvpj_plugindata.dataval_add('reverb_enabled', flsf_reverb_builtin)
        #cvpj_plugindata.dataval_add('chorus_enabled', flsf_chorus_builtin)

        asdflfo_att = flsf_asdf_A/1024 if flsf_asdf_A != -1 else 0
        asdflfo_dec = flsf_asdf_D/1024 if flsf_asdf_D != -1 else 0
        asdflfo_sus = flsf_asdf_S/127 if flsf_asdf_S != -1 else 1
        asdflfo_rel = flsf_asdf_R/1024 if flsf_asdf_R != -1 else 0
        asdflfo_amt = int( (flsf_asdf_A == flsf_asdf_D == flsf_asdf_S == flsf_asdf_R == -1) == False )

        cvpj_plugindata.dataval_add('file', flsf_filename)

        cvpj_plugindata.asdr_env_add('vol', 0, asdflfo_att, 0, asdflfo_dec, asdflfo_sus, asdflfo_rel, asdflfo_amt)

        if flsf_patch > 127:
            cvpj_plugindata.dataval_add('bank', 128)
            cvpj_plugindata.dataval_add('patch', flsf_patch-128)
        else:
            cvpj_plugindata.dataval_add('bank', flsf_bank)
            cvpj_plugindata.dataval_add('patch', flsf_patch)
        
        pitch_amount = flsf_lfo_amount/128 if flsf_lfo_amount != -128 else 0
        pitch_predelay = flsf_lfo_predelay/256 if flsf_lfo_predelay != -1 else 0
        pitch_speed = 1/(flsf_lfo_speed/6) if flsf_lfo_speed != -1 else 1

        #if flsf_vers == 6:
        #    continue
        #    newsf2data = struct.unpack('<bbiii', fl_plugstr.read(14))

        cvpj_plugindata.lfo_add('pitch', 'sine', 'seconds', pitch_speed, pitch_predelay, 0, pitch_amount)
        

    elif pluginname == 'fruity slicer':
        cvpj_plugindata = plugins.cvpj_plugin('deftype', 'sampler', 'slicer')
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
            cvpj_plugindata.dataval_add('file', slicer_filename)
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

        cvpj_plugindata.dataval_add('trigger', 'oneshot')
        cvpj_plugindata.dataval_add('bpm', slicer_bpm)
        cvpj_plugindata.dataval_add('beats', slicer_beats)
        cvpj_plugindata.dataval_add('slices', cvpj_slices)
        cvpj_plugindata.dataval_add('pitch', slicer_pitch/100)
        cvpj_plugindata.dataval_add('fade_in', slicer_att)
        cvpj_plugindata.dataval_add('fade_out', slicer_dec)
        cvpj_plugindata.dataval_add('stretch', stretch_data)
        
        
    # ------------------------------------------------------------------------------------------- FX

    elif pluginname == 'fruity convolver':
        try:
            fl_plugstr.read(20)
            fromstorage = fl_plugstr.read(1)[0]
            filename = data_bytes.readstring_lenbyte(fl_plugstr, 1, 'little', None)
            if fromstorage == 0:
                audiosize = int.from_bytes(fl_plugstr.read(4), "little")
                filename = os.path.join(foldername, pluginid+'_custom_audio.wav')
                with open(filename, "wb") as customconvolverfile:
                    customconvolverfile.write(fl_plugstr.read(audiosize))
            cvpj_plugindata = plugins.cvpj_plugin('deftype', 'native-flstudio', pluginname)
            cvpj_plugindata.dataval_add('file', filename.decode())
            fl_plugstr.read(36)
            autodata = {}
            for autoname in ['pan', 'vol', 'stereo', 'allpurpose', 'eq']:
                autodata_table = decode_pointdata(fl_plugstr)
                for point in autodata_table:
                    #print(autoname, test)
                    cvpj_plugindata.env_points_add(autoname, point[0], point[1][0], tension=point[2], type=envshapes[point[3]])
                autodata[autoname] = autodata_table
        except:
            pass
        


    elif pluginname == 'fruity html notebook':
        cvpj_plugindata = plugins.cvpj_plugin('deftype', 'native-flstudio', pluginname)
        version = int.from_bytes(fl_plugstr.read(4), "little")
        if version == 1: cvpj_plugindata.dataval_add('url', data_bytes.readstring_lenbyte(fl_plugstr, 1, 'little', 'utf-8'))
        

    elif pluginname in ['fruity notebook 2', 'fruity notebook']:
        cvpj_plugindata = plugins.cvpj_plugin('deftype', 'native-flstudio', pluginname)
        version = int.from_bytes(fl_plugstr.read(4), "little")
        if version == 0 and pluginname == 'fruity notebook 2' or version == 1000 and pluginname == 'fruity notebook': 
            cvpj_plugindata.dataval_add('currentpage', int.from_bytes(fl_plugstr.read(4), "little"))
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
            cvpj_plugindata.dataval_add('pages', pagesdata)
            cvpj_plugindata.dataval_add('editing_enabled', fl_plugstr.read(1)[0])
        

    elif pluginname == 'fruity vocoder':
        cvpj_plugindata = plugins.cvpj_plugin('deftype', 'native-flstudio', pluginname)
        flplugvals = struct.unpack('iiiib', fl_plugstr.read(17))
        vocbands = struct.unpack('f'*flplugvals[1], fl_plugstr.read(flplugvals[1]*4))
        cvpj_plugindata.dataval_add('bands', vocbands)
        cvpj_plugindata.dataval_add('filter', flplugvals[2])
        cvpj_plugindata.dataval_add('left_right', flplugvals[4])
        flplugvalsafter = struct.unpack('i'*12, fl_plugstr.read(12*4))
        #print(flplugvalsafter)
        cvpj_plugindata.param_add('freq_min', flplugvalsafter[0], 'int', "Freq Min")
        cvpj_plugindata.param_add('freq_max', flplugvalsafter[1], 'int', "Freq Max")
        cvpj_plugindata.param_add('freq_scale', flplugvalsafter[2], 'int', "Freq Scale")
        cvpj_plugindata.param_add('freq_invert', flplugvalsafter[3], 'bool', "Freq Invert")
        cvpj_plugindata.param_add('freq_formant', flplugvalsafter[4], 'int', "Freq Formant")
        cvpj_plugindata.param_add('freq_bandwidth', flplugvalsafter[5], 'int', "Freq BandWidth")
        cvpj_plugindata.param_add('env_att', flplugvalsafter[6], 'int', "Env Att")
        cvpj_plugindata.param_add('env_rel', flplugvalsafter[7], 'int', "Env Rel")
        cvpj_plugindata.param_add('mix_mod', flplugvalsafter[9], 'int', "Mix Mod")
        cvpj_plugindata.param_add('mix_car', flplugvalsafter[10], 'int', "Mix Car")
        cvpj_plugindata.param_add('mix_wet', flplugvalsafter[11], 'int', "Mix Wet")
        

    elif pluginname == 'fruity waveshaper':
        cvpj_plugindata = plugins.cvpj_plugin('deftype', 'native-flstudio', pluginname)
        flplugvals = struct.unpack('bHHIIbbbbbb', fl_plugstr.read(22))
        #print(flplugvals)
        cvpj_plugindata.param_add('preamp', flplugvals[2], 'int', "Pre Amp")
        cvpj_plugindata.param_add('wet', flplugvals[3], 'int', "Wet")
        cvpj_plugindata.param_add('postgain', flplugvals[4], 'int', "Post Gain")
        cvpj_plugindata.param_add('bipolarmode', flplugvals[5], 'bool', "Bi-polar Mode")
        cvpj_plugindata.param_add('removedc', flplugvals[6], 'bool', "Remove DC")

        autodata_table = decode_pointdata(fl_plugstr)
        for point in autodata_table:
            cvpj_plugindata.env_points_add('shape', point[0], point[1][0], tension=point[2], type=envshapes[point[3]])
        
    else:
        datadef_struct = dataset.object_var_get('datadef_struct', 'plugin', pluginname)
        #print(     chunkpdata.hex()     )
        if datadef_struct[0]:
            cvpj_plugindata = plugins.cvpj_plugin('deftype', 'native-flstudio', pluginname)
            jsondecoded = datadef.parse(datadef_struct[1], chunkpdata)

            #if True:
            #    for part in datadef.debugoutput:
            #        print(part)
            #    exit()

            cvpj_plugindata.param_dict_dataset_get(jsondecoded, dataset, 'plugin', pluginname)

    # ------------------------------------------------------------------------------------------- Other

    if pluginname != 'fruity wrapper': cvpj_plugindata.rawdata_add(chunkpdata)
    return cvpj_plugindata