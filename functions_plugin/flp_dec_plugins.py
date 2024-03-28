# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import os
import math
import varint
from functions import data_bytes
from functions import data_values
from functions_plugin_ext import plugin_vst2
#from functions_plugin_ext import plugin_vst3
from io import BytesIO

def decode_sslf(fl_plugstr):
    header = fl_plugstr.read(4)
    out = b''
    if header == b'SSLF':
        size = int.from_bytes(fl_plugstr.read(4), "little")
        out = fl_plugstr.read(size)
    return out



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

def getparams(convproj_obj, pluginid, flplugin, foldername, datadef, dataset):
    fl_plugstr = BytesIO(flplugin.params if flplugin.params else b'')
    flplugin.name = flplugin.name.lower()

    plugin_obj = convproj_obj.add_plugin(pluginid, 'native-flstudio', flplugin.name)

    windata_obj = convproj_obj.window_data_add(['plugin',pluginid])
    windata_obj.pos_x = flplugin.window_p_x
    windata_obj.pos_y = flplugin.window_p_y
    windata_obj.size_x = flplugin.window_s_x
    windata_obj.size_y = flplugin.window_s_y
    windata_obj.open = bool(flplugin.visible)
    windata_obj.detatched = bool(flplugin.detached)

    # ------------------------------------------------------------------------------------------- VST
    if flplugin.name == 'fruity wrapper':
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

                plugin_obj.type_set('vst2', 'win')
                pluginstate = wrapperdata['state']
                wrapper_vststate = pluginstate[0:9]
                wrapper_vstsize = int.from_bytes(pluginstate[9:13], "little")
                wrapper_vstpad = pluginstate[13:17]
                wrapper_vstprogram = int.from_bytes(pluginstate[17:21], "little")
                wrapper_vstdata = pluginstate[21:]

                if wrapper_vststate[0:4] == b'\xf7\xff\xff\xff' and wrapper_vststate[5:9] == b'\xfe\xff\xff\xff':

                    if wrapper_vststate[4] in [13, 12]:
                        plugin_obj.rawdata_add('chunk', wrapper_vstdata)
                        plugin_obj.datavals.add('current_program', wrapper_vstprogram)

                        plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id' ,'win', wrapperdata['fourid'], 'chunk', wrapper_vstdata, None)
                        plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name' ,'win', wrapperdata['name'], 'chunk', wrapper_vstdata, None)

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

                        plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name' ,'win', wrapperdata['name'], 'bank', cvpj_programs, None)
                        plugin_obj.datavals.add('current_program', wrapper_vstprogram)

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

            #    plugin_vst3.replace_data(convproj_obj, plugin_obj, 'name', 'win', wrapperdata['name'], vststatedata[3] if 3 in vststatedata else b'')

    # ------------------------------------------------------------------------------------------- Inst

    elif flplugin.name in ['fruity soundfont player', 'soundfont player']:
        flsf_vers, flsf_patch, flsf_bank, flsf_reverb_sendlvl, flsf_chorus_sendlvl, flsf_mod = struct.unpack('iiiiii', fl_plugstr.read(24))

        flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R = struct.unpack('iiii', fl_plugstr.read(16))
        flsf_lfo_predelay, flsf_lfo_amount, flsf_lfo_speed, flsf_cutoff = struct.unpack('iiii', fl_plugstr.read(16))
        flsf_filelen = int.from_bytes(fl_plugstr.read(1), "little")
        flsf_filename = fl_plugstr.read(flsf_filelen).decode('utf-8')
        flsf_reverb_sendto, flsf_reverb_builtin = struct.unpack('ib', fl_plugstr.read(5))
        flsf_chorus_sendto, flsf_chorus_builtin = struct.unpack('ib', fl_plugstr.read(5))
        flsf_hqrender = int.from_bytes(fl_plugstr.read(1), "little")

        plugin_obj.type_set('soundfont2', None)

        #plugin_obj.datavals.add('reverb_enabled', flsf_reverb_builtin)
        #plugin_obj.datavals.add('chorus_enabled', flsf_chorus_builtin)

        asdflfo_att = flsf_asdf_A/1024 if flsf_asdf_A != -1 else 0
        asdflfo_dec = flsf_asdf_D/1024 if flsf_asdf_D != -1 else 0
        asdflfo_sus = flsf_asdf_S/127 if flsf_asdf_S != -1 else 1
        asdflfo_rel = flsf_asdf_R/1024 if flsf_asdf_R != -1 else 0
        asdflfo_amt = int( (flsf_asdf_A == flsf_asdf_D == flsf_asdf_S == flsf_asdf_R == -1) == False )

        convproj_obj.add_fileref(flsf_filename, flsf_filename)
        plugin_obj.filerefs['file'] = flsf_filename
        
        plugin_obj.env_asdr_add('vol', 0, asdflfo_att, 0, asdflfo_dec, asdflfo_sus, asdflfo_rel, asdflfo_amt)

        if flsf_patch > 127:
            plugin_obj.datavals.add('bank', 128)
            plugin_obj.datavals.add('patch', flsf_patch-128)
        else:
            plugin_obj.datavals.add('bank', flsf_bank)
            plugin_obj.datavals.add('patch', flsf_patch)
        
        pitch_amount = flsf_lfo_amount/128 if flsf_lfo_amount != -128 else 0
        pitch_predelay = flsf_lfo_predelay/256 if flsf_lfo_predelay != -1 else 0
        pitch_speed = 1/(flsf_lfo_speed/6) if flsf_lfo_speed != -1 else 1

        #if flsf_vers == 6:
        #    continue
        #    newsf2data = struct.unpack('<bbiii', fl_plugstr.read(14))

        lfo_obj = plugin_obj.lfo_add('pitch')
        lfo_obj.predelay = pitch_predelay
        lfo_obj.time.set_seconds(pitch_speed)
        lfo_obj.amount = pitch_amount

    elif flplugin.name == 'fruity slicer':
        plugin_obj.type_set( 'sampler', 'slicer')
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
        slicechannels = 2
        max_dur = 10000000

        if slicer_filename != "": 
            sampleref_obj = convproj_obj.add_sampleref(slicer_filename, slicer_filename)
            plugin_obj.samplerefs['sample'] = slicer_filename
            slicechannels = sampleref_obj.channels
            max_dur = sampleref_obj.dur_samples

        slicer_numslices = int.from_bytes(fl_plugstr.read(4), "little")

        slicer_data = []
        for _ in range(slicer_numslices):
            slicer_slicenamelen = int.from_bytes(fl_plugstr.read(1), "little")
            slicer_slicename = fl_plugstr.read(slicer_slicenamelen).decode('utf-8')
            slicer_s_slice = struct.unpack('iihBBB', fl_plugstr.read(13))
            slicer_data.append([slicer_s_slice, slicer_slicename])

        slicepos = [int(x[0][0]*(slicechannels/2)) for x in slicer_data]+[max_dur]

        prev_pos = -1
        for slicenum, fl_slicedata in enumerate(slicer_data):
            fl_slice, slice_name = fl_slicedata
            cvpj_region = {}
            cvpj_region['name'] = slice_name
            if slicer_s_slice[1] != -1: cvpj_region['note'] = fl_slice[1]
            cvpj_region['reverse'] = fl_slice[5]
            plugin_obj.regions.add(slicepos[slicenum], slicepos[slicenum+1], cvpj_region)

        plugin_obj.datavals.add('trigger', 'oneshot')
        plugin_obj.datavals.add('bpm', slicer_bpm)
        plugin_obj.datavals.add('beats', slicer_beats)
        plugin_obj.datavals.add('pitch', slicer_pitch/100)
        plugin_obj.datavals.add('fade_in', slicer_att)
        plugin_obj.datavals.add('fade_out', slicer_dec)
        plugin_obj.datavals.add('stretch', stretch_data)
        
        
    # ------------------------------------------------------------------------------------------- FX

    elif flplugin.name == 'fruity convolver':
        try:
            fl_plugstr.read(20)
            fromstorage = fl_plugstr.read(1)[0]
            filename = data_bytes.readstring_lenbyte(fl_plugstr, 1, 'little', None)
            if fromstorage == 0:
                audiosize = int.from_bytes(fl_plugstr.read(4), "little")
                filename = os.path.join(foldername, pluginid+'_custom_audio.wav')
                with open(filename, "wb") as customconvolverfile:
                    customconvolverfile.write(fl_plugstr.read(audiosize))
            plugin_obj.type_set( 'native-flstudio', flplugin.name)
            plugin_obj.datavals.add('file', filename.decode())
            fl_plugstr.read(36)
            autodata = {}
            for autoname in ['pan', 'vol', 'stereo', 'allpurpose', 'eq']:
                autodata_table = decode_pointdata(fl_plugstr)
                autopoints_obj = plugin_obj.env_points_add(autoname, 4, True, 'float')
                for point in autodata_table:
                    autopoint_obj = autopoints_obj.add_point()
                    autopoint_obj.pos = point[0]
                    autopoint_obj.value = point[1][0]
                    autopoint_obj.type = envshapes[point[3]]
                    autopoint_obj.tension = point[2]
                autodata[autoname] = autodata_table
        except:
            pass
        


    elif flplugin.name == 'fruity html notebook':
        plugin_obj.type_set( 'native-flstudio', flplugin.name)
        version = int.from_bytes(fl_plugstr.read(4), "little")
        if version == 1: plugin_obj.datavals.add('url', data_bytes.readstring_lenbyte(fl_plugstr, 1, 'little', 'utf-8'))
        

    elif flplugin.name in ['fruity notebook 2', 'fruity notebook']:
        plugin_obj.type_set( 'native-flstudio', flplugin.name)
        version = int.from_bytes(fl_plugstr.read(4), "little")
        if version == 0 and flplugin.name == 'fruity notebook 2' or version == 1000 and flplugin.name == 'fruity notebook': 
            plugin_obj.datavals.add('currentpage', int.from_bytes(fl_plugstr.read(4), "little"))
            pagesdata = {}
            while True:
                pagenum = int.from_bytes(fl_plugstr.read(4), "little")
                if pagenum == 0 or pagenum > 100: break
                if flplugin.name == 'fruity notebook 2': 
                    length = varint.decode_stream(fl_plugstr)
                    text = fl_plugstr.read(length*2).decode('utf-16le')
                if flplugin.name == 'fruity notebook': 
                    length = int.from_bytes(fl_plugstr.read(4), "little")
                    text = fl_plugstr.read(length).decode('ascii')
                pagesdata[pagenum] = text
            plugin_obj.datavals.add('pages', pagesdata)
            plugin_obj.datavals.add('editing_enabled', fl_plugstr.read(1)[0])
        

    elif flplugin.name == 'fruity vocoder':
        plugin_obj.type_set( 'native-flstudio', flplugin.name)
        flplugvals = struct.unpack('iiiib', fl_plugstr.read(17))
        vocbands = struct.unpack('f'*flplugvals[1], fl_plugstr.read(flplugvals[1]*4))
        plugin_obj.datavals.add('bands', vocbands)
        plugin_obj.datavals.add('filter', flplugvals[2])
        plugin_obj.datavals.add('left_right', flplugvals[4])
        flplugvalsafter = struct.unpack('i'*12, fl_plugstr.read(12*4))
        #print(flplugvalsafter)
        
        param_obj = plugin_obj.params.add('freq_min', flplugvalsafter[0], 'int')
        param_obj.visual.name = "Freq Min"
        param_obj = plugin_obj.params.add('freq_max', flplugvalsafter[1], 'int')
        param_obj.visual.name = "Freq Max"
        param_obj = plugin_obj.params.add('freq_scale', flplugvalsafter[2], 'int')
        param_obj.visual.name = "Freq Scale"
        param_obj = plugin_obj.params.add('freq_invert', flplugvalsafter[3], 'bool')
        param_obj.visual.name = "Freq Invert"
        param_obj = plugin_obj.params.add('freq_formant', flplugvalsafter[4], 'int')
        param_obj.visual.name = "Freq Formant"
        param_obj = plugin_obj.params.add('freq_bandwidth', flplugvalsafter[5], 'int')
        param_obj.visual.name = "Freq BandWidth"
        param_obj = plugin_obj.params.add('env_att', flplugvalsafter[6], 'int')
        param_obj.visual.name = "Env Att"
        param_obj = plugin_obj.params.add('env_rel', flplugvalsafter[7], 'int')
        param_obj.visual.name = "Env Rel"
        param_obj = plugin_obj.params.add('mix_mod', flplugvalsafter[9], 'int')
        param_obj.visual.name = "Mix Mod"
        param_obj = plugin_obj.params.add('mix_car', flplugvalsafter[10], 'int')
        param_obj.visual.name = "Mix Car"
        param_obj = plugin_obj.params.add('mix_wet', flplugvalsafter[11], 'int')
        param_obj.visual.name = "Mix Wet"

    elif flplugin.name == 'fruity waveshaper':
        plugin_obj.type_set( 'native-flstudio', flplugin.name)
        flplugvals = struct.unpack('bHHIIbbbbbb', fl_plugstr.read(22))
        #print(flplugvals)
        param_obj = plugin_obj.params.add('preamp', flplugvals[2], 'int')
        param_obj.visual.name = "Pre Amp"
        param_obj = plugin_obj.params.add('wet', flplugvals[3], 'int')
        param_obj.visual.name = "Wet"
        param_obj = plugin_obj.params.add('postgain', flplugvals[4], 'int')
        param_obj.visual.name = "Post Gain"
        param_obj = plugin_obj.params.add('bipolarmode', flplugvals[5], 'bool')
        param_obj.visual.name = "Bi-polar Mode"
        param_obj = plugin_obj.params.add('removedc', flplugvals[6], 'bool')
        param_obj.visual.name = "Remove DC"

        autodata_table = decode_pointdata(fl_plugstr)

        autopoints_obj = plugin_obj.env_points_add('shape', 4, True, 'float')
        for point in autodata_table:
            autopoint_obj = autopoints_obj.add_point()
            autopoint_obj.pos = point[0]
            autopoint_obj.value = point[1][0]
            autopoint_obj.type = envshapes[point[3]]
            autopoint_obj.tension = point[2]
    
    elif flplugin.name in ['bassdrum', 'pitcher']:
        sslfdata = decode_sslf(fl_plugstr)

        if flplugin.name == 'bassdrum': jsondecoded = datadef.parse('sslf_bassdrum', sslfdata)
        if flplugin.name == 'pitcher': jsondecoded = datadef.parse('sslf_pitcher', sslfdata)

        plugin_obj.type_set( 'native-flstudio', flplugin.name)
        plugin_obj.param_dict_dataset_get(jsondecoded, dataset, 'plugin', flplugin.name)

    #    if flplugin.name == 'sawer':
    #        jsondecoded = datadef.parse('sawer', sslfdata)

        if 0:
            for x in datadef.debugoutput:
                print(x)
            exit()

    else:
        datadef_struct = dataset.object_var_get('datadef_struct', 'plugin', flplugin.name)
        #print(     flplugin.name, flplugin.params.hex()     )
        if datadef_struct[0]:
            plugin_obj.type_set( 'native-flstudio', flplugin.name)
            jsondecoded = datadef.parse(datadef_struct[1], flplugin.params)

            if 0:
                for part in datadef.debugoutput:
                    print(part)
                exit()

            plugin_obj.param_dict_dataset_get(jsondecoded, dataset, 'plugin', flplugin.name)

    # ------------------------------------------------------------------------------------------- Other

    if plugin_obj.plugin_type != 'fruity wrapper': plugin_obj.rawdata_add('fl', flplugin.params)
    return plugin_obj