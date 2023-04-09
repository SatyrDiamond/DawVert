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
from functions import placements
from functions import tracks
from functions import data_bytes

try: import xmodits
except: xmodits_exists = False
else: xmodits_exists = True

startinststr = 'IT_Inst_'
t_retg_alg = [['mul', 1], ['minus', 1], ['minus', 2], ['minus', 4], ['minus', 8], ['minus', 16], ['mul', 2/3], ['mul', 1/2], ['mul', 1], ['plus', 1], ['plus', 2], ['plus', 4], ['plus', 8], ['plus', 16], ['mul', 3/2], ['mul', 2]]

class input_it(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'it'
    def getname(self): return 'Impulse Tracker'
    def gettype(self): return 'm'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': True,
        'placement_cut': False,
        'placement_warp': False,
        'no_placements': False
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytesdata = bytestream.read(4)
        if bytesdata == b'IMPM': return True
        else: return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        it_file = open(input_file, 'rb')

        modulename = os.path.splitext(os.path.basename(input_file))[0]
        samplefolder = folder_samples.samplefolder(extra_param, modulename)

        cvpj_l = {}

        it_header_magic = it_file.read(4)
        if it_header_magic != b'IMPM':
            print('[error] Not an IT File')
            exit()
        
        it_header_songname = it_file.read(26).split(b'\x00' * 1)[0].decode("utf-8")
        print("[input-it] Song Name: " + str(it_header_songname))
        it_header_hilight_minor, it_header_hilight_major, it_header_ordnum, it_header_insnum, it_header_smpnum, it_header_patnum = struct.unpack('BBHHHH', it_file.read(10))
        print("[input-it] # of Orders: " + str(it_header_ordnum))
        print("[input-it] # of Instruments: " + str(it_header_insnum))
        print("[input-it] # of Samples: " + str(it_header_smpnum))
        print("[input-it] # of Patterns: " + str(it_header_patnum))
        
        it_header_cwtv = int.from_bytes(it_file.read(2), "little")
        it_header_cmwt = int.from_bytes(it_file.read(2), "little")
        print("[input-it] CMWT: " + str(it_header_cmwt))
        
        it_header_flags = bin(int.from_bytes(it_file.read(2), "little"))[2:].zfill(16)
        it_header_flag_useinst = it_header_flags[13]
        it_header_special = it_file.read(2)
        it_header_globalvol = it_file.read(1)[0]
        it_header_mv = it_file.read(1)[0]
        it_header_speed = it_file.read(1)[0]
        print("[input-it] Speed: " + str(it_header_speed))
        current_speed = it_header_speed
        it_header_tempo = it_file.read(1)[0]
        print("[input-it] Tempo: " + str(it_header_tempo))
        it_header_sep = it_file.read(1)[0]
        it_header_pwd = it_file.read(1)[0]
        it_header_msglength = int.from_bytes(it_file.read(2), "little")
        it_header_msgoffset = int.from_bytes(it_file.read(4), "little")
        it_header_reserved = int.from_bytes(it_file.read(4), "little")
        
        table_chnpan = struct.unpack('B'*64, it_file.read(64))
        table_chnvol = struct.unpack('B'*64, it_file.read(64))

        table_orders = list(struct.unpack('B'*it_header_ordnum, it_file.read(it_header_ordnum)))
        table_offset_insts = struct.unpack('I'*it_header_insnum, it_file.read(it_header_insnum*4))
        table_offset_samples = struct.unpack('I'*it_header_smpnum, it_file.read(it_header_smpnum*4))
        table_offset_patterns = struct.unpack('I'*it_header_patnum, it_file.read(it_header_patnum*4))

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
            it_singleinst['newnoteaction'] = it_file.read(1)[0] # New Note Action
            it_singleinst['duplicatechecktype'] = it_file.read(1)[0] # Duplicate Check Type
            it_singleinst['duplicatecheckaction'] = it_file.read(1)[0] # Duplicate Check Action
            it_singleinst['fadeout'] = int.from_bytes(it_file.read(2), "little") # FadeOut
            it_singleinst['pitchpanseparation'] = int.from_bytes(it_file.read(1), "little", signed=True) # Pitch-Pan separation
            it_singleinst['pitchpancenter'] = it_file.read(1)[0]-60 # Pitch-Pan center
            it_singleinst['globalvol'] = it_file.read(1)[0]/128 # Global Volume
            inst_defaultpan = it_file.read(1)[0] # Default Pan
            if inst_defaultpan < 128: it_singleinst['defaultpan'] = (inst_defaultpan/32-1)
            it_singleinst['randomvariation_volume'] = it_file.read(1)[0]/100 # Random volume variation (percentage)
            it_singleinst['randomvariation_pan'] = it_file.read(1)[0]/64 # Random pan variation (percentage)
            it_singleinst['cwtv'] = int.from_bytes(it_file.read(2), "little") # TrkVers
            it_singleinst['smpnum'] = it_file.read(1)[0] # Number of samples associated with instrument. 
            it_file.read(1)
            it_singleinst['name'] = it_file.read(26).split(b'\x00' * 1)[0].decode("latin_1")
            inst_filtercutoff = it_file.read(1)[0]
            if inst_filtercutoff >= 128: it_singleinst['filtercutoff'] = inst_filtercutoff-128
            else: it_singleinst['filtercutoff'] = None
            inst_filterresonance = it_file.read(1)[0]
            if inst_filterresonance >= 128: it_singleinst['filterresonance'] =  inst_filterresonance-128
            else: it_singleinst['filterresonance'] = None
            it_inst_midi_chan = it_file.read(1)[0] # MIDI Channel
            it_inst_midi_inst = it_file.read(1)[0] # MIDI Program
            it_inst_midi_bank = int.from_bytes(it_file.read(2), "little") # MIDI Bank
            if it_inst_midi_chan != 0: it_singleinst['midi_chan'] = it_inst_midi_chan
            if it_inst_midi_inst != 255: it_singleinst['midi_inst'] = it_inst_midi_inst
            if it_inst_midi_bank != 65535: it_singleinst['midi_bank'] = it_inst_midi_bank
            table_notesample = []
            for _ in range(120):
                t_note = it_file.read(1)[0]-60
                t_sample = it_file.read(1)[0]
                table_notesample.append([t_note,t_sample])
            it_singleinst['notesampletable'] = table_notesample
            for env_type in range(3):
                env_out = {}
                env_flags = bin(it_file.read(1)[0])[2:].zfill(8)
                env_out['enabled'] = env_flags[7]
                env_out['loop_enabled'] = env_flags[6]
                env_out['susloop_enabled'] = env_flags[5]
                env_out['usepitch'] = env_flags[0]
                env_numpoints = it_file.read(1)[0]
                env_out['loop_start'] = it_file.read(1)[0]
                env_out['loop_end'] = it_file.read(1)[0]
                env_out['susloop_start'] = it_file.read(1)[0]
                env_out['susloop_end'] = it_file.read(1)[0]
                env_points = []
                for _ in range(env_numpoints):
                    env_point = {}
                    env_point['value'] = it_file.read(1)[0]
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
            it_file.read(2)
            it_singlesample['flags'] = bin(it_file.read(1)[0])[2:].zfill(8)
            it_file.read(1)
            it_singlesample['name'] = it_file.read(26).split(b'\x00' * 1)[0].decode("latin_1")
            it_file.read(2)
            it_singlesample['length'] = int.from_bytes(it_file.read(4), "little")
            it_singlesample['loop_start'] = int.from_bytes(it_file.read(4), "little")
            it_singlesample['loop_end'] = int.from_bytes(it_file.read(4), "little")
            samplecount += 1
        
        if xmodits_exists == True:
            try: xmodits.dump(input_file, samplefolder, index_only=True, index_raw=True, index_padding=0)
            except: pass

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
                        channelvariable = bin(it_file.read(1)[0])[2:].zfill(8)
                        cell_previous_maskvariable = int(channelvariable[0:1], 2)
                        cell_channel = int(channelvariable[1:8], 2) - 1
                        if int(channelvariable, 2) == 0: pattern_done = 1
                        else:
                            #print('ch:' + str(cell_channel) + '|', end=' ')
                            if cell_previous_maskvariable == 1:
                                maskvariable = bin(it_file.read(1)[0])[2:].zfill(8)
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
                            cell_commandval = None
        
                            if maskvariable_note == 1:
                                cell_note = it_file.read(1)[0]
                                table_lastnote[cell_channel] = cell_note
                            if maskvariable_instrument == 1:
                                cell_instrument = it_file.read(1)[0]
                                table_lastinstrument[cell_channel] = cell_instrument
                            if maskvariable_volpan == 1:
                                cell_volpan = it_file.read(1)[0]
                                table_lastvolpan[cell_channel] = cell_volpan
                            if maskvariable_command == 1:
                                cell_commandtype = it_file.read(1)[0]
                                cell_commandval = it_file.read(1)[0]
                                table_lastcommand[cell_channel] = [cell_commandtype, cell_commandval]
        
                            if maskvariable_last_note == 1: cell_note = table_lastnote[cell_channel]
                            if maskvariable_last_instrument == 1: cell_instrument = table_lastinstrument[cell_channel]
                            if maskvariable_last_volpan == 1: cell_volpan = table_lastvolpan[cell_channel]
                            if maskvariable_last_command == 1:
                                cell_commandtype = table_lastcommand[cell_channel][0]
                                cell_commandval = table_lastcommand[cell_channel][1]
        
                            if cell_volpan != None:
                                if cell_volpan <= 64: pattern_row[1][cell_channel][2]['vol'] = cell_volpan/64
                                elif 192 >= cell_volpan >= 128: pattern_row[1][cell_channel][2]['pan'] = ((cell_volpan-128)/64-0.5)*2
        
                            if cell_note != None: pattern_row[1][cell_channel][0] = cell_note - 60
                            if cell_note == 254: pattern_row[1][cell_channel][0] = 'Cut'
                            if cell_note == 255: pattern_row[1][cell_channel][0] = 'Off'
                            if cell_note == 246: pattern_row[1][cell_channel][0] = 'Fade'
        
                            if cell_instrument != None: pattern_row[1][cell_channel][1] = cell_instrument
                            
                            j_note_cmdval = pattern_row[1][cell_channel][2]

                            if cell_commandtype == 1: 
                                pattern_row[0]['speed'] = cell_commandval
                                current_speed = cell_commandval
                            
                            if cell_commandtype == 2: 
                                pattern_row[0]['pattern_jump'] = cell_commandval
                            
                            if cell_commandtype == 3: 
                                pattern_row[0]['break_to_row'] = cell_commandval
                            
                            if cell_commandtype == 4: 
                                j_note_cmdval['vol_slide'] = song_tracker.getfineval(cell_commandval)

                            if cell_commandtype == 5: 
                                j_note_cmdval['slide_down_cont'] = song_tracker.calcbendpower_down(cell_commandval, current_speed)
                            
                            if cell_commandtype == 6: 
                                j_note_cmdval['slide_up_cont'] = song_tracker.calcbendpower_up(cell_commandval, current_speed)
                            
                            if cell_commandtype == 7: 
                                j_note_cmdval['slide_to_note'] = song_tracker.calcslidepower(cell_commandval, current_speed)
                            
                            if cell_commandtype == 8: 
                                vibrato_params = {}
                                vibrato_params['speed'], vibrato_params['depth'] = data_bytes.splitbyte(cell_commandval)
                                j_note_cmdval['vibrato'] = vibrato_params
                            
                            if cell_commandtype == 9: 
                                tremor_params = {}
                                tremor_params['ontime'], tremor_params['offtime'] = data_bytes.splitbyte(cell_commandval)
                                j_note_cmdval['tremor'] = tremor_params
                            
                            if cell_commandtype == 10: 
                                arp_params = [0,0]
                                arp_params[0], arp_params[1] = data_bytes.splitbyte(cell_commandval)
                                j_note_cmdval['arp'] = arp_params
                            
                            if cell_commandtype == 11: 
                                j_note_cmdval['vol_slide'] = song_tracker.getfineval(cell_commandval)
                                j_note_cmdval['vibrato'] = {'speed': 0, 'depth': 0}
                            
                            if cell_commandtype == 12: 
                                j_note_cmdval['vol_slide'] = song_tracker.getfineval(cell_commandval)
                                j_note_cmdval['slide_to_note'] = song_tracker.getfineval(cell_commandval)

                            if cell_commandtype == 13: 
                                j_note_cmdval['channel_vol'] = cell_commandval/64

                            if cell_commandtype == 14: 
                                j_note_cmdval['channel_vol_slide'] = song_tracker.getfineval(cell_commandval)

                            if cell_commandtype == 15: 
                                j_note_cmdval['sample_offset'] = cell_commandval*256

                            if cell_commandtype == 16: 
                                j_note_cmdval['pan_slide'] = song_tracker.getfineval(cell_commandval)*-1

                            if cell_commandtype == 17: 
                                retrigger_params = {}
                                retrigger_alg, retrigger_params['speed'] = data_bytes.splitbyte(cell_commandval)
                                retrigger_params['alg'], retrigger_params['val'] = t_retg_alg[retrigger_alg]
                                j_note_cmdval['retrigger'] = retrigger_params
                            
                            if cell_commandtype == 18: 
                                tremolo_params = {}
                                tremolo_params['speed'], tremolo_params['depth'] = data_bytes.splitbyte(cell_commandval)
                                j_note_cmdval['tremolo'] = tremolo_params

                            if cell_commandtype == 19: 
                                ext_type, ext_value = data_bytes.splitbyte(cell_commandval)
                                if ext_type == 1: j_note_cmdval['glissando_control'] = ext_value
                                if ext_type == 3: j_note_cmdval['vibrato_waveform'] = ext_value
                                if ext_type == 4: j_note_cmdval['tremolo_waveform'] = ext_value
                                if ext_type == 5: j_note_cmdval['panbrello_waveform'] = ext_value
                                if ext_type == 6: j_note_cmdval['fine_pattern_delay'] = ext_value
                                if ext_type == 7: j_note_cmdval['it_inst_control'] = ext_value
                                if ext_type == 8: j_note_cmdval['set_pan'] = ext_value/16
                                if ext_type == 9: j_note_cmdval['it_sound_control'] = ext_value
                                if ext_type == 10: j_note_cmdval['sample_offset_high'] = ext_value*65536
                                if ext_type == 11: j_note_cmdval['loop_start'] = ext_value
                                if ext_type == 12: j_note_cmdval['note_cut'] = ext_value
                                if ext_type == 13: j_note_cmdval['note_delay'] = ext_value
                                if ext_type == 14: j_note_cmdval['pattern_delay'] = ext_value
                                if ext_type == 15: j_note_cmdval['it_active_macro'] = ext_value

                            if cell_commandtype == 20: 
                                pattern_row[0]['tempo'] = cell_commandval
                            
                            if cell_commandtype == 21: 
                                fine_vib_sp, fine_vib_de = data_bytes.splitbyte(cell_commandval)
                                vibrato_params = {}
                                vibrato_params['speed'] = fine_vib_sp/16
                                vibrato_params['depth'] = fine_vib_sp/16
                                j_note_cmdval['vibrato'] = vibrato_params
                            
                            if cell_commandtype == 22: 
                                pattern_row[0]['global_volume'] = cell_commandval/128
                            
                            if cell_commandtype == 23: 
                                pattern_row[0]['global_volume_slide'] = song_tracker.getfineval(cell_commandval)

                            if cell_commandtype == 24: 
                                j_note_cmdval['set_pan'] = cell_commandval/255

                            if cell_commandtype == 25: 
                                panbrello_params = {}
                                panbrello_params['speed'], panbrello_params['depth'] = data_bytes.splitbyte(cell_commandval)
                                j_note_cmdval['panbrello'] = panbrello_params

                            if cell_commandtype == 26: 
                                j_note_cmdval['pan'] = ((cell_commandval/255)-0.5)*2
                            
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

                if it_singleinst['name'] != '': cvpj_instname = it_singleinst['name']
                elif it_singleinst['dosfilename'] != '': cvpj_instname = it_singleinst['dosfilename']
                else: cvpj_instname = " "

                n_s_t = it_singleinst['notesampletable']
                bn_s_t = []

                basenoteadd = 60
                for n_s_te in n_s_t:
                    bn_s_t.append([n_s_te[0]+basenoteadd, n_s_te[1]])
                    basenoteadd -= 1

                bn_s_t_ifsame = False

                if all(item == bn_s_t[0] for item in bn_s_t) == True:
                    bn_s_t_ifsame = True
                    bn_s_t_f = bn_s_t[0]

                if all(item == bn_s_t[12] for item in bn_s_t[12:108]) == True:
                    bn_s_t_ifsame = True
                    bn_s_t_f = bn_s_t[12]

                if bn_s_t_ifsame == True and str(bn_s_t_f[1]-1) in IT_Samples:
                    it_singlesample = IT_Samples[str(bn_s_t_f[1]-1)]
                    cvpj_instdata = {}
                    cvpj_instdata['plugin'] = 'sampler'
                    cvpj_instdata['plugindata'] = {}
                    cvpj_instdata['plugindata']['point_value_type'] = "samples"
                    cvpj_instdata['plugindata']['file'] = samplefolder + str(bn_s_t_f[1]) + '.wav'
                    if it_singlesample['length'] != 0:
                        cvpj_instdata['plugindata']['length'] = it_singlesample['length']
                        cvpj_instdata['plugindata']['loop'] = {}
                        cvpj_instdata['plugindata']['loop']['enabled'] = int(it_singlesample['flags'][3])
                        cvpj_instdata['plugindata']['loop']['points'] = [it_singlesample['loop_start'],it_singlesample['loop_end']]

                else:
                    mscount = 0
                    ms_r = []
                    ms_r_c = None
                    for bn_s_t_e in bn_s_t:
                        if bn_s_t_e != ms_r_c: 
                            ms_r_c = bn_s_t_e
                            ms_r.append([ms_r_c[0], ms_r_c[1], 0])
                        ms_r[-1][2] += 1
                        mscount += 1

                    cvpj_instdata = {}
                    cvpj_instdata['plugin'] = 'sampler-multi'
                    cvpj_instdata['plugindata'] = {}
                    cvpj_instdata['plugindata']['point_value_type'] = "samples"
                    cvpj_instdata['plugindata']['regions'] = []

                    startpos = -60
                    for ms_r_e in ms_r:
                        region_note = ms_r_e[0]
                        region_inst = ms_r_e[1]
                        region_end = ms_r_e[2]+startpos-1

                        regionparams = {}
                        regionparams['r_key'] = [startpos, region_end]
                        regionparams['middlenote'] = region_note
                        regionparams['file'] = samplefolder + str(region_inst) + '.wav'
                        regionparams['start'] = 0
                        regionparams['end'] = 100000
                        regionparams['trigger'] = 'oneshot'
                        regionparams['loop'] = {}
                        regionparams['loop']['enabled'] = 0
                        cvpj_instdata['plugindata']['regions'].append(regionparams)

                        startpos += ms_r_e[2]

                if it_singleinst['filtercutoff'] != None and 'plugindata' in cvpj_instdata:
                    if it_singleinst['filtercutoff'] != 127:
                        plugdata = cvpj_instdata['plugindata']
                        plugdata['filter'] = {}
                        computedCutoff = (it_singleinst['filtercutoff'] * 512)
                        outputcutoff = 131.0 * pow(2.0, computedCutoff * (5.29 / (127.0 * 512.0)))
                        plugdata['filter']['cutoff'] = outputcutoff
                        if it_singleinst['filterresonance'] != None: plugdata['filter']['reso'] = (it_singleinst['filterresonance']/127)*6 + 1
                        else: plugdata['filter']['reso'] = 1
                        plugdata['filter']['type'] = "lowpass"
                        plugdata['filter']['wet'] = 1

                tracks.m_create_inst(cvpj_l, it_instname, cvpj_instdata)
                tracks.m_basicdata_inst(cvpj_l, it_instname, cvpj_instname, [0.71, 0.58, 0.47], 0.3, None)

                instrumentcount += 1
        if it_header_flag_useinst == 0:
            for IT_Sample in IT_Samples:
                it_samplename = startinststr + str(samplecount+1)
                it_singlesample = IT_Samples[IT_Sample]
                print(IT_Samples[IT_Sample])
                if it_singlesample['name'] != '': cvpj_instname = it_singlesample['name']
                elif it_singlesample['dosfilename'] != '': cvpj_instname = it_singlesample['dosfilename']
                else: cvpj_instname = " "
                cvpj_instdata = {}
                cvpj_instdata['plugin'] = 'sampler'
                cvpj_instdata['plugindata'] = {}
                cvpj_instdata['plugindata']['file'] = samplefolder + str(samplecount+1) + '.wav'
                if it_singlesample['length'] != 0:
                    cvpj_instdata['plugindata']['length'] = it_singlesample['length']
                    cvpj_instdata['plugindata']['loop'] = {}
                    cvpj_instdata['plugindata']['loop']['enabled'] = int(it_singlesample['flags'][3])
                    cvpj_instdata['plugindata']['loop']['points'] = [it_singlesample['loop_start'],it_singlesample['loop_end']]

                tracks.m_create_inst(cvpj_l, it_samplename, cvpj_instdata)
                tracks.m_basicdata_inst(cvpj_l, it_samplename, cvpj_instname, [0.71, 0.58, 0.47], 0.3, None)

                samplecount += 1

        patlentable = song_tracker.get_len_table(patterntable_all, table_orders)

        # ------------- Song Message -------------
        it_file.seek(it_header_msgoffset)
        it_songmessage = it_file.read(it_header_msglength).split(b'\x00' * 1)[0].decode("windows-1252")

        tracks.a_add_auto_pl(cvpj_l, 'main', None, 'bpm', song_tracker.tempo_auto(patterntable_all, table_orders, it_header_speed, it_header_tempo))

        cvpj_l['info'] = {}
        cvpj_l['info']['title'] = it_header_songname
        cvpj_l['info']['message'] = {}
        cvpj_l['info']['message']['type'] = 'text'
        cvpj_l['info']['message']['text'] = it_songmessage.replace('\r', '\n')

        cvpj_l['do_addwrap'] = True
        cvpj_l['do_lanefit'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        cvpj_l['timemarkers'] = placements.make_timemarkers([4,16], patlentable, None)

        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = it_header_tempo/(it_header_speed/6)
        return json.dumps(cvpj_l)

