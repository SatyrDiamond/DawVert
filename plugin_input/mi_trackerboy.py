# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import song_tracker
from functions import plugins
from functions import song
from functions import xtramath
from functions_tracks import tracks_mi
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

def speed_to_tempo(framerate, speed):
    return (framerate * 60.0) / (speed * 5)

def parse_fx_event(l_celldata, fx_p, fx_v):
    if fx_p == 1: l_celldata[0]['pattern_jump'] = fx_v
    if fx_p == 2: l_celldata[0]['stop'] = fx_v
    if fx_p == 3: l_celldata[0]['skip_pattern'] = fx_v
    if fx_p == 4: l_celldata[0]['tempo'] = speed_to_tempo(60, fx_v)*20

    if fx_p == 13:
        arp_params = [0,0]
        arp_params[0], arp_params[1] = data_bytes.splitbyte(fx_v)
        l_celldata[1][2]['arp'] = arp_params
    if fx_p == 14: l_celldata[1][2]['slide_up_persist'] = fx_v
    if fx_p == 15: l_celldata[1][2]['slide_down_persist'] = fx_v
    if fx_p == 16: l_celldata[1][2]['slide_to_note_persist'] = fx_v
    if fx_p == 17:
        fine_vib_sp, fine_vib_de = data_bytes.splitbyte(fx_v)
        vibrato_params = {}
        vibrato_params['speed'] = fine_vib_sp/16
        vibrato_params['depth'] = fine_vib_sp/16
        l_celldata[1][2]['vibrato'] = vibrato_params
    if fx_p == 18: l_celldata[1][2]['vibrato_delay'] = fx_v

    if fx_p == 22: 
        vol_left, vol_right = data_bytes.splitbyte(fx_v)
        if vol_left < 0: vol_left += 16
        if vol_right < 0: vol_right += 16
        l_celldata[0]['global_pan'], l_celldata[0]['global_volume'] = xtramath.sep_pan_to_vol(vol_left/15, vol_right/15)

