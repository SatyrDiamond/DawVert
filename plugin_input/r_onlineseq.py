# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_mod
from functions import notelist_data
from functions import auto
from functions import idvals
from functions import placement_data
from functions import tracks
from functions import note_data
import plugin_input
import json
import struct
import blackboxprotobuf

onlseq_auto = {}
onlseq_auto['1'] = ['vol',1]
onlseq_auto['2'] = ['delay',0]
onlseq_auto['3'] = ['reverb',0]
onlseq_auto['4'] = ['pan',1]
onlseq_auto['5'] = ['enable_eq',0]
onlseq_auto['6'] = ['eq_low',1]
onlseq_auto['7'] = ['eq_mid',1]
onlseq_auto['8'] = ['eq_high',1]
onlseq_auto['9'] = ['detune',1]
onlseq_auto['10'] = ['reverb_type',0]
onlseq_auto['11'] = ['one_minus_reverb_volume',1]
onlseq_auto['12'] = ['distort_type',0]
onlseq_auto['13'] = ['distort_volume',1]

def int2float(value): return struct.unpack("<f", struct.pack("<I", value))[0]

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
                param_name, param_isfloat = onlseq_auto[param]
                if param_isfloat == 1: instparams[param_name] = int2float(int(params[param]))
                if param_isfloat == 0: instparams[param_name] = int(params[param])
            outputlist[instid] = instparams
    return outputlist

def parse_marker(markerdata):
    data = {}
    inst = {}
    markertype = 'instant'

    if '1' in markerdata: data['position'] = int2float(int(markerdata['1']))
    if '2' in markerdata: inst['param'] = onlseq_auto[markerdata['2']][0]
    if '3' in markerdata: inst['id'] = markerdata['3']
    if '4' in markerdata: data['value'] = int2float(int(markerdata['4']))
    if '5' in markerdata: markertype = 'normal'
    data['type'] = markertype
    return (inst, data)

