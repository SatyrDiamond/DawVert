# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import xtramath
import plugin_input
import json
import struct
from objects import dv_dataset
from objects import dv_trackerpattern

def speed_to_tempo(framerate, speed):
    return (framerate * 60.0) / (speed * 5)

def parse_fx_event(l_celldata, fx_p, fx_v):
    if fx_p == 1: l_celldata.cell_g_param('pattern_jump', fx_v)
    if fx_p == 2: l_celldata.cell_g_param('stop', fx_v)
    if fx_p == 3: l_celldata.cell_g_param('skip_pattern', fx_v)
    if fx_p == 4: l_celldata.cell_g_param('tempo', speed_to_tempo(60, fx_v)*20)

    if fx_p == 13:
        arp_params = [0,0]
        arp_params[0], arp_params[1] = data_bytes.splitbyte(fx_v)
        l_celldata.cell_param(0, 'arp', [rp_params[0], arp_params[1]])
    if fx_p == 14: l_celldata.cell_param(0, 'slide_up_persist', fx_v)
    if fx_p == 15: l_celldata.cell_param(0, 'slide_down_persist', fx_v)
    if fx_p == 16: l_celldata.cell_param(0, 'slide_to_note_persist', fx_v)
    if fx_p == 17:
        fine_vib_sp, fine_vib_de = data_bytes.splitbyte(fx_v)
        vibrato_params = {}
        vibrato_params['speed'] = fine_vib_sp/16
        vibrato_params['depth'] = fine_vib_sp/16
        l_celldata.cell_param(0, 'vibrato', vibrato_params)
    if fx_p == 18: l_celldata.cell_param(0, 'vibrato_delay', fx_v)

    if fx_p == 22: 
        vol_left, vol_right = data_bytes.splitbyte(fx_v)
        if vol_left < 0: vol_left += 16
        if vol_right < 0: vol_right += 16
        out_pan, out_vol = xtramath.sep_pan_to_vol(vol_left/15, vol_right/15)
        l_celldata.cell_g_param('global_pan', out_pan)
        l_celldata.cell_g_param('global_vol', out_vol)

