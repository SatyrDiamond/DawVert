# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging

logger_project = logging.getLogger('project')

def convert(convproj_obj, dv_config):
	logger_project.info('ProjType Convert: MultipleIndexed > Multiple')

	do_unused = 'mi2m-output-unused-nle' in dv_config.flags_convproj

	nle_list = [x for x in convproj_obj.notelist_index]
	used_nle = []

	for pl_id, playlist_obj in convproj_obj.playlist__iter():
		used_nle += [x.fromindex for x in playlist_obj.placements.pl_notes_indexed.data]

	unused_nle = list(set(nle_list))

	for x in used_nle:
		if x in unused_nle: unused_nle.remove(x)

	if do_unused:
		pl_obj_found = None
		maxdur = convproj_obj.get_dur()

		for pl_id, playlist_obj in convproj_obj.playlist__iter():
			if not playlist_obj.placements.get_dur():
				pl_obj_found = playlist_obj
				break

		usednums = list(convproj_obj.playlist) 

		num = 0
		while True:
			if num not in usednums:
				pl_obj_found = convproj_obj.playlist__add(num, 1, True)
				pl_obj_found.visual.name = '>>> UNUSED'
				break
			num += 1

		startpos = maxdur
		for x in unused_nle:
			nle_obj = convproj_obj.notelist_index[x]
			nledur = nle_obj.notelist.get_dur()
			if nle_obj.visual.name: nle_obj.visual.name = '[UNUSED] '+nle_obj.visual.name
			else: nle_obj.visual.name = '[UNUSED]'

			if nledur:
				startpos += convproj_obj.time_ppq*4

				i_pl = pl_obj_found.placements.add_notes_indexed()
				i_pl.fromindex = x
				i_pl.time.set_posdur(startpos, nledur)

				startpos += nledur

	for pl_id, playlist_obj in convproj_obj.playlist__iter():
		playlist_obj.placements.unindex_notes(convproj_obj.notelist_index)
		playlist_obj.placements.unindex_audio(convproj_obj.sample_index)

	convproj_obj.notelist_index = {}
	convproj_obj.sample_index = {}

	convproj_obj.type = 'm'