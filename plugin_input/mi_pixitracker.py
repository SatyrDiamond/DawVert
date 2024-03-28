# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from objects_file import audio_wav
import plugin_input
import json
import struct
import os

pixi_colors = [[1, 1, 1],[0.31, 0.31, 1],[0.31, 1, 0.31],[0.31, 1, 1],[1, 0.31, 0.31],[1, 0.31, 1],[1, 1, 0.31],[1, 0.65, 0.48],[0.48, 0.65, 1],[0.65, 1, 0.48],[0.48, 1, 0.65],[1, 0.48, 0.65],[0.65, 0.48, 1],[0.40, 1, 0.7],[0.70, 1, 0.4],[1, 0.35, 0.74]]

class input_cvpj_f(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'pixitracker'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return True
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Pixitracker'
        dawinfo_obj.file_ext = 'piximod'
        dawinfo_obj.track_lanes = True
        dawinfo_obj.audio_filetypes = ['wav']
        dawinfo_obj.plugin_included = ['sampler:single']
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(8)
        if bytesdata == b'PIXIMOD1': return True
        else: return False

    def parse(self, convproj_obj, input_file, dv_config):
        convproj_obj.type = 'mi'
        convproj_obj.set_timings(4, False)

        song_file = open(input_file, 'rb')
        pixi_chunks = data_bytes.iff_read(song_file, 8)
        pixi_data_patterns = {}
        pixi_data_sounds = []

        samplefolder = dv_config.path_samples_extracted
        
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

                t_notelist = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

                for t_pattrack in t_patdata:
                    t_pos = 0
                    t_notes = []
                    for t_patnote in t_pattrack:
                        if t_patnote != (0, 0, 0, 0): t_notes.append([0, t_pos, t_patnote[0], t_patnote[1], t_patnote[2]])
                        if t_notes != []: t_notes[-1][0] += 1
                        t_pos += 1
                    for t_note in t_notes:
                        if t_note[4] != 0:
                            cvpj_note = ['pixi_'+str(t_note[3]), t_note[1], t_note[0], t_note[2]-78, t_note[4]/100]
                            t_notelist[t_note[3]].append(cvpj_note)

                pixi_data_patterns[pixi_pattern_num] = [pixi_c_pat_len, t_notelist]

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

            inst_obj = convproj_obj.add_instrument(cvpj_instid)
            inst_obj.visual.name = 'Inst #'+str(instnum+1)
            inst_obj.visual.color = pixi_colors[instnum]

            if pixi_data_sounds[instnum] != [None,None,None,None,None,None,None,None]:
                t_sounddata = pixi_data_sounds[instnum]
                wave_path = samplefolder + str(instnum) + '.wav'
                
                wavfile_obj = audio_wav.wav_main()
                wavfile_obj.set_freq(t_sounddata[1])
                wavfile_obj.data_add_data(16, t_sounddata[0], False, t_sounddata[7])
                wavfile_obj.write(wave_path)

                plugin_obj, inst_obj.pluginid, sampleref_obj = convproj_obj.add_plugin_sampler_genid(wave_path)

                inst_obj.params.add('pitch', t_sounddata[2]/100, 'float')
                inst_obj.params.add('vol', t_sounddata[4]/100, 'float')
                inst_obj.datavals.add('middlenote', t_sounddata[3]*-1)

                plugin_obj.datavals.add('point_value_type', "samples")
                plugin_obj.datavals.add('start', t_sounddata[5])
                plugin_obj.datavals.add('end', t_sounddata[6])
                plugin_obj.datavals.add('length', len(t_sounddata[7])//t_sounddata[0])
                plugin_obj.datavals.add('trigger', 'normal')
            instnum += 1

        for pixi_data_pattern in pixi_data_patterns:
            nle_obj = convproj_obj.add_notelistindex('pixi_'+str(pixi_data_pattern))
            nle_obj.visual.name = 'Pattern '+str(pixi_data_pattern+1)

            nli_notes = []
            for pixi_data_pattern_inst in pixi_data_patterns[pixi_data_pattern][1]:
                for tn in pixi_data_pattern_inst: nle_obj.notelist.add_m(tn[0], tn[1], tn[2], tn[3], tn[4], {})

        playlist_obj = convproj_obj.add_playlist(0, 1, True)

        placements_pos = 0
        for patnum in pixi_patternorder:
            patlen = pixi_data_patterns[pixi_data_pattern][0]

            cvpj_placement = playlist_obj.placements.add_notes_indexed()
            cvpj_placement.fromindex = 'pixi_'+str(patnum)
            cvpj_placement.position = placements_pos
            cvpj_placement.duration = patlen

            placements_pos += patlen

        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_lanefit')
        convproj_obj.params.add('bpm', pixi_bpm, 'float')
        convproj_obj.track_master.params.add('vol', pixi_vol/100, 'float')
