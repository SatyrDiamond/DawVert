# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import json
import struct
from functions import song_tracker
from functions import song_tracker_fx_mod
from functions import data_values
from functions import data_bytes
from functions import plugins
from functions import song
from functions_tracks import tracks_mi
from functions_tracks import auto_data

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

    current_speed = song_tracker_fx_mod.do_fx(current_speed, output_extra, output_param, cell_effect, cell_param)

    if cell_effect == 12: 
        output_param['vol'] = cell_param/64

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

    bio_patdata = data_bytes.to_bytesio(xm_pat_data)

    for rownum in range(xm_pat_num_rows):
        if xm_pat_patterndata_size != 0: rowsdata = parse_xm_row(bio_patdata, num_channels, 0)
        else: rowsdata = parse_xm_row_none(num_channels, 0)
        if rownum == 0: rowsdata[0]['firstrow'] = 1

        patterntable_single.append(rowsdata)
        #print(rownum, rowsdata)

    return patterntable_single

def parse_instrument(file_stream, samplecount):
    global cvpj_l
    global cvpj_l_instruments
    global cvpj_l_instrumentsorder 
    global xm_cursamplenum

    basepos = file_stream.tell()
    xm_inst_header_length = int.from_bytes(file_stream.read(4), "little")
    print("[input-xm]     Header Length: " + str(xm_inst_header_length))

    xm_inst_name = data_bytes.readstring_fixedlen(file_stream, 22, "latin1")
    print("[input-xm]     Name: " + str(xm_inst_name))
    xm_inst_type = file_stream.read(1)[0]
    print("[input-xm]     Type: " + str(xm_inst_type))
    xm_inst_num_samples = file_stream.read(1)[0]
    print("[input-xm]     # of samples: " + str(xm_inst_num_samples))

    if xm_inst_num_samples != 0:
        xm_inst_e_head_size = int.from_bytes(file_stream.read(4), "little")
        print("[input-xm]     Sample header size: " + str(xm_inst_e_head_size))
        xm_inst_e_table = struct.unpack('B'*96, file_stream.read(96))
        xm_inst_e_env_v = struct.unpack('>'+'H'*24, file_stream.read(48))
        xm_inst_e_env_p = struct.unpack('>'+'H'*24, file_stream.read(48))
        file_stream.read(1)
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
        xm_inst_e_volume_fadeout = int.from_bytes(file_stream.read(2), "little")
        xm_inst_e_reserved = int.from_bytes(file_stream.read(2), "little")

    t_sampleheaders = []
    basepos_end = file_stream.tell()

    xm_pat_extra_data = file_stream.read(xm_inst_header_length - (basepos_end-basepos))

    for _ in range(xm_inst_num_samples):
        sampheader = struct.unpack('IIIBBBBBB', file_stream.read(18))
        sampname = data_bytes.readstring_fixedlen(file_stream, 22, "windows-1252")
        t_sampleheaders.append([sampheader, sampname])

    for t_sampleheader in t_sampleheaders:
        file_stream.read(t_sampleheader[0][0])

    pluginid = plugins.get_id()
    cvpj_instid = startinststr + str(samplecount+1)

    tracks_mi.inst_create(cvpj_l, cvpj_instid)
    tracks_mi.inst_visual(cvpj_l, cvpj_instid, name=xm_inst_name, color=[0.16, 0.33, 0.53])
    tracks_mi.inst_pluginid(cvpj_l, cvpj_instid, pluginid)

    if xm_inst_num_samples == 0:
        pass
    elif xm_inst_num_samples == 1:
        tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'vol', 0.3*(t_sampleheaders[0][0][3]/64), 'float')
        plugins.add_plug_sampler_singlefile(cvpj_l, pluginid, samplefolder+str(xm_cursamplenum)+'.wav')
        plugins.add_plug_data(cvpj_l, pluginid, 'trigger', 'normal')
        plugins.add_plug_data(cvpj_l, pluginid, 'point_value_type', "samples")
        plugins.add_plug_data(cvpj_l, pluginid, 'length', t_sampleheaders[0][0][0])

        sampleflags = data_bytes.to_bin(t_sampleheaders[0][0][5], 8)

        loopon = None
        xm_loop_start = t_sampleheaders[0][0][1]
        xm_loop_len = t_sampleheaders[0][0][2]

        if sampleflags[7] == 1: loopon = 'normal'
        if sampleflags[6] == 1: loopon = 'pingpong'

        if loopon == None:
            plugins.add_plug_data(cvpj_l, pluginid, 'loop', {"enabled": 0})
        else:
            plugins.add_plug_data(cvpj_l, pluginid, 'loop', 
                {"enabled": 1, "mode": loopon, "points": [xm_loop_start,xm_loop_start+xm_loop_len]})
    else:
        tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'vol', 0.3, 'float')
        sampleregions = data_values.list_to_reigons(xm_inst_e_table, 48)
        plugins.add_plug_multisampler(cvpj_l, pluginid)
        plugins.add_plug_data(cvpj_l, pluginid, 'point_value_type', "samples")

        for sampleregion in sampleregions:
            instrumentnum = sampleregion[0]
            regionparams = {}
            regionparams['r_key'] = [sampleregion[1], sampleregion[2]]
            regionparams['middlenote'] = 0
            regionparams['file'] = samplefolder + str(xm_cursamplenum+instrumentnum) + '.wav'
            regionparams['start'] = 0
            regionparams['end'] = t_sampleheaders[instrumentnum][0][0]
            regionparams['name'] = t_sampleheaders[instrumentnum][1]
            regionparams['trigger'] = 'oneshot'
            regionparams['loop'] = {}
            if t_sampleheaders[instrumentnum][0][1:3] == (0, 0): 
                regionparams['loop']['enabled'] = 0
            else:
                regionparams['loop']['enabled'] = 1
                xm_loop_start = t_sampleheaders[instrumentnum][0][1]
                xm_loop_len = t_sampleheaders[instrumentnum][0][2]
                regionparams['loop']['points'] = [xm_loop_start,xm_loop_start+xm_loop_len]

            plugins.add_plug_multisampler_region(cvpj_l, pluginid, regionparams)

    if xm_inst_num_samples != 0:

        splitted_points_v = data_values.list_chunks(xm_inst_e_env_v[0:xm_inst_e_number_of_volume_points*2], 2)
        splitted_points_p = data_values.list_chunks(xm_inst_e_env_p[0:xm_inst_e_number_of_panning_points*2], 2)

        pointsdata = [
        ['vol', splitted_points_v, xm_inst_e_volume_sustain_point, xm_inst_e_volume_loop_start_point, xm_inst_e_volume_loop_end_point], 
        ['pan', splitted_points_p, xm_inst_e_panning_sustain_point, xm_inst_e_panning_loop_start_point, xm_inst_e_panning_loop_end_point]
        ]

        envflags = data_bytes.to_bin(xm_inst_e_volume_type, 8)

        for typedata in pointsdata:
            zerofound = False

            if envflags[6] == 1:
                plugins.add_env_point_var(cvpj_l, pluginid, typedata[0], 'sustain', typedata[2]+1)
            if envflags[5] == 1: 
                plugins.add_env_point_var(cvpj_l, pluginid, typedata[0], 'loop', [typedata[4], typedata[3]+typedata[4]])

            if typedata[0] == 'vol':
                if xm_inst_e_volume_fadeout != 0:
                    plugins.add_env_point_var(cvpj_l, pluginid, typedata[0], 'fadeout', (128/xm_inst_e_volume_fadeout)*5)

            for groupval in typedata[1]:
                if groupval[0] == 0:
                    if zerofound == True: break
                    zerofound = True
                if typedata[0] == 'vol' and envflags[7] == 1:
                    plugins.add_env_point(cvpj_l, pluginid, 'vol', groupval[0]/48, groupval[1]/64)
                if typedata[0] == 'pan':
                    plugins.add_env_point(cvpj_l, pluginid, 'pan', groupval[0]/48, (groupval[1]-32)/32)

        plugins.env_point_to_asdr(cvpj_l, pluginid, 'vol')

    if xm_inst_num_samples != 0: xm_cursamplenum += xm_inst_num_samples

