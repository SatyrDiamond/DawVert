# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import os

class input_korg_m1_nds(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'

	def get_shortname(self):
		return 'korg_m1_nds'

	def get_name(self):
		return 'Korg M1 DS'

	def get_priority(self):
		return 0

	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_past import korg_m1_nds as proj_korg_m1_nds

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		project_obj = proj_korg_m1_nds.korg_m1_proj()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		projsong_obj = project_obj.songs[dawvert_intent.songnum]
		steps = projsong_obj.steps
		swing = projsong_obj.swing

		convproj_obj.params.add('bpm', projsong_obj.tempo, 'float')
		convproj_obj.metadata.name = projsong_obj.name

		for num, channel_obj in enumerate(projsong_obj.channels):
			cvpj_trackid = str(num)
			track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)

			for block_obj in channel_obj.blocks:
				placement_obj = track_obj.placements.add_notes()
				placement_obj.time.set_posdur(block_obj.offset*steps, steps)

				cvpj_notelist = placement_obj.notelist

				for note in block_obj.notes:
					oswing = ((swing-50)/50) if (note.offset%2) else 0

					cvpj_notelist.add_r(note.offset+oswing, note.length, (note.pitch-128)-60, note.velocity/15, None)