# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

def convert(convproj_obj):
    print('[song-convert] Converting from RegularIndexed > Regular')

    for trackid, track_obj in convproj_obj.iter_track():
        if not track_obj.is_laned: 
            track_obj.placements.unindex_notes(track_obj.notelist_index)
        else:
            for lane_id, lane_obj in track_obj.lanes.items():
                lane_obj.placements.unindex_notes(track_obj.notelist_index)
                
    convproj_obj.type = 'r'