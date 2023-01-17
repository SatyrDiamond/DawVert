# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import struct
from functions import data_bytes
from functions import values

gm_colors = values.getlist_gm_colors()
gm_names = values.getlist_gm_names()

def calc_gatetime(bio_mmf_Mtsq):
    out_duration = 0
    t_durgate = []
    t_durgate_value = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
    t_durgate.append(t_durgate_value)
    if bool(t_durgate_value & 0b10000000) == True: 
        t_durgate_value = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
        t_durgate.append(t_durgate_value)
        if bool(t_durgate_value & 0b10000000) == True: 
            t_durgate_value = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            t_durgate.append(t_durgate_value)

    shift = 0

    t_durgate.reverse()

    for note_durbyte in t_durgate:
        out_duration += (note_durbyte & 0b01111111) << shift
        shift += 7

    return out_duration

def noteresize(value):
    return value*8

def splitbyte(value):
    first = value >> 4
    second = value & 0x0F
    return (first, second)

def parse_ma3_Mtsq(Mtsqdata, tb_ms):
    bio_mmf_Mtsq = data_bytes.bytearray2BytesIO(Mtsqdata)
    bio_mmf_Mtsq_size = len(Mtsqdata)
    notecount = 0
    #print('size', bio_mmf_Mtsq_size)
    #print('      1ST 2ND | CH#  CMD')

    basepos = 0

    t_currentprogram = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    t_currentbank = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    t_cvpj_notelist = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    t_usedprograms = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    t_chanvol = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]

    beforenote = True
    position = 0
    while bio_mmf_Mtsq.tell() < bio_mmf_Mtsq_size:
        basepos += calc_gatetime(bio_mmf_Mtsq)

        #print(str(basepos).ljust(5), end=' ')

        firstbyte = splitbyte(int.from_bytes(bio_mmf_Mtsq.read(1), "big"))
        #print(str(firstbyte[0]).ljust(3), str(firstbyte[1]).ljust(3), end=' ')
        if firstbyte[0] == 0:
            null_durgate = calc_gatetime(bio_mmf_Mtsq)
            #print('|      NULL    ', null_durgate)
        elif firstbyte[0] == 8:
            note_note = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            note_durgate = calc_gatetime(bio_mmf_Mtsq)
            #print('| '+str(firstbyte[1]).ljust(4), 'NOTE    ', str(note_note).ljust(4), '     dur ', note_durgate)
            note_program = t_currentprogram[firstbyte[1]]
            note_bankprogram = [t_currentbank[firstbyte[1]], t_currentprogram[firstbyte[1]]]
            if note_bankprogram not in t_usedprograms[firstbyte[1]]:
                t_usedprograms[firstbyte[1]].append(note_bankprogram)
            cvpj_note = {}
            cvpj_note["duration"] = noteresize(note_durgate*tb_ms)
            cvpj_note["key"] = note_note-60
            cvpj_note["position"] = noteresize(basepos*tb_ms)
            cvpj_note["instrument"] = 'c'+str(firstbyte[1])+'b'+str(t_currentbank[firstbyte[1]])+'i'+str(note_program)
            t_cvpj_notelist[firstbyte[1]].append(cvpj_note)
            beforenote = False
        elif firstbyte[0] == 9:
            note_note = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            note_vol = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            note_durgate = calc_gatetime(bio_mmf_Mtsq)
            #print('| '+str(firstbyte[1]).ljust(4), 'NOTE+V  ', str(note_note).ljust(4), str(note_vol).ljust(4), 'dur ', note_durgate)
            note_program = t_currentprogram[firstbyte[1]]
            note_bankprogram = [t_currentbank[firstbyte[1]], t_currentprogram[firstbyte[1]]]
            if note_bankprogram not in t_usedprograms[firstbyte[1]]:
                t_usedprograms[firstbyte[1]].append(note_bankprogram)
            cvpj_note = {}
            cvpj_note["duration"] = noteresize(note_durgate*tb_ms)
            cvpj_note["key"] = note_note-60
            cvpj_note["position"] = noteresize(basepos*tb_ms)
            cvpj_note["vol"] = note_vol/128
            cvpj_note["instrument"] = 'c'+str(firstbyte[1])+'b'+str(t_currentbank[firstbyte[1]])+'i'+str(note_program)
            t_cvpj_notelist[firstbyte[1]].append(cvpj_note)
            beforenote = False

        elif firstbyte[0] == 11:
            cntltype = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            cntldata = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            #print('| '+str(firstbyte[1]).ljust(4), 'CONTROL ', str(cntltype).ljust(4), str(cntldata).ljust(4))
            if cntltype == 7:
                t_chanvol[firstbyte[1]] = cntldata/127
            if cntltype == 0:
                t_currentbank[firstbyte[1]] = cntldata
        elif firstbyte[0] == 12:
            prognumber = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            #print('| '+str(firstbyte[1]).ljust(4), 'PROGRAM ', prognumber)
            t_currentprogram[firstbyte[1]] = prognumber
        elif firstbyte[0] == 14:
            lsbpitch = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            msbpitch = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            #print('| '+str(firstbyte[1]).ljust(4), 'PITCH   ', str(lsbpitch).ljust(4), str(msbpitch).ljust(4))
        elif firstbyte[0] == 15 and firstbyte[1] == 0:
            sysexsize = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            sysexdata = bio_mmf_Mtsq.read(sysexsize)
            #print('| '+str(firstbyte[1]).ljust(4), 'SYSEX   ', sysexdata.hex())
        elif firstbyte[0] == 15 and firstbyte[1] == 15:
            pass
            #print('| '+str(firstbyte[1]).ljust(4), 'NOP     ')
        else:
            print('Unknown Command', firstbyte[0], "0x%X" % firstbyte[0])
            exit()

    for channel in range(16):
        print('[input-smaf] MA3, Channel '+str(channel))
        print('[input-smaf]       Notes: '+str(len(t_cvpj_notelist[channel])))
        print('[input-smaf]       Used Insts: '+str(', '.join(str(x) for x in t_usedprograms[channel])   ))
        print('[input-smaf]')
    return (3, 16, t_cvpj_notelist, t_usedprograms, t_chanvol)

