# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def process(convproj_obj, in__placement_loop, out__placement_loop):

    if in__placement_loop == [] and 'loop' in out__placement_loop:

        if convproj_obj.type in ['r', 'ri', 'rm']: 
            for trackid, track_obj in convproj_obj.iter_track(): 
                track_obj.placements.add_loops()
                for laneid, lane_obj in track_obj.lanes.items(): 
                    lane_obj.placements.add_loops()
            return True

        if convproj_obj.type in ['m', 'mi']: 
            for pl_id, playlist_obj in convproj_obj.playlist.items(): 
                playlist_obj.placements.add_loops()
            return True

    else: return False