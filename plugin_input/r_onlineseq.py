# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import idvals
from functions import note_data
from functions import plugins
from functions import placement_data
from functions import song
from functions_tracks import auto_nopl
from functions_tracks import fxslot
from functions_tracks import tracks_r
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

def parse_note(notedata):
    global onlseq_notelist
    ols_pos = 0
    ols_inst = 0
    ols_vol = 1
    ols_note = int(notedata['1'])
    ols_dur = 1
    if '2' in notedata: ols_pos = int2float(int(notedata['2']))
    if '3' in notedata: ols_dur = int2float(int(notedata['3']))
    if '4' in notedata: ols_inst = int(notedata['4'])
    if '5' in notedata: ols_vol = int2float(int(notedata['5']))
    if ols_dur > 0.00001:
        cvpj_notedata = note_data.rx_makenote(ols_pos, ols_dur, ols_note-60, ols_vol, None)
        if ols_inst not in onlseq_notelist: onlseq_notelist[ols_inst] = []
        onlseq_notelist[ols_inst].append(cvpj_notedata)

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
    def parse(self, input_file, extra_param):
        global onlseq_notelist
        global onlseq_customnames

        cvpj_l = {}
        
        cvpj_l_keynames_data = {}
        onlseq_customnames = {}

        os_data_song_stream = open(input_file, 'rb')
        os_data_song_data = os_data_song_stream.read()
        message, typedef = blackboxprotobuf.protobuf_to_json(os_data_song_data)

        idvals_onlineseq_inst = idvals.parse_idvalscsv('data_idvals/onlineseq_inst.csv')
        idvals_onlineseq_drumkit = idvals.parse_idvalscsv('data_idvals/onlineseq_drumkit.csv')
        idvals_onlineseq_drumkit_808 = idvals.parse_idvalscsv('data_idvals/onlineseq_drumkit_808.csv')
        idvals_onlineseq_drumkit_909 = idvals.parse_idvalscsv('data_idvals/onlineseq_drumkit_909.csv')
        idvals_onlineseq_drumkit_2013 = idvals.parse_idvalscsv('data_idvals/onlineseq_drumkit_2013.csv')
        idvals_onlineseq_drumkit_retro = idvals.parse_idvalscsv('data_idvals/onlineseq_drumkit_retro.csv')
        
        cvpj_l_keynames_data['drumkit_midi'] = idvals.idval2drumkeynames(idvals_onlineseq_drumkit)
        cvpj_l_keynames_data['drumkit_808'] = idvals.idval2drumkeynames(idvals_onlineseq_drumkit_808)
        cvpj_l_keynames_data['drumkit_909'] = idvals.idval2drumkeynames(idvals_onlineseq_drumkit_909)
        cvpj_l_keynames_data['drumkit_2013'] = idvals.idval2drumkeynames(idvals_onlineseq_drumkit_2013)
        cvpj_l_keynames_data['drumkit_retro'] = idvals.idval2drumkeynames(idvals_onlineseq_drumkit_retro)

        os_data = json.loads(message)

        onlseq_data_main = os_data["1"]
        onlseq_data_notes = os_data["2"]
        if '3' in os_data: onlseq_data_markers = os_data["3"]
        else: onlseq_data_markers = []

        t_auto_tempo = []
        t_auto_vol = []
        t_auto_inst = {}

        if "3" in onlseq_data_main: onlseq_data_instparams = parse_inst_params(os_data["1"]["3"])
        else: onlseq_data_instparams = {}

        onlseq_notelist = {}

        used_fx_inst = {}

        for os_note in dict2list(onlseq_data_notes): parse_note(os_note)

        for instid in onlseq_notelist:
            used_fx_inst[instid] = []

            cvpj_instid = 'os_'+str(instid)
            cvpj_notelist = onlseq_notelist[instid]

            trueinstid = instid%10000

            if instid in onlseq_customnames:
                inst_name = onlseq_customnames[instid]
            else:
                inst_name = idvals.get_idval(idvals_onlineseq_inst, str(trueinstid), 'name')

            inst_color = idvals.get_idval(idvals_onlineseq_inst, str(trueinstid), 'color')
            inst_gminst = idvals.get_idval(idvals_onlineseq_inst, str(trueinstid), 'gm_inst')
            inst_isdrum = idvals.get_idval(idvals_onlineseq_inst, str(trueinstid), 'isdrum')

            pluginid = cvpj_instid

            onlseq_s_iparams = {}
            if instid in onlseq_data_instparams: onlseq_s_iparams = onlseq_data_instparams[instid]
            trk_vol = data_values.get_value(onlseq_s_iparams, 'vol', 1)
            trk_pan = data_values.get_value(onlseq_s_iparams, 'pan', 0)

            tracks_r.track_create(cvpj_l, cvpj_instid, 'instrument')
            tracks_r.track_visual(cvpj_l, cvpj_instid, name=inst_name, color=inst_color)
            tracks_r.track_inst_pluginid(cvpj_l, cvpj_instid, pluginid)
            tracks_r.track_param_add(cvpj_l, cvpj_instid, 'vol', trk_vol, 'float')
            tracks_r.track_param_add(cvpj_l, cvpj_instid, 'pan', trk_pan, 'float')

            if instid == 13: plugins.add_plug(cvpj_l, pluginid, 'retro', 'sine')
            elif instid == 14: plugins.add_plug(cvpj_l, pluginid, 'retro', 'square')
            elif instid == 15: plugins.add_plug(cvpj_l, pluginid, 'retro', 'saw')
            elif instid == 16: plugins.add_plug(cvpj_l, pluginid, 'retro', 'triangle')
            else:
                if inst_gminst != None:
                    if inst_isdrum == True: 
                        plugins.add_plug_gm_midi(cvpj_l, pluginid, 128, inst_gminst-1)
                        tracks_r.track_param_add(cvpj_l, cvpj_instid, 'usemasterpitch', False, 'bool')
                        tracks_r.track_dataval_add(cvpj_l, cvpj_instid, 'midi', 'output', {'drums': True, 'program': inst_gminst-1})
                    else: 
                        plugins.add_plug_gm_midi(cvpj_l, pluginid, 0, inst_gminst-1)
                        tracks_r.track_param_add(cvpj_l, cvpj_instid, 'usemasterpitch', True, 'bool')
                        tracks_r.track_dataval_add(cvpj_l, cvpj_instid, 'midi', 'output', {'program': inst_gminst-1})

            tracks_r.add_pl(cvpj_l, cvpj_instid, 'notes', placement_data.nl2pl(cvpj_notelist))

            if 'delay_on' in onlseq_s_iparams: 
                if 'delay' not in used_fx_inst[instid]: used_fx_inst[instid].append('delay')
            if 'distort_type' in onlseq_s_iparams: 
                if 'distort' not in used_fx_inst[instid]: used_fx_inst[instid].append('distort')
            if 'distort_wet' in onlseq_s_iparams: 
                if 'distort' not in used_fx_inst[instid]: used_fx_inst[instid].append('distort')
            if 'reverb_type' in onlseq_s_iparams: 
                if 'reverb' not in used_fx_inst[instid]: used_fx_inst[instid].append('reverb')
            if 'reverb_on' in onlseq_s_iparams: 
                if 'reverb' not in used_fx_inst[instid]: used_fx_inst[instid].append('reverb')
            if 'reverb_wet' in onlseq_s_iparams: 
                if 'reverb' not in used_fx_inst[instid]: used_fx_inst[instid].append('reverb')
            if 'eq_high' in onlseq_s_iparams: 
                if 'eq' not in used_fx_inst[instid]: used_fx_inst[instid].append('eq')
            if 'eq_mid' in onlseq_s_iparams: 
                if 'eq' not in used_fx_inst[instid]: used_fx_inst[instid].append('eq')
            if 'eq_low' in onlseq_s_iparams: 
                if 'eq' not in used_fx_inst[instid]: used_fx_inst[instid].append('eq')

        bpm = 120
        if '1' in onlseq_data_main: bpm = int(onlseq_data_main['1'])

        for onlseq_data_marker in dict2list(onlseq_data_markers):
            t_markerdata = parse_marker(onlseq_data_marker)

            trackid = 'os_'+str(t_markerdata[0])
            if t_markerdata[0] != -1:

                if t_markerdata[0] not in used_fx_inst: used_fx_inst[t_markerdata[0]] = []

                if t_markerdata[1] == 'vol': auto_nopl.addpoint(['track', trackid, 'vol'], 'float', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                if t_markerdata[1] == 'pan': auto_nopl.addpoint(['track', trackid, 'pan'], 'float', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                if t_markerdata[1] == 'detune': auto_nopl.addpoint(['track', trackid, 'pitch'], 'float', t_markerdata[2], t_markerdata[3]/100, t_markerdata[4])

                if t_markerdata[1] in ['eq_high', 'eq_mid', 'eq_low']: 
                    auto_nopl.addpoint(['plugin', trackid+'_eq', t_markerdata[1]], 'float', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                    if 'eq' not in used_fx_inst[t_markerdata[0]]: used_fx_inst[t_markerdata[0]].append('eq')

                if t_markerdata[1] == 'delay_on': 
                    auto_nopl.addpoint(['slot', trackid+'_delay', 'enabled'], 'bool', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                    if 'delay' not in used_fx_inst[t_markerdata[0]]: used_fx_inst[t_markerdata[0]].append('delay')

                if t_markerdata[1] == 'reverb_type': 
                    auto_nopl.addpoint(['plugin', trackid+'_reverb', 'reverb_type'], 'float', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                    if 'reverb' not in used_fx_inst[t_markerdata[0]]: used_fx_inst[t_markerdata[0]].append('reverb')

                if t_markerdata[1] == 'reverb_wet': 
                    auto_nopl.addpoint(['slot', trackid+'_reverb', 'wet'], 'float', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                    if 'reverb' not in used_fx_inst[t_markerdata[0]]: used_fx_inst[t_markerdata[0]].append('reverb')

                if t_markerdata[1] == 'distort_type': 
                    if t_markerdata[3] != 0: auto_nopl.addpoint(['plugin', trackid+'_distort', 'distort_type'], 'int', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                    auto_nopl.addpoint(['slot', trackid+'_distort', 'enabled'], 'bool', t_markerdata[2], int(bool(t_markerdata[3])), t_markerdata[4])
                    if 'distort' not in used_fx_inst[t_markerdata[0]]: used_fx_inst[t_markerdata[0]].append('distort')

                if t_markerdata[1] == 'distort_wet': 
                    auto_nopl.addpoint(['slot', trackid+'_distort', 'wet'], 'float', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                    if 'distort' not in used_fx_inst[t_markerdata[0]]: used_fx_inst[t_markerdata[0]].append('distort')

            else:
                if t_markerdata[1] == 'vol': auto_nopl.addpoint(['song', 'vol'], 'float', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                if t_markerdata[1] == 'bpm': auto_nopl.addpoint(['song', 'bpm'], 'float', t_markerdata[2], t_markerdata[3], t_markerdata[4])

        for used_fx_inst_i in used_fx_inst:

            autoid = str(used_fx_inst_i)
            trackid = 'os_'+str(used_fx_inst_i)

            if 'delay' in used_fx_inst[used_fx_inst_i]:
                pluginid = trackid+'_delay'
                plugins.add_plug(cvpj_l, pluginid, 'universal', 'delay-c')
                fx_enabled = bool(data_values.get_value(onlseq_data_instparams[used_fx_inst_i], 'delay_on', 0))

                plugins.add_plug_data(cvpj_l, pluginid, 'time_type', 'steps')
                plugins.add_plug_data(cvpj_l, pluginid, 'time', 2)
                plugins.add_plug_data(cvpj_l, pluginid, 'feedback', 0.25)

                plugins.add_plug_fxdata(cvpj_l, pluginid, fx_enabled, 0.5)
                plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Delay', None)
                fxslot.insert(cvpj_l, ['track', trackid], 'audio', pluginid)

            if 'distort' in used_fx_inst[used_fx_inst_i]:
                pluginid = trackid+'_distort'
                plugins.add_plug(cvpj_l, pluginid, 'native-onlineseq', 'distort')
                fx_wet = data_values.get_value(onlseq_data_instparams[used_fx_inst_i], 'distort_wet', 0)
                plugins.add_plug_fxdata(cvpj_l, pluginid, True, fx_wet)
                plugins.add_plug_param(cvpj_l, pluginid, 'distort_type', 
                    data_values.get_value(onlseq_data_instparams[used_fx_inst_i], 'distort_type', 0)
                    , 'int', 'Type')
                plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Distortion', None)
                fxslot.insert(cvpj_l, ['track', trackid], 'audio', pluginid)

            if 'reverb' in used_fx_inst[used_fx_inst_i]:
                pluginid = trackid+'_reverb'
                plugins.add_plug(cvpj_l, pluginid, 'native-onlineseq', 'reverb')
                fx_enabled = bool(data_values.get_value(onlseq_data_instparams[used_fx_inst_i], 'reverb_on', 0))
                fx_wet = data_values.get_value(onlseq_data_instparams[used_fx_inst_i], 'reverb_wet', 1)
                plugins.add_plug_param(cvpj_l, pluginid, 'reverb_type', 
                    data_values.get_value(onlseq_data_instparams[used_fx_inst_i], 'reverb_type', 0)
                    , 'int', 'Type')
                plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Reverb', None)
                fxslot.insert(cvpj_l, ['track', trackid], 'audio', pluginid)

            if 'eq' in used_fx_inst[used_fx_inst_i]:
                pluginid = trackid+'_eq'
                fx_enabled = bool(data_values.get_value(onlseq_data_instparams[used_fx_inst_i], 'enable_eq', 0))
                plugins.add_plug(cvpj_l, pluginid, 'native-onlineseq', 'eq')
                plugins.add_plug_fxdata(cvpj_l, pluginid, fx_enabled, 1)
                for paramname in ['eq_high', 'eq_mid', 'eq_low']:
                    plugins.add_plug_param(cvpj_l, pluginid, paramname, 
                        data_values.get_value(onlseq_data_instparams[used_fx_inst_i], paramname, 0)
                        , 'float', paramname)
                plugins.add_plug_fxvisual(cvpj_l, pluginid, 'EQ', None)
                fxslot.insert(cvpj_l, ['track', trackid], 'audio', pluginid)

        auto_nopl.to_cvpj(cvpj_l)

        timesig_numerator = 4
        if '2' in onlseq_data_main: timesig_numerator = int(onlseq_data_main['2'])

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True

        cvpj_l['keynames_data'] = cvpj_l_keynames_data
        song.add_param(cvpj_l, 'bpm', bpm)
        cvpj_l['timesig'] = [timesig_numerator, 4]

        return json.dumps(cvpj_l)
