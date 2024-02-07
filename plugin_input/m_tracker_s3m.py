# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
from functions import audio_wav
from functions import data_bytes
from objects import dv_trackerpattern

class input_s3m(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 's3m'
    def getname(self): return 'Scream Tracker 3 Module'
    def gettype(self): return 'm'
    def getdawcapabilities(self): 
        return {
        'samples_inside': True,
        'track_lanes': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(44)
        bytesdata = bytestream.read(4)
        if bytesdata == b'SCRM': return True
        else: return False
        bytestream.seek(0)

    def parse(self, convproj_obj, input_file, extra_param):
        bio_mainfile = open(input_file, 'rb')
        
        samplefolder = extra_param['samplefolder']
        
        startinststr = 'S3M_Inst_'
        maincolor = [0.65, 0.57, 0.33]

        s3m_name = data_bytes.readstring_fixedlen(bio_mainfile, 28, "windows-1252")
        print("[input-st3] Song Name: " + str(s3m_name))
        s3m_sig1 = bio_mainfile.read(1)
        s3m_type = bio_mainfile.read(1)
        s3m_reserved = int.from_bytes(bio_mainfile.read(2), "little")
        s3m_numorder = int.from_bytes(bio_mainfile.read(2), "little")
        s3m_numinst = int.from_bytes(bio_mainfile.read(2), "little")
        s3m_numpat = int.from_bytes(bio_mainfile.read(2), "little")
        s3m_flags = bio_mainfile.read(2)
        s3m_trkrvers = bio_mainfile.read(2)
        s3m_samptype = int.from_bytes(bio_mainfile.read(2), "little")
        s3m_sig2 = bio_mainfile.read(4)
        s3m_globalvol = bio_mainfile.read(1)[0]
        s3m_speed = bio_mainfile.read(1)[0]
        s3m_tempo = bio_mainfile.read(1)[0]
        current_tempo = s3m_tempo
        print("[input-st3] Tempo: " + str(s3m_tempo))
        s3m_mastervol = bio_mainfile.read(1)
        s3m_ultraclickremoval = bio_mainfile.read(1)[0]
        s3m_defaultpan = bio_mainfile.read(1)
        s3m_reserved2 = bio_mainfile.read(8)
        s3m_numspecial = int.from_bytes(bio_mainfile.read(2), "little")
        s3m_chnlsettings = bio_mainfile.read(32)
        
        current_speed = s3m_speed
        tempo_slide = 0

        s3m_orderlist = bio_mainfile.read(s3m_numorder)
        t_orderlist = []
        for s3m_orderlistentry in s3m_orderlist: t_orderlist.append(s3m_orderlistentry)
        
        while 255 in t_orderlist: t_orderlist.remove(255)
        print("[input-st3] Order List: " + str(t_orderlist))
        
        s3m_pointer_insts = []
        for _ in range(s3m_numinst): s3m_pointer_insts.append(int.from_bytes(bio_mainfile.read(2), "little")*16)
        print("[input-st3] # of Instruments: " + str(len(s3m_pointer_insts)))
        if s3m_numinst > 255: print('[error] Not a S3M File'); exit()
        
        s3m_pointer_patterns = []
        for _ in range(s3m_numpat): s3m_pointer_patterns.append(int.from_bytes(bio_mainfile.read(2), "little")*16)
        print("[input-st3] # of Samples: " + str(len(s3m_pointer_patterns)))
        if s3m_numpat > 255: print('[error] Not a S3M File'); exit()
        
        table_defualtvol = []
        
        # ------------- Instruments -------------
        s3m_numinst = 0
        for s3m_pointer_inst in s3m_pointer_insts:
            bio_mainfile.seek(s3m_pointer_inst)
            s3m_inst_type = bio_mainfile.read(1)[0]
            s3m_inst_filename = data_bytes.readstring_fixedlen(bio_mainfile, 12, "windows-1252")
            if s3m_inst_type == 0 or s3m_inst_type == 1:
                s3m_inst_s3m_pointer_DataH = bio_mainfile.read(1)
                s3m_inst_s3m_pointer_DataL = bio_mainfile.read(2)
                cvpj_inst_samplelocation = int.from_bytes(s3m_inst_s3m_pointer_DataL + s3m_inst_s3m_pointer_DataH, "little")*16
                s3m_inst_length = int.from_bytes(bio_mainfile.read(4), "little")
                s3m_inst_loopStart = int.from_bytes(bio_mainfile.read(4), "little")
                s3m_inst_loopEnd = int.from_bytes(bio_mainfile.read(4), "little")
                s3m_inst_vol = bio_mainfile.read(1)[0]/64
                s3m_inst_reserved = bio_mainfile.read(1)[0]
                s3m_inst_pack = bio_mainfile.read(1)[0]
                s3m_inst_flags = bin(bio_mainfile.read(1)[0])[2:].zfill(8)
                s3m_inst_16bit = int(s3m_inst_flags[5], 2)
                s3m_inst_stereo = int(s3m_inst_flags[6], 2)
                s3m_inst_loopon = int(s3m_inst_flags[7], 2)
                s3m_inst_c2spd = int.from_bytes(bio_mainfile.read(4), "little")
                s3m_inst_internal = bio_mainfile.read(12)
                s3m_inst_name = data_bytes.readstring_fixedlen(bio_mainfile, 28, "windows-1252")
                s3m_inst_sig = bio_mainfile.read(4)

            cvpj_instid = startinststr + str(s3m_numinst+1)

            if s3m_inst_type == 0: print("[input-st3] Message #" + str(s3m_numinst) + ': "' + s3m_inst_name + '", Filename:"' + s3m_inst_filename+ '"')
            else: print("[input-st3] Instrument #" + str(s3m_numinst) + ': "' + s3m_inst_name + '", Filename:"' + s3m_inst_filename+ '"')
            table_defualtvol.append(s3m_inst_vol)

            if s3m_inst_filename != '': cvpj_inst_name = s3m_inst_filename
            elif s3m_inst_name != '': cvpj_inst_name = s3m_inst_name
            else: cvpj_inst_name = ' '

            wave_path = samplefolder+str(s3m_numinst).zfill(2)+'.wav'
            if s3m_inst_type == 1: cvpj_inst_color = [0.65, 0.57, 0.33]
            else: cvpj_inst_color = [0.32, 0.27, 0.16]

            inst_obj = convproj_obj.add_instrument(cvpj_instid)
            inst_obj.visual.name = cvpj_inst_name
            inst_obj.visual.color = cvpj_inst_color
            inst_obj.params.add('vol', 0.3, 'float')
            plugin_obj, pluginid, sampleref_obj = convproj_obj.add_plugin_sampler_genid(wave_path)
            plugin_obj.datavals.add('point_value_type', "samples")

            if cvpj_inst_samplelocation != 0 and s3m_inst_length != 0:
                cvpj_loop = {}
                if s3m_inst_loopon == 1:
                    cvpj_loop['enabled'] = 1
                    cvpj_loop['mode'] = "normal"
                    cvpj_loop['points'] = [s3m_inst_loopStart, s3m_inst_loopEnd-1]
                    loopdata = {'loop':[s3m_inst_loopStart, s3m_inst_loopEnd-1]}
                else:
                    cvpj_loop['enabled'] = 0
                    loopdata = None

                plugin_obj.datavals.add('loop', cvpj_loop)

                print("[input-st3] Ripping Sample " + str(s3m_numinst))
                bio_mainfile.seek(cvpj_inst_samplelocation)
                os.makedirs(samplefolder, exist_ok=True)

                if s3m_inst_16bit == 0: t_samplelen = s3m_inst_length
                if s3m_inst_16bit == 1: t_samplelen = s3m_inst_length*2
                wave_sampledata = bio_mainfile.read(t_samplelen)
                wave_bits = 8
                wave_channels = 1
                if s3m_inst_16bit == 1: wave_bits = 16
                if s3m_inst_16bit == 0 and s3m_inst_stereo == 1: 
                    wave_channels = 2
                    wave_sampledata_second = bio_mainfile.read(t_samplelen)
                    wave_sampledata = data_bytes.mono2stereo(wave_sampledata, wave_sampledata_second, 1)
                if s3m_inst_16bit == 1 and s3m_inst_stereo == 1:
                    wave_channels = 2
                    wave_sampledata_second = bio_mainfile.read(t_samplelen)
                    wave_sampledata = data_bytes.mono2stereo(wave_sampledata, wave_sampledata_second, 2)
                if s3m_inst_16bit == 0 and s3m_samptype == 1: wave_sampledata = data_bytes.unsign_8(wave_sampledata)
                if s3m_inst_16bit == 1 and s3m_samptype == 2: wave_sampledata = data_bytes.unsign_16(wave_sampledata)
                audio_wav.generate(wave_path, wave_sampledata, wave_channels, s3m_inst_c2spd, wave_bits, loopdata)

            if s3m_inst_type == 1: inst_obj.pluginid = pluginid
            s3m_numinst += 1

        patterncount = 1

        patterndata = dv_trackerpattern.patterndata(32, startinststr, maincolor)

        #print("[input-st3] Decoding Pattern:",end=' ')
        for s3m_pointer_pattern in s3m_pointer_patterns:
            #print(str(patterncount),end=' ')
            patterntable_single = []
            if s3m_pointer_pattern != 0:
                bio_mainfile.seek(s3m_pointer_pattern)
                pattern_packed_len = int.from_bytes(bio_mainfile.read(2), "little")

                patterndata.pattern_add(patterncount-1, 64)
                for _ in range(64):
                    pattern_done = 0
                    pattern_row_local = []

                    while pattern_done == 0:
                        packed_what = bin(bio_mainfile.read(1)[0])[2:].zfill(8)
                        if int(packed_what, 2) == 0: pattern_done = 1
                        else:
                            packed_what_command_info = int(packed_what[0], 2)
                            packed_what_vol = int(packed_what[1], 2)
                            packed_what_note_instrument = int(packed_what[2], 2)
                            packed_what_channel = int(packed_what[3:8], 2)
        
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
                                packed_note = bio_mainfile.read(1)[0]
                                if packed_note == 255: packed_note = None
                                out_inst = bio_mainfile.read(1)[0]
                                if out_inst == 0: out_inst = None
                            if packed_what_vol == 1: packed_vol = bio_mainfile.read(1)[0]
                            if packed_what_command_info == 1: out_cmd = bio_mainfile.read(1)[0]
                            if packed_what_command_info == 1: out_info = bio_mainfile.read(1)[0]
                            if packed_note != None:
                                bits_packed_note = bin(packed_note)[2:].zfill(8)
                                bits_packed_note_oct = int(bits_packed_note[0:4], 2)-4
                                bits_packed_note_tone = int(bits_packed_note[4:8], 2)
                                final_note = bits_packed_note_oct*12 + bits_packed_note_tone
                                out_note = final_note if packed_note != 254 else 'cut'

                            if packed_vol != None: out_vol = packed_vol/64
                            else: out_vol = table_defualtvol[out_inst-1] if out_inst != None else 1.0

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

            patterncount += 1
        #print(' ')

        patterndata.to_cvpj(convproj_obj, t_orderlist, startinststr, s3m_tempo, s3m_speed, maincolor)

        #patlentable = song_tracker.get_len_table(patterntable_all, t_orderlist)
        #auto_data.add_pl(cvpj_l, 'float', ['main', 'bpm'], song_tracker.tempo_auto(patterntable_all, t_orderlist, s3m_speed, s3m_tempo))

        convproj_obj.metadata.name = s3m_name
        
        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_lanefit')

        convproj_obj.params.add('bpm', s3m_tempo, 'float')
