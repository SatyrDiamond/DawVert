# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import math
import json
import struct
import numpy as np
from functions import plugins
from functions import data_bytes
from functions import song_tracker
from functions import song_tracker_fx_mod
from functions import audio_wav
from functions import song
from functions_tracks import tracks_mi
from functions_tracks import auto_data

modfinetune = [8363, 8413, 8463, 8529, 8581, 8651, 8723, 8757, 7895, 7941, 7985, 8046, 8107, 8169, 8232, 8280]

def parse_mod_cell(file_stream, firstrow):
    global current_speed
    global table_samples
    output_note = None
    output_inst = None
    vibrato_depth = 0
    output_param = {}
    output_extra = {}
    if firstrow == 1: output_extra['firstrow'] = 1
    cell_p1 = int.from_bytes(file_stream.read(2), "big")
    cell_p2 = int.from_bytes(file_stream.read(2), "big")
    mod_inst_low = cell_p2 >> 12
    mod_inst_high = cell_p1 >> 12
    noteperiod = (cell_p1 & 0x0FFF) 
    if noteperiod != 0: output_note = (round(12 * math.log2((447902/(noteperiod*2)) / 440)) + 69)-72
    cell_fx_type = (cell_p2 & 0xF00) >> 8
    cell_fx_param = (cell_p2 & 0xFF) 
    cell_inst_num = mod_inst_high << 4 | mod_inst_low
    if cell_inst_num != 0: output_inst = cell_inst_num

    current_speed = song_tracker_fx_mod.do_fx(current_speed, output_extra, output_param, cell_fx_type, cell_fx_param)

    if cell_fx_type == 12: 
        output_param['vol'] = cell_fx_param/64
    else: 
        if output_inst != None:
            if output_inst < 32:
                output_param['vol'] = table_samples[output_inst-1][3]/64

    if cell_fx_type == 15:
        if cell_fx_param < 32: 
            output_extra['speed'] = cell_fx_param
            current_speed = cell_fx_param
        else: output_extra['tempo'] = cell_fx_param


    return [output_note, output_inst, output_param, output_extra]

def parse_mod_row(file_stream, firstrow):
    global table_singlepattern
    global mod_num_channels
    table_row = []
    globaljson = {}
    for channel in range(mod_num_channels):
        celldata = parse_mod_cell(file_stream, firstrow)
        rowdata_global = celldata[3]
        globaljson = rowdata_global | globaljson
        table_row.append(celldata)
    return [globaljson, table_row]

def parse_pattern(file_stream):
    global table_singlepattern
    table_singlepattern = []
    firstrow = 1
    for row in range(64):
        table_singlepattern.append(parse_mod_row(file_stream, firstrow))
        firstrow = 0

def parse_song(file_stream):
    print("[input-mod] Decoding Pattern:",end=' ')
    table_patterns = []
    for pattern in range(mod_num_patterns+1):
        print(str(pattern),end=' ')
        parse_pattern(file_stream)
        table_patterns.append(table_singlepattern)
    print(' ')
    return table_patterns

text_inst_start = 'MOD_Inst_'

