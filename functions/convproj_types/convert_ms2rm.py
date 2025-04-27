# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging

logger_project = logging.getLogger('project')

def convert(convproj_obj, out_dawinfo):
	logger_project.info('ProjType Convert: MultipleScened > RegularMultiple')

	prevsceneid = None
	for scenepl in convproj_obj.scene_placements:
		if scenepl.id != prevsceneid:
			if 'markers_from_scene' in convproj_obj.do_actions:
				timemarker_obj = convproj_obj.timemarker__add()
				timemarker_obj.position = scenepl.position
				if scenepl.id in convproj_obj.scenes:
					timemarker_obj.visual = convproj_obj.scenes[scenepl.id].visual.copy()
			prevsceneid = scenepl.id
			if scenepl.id in convproj_obj.scenes:
				convproj_obj.automation.merge(convproj_obj.scenes[scenepl.id].automation, scenepl.position, scenepl.duration)

	for trackid, track_obj in convproj_obj.track__iter():
		lanes = []

		for _, v in track_obj.scenes.items():
			for ln in v:
				if ln not in lanes: lanes.append(ln)

		for x in lanes: track_obj.add_lane(x)

		groupnum = 1

		for plnum, scenepl in enumerate(convproj_obj.scene_placements):
			if scenepl.id in track_obj.scenes:
				if not out_dawinfo.audio_nested:
					for laneid, scene_pl in track_obj.scenes[scenepl.id].items():
						lanepl = track_obj.lanes[laneid].placements
						groupid = 'ms2rm_'+str(groupnum)+'_'+str(plnum)+'_'+trackid+'_'+laneid+'_'+scenepl.id
						lanepl.merge_crop(scene_pl, scenepl.position, scenepl.duration, convproj_obj.scenes[scenepl.id].visual, groupid)
						groupnum += 1
				else:
					for laneid, scene_pl in track_obj.scenes[scenepl.id].items():
						track_obj.lanes[laneid].placements.merge_crop_nestedaudio(scene_pl, scenepl.position, scenepl.duration, convproj_obj.scenes[scenepl.id].visual)
	
	#exit()
	convproj_obj.type = 'rm'