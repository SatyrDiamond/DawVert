# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import json
from functions import song_tracker
from functions import audio_wav
from functions import data_bytes
from functions import folder_samples
from functions import placements

class input_s3m(plugin_input.base):
    def __init__(self): pass
    def getshortname(self): return 'trk_s3m'
    def getname(self): return 'Tracker: Scream Tracker 3 Module'
    def gettype(self): return 'm'
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(44)
        bytesdata = bytestream.read(4)
        if bytesdata == b'SCRM': return True
        else: return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        file_stream = open(input_file, 'rb')
        
        s3m_modulename = os.path.splitext(os.path.basename(input_file))[0]
        samplefolder = folder_samples.samplefolder(extra_param, s3m_modulename)

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []

        startinststr = 'S3M_s3m_inst_'

        s3m_name = file_stream.read(28).split(b'\x00' * 1)[0].decode("utf-8")
        print("[input-st3] Song Name: " + str(s3m_name))
        s3m_sig1 = file_stream.read(1)
        s3m_type = file_stream.read(1)
        s3m_reserved = int.from_bytes(file_stream.read(2), "little")
        s3m_numorder = int.from_bytes(file_stream.read(2), "little")
        s3m_numinst = int.from_bytes(file_stream.read(2), "little")
        s3m_numpat = int.from_bytes(file_stream.read(2), "little")
        s3m_flags = file_stream.read(2)
        s3m_trkrvers = file_stream.read(2)
        s3m_samptype = int.from_bytes(file_stream.read(2), "little")
        s3m_sig2 = file_stream.read(4)
        s3m_globalvol = int.from_bytes(file_stream.read(1), "little")
        s3m_speed = int.from_bytes(file_stream.read(1), "little")
        s3m_tempo = int.from_bytes(file_stream.read(1), "little")
        print("[input-st3] Tempo: " + str(s3m_tempo))
        s3m_mastervol = file_stream.read(1)
        s3m_ultraclickremoval = int.from_bytes(file_stream.read(1), "little")
        s3m_defaultpan = file_stream.read(1)
        s3m_reserved2 = file_stream.read(8)
        s3m_numspecial = int.from_bytes(file_stream.read(2), "little")
        s3m_chnlsettings = file_stream.read(32)
        
        s3m_orderlist = file_stream.read(s3m_numorder)
        t_orderlist = []
        for s3m_orderlistentry in s3m_orderlist: t_orderlist.append(s3m_orderlistentry)
        
        while 255 in t_orderlist: t_orderlist.remove(255)
        print("[input-st3] Order List: " + str(t_orderlist))
        
        s3m_pointer_insts = []
        for _ in range(s3m_numinst): s3m_pointer_insts.append(int.from_bytes(file_stream.read(2), "little")*16)
        print("[input-st3] # of Instruments: " + str(len(s3m_pointer_insts)))
        if s3m_numinst > 255:
            print('[error] Not a S3M File')
            exit()
        
        s3m_pointer_patterns = []
        for _ in range(s3m_numpat):
            s3m_pointer_patterns.append(int.from_bytes(file_stream.read(2), "little")*16)
        print("[input-st3] # of Samples: " + str(len(s3m_pointer_patterns)))
        if s3m_numpat > 255:
            print('[error] Not a S3M File')
            exit()
        
        table_defualtvol = []
        
        # ------------- Instruments -------------
        s3m_numinst = 0
        for s3m_pointer_inst in s3m_pointer_insts:
            file_stream.seek(s3m_pointer_inst)
            s3m_inst_type = int.from_bytes(file_stream.read(1), "little")
            s3m_inst_filename = file_stream.read(12)
            if s3m_inst_type == 0 or s3m_inst_type == 1:
                s3m_inst_s3m_pointer_DataH = file_stream.read(1)
                s3m_inst_s3m_pointer_DataL = file_stream.read(2)
                cvpj_inst_samplelocation = int.from_bytes(s3m_inst_s3m_pointer_DataL + s3m_inst_s3m_pointer_DataH, "little")*16
                s3m_inst_length = int.from_bytes(file_stream.read(4), "little")
                s3m_inst_loopStart = int.from_bytes(file_stream.read(4), "little")
                s3m_inst_loopEnd = int.from_bytes(file_stream.read(4), "little")
                s3m_inst_vol = int.from_bytes(file_stream.read(1), "little")/64
                s3m_inst_reserved = int.from_bytes(file_stream.read(1), "little")
                s3m_inst_pack = int.from_bytes(file_stream.read(1), "little")
                s3m_inst_flags = bin(int.from_bytes(file_stream.read(1), "little"))[2:].zfill(8)
                s3m_inst_16bit = int(s3m_inst_flags[5], 2)
                s3m_inst_stereo = int(s3m_inst_flags[6], 2)
                s3m_inst_loopon = int(s3m_inst_flags[7], 2)
                s3m_inst_c2spd = int.from_bytes(file_stream.read(4), "little")
                s3m_inst_internal = file_stream.read(12)
                s3m_inst_namebytes = file_stream.read(28)
                s3m_inst_sig = file_stream.read(4)
            t_inst_filename = s3m_inst_filename.split(b'\x00' * 1)[0].decode("latin_1")
            t_inst_name = s3m_inst_namebytes.split(b'\x00' * 1)[0].decode("latin_1")

            s3m_t_inst_name = startinststr + str(s3m_numinst+1)

            cvpj_l_instruments[s3m_t_inst_name] = {}
            cvpj_l_single_inst = cvpj_l_instruments[s3m_t_inst_name]
            cvpj_l_instrumentsorder.append(s3m_t_inst_name)

            if s3m_inst_type == 0: print("[input-st3] Message #" + str(s3m_numinst) + ': "' + t_inst_name + '", Filename:"' + t_inst_filename+ '"')
            else: print("[input-st3] Instrument #" + str(s3m_numinst) + ': "' + t_inst_name + '", Filename:"' + t_inst_filename+ '"')
            table_defualtvol.append(s3m_inst_vol)

            if t_inst_filename != '': cvpj_l_single_inst['name'] = t_inst_filename
            elif t_inst_name != '': cvpj_l_single_inst['name'] = t_inst_name
            else: cvpj_l_single_inst['name'] = ' '

            cvpj_l_single_inst['vol'] = 0.3
            cvpj_l_single_inst['instdata'] = {}
            cvpj_l_inst = cvpj_l_single_inst['instdata']
            cvpj_l_inst['plugindata'] = {}
            cvpj_l_plugin = cvpj_l_inst['plugindata']

            if s3m_inst_type == 1:
                cvpj_l_single_inst['color'] = [0.65, 0.57, 0.33]
                cvpj_l_single_inst['instdata']['plugin'] = 'sampler'
                cvpj_l_plugin['file'] = samplefolder + str(s3m_numinst).zfill(2) + '.wav'
            else:
                cvpj_l_single_inst['color'] = [0.32, 0.27, 0.16]
                cvpj_l_inst['plugin'] = 'none'

            cvpj_l_plugin['length'] = s3m_inst_length

            if cvpj_inst_samplelocation != 0 and s3m_inst_length != 0:
                cvpj_l_plugin['loop'] = {}
                if s3m_inst_loopon == 1:
                    cvpj_l_plugin['loop']['enabled'] = 1
                    cvpj_l_plugin['loop']['mode'] = "normal"
                    cvpj_l_plugin['loop']['points'] = [s3m_inst_loopStart, s3m_inst_loopEnd-1]
                    print(s3m_inst_loopStart, s3m_inst_loopEnd)
                    loopdata = {'loop':[s3m_inst_loopStart, s3m_inst_loopEnd-1]}
                else:
                    cvpj_l_plugin['loop']['enabled'] = 0
                    loopdata = None
                print("[input-st3] Ripping Sample " + str(s3m_numinst))
                file_stream.seek(cvpj_inst_samplelocation)
                os.makedirs(samplefolder, exist_ok=True)
                wave_path = samplefolder + str(s3m_numinst).zfill(2) + '.wav'

                t_samplelen = s3m_inst_length

                if s3m_inst_16bit == 0: t_samplelen = t_samplelen
                if s3m_inst_16bit == 1: t_samplelen = t_samplelen*2
                wave_sampledata = file_stream.read(t_samplelen)
                wave_bits = 8
                wave_channels = 1
                if s3m_inst_16bit == 1: wave_bits = 16
                if s3m_inst_16bit == 0 and s3m_inst_stereo == 1: 
                    wave_channels = 2
                    wave_sampledata_second = file_stream.read(t_samplelen)
                    wave_sampledata = data_bytes.mono2stereo(wave_sampledata, wave_sampledata_second, 1)
                if s3m_inst_16bit == 1 and s3m_inst_stereo == 1:
                    wave_channels = 2
                    wave_sampledata_second = file_stream.read(t_samplelen)
                    wave_sampledata = data_bytes.mono2stereo(wave_sampledata, wave_sampledata_second, 2)
                if s3m_inst_16bit == 0 and s3m_samptype == 1: wave_sampledata = data_bytes.unsign_8(wave_sampledata)
                if s3m_inst_16bit == 1 and s3m_samptype == 2: wave_sampledata = data_bytes.unsign_16(wave_sampledata)
                audio_wav.generate(wave_path, wave_sampledata, wave_channels, s3m_inst_c2spd, wave_bits, loopdata)

            s3m_numinst += 1

        patterncount = 1
        patterntable_all = []
        print("[input-st3] Decoding Pattern:",end=' ')
        for s3m_pointer_pattern in s3m_pointer_patterns:
            print(str(patterncount),end=' ')
            patterntable_single = []
            if s3m_pointer_pattern != 0:
                file_stream.seek(s3m_pointer_pattern)
                pattern_packed_len = int.from_bytes(file_stream.read(2), "little")
                firstrow = 1
                rowcount = 0
                for _ in range(64):
                    pattern_done = 0
                    pattern_row_local = []
                    for _ in range(32): pattern_row_local.append([None, None, {}, {}])
                    pattern_row = [{}, pattern_row_local]
                    while pattern_done == 0:
                        packed_what = bin(int.from_bytes(file_stream.read(1), "little"))[2:].zfill(8)
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
                                packed_note = int.from_bytes(file_stream.read(1), "little")
                                packed_instrument = int.from_bytes(file_stream.read(1), "little")
                                if packed_note == 255: packed_note = None
                                if packed_instrument == 0: packed_instrument = None
                            if packed_what_vol == 1: packed_vol = int.from_bytes(file_stream.read(1), "little")
        
                            if packed_what_command_info == 1: packed_command = int.from_bytes(file_stream.read(1), "little")
                            if packed_what_command_info == 1: packed_info = int.from_bytes(file_stream.read(1), "little")
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
                            if packed_what_command_info == 1:
                                if packed_command == 1:
                                    pattern_row[1][packed_what_channel][3]['tracker_speed'] = packed_info
                                    pattern_row[0]['tracker_speed'] = packed_info
                                if packed_command == 3:
                                    pattern_row[1][packed_what_channel][3]['tracker_break_to_row'] = packed_info
                                    pattern_row[0]['tracker_break_to_row'] = packed_info
                    firstrow = 0
                    patterntable_single.append(pattern_row)
                    rowcount += 1
            patterntable_all.append(patterntable_single)
            patterncount += 1
        print(' ')
        
        cvpj_l_playlist = song_tracker.song2playlist(patterntable_all, 32, t_orderlist, startinststr, [0.65, 0.57, 0.33])

        patlentable = song_tracker.get_len_table(patterntable_all, t_orderlist)

        cvpj_l['title'] = s3m_name

        cvpj_l['timemarkers'] = placements.make_timemarkers([4,4], patlentable, None)
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = s3m_tempo
        return json.dumps(cvpj_l)