class input_mod(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mod'
    def getname(self): return 'Protracker Module'
    def gettype(self): return 'm'
    def getdawcapabilities(self): 
        return {
        'samples_inside': True,
        'track_lanes': True
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global mod_num_patterns
        global mod_num_channels
        global table_samples
        global current_speed

        cvpj_l = {}
        
        samplefolder = extra_param['samplefolder']

        file_stream = open(input_file, 'rb')
        mod_name = data_bytes.readstring_fixedlen(file_stream, 20, "ascii")
        print("[input-mod] Song Name: " + str(mod_name))
        table_samples = []
        cvpj_bpm = 125
        current_speed = 6
        for mod_numinst in range(31):
            mod_numinst += 1
            mod_inst_mod_name = data_bytes.readstring_fixedlen(file_stream, 22, "ascii")
            mod_inst_length, mod_inst_finetune, mod_inst_defaultvol, mod_inst_loopstart, mod_inst_looplength = struct.unpack('>HBBHH', file_stream.read(8))
            print('[input-mod] Instrument ' + str(mod_numinst) + ': ' + mod_inst_mod_name)
            table_samples.append([mod_inst_mod_name, mod_inst_length, mod_inst_finetune, mod_inst_defaultvol, mod_inst_loopstart*2, mod_inst_looplength*2])

            cvpj_instid = text_inst_start + str(mod_numinst)

            pluginid = 'sampler_'+str(mod_numinst)
            if mod_inst_mod_name != "": cvpj_instname = mod_inst_mod_name
            else: cvpj_instname = ' '

            tracks_mi.inst_create(cvpj_l, cvpj_instid)
            tracks_mi.inst_visual(cvpj_l, cvpj_instid, name=cvpj_instname, color=[0.71, 0.58, 0.47])
            tracks_mi.inst_pluginid(cvpj_l, cvpj_instid, pluginid)

            tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'vol', 0.3, 'float')
            
            if mod_inst_length != 0 and mod_inst_length != 1:
                wave_path = samplefolder + str(mod_numinst).zfill(2) + '.wav'

                inst_plugindata = plugins.cvpj_plugin('sampler', wave_path, None)
                inst_plugindata.dataval_add('point_value_type', 'samples')
                inst_plugindata.dataval_add('trigger', 'normal')
                inst_plugindata.dataval_add('start', 0)
                inst_plugindata.dataval_add('end', mod_inst_length)
                inst_plugindata.dataval_add('length', mod_inst_length)

                cvpj_loopdata = {}
                if mod_inst_loopstart != 0 and mod_inst_looplength != 1:
                    cvpj_loopdata['enabled'] = 1
                    cvpj_loopdata['mode'] = "normal"
                    cvpj_loopdata['points'] = [mod_inst_loopstart, mod_inst_loopstart+mod_inst_looplength]
                else: cvpj_loopdata['enabled'] = 0

                inst_plugindata.dataval_add('loop', cvpj_loopdata)
                inst_plugindata.to_cvpj(cvpj_l, pluginid)

        mod_orderlist_length = file_stream.read(1)[0]
        mod_extravalue = file_stream.read(1)[0]
        t_orderlist = []
        for number in range(128):
            ordernum = file_stream.read(1)[0]
            if number < mod_orderlist_length: t_orderlist.append(ordernum)
        print("[input-mod] Order List: " + str(t_orderlist))
        mod_inst_tag = file_stream.read(4).decode()
        mod_num_patterns = max(t_orderlist)
        print("[input-mod] Patterns: " + str(mod_num_patterns))
        mod_num_channels = 4

        if mod_inst_tag == '1CHN': mod_num_channels = 1
        if mod_inst_tag == '6CHN': mod_num_channels = 6
        if mod_inst_tag == '8CHN': mod_num_channels = 8
        if mod_inst_tag == 'CD81': mod_num_channels = 8
        if mod_inst_tag == 'OKTA': mod_num_channels = 8
        if mod_inst_tag == 'OCTA': mod_num_channels = 8
        if mod_inst_tag == '6CHN': mod_num_channels = 6
        if mod_inst_tag[-2:] == 'CH': mod_num_channels = int(mod_inst_tag[:2])
        if mod_inst_tag == '2CHN': mod_num_channels = 2
        if mod_inst_tag[-2:] == 'CN': mod_num_channels = int(mod_inst_tag[:2])
        if mod_inst_tag == 'TDZ1': mod_num_channels = 1
        if mod_inst_tag == 'TDZ2': mod_num_channels = 2
        if mod_inst_tag == 'TDZ3': mod_num_channels = 3
        if mod_inst_tag == '5CHN': mod_num_channels = 5
        if mod_inst_tag == '7CHN': mod_num_channels = 7
        if mod_inst_tag == '9CHN': mod_num_channels = 9
        if mod_inst_tag == 'FLT4': mod_num_channels = 4
        if mod_inst_tag == 'FLT8': mod_num_channels = 8
        print("[input-mod] Sample Tag: " + str(mod_inst_tag))
        print("[input-mod] Channels: " + str(mod_num_channels))

        patterntable_all = parse_song(file_stream)
        veryfirstrow = patterntable_all[t_orderlist[0]][0][0]

        for sample in range(31):
            mod_inst_entry = table_samples[sample]
            print("[input-mod] Ripping Sample", sample)
            os.makedirs(samplefolder, exist_ok=True)
            wave_path = samplefolder + str(sample+1).zfill(2) + '.wav'
            mod_sampledata = file_stream.read(table_samples[sample][1]*2)
            t_sampledata = np.frombuffer(mod_sampledata, dtype='uint8')
            t_sampledata = np.array(t_sampledata) + 128
            wave_data = t_sampledata.tobytes('C')
            finetune = modfinetune[table_samples[sample][2]]
            if mod_inst_entry[4] == 0 and mod_inst_entry[5] == 1:
                audio_wav.generate(wave_path, wave_data, 1, finetune, 8, None)
            elif mod_inst_entry[4] == 0 and mod_inst_entry[5] == 2:
                audio_wav.generate(wave_path, wave_data, 1, finetune, 8, None)
            else:
                audio_wav.generate(wave_path, wave_data, 1, finetune, 8, {'loop':[mod_inst_entry[4]*2, (mod_inst_entry[4]*2)+(mod_inst_entry[5]*2)]})

        cvpj_l_playlist = song_tracker.song2playlist(patterntable_all, mod_num_channels, t_orderlist, text_inst_start, [0.47, 0.47, 0.47])

        if 'tempo' in veryfirstrow: cvpj_bpm = veryfirstrow['tempo']
        print("[input-mod] Tempo: " + str(cvpj_bpm))

        auto_data.add_pl(cvpj_l, 'float', ['main', 'bpm'], song_tracker.tempo_auto(patterntable_all, t_orderlist, 6, cvpj_bpm))

        song.add_info(cvpj_l, 'title', mod_name)
        
        cvpj_l['do_addloop'] = True
        cvpj_l['do_lanefit'] = True

        cvpj_l['use_fxrack'] = False
        cvpj_l['use_instrack'] = False
        
        cvpj_l['playlist'] = cvpj_l_playlist
        song.add_param(cvpj_l, 'bpm', cvpj_bpm)
        return json.dumps(cvpj_l)

