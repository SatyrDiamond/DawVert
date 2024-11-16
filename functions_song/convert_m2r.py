# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
from functions import data_values
from functions import xtramath
import copy

logger_project = logging.getLogger('project')

def convert(convproj_obj):
	logger_project.info('ProjType Convert: Multiple > Regular')

	uses_placements, is_indexed = True, False
	for inst_id, playlist_obj in convproj_obj.playlist.items():
		uses_placements = playlist_obj.placements.uses_placements
		is_indexed = playlist_obj.placements.is_indexed

	fxrack_order = {}

	track_stor = {}
	for inst_id, inst_obj in convproj_obj.instruments.items():
		track_obj = convproj_obj.track__add(inst_id, 'instrument', uses_placements, is_indexed)
		track_obj.visual = copy.deepcopy(inst_obj.visual)
		track_obj.params = copy.deepcopy(inst_obj.params)
		track_obj.datavals = copy.deepcopy(inst_obj.datavals)
		track_obj.fxrack_channel = inst_obj.fxrack_channel
		track_obj.midi = copy.deepcopy(inst_obj.midi)
		track_obj.plugslots = copy.deepcopy(inst_obj.plugslots)
		track_obj.is_drum = inst_obj.is_drum
		track_stor[inst_id] = track_obj
		if track_obj.fxrack_channel not in fxrack_order: 
			fxrack_order[track_obj.fxrack_channel] = []
		fxrack_order[track_obj.fxrack_channel].append(inst_id)

	del convproj_obj.instruments

	for pl_id, playlist_obj in convproj_obj.playlist.items():
		splitted_pl = playlist_obj.placements.inst_split()
		splitted_nl = playlist_obj.placements.notelist.inst_split()

		comb_split = {}
		for inst_id, placements in splitted_pl.items():
			if inst_id not in comb_split: comb_split[inst_id] = [None, None]
			comb_split[inst_id][0] = placements

		for inst_id, placements in splitted_nl.items():
			if inst_id not in comb_split: comb_split[inst_id] = [None, None]
			comb_split[inst_id][1] = placements

		for inst_id, placements in comb_split.items():
			if inst_id in track_stor:
				lane_obj = track_stor[inst_id].add_lane(str(pl_id))
				lane_obj.visual.color.merge(playlist_obj.visual.color)
				if placements[0]: lane_obj.placements.pl_notes.data = placements[0]
				if placements[1]: lane_obj.placements.notelist = placements[1]

		fxrack_audio_pl = {}
		if playlist_obj.placements.pl_audio.data:
			for a_pl in playlist_obj.placements.pl_audio.data:
				if a_pl.sample.fxrack_channel not in fxrack_audio_pl: fxrack_audio_pl[a_pl.sample.fxrack_channel] = []
				fxrack_audio_pl[a_pl.sample.fxrack_channel].append(a_pl)

		#if fxrack_audio_pl: print(fxrack_audio_pl) 

		for fx_num, placements in fxrack_audio_pl.items():
			cvpj_trackid = str(pl_id)+'_audio_'+str(fx_num)
			track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', uses_placements, is_indexed)
			if track_obj.fxrack_channel not in fxrack_order: fxrack_order[track_obj.fxrack_channel] = []
			fxrack_order[track_obj.fxrack_channel].append(cvpj_trackid)
			track_obj.visual = copy.deepcopy(playlist_obj.visual)
			track_obj.params = copy.deepcopy(playlist_obj.params)
			track_obj.datavals = copy.deepcopy(playlist_obj.datavals)
			track_obj.fxrack_channel = fx_num
			track_obj.placements.pl_audio.data = placements

	convproj_obj.track_order = []
	for n, t in fxrack_order.items():
		for n in t: convproj_obj.track_order.append(n)

	convproj_obj.main__do_lanefit()

	convproj_obj.automation.move_everything(['inst'], ['track'])

	#print(convproj_obj.automation.data)
	#exit()

	convproj_obj.playlist = {}
	convproj_obj.type = 'r'