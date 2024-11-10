# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import logging
logger_input = logging.getLogger('input')

class input_ex_basic_pitch(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'funkin'
	def get_name(self): return 'Friday Night Funkin'
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'json'
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv']
	def parse(self, convproj_obj, input_file, dv_config):
		convproj_obj.type = 'r'
		convproj_obj.set_timings(600, False)
		convproj_obj.params.add('bpm', 120, 'float')

		bytestream = open(input_file, 'r', encoding='utf8')

		try:
			funkin_json = json.load(bytestream)
		except UnicodeDecodeError as t:
			logger_input.error('funkin: Unicode Decode Error: '+str(t))
			exit()
		except json.decoder.JSONDecodeError as t:
			logger_input.error('funkin: JSON parsing error: '+str(t))
			exit()

		fnf_scrollSpeed = funkin_json['scrollSpeed'] if 'scrollSpeed' in funkin_json else {}
		fnf_events = funkin_json['events'] if 'events' in funkin_json else {}
		fnf_notes = funkin_json['notes'].copy() if 'notes' in funkin_json else {}

		numchars = 2
		numnotes = 4
		charcolors = [[0.22, 0.70, 0.82], [0.69, 0.40, 0.81]]

		endsong = 0

		for notedif, notedata in fnf_notes.items():
			trackchar = []

			for x in range(numchars):
				trackid = notedif+str(x)
				track_obj = convproj_obj.track__add(trackid, 'instrument', 1, False)
				track_obj.visual.name = 'pyr_'+str(x)+','+notedif
				track_obj.visual.color.set_float(charcolors[(numchars-x)-1])
				placement_obj = track_obj.placements.add_notes()
				trackchar.append(placement_obj)

			for note in notedata:
				key = note['d']
				pos = note['t']
				dur = note['l'] if 'l' in note else 150
				event = note['k'] if 'k' in note else None
				numtrack = key//numnotes
				trackchar[numtrack].notelist.add_r(pos, dur, key-(numnotes*numtrack), 1, None)
				trackchar[numtrack].time.duration = pos+dur

				endpos = pos+dur
				if endsong<endpos: endsong = endpos

				if 'l' in note: del note['l']
				del note['d']
				del note['t']

				if 'k' in note: del note['k']

		convproj_obj.do_actions.append('do_singlenotelistcut')