class input_xm(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'xm'
    def getname(self): return 'FastTracker 2'
    def gettype(self): return 'm'
    def getdawcapabilities(self): 
        return {
        'samples_inside': True,
        'track_lanes': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytesdata = bytestream.read(17)
        if bytesdata == b'Extended Module: ': return True
        else: return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        global cvpj_l
        global samplefolder
        global current_speed
        global xm_cursamplenum

        cvpj_l = {}
        
        xm_cursamplenum = 1

        samplefolder = extra_param['samplefolder']
        
        cvpj_l_playlist = []

        file_stream = open(input_file, 'rb')

        xm_header = file_stream.read(17)

        xm_name = data_bytes.readstring_fixedlen(file_stream, 20, "windows-1252")
        print("[input-xm] Song Name: " + xm_name)
        xm_1a = file_stream.read(1)
        xm_trkr_name = data_bytes.readstring_fixedlen(file_stream, 20, "windows-1252")
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

        cvpj_l_playlist = song_tracker.song2playlist(patterntable_all, xm_song_num_channels, t_orderlist, startinststr, [0.16, 0.33, 0.53])

        auto_data.add_pl(cvpj_l, 'float', ['main', 'bpm'], song_tracker.tempo_auto(patterntable_all, t_orderlist, 6, xm_song_bpm))

        song.add_info(cvpj_l, 'title', xm_name)
        
        cvpj_l['do_addloop'] = True
        cvpj_l['do_lanefit'] = True

        cvpj_l['use_fxrack'] = False
        cvpj_l['use_instrack'] = False
        
        cvpj_l['playlist'] = cvpj_l_playlist
        song.add_param(cvpj_l, 'bpm', xm_song_bpm)
        return json.dumps(cvpj_l)