def parse_note(notedata):
    global onlseq_notelist
    ols_pos = 0
    ols_inst = 0
    ols_vol = 1
    ols_note = int(notedata['1'])
    ols_dur = 1
    if '4' in notedata: ols_inst = int(notedata['4'])
    if '2' in notedata: ols_pos = int2float(int(notedata['2']))
    if '3' in notedata: ols_dur = int2float(int(notedata['3']))
    if '5' in notedata: ols_vol = int2float(int(notedata['5']))
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
        'fxrack': False,
        'r_track_lanes': False,
        'placement_cut': False,
        'placement_warp': False,
        'no_pl_auto': True,
        'no_placements': True
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global onlseq_notelist

        cvpj_l = {}
        
        cvpj_l_keynames_data = {}

        cvpj_automation = {}
        cvpj_automation['main'] = {}
        cvpj_automation['track'] = {}
        os_data_song_stream = open(input_file, 'rb')
        os_data_song_data = os_data_song_stream.read()
        message, typedef = blackboxprotobuf.protobuf_to_json(os_data_song_data)

        idvals_onlineseq_inst = idvals.parse_idvalscsv('idvals/onlineseq_inst.csv')
        idvals_onlineseq_drumkit = idvals.parse_idvalscsv('idvals/onlineseq_drumkit.csv')
        idvals_onlineseq_drumkit_808 = idvals.parse_idvalscsv('idvals/onlineseq_drumkit_808.csv')
        idvals_onlineseq_drumkit_909 = idvals.parse_idvalscsv('idvals/onlineseq_drumkit_909.csv')
        idvals_onlineseq_drumkit_2013 = idvals.parse_idvalscsv('idvals/onlineseq_drumkit_2013.csv')
        idvals_onlineseq_drumkit_retro = idvals.parse_idvalscsv('idvals/onlineseq_drumkit_retro.csv')
        
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

        for onlseq_data_marker in onlseq_data_markers:
            t_markerdata = parse_marker(onlseq_data_marker)

            position = 0
            value = 0
            if 'position' in t_markerdata[1]: position = t_markerdata[1]['position']
            if 'value' in t_markerdata[1]: value = t_markerdata[1]['value']
            marker_type = t_markerdata[1]['type']

            if t_markerdata[0] == {}:
                t_auto_tempo.append({"position": position, 'type': marker_type, "value": value})
            elif 'param' in t_markerdata[0]:
                if t_markerdata[0]['param'] == 'eq_high':
                    t_auto_vol.append({"position": position, 'type': marker_type, "value": value})
            elif 'id' in t_markerdata[0]:
                inst_id = int(t_markerdata[0]['id'])
                inst_param = str(t_markerdata[0]['param'])
                if 'value' in t_markerdata[1]:
                    if inst_id not in t_auto_inst: t_auto_inst[inst_id] = {}
                    if inst_param not in t_auto_inst[inst_id]: t_auto_inst[inst_id][inst_param] = []
                    t_auto_inst[inst_id][inst_param].append({"position": position, 'type': marker_type, "value": value})

        if "3" in onlseq_data_main: onlseq_data_instparams = parse_inst_params(os_data["1"]["3"])
        else: onlseq_data_instparams = {}

        onlseq_notelist = {}

        for os_note in onlseq_data_notes: parse_note(os_note)

        songduration = 0

        for instid in onlseq_notelist:
            cvpj_notelist = onlseq_notelist[instid]

            inst_name = idvals.get_idval(idvals_onlineseq_inst, str(instid), 'name')
            inst_color = idvals.get_idval(idvals_onlineseq_inst, str(instid), 'color')
            inst_gminst = idvals.get_idval(idvals_onlineseq_inst, str(instid), 'gm_inst')
            inst_isdrum = idvals.get_idval(idvals_onlineseq_inst, str(instid), 'isdrum')
            cvpj_instdata = {}
            if inst_gminst != None:
                cvpj_instdata['plugin'] = 'general-midi'
                if inst_isdrum == True: cvpj_instdata = {'plugin': 'general-midi', 'usemasterpitch': 0, 'plugindata': {'bank':128, 'inst':inst_gminst-1}}
                else: cvpj_instdata = {'plugin': 'general-midi', 'usemasterpitch': 1, 'plugindata': {'bank':0, 'inst':inst_gminst-1}}

            trk_vol = 1
            trk_pan = 0

            if instid in onlseq_data_instparams:
                if 'vol' in onlseq_data_instparams[instid]: trk_vol = onlseq_data_instparams[instid]['vol']
                if 'pan' in onlseq_data_instparams[instid]: trk_pan = onlseq_data_instparams[instid]['pan']

            trackduration = notelist_data.getduration(cvpj_notelist)
            if trackduration > songduration: songduration = trackduration

            instid = 'os_'+str(instid)
            if instid in t_auto_inst:
                cvpj_automation['track'][instid] = {}
                for param in t_auto_inst[instid]:
                    cvpj_autodata = {}
                    cvpj_autodata["position"] = 0
                    cvpj_autodata["duration"] = trackduration
                    cvpj_autodata["points"] = t_auto_inst[instid][param]
                    auto.resize(cvpj_autodata)
                    cvpj_automation['track'][instid][param] = [cvpj_autodata]

            tracks.r_create_inst(cvpj_l, instid, cvpj_instdata)
            tracks.r_basicdata(cvpj_l, instid, inst_name, inst_color, trk_vol, trk_pan)
            tracks.r_pl_notes(cvpj_l, instid, placement_data.nl2pl(cvpj_notelist))

        bpm = 120
        if '1' in onlseq_data_main: bpm = int(onlseq_data_main['1'])

        if t_auto_vol != []:
            cvpj_autodata = {}
            cvpj_autodata["position"] = 0
            cvpj_autodata["duration"] = songduration
            cvpj_autodata["points"] = [{'position': 0, 'value': 1}]
            for point in t_auto_vol: cvpj_autodata["points"].append(point)
            cvpj_automation['main']['vol'] = [cvpj_autodata]

        if t_auto_tempo != []:
            cvpj_autodata = {}
            cvpj_autodata["position"] = 0
            cvpj_autodata["duration"] = songduration
            cvpj_autodata["points"] = [{'position': 0, 'value': bpm}]
            for point in t_auto_tempo: cvpj_autodata["points"].append(point)
            cvpj_automation['main']['bpm'] = [cvpj_autodata]

        timesig_numerator = 4
        if '2' in onlseq_data_main: timesig_numerator = int(onlseq_data_main['2'])

        cvpj_l['do_addwrap'] = True
        cvpj_l['do_singlenotelistcut'] = True

        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        
        cvpj_l['keynames_data'] = cvpj_l_keynames_data
        cvpj_l['bpm'] = bpm
        cvpj_l['timesig_denominator'] = 4
        cvpj_l['timesig_numerator'] = timesig_numerator
        cvpj_l['automation'] = cvpj_automation

        return json.dumps(cvpj_l)
