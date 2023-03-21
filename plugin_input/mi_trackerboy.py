# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import song_tracker
from functions import tracks
import plugin_input
import json
import struct

chiptypecolors = {}
chiptypecolors['pulse'] = [0.40, 1.00, 0.20]
chiptypecolors['noise'] = [0.80, 0.80, 0.80]
chiptypecolors['wavetable'] = [1.00, 0.50, 0.20]

chipname = {}
chipname['pulse'] = 'Pulse'
chipname['noise'] = 'Noise'
chipname['wavetable'] = 'Wavetable'

replace_duty = {0:0, 1:1, 2:2, 3:1}
replace_vol = {0:0, 1:15, 2:15, 3:15}
replace_duty_get = replace_duty.get
replace_vol_get = replace_vol.get


def splitbyte(value):
    first = value >> 4
    second = value & 0x0F
    return (first, second)

def readstring(bio_data):
    tb_namelen = int.from_bytes(bio_data.read(2), "little")
    tb_name = bio_data.read(tb_namelen).decode("utf-8")
    return tb_name

def speed_to_tempo(framerate, speed):
    return (framerate * 60.0) / (speed * 5)

def parse_fx_event(l_celldata, fx_p, fx_v):
    if fx_p == 1: l_celldata[0]['pattern_jump'] = fx_v
    if fx_p == 2: l_celldata[0]['stop'] = fx_v
    if fx_p == 3: l_celldata[0]['skip_pattern'] = fx_v
    if fx_p == 4: l_celldata[0]['tempo'] = speed_to_tempo(60, fx_v)*20

    if fx_p == 13:
        arp_params = [0,0]
        arp_params[0], arp_params[1] = splitbyte(fx_v)
        l_celldata[1][2]['arp'] = arp_params
    if fx_p == 14: l_celldata[1][2]['slide_up_persist'] = fx_v
    if fx_p == 15: l_celldata[1][2]['slide_down_persist'] = fx_v
    if fx_p == 16: l_celldata[1][2]['slide_to_note_persist'] = fx_v
    if fx_p == 17:
        fine_vib_sp, fine_vib_de = splitbyte(fx_v)
        vibrato_params = {}
        vibrato_params['speed'] = fine_vib_sp/16
        vibrato_params['depth'] = fine_vib_sp/16
        l_celldata[1][2]['vibrato'] = vibrato_params
    if fx_p == 18: l_celldata[1][2]['vibrato_delay'] = fx_v

    if fx_p == 22: 
        vol_left, vol_right = splitbyte(fx_v)
        if vol_left < 0: vol_left += 16
        if vol_right < 0: vol_right += 16
        vol_left = vol_left/15
        vol_right = vol_right/15
        val_vol = max(vol_left, vol_right)
        if val_vol != 0: 
            vol_left = vol_left/val_vol
            vol_right = vol_right/val_vol
        pan_val = (vol_left*-1)+vol_right
        l_celldata[0]['global_volume'] = val_vol
        l_celldata[0]['global_pan'] = pan_val

