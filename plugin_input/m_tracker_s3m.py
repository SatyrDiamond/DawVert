# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
from functions import data_bytes
from objects_file import audio_wav
from objects import dv_trackerpattern

class s3m_instrument:
    def __init__(self, fs, ptr):
        fs.seek(ptr)
        self.type = fs.read(1)[0]
        self.filename = data_bytes.readstring_fixedlen(fs, 12, "windows-1252")
        self.name = ''
        self.volume = 1
        if self.type == 0 or self.type == 1:
            self.ptrDataH = fs.read(1)
            self.ptrDataL = fs.read(2)
            self.sampleloc = int.from_bytes(self.ptrDataL + self.ptrDataH, "little")*16
            self.length = int.from_bytes(fs.read(4), "little")
            self.loopStart = int.from_bytes(fs.read(4), "little")
            self.loopEnd = int.from_bytes(fs.read(4), "little")
            self.volume = fs.read(1)[0]/64
            self.reserved = fs.read(1)[0]
            self.pack = fs.read(1)[0]
            self.flags = bin(fs.read(1)[0])[2:].zfill(8)
            self.double = int(self.flags[5], 2)
            self.stereo = int(self.flags[6], 2)
            self.loopon = int(self.flags[7], 2)
            self.c2spd = int.from_bytes(fs.read(4), "little")
            self.internal = fs.read(12)
            self.name = data_bytes.readstring_fixedlen(fs, 28, "windows-1252")
            self.sig = fs.read(4)
        if self.type == 2:
            self.reserved = fs.read(3)
            self.oplValues = fs.read(12)
            self.volume = fs.read(1)[0]/64
            self.dsk = fs.read(1)[0]
            self.reserved2 = fs.read(2)
            self.c2spd = int.from_bytes(fs.read(4), "little")
            self.unused = fs.read(12)
            self.name = data_bytes.readstring_fixedlen(fs, 28, "windows-1252")
            self.sig = fs.read(4)

        if self.type == 0: print('[input-st3] MSG | "' + self.name + '", Filename:"' + self.filename+ '"')
        if self.type == 1: print('[input-st3] PCM | "' + self.name + '", Filename:"' + self.filename+ '"')
        if self.type == 2: print('[input-st3] OPL | "' + self.name + '", Filename:"' + self.filename+ '"')

    def rip_sample(self, fs, samplefolder, s3m_samptype, wave_path):
        if self.type == 1:
            if self.sampleloc != 0 and self.length != 0:
                fs.seek(self.sampleloc)
                os.makedirs(samplefolder, exist_ok=True)
                t_samplelen = self.length if not self.double else self.length*2
                wave_sampledata = fs.read(t_samplelen)
                wave_bits = 8 if not self.double else 16
                wave_channels = 1 if not self.stereo else 2
                if self.double == 0 and self.stereo == 1: wave_sampledata = data_bytes.mono2stereo(wave_sampledata, fs.read(t_samplelen), 1)
                if self.double == 1 and self.stereo == 1: wave_sampledata = data_bytes.mono2stereo(wave_sampledata, fs.read(t_samplelen), 2)
                if self.double == 0 and s3m_samptype == 1: wave_sampledata = data_bytes.unsign_8(wave_sampledata)
                if self.double == 1 and s3m_samptype == 2: wave_sampledata = data_bytes.unsign_16(wave_sampledata)
                wavfile_obj = audio_wav.wav_main()
                wavfile_obj.data_add_data(wave_bits, wave_channels, False, wave_sampledata)
                wavfile_obj.set_freq(self.c2spd)
                if self.loopon: wavfile_obj.add_loop(self.loopStart, self.loopEnd-1)
                wavfile_obj.write(wave_path)


