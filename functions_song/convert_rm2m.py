# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import copy
import logging

logger_project = logging.getLogger('project')

def convert(convproj_obj, change_instnames):
	logger_project.info('ProjType Convert: RegularMultiple > Multiple')

	useable_plugins = convproj_obj.plugins
	convproj_obj.plugins = {}

	used_plugins = []

	old_instruments = convproj_obj.instruments

	convproj_obj.instruments = {}
	convproj_obj.instruments_order = []

	plnum = -1
	for trackid, track_obj in convproj_obj.track__iter():
		instruments = track_obj.used_insts()

		for instid in instruments:
			newinstid = 'rm2m__'+trackid+'__'+instid
			if instid in old_instruments:
				new_inst = copy.deepcopy(old_instruments[instid])
				if new_inst.plugslots.synth not in used_plugins:
					used_plugins.append(new_inst.plugslots.synth)
				convproj_obj.instruments[newinstid] = new_inst
				convproj_obj.instruments_order.append(newinstid)
			else:
				inst_obj = convproj_obj.instrument__add(newinstid)
				inst_obj.visual.name = instid

			if convproj_obj.instruments[newinstid].fxrack_channel == -1:
				convproj_obj.instruments[newinstid].fxrack_channel = track_obj.fxrack_channel 
		
		if change_instnames:	  
			track_obj.placements.notelist.appendtxt_inst('rm2m__'+trackid+'__', '')

		for audiopl_obj in track_obj.placements.pl_audio:
			audiopl_obj.sample.fxrack_channel = track_obj.fxrack_channel

		if not track_obj.is_laned:
			plnum += 1
			
			playlist_obj = convproj_obj.playlist__add(plnum, track_obj.uses_placements, track_obj.is_indexed)
			playlist_obj.visual = copy.deepcopy(track_obj.visual)
			playlist_obj.visual_ui = copy.deepcopy(track_obj.visual_ui)
			playlist_obj.placements = copy.deepcopy(track_obj.placements)
			if change_instnames:
				for nlp in playlist_obj.placements.pl_notes:
					nlp.notelist.appendtxt_inst('rm2m__'+trackid+'__', '')

		else:
			for lane_id, lane_obj in track_obj.lanes.items():
				plnum += 1
				lane_obj.placements.notelist.appendtxt_inst('rm2m__'+trackid+'__', '')
				playlist_obj = convproj_obj.playlist__add(plnum, track_obj.uses_placements, track_obj.is_indexed)
				playlist_obj.visual = copy.deepcopy(track_obj.visual)
				if lane_obj.visual.name: playlist_obj.visual.name += ' ('+lane_obj.visual.name+')'
				playlist_obj.visual_ui = copy.deepcopy(lane_obj.visual_ui)
				playlist_obj.params = copy.deepcopy(lane_obj.params)
				playlist_obj.datavals = copy.deepcopy(lane_obj.datavals)
				playlist_obj.placements = copy.deepcopy(lane_obj.placements)
				if change_instnames:
					for nlp in playlist_obj.placements.pl_notes:
						nlp.notelist.appendtxt_inst('rm2m__'+trackid+'__', '')

	for fxnum, fxchan_obj in convproj_obj.fxrack.items():
		for x in fxchan_obj.plugslots.slots_audio: used_plugins.append(x)

	for plugid in used_plugins:
		if plugid:
			convproj_obj.plugins[plugid] = useable_plugins[plugid]

	convproj_obj.track_data = {}
	convproj_obj.track_order = []
	convproj_obj.type = 'm'