# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import data_values

from functions_plugin import openmpt_chunks

from io import BytesIO
from objects import dv_trackerpattern

import math
import numpy as np
import os.path
import plugin_input
import struct

try: import xmodits
except: xmodits_exists = False
else: xmodits_exists = True

startinststr = 'it_inst_'
maincolor = [0.71, 0.58, 0.47]

class it_sample:
    def __init__(self, it_file, table_offset_sample, samplecount): 
        it_file.seek(table_offset_sample)
        if it_file.read(4) != b'IMPS':
            print('[input-it] Sample not Valid')
            exit()
        print("[input-it] Sample " + str(samplecount) + ': at offset ' + str(table_offset_sample))
        self.dosfilename = data_bytes.readstring_fixedlen(it_file, 12, "windows-1252")
        it_file.read(1)
        self.globalvol = it_file.read(1)[0]/64
        self.flags = bin(it_file.read(1)[0])[2:].zfill(8)
        self.defualtvolume = it_file.read(1)[0]/64
        self.name = data_bytes.readstring_fixedlen(it_file, 26, "windows-1252")
        it_file.read(2)
        self.length = int.from_bytes(it_file.read(4), "little")
        self.loop_start = int.from_bytes(it_file.read(4), "little")
        self.loop_end = int.from_bytes(it_file.read(4), "little")
        self.C5_speed = int.from_bytes(it_file.read(4), "little")
        self.susloop_start = int.from_bytes(it_file.read(4), "little")-1
        self.susloop_end = int.from_bytes(it_file.read(4), "little")-1
        self.sample_pointer = int.from_bytes(it_file.read(4), "little")
        self.vibrato_speed = it_file.read(1)[0]
        self.vibrato_depth = it_file.read(1)[0]
        self.vibrato_sweep = it_file.read(1)[0]
        self.vibrato_wave = it_file.read(1)[0]

    def vibrato_lfo(self, plugin_obj):
        vibrato_on = self.vibrato_sweep != 0 and self.vibrato_speed != 0
        if vibrato_on:
            vibrato_speed = 1/((256/self.vibrato_speed)/100)
            vibrato_depth = self.vibrato_depth/64
            vibrato_wave = ['sine','saw','square','random'][self.vibrato_wave&3]
            vibrato_sweep = (8192/self.vibrato_sweep)/50

            lfo_obj = plugin_obj.lfo_add('pitch')
            lfo_obj.attack = vibrato_sweep
            lfo_obj.shape = vibrato_wave
            lfo_obj.time.set_seconds(vibrato_speed)
            lfo_obj.amount = vibrato_depth

class it_instrument:
    def __init__(self, it_file, table_offset_inst, samplecount): 
        it_file.seek(table_offset_inst)
        if it_file.read(4) != b'IMPI':
            print('[input-it] Instrument not Valid')
            exit()
        print("[input-it] Instrument " + str(samplecount) + ": at offset " + str(table_offset_inst))
        self.dosfilename = data_bytes.readstring_fixedlen(it_file, 12, "windows-1252")
        it_file.read(1)
        self.newnoteaction = it_file.read(1)[0] # New Note Action
        self.duplicatechecktype = it_file.read(1)[0] # Duplicate Check Type
        self.duplicatecheckaction = it_file.read(1)[0] # Duplicate Check Action
        self.fadeout = int.from_bytes(it_file.read(2), "little") # FadeOut
        self.pitchpanseparation = int.from_bytes(it_file.read(1), "little", signed=True) # Pitch-Pan separation
        self.pitchpancenter = it_file.read(1)[0]-60 # Pitch-Pan center
        self.globalvol = it_file.read(1)[0]/128 # Global Volume
        inst_defaultpan = it_file.read(1)[0] # Default Pan
        self.defaultpan = (inst_defaultpan/32)-1 if inst_defaultpan < 128 else 0
        self.randomvariation_volume = it_file.read(1)[0]/100 # Random volume variation (percentage)
        self.randomvariation_pan = it_file.read(1)[0]/64 # Random pan variation (percentage)
        self.cwtv = int.from_bytes(it_file.read(2), "little") # TrkVers
        self.smpnum = it_file.read(1)[0] # Number of samples associated with instrument. 
        it_file.read(1)
        self.name = data_bytes.readstring_fixedlen(it_file, 26, "windows-1252")
        inst_filtercutoff = it_file.read(1)[0]
        inst_filterresonance = it_file.read(1)[0]
        it_inst_midi_chan = it_file.read(1)[0] # MIDI Channel
        it_inst_midi_inst = it_file.read(1)[0] # MIDI Program
        it_inst_midi_bank = int.from_bytes(it_file.read(2), "little") # MIDI Bank

        self.filtercutoff = inst_filtercutoff-128 if inst_filtercutoff >= 128 else None
        self.filterresonance = inst_filterresonance-128 if inst_filterresonance >= 128 else None
        self.midi_chan = it_inst_midi_chan if it_inst_midi_chan != 0 else None
        self.midi_inst = it_inst_midi_inst if it_inst_midi_inst != 255 else None
        self.midi_bank = it_inst_midi_bank if it_inst_midi_bank != 65535 else None

        self.notesampletable = []
        for _ in range(120):
            t_note = it_file.read(1)[0]-60
            t_sample = it_file.read(1)[0]
            self.notesampletable.append([t_note,t_sample])

        self.env_vol = it_env(it_file)
        self.env_pan = it_env(it_file)
        self.env_pitch = it_env(it_file)

        self.ramping = 0
        self.resampling = -1

        self.randomvariation_cutoff = 0
        self.randomvariation_reso = 0
        self.filtermode = 255
        self.pluginnum = 0


