# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import math
import json
import numpy as np
from functions import song_tracker
from functions import audio_wav
from functions import folder_samples

def splitbyte(value):
    first = value >> 4
    second = value & 0x0F
    return (first, second)

def parse_mod_cell(file_stream, firstrow):
    output_note = None
    output_inst = None
    global table_samples
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
    if cell_fx_type == 0 and cell_fx_param != 0:
        arpeggio_first = cell_fx_param >> 4
        arpeggio_second = cell_fx_param & 0x0F
        output_param['tracker_arpeggio'] = [arpeggio_first, arpeggio_second]
    if cell_fx_type == 1: output_param['tracker_slide_up'] = cell_fx_param
    if cell_fx_type == 2: output_param['tracker_slide_down'] = cell_fx_param
    if cell_fx_type == 3: output_param['tracker_slide_to_note'] = cell_fx_param
    if cell_fx_type == 4: 
        vibrato_params = {}
        vibrato_params['speed'], vibrato_params['depth'] = splitbyte(cell_fx_param)
        output_param['vibrato'] = vibrato_params
    if cell_fx_type == 5:
        pos, neg = splitbyte(cell_fx_param)
        output_param['tracker_vol_slide_plus_slide_to_note'] = (neg*-1) + pos
    if cell_fx_type == 6:
        pos, neg = splitbyte(cell_fx_param)
        output_param['tracker_vol_slide_plus_vibrato'] = (neg*-1) + pos
    if cell_fx_type == 7:
        tremolo_params = {}
        tremolo_params['speed'], tremolo_params['depth'] = splitbyte(cell_fx_param)
        output_param['tremolo'] = tremolo_params
    if cell_fx_type == 8: output_param['pan'] = (cell_fx_param-128)/128
    if cell_fx_type == 9: output_param['audio_mod_inst_offset'] = cell_fx_param*256
    if cell_fx_type == 10:
        pos, neg = splitbyte(cell_fx_param)
        output_param['tracker_vol_slide'] = (neg*-1) + pos
    if cell_fx_type == 11: output_extra['tracker_jump_to_offset'] = cell_fx_param
    if cell_fx_type == 12: output_param['vol'] = cell_fx_param/64
    else: 
        if output_inst != None:
            if output_inst < 32:
                output_param['vol'] = table_samples[output_inst-1][3]/64
    if cell_fx_type == 13: output_extra['tracker_break_to_row'] = cell_fx_param
    if cell_fx_type == 15:
        if cell_fx_param < 32: output_extra['tracker_speed'] = cell_fx_param
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

