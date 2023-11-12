# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import json
from functions import song_tracker
from functions import song_tracker_fx_s3m
from functions import audio_wav
from functions import data_bytes
from functions import placements
from functions import plugins
from functions import song
from functions_tracks import tracks_mi
from functions_tracks import auto_data

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

    def parse(self, input_file, extra_param):
        bio_mainfile = open(input_file, 'rb')
        
        samplefolder = extra_param['samplefolder']
        
        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []

        startinststr = 'S3M_Inst_'

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
        s3m_globalvol = int.from_bytes(bio_mainfile.read(1), "little")
        s3m_speed = int.from_bytes(bio_mainfile.read(1), "little")
        s3m_tempo = int.from_bytes(bio_mainfile.read(1), "little")
        current_tempo = s3m_tempo
        print("[input-st3] Tempo: " + str(s3m_tempo))
        s3m_mastervol = bio_mainfile.read(1)
        s3m_ultraclickremoval = int.from_bytes(bio_mainfile.read(1), "little")
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
            s3m_inst_type = int.from_bytes(bio_mainfile.read(1), "little")
            s3m_inst_filename = data_bytes.readstring_fixedlen(bio_mainfile, 12, "windows-1252")
            if s3m_inst_type == 0 or s3m_inst_type == 1:
                s3m_inst_s3m_pointer_DataH = bio_mainfile.read(1)
                s3m_inst_s3m_pointer_DataL = bio_mainfile.read(2)
                cvpj_inst_samplelocation = int.from_bytes(s3m_inst_s3m_pointer_DataL + s3m_inst_s3m_pointer_DataH, "little")*16
                s3m_inst_length = int.from_bytes(bio_mainfile.read(4), "little")
                s3m_inst_loopStart = int.from_bytes(bio_mainfile.read(4), "little")
                s3m_inst_loopEnd = int.from_bytes(bio_mainfile.read(4), "little")
                s3m_inst_vol = int.from_bytes(bio_mainfile.read(1), "little")/64
                s3m_inst_reserved = int.from_bytes(bio_mainfile.read(1), "little")
                s3m_inst_pack = int.from_bytes(bio_mainfile.read(1), "little")
                s3m_inst_flags = bin(int.from_bytes(bio_mainfile.read(1), "little"))[2:].zfill(8)
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

            pluginid = plugins.get_id()
            if s3m_inst_filename != '': cvpj_inst_name = s3m_inst_filename
            elif s3m_inst_name != '': cvpj_inst_name = s3m_inst_name
            else: cvpj_inst_name = ' '

            wave_path = samplefolder+str(s3m_numinst).zfill(2)+'.wav'
            inst_plugindata = plugins.cvpj_plugin('sampler', wave_path, None)
            if s3m_inst_type == 1: cvpj_inst_color = [0.65, 0.57, 0.33]
            else: cvpj_inst_color = [0.32, 0.27, 0.16]

            tracks_mi.inst_create(cvpj_l, cvpj_instid)
            tracks_mi.inst_visual(cvpj_l, cvpj_instid, name=cvpj_inst_name, color=cvpj_inst_color)
            tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'vol', 0.3, 'float')

            inst_plugindata.dataval_add('length', s3m_inst_length)
            inst_plugindata.dataval_add('trigger', 'normal')
            inst_plugindata.dataval_add('point_value_type', "samples")

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

                inst_plugindata.dataval_add('loop', cvpj_loop)

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

            if s3m_inst_type == 1: 
                inst_plugindata.to_cvpj(cvpj_l, pluginid)
                tracks_mi.inst_pluginid(cvpj_l, cvpj_instid, pluginid)
            s3m_numinst += 1

        patterncount = 1
        patterntable_all = []
        print("[input-st3] Decoding Pattern:",end=' ')
        for s3m_pointer_pattern in s3m_pointer_patterns:
            print(str(patterncount),end=' ')
            patterntable_single = []
            if s3m_pointer_pattern != 0:
                bio_mainfile.seek(s3m_pointer_pattern)
                pattern_packed_len = int.from_bytes(bio_mainfile.read(2), "little")
                firstrow = 1
                rowcount = 0
                for _ in range(64):
                    pattern_done = 0
                    pattern_row_local = []
                    for _ in range(32): pattern_row_local.append([None, None, {}, {}])
                    pattern_row = [{}, pattern_row_local]
                    while pattern_done == 0:
                        packed_what = bin(int.from_bytes(bio_mainfile.read(1), "little"))[2:].zfill(8)
                        if int(packed_what, 2) == 0: pattern_done = 1
                        else:
                            packed_what_command_info = int(packed_what[0], 2)
                            packed_what_vol = int(packed_what[1], 2)
                            packed_what_note_instrument = int(packed_what[2], 2)
                            packed_what_channel = int(packed_what[3:8], 2)
        
                            packed_note = None
                            packed_instrument = None
                            packed_vol = None
                            packed_command = None
                            packed_info = None
        
                            if packed_what_note_instrument == 1:
                                packed_note = int.from_bytes(bio_mainfile.read(1), "little")
                                packed_instrument = int.from_bytes(bio_mainfile.read(1), "little")
                                if packed_note == 255: packed_note = None
                                if packed_instrument == 0: packed_instrument = None
                            if packed_what_vol == 1: packed_vol = int.from_bytes(bio_mainfile.read(1), "little")
        
                            if packed_what_command_info == 1: packed_command = int.from_bytes(bio_mainfile.read(1), "little")
                            if packed_what_command_info == 1: packed_info = int.from_bytes(bio_mainfile.read(1), "little")
                            if packed_note != None:
                                bits_packed_note = bin(packed_note)[2:].zfill(8)
                                bits_packed_note_oct = int(bits_packed_note[0:4], 2)-4
                                bits_packed_note_tone = int(bits_packed_note[4:8], 2)
                                final_note = bits_packed_note_oct*12 + bits_packed_note_tone
                                if packed_note == 254: pattern_row[1][packed_what_channel][0] = 'Cut'
                                else: pattern_row[1][packed_what_channel][0] = final_note
                            if packed_instrument != None: pattern_row[1][packed_what_channel][1] = packed_instrument
                            if packed_vol != None: pattern_row[1][packed_what_channel][2]['vol'] = packed_vol/64
                            else:
                                if packed_instrument != None: pattern_row[1][packed_what_channel][2]['vol'] = table_defualtvol[packed_instrument-1]
                                else: pattern_row[1][packed_what_channel][2]['vol'] = 1.0
                            if firstrow == 1:
                                pattern_row[1][packed_what_channel][3]['firstrow'] = 1
                                pattern_row[0]['firstrow'] = 1

                            j_note_cmdval = pattern_row[1][packed_what_channel][2]

                            if packed_what_command_info == 1:

                                current_speed = song_tracker_fx_s3m.do_fx(current_speed, pattern_row[0], j_note_cmdval, packed_command, packed_info)

                                if packed_command == 20: 
                                    tempoval = packed_info
                                    if packed_info == 0:
                                        current_tempo += tempo_slide
                                    if 0 < packed_info < 32:
                                        tempo_slide = packed_info-16
                                        current_tempo += tempo_slide
                                    if packed_info > 32:
                                        current_tempo = packed_info
                                    pattern_row[0]['tempo'] = current_tempo

                                if packed_command == 26: 
                                    j_note_cmdval['pan'] = ((packed_info/128)-0.5)*2
                            
                    firstrow = 0
                    patterntable_single.append(pattern_row)
                    rowcount += 1
            patterntable_all.append(patterntable_single)
            patterncount += 1
        print(' ')
        
        cvpj_l_playlist = song_tracker.song2playlist(patterntable_all, 32, t_orderlist, startinststr, [0.65, 0.57, 0.33])

        patlentable = song_tracker.get_len_table(patterntable_all, t_orderlist)

        auto_data.add_pl(cvpj_l, 'float', ['main', 'bpm'], song_tracker.tempo_auto(patterntable_all, t_orderlist, s3m_speed, s3m_tempo))
        placements.make_timemarkers(cvpj_l, [4,16], patlentable, None)
        song.add_info(cvpj_l, 'title', s3m_name)
        
        cvpj_l['do_addloop'] = True
        cvpj_l['do_lanefit'] = True

        cvpj_l['playlist'] = cvpj_l_playlist
        song.add_param(cvpj_l, 'bpm', s3m_tempo)
        return json.dumps(cvpj_l)