def parse_ma3_track(datain, tracknum):
    bio_mmf_track = data_bytes.bytearray2BytesIO(datain)
    trk_type_format, trk_type_seq, trk_tb_d, trk_tb_g = struct.unpack("BBBB", bio_mmf_track.read(4))
    if trk_tb_d == 2: tb_ms = 0.004
    if trk_tb_d == 3: tb_ms = 0.005
    if trk_tb_d == 16: tb_ms = 0.010
    if trk_tb_d == 17: tb_ms = 0.020
    if trk_tb_d == 18: tb_ms = 0.040
    if trk_tb_d == 19: tb_ms = 0.050
    print('[input-smaf] TimeBase MS:', tb_ms*1000)
    trk_chanstat = struct.unpack("IIII", bio_mmf_track.read(16))
    #print(trk_type_format, trk_type_seq, trk_tb_d, trk_tb_g, trk_chanstat)
    trk_chunks = data_bytes.riff_read_big(bio_mmf_track.read(), 0)
    outputdata = None
    for trk_chunk in trk_chunks:
        print('[input-smaf] MTR CHUNK:',trk_chunk[0])
        if trk_chunk[0] == b'Mtsq':
            outputdata = parse_ma3_Mtsq(trk_chunk[1], tb_ms)
    if outputdata == None:
        print('[input-smaf] No Mtsq found.')
        exit()
    else:
        return outputdata


