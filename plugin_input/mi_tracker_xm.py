# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import math
import json
import struct
import numpy as np
from functions import song_tracker
from functions import audio_wav
from functions import folder_samples
from functions import data_bytes
from functions import tracks

try: import xmodits
except: xmodits_exists = False
else: xmodits_exists = True

startinststr = 'XM_Inst_'

def parse_xm_cell(databytes, firstrow):
    global current_speed
    globaljson = {}

    if firstrow == 1: globaljson['firstrow'] = 1

    cell_note = None
    cell_instrument = None
    cell_vol = None
    cell_effect = None
    cell_param = 0

    packed_first = int.from_bytes(databytes.read(1), "little")
    packed_flags = bin(packed_first)[2:].zfill(8)

    packed_note = int(packed_flags[7], 2) 
    packed_instrument = int(packed_flags[6], 2)
    packed_vol = int(packed_flags[5], 2)
    packed_effect = int(packed_flags[4], 2)
    packed_param = int(packed_flags[3], 2)
    packed_msb = int(packed_flags[0], 2)
    if packed_msb == 1:
        if packed_note == 1: cell_note = int.from_bytes(databytes.read(1), "little")
        if packed_instrument == 1: cell_instrument = int.from_bytes(databytes.read(1), "little")
        if packed_vol == 1: cell_vol = int.from_bytes(databytes.read(1), "little")
        if packed_effect == 1: cell_effect = int.from_bytes(databytes.read(1), "little")
        if packed_param == 1: cell_param = int.from_bytes(databytes.read(1), "little")
    else:
        cell_note = packed_first
        cell_instrument = int.from_bytes(databytes.read(1), "little")
        cell_vol = int.from_bytes(databytes.read(1), "little")
        cell_effect = int.from_bytes(databytes.read(1), "little")
        cell_param = int.from_bytes(databytes.read(1), "little")

    output_note = cell_note
    if cell_note != None:
        if cell_note == 97: output_note = 'Off'
        else: output_note = cell_note - 49
    output_inst = cell_instrument
    output_param = {}
    output_extra = {}

    if current_speed == 0: current_speed = 3

    if cell_effect == 0:
        arpeggio_first = cell_param >> 4
        arpeggio_second = cell_param & 0x0F
        output_param['arp'] = [arpeggio_first, arpeggio_second]

    if cell_effect == 1: 
        output_param['slide_up'] = song_tracker.calcbendpower_up(cell_param, current_speed)

    if cell_effect == 2: 
        output_param['slide_down'] = song_tracker.calcbendpower_down(cell_param, current_speed)

    if cell_effect == 3: 
        output_param['slide_to_note'] = song_tracker.calcslidepower(cell_param, current_speed)

    if cell_effect == 4: 
        vibrato_params = {}
        vibrato_params['speed'], vibrato_params['depth'] = data_bytes.splitbyte(cell_param)
        output_param['vibrato'] = vibrato_params

    if cell_effect == 5:
        pos, neg = data_bytes.splitbyte(cell_param)
        output_param['vol_slide'] = (neg*-1) + pos
        output_param['slide_to_note'] = (neg*-1) + pos

    if cell_effect == 6:
        pos, neg = data_bytes.splitbyte(cell_param)
        output_param['vibrato'] = {'speed': 0, 'depth': 0}
        output_param['vol_slide'] = (neg*-1) + pos

    if cell_effect == 7:
        tremolo_params = {}
        tremolo_params['speed'], tremolo_params['depth'] = data_bytes.splitbyte(cell_param)
        output_param['tremolo'] = tremolo_params

    if cell_effect == 8: 
        output_param['pan'] = (cell_param-128)/128

    if cell_effect == 9: 
        output_param['sample_offset'] = cell_param*256

    if cell_effect == 10:
        pos, neg = data_bytes.splitbyte(cell_param)
        output_param['vol_slide'] = (neg*-1) + pos

    if cell_effect == 11: 
        output_extra['pattern_jump'] = cell_param

    if cell_effect == 12: 
        output_param['vol'] = cell_param/64

    if cell_effect == 13: 
        output_extra['break_to_row'] = cell_param

    if cell_effect == 14: 
        ext_type, ext_value = data_bytes.splitbyte(cell_param)
        if ext_type == 0: output_param['filter_amiga_led'] = ext_value
        if ext_type == 1: output_param['fine_slide_up'] = ext_value
        if ext_type == 2: output_param['fine_slide_down'] = ext_value
        if ext_type == 3: output_param['glissando_control'] = ext_value
        if ext_type == 4: output_param['vibrato_waveform'] = ext_value
        if ext_type == 5: output_param['set_finetune'] = ext_value
        if ext_type == 6: output_param['pattern_loop'] = ext_value
        if ext_type == 7: output_param['tremolo_waveform'] = ext_value
        if ext_type == 8: output_param['set_pan'] = ext_value
        if ext_type == 9: output_param['retrigger_note'] = ext_value
        if ext_type == 10: output_param['fine_vol_slide_up'] = ext_value
        if ext_type == 11: output_param['fine_vol_slide_down'] = ext_value
        if ext_type == 12: output_param['note_cut'] = ext_value
        if ext_type == 13: output_param['note_delay'] = ext_value
        if ext_type == 14: output_param['pattern_delay'] = ext_value
        if ext_type == 15: output_param['invert_loop'] = ext_value

    if cell_effect == 15:
        output_extra['speed'] = cell_param
        globaljson['speed'] = cell_param
        current_speed = cell_param

    if cell_effect == 16: 
        output_extra['global_volume'] = cell_param/64

    if cell_effect == 17: 
        output_extra['global_volume_slide'] = song_tracker.getfineval(cell_param)

    if cell_effect == 34: 
        panbrello_params = {}
        panbrello_params['speed'], panbrello_params['depth'] = data_bytes.splitbyte(cell_param)
        output_param['panbrello'] = panbrello_params

    if cell_vol != None:
        if 80 >= cell_vol >= 16: output_param['vol'] = (cell_vol-16)/64

    return globaljson, [output_note, output_inst, output_param, output_extra]

