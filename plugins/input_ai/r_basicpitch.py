# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import sys
import importlib.util

class input_ex_basic_pitch(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'basic_pitch'
	def get_name(self): return 'Basic Pitch'
	def get_prop(self, in_dict): 
		in_dict['track_nopl'] = True
	def usable(self): 
		usable = importlib.util.find_spec('basic_pitch')
		usable_meg = 'Basic Pitch is not installed. do "pip install basic_pitch"' if not usable else ''
		return usable, usable_meg
	def parse(self, convproj_obj, input_file, dv_config):
		from basic_pitch.inference import predict
		from basic_pitch import ICASSP_2022_MODEL_PATH

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, False)
		convproj_obj.params.add('bpm', 120, 'float')

		model_output, midi_data, note_events = predict(input_file)

		track_obj, plugin_obj = convproj_obj.track__addspec__midi('basicpitch', 'basicpitch', 0, 0, False, 1, False)

		for note_event in note_events:
			track_obj.placements.notelist.add_r(
				float(note_event[0])*8, 
				float(note_event[1]-note_event[0])*8, 
				int(note_event[2]-60), 
				float(note_event[3]), 
				{})

			if not all(item == 0 for item in note_event[4]):
				for num, point in enumerate(note_event[4]):
					autopoint_obj = track_obj.placements.notelist.last_add_auto('pitch')
					autopoint_obj.pos = num*0.1
					autopoint_obj.value = (point-1)/4
