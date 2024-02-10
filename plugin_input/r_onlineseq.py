# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import dv_dataset
from objects import convproj
from functions import data_values
import plugin_input
import json
import math
import struct
import blackboxprotobuf

onlseq_param_song = {}
onlseq_param_song['1'] = ['bpm',1]
onlseq_param_song['2'] = ['unknown2',1]
onlseq_param_song['3'] = ['unknown3',1]
onlseq_param_song['4'] = ['unknown4',1]
onlseq_param_song['5'] = ['unknown5',1]
onlseq_param_song['6'] = ['unknown6',1]
onlseq_param_song['7'] = ['unknown7',1]
onlseq_param_song['8'] = ['vol',1]
onlseq_param_song['9'] = ['fast_gfx',1]
onlseq_param_song['10'] = ['autoscroll',1]
onlseq_param_song['11'] = ['unknown11',1]

onlseq_param_inst = {}
onlseq_param_inst['1'] = ['vol',1]
onlseq_param_inst['2'] = ['delay_on',0]
onlseq_param_inst['3'] = ['reverb_on',0]
onlseq_param_inst['4'] = ['pan',1]
onlseq_param_inst['5'] = ['enable_eq',0]
onlseq_param_inst['6'] = ['eq_low',1]
onlseq_param_inst['7'] = ['eq_mid',1]
onlseq_param_inst['8'] = ['eq_high',1]
onlseq_param_inst['9'] = ['detune',1]
onlseq_param_inst['10'] = ['reverb_type',0]
onlseq_param_inst['11'] = ['reverb_wet',1]
onlseq_param_inst['12'] = ['distort_type',0]
onlseq_param_inst['13'] = ['distort_wet',1]

onlseq_param_auto = {}
onlseq_param_auto['1'] = 'vol'
onlseq_param_auto['2'] = 'pan'
onlseq_param_auto['3'] = 'eq_high'
onlseq_param_auto['4'] = 'eq_mid'
onlseq_param_auto['5'] = 'eq_low'
onlseq_param_auto['6'] = 'delay_on'
onlseq_param_auto['7'] = 'reverb_type'
onlseq_param_auto['11'] = 'detune'
onlseq_param_auto['12'] = 'reverb_wet'
onlseq_param_auto['13'] = 'distort_type'
onlseq_param_auto['14'] = 'distort_wet'
onlseq_param_auto['15'] = 'reset_params'


def int2float(value): return struct.unpack("<f", struct.pack("<I", value))[0]

def dict2list(i_dict):
    if isinstance(i_dict, list) == False: return [i_dict]
    else: return i_dict

def parse_inst_params(data):
    outputlist = {}
    if type(data) == dict: in_data = [data]
    else: in_data = data

    for part in in_data:
        if '1' in part:  instid = int(part['1'])
        if '2' in part: 
            params = part['2']
            instparams = {}
            for param in params: 
                if param == '15':
                    onlseq_customnames[instid] = params['15']
                elif param in onlseq_param_inst: 
                    param_name, param_isfloat = onlseq_param_inst[param]
                    if param_isfloat == 1: instparams[param_name] = int2float(int(params[param]))
                    if param_isfloat == 0: instparams[param_name] = int(params[param])
            outputlist[instid] = instparams
    return outputlist

def parse_marker(markerdata):
    data_pos = 0
    data_value = 0
    data_markertype = 'instant'
    inst_id = -1
    inst_param = 'vol'

    if '1' in markerdata: data_pos = int2float(int(markerdata['1']))
    if '3' in markerdata: inst_id = int(markerdata['3'])
    if '4' in markerdata: data_value = int2float(int(markerdata['4']))
    if '5' in markerdata: data_markertype = 'normal'

    if inst_id == -1: inst_param = 'bpm'
    else: inst_param = 'vol'

    if '2' in markerdata: 
        if inst_id == -1: inst_param = onlseq_param_song[markerdata['2']]
        else: inst_param = onlseq_param_auto[markerdata['2']]

    return [inst_id, inst_param, data_pos, data_value, data_markertype]

