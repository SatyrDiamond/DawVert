# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def tracklanename(trackname, lanename):
	if trackname:
		if lanename: ntp_name = trackname+' ['+lanename+']'
		if not lanename: ntp_name = trackname
	if not trackname:
		if lanename: ntp_name = 'none'+' ['+lanename+']'
		if not lanename: ntp_name = 'none'
	return ntp_name

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

			if not track_obj.is_laned:
				convproj_obj.track_order.append(trackid)
				convproj_obj.track_data[trackid] = track_obj
				if trackroute_sendobj != None: convproj_obj.trackroute[trackid] = trackroute_sendobj
			else:
				for laneid, lane_obj in track_obj.lanes.items():
					cvpj_trackid = trackid+'_lane_'+laneid
					sep_track_obj = track_obj.make_base()
					sep_track_obj.visual.name = tracklanename(sep_track_obj.visual.name, lane_obj.visual.name)
					sep_track_obj.placements = lane_obj.placements
					convproj_obj.track_order.append(cvpj_trackid)
					convproj_obj.track_data[cvpj_trackid] = sep_track_obj
					if trackroute_sendobj != None: convproj_obj.trackroute[cvpj_trackid] = trackroute_sendobj

	return True

def process(convproj_obj, in__track_lanes, out__track_lanes, out_type):
	if in__track_lanes == True and out__track_lanes == False:
		if convproj_obj.type in ['r', 'ri', 'rm']: return process_r(convproj_obj)
		else: return False
	else: return False