class input_trackerboy(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'trackerboy'
    def getname(self): return 'TrackerBoy'
    def gettype(self): return 'rm'
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
    def parse(self, convproj_obj, input_file, extra_param):
        convproj_obj.set_timings(4, False)

        song_file = open(input_file, 'rb')

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

        dataset = dv_dataset.dataset('./data_dset/trackerboy.dset')
        multitrkdata = dv_trackerpattern.multipatterndata(['pulse','pulse','wavetable','noise'], dataset, 64)

        selectedsong = int(extra_param['songnum']) if 'songnum' in extra_param else 1

        songnum = 1

        song_file.seek(160)
        trackerboy_chunks = data_bytes.riff_read(song_file.read(), 0)

        songfound = False

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
                    songfound = True
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

                    mt_ord = [[],[],[],[]]
                    for _ in range(tb_len):
                        mt_ord[0].append(tb_songdata.read(1)[0])
                        mt_ord[1].append(tb_songdata.read(1)[0])
                        mt_ord[2].append(tb_songdata.read(1)[0])
                        mt_ord[3].append(tb_songdata.read(1)[0])

                    print("[input-trackerboy]     Order Square1:",mt_ord[0])
                    print("[input-trackerboy]     Order Square2:",mt_ord[1])
                    print("[input-trackerboy]     Order Wave:",mt_ord[2])
                    print("[input-trackerboy]     Order Noise:",mt_ord[3])

                    for _ in range(tb_pat_num):
                        tb_pate_ch, tb_pate_trkid, tb_pate_rows = struct.unpack('bbb', tb_songdata.read(3))
                        multitrkdata.mul_pd[tb_pate_ch].pattern_add(tb_pate_trkid, 64)
                        for _ in range(tb_pate_rows+1):
                            n_pos, n_key, n_inst, fx1p, fx1v, fx2p, fx2v, fx3p, fx3v = struct.unpack('bbbbbbbbb', tb_songdata.read(9))
                            multitrkdata.mul_pd[tb_pate_ch].row_set_cur(n_pos)
                            multitrkdata.mul_pd[tb_pate_ch].cell_note(0, 'off' if n_key == 85 else n_key-25, n_inst)
                            parse_fx_event(multitrkdata.mul_pd[tb_pate_ch], fx1p, fx1v)
                            parse_fx_event(multitrkdata.mul_pd[tb_pate_ch], fx2p, fx2v)
                            parse_fx_event(multitrkdata.mul_pd[tb_pate_ch], fx3p, fx3v)

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

        if songfound: 
            multitrkdata.to_cvpj(convproj_obj, mt_ord, 120, 3)
        else:
            print('[error] Song #'+str(selectedsong)+' not found.')
            exit()

        for total_used_instrument in multitrkdata.used_inst:

            insttype = total_used_instrument[0]
            instid = total_used_instrument[1]
            if instid in t_instruments:
                trackerboy_instdata = t_instruments[instid]

                s_chip_name, s_chip_color = dataset.object_get_name_color('chip', insttype)

                cvpj_instid = insttype+'_'+str(instid)
                cvpj_instname = trackerboy_instdata[0]
                if s_chip_name != None: cvpj_instname += ' ('+s_chip_name+')'
                cvpj_instcolor = s_chip_color

                inst_obj = convproj_obj.add_instrument(cvpj_instid)
                inst_obj.visual.name = cvpj_instname
                inst_obj.visual.color = cvpj_instcolor
                inst_obj.params.add('vol', 0.4, 'float')

                plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')

                if trackerboy_instdata[1][0] != (): 
                    plugin_obj.env_blocks_add('arp', trackerboy_instdata[1][0], None, None, None, None)

                if trackerboy_instdata[2][0] != (): 
                    plugin_obj.env_blocks_add('pan', [(x-3 if x > 1 else x) for x in trackerboy_instdata[2][0]], None, None, None, None)

                if trackerboy_instdata[3][0] != (): 
                    plugin_obj.env_blocks_add('pitch', trackerboy_instdata[4][0], None, None, None, None)

                if trackerboy_instdata[4][0] != (): 
                    if insttype == 'pulse': 
                        plugin_obj.env_blocks_add('duty', [[0.125, 0.25, 0.5, 0.75][x] for x in trackerboy_instdata[4][0]], None, 1, None, None)
                    if insttype == 'wavetable':
                        plugin_obj.env_blocks_add('vol', trackerboy_instdata[4][0], None, 3, None, None)
                    if insttype == 'noise': 
                        plugin_obj.env_blocks_add('noise', trackerboy_instdata[4][0], None, 3, None, None)

                osc_data = plugin_obj.osc_add()
                if insttype == 'pulse': 
                    osc_data.shape = 'square'
                    osc_data.params['pulse_width'] = 0.25
                if insttype == 'wavetable':
                    osc_data.shape = 'custom_wave'
                    osc_data.params['wave_name'] = 'main'
                if insttype == 'noise': 
                    osc_data.shape = 'noise'

                if insttype != 'wavetable':
                    env_attack = 0
                    env_decay = 0
                    env_sustain = 1

                    if trackerboy_instdata[6] == 0: env_sustain = 1
                    elif trackerboy_instdata[6] < 8: 
                        env_decay = trackerboy_instdata[6]/5
                        env_sustain = 0
                    elif trackerboy_instdata[6] >= 8:
                        env_attack = (trackerboy_instdata[6]-8)/5
                        env_sustain = 1
                    plugin_obj.env_asdr_add('vol', 0, env_attack, 0, env_decay, env_sustain, 0, 1)
                else:
                    if t_waves:
                        if trackerboy_instdata[6] == 0: 
                            wave_obj = plugin_obj.wave_add('main')
                            wave_obj.set_all_range(t_waves[1][1], 0, 15)
                        else: 
                            outwavname = trackerboy_instdata[6]+1
                            if trackerboy_instdata[6]+1 not in t_waves: outwavname = 1
                            wave_obj = plugin_obj.wave_add('main')
                            wave_obj.set_all_range(t_waves[outwavname][1], 0, 15)


        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_lanefit')
        convproj_obj.params.add('bpm', speed_to_tempo(60, tb_speed)*20, 'float')

        convproj_obj.metadata.name = trackerboy_title
        convproj_obj.metadata.author = trackerboy_artist
        convproj_obj.metadata.copyright = trackerboy_copyright