class input_mod(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mod'
    def getname(self): return 'Protracker Module'
    def gettype(self): return 'm'
    def supported_autodetect(self): return True

    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(20)
        IsMod = 1
        for _ in range(31):
            bytestream.read(24)
            mod_inst_finetune = bytestream.read(1)[0]
            if 15 < mod_inst_finetune: IsMod = 0
            mod_inst_defaultvol = bytestream.read(1)[0]
            if 64 < mod_inst_defaultvol: IsMod = 0
            bytestream.read(4)
        if IsMod == 1: return True
        else: return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        global mod_num_patterns
        global mod_num_channels
        global table_samples

        text_inst_start = 'MOD_Inst_'

        file_name = os.path.splitext(os.path.basename(input_file))[0]
        samplefolder = folder_samples.samplefolder(extra_param, file_name)

        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []

        file_stream = open(input_file, 'rb')
        mod_name = file_stream.read(20).decode().rstrip('\x00')
        print("[input-mod] Song Name: " + str(mod_name))
        table_samples = []
        cvpj_bpm = 125
        for mod_numinst in range(31):
            mod_numinst += 1
            mod_inst_mod_name = file_stream.read(22).decode().rstrip('\x00')
            mod_inst_length = int.from_bytes(file_stream.read(2), "big")
            mod_inst_finetune = int.from_bytes(file_stream.read(1), "big")
            if mod_inst_finetune > 7: mod_inst_finetune -= 16
            mod_inst_defaultvol = int.from_bytes(file_stream.read(1), "big")
            mod_inst_loopstart = int.from_bytes(file_stream.read(2), "big")*2
            mod_inst_looplength = int.from_bytes(file_stream.read(2), "big")*2
            print('[input-mod] Instrument ' + str(mod_numinst) + ': ' + mod_inst_mod_name)
            table_samples.append([mod_inst_mod_name, mod_inst_length, mod_inst_finetune, mod_inst_defaultvol, mod_inst_loopstart, mod_inst_looplength])
            cvpj_l_instruments[text_inst_start + str(mod_numinst)] = {}
            #print([mod_inst_mod_name, mod_inst_length, mod_inst_finetune, mod_inst_defaultvol, mod_inst_loopstart, mod_inst_looplength])
            cvpj_l_single_inst = cvpj_l_instruments[text_inst_start + str(mod_numinst)]
            if mod_inst_mod_name != "": cvpj_l_single_inst['name'] = mod_inst_mod_name
            else: cvpj_l_single_inst['name'] = ' '
            cvpj_l_single_inst['vol'] = 0.3
            cvpj_l_single_inst['instdata'] = {}
            cvpj_l_single_inst['instdata']['pitch'] = int((mod_inst_finetune/7)*100)
            if mod_inst_length != 0 and mod_inst_length != 1:
                cvpj_l_single_inst['color'] = [0.53, 0.53, 0.53]
                cvpj_l_single_inst['instdata']['plugin'] = 'sampler'
                cvpj_l_single_inst['instdata']['plugindata'] = {}
                cvpj_l_single_inst['instdata']['plugindata']['trigger'] = 'normal'
                cvpj_l_single_inst['instdata']['plugindata']['length'] = mod_inst_length
                cvpj_l_single_inst['instdata']['plugindata']['file'] = samplefolder + str(mod_numinst).zfill(2) + '.wav'
                cvpj_l_single_inst['instdata']['plugindata']['loop'] = {}
                if mod_inst_loopstart != 0 and mod_inst_looplength != 1:
                    cvpj_l_single_inst['instdata']['plugindata']['loop']['enabled'] = 1
                    cvpj_l_single_inst['instdata']['plugindata']['loop']['mode'] = "normal"
                    cvpj_l_single_inst['instdata']['plugindata']['loop']['points'] = [mod_inst_loopstart, mod_inst_loopstart+mod_inst_looplength]
                else:
                    cvpj_l_single_inst['instdata']['plugindata']['loop']['enabled'] = 0
            else: 
                cvpj_l_single_inst['color'] = [0.33, 0.33, 0.33]
                cvpj_l_single_inst['instdata']['plugin'] = 'none'

            cvpj_l_instrumentsorder.append(text_inst_start + str(mod_numinst))
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
            if mod_inst_entry[4] == 0 and mod_inst_entry[5] == 1:
                audio_wav.generate(wave_path, wave_data, 1, 8272, 8, None)
            elif mod_inst_entry[4] == 0 and mod_inst_entry[5] == 2:
                audio_wav.generate(wave_path, wave_data, 1, 8272, 8, None)
            else:
                audio_wav.generate(wave_path, wave_data, 1, 8272, 8, {'loop':[mod_inst_entry[4]*2, (mod_inst_entry[4]*2)+(mod_inst_entry[5]*2)]})

        
        for sample in range(31):
            cvpj_l_single_inst = cvpj_l_instruments[text_inst_start + str(mod_numinst)]
            cvpj_l_inst = cvpj_l_single_inst['instdata']
            if 'plugindata' in cvpj_l_inst:
                cvpj_l_plugin = cvpj_l_inst['plugindata']
                cvpj_l_plugin['loop'] = {}
                if mod_inst_entry[4] == 0 and mod_inst_entry[5] == 1:
                    cvpj_l_plugin['loop']['enabled'] = 0
                else:
                    loopdata = [mod_inst_entry[4]*2, (mod_inst_entry[4]*2)+(mod_inst_entry[5]*2)]
                    cvpj_l_plugin['loop']['enabled'] = 1
                    cvpj_l_plugin['loop']['mode'] = "normal"
                    cvpj_l_plugin['loop']['points'] = loopdata


        cvpj_l_playlist = song_tracker.song2playlist(patterntable_all, mod_num_channels, t_orderlist, text_inst_start, [0.47, 0.47, 0.47])

        if 'tempo' in veryfirstrow: cvpj_bpm = veryfirstrow['tempo']
        print("[input-mod] Tempo: " + str(cvpj_bpm))


        cvpj_l = {}
        
        automation = {}
        automation['main'] = {}
        automation['main']['bpm'] = song_tracker.tempo_auto(patterntable_all, t_orderlist, 6, cvpj_bpm)
        cvpj_l['automation'] = automation

        cvpj_l['info'] = {}
        cvpj_l['info']['title'] = mod_name
        cvpj_l['use_fxrack'] = False
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = cvpj_bpm
        return json.dumps(cvpj_l)

