# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def process(convproj_obj, in_compat, out_compat, out_type):
	tempo = convproj_obj.params.get('bpm', 120).value

	ppq = convproj_obj.time_ppq

	is_seconds = 0
	if in_compat == False and out_compat == True: is_seconds = 1
	elif in_compat == True and out_compat == False: is_seconds = -1

	if is_seconds:
		if convproj_obj.type in ['r', 'rm', 'ri']: 
			for trackid, track_obj in convproj_obj.track__iter(): 
				track_obj.placements.change_seconds(is_seconds==1, tempo, ppq)
				for laneid, lane_obj in track_obj.lanes.items(): 
					lane_obj.placements.change_seconds(is_seconds==1, tempo, ppq)
			convproj_obj.automation.change_seconds(is_seconds==1, tempo, ppq)
			return True


		#if convproj_obj.type in ['m', 'mi']: 
		#s	for pl_id, playlist_obj in convproj_obj.playlist.items(): 
		#		playlist_obj.placements.change_seconds(is_seconds==1, tempo)