class input_s3m(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 's3m'
    def gettype(self): return 'm'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Scream Tracker 3 Module'
        dawinfo_obj.file_ext = 's3m'
        dawinfo_obj.track_lanes = True
        dawinfo_obj.audio_filetypes = ['wav']
        dawinfo_obj.plugin_included = ['sampler:single']
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(44)
        bytesdata = bytestream.read(4)
        if bytesdata == b'SCRM': return True
        else: return False
        bytestream.seek(0)

    def parse(self, convproj_obj, input_file, dv_config):
        fs = open(input_file, 'rb')
        
        samplefolder = dv_config.path_samples_extracted
        
        startinststr = 's3m_inst_'
        maincolor = [0.65, 0.57, 0.33]

        s3m_name = data_bytes.readstring_fixedlen(fs, 28, "windows-1252")
        print("[input-st3] Song Name: " + str(s3m_name))
        s3m_sig1 = fs.read(1)
        s3m_type = fs.read(1)
        s3m_reserved = int.from_bytes(fs.read(2), "little")
        s3m_numorder = int.from_bytes(fs.read(2), "little")
        s3m_numinst = int.from_bytes(fs.read(2), "little")
        s3m_numpat = int.from_bytes(fs.read(2), "little")
        s3m_flags = fs.read(2)
        s3m_trkrvers = fs.read(2)
        s3m_samptype = int.from_bytes(fs.read(2), "little")
        s3m_sig2 = fs.read(4)
        s3m_globalvol = fs.read(1)[0]
        s3m_speed = fs.read(1)[0]
        s3m_tempo = fs.read(1)[0]
        current_tempo = s3m_tempo
        print("[input-st3] Tempo: " + str(s3m_tempo))
        s3m_mastervol = fs.read(1)
        s3m_ultraclickremoval = fs.read(1)[0]
        s3m_defaultpan = fs.read(1)
        s3m_reserved2 = fs.read(8)
        s3m_numspecial = int.from_bytes(fs.read(2), "little")
        s3m_chnlsettings = fs.read(32)
        
        current_speed = s3m_speed
        tempo_slide = 0

        s3m_orderlist = fs.read(s3m_numorder)
        t_orderlist = []
        for s3m_orderlistentry in s3m_orderlist: t_orderlist.append(s3m_orderlistentry)
        
        while 255 in t_orderlist: t_orderlist.remove(255)
        print("[input-st3] Order List: " + str(t_orderlist))
        
        s3m_pointer_insts = [int.from_bytes(fs.read(2), "little")*16 for _ in range(s3m_numinst)]
        if s3m_numinst > 255: print('[error] Not a S3M File'); exit()
        print("[input-st3] # of Instruments: " + str(len(s3m_pointer_insts)))
        
        s3m_pointer_patterns = [int.from_bytes(fs.read(2), "little")*16 for _ in range(s3m_numpat)]
        if s3m_numpat > 255: print('[error] Not a S3M File'); exit()
        print("[input-st3] # of Samples: " + str(len(s3m_pointer_patterns)))
        
        s3m_insts = [s3m_instrument(fs, x) for x in s3m_pointer_insts]

        # ------------- Instruments -------------
        for s3m_numinst, s3m_inst in enumerate(s3m_insts):
            cvpj_instid = startinststr + str(s3m_numinst+1)

            if s3m_inst.filename != '': cvpj_inst_name = s3m_inst.filename
            elif s3m_inst.name != '': cvpj_inst_name = s3m_inst.name
            else: cvpj_inst_name = ' '

            wave_path = samplefolder+str(s3m_numinst).zfill(2)+'.wav'
            inst_obj = convproj_obj.add_instrument(cvpj_instid)
            inst_obj.visual.name = cvpj_inst_name
            inst_obj.visual.color = [0.32, 0.27, 0.16] if not s3m_inst.type else [0.65, 0.57, 0.33]
            inst_obj.params.add('vol', 0.3, 'float')

            if s3m_inst.type == 1:
                s3m_inst.rip_sample(fs, samplefolder, s3m_samptype, wave_path)
                plugin_obj, pluginid, sampleref_obj = convproj_obj.add_plugin_sampler_genid(wave_path)
                plugin_obj.datavals.add('point_value_type', "samples")

                if s3m_inst.sampleloc != 0 and s3m_inst.length != 0:
                    cvpj_loop = {}
                    if s3m_inst.loopon == 1:
                        cvpj_loop['enabled'] = 1
                        cvpj_loop['mode'] = "normal"
                        cvpj_loop['points'] = [s3m_inst.loopStart, s3m_inst.loopEnd-1]
                    else: cvpj_loop['enabled'] = 0

                    plugin_obj.datavals.add('loop', cvpj_loop)

                inst_obj.pluginid = pluginid


        patterndata = dv_trackerpattern.patterndata(32, startinststr, maincolor)

        for patterncount, s3m_pointer_pattern in enumerate(s3m_pointer_patterns):
            patterntable_single = []
            if s3m_pointer_pattern != 0:
                fs.seek(s3m_pointer_pattern)
                pattern_packed_len = int.from_bytes(fs.read(2), "little")

                patterndata.pattern_add(patterncount, 64)
                for _ in range(64):
                    pattern_done = 0
                    pattern_row_local = []

                    while pattern_done == 0:
                        packed_what = fs.read(1)[0]
                        if not packed_what: pattern_done = 1
                        else:
                            packed_what_command_info = bool(packed_what&128)
                            packed_what_vol = bool(packed_what&64)
                            packed_what_note_instrument = bool(packed_what&32)
                            packed_what_channel = packed_what&31
        
                            packed_note = None
                            packed_inst = None
                            packed_vol = None
                            packed_command = None
                            packed_info = None
        
                            out_note = None
                            out_inst = None
                            out_vol = None
                            out_cmd = None
                            out_info = None

                            if packed_what_note_instrument == 1:
                                packed_note = fs.read(1)[0]
                                if packed_note == 255: packed_note = None
                                out_inst = fs.read(1)[0]
                                if out_inst == 0: out_inst = None
                            if packed_what_vol == 1: packed_vol = fs.read(1)[0]
                            if packed_what_command_info == 1: out_cmd = fs.read(1)[0]
                            if packed_what_command_info == 1: out_info = fs.read(1)[0]
                            if packed_note != None:
                                bits_packed_note = bin(packed_note)[2:].zfill(8)
                                bits_packed_note_oct = int(bits_packed_note[0:4], 2)-4
                                bits_packed_note_tone = int(bits_packed_note[4:8], 2)
                                final_note = bits_packed_note_oct*12 + bits_packed_note_tone
                                out_note = final_note if packed_note != 254 else 'cut'

                            if packed_vol != None: out_vol = packed_vol/64
                            else: out_vol = s3m_insts[out_inst-1].volume if out_inst != None else 1

                            patterndata.cell_note(packed_what_channel, out_note, out_inst)
                            patterndata.cell_param(packed_what_channel, 'vol', out_vol)

                            if packed_what_command_info == 1:
                                patterndata.cell_fx_s3m(packed_what_channel, out_cmd, out_info)

                                if packed_command == 20: 
                                    tempoval = packed_info
                                    if packed_info == 0:
                                        current_tempo += tempo_slide
                                    if 0 < packed_info < 32:
                                        tempo_slide = packed_info-16
                                        current_tempo += packed_info-16
                                    if packed_info > 32:
                                        current_tempo = packed_info
                                    patterndata.cell_g_param('tempo', current_tempo)

                                if packed_command == 26: 
                                    patterndata.cell_param(packed_what_channel, 'pan', ((packed_info/128)-0.5)*2)
                          
                    patterndata.row_next()  

        #print(' ')

        patterndata.to_cvpj(convproj_obj, t_orderlist, startinststr, s3m_tempo, s3m_speed, maincolor)

        #patlentable = song_tracker.get_len_table(patterntable_all, t_orderlist)
        #auto_data.add_pl(cvpj_l, 'float', ['main', 'bpm'], song_tracker.tempo_auto(patterntable_all, t_orderlist, s3m_speed, s3m_tempo))

        convproj_obj.metadata.name = s3m_name
        convproj_obj.metadata.comment_text = '\r'.join([i.name for i in s3m_insts])
        
        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_lanefit')

        convproj_obj.params.add('bpm', s3m_tempo, 'float')
