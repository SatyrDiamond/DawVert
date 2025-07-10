# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
import plugins
import xml.etree.ElementTree as ET
from objects import globalstore

class input_v2m(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'v2m'
	
	def get_name(self):
		return 'Farbrausch V2M'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['projtype'] = 'cs'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_past import v2m as proj_v2m
		from objects import colors

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'cs'

		traits_obj = convproj_obj.traits
		traits_obj.fxrack_params = ['vol','pan','pitch']
		traits_obj.auto_types = ['nopl_ticks']
		traits_obj.track_nopl = True

		project_obj = proj_v2m.v2m_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.set_timings(project_obj.timediv)

		for n, track in enumerate(project_obj.tracks):
			track_obj = convproj_obj.track__add(str(n), 'midi', 1, False)
			track_obj.visual.name = 'Track #'+str(n)
			track_obj.midi.out_enabled = True
			track_obj.midi.out_chanport.chan = n
			track_obj.midi.out_chanport.port = 0

			events_obj = track_obj.placements.midievents

			cur_note = 0
			cur_pos = 0
			for note in track.notes:
				cur_pos += note[0]
				cur_note += note[1]
				if not note[2]&128:
					events_obj.add_note_on(cur_pos, n, cur_note, note[2]&127)
				else:
					events_obj.add_note_off(cur_pos, n, cur_note, note[2]&127)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')