# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_data
from functions import placement_data
from functions_tracks import tracks_r
import plugins
import json

class input_ex_basic_pitch(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'basic_pitch'
	def gettype(self): return 'r'
	def supported_autodetect(self): return False
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Basic Pitch'
		dawinfo_obj.track_nopl = True
	def parse(self, convproj_obj, input_file, dv_config):
		convproj_obj.type = 'r'
		convproj_obj.set_timings(1, False)
		convproj_obj.params.add('bpm', 120, 'float')

		from basic_pitch.inference import predict
		from basic_pitch import ICASSP_2022_MODEL_PATH

		model_output, midi_data, note_events = predict(input_file)

		track_obj = convproj_obj.add_track('basicpitch', 'instrument', 1, False)

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
