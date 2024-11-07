# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath

def process(convproj_obj, in__placement_audio_nested, out__placement_audio_nested, out_type):
	if in__placement_audio_nested == True and out__placement_audio_nested == False:
		if convproj_obj.type == 'm':
			for pl_id, playlist_obj in convproj_obj.playlist.items(): playlist_obj.placements.remove_nested()
			return True
		elif convproj_obj.type == 'r':
			for trackid, track_obj in convproj_obj.track__iter():
				track_obj.placements.remove_nested()
				for trackid, lane_obj in track_obj.lanes.items(): lane_obj.placements.remove_nested()
			return True
	else:
		return False