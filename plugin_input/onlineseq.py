# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_mod
from functions import placements
import plugin_input
import json
import struct
import blackboxprotobuf

onlseq_instlist = {}
onlseq_instlist[43] = [0,    5,[0.01, 0.66, 0.96],"Electric Piano"]
onlseq_instlist[41] = [0,    1,[0.08, 0.40, 0.75],"Grand Piano"]
onlseq_instlist[17] = [0,    7,[1.00, 0.34, 0.13],"Harpsichord"]
onlseq_instlist[25] = [0,    4,[0.05, 0.28, 0.63],"Ragtime Piano"]
onlseq_instlist[26] = [0,   11,[0.11, 0.62, 0.62],"Music Box"]
onlseq_instlist[ 0] = [0,    5,[0.01, 0.66, 0.96],"Elec. Piano (Classic)"]
onlseq_instlist[ 8] = [0,    1,[0.08, 0.40, 0.75],"Grand Piano (Classic)"]

onlseq_instlist[ 2] = [1,    1,[0.72, 0.11, 0.11],"Drum Kit"]
onlseq_instlist[31] = [1,   25,[1.00, 0.44, 0.44],"Electric Drum Kit"]
onlseq_instlist[19] = [0,   14,[0.96, 0.26, 0.21],"Xylophone"]
onlseq_instlist[34] = [0,   12,[0.33, 0.79, 0.79],"Vibraphone"]
onlseq_instlist[21] = [0,  115,[0.46, 0.46, 0.46],"Steel Drums"]

onlseq_instlist[39] = [1, None,[0.62, 0.06, 0.13],"8-Bit Drum Kit"]
onlseq_instlist[40] = [1, None,[0.51, 0.02, 0.08],"2013 Drum Kit"]
onlseq_instlist[36] = [1,   26,[0.50, 0.06, 0.28],"808 Drum Kit"]
onlseq_instlist[42] = [1, None,[0.60, 0.00, 1.00],"909 Drum Kit"]

onlseq_instlist[ 1] = [0,   25,[1.00, 0.60, 0.00],"Acoustic Guitar"]
onlseq_instlist[ 4] = [0,   27,[0.30, 0.69, 0.31],"Electric Guitar"]
onlseq_instlist[48] = [0,   33,[0.13, 0.13, 0.13],"Bass"]
onlseq_instlist[ 5] = [0,   33,[0.13, 0.13, 0.13],"Bass (Classic)"]
onlseq_instlist[29] = [0,   37,[0.02, 0.06, 0.18],"Slap Bass"]
onlseq_instlist[32] = [0,   27,[0.63, 0.65, 0.21],"Jazz Guitar"]
onlseq_instlist[35] = [0,   29,[0.00, 0.50, 0.25],"Muted E-Guitar"]
onlseq_instlist[38] = [0,   31,[0.00, 0.27, 0.12],"Distortion Guitar"]
onlseq_instlist[49] = [0,   28,[0.88, 0.83, 0.09],"Clean Guitar"]
onlseq_instlist[22] = [0,  105,[0.88, 0.68, 0.00],"Sitar"]
onlseq_instlist[33] = [0,  108,[0.92, 0.47, 0.00],"Koto"]

onlseq_instlist[ 3] = [0, None,[0.91, 0.12, 0.39],"Smooth Synth"]
onlseq_instlist[ 6] = [0, None,[0.25, 0.32, 0.71],"Synth Pluck"]
onlseq_instlist[ 7] = [0, None,[0.80, 0.86, 0.22],"Scifi"]
onlseq_instlist[13] = [0, None,[1.00, 0.39, 0.39],"8-Bit Sine"]
onlseq_instlist[14] = [0, None,[0.46, 1.00, 0.39],"8-Bit Square"]
onlseq_instlist[15] = [0, None,[0.39, 0.88, 1.00],"8-Bit Sawtooth"]
onlseq_instlist[16] = [0, None,[0.99, 0.39, 1.00],"8-Bit Triangle"]

onlseq_instlist[ 9] = [0,   61,[0.51, 0.47, 0.09],"French Horn"]
onlseq_instlist[10] = [0,   58,[1.00, 0.92, 0.00],"Trombone"]
onlseq_instlist[11] = [0,   41,[0.55, 0.43, 0.39],"Violin"]
onlseq_instlist[46] = [0,   41,[0.55, 0.43, 0.39],"Violin (Sustain)"]
onlseq_instlist[12] = [0,   43,[0.31, 0.20, 0.18],"Cello"]
onlseq_instlist[45] = [0,   43,[0.31, 0.20, 0.18],"Cello (Sustain)"]
onlseq_instlist[18] = [0,   47,[0.11, 0.37, 0.13],"Concert Harp"]
onlseq_instlist[20] = [0,   46,[1.00, 0.88, 0.70],"Pizzicato"]
onlseq_instlist[23] = [0,   74,[0.91, 0.98, 0.74],"Flute"]
onlseq_instlist[47] = [0,   49,[0.56, 0.46, 1.00],"Strings (Sustain)"]

onlseq_instlist[24] = [0,   65,[0.66, 0.78, 0.33],"Saxophone"]
onlseq_instlist[27] = [0,   39,[0.12, 0.77, 0.48],"Synth Bass"]
onlseq_instlist[28] = [0,   20,[0.08, 0.13, 0.31],"Church Organ"]
onlseq_instlist[30] = [0,   91,[0.42, 0.95, 0.72],"Pop Synth"]
onlseq_instlist[37] = [0, None,[0.00, 0.00, 0.00],"808 Bass"]

