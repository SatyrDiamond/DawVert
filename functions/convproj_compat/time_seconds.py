# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def get_sec(in_time_seconds, out_time_seconds):
	is_seconds = 0
	if in_time_seconds == False and out_time_seconds == True: is_seconds = 1
	elif in_time_seconds == True and out_time_seconds == False: is_seconds = -1
	return bool(is_seconds), is_seconds==1

def process(convproj_obj, in_compat, out_compat, out_type, dawvert_intent):
	tempo = convproj_obj.params.get('bpm', 120).value

	ppq = convproj_obj.time_ppq

	traits_obj = convproj_obj.traits

	is_seconds = 0
	if in_compat.time_seconds == False and out_compat.time_seconds == True: is_seconds = 1
	elif in_compat.time_seconds == True and out_compat.time_seconds == False: is_seconds = -1

	if convproj_obj.type in ['r', 'rm', 'ri']: 
		if not convproj_obj.time_tempocalc.use_stored>0: convproj_obj.automation.delete(['main', 'bpm'])

		# -- tracks --
		dochange, is_sec = get_sec(in_compat.time_seconds_tracks, out_compat.time_seconds_tracks)
		if dochange:
			for trackid, track_obj in convproj_obj.track__iter(): 
				track_obj.placements.change_seconds(is_sec, tempo, ppq)
				for laneid, lane_obj in track_obj.lanes.items(): 
					lane_obj.placements.change_seconds(is_sec, tempo, ppq)

		# -- automation --
		dochange, is_sec = get_sec(in_compat.time_seconds_auto, out_compat.time_seconds_auto)
		if dochange: convproj_obj.automation.change_seconds_notempo(is_sec, tempo, ppq)

		# -- tempo --
		dochange, is_sec = get_sec(in_compat.time_seconds_tempo, out_compat.time_seconds_tempo)
		if dochange: convproj_obj.automation.change_seconds_tempo(is_sec, tempo, ppq)

		# -- timesig --
		dochange, is_sec = get_sec(in_compat.time_seconds_timesig, out_compat.time_seconds_timesig)
		if dochange: convproj_obj.timesig_auto.change_seconds_global(is_sec, convproj_obj.id, ppq)

		# -- transport --
		dochange, is_sec = get_sec(in_compat.time_seconds_transport, out_compat.time_seconds_transport)
		if dochange: convproj_obj.transport.change_seconds(is_sec, tempo, ppq)

		# -- timemarkers --
		dochange, is_sec = get_sec(in_compat.time_seconds_timemarkers, out_compat.time_seconds_timemarkers)
		if dochange: convproj_obj.timemarkers.change_seconds(is_sec, tempo, ppq)

		#if convproj_obj.type in ['m', 'mi']: 
		#s	for pl_id, playlist_obj in convproj_obj.playlist.items(): 
		#		playlist_obj.placements.change_seconds(is_seconds==1, tempo)