class it_env:
    def __init__(self, it_file): 
        env_flags = bin(it_file.read(1)[0])[2:].zfill(8)
        self.enabled = int(env_flags[7])
        self.loop_enabled = int(env_flags[6])
        self.susloop_enabled = int(env_flags[5])
        self.usefilter = int(env_flags[0])

        self.env_numpoints = it_file.read(1)[0]
        self.loop_start = it_file.read(1)[0]
        self.loop_end = it_file.read(1)[0]
        self.susloop_start = it_file.read(1)[0]
        self.susloop_end = it_file.read(1)[0]
        self.env_points = []
        for _ in range(self.env_numpoints):
            env_value = int.from_bytes(it_file.read(1), "little", signed=True)
            env_pos = int.from_bytes(it_file.read(2), "little")
            self.env_points.append([env_value, env_pos])
        it_file.read(76-(self.env_numpoints*3))

    def ext_ticks_pos(self, i_input):
        unpacked = struct.unpack('H'*(self.env_numpoints), i_input[0:self.env_numpoints*2])
        if self.env_numpoints != len(self.env_points): self.env_points = [[p, 0] for p in unpacked]
        else: 
            for c, v in enumerate(unpacked): self.env_points[c][0] = v

    def ext_ticks_val(self, i_input):
        unpacked = struct.unpack('B'*(self.env_numpoints), i_input[0:self.env_numpoints])
        if self.env_numpoints != len(self.env_points): self.env_points = [[0, v] for v in unpacked]
        else: 
            for c, v in enumerate(unpacked): self.env_points[c][1] = v

    def to_cvpj(self, plugin_obj, t_type, i_div): 
        autopoints_obj = plugin_obj.env_points_add(t_type, 48, False, 'float')
        autopoints_obj.sustain_on    = bool(self.susloop_enabled)
        autopoints_obj.sustain_point = self.susloop_start
        autopoints_obj.sustain_end   = self.susloop_end
        autopoints_obj.loop_on       = bool(self.loop_enabled)
        autopoints_obj.loop_start    = self.loop_start
        autopoints_obj.loop_end      = self.loop_end

        for pv, pp in self.env_points:
            autopoint_obj = autopoints_obj.add_point()
            autopoint_obj.pos = pp
            autopoint_obj.value = pv/i_div

        maxval = max([i[1]/i_div for i in self.env_points]) if self.env_points else 1
        return autopoints_obj, maxval


def get_name(inst_name, dosfilename):
    if inst_name != '': return inst_name
    elif dosfilename != '': return dosfilename
    else: return " "

def calc_filter_freq(i_cutoff):
    computedCutoff = (i_cutoff * 512)
    return 131.0 * pow(2.0, computedCutoff * (5.29 / (127.0 * 512.0)))

def add_filter(plugin_obj, i_cutoff, i_reso):
    if i_cutoff != None:
        if i_cutoff != 127:
            plugin_obj.filter.on = True
            plugin_obj.filter.freq = calc_filter_freq(i_cutoff)
            plugin_obj.filter.q = ((i_reso/127)*6 + 1) if i_reso != None else 1
            plugin_obj.filter.type = 'low_pass'

