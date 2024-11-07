# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_petaporon(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'flipper0'
	def get_name(self): return 'Flipper Zero'
	def get_priority(self): return 0
	def supported_autodetect(self): return False
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['fmf']
		in_dict['track_nopl'] = True
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_flipperzero
		from functions import note_data

		convproj_obj.type = 'r'
		convproj_obj.set_timings(1, True)

		project_obj = proj_flipperzero.fmf_song()
		project_obj.load_from_file(input_file)

		convproj_obj.params.add('bpm', project_obj.bpm, 'float')

		track_obj = convproj_obj.track__add('flipper', 'instrument', 0, False)
		track_obj.visual.name = 'Flipper Zero'
		track_obj.visual.color.set_float([0.94, 0.58, 0.23])

		curpos = 0
		for note in project_obj.notes:
			notedur = (project_obj.duration)*(1/note.duration)
			for x in range(note.dots): notedur *= 1.5
			#print(notedur,note.key,note.sharp,note.octave,note.dots, (1.5**note.dots))
			if note.key != 'P':
				notekey = note_data.keyletter_to_note(note.key, note.octave-5)
				track_obj.placements.notelist.add_r(curpos, notedur, notekey, 1, None)
			curpos += notedur

		convproj_obj.do_actions.append('do_singlenotelistcut')