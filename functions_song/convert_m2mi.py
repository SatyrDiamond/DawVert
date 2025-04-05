# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
logger_project = logging.getLogger('project')

VISUAL_COLOR = True

def convert(convproj_obj):
	logger_project.info('ProjType Convert: Multiple > MultipleIndexed')

	existingpatterns = []
	pn = 1
	for pl_id, playlist_obj in convproj_obj.playlist__iter():
		x, pn = playlist_obj.placements.to_indexed_notes(existingpatterns, pn)

		for patid, nle_data in x:
			nle_obj = convproj_obj.notelistindex__add(patid)
			nle_obj.notelist = nle_data[0]
			nle_obj.visual.name = nle_data[1]
			nle_obj.visual.color = nle_data[2]

	existingsamples = []
	pn = 1
	for pl_id, playlist_obj in convproj_obj.playlist__iter():
		x, pn = playlist_obj.placements.to_indexed_audio(existingsamples, pn)
		for patid, sle_data in x: 
			convproj_obj.sample_index[patid] = sle_data

	if VISUAL_COLOR:
		assoc_color = dict([[x, []] for x in convproj_obj.sample_index])
		for pl_id, playlist_obj in convproj_obj.playlist__iter():
			for pla in playlist_obj.placements.pl_audio_indexed:
				fromindex = pla.fromindex
				if fromindex:
					if pl_id not in assoc_color[fromindex]:
						assoc_color[fromindex].append(pl_id)

		for fromindex, plnums in assoc_color.items():
			if len(plnums)==1 and fromindex in convproj_obj.sample_index:
				playlist_obj = convproj_obj.playlist[plnums[0]]
				sle_data = convproj_obj.sample_index[fromindex]
				if not sle_data.visual.color:
					sle_data.visual.color = playlist_obj.visual.color.copy()

		assoc_color = dict([[x, []] for x in convproj_obj.notelist_index])
		for pl_id, playlist_obj in convproj_obj.playlist__iter():
			for pla in playlist_obj.placements.pl_notes_indexed:
				fromindex = pla.fromindex
				if fromindex:
					if pl_id not in assoc_color[fromindex]:
						assoc_color[fromindex].append(pl_id)

		for fromindex, plnums in assoc_color.items():
			if len(plnums)==1 and fromindex in convproj_obj.notelist_index:
				playlist_obj = convproj_obj.playlist[plnums[0]]
				sle_data = convproj_obj.notelist_index[fromindex]
				if not sle_data.visual.color:
					sle_data.visual.color = playlist_obj.visual.color.copy()

	convproj_obj.type = 'mi'