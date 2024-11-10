# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging

logger_project = logging.getLogger('project')

def convert(convproj_obj, out_dawinfo):
	logger_project.info('ProjType Convert: MultipleScened > RegularMultiple')

	for trackid, track_obj in convproj_obj.track__iter():
		lanes = []

		for _, v in track_obj.scenes.items():
			for ln in v:
				if ln not in lanes: lanes.append(ln)

		for x in lanes: track_obj.add_lane(x)

		for scenepl in convproj_obj.scene_placements:
			if scenepl.id in track_obj.scenes:
				if not out_dawinfo.audio_nested:
					for laneid, scene_pl in track_obj.scenes[scenepl.id].items():
						track_obj.lanes[laneid].placements.merge_crop(scene_pl, scenepl.position, scenepl.duration, convproj_obj.scenes[scenepl.id].visual)
				else:
					for laneid, scene_pl in track_obj.scenes[scenepl.id].items():
						track_obj.lanes[laneid].placements.merge_crop_nestedaudio(scene_pl, scenepl.position, scenepl.duration, convproj_obj.scenes[scenepl.id].visual)
						
	convproj_obj.type = 'r'