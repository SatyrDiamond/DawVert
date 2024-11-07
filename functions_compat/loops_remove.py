# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def process(convproj_obj, in__placement_loop, out__placement_loop, out_type):
	remainingplloop = [e for e in in__placement_loop if e not in out__placement_loop]
	if (in__placement_loop != [] and remainingplloop != []):

		if convproj_obj.type in ['r', 'ri', 'rm']: 
			for trackid, track_obj in convproj_obj.track__iter(): 
				track_obj.placements.remove_loops(out__placement_loop)
				for laneid, lane_obj in track_obj.lanes.items(): 
					lane_obj.placements.remove_loops(out__placement_loop)
			return True

		if convproj_obj.type in ['m', 'mi']: 
			for pl_id, playlist_obj in convproj_obj.playlist.items(): 
				playlist_obj.placements.remove_loops(out__placement_loop)
			return True

	else: return False