def add_single_sampler(convproj_obj, it_samp, sampleidnum):
    filename = samplefolder+str(sampleidnum)+'.wav'
    plugin_obj, pluginid, sampleref_obj = convproj_obj.add_plugin_sampler_genid(filename)
    plugin_obj.datavals.add('point_value_type', "samples")
    if it_samp.length != 0:
        cvpj_loop = {}
        cvpj_loop['enabled'] = int(it_samp.flags[3])
        cvpj_loop['mode'] = 'normal' if int(it_samp.flags[1]) == 0 else 'pingpong'
        if int(it_samp.flags[3]) != 0: cvpj_loop['points'] = [it_samp.loop_start,it_samp.loop_end]
        plugin_obj.datavals.add('loop', cvpj_loop)
    it_samp.vibrato_lfo(plugin_obj)
    return plugin_obj, pluginid, sampleref_obj

class input_it(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'it'
    def gettype(self): return 'm'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Impulse Tracker'
        dawinfo_obj.file_ext = 'it'
        dawinfo_obj.track_lanes = True
        dawinfo_obj.audio_filetypes = ['wav']
        dawinfo_obj.plugin_included = ['sampler:single', 'sampler:multi']
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytesdata = bytestream.read(4)
        if bytesdata == b'IMPM': return True
        else: return False
        bytestream.seek(0)

    def parse(self, convproj_obj, input_file, dv_config):
        global samplefolder
        global dataset

        it_file = open(input_file, 'rb')

        samplefolder = dv_config.path_samples_extracted
        
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
        
        it_header_cwtv = data_bytes.splitbyte(it_file.read(1)[0])+data_bytes.splitbyte(it_file.read(1)[0])
        it_header_cmwt = it_file.read(2)
        print("[input-it] Cwt/v: " + str(it_header_cwtv))
        
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

        endpos = it_file.tell()

        pntstart = table_offset_insts[0] if table_offset_insts else 0
        extrasize = max(0, pntstart-endpos)
        extradata = it_file.read(extrasize)

        extradata = BytesIO(extradata)

        unknown_amount = int.from_bytes(extradata.read(2), "little")
        unknown_data = [extradata.read(8) for x in range(unknown_amount)]

        patnames, channames = openmpt_chunks.parse_start(extradata, convproj_obj)

        # ------------- Orders -------------
        while 254 in table_orders: table_orders.remove(254)
        while 255 in table_orders: table_orders.remove(255)
        print("[input-it] Order List: " + str(table_orders))
        
        # ------------- Instruments -------------
        it_insts = [it_instrument(it_file, x, c) for c, x in enumerate(table_offset_insts)]

        # ------------- Samples -------------
        it_samples = [it_sample(it_file, x, c) for c, x in enumerate(table_offset_samples)]
        
        if xmodits_exists == True:
            if not os.path.exists(samplefolder): os.makedirs(samplefolder)
            try: xmodits.dump(input_file, samplefolder, index_only=True, index_raw=True, index_padding=0)
            except: pass

        # ------------- Pattern -------------
        patterndata = dv_trackerpattern.patterndata(64, startinststr, maincolor)

        for patterncount, table_offset_pattern in enumerate(table_offset_patterns):

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

        #print([x.sample_pointer for x in it_samples])

        extension_name = b''

        #while True:
        #    extension_name = it_file.read(4)
        #    if extension_name == b'': break
        #    if extension_name in [b'XTPM', b'STPM']: 
        #        it_file.seek(it_file.tell()-4)
        #        break
        #    it_file.seek(it_file.tell()-3)

        XTPM_data, STPM_data = openmpt_chunks.parse_xtst(it_file, it_header_insnum)

        #print(XTPM_data, STPM_data)

        for n, d in enumerate(XTPM_data):
            for c, v in d:
                if c == b'..OF': it_insts[n].fadeout = int.from_bytes(v, "little")
                elif c == b'...P': pass
                elif c == b'..EV': it_insts[n].env_vol.env_numpoints = int.from_bytes(v, "little")
                elif c == b'..EP': it_insts[n].env_pan.env_numpoints = int.from_bytes(v, "little")
                elif c == b'.EiP': it_insts[n].env_pitch.env_numpoints = int.from_bytes(v, "little")
                elif c == b'.[PV': it_insts[n].env_vol.ext_ticks_pos(v)
                elif c == b'.[EV': it_insts[n].env_vol.ext_ticks_val(v)
                elif c == b'.[PP': it_insts[n].env_pan.ext_ticks_pos(v)
                elif c == b'.[EP': it_insts[n].env_pan.ext_ticks_val(v)
                elif c == b'[PiP': it_insts[n].env_pitch.ext_ticks_pos(v)
                elif c == b'[EiP': it_insts[n].env_pitch.ext_ticks_val(v)
                elif c == b'..RV': it_insts[n].ramping = int.from_bytes(v, "little")
                elif c == b'...R': it_insts[n].resampling = v[0]
                elif c == b'.PiM': it_insts[n].pluginnum = v[0]
                elif c == b'..SC': it_insts[n].randomvariation_cutoff = v[0]
                elif c == b'..SR': it_insts[n].randomvariation_reso = v[0]
                elif c == b'..MF': it_insts[n].filtermode = v[0]

        for c, d in enumerate(STPM_data):
            if c == b'...C': patterndata.num_chans = int.from_bytes(chunk_value, "little")
            elif c == b'AUTH': convproj_obj.metadata.author = chunk_value.decode()
            elif c == b'CCOL': patterndata.ch_colors = d

        if channames:
            for n, v in enumerate(channames):
                patterndata.ch_names[n] = v

        if patnames:
            for n, v in enumerate(patnames):
                patterndata.pat_names[n] = v

        patterndata.to_cvpj(convproj_obj, table_orders, startinststr, it_header_tempo, it_header_speed, maincolor)

        for n in range(64):
            ch_pan = ((table_chnpan[n]&127)/32)-1
            ch_mute = bool(table_chnpan[n]&128)
            ch_vol = table_chnvol[n]/64
            if n in convproj_obj.playlist:
                s_pl = convproj_obj.playlist[n]
                if ch_pan != 2.125: s_pl.params.add('pan', ch_pan, 'float')
                s_pl.params.add('vol', ch_vol, 'float')
                s_pl.params.add('on', not ch_mute, 'bool')

        track_volume = 0.3

        it_header_flag_useinst = int(it_header_flag_useinst)
        if it_header_flag_useinst == 1:
            for instrumentcount, it_inst in enumerate(it_insts):
                it_instname = startinststr + str(instrumentcount+1)
                
                cvpj_instname = get_name(it_inst.name, it_inst.dosfilename)

                n_s_t = it_inst.notesampletable
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

                if bn_s_t_ifsame:
                    if (not ''.join(list(map(lambda x: x.strip(), cvpj_instname.split())))):
                        inst_obj.visual.name = it_samples[bn_s_t_f[1]-1].name
                        if not inst_obj.visual.name: 
                            inst_obj.visual.name = it_samples[bn_s_t_f[1]-1].dosfilename

                if it_inst.pitchpanseparation:
                    plugin_obj, pluginid = convproj_obj.add_plugin_genid('pitch_pan_separation', None)
                    plugin_obj.params.add('range', 1/(it_inst.pitchpanseparation/32), 'float')
                    plugin_obj.datavals.add('center_note', it_inst.pitchpancenter)
                    inst_obj.fxslots_notes.append(pluginid)

                if it_inst.randomvariation_volume:
                    plugin_obj, pluginid = convproj_obj.add_plugin_genid('random_variation', 'vol')
                    plugin_obj.params.add('amount', it_inst.randomvariation_volume, 'float')
                    inst_obj.fxslots_notes.append(pluginid)

                if it_inst.randomvariation_pan:
                    plugin_obj, pluginid = convproj_obj.add_plugin_genid('random_variation', 'pan')
                    plugin_obj.params.add('amount', it_inst.randomvariation_pan, 'float')
                    inst_obj.fxslots_notes.append(pluginid)

                inst_used = False
                if bn_s_t_ifsame == True:

                    if bn_s_t_f[1]-1 < len(it_samples):
                        it_samp = it_samples[bn_s_t_f[1]-1]
                        track_volume = 0.3*it_inst.globalvol*it_samp.defualtvolume*it_samp.globalvol
                        plugin_obj, inst_obj.pluginid, sampleref_obj = add_single_sampler(convproj_obj, it_samp, bn_s_t_f[1])
                        inst_used = True
                else:
                    inst_used = True
                    sampleregions = data_values.list_to_reigons(bn_s_t, 60)

                    plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('sampler', 'multi')
                    plugin_obj.datavals.add('point_value_type', "samples")

                    for sampleregion in sampleregions:
                        instrumentnum = sampleregion[0][1]

                        filename = samplefolder + str(instrumentnum) + '.wav'
                        sampleref_obj = convproj_obj.add_sampleref(filename, filename)
                        regionparams = {}
                        regionparams['middlenote'] = sampleregion[0][0]*-1
                        regionparams['sampleref'] = filename
                        if instrumentnum-1 <= len(it_samples):
                            it_samp = it_samples[instrumentnum-1]
                            regionparams['loop'] = {}
                            regionparams['loop']['enabled'] = int(it_samp.flags[3])
                            regionparams['loop']['points'] = [it_samp.loop_start,it_samp.loop_end]
                        plugin_obj.regions.add(sampleregion[1], sampleregion[2], regionparams)

                if inst_used:
                    if it_inst.resampling != -1:
                        interpolation = 'none'
                        if it_inst.resampling == 1: interpolation = 'linear'
                        if it_inst.resampling == 2: interpolation = 'cubic_spline'
                        if it_inst.resampling == 3: interpolation = 'sinc'
                        if it_inst.resampling == 4: interpolation = 'sinc_lowpass'
                        plugin_obj.datavals.add('interpolation', interpolation)
                    else:
                        plugin_obj.datavals.add('interpolation', 'linear')

                if it_inst.midi_chan != None: 
                    inst_obj.midi.out_enabled = 1
                    inst_obj.midi.out_chan = it_inst.midi_chan+1
                if it_inst.midi_inst != None: inst_obj.midi.out_patch = it_inst.midi_inst+1
                if it_inst.midi_bank != None: inst_obj.midi.out_bank = it_inst.midi_bank+1

                if inst_used:
                    autopoints_obj, maxvol = it_inst.env_vol.to_cvpj(plugin_obj, 'vol', 48)
                    if it_inst.fadeout != 0: autopoints_obj.data['fadeout'] = (256/it_inst.fadeout)/8
                    autopoints_obj, _ = it_inst.env_pan.to_cvpj(plugin_obj, 'pan', 48)
                    if it_inst.env_pitch.usefilter: 
                        it_inst.env_pitch.env_points = [[calc_filter_freq(pv), pp] for pv, pp in it_inst.env_pitch.env_points]
                        autopoints_obj, _ = it_inst.env_pitch.to_cvpj(plugin_obj, 'cutoff', 1)
                    else:
                        autopoints_obj, _ = it_inst.env_pitch.to_cvpj(plugin_obj, 'pitch', 48)

                    if not (it_inst.env_pitch.enabled and it_inst.env_pitch.usefilter): 
                        add_filter(plugin_obj, it_inst.filtercutoff, it_inst.filterresonance)

                    plugin_obj.env_asdr_from_points('vol')

                if it_inst.filtermode == 1: plugin_obj.filter.type = 'high_pass'

                if it_inst.pluginnum: inst_obj.fxslots_audio.append('FX'+str(it_inst.pluginnum))

                inst_obj.params.add('vol', track_volume, 'float')
                inst_obj.params.add('pan', it_inst.defaultpan, 'float')

        #exit()

        if it_header_flag_useinst == 0:
            for samplecount, it_samp in enumerate(it_samples):
                it_instname = startinststr + str(samplecount+1)
                cvpj_instname = get_name(it_samp.name, it_samp.dosfilename)
                track_volume = 0.3*it_samp.defualtvolume*it_samp.globalvol

                inst_obj = convproj_obj.add_instrument(it_instname)
                inst_obj.visual.name = cvpj_instname
                inst_obj.visual.color = maincolor
                plugin_obj, inst_obj.pluginid, sampleref_obj = add_single_sampler(convproj_obj, it_samp, samplecount+1)
                inst_obj.params.add('vol', track_volume, 'float')

        convproj_obj.track_master.params.add('vol', it_header_globalvol/128, 'float')

        # ------------- Song Message -------------
        it_file.seek(it_header_msgoffset)
        it_songmessage = data_bytes.readstring_fixedlen_nofix(it_file, it_header_msglength, "windows-1252")

        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_lanefit')
        convproj_obj.params.add('bpm', it_header_tempo/(it_header_speed/6), 'float')

        convproj_obj.metadata.name = it_header_songname
        convproj_obj.metadata.comment_text = it_songmessage