def print_value(name, data):
    print(str(' '+name+': '+str(data)).ljust(11), end=' ')


def parse_inst_params(data):
    outputlist = {}
    for part in data:
        if '1' in part: instid = int(part['1'])
        if '2' in part: 
            params = part['2']
            instparams = {}
            if '1' in params: instparams['volume'] = int2float(int(params['1']))
            if '2' in params: instparams['delay'] = int(params['2'])
            if '3' in params: instparams['reverb'] = int(params['3'])
            if '10' in params: instparams['reverb_type'] = int(params['10'])
            if '11' in params: instparams['one_minus_reverb_volume'] = int2float(int(params['11']))
            if '4' in params: instparams['pan'] = int2float(int(params['4']))
            if '5' in params: instparams['enable_eq'] = int(params['5'])
            if '6' in params: instparams['eq_low'] = int2float(int(params['6']))
            if '7' in params: instparams['eq_mid'] = int2float(int(params['7']))
            if '8' in params: instparams['eq_high'] = int2float(int(params['8']))
            if '9' in params: instparams['detune'] = int2float(int(params['9']))
            if '12' in params: instparams['distort_type'] = int(params['12'])
            if '13' in params: instparams['distort_volume'] = int2float(int(params['13']))
            outputlist[instid] = instparams
    return outputlist

def parse_note(notedata):
    global t_notelist
    ols_pos = 0
    ols_inst = 0
    ols_vol = 1
    ols_note = int(notedata['1'])
    ols_dur = int2float(int(notedata['3']))
    if '4' in notedata: ols_inst = int(notedata['4'])
    if '2' in notedata: ols_pos = int2float(int(notedata['2']))
    if '3' in notedata: ols_dur = int2float(int(notedata['3']))
    if '5' in notedata: ols_vol = int2float(int(notedata['5']))
    note = {}
    note['position'] = ols_pos
    note['key'] = ols_note-60
    note['duration'] = ols_dur
    note['volume'] = ols_vol
    if ols_inst not in t_notelist: t_notelist[ols_inst] = []
    t_notelist[ols_inst].append(note)

def int2float(value): return struct.unpack("<f", struct.pack("<I", value))[0]

class input_onlinesequencer(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'onlineseq'
    def getname(self): return 'Online Sequencer'
    def gettype(self): return 'r'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global t_notelist

        cvpj_l_trackdata = {}
        cvpj_l_trackordering = []
        cvpj_l_timemarkers = []
        cvpj_l_fxrack = {}

        os_data_song_stream = open(input_file, 'rb')
        os_data_song_data = os_data_song_stream.read()
        message, typedef = blackboxprotobuf.protobuf_to_json(os_data_song_data)

        os_data = json.loads(message)

        onlseq_data_main = os_data["1"]
        onlseq_data_notes = os_data["2"]

        if "3" in onlseq_data_main: 
            onlseq_data_instparams = parse_inst_params(os_data["1"]["3"])
        else: onlseq_data_instparams = {}

        #for partt in onlseq_data_extra:
        #    print(partt)

        t_notelist = {}

        for os_note in onlseq_data_notes:
            parse_note(os_note)

        for instid in t_notelist:
            cvpj_notelist = t_notelist[instid]

            cvpj_inst = {}
            cvpj_inst["type"] = 'instrument'
            cvpj_inst["name"] = onlseq_instlist[instid][3]
            cvpj_inst["color"] = onlseq_instlist[instid][2]
            cvpj_inst["instdata"] = {}
            cvpj_instdata = cvpj_inst["instdata"]
            if onlseq_instlist[instid][1] != None:
                cvpj_instdata['plugin'] = 'general-midi'
                if onlseq_instlist[instid][0] == 1:
                    cvpj_instdata['usemasterpitch'] = 0
                    cvpj_instdata['plugindata'] = {'bank':128, 'inst':onlseq_instlist[instid][1]-1}
                else:
                    cvpj_instdata['usemasterpitch'] = 1
                    cvpj_instdata['plugindata'] = {'bank':0, 'inst':onlseq_instlist[instid][1]-1}
            else:
                cvpj_instdata['plugin'] = 'none'
            if instid in onlseq_data_instparams:
                if 'volume' in onlseq_data_instparams[instid]:
                    cvpj_inst["vol"] = onlseq_data_instparams[instid]['volume']
                if 'pan' in onlseq_data_instparams[instid]:
                    cvpj_inst["pan"] = onlseq_data_instparams[instid]['pan']

            cvpj_placement = {}
            cvpj_placement['position'] = 0
            cvpj_placement['duration'] = note_mod.getduration(cvpj_notelist)
            cvpj_placement['notelist'] = cvpj_notelist

            cvpj_placement = placements.resize_nl(cvpj_placement)

            cvpj_inst['placements'] = [cvpj_placement]
            cvpj_l_trackdata['os_'+str(instid)] = cvpj_inst
            cvpj_l_trackordering.append('os_'+str(instid))

        cvpj_l = {}
        cvpj_l['use_fxrack'] = False
        cvpj_l['trackdata'] = cvpj_l_trackdata
        cvpj_l['trackordering'] = cvpj_l_trackordering
        cvpj_l['timesig_denominator'] = 4
        
        if '1' in onlseq_data_main: cvpj_l['bpm'] = int(onlseq_data_main['1'])
        else: cvpj_l['bpm'] = 120

        if '2' in onlseq_data_main: cvpj_l['timesig_numerator'] = int(onlseq_data_main['2'])
        else: cvpj_l['timesig_numerator'] = 4

        return json.dumps(cvpj_l)
