# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import copy

def tracklanename(trackname, lanename):
	if trackname:
		if lanename: ntp_name = trackname+' ['+lanename+']'
		if not lanename: ntp_name = trackname
	if not trackname:
		if lanename: ntp_name = 'none'+' ['+lanename+']'
		if not lanename: ntp_name = 'none'
	return ntp_name

def process_r(convproj_obj, out_dawinfo):
	org_track_data = convproj_obj.track_data
	org_track_order = convproj_obj.track_order
	org_trackroute = convproj_obj.trackroute
	out_fxtype = out_dawinfo.fxtype

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
				insidegroup = len(track_obj.lanes)>1 and out_fxtype == 'groupreturn'

				if insidegroup:
					group_obj = convproj_obj.fx__group__add(trackid)
					group_obj.visual = copy.deepcopy(track_obj.visual)
					for paramid in track_obj.params.list():
						track_obj.params.move(group_obj.params, paramid)
						convproj_obj.automation.move(['track',trackid,paramid], ['group',trackid,paramid])
						track_obj.params.move(group_obj.params, paramid)
					group_obj.plugslots.slots_notes = track_obj.plugslots.slots_notes
					group_obj.plugslots.slots_audio = track_obj.plugslots.slots_audio
					track_obj.plugslots.slots_notes = []
					track_obj.plugslots.slots_audio = []

				for laneid, lane_obj in track_obj.lanes.items():
					cvpj_trackid = trackid+'_lane_'+laneid
					if not insidegroup:
						convproj_obj.automation.move_everything(['track', trackid], ['track', cvpj_trackid])
					sep_track_obj = track_obj.make_base()
					sep_track_obj.visual.name = tracklanename(sep_track_obj.visual.name, lane_obj.visual.name)
					sep_track_obj.visual.color.merge(lane_obj.visual.color)
					sep_track_obj.placements = lane_obj.placements
					convproj_obj.track_order.append(cvpj_trackid)
					convproj_obj.track_data[cvpj_trackid] = sep_track_obj
					if insidegroup: sep_track_obj.group = trackid

					if trackroute_sendobj != None: convproj_obj.trackroute[cvpj_trackid] = trackroute_sendobj

				colors = [x.visual.color for _, x in track_obj.lanes.items() if x.visual.color]
				allcolor = colors[0] if (all(x == colors[0] for x in colors) and colors) else None

				if allcolor:
					track_obj.visual.color.merge(allcolor)
					if insidegroup: group_obj.visual.color = copy.deepcopy(allcolor)
	return True

def process(convproj_obj, in__track_lanes, out_dawinfo, out_type):
	if in__track_lanes == True and out_dawinfo.track_lanes == False:
		if convproj_obj.type in ['r', 'ri', 'rm']: return process_r(convproj_obj, out_dawinfo)
		else: return False
	else: return False