# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import audio_wav
from functions import tracks
from functions import note_data
from functions import placement_data
from functions import plugins
from functions import song
import plugin_input
import json
import struct
import os

pixi_colors = [[1, 1, 1],[0.31, 0.31, 1],[0.31, 1, 0.31],[0.31, 1, 1],[1, 0.31, 0.31],[1, 0.31, 1],[1, 1, 0.31],[1, 0.65, 0.48],[0.48, 0.65, 1],[0.65, 1, 0.48],[0.48, 1, 0.65],[1, 0.48, 0.65],[0.65, 0.48, 1],[0.40, 1, 0.7],[0.70, 1, 0.4],[1, 0.35, 0.74]]

class input_cvpj_f(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'pixitracker'
    def getname(self): return 'pixitracker'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return True
    def getdawcapabilities(self): 
        return {
        'samples_inside': True,
        'track_lanes': True,
        }
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(8)
        if bytesdata == b'PIXIMOD1': return True
        else: return False
    def parse(self, input_file, extra_param):
        song_file = open(input_file, 'rb')
        pixi_chunks = data_bytes.riff_read(song_file, 8)
        pixi_data_patterns = {}
        pixi_data_sounds = []

        cvpj_l = {}
        
        samplefolder = extra_param['samplefolder']
        
        for _ in range(16): pixi_data_sounds.append([None,None,None,None,None,None,None,None])

        for pixi_chunk in pixi_chunks:
            #print(pixi_chunk[0])
            if pixi_chunk[0] == b'BPM ':
                pixi_bpm = int.from_bytes(pixi_chunk[1], "little")
                print('[input-pixitracker] Tempo: ' + str(pixi_bpm))
            elif pixi_chunk[0] == b'LPB ':
                pixi_lpb = int.from_bytes(pixi_chunk[1], "little")
                print('[input-pixitracker] LPB: ' + str(pixi_lpb))
            elif pixi_chunk[0] == b'TPL ':
                pixi_tpl = int.from_bytes(pixi_chunk[1], "little")
                print('[input-pixitracker] TPL: ' + str(pixi_tpl))
            elif pixi_chunk[0] == b'SHFL':
                pixi_shfl = int.from_bytes(pixi_chunk[1], "little")
                print('[input-pixitracker] Shuffle: ' + str(pixi_shfl))
            elif pixi_chunk[0] == b'VOL ':
                pixi_vol = int.from_bytes(pixi_chunk[1], "little")
                print('[input-pixitracker] Volume: ' + str(pixi_vol))
            elif pixi_chunk[0] == b'PATT':
                pixi_patternorder_bytes = pixi_chunk[1][12:]
                pixi_patternorder_size = int.from_bytes(pixi_chunk[1][4:8], "little")
                pixi_patternorder = struct.unpack('h'*pixi_patternorder_size, pixi_patternorder_bytes)
                print('[input-pixitracker] Pattern Order: '+', '.join([str(x) for x in pixi_patternorder]))
            elif pixi_chunk[0] == b'PATN':
                pixi_pattern_num = int.from_bytes(pixi_chunk[1], "little")
                print('[input-pixitracker] Pattern #' + str(pixi_pattern_num+1))
            elif pixi_chunk[0] == b'PATD':
                t_pattrack = []
                t_patdata = []
                pixi_c_pat_len = int.from_bytes(pixi_chunk[1][8:12], "little")
                for _ in range(pixi_c_pat_len): t_pattrack.append(None)
                pixi_c_pat_tracks = int.from_bytes(pixi_chunk[1][4:8], "little")
                for _ in range(pixi_c_pat_tracks): t_patdata.append(t_pattrack.copy())
                print('[input-pixitracker]    Tracks:',pixi_c_pat_tracks)
                print('[input-pixitracker]    Length:',pixi_c_pat_len)
                pixi_c_pat_data = data_bytes.to_bytesio(pixi_chunk[1][12:])
                for c_len_num in range(pixi_c_pat_len):
                    for c_trk_num in range(pixi_c_pat_tracks):
                        t_patdata[c_trk_num][c_len_num] = struct.unpack('bbbb', pixi_c_pat_data.read(4))

                cvpj_notelist = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

                for t_pattrack in t_patdata:
                    t_pos = 0
                    t_notes = []
                    for t_patnote in t_pattrack:
                        if t_patnote != (0, 0, 0, 0): t_notes.append([0, t_pos, t_patnote[0], t_patnote[1], t_patnote[2]])
                        if t_notes != []: t_notes[-1][0] += 1
                        t_pos += 1
                    for t_note in t_notes:
                        if t_note[4] != 0:
                            cvpj_note = note_data.mx_makenote('pixi_'+str(t_note[3]), t_note[1], t_note[0], t_note[2]-78, t_note[4]/100, None)
                            cvpj_notelist[t_note[3]].append(cvpj_note)

                pixi_data_patterns[pixi_pattern_num] = {'len': pixi_c_pat_len, 'notes': cvpj_notelist}

            elif pixi_chunk[0] == b'SNDN':
                pixi_sound_num = int.from_bytes(pixi_chunk[1], "little")
                print('[input-pixitracker] Sound #' + str(pixi_sound_num+1))
            elif pixi_chunk[0] == b'CHAN':
                pixi_data_sounds[pixi_sound_num][0] = int.from_bytes(pixi_chunk[1], "little")
                print('[input-pixitracker]    Channels: ' + str(pixi_data_sounds[pixi_sound_num][0]))
            elif pixi_chunk[0] == b'RATE':
                pixi_data_sounds[pixi_sound_num][1] = int.from_bytes(pixi_chunk[1], "little")
                print('[input-pixitracker]    Rate: ' + str(pixi_data_sounds[pixi_sound_num][1]))
            elif pixi_chunk[0] == b'FINE':
                pixi_data_sounds[pixi_sound_num][2] = int.from_bytes(pixi_chunk[1], "little", signed=True)/0.64
                print('[input-pixitracker]    Fine: ' + str(pixi_data_sounds[pixi_sound_num][2]))
            elif pixi_chunk[0] == b'RELN':
                pixi_data_sounds[pixi_sound_num][3] = int.from_bytes(pixi_chunk[1], "little", signed=True)
                print('[input-pixitracker]    Transpose: ' + str(pixi_data_sounds[pixi_sound_num][3]))
            elif pixi_chunk[0] == b'SVOL':
                pixi_data_sounds[pixi_sound_num][4] = int.from_bytes(pixi_chunk[1], "little", signed=True)
                print('[input-pixitracker]    Volume: ' + str(pixi_data_sounds[pixi_sound_num][4]))
            elif pixi_chunk[0] == b'SOFF':
                pixi_data_sounds[pixi_sound_num][5] = int.from_bytes(pixi_chunk[1], "little", signed=True)
                print('[input-pixitracker]    Start: ' + str(pixi_data_sounds[pixi_sound_num][5]))
            elif pixi_chunk[0] == b'SOF2':
                pixi_data_sounds[pixi_sound_num][6] = int.from_bytes(pixi_chunk[1], "little", signed=True)
                print('[input-pixitracker]    End: ' + str(pixi_data_sounds[pixi_sound_num][6]))
            elif pixi_chunk[0] == b'SND1':
                pixi_data_sounds[pixi_sound_num][7] = pixi_chunk[1][8:]
                print('[input-pixitracker]    Data Size: ' + str(len(pixi_data_sounds[pixi_sound_num][7])))
            elif pixi_chunk[0] == b'SND2':
                pixi_data_sounds[pixi_sound_num][7] = pixi_chunk[1][8:]
                print('[input-pixitracker]    Data Size: ' + str(len(pixi_data_sounds[pixi_sound_num][7])))
            else:
                print('[input-pixitracker] Unknown Chunk,'+str(pixi_chunk[0]))
                exit()

        for instnum in range(16):
            cvpj_inst = {}
            cvpj_instid = 'pixi_'+str(instnum)
            cvpj_instvol = 1.0

            pluginid = plugins.get_id()

            tracks.m_inst_create(cvpj_l, cvpj_instid, name='Inst #'+str(instnum+1), color=pixi_colors[instnum])

            if pixi_data_sounds[instnum] != [None,None,None,None,None,None,None,None]:
                t_sounddata = pixi_data_sounds[instnum]
                wave_path = samplefolder + str(instnum) + '.wav'
                audio_wav.generate(wave_path, t_sounddata[7], t_sounddata[0], t_sounddata[1], 16, None)
                tracks.m_inst_pluginid(cvpj_l, cvpj_instid, pluginid)
                tracks.m_inst_add_param(cvpj_l, cvpj_instid, 'pitch', t_sounddata[2]/100, 'float')
                tracks.m_inst_add_dataval(cvpj_l, cvpj_instid, None, 'middlenote', t_sounddata[3]*-1)
                tracks.m_inst_add_param(cvpj_l, cvpj_instid, 'vol', t_sounddata[4]/100, 'float')
                plugins.add_plug_sampler_singlefile(cvpj_l, pluginid, wave_path)
                plugins.add_plug_data(cvpj_l, pluginid, 'point_value_type', "samples")
                plugins.add_plug_data(cvpj_l, pluginid, 'start', t_sounddata[5])
                plugins.add_plug_data(cvpj_l, pluginid, 'end', t_sounddata[6])
                plugins.add_plug_data(cvpj_l, pluginid, 'length', len(t_sounddata[7])//t_sounddata[0])
                plugins.add_plug_data(cvpj_l, pluginid, 'trigger', 'normal')

        for pixi_data_pattern in pixi_data_patterns:
            nli_notes = []
            for pixi_data_pattern_inst in pixi_data_patterns[pixi_data_pattern]['notes']:
                for pixi_data_pattern_note in pixi_data_pattern_inst:
                    nli_notes.append(pixi_data_pattern_note)
            tracks.m_add_nle(cvpj_l, 'pixi_'+str(pixi_data_pattern), nli_notes)
            tracks.m_add_nle_info(cvpj_l, 'pixi_'+str(pixi_data_pattern), 'Pattern '+str(pixi_data_pattern+1), None)

        placements = []
        placements_pos = 0
        for patnum in pixi_patternorder:
            placements.append( placement_data.makepl_n_mi(placements_pos, pixi_data_patterns[pixi_data_pattern]['len'], 'pixi_'+str(patnum)) )
            placements_pos += pixi_data_patterns[pixi_data_pattern]['len']

        tracks.m_playlist_pl(cvpj_l, '1', None, None, placements)

        cvpj_l['do_addloop'] = True

        song.add_param(cvpj_l, 'vol', pixi_vol/100)
        song.add_param(cvpj_l, 'bpm', pixi_bpm)
        return json.dumps(cvpj_l)