def parse_xm_row(xmdata, numchannels, firstrow):
    table_row = []
    globaljson = {}
    for channel in range(numchannels):
        if firstrow == 1: globaljson, celldata = parse_xm_cell(xmdata, 1)
        else: t_globaljson, celldata = parse_xm_cell(xmdata, 0)
        globaljson = globaljson | t_globaljson
        table_row.append(celldata)
    return [globaljson, table_row]

def parse_xm_row_none(numchannels, firstrow):
    table_row = []
    globaljson = {}
    for channel in range(numchannels):
        if firstrow == 1: globaljson['firstrow'] = 1
        celldata = [None, None, {}, {}]
        table_row.append(celldata)
    return [globaljson, table_row]

def parse_pattern(file_stream, num_channels): 
    basepos = file_stream.tell()
    xm_pat_header_length = int.from_bytes(file_stream.read(4), "little")
    print("Len: " + str(xm_pat_header_length), end=' | ')
    xm_pat_pak_type = file_stream.read(1)[0]
    print("PakType: " + str(xm_pat_pak_type), end=' | ')
    xm_pat_num_rows = int.from_bytes(file_stream.read(2), "little")
    print("#rows: " + str(xm_pat_num_rows), end=' | ')
    xm_pat_patterndata_size = int.from_bytes(file_stream.read(2), "little")
    print("DataSize: " + str(xm_pat_patterndata_size))

    patterntable_single = []

    basepos_end = file_stream.tell()
    xm_pat_extra_data = file_stream.read(xm_pat_header_length - (basepos_end-basepos))
    xm_pat_data = file_stream.read(xm_pat_patterndata_size)

    bio_patdata = data_bytes.bytearray2BytesIO(xm_pat_data)

    for rownum in range(xm_pat_num_rows):
        if xm_pat_patterndata_size != 0: rowsdata = parse_xm_row(bio_patdata, num_channels, 0)
        else: rowsdata = parse_xm_row_none(num_channels, 0)
        if rownum == 0: rowsdata[0]['firstrow'] = 1

        patterntable_single.append(rowsdata)
        #print(rownum, rowsdata)

    return patterntable_single