class input_trackerboy(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'trackerboy'
    def getname(self): return 'TrackerBoy'
    def gettype(self): return 'mi'
    def getdawcapabilities(self): 
        return {
        'track_lanes': True
        }
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
        trackerboy_title = data_bytes.readstring_fixedlen(song_file, 23, "utf-8")
        print("[input-trackerboy] Title: " + str(trackerboy_title))
        trackerboy_artist = data_bytes.readstring_fixedlen(song_file, 23, "utf-8")
        print("[input-trackerboy] Artist: " + str(trackerboy_artist))
        trackerboy_copyright = data_bytes.readstring_fixedlen(song_file, 23, "utf-8")
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

        song_file.seek(160)
        trackerboy_chunks = data_bytes.riff_read(song_file.read(), 0)

        t_waves = {}
        t_instruments = {}
        for trackerboy_chunk in trackerboy_chunks:
            if trackerboy_chunk[0] == b'INST':
                tb_instdata = data_bytes.to_bytesio(trackerboy_chunk[1])
                tb_id = tb_instdata.read(1)[0]+1
                print("[input-trackerboy] Inst " + str(tb_id) + ':')
                tb_name = data_bytes.readstring_lenbyte(tb_instdata, 2, "little", None)
                print("[input-trackerboy]     Name: " + str(tb_name))
                tb_channel = tb_instdata.read(1)[0]
                print("[input-trackerboy]     Channel: " + str(tb_channel))
                tb_envelopeEnabled = tb_instdata.read(1)[0]
                tb_envelope = tb_instdata.read(1)[0]
                if tb_channel != 2:
                    tb_param1, tb_param2 = data_bytes.splitbyte(tb_envelope)
                    print("[input-trackerboy]     Envelope Enabled: " + str(tb_envelopeEnabled))
                    print("[input-trackerboy]     Vol Env S: " + str(tb_param1))
                    print("[input-trackerboy]     Vol Env P: " + str(tb_param2))
                else:
                    tb_param1 = 0
                    tb_param2 = tb_envelope
                    print("[input-trackerboy]     Set Waveform: " + str(tb_envelopeEnabled))
                    print("[input-trackerboy]     Wave #: " + str(tb_param2))
                t_instruments[tb_id] = [tb_name]
                for _ in range(4):
                    envlength = int.from_bytes(tb_instdata.read(2), "little")
                    loopEnabled = tb_instdata.read(1)[0]
                    loopIndex = tb_instdata.read(1)[0]
                    envdata = struct.unpack('b'*envlength, tb_instdata.read(envlength))
                    t_instruments[tb_id].append([envdata, loopEnabled, loopIndex])
                t_instruments[tb_id].append(tb_param1)
                t_instruments[tb_id].append(tb_param2)
        
            if trackerboy_chunk[0] == b'SONG':
                if songnum == selectedsong:
                    #print(trackerboy_chunk[1])
                    tb_songdata = data_bytes.to_bytesio(trackerboy_chunk[1])
                    print("[input-trackerboy] Song:")
                    tb_name = data_bytes.readstring_lenbyte(tb_songdata, 2, "little", None)
                    print("[input-trackerboy]     Name: " + str(tb_name))
                    tb_beat = tb_songdata.read(1)[0]
                    print("[input-trackerboy]     Beats: " + str(tb_beat))
                    tb_measure = tb_songdata.read(1)[0]
                    print("[input-trackerboy]     Measure: " + str(tb_measure))
                    tb_speed = tb_songdata.read(1)[0]
                    print("[input-trackerboy]     Speed: " + str(tb_speed))
                    tb_len = tb_songdata.read(1)[0]+1
                    print("[input-trackerboy]     Length: " + str(tb_len))
                    tb_rows = tb_songdata.read(1)[0]+1
                    print("[input-trackerboy]     Rows: " + str(tb_rows))
                    tb_pat_num = int.from_bytes(tb_songdata.read(2), "little")
                    tb_numfxareas = tb_songdata.read(1)[0]

                    mt_ord = {0: [], 1: [], 2: [], 3: []}
                    for _ in range(tb_len):
                        mt_ord[0].append(tb_songdata.read(1)[0])
                        mt_ord[1].append(tb_songdata.read(1)[0])
                        mt_ord[2].append(tb_songdata.read(1)[0])
                        mt_ord[3].append(tb_songdata.read(1)[0])

                    print("[input-trackerboy]     Order Square1:",mt_ord[0])
                    print("[input-trackerboy]     Order Square2:",mt_ord[1])
                    print("[input-trackerboy]     Order Wave:",mt_ord[2])
                    print("[input-trackerboy]     Order Noise:",mt_ord[3])

                    for ch_num in range(4):
                        mt_pat[ch_num] = {}
                        for pat_num in range(tb_pat_num):
                            pattern_row = []
                            for _ in range(tb_rows): pattern_row.append([{},[None, None, {}, {}]])
                            mt_pat[ch_num][pat_num] = pattern_row

                    for _ in range(tb_pat_num):
                        tb_pate_ch, tb_pate_trkid, tb_pate_rows = struct.unpack('bbb', tb_songdata.read(3))
                        for _ in range(tb_pate_rows+1):
                            n_pos, n_key, n_inst, fx1p, fx1v, fx2p, fx2v, fx3p, fx3v = struct.unpack('bbbbbbbbb', tb_songdata.read(9))
                            trkr_cell = mt_pat[tb_pate_ch][tb_pate_trkid][n_pos]
                            trkr_cell_d = trkr_cell[1]
                            if n_key != 0:
                                if n_key == 85: trkr_cell_d[0] = 'Off'
                                else: trkr_cell_d[0] = n_key-25
                            trkr_cell_d[1] = n_inst
                            parse_fx_event(trkr_cell, fx1p, fx1v)
                            parse_fx_event(trkr_cell, fx2p, fx2v)
                            parse_fx_event(trkr_cell, fx3p, fx3v)

                songnum += 1

            if trackerboy_chunk[0] == b'WAVE':
                tb_instdata = data_bytes.to_bytesio(trackerboy_chunk[1])
                tb_id = tb_instdata.read(1)[0]+1
                print("[input-trackerboy] Wave " + str(tb_id) + ':')
                tb_name = data_bytes.readstring_lenbyte(tb_instdata, 2, "little", None)
                print("[input-trackerboy]     Name: " + str(tb_name))
                tb_wave = []
                for wavepoint in list(tb_instdata.read(16)):
                    splitwave = data_bytes.splitbyte(wavepoint)
                    tb_wave.append(splitwave[0])
                    tb_wave.append(splitwave[1])
                print("[input-trackerboy]     Data: " + str(tb_wave))
                t_waves[tb_id] = [tb_name, tb_wave]

        len_table = song_tracker.multi_get_len_table(tb_rows, mt_pat, mt_ord, mt_ch_insttype)

        song_tracker.multi_convert(cvpj_l, tb_rows, mt_pat, mt_ord, mt_ch_insttype, len_table)

        total_used_instruments = song_tracker.get_multi_used_instruments()

        for total_used_instrument in total_used_instruments:
            insttype = total_used_instrument[0]
            instid = total_used_instrument[1]
            if int(instid) in t_instruments:
                trackerboy_instdata = t_instruments[int(instid)]

                cvpj_instid = insttype+'_'+instid
                cvpj_instname = trackerboy_instdata[0]+' ('+chipname[insttype]+')'
                if insttype in chiptypecolors: cvpj_instcolor = chiptypecolors[insttype]
                else: cvpj_instcolor = None

                pluginid = plugins.get_id()
                plugins.add_plug(cvpj_l, pluginid, 'retro', insttype)

                if trackerboy_instdata[1][0] != (): 
                    plugins.add_env_blocks(cvpj_l, pluginid, 'arp', trackerboy_instdata[1][0], None, None, None)

                if trackerboy_instdata[2][0] != (): 
                    plugins.add_env_blocks(cvpj_l, pluginid, 'pan', trackerboy_instdata[2][0], None, None, None)

                if trackerboy_instdata[3][0] != (): 
                    plugins.add_env_blocks(cvpj_l, pluginid, 'pitch', trackerboy_instdata[4][0], None, None, None)

                if trackerboy_instdata[4][0] != (): 
                    if insttype == 'pulse': 
                        plugins.add_env_blocks(cvpj_l, pluginid, 'duty', trackerboy_instdata[4][0], 4, None, None)
                    if insttype == 'wavetable':
                        plugins.add_env_blocks(cvpj_l, pluginid, 'vol', trackerboy_instdata[4][0], 3, None, None)
                    if insttype == 'noise': 
                        plugins.add_env_blocks(cvpj_l, pluginid, 'noise', trackerboy_instdata[4][0], 3, None, None)

                if insttype != 'wavetable':
                    env_attack = 0
                    env_decay = 0
                    env_sustain = 1

                    if trackerboy_instdata[6] == 0: env_sustain = 1
                    elif trackerboy_instdata[6] < 8: env_decay = trackerboy_instdata[6]/5
                    elif trackerboy_instdata[6] >= 8:
                        env_attack = (trackerboy_instdata[6]-8)/5
                        env_sustain = 1
                    plugins.add_asdr_env(cvpj_l, pluginid, 'vol', 0, env_attack, 0, env_decay, env_sustain, 0, 1)
                else:
                    if trackerboy_instdata[6] == 0: 
                        plugins.add_wave(cvpj_l, pluginid, 'main', t_waves[1][1], 0, 15)
                    else: 
                        plugins.add_wave(cvpj_l, pluginid, 'main', t_waves[trackerboy_instdata[6]+1][1], 0, 15)

                tracks_mi.inst_create(cvpj_l, cvpj_instid)
                tracks_mi.inst_visual(cvpj_l, cvpj_instid, name=cvpj_instname, color=cvpj_instcolor)
                tracks_mi.inst_pluginid(cvpj_l, cvpj_instid, pluginid)
                tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'vol', 0.4, 'float')

        song.add_info(cvpj_l, 'title', trackerboy_title)
        song.add_info(cvpj_l, 'author', trackerboy_artist)
        song.add_info(cvpj_l, 'copyright', trackerboy_copyright)

        cvpj_l['do_addloop'] = True
        cvpj_l['do_lanefit'] = True
        
        song.add_param(cvpj_l, 'bpm', speed_to_tempo(60, tb_speed)*20)
        return json.dumps(cvpj_l)
