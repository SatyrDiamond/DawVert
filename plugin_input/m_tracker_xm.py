# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import json
import struct
from functions import data_values
from functions import data_bytes
from functions_plugin import openmpt_chunks
from io import BytesIO
from objects import dv_trackerpattern

try: import xmodits
except: xmodits_exists = False
else: xmodits_exists = True

startinststr = 'XM_Inst_'
maincolor = [0.16, 0.33, 0.53]

class xm_env:
    def __init__(self): 
        self.points = []
        self.numpoints = 0
        self.sustain = 0
        self.type = 0
        self.loop_start = 0
        self.loop_end = 0
        self.enabled = False
        self.sustain_on = False
        self.loop_on = False

    def set_type(self, i_type): 
        self.type = i_type
        self.enabled = bool(i_type&1)
        self.sustain_on = bool(i_type&2)
        self.loop_on = bool(i_type&4)

    def to_cvpj(self, plugin_obj, ispan, fadeout):
        autopoints_obj = plugin_obj.env_points_add('pan' if ispan else 'vol', 48, False, 'float')
        autopoints_obj.enabled       = self.enabled
        autopoints_obj.sustain_on    = self.sustain_on
        autopoints_obj.sustain_point = self.sustain+1
        autopoints_obj.sustain_end   = self.sustain+1
        autopoints_obj.loop_on       = self.loop_on
        autopoints_obj.loop_start    = self.loop_start
        autopoints_obj.loop_end      = self.loop_end
        for n in range(self.numpoints):
            xm_point = self.points[n]
            autopoint_obj = autopoints_obj.add_point()
            autopoint_obj.pos = xm_point[0]
            autopoint_obj.value = (xm_point[1]-32)/32 if ispan else xm_point[1]/64
        if not ispan: 
            if fadeout: autopoints_obj.data['fadeout'] = (256/fadeout)
            plugin_obj.env_asdr_from_points('vol')

class xm_sample_header:
    def __init__(self, fs): 
        self.length, self.loop_start, self.loop_end, self.vol, self.fine, self.type, self.pan, self.note, self.reserved = struct.unpack('IIIBBBBBB', fs.read(18))
        self.name = data_bytes.readstring_fixedlen(fs, 22, "windows-1252")
        self.vol /= 64
        if self.type&1: self.loop = 1
        elif self.type&2: self.loop = 2
        else: self.loop = 0
        self.loop_on = bool(self.loop)
        self.double = bool(self.type&16)
        if self.double: self.loop_start /= 2
        if self.double: self.loop_end /= 2

    def cvpj_loop(self): 
        if not self.loop:
            return {"enabled": 0}
        else:
            return {"enabled": 1, "mode": ('normal' if self.loop != 2 else 'pingpong'), "points": [self.loop_start,self.loop_start+self.loop_end]}



class xm_instrument:
    def __init__(self, fs): 
        basepos = fs.tell()
        header_length = int.from_bytes(fs.read(4), "little")
        self.name = data_bytes.readstring_fixedlen(fs, 22, "latin1")
        self.type = fs.read(1)[0]
        self.num_samples = fs.read(1)[0]

        print("[input-xm] Instrument:")
        print("[input-xm]     Name: " + str(self.name))
        print("[input-xm]     Type: " + str(self.type))
        print("[input-xm]     # of samples: " + str(self.num_samples-1))

        self.env_vol = xm_env()
        self.env_pan = xm_env()
        self.vibrato_type = 0
        self.vibrato_sweep = 0
        self.vibrato_depth = 0
        self.vibrato_rate = 0
        self.fadeout = 0

        self.notesampletable = []

        if self.num_samples != 0:
            xm_inst_e_head_size = int.from_bytes(fs.read(4), "little")
            print("[input-xm]     Sample header size: " + str(xm_inst_e_head_size))
            self.notesampletable = struct.unpack('B'*96, fs.read(96))
            self.env_vol.points = [[v for v in struct.unpack('>HH', fs.read(4))] for x in range(12)]
            self.env_pan.points = [[v for v in struct.unpack('>HH', fs.read(4))] for x in range(12)]
            fs.read(1)
            self.env_vol.numpoints = fs.read(1)[0]
            self.env_pan.numpoints = fs.read(1)[0]
            self.env_vol.sustain = fs.read(1)[0]-1
            self.env_vol.loop_start = fs.read(1)[0]
            self.env_vol.loop_end = fs.read(1)[0]
            self.env_pan.sustain = fs.read(1)[0]-1
            self.env_pan.loop_start = fs.read(1)[0]
            self.env_pan.loop_end = fs.read(1)[0]
            self.env_vol.set_type(fs.read(1)[0])
            self.env_pan.set_type(fs.read(1)[0])
            self.vibrato_type = fs.read(1)[0]
            self.vibrato_sweep = fs.read(1)[0]
            self.vibrato_depth = fs.read(1)[0]
            self.vibrato_rate = fs.read(1)[0]
            self.fadeout = int.from_bytes(fs.read(2), "little")
            self.reserved = int.from_bytes(fs.read(2), "little")

        basepos_end = fs.tell()
        xm_pat_extra_data = fs.read(header_length - (basepos_end-basepos))

        self.pluginnum = 0

        self.samp_head = [xm_sample_header(fs) for _ in range(self.num_samples)]
        self.samp_data = [fs.read(x.length) for x in self.samp_head]

    def vibrato_lfo(self, plugin_obj): 
        if self.vibrato_rate != 0:
            vibrato_speed = self.vibrato_rate
            vibrato_depth = (self.vibrato_depth/15)*0.23
            vibrato_wave = ['sine','square','ramp_up','ramp_down'][self.vibrato_type&3]
            vibrato_sweep = self.vibrato_sweep/50

            lfo_obj = plugin_obj.lfo_add('pitch')
            lfo_obj.attack = vibrato_sweep
            lfo_obj.shape = vibrato_wave
            lfo_obj.time.set_seconds(vibrato_speed)
            lfo_obj.amount = vibrato_depth

