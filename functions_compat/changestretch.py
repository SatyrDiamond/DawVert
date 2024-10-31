# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values

def process(convproj_obj, in__placement_audio_stretch, out__placement_audio_stretch, out_type):
	target = None
	if 'warp' in in__placement_audio_stretch and 'warp' not in out__placement_audio_stretch: target = 'rate'
	if 'rate' in in__placement_audio_stretch and 'rate' not in out__placement_audio_stretch: target = 'warp'
	if not out__placement_audio_stretch: target = 'none'

	if target:
		tempo = convproj_obj.params.get('bpm', 120).value

		if convproj_obj.type in ['r', 'rm']: 

			for trackid, track_obj in convproj_obj.iter_track(): 
				track_obj.placements.all_stretch_set_pitch_nonsync()
				for laneid, lane_obj in track_obj.lanes.items(): 
					lane_obj.placements.all_stretch_set_pitch_nonsync()

			for trackid, track_obj in convproj_obj.iter_track(): 
				track_obj.placements.changestretch(convproj_obj, target, tempo)
				for laneid, lane_obj in track_obj.lanes.items(): 
					lane_obj.placements.changestretch(convproj_obj, target, tempo)
			return True

		if convproj_obj.type in ['m']: 

			for pl_id, playlist_obj in convproj_obj.playlist.items(): 
				playlist_obj.placements.all_stretch_set_pitch_nonsync()

			for pl_id, playlist_obj in convproj_obj.playlist.items(): 
				playlist_obj.placements.changestretch(convproj_obj, target, tempo)
			return True


	return False