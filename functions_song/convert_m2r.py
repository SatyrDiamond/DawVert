# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from functions import data_values
from functions import xtramath
import copy

def convert(convproj_obj):
    print('[song-convert] Converting from Multiple > Regular')

    uses_placements, is_indexed = True, False
    for inst_id, playlist_obj in convproj_obj.playlist.items():
        uses_placements = playlist_obj.placements.uses_placements
        is_indexed = playlist_obj.placements.is_indexed

    fxrack_order = {}

    track_stor = {}
    for inst_id, inst_obj in convproj_obj.instruments.items():
        track_obj = convproj_obj.add_track(inst_id, 'instrument', uses_placements, is_indexed)
        track_obj.visual = copy.deepcopy(inst_obj.visual)
        track_obj.params = copy.deepcopy(inst_obj.params)
        track_obj.datavals = copy.deepcopy(inst_obj.datavals)
        track_obj.inst_pluginid = inst_obj.pluginid
        track_obj.fxrack_channel = inst_obj.fxrack_channel
        track_obj.midi = copy.deepcopy(inst_obj.midi)
        track_obj.fxslots_notes = inst_obj.fxslots_notes
        track_obj.fxslots_audio = inst_obj.fxslots_audio
        track_stor[inst_id] = track_obj
        if track_obj.fxrack_channel not in fxrack_order: 
            fxrack_order[track_obj.fxrack_channel] = []
        fxrack_order[track_obj.fxrack_channel].append(inst_id)

    del convproj_obj.instruments

    for pl_id, playlist_obj in convproj_obj.playlist.items():
        splitted_pl = playlist_obj.placements.inst_split()

        for inst_id, placements in splitted_pl.items():
            lane_obj = track_stor[inst_id].add_lane(str(pl_id))
            lane_obj.placements.data_notes = placements

        fxrack_audio_pl = {}
        if playlist_obj.placements.data_audio:
            for a_pl in playlist_obj.placements.data_audio:
                if a_pl.fxrack_channel not in fxrack_audio_pl: fxrack_audio_pl[a_pl.fxrack_channel] = []
                fxrack_audio_pl[a_pl.fxrack_channel].append(a_pl)

        #if fxrack_audio_pl: print(fxrack_audio_pl)

        for fx_num, placements in fxrack_audio_pl.items():
            cvpj_trackid = str(pl_id)+'_audio_'+str(fx_num)
            track_obj = convproj_obj.add_track(cvpj_trackid, 'audio', uses_placements, is_indexed)
            if track_obj.fxrack_channel not in fxrack_order: fxrack_order[track_obj.fxrack_channel] = []
            fxrack_order[track_obj.fxrack_channel].append(cvpj_trackid)
            track_obj.visual = copy.deepcopy(playlist_obj.visual)
            track_obj.params = copy.deepcopy(playlist_obj.params)
            track_obj.datavals = copy.deepcopy(playlist_obj.datavals)
            track_obj.fxrack_channel = fx_num
            track_obj.placements.data_audio = placements

    convproj_obj.track_order = []
    for n, t in fxrack_order.items():
        for n in t: convproj_obj.track_order.append(n)

    convproj_obj.playlist = {}
    convproj_obj.type = 'r'