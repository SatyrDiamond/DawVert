# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values

def process_r(convproj_obj):
	org_track_data = convproj_obj.track_data
	org_track_order = convproj_obj.track_order
	org_trackroute = convproj_obj.trackroute

	convproj_obj.track_order = []
	convproj_obj.track_data = {}
	convproj_obj.trackroute = {}

	for trackid in org_track_order:
		if trackid in org_track_data:
			track_obj = org_track_data[trackid]
			trackroute_sendobj = org_trackroute[trackid] if trackid in org_trackroute else None

			if_audio = track_obj.placements.pl_audio or track_obj.placements.pl_audio_nested
			if_notes = track_obj.placements.pl_notes or track_obj.placements.notelist

			if track_obj.type == 'hybrid':
				a_track_obj = track_obj.make_base()
				n_track_obj = track_obj.make_base()

				a_track_obj.placements.pl_audio = track_obj.placements.pl_audio
				a_track_obj.placements.pl_audio_nested = track_obj.placements.pl_audio_nested
				n_track_obj.placements.pl_notes = track_obj.placements.pl_notes
				n_track_obj.placements.notelist = track_obj.placements.notelist

				if if_notes:
					trackid_s = trackid+'_unhybrid_notes'
					n_track_obj.type = 'instrument'
					convproj_obj.track_order.append(trackid_s)
					convproj_obj.track_data[trackid_s] = n_track_obj
					if trackroute_sendobj != None: convproj_obj.trackroute[trackid_s] = trackroute_sendobj
					convproj_obj.automation.copy_everything(['track', trackid], ['track', trackid_s])

				if if_audio:
					trackid_s = trackid+'_unhybrid_audio'
					a_track_obj.type = 'audio'
					convproj_obj.track_order.append(trackid_s)
					convproj_obj.track_data[trackid_s] = a_track_obj
					if trackroute_sendobj != None: convproj_obj.trackroute[trackid_s] = trackroute_sendobj
					convproj_obj.automation.copy_everything(['track', trackid], ['track', trackid_s])
				#if not (if_audio and if_notes):
				#	n_track_obj.type = 'instrument'
				#	convproj_obj.track_order.append(trackid)
				#	convproj_obj.track_data[trackid] = n_track_obj
				#	if trackroute_sendobj != None: convproj_obj.trackroute[trackid] = trackroute_sendobj

	return True

def process(convproj_obj, in__track_hybrid, out__track_hybrid, out_type, dawvert_intent):
	if in__track_hybrid == True and out__track_hybrid == False:
		if convproj_obj.type in ['r', 'ri', 'rm']: return process_r(convproj_obj)
		else: return False
	else: return False