class input_mmf(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mmf'
    def getname(self): return 'Mobile Music File'
    def gettype(self): return 'm'
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'MMMD': return True
        else: return False
        bytestream.seek(0)
    def parse(self, input_file, extra_param):
        mmf_f_stream = open(input_file, 'rb')
        mmf_chunks_main = data_bytes.riff_read(mmf_f_stream.read(), 0)
        if mmf_chunks_main[0][0] != b'MMMD':
            print('[input-smaf] Not a SMAF File.'); exit()

        cvpj_l_playlist = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_fxrack = {}

        mmf_chunks_ins = data_bytes.riff_read(mmf_chunks_main[0][1], 0)

        trackparsed = False
        for mmf_chunk in mmf_chunks_ins:
            if mmf_chunk[0] == b'CNTI':
                bio_mmf_cnti = data_bytes.bytearray2BytesIO(mmf_chunk[1])
                mmf_cnti_class, mmf_cnti_type, mmf_cnti_codetype, mmf_cnti_status, mmf_cnti_counts = struct.unpack("BBBBB", bio_mmf_cnti.read(5))
                mmf_cnti_chunks = data_bytes.riff_read_big(bio_mmf_cnti, 5)
                for mmf_cnti_chunk in mmf_cnti_chunks:
                    print('[input-smaf] CNTI CHUNK:', mmf_cnti_chunk[0])
                    #if mmf_cnti_chunk[0] == b'OPDA':
                    #    print(mmf_cnti_chunk[1])
                    if mmf_cnti_chunk[0][:3] == b'MTR':
                        mmf_tracknum = int.from_bytes(mmf_cnti_chunk[0][3:], "big")
                        #print('track num', mmf_tracknum)
                        if mmf_tracknum in range(1, 4):
                            print('[input-smaf] Format: MA1/2 is not supported')
                            exit()
                        if mmf_tracknum in range(5, 8):
                            print('[input-smaf] Format: MA3')
                            trackparsed = True
                            matype, number_of_channels, t_cvpj_notelist, t_usedprograms, t_chanvol = parse_ma3_track(mmf_cnti_chunk[1], 3)

        cvpj_l_fxrack["0"] = {}
        cvpj_l_fxrack["0"]["name"] = "Master"

        if trackparsed == False:
            print('[input-smaf] No track data found.')
            exit()
        for channel in range(number_of_channels):
            c_notelist = t_cvpj_notelist[channel]
            c_usedinsts = t_usedprograms[channel]
            if matype == 3:
                for c_usedinst in c_usedinsts:
                    c_usedprogram = c_usedinst[1]
                    c_usedbank = c_usedinst[0]

                    instid = 'c'+str(channel)+'b'+str(c_usedbank)+'i'+str(c_usedprogram)
                    cvpj_inst = {}
                    if c_usedbank == 0:
                        cvpj_inst["name"] = gm_names[c_usedprogram]
                        cvpj_inst["color"] = gm_colors[c_usedprogram]
                        cvpj_inst["instdata"] = {}
                        cvpj_inst["instdata"]['plugin'] = 'general-midi'
                        if channel != 9:
                            cvpj_inst["instdata"]['usemasterpitch'] = 1
                            cvpj_inst["instdata"]['plugindata'] = {'bank':0, 'inst':c_usedprogram}
                        else:
                            cvpj_inst["instdata"]['usemasterpitch'] = 0
                            cvpj_inst["instdata"]['plugindata'] = {'bank':128, 'inst':0}
                    elif c_usedbank == 124:
                        cvpj_inst["name"] = 'MA-3 User #' + str(c_usedprogram)
                        cvpj_inst["color"] = [0.3,0.3,0.3]
                        cvpj_inst["instdata"] = {}
                        cvpj_inst["instdata"]['plugin'] = 'none'
                    elif c_usedbank == 125:
                        cvpj_inst["name"] = 'MA-3 PCM #' + str(c_usedprogram)
                        cvpj_inst["color"] = [0.2,0.2,0.2]
                        cvpj_inst["instdata"] = {}
                        cvpj_inst["instdata"]['plugin'] = 'none'
                    else:
                        cvpj_inst["name"] = 'Bank #'+str(c_usedbank+1)+', Inst #'+str(c_usedprogram+1)
                        cvpj_inst["color"] = [0.6, 0.6, 0.6]
                        cvpj_inst["instdata"] = {}
                        cvpj_inst["instdata"]['plugin'] = 'none'
                    cvpj_inst["pan"] = 0.0
                    cvpj_inst["vol"] = 1.0
                    cvpj_inst['fxrack_channel'] = channel+1

                    cvpj_l_instruments[instid] = cvpj_inst
                    cvpj_l_instrumentsorder.append(instid)

            playlistrowdata = {}
            playlistrowdata['name'] = 'Channel '+str(channel+1)
            playlistrowdata["color"] = [0.69, 0.63, 0.54]
            if len(c_notelist) != 0:
                playlistrowdata['placements'] = [{}]
                playlistrowdata['placements'][0]['type'] = 'instruments'
                playlistrowdata['placements'][0]['position'] = 0
                playlistrowdata['placements'][0]['notelist'] = c_notelist
            cvpj_l_playlist[str(channel+1)] = playlistrowdata

            cvpj_l_fxrack[str(channel+1)] = {}
            fxdata = cvpj_l_fxrack[str(channel+1)]
            fxdata["fxenabled"] = 1
            fxdata['color'] = [0.69, 0.63, 0.54]
            fxdata['vol'] = t_chanvol[channel]
            fxdata["name"] = "Channel "+str(channel+1)

        cvpj_l = {}
        cvpj_l['use_fxrack'] = True
        cvpj_l['fxrack'] = cvpj_l_fxrack
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = 120
        return json.dumps(cvpj_l)