# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import auto
from functions import data_bytes
from functions import data_values
from functions import idvals
from functions import note_data
from functions import note_mod
from functions import notelist_data
from functions import placement_data
from functions import tracks
import plugin_input
import json
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
    if '4' in notedata: ols_inst = int(notedata['4'])
    if '2' in notedata: ols_pos = int2float(int(notedata['2']))
    if '3' in notedata: ols_dur = int2float(int(notedata['3']))
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
        'fxrack': False,
        'r_track_lanes': False,
        'placement_cut': False,
        'placement_loop': False,
        'no_pl_auto': True,
        'no_placements': True
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global onlseq_notelist

        cvpj_l = {}
        
        cvpj_l_keynames_data = {}

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

        for os_note in onlseq_data_notes: parse_note(os_note)

        for instid in onlseq_notelist:
            cvpj_instid = 'os_'+str(instid)
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

            onlseq_s_iparams = {}
            if instid in onlseq_data_instparams: onlseq_s_iparams = onlseq_data_instparams[instid]
            trk_vol = data_values.get_value(onlseq_s_iparams, 'vol', 1)
            trk_pan = data_values.get_value(onlseq_s_iparams, 'pan', 0)

            tracks.r_create_inst(cvpj_l, cvpj_instid, cvpj_instdata)
            tracks.r_basicdata(cvpj_l, cvpj_instid, inst_name, inst_color, trk_vol, trk_pan)
            tracks.r_pl_notes(cvpj_l, cvpj_instid, placement_data.nl2pl(cvpj_notelist))

            tracks.make_fxslot_simple(cvpj_l, 'onlineseq', 'r_track', cvpj_instid, 
                data_values.get_value(onlseq_s_iparams, 'delay_on', 0), 
                None, 
                cvpj_instid+'_delay', 'delay', {})

            fx_distort_data = {}
            fx_distort_data['distort_type'] = data_values.get_value(onlseq_s_iparams, 'distort_type', 0)
            tracks.make_fxslot_simple(cvpj_l, 'onlineseq', 'r_track', cvpj_instid, 
                None, 
                data_values.get_value(onlseq_s_iparams, 'distort_wet', 1), 
                cvpj_instid+'_distort', 'distort', fx_distort_data)

            fx_reverb_data = {}
            fx_reverb_data['reverb_type'] = data_values.get_value(onlseq_s_iparams, 'reverb_type', 0)
            tracks.make_fxslot_simple(cvpj_l, 'onlineseq', 'r_track', cvpj_instid, 
                data_values.get_value(onlseq_s_iparams, 'reverb_on', 0), 
                data_values.get_value(onlseq_s_iparams, 'reverb_wet', 1), 
                cvpj_instid+'_reverb', 'reverb', fx_reverb_data)

            fx_eq_data = {}
            fx_eq_data['eq_high'] = data_values.get_value(onlseq_s_iparams, 'eq_high', 0)
            fx_eq_data['eq_mid'] = data_values.get_value(onlseq_s_iparams, 'eq_mid', 0)
            fx_eq_data['eq_low'] = data_values.get_value(onlseq_s_iparams, 'eq_low', 0)
            tracks.make_fxslot_simple(cvpj_l, 'onlineseq', 'r_track', cvpj_instid, 
                data_values.get_value(onlseq_s_iparams, 'enable_eq', 0), None, cvpj_instid+'_eq', 'eq', fx_eq_data)

        bpm = 120
        if '1' in onlseq_data_main: bpm = int(onlseq_data_main['1'])

        for onlseq_data_marker in dict2list(onlseq_data_markers):
            t_markerdata = parse_marker(onlseq_data_marker)

            trackid = 'os_'+str(t_markerdata[0])
            if t_markerdata[0] != -1:
                if t_markerdata[1] == 'vol': tracks.a_auto_nopl_addpoint('track', trackid, 'vol', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                if t_markerdata[1] == 'pan': tracks.a_auto_nopl_addpoint('track', trackid, 'pan', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                if t_markerdata[1] in ['eq_high', 'eq_mid', 'eq_low']: tracks.a_auto_nopl_addpoint('plugin', trackid+'_eq', t_markerdata[1], t_markerdata[2], t_markerdata[3], t_markerdata[4])
                if t_markerdata[1] == 'delay_on': tracks.a_auto_nopl_addpoint('slot', trackid+'_delay', 'enabled', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                if t_markerdata[1] == 'reverb_type': tracks.a_auto_nopl_addpoint('plugin', trackid+'_reverb', 'reverb_type', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                if t_markerdata[1] == 'reverb_wet': tracks.a_auto_nopl_addpoint('slot', trackid+'_reverb', 'wet', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                if t_markerdata[1] == 'detune': tracks.a_auto_nopl_addpoint('track', trackid, 'pitch', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                if t_markerdata[1] == 'distort_type': 
                    if t_markerdata[3] != 0: tracks.a_auto_nopl_addpoint('plugin', trackid+'_distort', 'distort_type', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                    tracks.a_auto_nopl_addpoint('slot', trackid+'_distort', 'enabled', t_markerdata[2], int(bool(t_markerdata[3])), t_markerdata[4])
                if t_markerdata[1] == 'distort_wet': tracks.a_auto_nopl_addpoint('slot', trackid+'_distort', 'wet', t_markerdata[2], t_markerdata[3], t_markerdata[4])
            else:
                if t_markerdata[1] == 'vol': tracks.a_auto_nopl_addpoint('song', None, 'vol', t_markerdata[2], t_markerdata[3], t_markerdata[4])
                if t_markerdata[1] == 'bpm': tracks.a_auto_nopl_addpoint('song', None, 'bpm', t_markerdata[2], t_markerdata[3], t_markerdata[4])

        tracks.a_auto_nopl_to_cvpj(cvpj_l)

        timesig_numerator = 4
        if '2' in onlseq_data_main: timesig_numerator = int(onlseq_data_main['2'])

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True

        cvpj_l['keynames_data'] = cvpj_l_keynames_data
        cvpj_l['bpm'] = bpm
        cvpj_l['timesig_denominator'] = 4
        cvpj_l['timesig_numerator'] = timesig_numerator

        return json.dumps(cvpj_l)