class input_xm(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'xm'
    def gettype(self): return 'm'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'FastTracker 2'
        dawinfo_obj.file_ext = 'xm'
        dawinfo_obj.track_lanes = True
        dawinfo_obj.audio_filetypes = ['wav']
        dawinfo_obj.plugin_included = ['sampler:single', 'sampler:multi']
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytesdata = bytestream.read(17)
        if bytesdata == b'Extended Module: ': return True
        else: return False
        bytestream.seek(0)

    def parse(self, convproj_obj, input_file, dv_config):
        global samplefolder
        global xm_cursamplenum

        xm_cursamplenum = 1

        samplefolder = dv_config.path_samples_extracted
        
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

        # ------------- Orders -------------
        xm_order = file_stream.read(xm_song_length)
        t_orderlist = []
        for xm_orderentry in xm_order: t_orderlist.append(xm_orderentry)
        print("[input-xm] Order List: " + str(t_orderlist))

        # ------------- Pattern -------------
        findpat = file_stream.tell()
        calc_pos = xm_headersize+xm_headersize_pos-4

        extra_data = file_stream.read(calc_pos-findpat)
        patterndata = dv_trackerpattern.patterndata(xm_song_num_channels, startinststr, maincolor)

        for patnum in range(xm_song_num_patterns):
            basepos = file_stream.tell()
            xm_pat_header_length = int.from_bytes(file_stream.read(4), "little")
            xm_pat_pak_type = file_stream.read(1)[0]
            xm_pat_num_rows = int.from_bytes(file_stream.read(2), "little")
            xm_pat_patterndata_size = int.from_bytes(file_stream.read(2), "little")
            basepos_end = file_stream.tell()
            xm_pat_extra_data = file_stream.read(xm_pat_header_length - (basepos_end-basepos))
            bio_patdata = BytesIO(file_stream.read(xm_pat_patterndata_size))

            patterndata.pattern_add(patnum, xm_pat_num_rows)
            for rownum in range(xm_pat_num_rows):
                if xm_pat_patterndata_size != 0: 
                    for channel in range(xm_song_num_channels):
                        cell_note = None
                        output_inst = None
                        cell_vol = 64
                        cell_effect = None
                        cell_param = 0

                        packed_first = int.from_bytes(bio_patdata.read(1), "little")
                        packed_flags = bin(packed_first)[2:].zfill(8)

                        packed_note = int(packed_flags[7], 2) 
                        packed_inst = int(packed_flags[6], 2)
                        packed_vol = int(packed_flags[5], 2)
                        packed_effect = int(packed_flags[4], 2)
                        packed_param = int(packed_flags[3], 2)
                        packed_msb = int(packed_flags[0], 2)
                        if packed_msb == 1:
                            if packed_note == 1: cell_note = int.from_bytes(bio_patdata.read(1), "little")
                            if packed_inst == 1: output_inst = int.from_bytes(bio_patdata.read(1), "little")
                            if packed_vol == 1: cell_vol = int.from_bytes(bio_patdata.read(1), "little")
                            if packed_effect == 1: cell_effect = int.from_bytes(bio_patdata.read(1), "little")
                            if packed_param == 1: cell_param = int.from_bytes(bio_patdata.read(1), "little")
                        else:
                            cell_note = packed_first
                            output_inst = int.from_bytes(bio_patdata.read(1), "little")
                            cell_vol = int.from_bytes(bio_patdata.read(1), "little")
                            cell_effect = int.from_bytes(bio_patdata.read(1), "little")
                            cell_param = int.from_bytes(bio_patdata.read(1), "little")

                        output_note = cell_note
                        if cell_note != None: output_note = 'off' if cell_note == 97 else cell_note-49
                        patterndata.cell_note(channel, output_note, output_inst)
                        patterndata.cell_param(channel, 'vol', cell_vol/64)
                        patterndata.cell_fx_mod(channel, cell_effect, cell_param)
                        if cell_effect == 12: patterndata.cell_param(channel, 'vol', cell_param/64)
                        if cell_effect == 15: patterndata.cell_g_param('speed', cell_param)
                        if cell_effect == 16: patterndata.cell_param(channel, 'global_volume', cell_param/64)
                        if cell_effect == 17: patterndata.cell_param(channel, 'global_volume_slide', dv_trackerpattern.getfineval(cell_param))
                        if cell_effect == 34:
                            panbrello_params = {}
                            panbrello_params['speed'], panbrello_params['depth'] = data_bytes.splitbyte(cell_param)
                            patterndata.cell_param(n_chan, 'panbrello', panbrello_params)
                patterndata.row_next()

        # ------------- Instruments -------------

        xm_insts = [xm_instrument(file_stream) for x in range(xm_song_num_instruments)]

        patnames, channames = openmpt_chunks.parse_start(file_stream, convproj_obj)
        XTPM_data, STPM_data = openmpt_chunks.parse_xtst(file_stream, xm_song_num_instruments)

        for n, d in enumerate(XTPM_data):
            for c, v in d:
                if c == b'.PiM': xm_insts[n].pluginnum = v[0]

        for c, d in enumerate(STPM_data):
            if c == b'...C': patterndata.num_chans = int.from_bytes(chunk_value, "little")
            elif c == b'AUTH': convproj_obj.metadata.author = chunk_value.decode()
            elif c == b'CCOL': patterndata.ch_colors = d

        if xmodits_exists == True:
            if not os.path.exists(samplefolder): os.makedirs(samplefolder)
            try: xmodits.dump(input_file, samplefolder, index_only=True, index_raw=True, index_padding=0)
            except: pass

        for instnum in range(xm_song_num_instruments):
            xm_inst = xm_insts[instnum]

            cvpj_instid = startinststr + str(instnum+1)

            inst_obj = convproj_obj.add_instrument(cvpj_instid)
            inst_obj.visual.name = xm_inst.name
            inst_obj.visual.color = maincolor
            inst_obj.params.add('vol', 0.3, 'float')

            sampleregions = data_values.list_to_reigons(xm_inst.notesampletable, 48)

            inst_used = False
            if xm_inst.num_samples == 0: pass
            elif xm_inst.num_samples == 1:
                inst_used = True
                first_s_obj = xm_inst.samp_head[0]
                inst_obj.params.add('vol', 0.3*(first_s_obj.vol), 'float')
                filename = samplefolder+str(xm_cursamplenum)+'.wav'
                plugin_obj, inst_obj.pluginid, sampleref_obj = convproj_obj.add_plugin_sampler_genid(filename)
                plugin_obj.datavals.add('point_value_type', "samples")
                plugin_obj.datavals.add('loop', first_s_obj.cvpj_loop())
            else:
                inst_used = True
                inst_obj.params.add('vol', 0.3, 'float')
                plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('sampler', 'multi')
                plugin_obj.datavals.add('point_value_type', "samples")
                for instnum, r_start, e_end in sampleregions:
                    filename = samplefolder + str(xm_cursamplenum+instnum) + '.wav'
                    sampleref_obj = convproj_obj.add_sampleref(filename, filename)
                    regionparams = {}
                    regionparams['sampleref'] = filename
                    regionparams['loop'] = xm_inst.samp_head[instnum].cvpj_loop()
                    plugin_obj.regions.add(r_start, e_end, regionparams)

            if xm_inst.num_samples != 0:
                xm_inst.vibrato_lfo(plugin_obj)
                xm_inst.env_vol.to_cvpj(plugin_obj, False, xm_inst.fadeout)
                xm_inst.env_pan.to_cvpj(plugin_obj, True, xm_inst.fadeout)

            if xm_inst.pluginnum: 
                inst_obj.fxslots_audio.append('FX'+str(xm_inst.pluginnum))

            xm_cursamplenum += xm_inst.num_samples

        if channames:
            for n, v in enumerate(channames): patterndata.ch_names[n] = v
        
        if patnames:
            for n, v in enumerate(channames): patterndata.pat_names[n] = v

        patterndata.to_cvpj(convproj_obj, t_orderlist, startinststr, xm_song_bpm, xm_song_speed, maincolor)
        convproj_obj.metadata.name = xm_name
        convproj_obj.metadata.comment_text = '\r'.join([i.name for i in xm_insts])
        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_lanefit')
        convproj_obj.params.add('bpm', xm_song_bpm, 'float')