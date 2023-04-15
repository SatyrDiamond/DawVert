# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import struct
import math
from functions import data_bytes
from functions import note_mod
from functions import format_midi_in

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

def parse_ma3_Mtsq(Mtsqdata, tb_ms):
    bio_mmf_Mtsq = data_bytes.to_bytesio(Mtsqdata)
    bio_mmf_Mtsq_size = len(Mtsqdata)
    notecount = 0
    #print('size', bio_mmf_Mtsq_size)
    #print('      1ST 2ND | CH#  CMD')

    format_midi_in.song_start(16, int(tb_ms*(math.pi*10000)))
    format_midi_in.track_start(16, 0)

    basepos = 0

    beforenote = True
    position = 0
    while bio_mmf_Mtsq.tell() < bio_mmf_Mtsq_size:
        resttime = calc_gatetime(bio_mmf_Mtsq)
        basepos += resttime
        format_midi_in.resttime(resttime)

        #print(str(basepos).ljust(5), end=' ')

        firstbyte = data_bytes.splitbyte(int.from_bytes(bio_mmf_Mtsq.read(1), "big"))
        #print(str(firstbyte[0]).ljust(3), end=' ')

        if firstbyte[0] == 0:
            null_durgate = calc_gatetime(bio_mmf_Mtsq)
            #print('|      NULL    ', null_durgate)

        elif firstbyte[0] == 8:
            note_note = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            note_durgate = calc_gatetime(bio_mmf_Mtsq)
            #print('| '+str(firstbyte[1]).ljust(4), 'NOTE    ', str(note_note).ljust(4), '     dur ', note_durgate)
            format_midi_in.note(note_note, note_durgate, firstbyte[1], 127)

        elif firstbyte[0] == 9:
            note_note = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            note_vol = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            note_durgate = calc_gatetime(bio_mmf_Mtsq)
            #print('| '+str(firstbyte[1]).ljust(4), 'NOTE+V  ', str(note_note).ljust(4), str(note_vol).ljust(4), 'dur ', note_durgate)
            format_midi_in.note(note_note, note_durgate, firstbyte[1], note_vol)

        elif firstbyte[0] == 11:
            cntltype = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            cntldata = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            #print('| '+str(firstbyte[1]).ljust(4), 'CONTROL ', str(cntltype).ljust(4), str(cntldata).ljust(4))
            format_midi_in.control_change(firstbyte[1], cntltype, cntldata)

        elif firstbyte[0] == 12:
            prognumber = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
            #print('| '+str(firstbyte[1]).ljust(4), 'PROGRAM ', prognumber)
            format_midi_in.program_change(firstbyte[1], prognumber)

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

    format_midi_in.track_end(16)

    usedinsts = format_midi_in.getusedinsts(16)

    for usedinst in usedinsts:
        if usedinst[1] == 124: 
            cvpj_trackdata = {}
            cvpj_trackdata["instdata"] = {}
            cvpj_trackdata["instdata"]['plugin'] = 'none'
            cvpj_trackdata["color"] = [0.3,0.3,0.3]
            cvpj_trackdata["name"] = 'MA-3 User #' + str(usedinst[2])
            format_midi_in.make_custominst(usedinst[0], usedinst[1], usedinst[2], cvpj_trackdata)
        elif usedinst[1] == 125: 
            cvpj_trackdata = {}
            cvpj_trackdata["instdata"] = {}
            cvpj_trackdata["instdata"]['plugin'] = 'none'
            cvpj_trackdata["color"] = [0.2,0.2,0.2]
            cvpj_trackdata["name"] = 'MA-3 PCM #' + str(usedinst[2])
            format_midi_in.make_custominst(usedinst[0], usedinst[1], usedinst[2], cvpj_trackdata)
        else: 
            format_midi_in.make_inst(usedinst[0], usedinst[1], usedinst[2])

    cvpj_l = format_midi_in.song_end(16)

    return cvpj_l

def parse_ma3_track(datain, tracknum):
    bio_mmf_track = data_bytes.to_bytesio(datain)
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
    def getdawcapabilities(self): 
        return {
        'fxrack': True,
        'r_track_lanes': True,
        'placement_cut': False,
        'placement_warp': False,
        'no_pl_auto': True,
        'no_placements': True
        }
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

        mmf_chunks_ins = data_bytes.riff_read(mmf_chunks_main[0][1], 0)

        cvpj_l = {}

        trackparsed = False
        for mmf_chunk in mmf_chunks_ins:
            if mmf_chunk[0] == b'CNTI':
                bio_mmf_cnti = data_bytes.to_bytesio(mmf_chunk[1])
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
                            cvpj_l = parse_ma3_track(mmf_cnti_chunk[1], 3)

        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = True
        
        cvpj_l['bpm'] = 120
        return json.dumps(cvpj_l)