def parse_instrument(file_stream, samplecount):
    global cvpj_l_instruments
    global cvpj_l_instrumentsorder 
    global xm_cursamplenum

    basepos = file_stream.tell()
    xm_inst_header_length = int.from_bytes(file_stream.read(4), "little")
    print("[input-xm]     Header Length: " + str(xm_inst_header_length))

    xm_inst_name = file_stream.read(22).decode('latin_1').rstrip('\x00')
    print("[input-xm]     Name: " + str(xm_inst_name))
    xm_inst_type = file_stream.read(1)[0]
    print("[input-xm]     Type: " + str(xm_inst_type))
    xm_inst_num_samples = file_stream.read(1)[0]
    print("[input-xm]     # of samples: " + str(xm_inst_num_samples))

    if xm_inst_num_samples != 0:
        xm_inst_e_head_size = int.from_bytes(file_stream.read(4), "little")
        print("[input-xm]     Sample header size: " + str(xm_inst_e_head_size))
        xm_inst_e_table = struct.unpack('B'*96, file_stream.read(96))
        xm_inst_e_env_v = struct.unpack('B'*48, file_stream.read(48))
        xm_inst_e_env_p = struct.unpack('B'*48, file_stream.read(48))
        xm_inst_e_number_of_volume_points = file_stream.read(1)[0]
        xm_inst_e_number_of_panning_points = file_stream.read(1)[0]
        xm_inst_e_volume_sustain_point = file_stream.read(1)[0]
        xm_inst_e_volume_loop_start_point = file_stream.read(1)[0]
        xm_inst_e_volume_loop_end_point = file_stream.read(1)[0]
        xm_inst_e_panning_sustain_point = file_stream.read(1)[0]
        xm_inst_e_panning_loop_start_point = file_stream.read(1)[0]
        xm_inst_e_panning_loop_end_point = file_stream.read(1)[0]
        xm_inst_e_volume_type = file_stream.read(1)[0]
        xm_inst_e_panning_type = file_stream.read(1)[0]
        xm_inst_e_vibrato_type = file_stream.read(1)[0]
        xm_inst_e_vibrato_sweep = file_stream.read(1)[0]
        xm_inst_e_vibrato_depth = file_stream.read(1)[0]
        xm_inst_e_vibrato_rate = file_stream.read(1)[0]
        xm_inst_e_vibrato_rate = file_stream.read(1)[0]
        xm_inst_e_volume_fadeout = int.from_bytes(file_stream.read(2), "little")
        xm_inst_e_reserved = int.from_bytes(file_stream.read(2), "little")

    t_sampleheaders = []
    basepos_end = file_stream.tell()

    xm_pat_extra_data = file_stream.read(xm_inst_header_length - (basepos_end-basepos))

    for _ in range(xm_inst_num_samples):
        sampheader = struct.unpack('IIIBBBBBB', file_stream.read(18))
        sampname = file_stream.read(22).split(b'\x00' * 1)[0].decode("latin_1")
        t_sampleheaders.append([sampheader, sampname])

    for t_sampleheader in t_sampleheaders:
        file_stream.read(t_sampleheader[0][0])

    it_samplename = startinststr + str(samplecount+1)
    cvpj_l_instruments[it_samplename] = {}
    cvpj_l_single_inst = cvpj_l_instruments[it_samplename]
    cvpj_l_single_inst['color'] = [0.16, 0.33, 0.53]
    cvpj_l_single_inst['name'] = xm_inst_name
    cvpj_l_single_inst['vol'] = 0.3
    cvpj_l_single_inst['instdata'] = {}
    if xm_inst_num_samples == 1:
        cvpj_l_single_inst['vol'] = 0.3*(t_sampleheaders[0][0][3]/64)
        cvpj_l_single_inst['instdata']['plugin'] = 'sampler'
        cvpj_l_single_inst['instdata']['plugindata'] = {'file': samplefolder + str(xm_cursamplenum) + '.wav'}
        cvpj_l_single_inst['instdata']['plugindata']['point_value_type'] = "samples"
        cvpj_l_single_inst['instdata']['plugindata']['length'] = t_sampleheaders[0][0][0]
        if t_sampleheaders[0][0][1:3] == (0, 0):
            cvpj_l_single_inst['instdata']['plugindata']['loop'] = {"enabled": 0}
        else:
            xm_loop_start = t_sampleheaders[0][0][1]
            xm_loop_len = t_sampleheaders[0][0][2]
            cvpj_l_single_inst['instdata']['plugindata']['loop'] = {"enabled": 1, "mode": "normal", "points": [xm_loop_start,xm_loop_start+xm_loop_len]}
    else:
        cvpj_l_single_inst['vol'] = 0.3
        cvpj_l_single_inst['instdata']['plugin'] = 'none'
        cvpj_l_single_inst['instdata']['plugindata'] = {}
    cvpj_l_instrumentsorder.append(it_samplename)
    if xm_inst_num_samples != 0: xm_cursamplenum += xm_inst_num_samples

