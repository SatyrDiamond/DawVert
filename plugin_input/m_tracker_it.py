# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import math
import struct
import numpy as np
from functions import audio_wav
from functions import data_values
from functions import data_bytes
from objects import dv_trackerpattern

try: import xmodits
except: xmodits_exists = False
else: xmodits_exists = True

startinststr = 'IT_Inst_'
maincolor = [0.71, 0.58, 0.47]

def get_name(inst_name, dosfilename):
    if inst_name != '': return inst_name
    elif dosfilename != '': return dosfilename
    else: return " "

def add_filter(plugin_obj, i_cutoff, i_reso):
    if i_cutoff != None:
        if i_cutoff != 127:
            computedCutoff = (i_cutoff * 512)
            plugin_obj.filter.on = True
            plugin_obj.filter.freq = 131.0 * pow(2.0, computedCutoff * (5.29 / (127.0 * 512.0)))
            plugin_obj.filter.q = ((i_reso/127)*6 + 1) if i_reso != None else 1
            plugin_obj.filter.type = 'low_pass'


def add_single_sampler(convproj_obj, sampledata, sampleidnum):
    filename = samplefolder+str(sampleidnum)+'.wav'
    plugin_obj, pluginid, sampleref_obj = convproj_obj.add_plugin_sampler_genid(filename)
    plugin_obj.datavals.add('point_value_type', "samples")
    if sampledata['length'] != 0:
        cvpj_loop = {}
        cvpj_loop['enabled'] = int(sampledata['flags'][3])
        cvpj_loop['mode'] = 'normal' if int(sampledata['flags'][1]) == 0 else 'pingpong'
        if int(sampledata['flags'][3]) != 0: cvpj_loop['points'] = [sampledata['loop_start'],sampledata['loop_end']]
        plugin_obj.datavals.add('loop', cvpj_loop)
    return plugin_obj, pluginid, sampleref_obj

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

    def parse(self, convproj_obj, input_file, extra_param):
        global samplefolder
        it_file = open(input_file, 'rb')

        samplefolder = extra_param['samplefolder']
        
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
        patterncount = 0

        patterndata = dv_trackerpattern.patterndata(64, startinststr, maincolor)

        for table_offset_pattern in table_offset_patterns:

            if table_offset_pattern != 0:
                print("[input-it] Pattern " + str(patterncount),end=': ')
                it_file.seek(table_offset_pattern)
                pattern_length = int.from_bytes(it_file.read(2), "little")
                pattern_rows = int.from_bytes(it_file.read(2), "little")
                print(str(pattern_rows) + ' Rows',end=', ')
                print('Size: ' + str(pattern_length) + ' at offset ' + str(table_offset_pattern))
                patterndata.pattern_add(patterncount, pattern_rows)
                it_file.read(4)
                rowcount = 0
                table_lastnote = [None for _ in range(64)]
                table_lastinstrument = [None for _ in range(64)]
                table_lastvolpan = [None for _ in range(64)]
                table_lastcommand = [[None, None] for _ in range(64)]
                table_previousmaskvariable = [None for _ in range(64)]
                for _ in range(pattern_rows):
                    pattern_done = 0

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

                            out_note = None
                            out_inst = None
                            out_vol = 64
                            out_pan = None

                            if cell_volpan != None:
                                if cell_volpan <= 64: out_vol = cell_volpan
                                elif 192 >= cell_volpan >= 128: out_pan = ((cell_volpan-128)/64-0.5)*2
        
                            if cell_note != None: out_note = cell_note - 60
                            if cell_note == 254: out_note = 'cut'
                            if cell_note == 255: out_note = 'off'
                            if cell_note == 246: out_note = 'fade'
        
                            if cell_instrument != None: out_inst = cell_instrument
                        
                            patterndata.cell_note(cell_channel, out_note, out_inst)
                            patterndata.cell_param(cell_channel, 'vol', out_vol/64)
                            if out_pan != None: patterndata.cell_param(cell_channel, 'pan', out_pan)

                            patterndata.cell_fx_s3m(cell_channel, cell_commandtype, cell_commandval)

                            if cell_commandtype == 20: patterndata.cell_g_param('tempo', cell_commandval)
                            if cell_commandtype == 26: patterndata.cell_param(cell_channel, 'pan', ((cell_commandval/255)-0.5)*2)
                    patterndata.row_next()

            patterncount += 1

        patterndata.to_cvpj(convproj_obj, table_orders, startinststr, it_header_tempo, it_header_speed, maincolor)

        instrumentcount = 0
        samplecount = 0

        track_volume = 0.3

        it_header_flag_useinst = int(it_header_flag_useinst)
        if it_header_flag_useinst == 1:
            for IT_Inst in IT_Insts:
                it_instname = startinststr + str(instrumentcount+1)
                it_singleinst = IT_Insts[IT_Inst]
                
                cvpj_instname = get_name(it_singleinst['name'], it_singleinst['dosfilename'])

                n_s_t = it_singleinst['notesampletable']
                bn_s_t = []

                basenoteadd = 60
                for n_s_te in n_s_t:
                    bn_s_t.append([n_s_te[0]+basenoteadd, n_s_te[1]])
                    basenoteadd -= 1

                bn_s_t_ifsame = data_values.ifallsame(bn_s_t)
                if bn_s_t_ifsame: bn_s_t_f = bn_s_t[0]

                bn_s_t_ifsame = data_values.ifallsame(bn_s_t[12:108])
                if bn_s_t_ifsame: bn_s_t_f = bn_s_t[12]

                inst_obj = convproj_obj.add_instrument(it_instname)
                inst_obj.visual.name = cvpj_instname
                inst_obj.visual.color = maincolor

                inst_used = False
                if bn_s_t_ifsame == True and str(bn_s_t_f[1]-1) in IT_Samples:
                    inst_used = True
                    it_singlesample = IT_Samples[str(bn_s_t_f[1]-1)]
                    track_volume = 0.3*it_singleinst['globalvol']*it_singlesample['defualtvolume']*it_singlesample['globalvol']
                    plugin_obj, inst_obj.pluginid, sampleref_obj = add_single_sampler(convproj_obj, it_singlesample, bn_s_t_f[1])
                else:
                    inst_used = True
                    sampleregions = data_values.list_to_reigons(bn_s_t, 60)

                    plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('sampler', 'multi')
                    plugin_obj.datavals.add('point_value_type', "samples")

                    for sampleregion in sampleregions:
                        instrumentnum = sampleregion[0][1]

                        if str(instrumentnum-1) in IT_Samples:
                            it_singlesample = IT_Samples[str(instrumentnum-1)]
                            filename = samplefolder + str(instrumentnum) + '.wav'
                            sampleref_obj = convproj_obj.add_sampleref(filename, filename)
                            regionparams = {}
                            regionparams['middlenote'] = sampleregion[0][0]*-1
                            regionparams['sampleref'] = filename
                            regionparams['loop'] = {}
                            regionparams['loop']['enabled'] = int(it_singlesample['flags'][3])
                            regionparams['loop']['points'] = [it_singlesample['loop_start'],it_singlesample['loop_end']]
                            plugin_obj.regions.add(sampleregion[1], sampleregion[2], regionparams)

                if 'midi_chan' in it_singleinst: 
                    inst_obj.midi.out_enabled = 1
                    inst_obj.midi.out_chan = it_singleinst['midi_chan']+1
                if 'midi_inst' in it_singleinst: inst_obj.midi.out_patch = it_singleinst['midi_inst']+1
                if 'midi_bank' in it_singleinst: inst_obj.midi.out_bank = it_singleinst['midi_bank']+1

                filterenv_used = False

                if inst_used:
                    for envtype in ['vol', 'pan', 'pitch']:
                        envvarname = 'env_'+envtype
                        envvardata = it_singleinst[envvarname]
                        susenabled = envvardata['susloop_enabled']
                    
                        if envvarname in it_singleinst: 

                            if envtype == 'vol': 
                                autopoints_obj = plugin_obj.env_points_add('vol', 48, False, 'float')
                                track_volume *= max([i['value']/64 for i in envvardata['points']])
    
                                if it_singleinst['fadeout'] != 0:
                                    autopoints_obj.data['fadeout'] = (256/it_singleinst['fadeout'])/8

                            if envtype == 'pan': autopoints_obj = plugin_obj.env_points_add('pan', 48, False, 'float')
                            if envtype == 'pitch': 
                                if envvardata['usepitch'] != 1: autopoints_obj = plugin_obj.env_points_add('pitch', 48, False, 'float')
                                else: autopoints_obj = plugin_obj.env_points_add('cutoff', 48, False, 'float')

                            if susenabled == 1: autopoints_obj.data['sustain'] = envvardata['susloop_start']+1

                            for itpd in envvardata['points']:
                                autopoint_obj = autopoints_obj.add_point()
                                autopoint_obj.pos = itpd['pos']
                                if envtype == 'vol': autopoint_obj.value = itpd['value']/64
                                if envtype == 'pan': autopoint_obj.value = itpd['value']/32
                                if envtype == 'pitch': 
                                    if envvardata['usepitch'] != 1: autopoint_obj.value = itpd['value']
                                    else: 
                                        autopoint_obj.value = itpd['value']/64
                                        filterenv_used = True

                    if filterenv_used == False:
                        add_filter(plugin_obj, it_singleinst['filtercutoff'], it_singleinst['filterresonance'])

                    plugin_obj.env_asdr_from_points('vol')
                    plugin_obj.env_asdr_from_points('cutoff')

                inst_obj.params.add('vol', track_volume, 'float')

                instrumentcount += 1


        if it_header_flag_useinst == 0:
            for IT_Sample in IT_Samples:
                it_instname = startinststr + str(samplecount+1)
                it_singlesample = IT_Samples[IT_Sample]
                cvpj_instname = get_name(it_singlesample['name'], it_singlesample['dosfilename'])
                track_volume = 0.3*it_singlesample['defualtvolume']*it_singlesample['globalvol']
                pluginid = plugins.get_id()

                inst_obj = convproj_obj.add_instrument(it_instname)
                inst_obj.visual.name = cvpj_instname
                inst_obj.visual.color = maincolor
                plugin_obj, inst_obj.pluginid, sampleref_obj = add_single_sampler(convproj_obj, it_singlesample, samplecount+1)
                inst_obj.params.add('vol', track_volume, 'float')
                samplecount += 1

        # ------------- Song Message -------------
        it_file.seek(it_header_msgoffset)
        it_songmessage = data_bytes.readstring_fixedlen(it_file, it_header_msglength, "windows-1252")

        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_lanefit')
        convproj_obj.params.add('bpm', it_header_tempo/(it_header_speed/6), 'float')

        convproj_obj.metadata.name = it_header_songname
        convproj_obj.metadata.comment_text = it_songmessage.replace('\r', '\n')