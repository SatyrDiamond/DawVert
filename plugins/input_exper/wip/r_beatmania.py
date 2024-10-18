# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from PIL import Image

import experiments_plugin_input
import os
import json
from functions import data_values
from functions import audio
from functions import song
from functions_tracks import tracks_r

def datachunk_to_placements(poschunk): 

    placement_out = []

    for chunkdata in poschunk:
        position = chunkdata
        sampid = poschunk[chunkdata]
        if sampid in audio_data:
            filename = audio_data[sampid]['file']
            duration = audio_data[sampid]['data']['dur_sec']
            placementdata = {}
            placementdata['position'] = position
            placementdata['duration'] = (duration*8)*(bpm/120)
            placementdata['file'] = filename
            placement_out.append(placementdata)

    return placement_out


class input_color_art(experiments_plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def get_shortname(self): return 'beatmania'
    def getname(self): return 'Beatmania'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {}
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global audio_data
        global bpm

        bms_txt = open(input_file, 'r')
        bms_lines = bms_txt.readlines()
        cvpj_l = {}

        usedbgmbar = {}

        chandata_bgm = {}
        chandata = {}

        for trackid in range(11, 17):
            tracks_r.track_create(cvpj_l, str(trackid), 'audio')
            tracks_r.track_visual(cvpj_l, str(trackid), name='Player 1: '+str(trackid-10))
            chandata[trackid] = {}

        for trackid in range(20, 27):
            tracks_r.track_create(cvpj_l, str(trackid), 'audio')
            tracks_r.track_visual(cvpj_l, str(trackid), name='Player 2: '+str(trackid-19))
            chandata[trackid] = {}

        audio_data = {}

        bpm = 120

        for bms_line in bms_lines:
            bms_line = bms_line.strip()
            if len(bms_line) != 0:
                bms_arg = bms_line[1:]
                bms_cmd = bms_line[0]
                bms_split = bms_arg.split(' ', 1)
                #print(bms_cmd, bms_split[0][0:3], bms_split)

                if bms_cmd == '#':
                    if bms_split[0] == 'TITLE': song.add_info(cvpj_l, 'title', bms_split[1])
                    elif bms_split[0] == 'ARTIST': song.add_info(cvpj_l, 'author', bms_split[1])
                    elif bms_split[0] == 'BPM': bpm = int(bms_split[1])
                    elif bms_split[0][0:3] == 'WAV': 
                        #print('[input-beatmania] WAV File '+bms_split[0][3:]+', '+bms_split[1])
                        audiopath = os.path.join(os.path.dirname(input_file), bms_split[1])

                        audio_data[bms_split[0][3:]] = {}
                        singleaudiodat = audio_data[bms_split[0][3:]]
                        singleaudiodat['file'] = audiopath
                        singleaudiodat['data'] = audio.get_audiofile_info_nocache(audiopath)

                    elif ':' in bms_split[0]:
                        bms_bartarg, bms_data = bms_split[0].split(':')
                        bms_bar = int(bms_bartarg[0:3])*16
                        bms_targ = int(bms_bartarg[3:5])
                        bms_data_chunks = data_values.list__chunks(bms_data, 2)
                        bms_data_chunk_size = len(bms_data_chunks)
                        for chunknum in range(bms_data_chunk_size):
                            chunkcmd = bms_data_chunks[chunknum]
                            if chunkcmd != '00':
                                chunkpos = bms_bar + (chunknum/bms_data_chunk_size)*16
                                #print(chunkpos, bms_targ, chunkcmd)

                                if bms_targ == 1:
                                    if bms_bar not in usedbgmbar: usedbgmbar[bms_bar] = 0
                                    else: usedbgmbar[bms_bar] += 1

                                    bgmid = usedbgmbar[bms_bar]
                                    #print(chunkpos, bms_bar, bgmid)
                                    if bgmid not in chandata_bgm: chandata_bgm[bgmid] = {}
                                    chandata_bgm[bgmid][chunkpos] = chunkcmd
                                else:
                                    if bms_targ in chandata: 
                                        chandata[bms_targ][chunkpos] = chunkcmd


        song.add_param(cvpj_l, 'bpm', bpm)

        for trackid in range(11, 27):
            if trackid in chandata:
                tracks_r.add_pl(cvpj_l, trackid, 'audio', datachunk_to_placements(chandata[trackid]))

        for s_chandata_bgm in chandata_bgm:
            print(s_chandata_bgm, chandata_bgm[s_chandata_bgm])
            trackid = 'bgm_'+str(s_chandata_bgm)
            tracks_r.track_create(cvpj_l, trackid, 'audio')
            tracks_r.track_visual(cvpj_l, trackid, name='BGM #'+str(s_chandata_bgm))
            tracks_r.add_pl(cvpj_l, trackid, 'audio', datachunk_to_placements(chandata_bgm[s_chandata_bgm]))


        #exit()

        return json.dumps(cvpj_l)