class input_xm(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'xm'
    def getname(self): return 'FastTracker 2'
    def gettype(self): return 'm'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': True,
        'placement_cut': False,
        'placement_warp': False,
        'no_pl_auto': False,
        'no_placements': False
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytesdata = bytestream.read(17)
        if bytesdata == b'Extended Module: ': return True
        else: return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        global cvpj_l_instruments
        global cvpj_l_instrumentsorder
        global samplefolder
        global current_speed
        global xm_cursamplenum

        xm_cursamplenum = 1

        file_name = os.path.splitext(os.path.basename(input_file))[0]
        samplefolder = folder_samples.samplefolder(extra_param, file_name)

        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_playlist = []

        file_stream = open(input_file, 'rb')

        xm_header = file_stream.read(17)
        xm_name = file_stream.read(20).split(b'\x00' * 1)[0].decode("windows-1252")
        print("[input-xm] Song Name: " + xm_name)
        xm_1a = file_stream.read(1)
        xm_trkr_name = file_stream.read(20).split(b'\x00' * 1)[0].decode("windows-1252")
        print("[input-xm] Tracker Name: " + xm_trkr_name)
        xm_version = file_stream.read(2)
        print("[input-xm] Version: " + str(xm_version[1]), str(xm_version[0]))

        xm_headersize = int.from_bytes(file_stream.read(4), "little")
        xm_headersize_pos = file_stream.tell()

        xm_song_length = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Song Length: " + str(xm_song_length))
        xm_song_restart_pos = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Song Restart Position: " + str(xm_song_restart_pos))
        xm_song_num_channels = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Number of channels: " + str(xm_song_num_channels))
        xm_song_num_patterns = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Number of patterns: " + str(xm_song_num_patterns))
        xm_song_num_instruments = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Number of instruments: " + str(xm_song_num_instruments))
        xm_song_flags = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Flags: " + str(xm_song_flags))
        xm_song_speed = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Speed: " + str(xm_song_speed))
        xm_song_bpm = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] BPM: " + str(xm_song_bpm))

        current_speed = xm_song_speed

        # ------------- Orders -------------
        xm_order = file_stream.read(xm_song_length)
        t_orderlist = []
        for xm_orderentry in xm_order: t_orderlist.append(xm_orderentry)
        print("[input-xm] Order List: " + str(t_orderlist))

        # ------------- Pattern -------------
        findpat = file_stream.tell()
        calc_pos = xm_headersize+xm_headersize_pos-4

        #print(findpat, xm_headersize, xm_headersize_pos, calc_pos, hex(calc_pos))

        extra_data = file_stream.read(calc_pos-findpat)
        patterntable_all = []
        for patnum in range(xm_song_num_patterns):
            print("[input-xm] Pattern "+str(patnum+1), end=': ')
            patterntable_single = parse_pattern(file_stream, xm_song_num_channels)
            patterntable_all.append(patterntable_single)

        # ------------- Instruments -------------
        for instnum in range(xm_song_num_instruments):
            print("[input-xm] Instrument:")
            parse_instrument(file_stream, instnum)

        # ------------- Samples -------------
        if xmodits_exists == True:
            try: xmodits.dump(input_file, samplefolder, index_only=True, index_raw=True, index_padding=0)
            except: pass

        cvpj_l = {}
        
        cvpj_l_playlist = song_tracker.song2playlist(patterntable_all, xm_song_num_channels, t_orderlist, startinststr, [0.16, 0.33, 0.53])

        tracks.a_add_auto_pl(cvpj_l, 'main', None, 'bpm', song_tracker.tempo_auto(patterntable_all, t_orderlist, 6, xm_song_bpm))

        cvpj_l['info'] = {}
        cvpj_l['info']['title'] = xm_name
        
        cvpj_l['do_addwrap'] = True
        cvpj_l['do_lanefit'] = True

        cvpj_l['use_fxrack'] = False
        cvpj_l['use_instrack'] = False
        
        cvpj_l['instruments_data'] = cvpj_l_instruments
        cvpj_l['instruments_order'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = xm_song_bpm
        return json.dumps(cvpj_l)

