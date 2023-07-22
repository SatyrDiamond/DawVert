# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import math
import json
import struct
import numpy as np
from functions import data_bytes
from functions import song_tracker
from functions import audio_wav
from functions import tracks
from functions import plugins
from functions import song

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

    if cell_fx_type == 0:
        arpeggio_first = cell_fx_param >> 4
        arpeggio_second = cell_fx_param & 0x0F
        output_param['arp'] = [arpeggio_first, arpeggio_second]

    if cell_fx_type == 1: 
        output_param['slide_up'] = song_tracker.calcbendpower_up(cell_fx_param, current_speed)

    if cell_fx_type == 2: 
        output_param['slide_down'] = song_tracker.calcbendpower_down(cell_fx_param, current_speed)

    if cell_fx_type == 3: 
        output_param['slide_to_note'] = song_tracker.calcslidepower(cell_fx_param, current_speed)

    if cell_fx_type == 4: 
        vibrato_params = {}
        vibrato_params['speed'], vibrato_params['depth'] = data_bytes.splitbyte(cell_fx_param)
        output_param['vibrato'] = vibrato_params

    if cell_fx_type == 5:
        pos, neg = data_bytes.splitbyte(cell_fx_param)
        output_param['vol_slide'] = (neg*-1) + pos
        output_param['slide_to_note'] = (neg*-1) + pos

    if cell_fx_type == 6:
        pos, neg = data_bytes.splitbyte(cell_fx_param)
        output_param['vibrato'] = {'speed': 0, 'depth': 0}
        output_param['vol_slide'] = (neg*-1) + pos

    if cell_fx_type == 7:
        tremolo_params = {}
        tremolo_params['speed'], tremolo_params['depth'] = ()
        output_param['tremolo'] = tremolo_params

    if cell_fx_type == 8: 
        output_param['pan'] = (cell_fx_param-128)/128

    if cell_fx_type == 9: 
        output_param['sample_offset'] = cell_fx_param*256

    if cell_fx_type == 10:
        pos, neg = data_bytes.splitbyte(cell_fx_param)
        output_param['vol_slide'] = (neg*-1) + pos

    if cell_fx_type == 11: 
        output_extra['pattern_jump'] = cell_fx_param

    if cell_fx_type == 12: 
        output_param['vol'] = cell_fx_param/64
    else: 
        if output_inst != None:
            if output_inst < 32:
                output_param['vol'] = table_samples[output_inst-1][3]/64

    if cell_fx_type == 13: 
        output_extra['break_to_row'] = cell_fx_param

    if cell_fx_type == 14: 
        ext_type, ext_value = data_bytes.splitbyte(cell_fx_param)
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

            pluginid = plugins.get_id()
            if mod_inst_mod_name != "": cvpj_instname = mod_inst_mod_name
            else: cvpj_instname = ' '
            tracks.m_inst_create(cvpj_l, cvpj_instid, name=cvpj_instname, color=[0.33, 0.33, 0.33])
            tracks.m_inst_pluginid(cvpj_l, cvpj_instid, pluginid)
            tracks.m_inst_add_param(cvpj_l, cvpj_instid, 'vol', 0.3, 'float')
            
            if mod_inst_length != 0 and mod_inst_length != 1:
                wave_path = samplefolder + str(mod_numinst).zfill(2) + '.wav'
                plugins.add_plug_sampler_singlefile(cvpj_l, pluginid, wave_path)
                plugins.add_plug_data(cvpj_l, pluginid, 'point_value_type', "samples")
                plugins.add_plug_data(cvpj_l, pluginid, 'trigger', "normal")
                plugins.add_plug_data(cvpj_l, pluginid, 'start', 0)
                plugins.add_plug_data(cvpj_l, pluginid, 'end', mod_inst_length)
                plugins.add_plug_data(cvpj_l, pluginid, 'length', mod_inst_length)

                cvpj_loopdata = {}
                if mod_inst_loopstart != 0 and mod_inst_looplength != 1:
                    cvpj_loopdata['enabled'] = 1
                    cvpj_loopdata['mode'] = "normal"
                    cvpj_loopdata['points'] = [mod_inst_loopstart, mod_inst_loopstart+mod_inst_looplength]
                else: cvpj_loopdata['enabled'] = 0

                plugins.add_plug_data(cvpj_l, pluginid, 'loop', cvpj_loopdata)

        mod_orderlist_length = int.from_bytes(file_stream.read(1), "big")
        mod_extravalue = int.from_bytes(file_stream.read(1), "big")
        t_orderlist = []
        for number in range(128):
            ordernum = int.from_bytes(file_stream.read(1), "big")
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

        tracks.a_add_auto_pl(cvpj_l, 'float', ['main', 'bpm'], song_tracker.tempo_auto(patterntable_all, t_orderlist, 6, cvpj_bpm))

        song.add_info(cvpj_l, 'title', mod_name)
        
        cvpj_l['do_addloop'] = True
        cvpj_l['do_lanefit'] = True

        cvpj_l['use_fxrack'] = False
        cvpj_l['use_instrack'] = False
        
        cvpj_l['playlist'] = cvpj_l_playlist
        song.add_param(cvpj_l, 'bpm', cvpj_bpm)
        return json.dumps(cvpj_l)