class input_trackerboy(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'trackerboy'
    def getname(self): return 'TrackerBoy'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(12)
        if bytesdata == b'\x00TRACKERBOY\x00': return True
        else: return False
    def parse(self, input_file, extra_param):
        song_file = open(input_file, 'rb')

        cvpj_l = {}
        cvpj_l_instrument_data = {}
        cvpj_l_instrument_order = []

        trackerboy_header = song_file.read(12)

        song_file.seek(24)
        trackerboy_m_rev = song_file.read(1)
        trackerboy_n_rev = song_file.read(1)
        song_file.read(2)
        trackerboy_title = song_file.read(32).split(b'\x00' * 1)[0].decode("utf-8")
        print("[input-trackerboy] Title: " + str(trackerboy_title))
        trackerboy_artist = song_file.read(32).split(b'\x00' * 1)[0].decode("utf-8")
        print("[input-trackerboy] Artist: " + str(trackerboy_artist))
        trackerboy_copyright = song_file.read(32).split(b'\x00' * 1)[0].decode("utf-8")
        print("[input-trackerboy] Copyright: " + str(trackerboy_copyright))
        trackerboy_icount = song_file.read(1)[0]
        print("[input-trackerboy] Instrument Count: " + str(trackerboy_icount))
        trackerboy_scount = song_file.read(1)[0]
        print("[input-trackerboy] Song Count: " + str(trackerboy_scount))
        trackerboy_wcount = song_file.read(1)[0]
        print("[input-trackerboy] Waveform Count: " + str(trackerboy_wcount))
        trackerboy_system = song_file.read(1)[0]
        print("[input-trackerboy] System: " + str(trackerboy_system))

        mt_pat = {}
        mt_ord = {}
        mt_ch_insttype = ['pulse','pulse','wavetable','noise']
        mt_ch_names = ['Pulse 1','Pulse 2','Wavetable','Noise']
        mt_type_colors = chiptypecolors

        mt_pat[0] = {}
        mt_pat[1] = {}
        mt_pat[2] = {}
        mt_pat[3] = {}

        if 'songnum' in extra_param: selectedsong = int(extra_param['songnum'])
        else: selectedsong = 1

        songnum = 1

        t_instruments = {}

        song_file.seek(160)
        trackerboy_chunks = data_bytes.riff_read(song_file.read(), 0)

        for trackerboy_chunk in trackerboy_chunks:
            #print(trackerboy_chunk[0])
        
            if trackerboy_chunk[0] == b'INST':
                tb_instdata = data_bytes.bytearray2BytesIO(trackerboy_chunk[1])
                tb_id = tb_instdata.read(1)[0]+1
                print("[input-trackerboy] Inst " + str(tb_id) + ':')
                tb_name = readstring(tb_instdata)
                print("[input-trackerboy]     Name: " + str(tb_name))
                tb_channel = tb_instdata.read(1)[0]
                print("[input-trackerboy]     Channel: " + str(tb_channel))
                tb_envelopeEnabled = tb_instdata.read(1)[0]
                print("[input-trackerboy]     Envelope Enabled: " + str(tb_envelopeEnabled))
                tb_envelope = tb_instdata.read(1)[0]

                tb_volinit, tb_volper = splitbyte(tb_envelope)
                print("[input-trackerboy]     Vol Env S: " + str(tb_volinit))
                print("[input-trackerboy]     Vol Env P: " + str(tb_volper))

                t_instruments[tb_id] = [tb_name]
                for _ in range(4):
                    envlength = int.from_bytes(tb_instdata.read(2), "little")
                    loopEnabled = tb_instdata.read(1)[0]
                    loopIndex = tb_instdata.read(1)[0]
                    envdata = struct.unpack('b'*envlength, tb_instdata.read(envlength))
                    t_instruments[tb_id].append([envdata, loopEnabled, loopIndex])

                t_instruments[tb_id].append(tb_volinit)
                t_instruments[tb_id].append(tb_volper)

        
            if trackerboy_chunk[0] == b'SONG':
                if songnum == selectedsong:
                    #print(trackerboy_chunk[1])
                    tb_songdata = data_bytes.bytearray2BytesIO(trackerboy_chunk[1])
                    tb_name = readstring(tb_songdata)
                    tb_beat = tb_songdata.read(1)[0]
                    tb_measure = tb_songdata.read(1)[0]
                    tb_speed = tb_songdata.read(1)[0]
                    tb_len = tb_songdata.read(1)[0]+1
                    tb_rows = tb_songdata.read(1)[0]+1

                    print("[input-trackerboy] Song:")
                    print("[input-trackerboy]     Name: " + str(tb_name))
                    print("[input-trackerboy]     Beats: " + str(tb_beat))
                    print("[input-trackerboy]     Measure: " + str(tb_measure))
                    print("[input-trackerboy]     Length: " + str(tb_len))
                    print("[input-trackerboy]     Speed: " + str(tb_speed))
                    print("[input-trackerboy]     Rows: " + str(tb_rows))
        
                    tb_pat_num = int.from_bytes(tb_songdata.read(2), "little")
            
                    tb_numfxareas = tb_songdata.read(1)[0]
        
                    tb_nfa1 = (tb_numfxareas & 0x03)
                    tb_nfa2 = (tb_numfxareas & 0x0c) >> 2
                    tb_nfa3 = (tb_numfxareas & 0x30) >> 4
                    tb_nfa4 = (tb_numfxareas & 0xc0) >> 6
        
                    print("[input-trackerboy]     FXA:",tb_nfa1,tb_nfa2,tb_nfa3,tb_nfa4)
        
                    CH1_order = []
                    CH2_order = []
                    CH3_order = []
                    CH4_order = []
        
                    for _ in range(tb_len):
                        CH1_onum, CH2_onum, CH3_onum, CH4_onum = struct.unpack('bbbb', tb_songdata.read(4))
                        CH1_order.append(CH1_onum)
                        CH2_order.append(CH2_onum)
                        CH3_order.append(CH3_onum)
                        CH4_order.append(CH4_onum)
        
                    mt_ord[0] = CH1_order
                    mt_ord[1] = CH2_order
                    mt_ord[2] = CH3_order
                    mt_ord[3] = CH4_order

                    print("[input-trackerboy]     Order Square1:",CH1_order)
                    print("[input-trackerboy]     Order Square2:",CH2_order)
                    print("[input-trackerboy]     Order Wave:",CH3_order)
                    print("[input-trackerboy]     Order Noise:",CH4_order)

                    for ch_num in range(4):
                        mt_pat[ch_num] = {}
                        for pat_num in range(tb_pat_num):
                            pattern_row = []
                            for _ in range(tb_rows): pattern_row.append([{},[None, None, {}, {}]])
                            mt_pat[ch_num][pat_num] = pattern_row

                    for _ in range(tb_pat_num):
                        tb_pate_ch, tb_pate_trkid, tb_pate_rows = struct.unpack('bbb', tb_songdata.read(3))
                        #print(tb_pate_ch, tb_pate_trkid, tb_pate_rows)

                        for _ in range(tb_pate_rows+1):
                            n_pos, n_key, n_inst, fx1p, fx1v, fx2p, fx2v, fx3p, fx3v = struct.unpack('bbbbbbbbb', tb_songdata.read(9))
                            trkr_cell = mt_pat[tb_pate_ch][tb_pate_trkid][n_pos]

                            trkr_cell_g = trkr_cell[0]
                            trkr_cell_d = trkr_cell[1]

                            if n_key != 0:
                                if n_key == 85: trkr_cell_d[0] = 'Off'
                                else: trkr_cell_d[0] = n_key-25
                            trkr_cell_d[1] = n_inst

                            parse_fx_event(trkr_cell, fx1p, fx1v)
                            parse_fx_event(trkr_cell, fx2p, fx2v)
                            parse_fx_event(trkr_cell, fx3p, fx3v)

                            #print(mt_pat[tb_pate_ch][tb_pate_trkid][n_pos])

                songnum += 1

        song_tracker.multi_convert(cvpj_l, tb_rows, mt_pat, mt_ord, mt_ch_insttype, mt_ch_names, mt_type_colors)

        total_used_instruments = song_tracker.get_multi_used_instruments()

        #print(t_instruments)
        for total_used_instrument in total_used_instruments:
            insttype = total_used_instrument[0]
            instid = total_used_instrument[1]
            if int(instid) in t_instruments:
                trackerboy_instdata = t_instruments[int(instid)]

                cvpj_instid = insttype+'_'+instid
                cvpj_instname = trackerboy_instdata[0]+' ('+chipname[insttype]+')'
                if insttype in chiptypecolors: cvpj_instcolor = chiptypecolors[insttype]
                else: cvpj_instcolor = None

                cvpj_instdata = {}
                cvpj_instdata["plugin"] = 'gameboy'

                plugindata =  {}

                if insttype == 'pulse': plugindata['wave'] = 'square'
                if insttype == 'noise': plugindata['wave'] = 'noise'
                if insttype == 'wavetable': plugindata['wave'] = 'square'

                if trackerboy_instdata[1][0] != ():
                    plugindata['env_arp'] = {}
                    plugindata['env_arp']['values'] = trackerboy_instdata[1][0]

                if trackerboy_instdata[2][0] != ():
                    voldata = trackerboy_instdata[2][0]
                    plugindata['env_vol'] = {}
                    plugindata['env_vol']['values'] = [replace_vol_get(n, n) for n in voldata]
 
                if trackerboy_instdata[4][0] != ():
                    dutydata = trackerboy_instdata[4][0]
                    plugindata['env_duty'] = {}
                    plugindata['env_duty']['values'] = [replace_duty_get(n, n) for n in dutydata]

                if trackerboy_instdata[6] == 0:
                    plugindata['attack'] = 0
                    plugindata['decay'] = 0
                    plugindata['sustain'] = 1
                    plugindata['release'] = 0
                    
                elif trackerboy_instdata[6] < 8:
                    plugindata['attack'] = 0
                    plugindata['decay'] = trackerboy_instdata[6]/5
                    plugindata['sustain'] = 0
                    plugindata['release'] = 0

                elif trackerboy_instdata[6] >= 8:
                    plugindata['attack'] = (trackerboy_instdata[6]-8)/5
                    plugindata['decay'] = 0
                    plugindata['sustain'] = 1
                    plugindata['release'] = 0

                cvpj_instdata["plugindata"] = plugindata

                tracks.m_addinst(cvpj_l, cvpj_instid, cvpj_instdata)
                tracks.m_addinst_data(cvpj_l, cvpj_instid, cvpj_instname, cvpj_instcolor, 0.4, 0.0)

        cvpj_l['info'] = {}
        cvpj_l['info']['title'] = trackerboy_title
        cvpj_l['info']['author'] = trackerboy_artist
        cvpj_l['info']['copyright'] = trackerboy_copyright

        cvpj_l['do_addwrap'] = True
        cvpj_l['do_lanefit'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False

        cvpj_l['bpm'] = speed_to_tempo(60, tb_speed)*20
        return json.dumps(cvpj_l)
