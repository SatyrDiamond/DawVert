# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import copy

def convert(convproj_obj):
    print('[song-convert] Converting from Regular > Multiple')

    plnum = -1
    for trackid, track_obj in convproj_obj.iter_track():

        used_inst = False
        if track_obj.type == 'instruments': used_inst = True
        if track_obj.type == 'instrument': used_inst = True
        if track_obj.placements.data_notes: used_inst = True


        if not track_obj.is_laned:
            plnum += 1
            print('[song-convert] r2m: non-laned:', trackid)
            playlist_obj = convproj_obj.add_playlist(plnum, track_obj.uses_placements, track_obj.is_indexed)
            playlist_obj.visual = copy.deepcopy(track_obj.visual)
            playlist_obj.visual_ui = copy.deepcopy(track_obj.visual_ui)
            playlist_obj.placements = copy.deepcopy(track_obj.placements)
            playlist_obj.placements.add_inst_to_notes(trackid)
        else:
            print('[song-convert] r2m: laned:', trackid)
            for lane_id, lane_obj in track_obj.lanes.items():
                plnum += 1
                playlist_obj = convproj_obj.add_playlist(plnum, track_obj.uses_placements, track_obj.is_indexed)
                playlist_obj.visual = copy.deepcopy(track_obj.visual)
                if lane_obj.visual.name: playlist_obj.visual.name += ' ('+lane_obj.visual.name+')'
                playlist_obj.visual_ui = copy.deepcopy(lane_obj.visual_ui)
                playlist_obj.params = copy.deepcopy(lane_obj.params)
                playlist_obj.datavals = copy.deepcopy(lane_obj.datavals)
                playlist_obj.placements = copy.deepcopy(lane_obj.placements)
        if used_inst:
            inst_obj = convproj_obj.add_instrument(trackid)
            inst_obj.visual = copy.deepcopy(track_obj.visual)
            inst_obj.params = copy.deepcopy(track_obj.params)
            inst_obj.datavals = copy.deepcopy(track_obj.datavals)
            inst_obj.pluginid = track_obj.inst_pluginid
            inst_obj.fxrack_channel = track_obj.fxrack_channel
            inst_obj.midi = copy.deepcopy(track_obj.midi)
            inst_obj.fxslots_notes = track_obj.fxslots_notes
            inst_obj.fxslots_audio = track_obj.fxslots_audio

    convproj_obj.track_data = {}
    convproj_obj.track_order = []
    convproj_obj.type = 'm'