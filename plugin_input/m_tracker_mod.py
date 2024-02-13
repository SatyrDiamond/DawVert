# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import math
import json
import struct
import numpy as np
from functions import data_bytes
from functions import audio_wav
from objects import dv_trackerpattern

modfinetune = [8363, 8413, 8463, 8529, 8581, 8651, 8723, 8757, 7895, 7941, 7985, 8046, 8107, 8169, 8232, 8280]

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

    def parse(self, convproj_obj, input_file, extra_param):
        global mod_num_patterns
        global mod_num_channels
        global table_samples
        global current_speed

        maincolor = [0.47, 0.47, 0.47]

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

            inst_obj = convproj_obj.add_instrument(cvpj_instid)
            inst_obj.visual.name = cvpj_instname
            inst_obj.visual.color = maincolor
            inst_obj.params.add('vol', 0.3, 'float')
            
            mod_inst_length *= 2
            mod_inst_loopstart *= 2
            mod_inst_looplength *= 2

            if mod_inst_length != 0 and mod_inst_length != 1:
                wave_path = samplefolder + str(mod_numinst).zfill(2) + '.wav'

                plugin_obj, inst_obj.pluginid, sampleref_obj = convproj_obj.add_plugin_sampler_genid(wave_path)
                plugin_obj.datavals.add('point_value_type', 'samples')

                cvpj_loopdata = {}
                if mod_inst_loopstart != 0 and mod_inst_looplength != 1:
                    cvpj_loopdata['enabled'] = 1
                    cvpj_loopdata['mode'] = "normal"
                    cvpj_loopdata['points'] = [mod_inst_loopstart, mod_inst_loopstart+mod_inst_looplength]
                else: cvpj_loopdata['enabled'] = 0

                plugin_obj.datavals.add('loop', cvpj_loopdata)

        mod_orderlist_length = file_stream.read(1)[0]
        mod_extravalue = file_stream.read(1)[0]
        t_orderlist = []
        for number in range(128):
            ordernum = file_stream.read(1)[0]
            if number < mod_orderlist_length: t_orderlist.append(ordernum)
        print("[input-mod] Order List: " + str(t_orderlist))
        mod_inst_tag = file_stream.read(4).decode()
        print("[input-mod] TAG: " + str(mod_inst_tag))
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

        patterndata = dv_trackerpattern.patterndata(mod_num_channels, text_inst_start, maincolor)

        for num_pat in range(mod_num_patterns+1):
            patterndata.pattern_add(num_pat, 64)
            for num_row in range(64):
                for num_ch in range(mod_num_channels):
                    output_note = None
                    output_inst = None
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
                    patterndata.cell_note(num_ch, output_note, output_inst)
                    patterndata.cell_fx_mod(num_ch, cell_fx_type, cell_fx_param)

                    if cell_fx_type == 12: 
                        patterndata.cell_param(num_ch, 'vol', cell_fx_param/64)
                    else: 
                        if output_inst != None:
                            if output_inst < 32:
                                patterndata.cell_param(num_ch, 'vol', table_samples[output_inst-1][3]/64)

                    if cell_fx_type == 13: patterndata.cell_g_param('break_to_row', cell_fx_param)

                    if cell_fx_type == 15:
                        if cell_fx_param < 32: patterndata.cell_g_param('speed', cell_fx_param)
                        else: patterndata.cell_g_param('tempo', cell_fx_param)

                patterndata.row_next()

        veryfirstrow = patterndata.veryfirstrow(t_orderlist[0])

        patterndata.to_cvpj(convproj_obj, t_orderlist, text_inst_start, cvpj_bpm, current_speed, maincolor)

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

        if 'tempo' in veryfirstrow: cvpj_bpm = veryfirstrow['tempo']
        if 'speed' in veryfirstrow: cvpj_bpm = cvpj_bpm*(6/veryfirstrow['speed'])
        print("[input-mod] Tempo: " + str(cvpj_bpm))

        convproj_obj.metadata.name = mod_name
        
        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_lanefit')

        convproj_obj.params.add('bpm', cvpj_bpm, 'float')