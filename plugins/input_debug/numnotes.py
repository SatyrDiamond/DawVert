# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class plugintest(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'numnotes'
	def get_name(self): return 'number of notes'
	def get_prop(self, in_dict): 
		pass
	def parse(self, convproj_obj, input_file, dv_config):
		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, False)

		for numtracks in range(30):
			trackid = str('track'+str(numtracks))
			track_obj = convproj_obj.add_track(trackid, 'instrument', 1, False)
			track_obj.visual.name = '.'
			placement_obj = track_obj.placements.add_notes()
			placement_obj.time.position = 0
			placement_obj.time.duration = 100
			for note in range(numtracks+1):
				placement_obj.notelist.add_r(note, 1, note-1, 1, {})


