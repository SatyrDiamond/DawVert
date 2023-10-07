# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import math
import json
import struct
import numpy as np
from functions import song_tracker
from functions import song_tracker_fx_s3m
from functions import audio_wav
from functions import data_values
from functions import placements
from functions import plugins
from functions import data_bytes
from functions import song
from functions_tracks import tracks_mi
from functions_tracks import auto_data

try: import xmodits
except: xmodits_exists = False
else: xmodits_exists = True

startinststr = 'IT_Inst_'

class input_it(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'it'
    def getname(self): return 'Impulse Tracker'
    def gettype(self): return 'm'
    def getdawcapabilities(self): 
        return {
        'samples_inside': True,
        'track_lanes': True
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

        samplefolder = extra_param['samplefolder']
        
        cvpj_l = {}

        it_header_magic = it_file.read(4)
        if it_header_magic != b'IMPM':
            print('[error] Not an IT File')
            exit()
        
        it_header_songname = data_bytes.readstring_fixedlen(it_file, 26, "windows-1252")
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
            it_singleinst['dosfilename'] = data_bytes.readstring_fixedlen(it_file, 12, "windows-1252")
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
            it_singleinst['name'] = data_bytes.readstring_fixedlen(it_file, 26, "windows-1252")
            inst_filtercutoff = it_file.read(1)[0]
            it_singleinst['filtercutoff'] = inst_filtercutoff-128 if inst_filtercutoff >= 128 else None
            inst_filterresonance = it_file.read(1)[0]
            it_singleinst['filterresonance'] = inst_filterresonance-128 if inst_filterresonance >= 128 else None
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
                env_out['enabled'] = int(env_flags[7])
                env_out['loop_enabled'] = int(env_flags[6])
                env_out['susloop_enabled'] = int(env_flags[5])
                env_out['usepitch'] = int(env_flags[0])

                env_numpoints = it_file.read(1)[0]
                env_out['loop_start'] = it_file.read(1)[0]
                env_out['loop_end'] = it_file.read(1)[0]
                env_out['susloop_start'] = it_file.read(1)[0]
                env_out['susloop_end'] = it_file.read(1)[0]
                env_points = []
                for _ in range(env_numpoints):
                    env_point = {}
                    env_point['value'] = int.from_bytes(it_file.read(1), "little", signed=True)
                    env_point['pos'] = int.from_bytes(it_file.read(2), "little")
                    env_points.append(env_point)
                env_data = {}
                env_out['points'] = env_points
                if env_type == 0: it_singleinst['env_vol'] = env_out
                if env_type == 1: it_singleinst['env_pan'] = env_out
                if env_type == 2: it_singleinst['env_pitch'] = env_out
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
            it_singlesample['dosfilename'] = data_bytes.readstring_fixedlen(it_file, 12, "windows-1252")
            it_file.read(1)
            it_singlesample['globalvol'] = it_file.read(1)[0]/64
            it_singlesample['flags'] = bin(it_file.read(1)[0])[2:].zfill(8)
            it_singlesample['defualtvolume'] = it_file.read(1)[0]/64
            it_singlesample['name'] = data_bytes.readstring_fixedlen(it_file, 26, "windows-1252")
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
                table_lastnote = [None for _ in range(64)]
                table_lastinstrument = [None for _ in range(64)]
                table_lastvolpan = [None for _ in range(64)]
                table_lastcommand = [[None, None] for _ in range(64)]
                table_previousmaskvariable = [None for _ in range(64)]
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

                            current_speed = song_tracker_fx_s3m.do_fx(current_speed, pattern_row[0], j_note_cmdval, cell_commandtype, cell_commandval)
                            if cell_commandtype == 20: pattern_row[0]['tempo'] = cell_commandval
                            if cell_commandtype == 26: j_note_cmdval['pan'] = ((cell_commandval/255)-0.5)*2
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

        track_volume = 0.3

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

                pluginid = plugins.get_id()

                if bn_s_t_ifsame == True and str(bn_s_t_f[1]-1) in IT_Samples:
                    it_singlesample = IT_Samples[str(bn_s_t_f[1]-1)]

                    track_volume = 0.3*it_singleinst['globalvol']*it_singlesample['defualtvolume']*it_singlesample['globalvol']

                    plugins.add_plug_sampler_singlefile(cvpj_l, pluginid, samplefolder+str(bn_s_t_f[1])+'.wav')
                    plugins.add_plug_data(cvpj_l, pluginid, 'trigger', 'normal')
                    plugins.add_plug_data(cvpj_l, pluginid, 'point_value_type', "samples")

                    if it_singlesample['length'] != 0:
                        plugins.add_plug_data(cvpj_l, pluginid, 'length', it_singlesample['length'])
                        cvpj_loop = {}
                        cvpj_loop['enabled'] = int(it_singlesample['flags'][3])
                        if int(it_singlesample['flags'][1]) == 0: cvpj_loop['mode'] = 'normal'
                        else: cvpj_loop['mode'] = 'pingpong'
                        if int(it_singlesample['flags'][3]) != 0:
                            cvpj_loop['points'] = [it_singlesample['loop_start'],it_singlesample['loop_end']]
                        plugins.add_plug_data(cvpj_l, pluginid, 'loop', cvpj_loop)
                else:
                    sampleregions = data_values.list_to_reigons(bn_s_t, 60)
                    plugins.add_plug_multisampler(cvpj_l, pluginid)
                    plugins.add_plug_data(cvpj_l, pluginid, 'point_value_type', "samples")

                    for sampleregion in sampleregions:
                        instrumentnum = sampleregion[0][1]

                        if str(instrumentnum-1) in IT_Samples:
                            it_singlesample = IT_Samples[str(instrumentnum-1)]
                            regionparams = {}
                            regionparams['r_key'] = [sampleregion[1], sampleregion[2]]
                            regionparams['middlenote'] = sampleregion[0][0]*-1
                            regionparams['file'] = samplefolder + str(instrumentnum) + '.wav'
                            regionparams['start'] = 0
                            regionparams['end'] = it_singlesample['length']
                            regionparams['trigger'] = 'oneshot'
                            regionparams['loop'] = {}
                            regionparams['loop']['enabled'] = int(it_singlesample['flags'][3])
                            regionparams['loop']['points'] = [it_singlesample['loop_start'],it_singlesample['loop_end']]
                            plugins.add_plug_multisampler_region(cvpj_l, pluginid, regionparams)

                if it_singleinst['filtercutoff'] != None:
                    if it_singleinst['filtercutoff'] != 127:
                        computedCutoff = (it_singleinst['filtercutoff'] * 512)
                        outputcutoff = 131.0 * pow(2.0, computedCutoff * (5.29 / (127.0 * 512.0)))
                        if it_singleinst['filterresonance'] != None: outputreso = (it_singleinst['filterresonance']/127)*6 + 1
                        else: outputreso = 1
                        plugins.add_filter(cvpj_l, pluginid, True, outputcutoff, outputreso, "lowpass", None)

                tracks_mi.inst_create(cvpj_l, it_instname)
                tracks_mi.inst_visual(cvpj_l, it_instname, name=cvpj_instname, color=[0.71, 0.58, 0.47])
                tracks_mi.inst_pluginid(cvpj_l, it_instname, pluginid)

                cvpj_instdata_midiout = {}
                if 'midi_chan' in it_singleinst: 
                    cvpj_instdata_midiout['enabled'] = 1
                    cvpj_instdata_midiout['channel'] = it_singleinst['midi_chan']+1
                if 'midi_inst' in it_singleinst: cvpj_instdata_midiout['program'] = it_singleinst['midi_inst']+1
                if 'midi_bank' in it_singleinst: cvpj_instdata_midiout['bank'] = it_singleinst['midi_bank']+1
                tracks_mi.inst_dataval_add(cvpj_l, it_instname, 'midi', 'output', cvpj_instdata_midiout)

                filterenv_used = False

                for envtype in ['vol', 'pan', 'pitch']:
                    envvarname = 'env_'+envtype
                    envvardata = it_singleinst[envvarname]

                    susenabled = envvardata['susloop_enabled']
                    
                    if envvarname in it_singleinst: 
                        if envtype == 'vol' and len(envvardata['points']) != 0:
                            track_volume *= max([i['value']/64 for i in envvardata['points']])
                        for itpd in envvardata['points']:
                            if envtype == 'vol': 
                                plugins.add_env_point(cvpj_l, pluginid, 'vol', itpd['pos']/48, itpd['value']/64)
                                if susenabled == 1: plugins.add_env_point_var(cvpj_l, pluginid, 'vol', 'sustain', envvardata['susloop_start']+1)
                            if envtype == 'pan': 
                                plugins.add_env_point(cvpj_l, pluginid, 'pan', itpd['pos']/48, (itpd['value'])/32)
                                if susenabled == 1: plugins.add_env_point_var(cvpj_l, pluginid, 'pan', 'sustain', envvardata['susloop_start']+1)
                            if envtype == 'pitch': 
                                if envvardata['usepitch'] != 1:
                                    plugins.add_env_point(cvpj_l, pluginid, 'pitch', itpd['pos']/48, (itpd['value']))
                                    if susenabled == 1: plugins.add_env_point_var(cvpj_l, pluginid, 'pitch', 'sustain', envvardata['susloop_start']+1)
                                else:
                                    plugins.add_env_point(cvpj_l, pluginid, 'cutoff', itpd['pos']/48, (itpd['value']/64))
                                    if susenabled == 1: plugins.add_env_point_var(cvpj_l, pluginid, 'cutoff', 'sustain', envvardata['susloop_start']+1)
                                    filterenv_used = True

                if it_singleinst['fadeout'] != 0:
                    plugins.add_env_point_var(cvpj_l, pluginid, 'vol', 'fadeout', (256/it_singleinst['fadeout'])/8)

                if filterenv_used == False:
                    if it_singleinst['filtercutoff'] != None:
                        if it_singleinst['filtercutoff'] != 127:
                            computedCutoff = (it_singleinst['filtercutoff'] * 512)
                            outputcutoff = 131.0 * pow(2.0, computedCutoff * (5.29 / (127.0 * 512.0)))
                            if it_singleinst['filterresonance'] != None: outputreso = (it_singleinst['filterresonance']/127)*6 + 1
                            else: outputreso = 1
                            plugins.add_filter(cvpj_l, pluginid, True, outputcutoff, outputreso, "lowpass", None)
                #else:
                #    if it_singleinst['filterresonance'] != None: outputreso = (it_singleinst['filterresonance']/127)*6 + 1
                #    else: outputreso = 0
                #    plugins.add_filter(cvpj_l, pluginid, True, 0, outputreso, "lowpass", None)

                plugins.env_point_to_asdr(cvpj_l, pluginid, 'vol')
                plugins.env_point_to_asdr(cvpj_l, pluginid, 'cutoff')
                tracks_mi.inst_param_add(cvpj_l, it_instname, 'vol', track_volume, 'float')

                instrumentcount += 1
        if it_header_flag_useinst == 0:
            for IT_Sample in IT_Samples:
                it_instname = startinststr + str(samplecount+1)
                it_singlesample = IT_Samples[IT_Sample]
                if it_singlesample['name'] != '': cvpj_instname = it_singlesample['name']
                elif it_singlesample['dosfilename'] != '': cvpj_instname = it_singlesample['dosfilename']
                else: cvpj_instname = " "

                track_volume = 0.3*it_singlesample['defualtvolume']*it_singlesample['globalvol']

                pluginid = plugins.get_id()
                plugins.add_plug_sampler_singlefile(cvpj_l, pluginid, samplefolder+str(samplecount+1)+'.wav')
                plugins.add_plug_data(cvpj_l, pluginid, 'trigger', 'normal')
                plugins.add_plug_data(cvpj_l, pluginid, 'point_value_type', "samples")
                if it_singlesample['length'] != 0:
                    plugins.add_plug_data(cvpj_l, pluginid, 'length', it_singlesample['length'])
                    cvpj_loop = {}
                    cvpj_loop['enabled'] = int(it_singlesample['flags'][3])
                    if int(it_singlesample['flags'][1]) == 0: cvpj_loop['mode'] = 'normal'
                    else: cvpj_loop['mode'] = 'pingpong'
                    if int(it_singlesample['flags'][3]) != 0:
                        cvpj_loop['points'] = [it_singlesample['loop_start'],it_singlesample['loop_end']]

                    plugins.add_plug_data(cvpj_l, pluginid, 'loop', cvpj_loop)

                tracks_mi.inst_create(cvpj_l, it_instname)
                tracks_mi.inst_visual(cvpj_l, it_instname, name=cvpj_instname, color=[0.71, 0.58, 0.47])
                tracks_mi.inst_pluginid(cvpj_l, it_instname, pluginid)
                tracks_mi.inst_param_add(cvpj_l, it_instname, 'vol', track_volume, 'float')

                samplecount += 1

        patlentable = song_tracker.get_len_table(patterntable_all, table_orders)

        # ------------- Song Message -------------
        it_file.seek(it_header_msgoffset)
        it_songmessage = data_bytes.readstring_fixedlen(it_file, it_header_msglength, "windows-1252")

        auto_data.add_pl(cvpj_l, 'float', ['main', 'bpm'], song_tracker.tempo_auto(patterntable_all, table_orders, it_header_speed, it_header_tempo))
        placements.make_timemarkers(cvpj_l, [4,16], patlentable, None)
        song.add_info(cvpj_l, 'title', it_header_songname)
        song.add_info_msg(cvpj_l, 'text', it_songmessage.replace('\r', '\n'))

        cvpj_l['do_addloop'] = True
        cvpj_l['do_lanefit'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False

        cvpj_l['playlist'] = cvpj_l_playlist
        song.add_param(cvpj_l, 'bpm', it_header_tempo/(it_header_speed/6))
        return json.dumps(cvpj_l)

