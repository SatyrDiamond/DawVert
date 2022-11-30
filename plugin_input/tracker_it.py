# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import math
import json
import numpy as np
from functions import song_tracker
from functions import audio_wav
from functions import folder_samples

try: import xmodits
except: xmodits_exists = False
else: xmodits_exists = True

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
    def getshortname(self): return 'it'
    def getname(self): return 'Tracker: Impulse Tracker'
    def gettype(self): return 'm'
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytesdata = bytestream.read(4)
        if bytesdata == b'IMPM': return True
        else: return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        it_file = open(input_file, 'rb')

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []

        startinststr = 'IT_Inst_'

        modulename = os.path.splitext(os.path.basename(input_file))[0]
        samplefolder = folder_samples.samplefolder(extra_param, modulename)

        it_header_magic = it_file.read(4)
        if it_header_magic != b'IMPM':
            print('[error] Not an IT File')
            exit()
        
        it_header_songname = it_file.read(26).split(b'\x00' * 1)[0].decode("utf-8")
        print("[input-it] Song Name: " + str(it_header_songname))
        it_header_hilight_minor = int.from_bytes(it_file.read(1), "little")
        it_header_hilight_major = int.from_bytes(it_file.read(1), "little")
        it_header_ordnum = int.from_bytes(it_file.read(2), "little")
        print("[input-it] # of Orders: " + str(it_header_ordnum))
        it_header_insnum = int.from_bytes(it_file.read(2), "little")
        print("[input-it] # of Instruments: " + str(it_header_insnum))
        it_header_smpnum = int.from_bytes(it_file.read(2), "little")
        print("[input-it] # of Samples: " + str(it_header_smpnum))
        it_header_patnum = int.from_bytes(it_file.read(2), "little")
        print("[input-it] # of Patterns: " + str(it_header_patnum))
        
        it_header_cwtv = int.from_bytes(it_file.read(2), "little")
        it_header_cmwt = int.from_bytes(it_file.read(2), "little")
        print("[input-it] CMWT: " + str(it_header_cmwt))
        
        it_header_flags = bin(int.from_bytes(it_file.read(2), "little"))[2:].zfill(16)
        it_header_flag_useinst = it_header_flags[13]
        it_header_special = it_file.read(2)
        it_header_globalvol = int.from_bytes(it_file.read(1), "little")
        it_header_mv = int.from_bytes(it_file.read(1), "little")
        it_header_speed = int.from_bytes(it_file.read(1), "little")
        print("[input-it] Speed: " + str(it_header_speed))
        it_header_tempo = int.from_bytes(it_file.read(1), "little")
        print("[input-it] Tempo: " + str(it_header_tempo))
        it_header_sep = int.from_bytes(it_file.read(1), "little")
        it_header_pwd = int.from_bytes(it_file.read(1), "little")
        it_header_msglength = int.from_bytes(it_file.read(2), "little")
        it_header_msgoffset = int.from_bytes(it_file.read(4), "little")
        it_header_reserved = int.from_bytes(it_file.read(4), "little")
        
        table_chnpan = []
        for _ in range(64): table_chnpan.append(int.from_bytes(it_file.read(1), "little"))
        table_chnvol = []
        for _ in range(64): table_chnvol.append(int.from_bytes(it_file.read(1), "little"))
        table_orders = []
        for _ in range(it_header_ordnum): table_orders.append(int.from_bytes(it_file.read(1), "little"))
        table_offset_insts = []
        for _ in range(it_header_insnum): table_offset_insts.append(int.from_bytes(it_file.read(4), "little"))
        table_offset_samples = []
        for _ in range(it_header_smpnum): table_offset_samples.append(int.from_bytes(it_file.read(4), "little"))
        table_offset_patterns = []
        for _ in range(it_header_patnum): table_offset_patterns.append(int.from_bytes(it_file.read(4), "little"))
        
        # ------------- Orders -------------
        while 254 in table_orders: table_orders.remove(254)
        while 255 in table_orders: table_orders.remove(255)
        print("[input-it] Order List: " + str(table_orders))
        
        # ------------- Instruments -------------
        IT_Insts = {}
        instrumentcount = 0
        for table_offset_inst in table_offset_insts:
            IT_Insts[str(instrumentcount)] = {}
            it_singleinst = IT_Insts[str(instrumentcount)]
            it_file.seek(table_offset_inst)
            inst_magic = it_file.read(4)
            if inst_magic != b'IMPI':
                print('[input-it] Instrument not Valid')
                exit()
            print("[input-it] Instrument " + str(instrumentcount) + ': at offset ' + str(table_offset_inst))
            it_singleinst['dosfilename'] = it_file.read(12).split(b'\x00' * 1)[0].decode("latin_1")
            it_file.read(1)
            it_singleinst['newnoteaction'] = int.from_bytes(it_file.read(1), "little") # New Note Action
            it_singleinst['duplicatechecktype'] = int.from_bytes(it_file.read(1), "little") # Duplicate Check Type
            it_singleinst['duplicatecheckaction'] = int.from_bytes(it_file.read(1), "little") # Duplicate Check Action
            it_singleinst['fadeout'] = int.from_bytes(it_file.read(2), "little") # FadeOut
            it_singleinst['pitchpanseparation'] = int.from_bytes(it_file.read(1), "little", signed=True) # Pitch-Pan separation
            it_singleinst['pitchpancenter'] = int.from_bytes(it_file.read(1), "little")-60 # Pitch-Pan center
            it_singleinst['globalvol'] = int.from_bytes(it_file.read(1), "little")/128 # Global Volume
            inst_defaultpan = int.from_bytes(it_file.read(1), "little") # Default Pan
            if inst_defaultpan < 128: it_singleinst['defaultpan'] = (inst_defaultpan/32-1)
            it_singleinst['randomvariation_volume'] = int.from_bytes(it_file.read(1), "little")/100 # Random volume variation (percentage)
            it_singleinst['randomvariation_pan'] = int.from_bytes(it_file.read(1), "little")/64 # Random pan variation (percentage)
            it_singleinst['cwtv'] = int.from_bytes(it_file.read(2), "little") # TrkVers
            it_singleinst['smpnum'] = int.from_bytes(it_file.read(1), "little") # Number of samples associated with instrument. 
            it_file.read(1)
            it_singleinst['name'] = it_file.read(26).split(b'\x00' * 1)[0].decode("latin_1")
            inst_filtercutoff = int.from_bytes(it_file.read(1), "little")
            if inst_filtercutoff >= 128: it_singleinst['filtercutoff'] = inst_filtercutoff-128
            else: it_singleinst['filtercutoff'] = None
            inst_filterresonance = int.from_bytes(it_file.read(1), "little")
            if inst_filterresonance >= 128: it_singleinst['filterresonance'] =  inst_filterresonance-128
            else: it_singleinst['filterresonance'] = None
            it_inst_midi_chan = int.from_bytes(it_file.read(1), "little") # MIDI Channel
            it_inst_midi_inst = int.from_bytes(it_file.read(1), "little") # MIDI Program
            it_inst_midi_bank = int.from_bytes(it_file.read(2), "little") # MIDI Bank
            if it_inst_midi_chan != 0: it_singleinst['midi_chan'] = it_inst_midi_chan
            if it_inst_midi_inst != 255: it_singleinst['midi_inst'] = it_inst_midi_inst
            if it_inst_midi_bank != 65535: it_singleinst['midi_bank'] = it_inst_midi_bank
            #print(it_inst_midi_chan,it_inst_midi_inst,it_inst_midi_bank)
            table_notesample = []
            for _ in range(120):
                t_note = int.from_bytes(it_file.read(1), "little")-60
                t_sample = int.from_bytes(it_file.read(1), "little")
                table_notesample.append([t_note,t_sample])
            it_singleinst['notesampletable'] = table_notesample
            for env_type in range(3):
                env_out = {}
                env_flags = bin(int.from_bytes(it_file.read(1), "little"))[2:].zfill(8)
                env_out['enabled'] = env_flags[7]
                env_out['loop_enabled'] = env_flags[6]
                env_out['susloop_enabled'] = env_flags[5]
                env_out['usepitch'] = env_flags[0]
                env_numpoints = int.from_bytes(it_file.read(1), "little")
                env_out['loop_start'] = int.from_bytes(it_file.read(1), "little")
                env_out['loop_end'] = int.from_bytes(it_file.read(1), "little")
                env_out['susloop_start'] = int.from_bytes(it_file.read(1), "little")
                env_out['susloop_end'] = int.from_bytes(it_file.read(1), "little")
                env_points = []
                for _ in range(env_numpoints):
                    env_point = {}
                    env_point['value'] = int.from_bytes(it_file.read(1), "little")
                    env_point['pos'] = int.from_bytes(it_file.read(2), "little")
                    env_points.append(env_point)
                if env_type == 0: it_singleinst['env_volume'] = env_points
                if env_type == 1: it_singleinst['env_pan'] = env_points
                if env_type == 2: it_singleinst['env_pitch'] = env_points
                it_file.read(76-(env_numpoints*3))
            instrumentcount += 1
        
        # ------------- Samples -------------
        IT_Samples = {}
        samplecount = 0
        for table_offset_sample in table_offset_samples:
            IT_Samples[str(samplecount)] = {}
            it_singlesample = IT_Samples[str(samplecount)]
            it_file.seek(table_offset_sample)
            sample_header = it_file.read(4)
            if sample_header != b'IMPS':
                print('[input-it] Sample not Valid')
                exit()
            print("[input-it] Sample " + str(samplecount) + ': at offset ' + str(table_offset_sample))
            it_singlesample['dosfilename'] = it_file.read(12).split(b'\x00' * 1)[0].decode("latin_1")
            it_file.read(4)
            it_singlesample['name'] = it_file.read(26).split(b'\x00' * 1)[0].decode("latin_1")
            samplecount += 1
        
        if xmodits_exists == True:
            xmodits.dump(input_file, samplefolder, index_only=True)

        # ------------- Pattern -------------
        patterncount = 1
        patterntable_all = []
        for table_offset_pattern in table_offset_patterns:
            patterntable_single = []
            if table_offset_pattern != 0:
                print("[input-it] Pattern " + str(patterncount),end=': ')
                it_file.seek(table_offset_pattern)
                pattern_length = int.from_bytes(it_file.read(2), "little")
                pattern_rows = int.from_bytes(it_file.read(2), "little")
                print(str(pattern_rows) + ' Rows',end=', ')
                print('Size: ' + str(pattern_length) + ' at offset ' + str(table_offset_pattern))
                it_file.read(4)
                firstrow = 1
                rowcount = 0
                table_lastnote = []
                for _ in range(64): table_lastnote.append(None)
                table_lastinstrument = []
                for _ in range(64):  table_lastinstrument.append(None)
                table_lastvolpan = []
                for _ in range(64): table_lastvolpan.append(None)
                table_lastcommand = []
                for _ in range(64): table_lastcommand.append([None, None])
                table_previousmaskvariable = []
                for _ in range(64): table_previousmaskvariable.append(None)
                for _ in range(pattern_rows):
                    pattern_done = 0
                    pattern_row_local = []
                    for _ in range(64): pattern_row_local.append([None, None, {}, {}])
                    pattern_row = [{}, pattern_row_local]
                    while pattern_done == 0:
                        channelvariable = bin(int.from_bytes(it_file.read(1), "little"))[2:].zfill(8)
                        cell_previous_maskvariable = int(channelvariable[0:1], 2)
                        cell_channel = int(channelvariable[1:8], 2) - 1
                        if int(channelvariable, 2) == 0: pattern_done = 1
                        else:
                            #print('ch:' + str(cell_channel) + '|', end=' ')
                            if cell_previous_maskvariable == 1:
                                maskvariable = bin(int.from_bytes(it_file.read(1), "little"))[2:].zfill(8)
                                table_previousmaskvariable[cell_channel] = maskvariable
                            else: maskvariable = table_previousmaskvariable[cell_channel]
                            maskvariable_note = int(maskvariable[7], 2) 
                            maskvariable_instrument = int(maskvariable[6], 2)
                            maskvariable_volpan = int(maskvariable[5], 2)
                            maskvariable_command = int(maskvariable[4], 2)
                            maskvariable_last_note = int(maskvariable[3], 2)
                            maskvariable_last_instrument = int(maskvariable[2], 2)
                            maskvariable_last_volpan = int(maskvariable[1], 2)
                            maskvariable_last_command = int(maskvariable[0], 2)
        
                            cell_note = None
                            cell_instrument = None
                            cell_volpan = None
                            cell_commandtype = None
                            cell_commandnum = None
        
                            if maskvariable_note == 1:
                                cell_note = int.from_bytes(it_file.read(1), "little")
                                table_lastnote[cell_channel] = cell_note
                            if maskvariable_instrument == 1:
                                cell_instrument = int.from_bytes(it_file.read(1), "little")
                                table_lastinstrument[cell_channel] = cell_instrument
                            if maskvariable_volpan == 1:
                                cell_volpan = int.from_bytes(it_file.read(1), "little")
                                table_lastvolpan[cell_channel] = cell_volpan
                            if maskvariable_command == 1:
                                cell_commandtype = int.from_bytes(it_file.read(1), "little")
                                cell_commandnum = int.from_bytes(it_file.read(1), "little")
                                table_lastcommand[cell_channel] = [cell_commandtype, cell_commandnum]
        
                            if maskvariable_last_note == 1: cell_note = table_lastnote[cell_channel]
                            if maskvariable_last_instrument == 1: cell_instrument = table_lastinstrument[cell_channel]
                            if maskvariable_last_volpan == 1: cell_volpan = table_lastvolpan[cell_channel]
                            if maskvariable_last_command == 1:
                                cell_commandtype = table_lastcommand[cell_channel][0]
                                cell_commandnum = table_lastcommand[cell_channel][1]
        
                            if cell_volpan != None:
                                if cell_volpan <= 64: pattern_row[1][cell_channel][2]['vol'] = cell_volpan/64
                                elif 192 >= cell_volpan >= 128: pattern_row[1][cell_channel][2]['pan'] = ((cell_volpan-128)/64-0.5)*2
        
                            if cell_note != None: pattern_row[1][cell_channel][0] = cell_note - 48
                            if cell_note == 254: pattern_row[1][cell_channel][0] = 'Cut'
                            if cell_note == 255: pattern_row[1][cell_channel][0] = 'Off'
                            if cell_note == 246: pattern_row[1][cell_channel][0] = 'Fade'
        
                            if cell_instrument != None: pattern_row[1][cell_channel][1] = cell_instrument
                                
                            if cell_commandtype == 1: pattern_row[0]['tracker_speed'] = cell_commandnum
                            if cell_commandtype == 24: pattern_row[1][cell_channel][2]['pan'] = ((cell_commandnum/255)-0.5)*2
                            if firstrow == 1: pattern_row[0]['firstrow'] = 1
                            rowcount += 1
                    firstrow = 0
                    patterntable_single.append(pattern_row)
            patterntable_all.append(patterntable_single)
            patterncount += 1

        veryfirstrow = patterntable_all[table_orders[0]][0][0]

        cvpj_l_playlist = song_tracker.song2playlist(patterntable_all, 64, table_orders, startinststr, [0.71, 0.58, 0.47])

        instrumentcount = 0
        samplecount = 0
        it_header_flag_useinst = int(it_header_flag_useinst)
        if it_header_flag_useinst == 1:
            for IT_Inst in IT_Insts:
                it_instname = startinststr + str(instrumentcount+1)
                it_singleinst = IT_Insts[IT_Inst]
                cvpj_l_instruments[it_instname] = {}
                cvpj_l_single_inst = cvpj_l_instruments[it_instname]
                cvpj_l_single_inst['color'] = [0.71, 0.58, 0.47]
                if it_singleinst['name'] != '': cvpj_l_single_inst['name'] = it_singleinst['name']
                elif it_singleinst['dosfilename'] != '': cvpj_l_single_inst['name'] = it_singleinst['dosfilename']
                else: cvpj_l_single_inst['name'] = " "
                cvpj_l_single_inst['vol'] = 0.3

                temp_inst_is_single_sample = True
                temp_allsample = None
                temp_firstsamplefound = None

                for it_notesample_entry in it_singleinst['notesampletable']:
                    temp_sampnum = it_notesample_entry[1]
                    if temp_firstsamplefound == None and temp_sampnum != 0:
                        temp_firstsamplefound = temp_sampnum
                    elif temp_firstsamplefound != temp_sampnum and temp_sampnum != 0:
                        temp_inst_is_single_sample = False

                temp_nst_currentnote = -60

                for it_notesample_entry in it_singleinst['notesampletable']:
                    if it_notesample_entry[0] != temp_nst_currentnote:
                        temp_inst_is_single_sample = False
                        break
                    temp_nst_currentnote += 1

                if temp_firstsamplefound != None and temp_inst_is_single_sample == True:
                    temp_allsample = temp_firstsamplefound
                    cvpj_l_single_inst['instdata'] = {}
                    cvpj_l_single_inst['instdata']['middlenote'] = 12
                    cvpj_l_single_inst['instdata']['plugin'] = 'sampler'
                    cvpj_l_single_inst['instdata']['plugindata'] = {}
                    cvpj_l_single_inst['instdata']['plugindata']['file'] = samplefolder + str(temp_allsample).zfill(2) + '.wav'
                else:
                    cvpj_l_single_inst['instdata'] = {}
                    cvpj_l_single_inst['instdata']['plugin'] = 'none'
                    cvpj_l_single_inst['instdata']['middlenote'] = 12
                cvpj_l_instrumentsorder.append(it_instname)
                instrumentcount += 1
        if it_header_flag_useinst == 0:
            for IT_Sample in IT_Samples:
                it_samplename = startinststr + str(samplecount+1)
                it_singlesample = IT_Samples[IT_Sample]
                cvpj_l_instruments[it_samplename] = {}
                cvpj_l_single_inst = cvpj_l_instruments[it_samplename]
                cvpj_l_single_inst['color'] = [0.71, 0.58, 0.47]
                if it_singlesample['name'] != '': cvpj_l_single_inst['name'] = it_singlesample['name']
                elif it_singlesample['dosfilename'] != '': cvpj_l_single_inst['name'] = it_singlesample['dosfilename']
                else: cvpj_l_single_inst['name'] = " "
                cvpj_l_single_inst['vol'] = 0.3
                cvpj_l_single_inst['instdata'] = {}
                cvpj_l_single_inst['instdata']['middlenote'] = 12
                cvpj_l_single_inst['instdata']['plugin'] = 'sampler'
                cvpj_l_single_inst['instdata']['plugindata'] = {}
                cvpj_l_single_inst['instdata']['plugindata']['file'] = samplefolder + str(samplecount+1).zfill(2) + '.wav'
                cvpj_l_instrumentsorder.append(it_samplename)
                samplecount += 1

        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = it_header_tempo
        return json.dumps(cvpj_l)

