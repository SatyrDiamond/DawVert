# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import copy
import logging
from functions import data_values

logger_project = logging.getLogger('project')

def index_nliid(singletrack_pl, trackid):
	for placement in singletrack_pl:
		placement['fromindex'] = trackid+'_'+placement['fromindex']

def convert(convproj_obj):
	logger_project.info('ProjType Convert: RegularIndexed > MultipleIndexed')


	plnum = -1
	for trackid, track_obj in convproj_obj.track__iter():
		inst_obj = convproj_obj.instrument__add(trackid)
		inst_obj.visual = copy.deepcopy(track_obj.visual)
		inst_obj.params = copy.deepcopy(track_obj.params)
		inst_obj.datavals = copy.deepcopy(track_obj.datavals)
		inst_obj.pluginid = track_obj.inst_pluginid
		inst_obj.fxrack_channel = track_obj.fxrack_channel

		inst_obj.midi = copy.deepcopy(track_obj.midi)
		inst_obj.fxslots_notes = track_obj.fxslots_notes
		inst_obj.fxslots_audio = track_obj.fxslots_audio
		inst_obj.is_drum = track_obj.is_drum

		starttxt = trackid+'_'

		for nle_id, nle_obj in track_obj.notelist_index.items():
			nle_obj.notelist.inst_all(trackid)
			convproj_obj.notelist_index[starttxt+nle_id] = nle_obj

		track_obj.notelist_index = {}

		if not track_obj.is_laned: 
			logger_project.info('ProjType Convert: ri2mi: inst non-laned'+(': '+trackid if trackid else ''))
			plnum += 1
			playlist_obj = convproj_obj.playlist__add(plnum, track_obj.uses_placements, track_obj.is_indexed)
			playlist_obj.visual = copy.deepcopy(track_obj.visual)
			playlist_obj.visual_ui = copy.deepcopy(track_obj.visual_ui)
			playlist_obj.placements = copy.deepcopy(track_obj.placements)
			for placement_obj in playlist_obj.placements.pl_notes_indexed: 
				placement_obj.fromindex = starttxt+placement_obj.fromindex
		else:
			logger_project.info('ProjType Convert: ri2mi: laned'+(': '+trackid if trackid else ''))
			for lane_id, lane_obj in track_obj.lanes.items():
				plnum += 1
				for placement_obj in lane_obj.placements.pl_notes_indexed: 
					placement_obj.fromindex = starttxt+placement_obj.fromindex
				playlist_obj = convproj_obj.playlist__add(plnum, track_obj.uses_placements, track_obj.is_indexed)
				playlist_obj.visual = copy.deepcopy(track_obj.visual)
				playlist_obj.visual.name = data_values.text__insidename(playlist_obj.visual.name, lane_obj.visual.name)
				playlist_obj.visual_ui = copy.deepcopy(lane_obj.visual_ui)
				playlist_obj.params = copy.deepcopy(lane_obj.params)
				playlist_obj.datavals = copy.deepcopy(lane_obj.datavals)
				playlist_obj.placements = copy.deepcopy(lane_obj.placements)
	
	convproj_obj.automation.move_everything(['track'], ['inst'])

	convproj_obj.track_data = {}
	convproj_obj.track_order = []
	convproj_obj.type = 'mi'