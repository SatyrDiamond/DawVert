# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import json
from functions import song_tracker
from functions import audio_wav
from functions import data_bytes
from functions import folder_samples
from functions import placements
from functions import tracks

t_retg_alg = [['mul', 1], ['minus', 1], ['minus', 2], ['minus', 4], ['minus', 8], ['minus', 16], ['mul', 2/3], ['mul', 1/2], ['mul', 1], ['plus', 1], ['plus', 2], ['plus', 4], ['plus', 8], ['plus', 16], ['mul', 3/2], ['mul', 2]]

class input_s3m(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 's3m'
    def getname(self): return 'Scream Tracker 3 Module'
    def gettype(self): return 'm'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': True,
        'placement_cut': False,
        'placement_loop': False,
        'no_pl_auto': False,
        'no_placements': False
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
        
        s3m_modulename = os.path.splitext(os.path.basename(input_file))[0]
        samplefolder = folder_samples.samplefolder(extra_param, s3m_modulename)

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

            cvpj_l_instruments[cvpj_instid] = {}
            cvpj_l_single_inst = cvpj_l_instruments[cvpj_instid]
            cvpj_l_instrumentsorder.append(cvpj_instid)

            if s3m_inst_type == 0: print("[input-st3] Message #" + str(s3m_numinst) + ': "' + s3m_inst_name + '", Filename:"' + s3m_inst_filename+ '"')
            else: print("[input-st3] Instrument #" + str(s3m_numinst) + ': "' + s3m_inst_name + '", Filename:"' + s3m_inst_filename+ '"')
            table_defualtvol.append(s3m_inst_vol)

            if s3m_inst_filename != '': cvpj_l_single_inst['name'] = s3m_inst_filename
            elif s3m_inst_name != '': cvpj_l_single_inst['name'] = s3m_inst_name
            else: cvpj_l_single_inst['name'] = ' '

            cvpj_l_single_inst['vol'] = 0.3
            cvpj_l_single_inst['instdata'] = {}
            cvpj_l_inst = cvpj_l_single_inst['instdata']
            cvpj_l_inst['plugindata'] = {}
            cvpj_l_plugin = cvpj_l_inst['plugindata']
            cvpj_l_plugin['trigger'] = 'normal'
            cvpj_l_plugin['point_value_type'] = "samples"

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
                    loopdata = {'loop':[s3m_inst_loopStart, s3m_inst_loopEnd-1]}
                else:
                    cvpj_l_plugin['loop']['enabled'] = 0
                    loopdata = None
                print("[input-st3] Ripping Sample " + str(s3m_numinst))
                bio_mainfile.seek(cvpj_inst_samplelocation)
                os.makedirs(samplefolder, exist_ok=True)
                wave_path = samplefolder + str(s3m_numinst).zfill(2) + '.wav'

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

                                if packed_command == 1:
                                    pattern_row[0]['speed'] = packed_info
                                    current_speed = packed_info

                                if packed_command == 2: 
                                    pattern_row[0]['pattern_jump'] = packed_info

                                if packed_command == 3:
                                    pattern_row[0]['break_to_row'] = packed_info

                                if packed_command == 4: 
                                    j_note_cmdval['vol_slide'] = song_tracker.getfineval(packed_info)

                                if packed_command == 5:
                                    j_note_cmdval['slide_down_cont'] = song_tracker.calcbendpower_down(packed_info, current_speed)

                                if packed_command == 6:
                                    j_note_cmdval['slide_up_cont'] = song_tracker.calcbendpower_up(packed_info, current_speed)

                                if packed_command == 7:
                                    j_note_cmdval['slide_to_note'] = song_tracker.calcslidepower(packed_info, current_speed)
                            
                                if packed_command == 8: 
                                    vibrato_params = {}
                                    vibrato_params['speed'], vibrato_params['depth'] = data_bytes.splitbyte(packed_info)
                                    j_note_cmdval['vibrato'] = vibrato_params
                                
                                if packed_command == 9: 
                                    tremor_params = {}
                                    tremor_params['ontime'], tremor_params['offtime'] = data_bytes.splitbyte(packed_info)
                                    j_note_cmdval['tremor'] = tremor_params
                            
                                if packed_command == 10: 
                                    arp_params = [0,0]
                                    arp_params[0], arp_params[1] = data_bytes.splitbyte(packed_info)
                                    j_note_cmdval['arp'] = arp_params
                            
                                if packed_command == 11: 
                                    j_note_cmdval['vol_slide'] = song_tracker.getfineval(packed_info)
                                    j_note_cmdval['vibrato'] = {'speed': 0, 'depth': 0}
                            
                                if packed_command == 12: 
                                    j_note_cmdval['vol_slide'] = song_tracker.getfineval(packed_info)
                                    j_note_cmdval['slide_to_note'] = song_tracker.getfineval(packed_info)

                                if packed_command == 13: 
                                    j_note_cmdval['channel_vol'] = packed_info/64

                                if packed_command == 14: 
                                    j_note_cmdval['channel_vol_slide'] = song_tracker.getfineval(packed_info)

                                if packed_command == 15: 
                                    j_note_cmdval['sample_offset'] = packed_info*256

                                if packed_command == 16: 
                                    j_note_cmdval['pan_slide'] = song_tracker.getfineval(packed_info)*-1

                                if packed_command == 17: 
                                    retrigger_params = {}
                                    retrigger_alg, retrigger_params['speed'] = data_bytes.splitbyte(packed_info)
                                    retrigger_params['alg'], retrigger_params['val'] = t_retg_alg[retrigger_alg]
                                    j_note_cmdval['retrigger'] = retrigger_params
                            
                                if packed_command == 18: 
                                    tremolo_params = {}
                                    tremolo_params['speed'], tremolo_params['depth'] = data_bytes.splitbyte(packed_info)
                                    j_note_cmdval['tremolo'] = tremolo_params

                                if packed_command == 19: 
                                    ext_type, ext_value = data_bytes.splitbyte(packed_info)
                                    if ext_type == 1: j_note_cmdval['glissando_control'] = ext_value
                                    if ext_type == 2: j_note_cmdval['set_finetune'] = ext_value
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

                                if packed_command == 21: 
                                    fine_vib_sp, fine_vib_de = data_bytes.splitbyte(packed_info)
                                    vibrato_params = {}
                                    vibrato_params['speed'] = fine_vib_sp/15
                                    vibrato_params['depth'] = fine_vib_sp/15
                                    j_note_cmdval['vibrato'] = vibrato_params

                                if packed_command == 22: 
                                    pattern_row[0]['global_volume'] = packed_info/64
                            
                                if packed_command == 23: 
                                    pattern_row[0]['global_volume_slide'] = song_tracker.getfineval(packed_info)

                                if packed_command == 24: 
                                    j_note_cmdval['set_pan'] = packed_info/255

                                if packed_command == 25: 
                                    panbrello_params = {}
                                    panbrello_params['speed'], panbrello_params['depth'] = data_bytes.splitbyte(packed_info)
                                    j_note_cmdval['panbrello'] = panbrello_params

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

        cvpj_l = {}

        tracks.a_add_auto_pl(cvpj_l, 'main', None, 'bpm', song_tracker.tempo_auto(patterntable_all, t_orderlist, s3m_speed, s3m_tempo))

        placements.make_timemarkers(cvpj_l, [4,16], patlentable, None)
        
        cvpj_l['info'] = {}
        cvpj_l['info']['title'] = s3m_name

        cvpj_l['do_addloop'] = True
        cvpj_l['do_lanefit'] = True

        cvpj_l['use_fxrack'] = False
        cvpj_l['use_instrack'] = False
        
        cvpj_l['instruments_data'] = cvpj_l_instruments
        cvpj_l['instruments_order'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = s3m_tempo
        return json.dumps(cvpj_l)
