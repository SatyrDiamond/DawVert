# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_mod
import plugin_input
import json
import varint
import struct

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

onlseq_instlist[39] = [0, None,[0.62, 0.06, 0.13],"8-Bit Drum Kit"]
onlseq_instlist[40] = [0, None,[0.51, 0.02, 0.08],"2013 Drum Kit"]
onlseq_instlist[36] = [0,   26,[0.50, 0.06, 0.28],"808 Drum Kit"]
onlseq_instlist[42] = [0, None,[0.60, 0.00, 1.00],"909 Drum Kit"]

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

def parse_note(data):
    global t_notelist
    #print(data.hex())
    notedata_bio = data_bytes.bytearray2BytesIO(data)
    notedata_len = len(data)
    onlseq_pos = 0
    onlseq_inst = 0
    while notedata_bio.tell() < notedata_len:
        firstbyte = int.from_bytes(notedata_bio.read(1))
        if firstbyte == 8: onlseq_note = int.from_bytes(notedata_bio.read(1))-60
        elif firstbyte == 21: onlseq_pos = struct.unpack('f', notedata_bio.read(4))[0]
        elif firstbyte == 29: onlseq_dur = struct.unpack('f', notedata_bio.read(4))[0]
        elif firstbyte == 32: onlseq_inst = int.from_bytes(notedata_bio.read(1))
        elif firstbyte == 45: secondbyte = struct.unpack('f', notedata_bio.read(4))[0]
        else: print('[input-onlinesequencer] Sequence/Notes: Unknown Byte: ',firstbyte)
    cvpj_note = {}
    cvpj_note['position'] = onlseq_pos
    cvpj_note['key'] = onlseq_note
    cvpj_note['duration'] = onlseq_dur
    if onlseq_inst not in t_notelist: t_notelist[onlseq_inst] = []
    t_notelist[onlseq_inst].append(cvpj_note)


class input_onlinesequencer(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'onlinesequencer'
    def getname(self): return 'Online Sequencer'
    def gettype(self): return 'r'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global t_notelist
        onlseq_f_stream = open(input_file, 'rb')
        onlseq_f_stream.seek(0,2)
        onlseq_len = onlseq_f_stream.tell()
        onlseq_f_stream.seek(0)

        onlseq_data_notes = []
        onlseq_data_extra = []

        cvpj_l_playlist = {}
        cvpj_l_trackdata = {}
        cvpj_l_trackordering = []
        cvpj_l_timemarkers = []
        cvpj_l_fxrack = {}

        while onlseq_f_stream.tell() < onlseq_len:
            firstbyte_bin = onlseq_f_stream.read(1)
            firstbyte = int.from_bytes(firstbyte_bin, "little")
            #print('--------- '+str(firstbyte).ljust(3), '0x'+firstbyte_bin.hex(), end=' ')
            if firstbyte == 10:
                secondbyte = varint.decode_stream(onlseq_f_stream)
                print('[input-onlinesequencer] Sequence/Main')
                onlseq_data_main = onlseq_f_stream.read(secondbyte)
            elif firstbyte == 18:
                secondbyte = int.from_bytes(onlseq_f_stream.read(1))
                onlseq_data_notes.append(onlseq_f_stream.read(secondbyte))
            elif firstbyte == 26:
                secondbyte = int.from_bytes(onlseq_f_stream.read(1))
                onlseq_data_extra.append(onlseq_f_stream.read(secondbyte))
            else:
                print('[input-onlinesequencer] Sequence: Unknown Byte: ',firstbyte)
                print(firstbyte, firstbyte_bin, onlseq_f_stream.read(20).hex())
                exit()
        print('[input-onlinesequencer] Sequence/Notes:', len(onlseq_data_notes))

        t_notelist = {}

        for onlseq_data_note in onlseq_data_notes:
            parse_note(onlseq_data_note)

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
                    cvpj_instdata['plugindata'] = {'bank':128, 'inst':onlseq_instlist[instid][1]-1}
                else:
                    cvpj_instdata['plugindata'] = {'bank':0, 'inst':onlseq_instlist[instid][1]-1}
            else:
                cvpj_instdata['plugin'] = 'none'
            cvpj_inst['placements'] = [{}]
            cvpj_inst['placements'][0]['position'] = 0
            cvpj_inst['placements'][0]['duration'] = note_mod.getduration(cvpj_notelist)
            cvpj_inst['placements'][0]['notelist'] = cvpj_notelist
            cvpj_l_trackdata['os_'+str(instid)] = cvpj_inst
            cvpj_l_trackordering.append('os_'+str(instid))

        cvpj_l = {}
        cvpj_l['use_fxrack'] = False
        cvpj_l['trackdata'] = cvpj_l_trackdata
        cvpj_l['trackordering'] = cvpj_l_trackordering
        cvpj_l['bpm'] = 120

        return json.dumps(cvpj_l)
