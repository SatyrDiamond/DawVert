# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from objects.convproj import fileref
import os

class input_fl_mobile_old(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'bajloop'
	
	def get_name(self):
		return "Bhaji's Loops"
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		pass

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_mobile import bajloops
		from objects import audio_data

		project_obj = bajloops.bajloop_file()

		convproj_obj.type = 'mi'

		convproj_obj.set_timings(8)

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.do_actions.append('do_addloop')

		for num, binst in enumerate(project_obj.insts):
			inst_obj = convproj_obj.instrument__add(str(num+1))
			visual_obj = inst_obj.visual
			visual_obj.color.set_int(binst.color.tolist())
			visual_obj.name = binst.name

		patsize = {}
		for num, bpattern in enumerate(project_obj.patterns):
			if len(bpattern.events):
				nle_obj = convproj_obj.notelistindex__add(str(num+1))
				visual_obj = nle_obj.visual
				visual_obj.name = bpattern.name
				visual_obj.color.set_int(bpattern.color.tolist())
				cvpj_notelist = nle_obj.notelist
				for event in bpattern.events:
					cvpj_notelist.add_m(str(event[3]), event[0], event[1]-event[0], int(event[2])-60, 1, None)
				nl_dur = cvpj_notelist.get_dur()
				patsize[num+1] = (nl_dur/32).__ceil__()

		playlist_stor = {}
		for num in range(8):
			playlist_stor[num] = {}

		for pos, data in enumerate(project_obj.placements):
			for num, patn in enumerate(data):
				if patn: 
					playlist_stor[num][pos] = int(patn)

		for num in range(8):
			playlist_obj = convproj_obj.playlist__add(num, 1, True)
			for pos, pnum in playlist_stor[num].items():
				s = (patsize[pnum] if pnum in patsize else 1)
				placement_obj = playlist_obj.placements.add_notes_indexed()
				placement_obj.fromindex = str(pnum)
				time_obj = placement_obj.time
				time_obj.set_posdur(pos*32, 32*s)