class input_onlinesequencer(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'onlineseq'
    def getname(self): return 'Online Sequencer'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'auto_nopl': True,
        'track_nopl': True
        }
    def supported_autodetect(self): return False
    def parse(self, convproj_obj, input_file, extra_param):
        global onlseq_notelist
        global onlseq_customnames
        global dataset

        convproj_obj.type = 'r'
        convproj_obj.set_timings(4, True)

        dataset = dv_dataset.dataset('./data_dset/onlineseq.dset')
        dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')

        onlseq_customnames = {}

        os_data_song_stream = open(input_file, 'rb')
        os_data_song_data = os_data_song_stream.read()
        message, typedef = blackboxprotobuf.protobuf_to_json(os_data_song_data)

        os_data = json.loads(message)

        onlseq_data_main = os_data["1"]
        onlseq_data_notes = os_data["2"]
        onlseq_data_markers = os_data["3"] if '3' in os_data else []

        t_auto_tempo = []
        t_auto_vol = []
        t_auto_inst = {}

        onlseq_data_instparams = parse_inst_params(os_data["1"]["3"]) if "3" in onlseq_data_main else {}

        onlseq_notelist = {}

        used_fx_inst = {}

        for os_note in dict2list(onlseq_data_notes): 
            ols_note = int(os_note['1'])
            ols_pos = int2float(int(os_note['2'])) if '2' in os_note else 0
            ols_dur = int2float(int(os_note['3'])) if '3' in os_note else 1
            ols_inst = int(os_note['4']) if '4' in os_note else 0
            ols_vol = int2float(int(os_note['5'])) if '5' in os_note else 1
            if ols_dur > 0.00001:
                if ols_inst not in onlseq_notelist: 
                    onlseq_notelist[ols_inst] = []
                onlseq_notelist[ols_inst].append([ols_pos, ols_dur, ols_note-60, ols_vol])

        for instid in onlseq_notelist:
            used_fx_inst[instid] = []

            cvpj_instid = 'os_'+str(instid)
            cvpj_notelist = onlseq_notelist[instid]

            trueinstid = instid%10000
            
            onlseq_s_iparams = {}
            if instid in onlseq_data_instparams: onlseq_s_iparams = onlseq_data_instparams[instid]

            track_obj, plugin_obj = convproj_obj.add_track_from_dset(cvpj_instid, cvpj_instid, dataset, dataset_midi, str(trueinstid), None, None, 0, False)
            if 'vol' in onlseq_s_iparams: track_obj.params.add('vol', onlseq_s_iparams['vol'], 'float')
            if 'pan' in onlseq_s_iparams: track_obj.params.add('pan', onlseq_s_iparams['pan'], 'float')

            #print(plugin_obj.plugin_type, plugin_obj.plugin_subtype)

            if not plugin_obj.plugin_type:
                if instid in [13,14,15,16]: 
                    plugin_obj.type_set('universal', 'synth-osc')
                    osc_data = plugin_obj.osc_add()
                    if instid == 13: osc_data.shape = 'sine'
                    if instid == 14: osc_data.shape = 'square'
                    if instid == 15: osc_data.shape = 'saw'
                    if instid == 16: osc_data.shape = 'triangle'

            placement_obj = track_obj.placements.add_notes()
            for ols_pos, ols_dur, ols_note, ols_vol in cvpj_notelist: placement_obj.notelist.add_r(ols_pos, ols_dur, ols_note, ols_vol, {})

            if 'delay_on' in onlseq_s_iparams and 'delay' not in used_fx_inst[instid]: used_fx_inst[instid].append('delay')
            if 'distort_type' in onlseq_s_iparams and 'distort' not in used_fx_inst[instid]: used_fx_inst[instid].append('distort')
            if 'distort_wet' in onlseq_s_iparams and 'distort' not in used_fx_inst[instid]: used_fx_inst[instid].append('distort')
            if 'reverb_type' in onlseq_s_iparams and 'reverb' not in used_fx_inst[instid]: used_fx_inst[instid].append('reverb')
            if 'reverb_on' in onlseq_s_iparams and 'reverb' not in used_fx_inst[instid]: used_fx_inst[instid].append('reverb')
            if 'reverb_wet' in onlseq_s_iparams and 'reverb' not in used_fx_inst[instid]: used_fx_inst[instid].append('reverb')
            if 'eq_high' in onlseq_s_iparams and 'eq' not in used_fx_inst[instid]: used_fx_inst[instid].append('eq')
            if 'eq_mid' in onlseq_s_iparams and 'eq' not in used_fx_inst[instid]: used_fx_inst[instid].append('eq')
            if 'eq_low' in onlseq_s_iparams and 'eq' not in used_fx_inst[instid]: used_fx_inst[instid].append('eq')

        bpm = int(onlseq_data_main['1']) if '1' in onlseq_data_main else 120

        for onlseq_data_marker in dict2list(onlseq_data_markers):
            a_inst, a_param, a_pos, a_value, a_type = parse_marker(onlseq_data_marker)

            trackid = 'os_'+str(a_inst)
            if a_inst != -1:

                if a_inst not in used_fx_inst: used_fx_inst[a_inst] = []

                if a_param == 'vol': convproj_obj.add_autopoint(['track', trackid, 'vol'], 'float', a_pos, a_value, a_type)
                if a_param == 'pan': convproj_obj.add_autopoint(['track', trackid, 'pan'], 'float', a_pos, a_value, a_type)
                if a_param == 'detune': convproj_obj.add_autopoint(['track', trackid, 'pitch'], 'float', a_pos, a_value/100, a_type)

                if a_param in ['eq_high', 'eq_mid', 'eq_low']: 
                    convproj_obj.add_autopoint(['plugin', trackid+'_eq', a_param], 'float', a_pos, a_value, a_type)
                    if 'eq' not in used_fx_inst[a_inst]: used_fx_inst[a_inst].append('eq')

                if a_param == 'delay_on': 
                    convproj_obj.add_autopoint(['slot', trackid+'_delay', 'enabled'], 'bool', a_pos, bool(a_value), a_type)
                    if 'delay' not in used_fx_inst[a_inst]: used_fx_inst[a_inst].append('delay')

                if a_param == 'reverb_type': 
                    convproj_obj.add_autopoint(['plugin', trackid+'_reverb', 'reverb_type'], 'float', a_pos, a_value, a_type)
                    if 'reverb' not in used_fx_inst[a_inst]: used_fx_inst[a_inst].append('reverb')

                if a_param == 'reverb_wet': 
                    convproj_obj.add_autopoint(['slot', trackid+'_reverb', 'wet'], 'float', a_pos, a_value, a_type)
                    if 'reverb' not in used_fx_inst[a_inst]: used_fx_inst[a_inst].append('reverb')

                if a_param == 'distort_type': 
                    if a_value != 0: convproj_obj.add_autopoint(['plugin', trackid+'_distort', 'distort_type'], 'int', a_pos, a_value, a_type)
                    convproj_obj.add_autopoint(['slot', trackid+'_distort', 'enabled'], 'bool', a_pos, int(bool(a_value)), a_type)
                    if 'distort' not in used_fx_inst[a_inst]: used_fx_inst[a_inst].append('distort')

                if a_param == 'distort_wet': 
                    convproj_obj.add_autopoint(['slot', trackid+'_distort', 'wet'], 'float', a_pos, a_value, a_type)
                    if 'distort' not in used_fx_inst[a_inst]: used_fx_inst[a_inst].append('distort')

            else:
                if a_param == 'vol': convproj_obj.add_autopoint(['song', 'vol'], 'float', a_pos, a_value, a_type)
                if a_param == 'bpm': convproj_obj.add_autopoint(['song', 'bpm'], 'float', a_pos, a_value, a_type)

        for instid, instparams in used_fx_inst.items():
            trackid = 'os_'+str(instid)
            track_found, track_obj = convproj_obj.find_track(trackid)
            if track_found:
                autoid = str(instid)

                delay_fx_enabled = bool(data_values.nested_dict_get_value(onlseq_data_instparams, [instid, 'delay_on']))
                distort_type = data_values.nested_dict_get_value(onlseq_data_instparams, [instid, 'distort_type'])
                reverb_type = data_values.nested_dict_get_value(onlseq_data_instparams, [instid, 'reverb_type'])

                if 'delay' in instparams:
                    pluginid = trackid+'_delay'
                    plugin_obj = convproj_obj.add_plugin(pluginid, 'universal', 'delay-c')
                    plugin_obj.datavals.add('time_type', 'steps')
                    plugin_obj.datavals.add('time', 2)
                    plugin_obj.datavals.add('feedback', 0.25)
                    plugin_obj.fxdata_add(delay_fx_enabled if delay_fx_enabled else 0, 0.5)
                    plugin_obj.visual.name = 'Delay'
                    track_obj.fxslots_audio.append(pluginid)

                if 'distort' in instparams:
                    pluginid = trackid+'_distort'
                    plugin_obj = convproj_obj.add_plugin(pluginid, 'native-onlineseq', 'distort')
                    fx_wet = data_values.nested_dict_get_value(onlseq_data_instparams, [instid, 'distort_wet'])
                    if fx_wet == None: fx_wet = 1
                    plugin_obj.fxdata_add(True, fx_wet)
                    plugin_obj.params.add('distort_type', distort_type if distort_type else 0, 'int')
                    plugin_obj.visual.name = 'Distortion'
                    track_obj.fxslots_audio.append(pluginid)

                if 'reverb' in instparams:
                    pluginid = trackid+'_reverb'
                    plugin_obj = convproj_obj.add_plugin(pluginid, 'native-onlineseq', 'reverb')
                    fx_enabled = bool(data_values.nested_dict_get_value(onlseq_data_instparams, [instid, 'reverb_on']))
                    if fx_enabled == None: fx_enabled = 0
                    fx_wet = data_values.nested_dict_get_value(onlseq_data_instparams, [instid, 'reverb_wet'])
                    if fx_wet == None: fx_wet = 1
                    plugin_obj.params.add('reverb_type', reverb_type if reverb_type else 0, 'int')
                    plugin_obj.visual.name = 'Reverb'
                    track_obj.fxslots_audio.append(pluginid)

                if 'eq' in instparams:
                    pluginid = trackid+'_eq'
                    fx_enabled = bool(data_values.nested_dict_get_value(onlseq_data_instparams, [instid, 'enable_eq']))
                    if fx_enabled == None: fx_enabled = 0
                    plugin_obj = convproj_obj.add_plugin(pluginid, 'native-onlineseq', 'eq')
                    plugin_obj.fxdata_add(fx_enabled, 1)
                    for paramname in ['eq_high', 'eq_mid', 'eq_low']:
                        eq_value = data_values.nested_dict_get_value(onlseq_data_instparams, [instid, paramname])
                        if eq_value == None: eq_value = 0
                        plugin_obj.params.add(paramname, eq_value, 'float')
                    plugin_obj.visual.name = 'EQ'
                    track_obj.fxslots_audio.append(pluginid)

        timesig_numerator = 4
        if '2' in onlseq_data_main: timesig_numerator = int(onlseq_data_main['2'])
        convproj_obj.timesig = [timesig_numerator, 4]

        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_singlenotelistcut')
        convproj_obj.params.add('bpm', bpm, 'float')
