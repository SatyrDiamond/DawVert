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

		event_tracks = {}
		eprev_pl = None
		eprev_pos = None
		for e in fnf_events:
			pos = e['t']
			event_e = e['e']
			event_v = e['v']

			if eprev_pl and eprev_pos:
				eprev_pl.time.duration = pos-eprev_pl.time.position

			if event_e not in event_tracks:
				etrack_obj = convproj_obj.add_track('event_'+event_e, 'instrument', 1, False)
				etrack_obj.visual.name = '__fnf,event,'+event_e
				etrack_obj.visual.color.set_float([0.5, 1, 0.11])
				event_tracks[event_e] = etrack_obj

			current_epl = etrack_obj.placements.add_notes()
			current_epl.visual.name = event_e
			if isinstance(event_v, dict): current_epl.visual.name =json.dumps(event_v)
			else: current_xpl.visual.name = str(event_v)
			current_epl.time.position = pos
			eprev_pl = current_epl
			eprev_pos = pos


		endsong = 0

		for notedif, notedata in fnf_notes.items():
			trackchar = []

			speed = fnf_scrollSpeed[notedif] if notedif in fnf_scrollSpeed else 1.0

			for x in range(numchars):
				trackid = notedif+str(x)
				track_obj = convproj_obj.add_track(trackid, 'instrument', 1, False)
				track_obj.visual.name = '__fnf,note,'+notedif
				track_obj.visual.color.set_float(charcolors[(numchars-x)-1])
				if x == 0: track_obj.visual.name += ",%"+str(speed)
				track_obj.visual.name += ",^"+str(x)
				placement_obj = track_obj.placements.add_notes()
				trackchar.append(placement_obj)
			xtrack_obj = convproj_obj.add_track(notedif+'_extra', 'instrument', 1, False)
			xtrack_obj.visual.name = '__fnf,note,'+notedif+',extra'
			xtrack_obj.visual.color.set_float([0.89, 0.37, 0.11])

			prev_x = {}
			prev_event = None
			current_xpl = False
			current_xt = None

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

				if prev_event != event:
					prev_event = event
					if event: 
						current_xpl = xtrack_obj.placements.add_notes()
						
						if isinstance(event, dict): current_xpl.visual.name = 'D>'+json.dumps(event)
						else: current_xpl.visual.name = 'S>'+str(event)
						hashcolor = (hash(event)/10000000000000000000)
						current_xpl.visual.color.set_hsv(hashcolor, 0.7, 0.6)

						current_xpl.time.position = pos
						current_xt = pos
					else: 
						current_xpl = None
						current_xt = None

				if current_xpl and event: current_xpl.time.duration = pos+dur-current_xt
				if prev_x != note: prev_x = note
				if 'k' in note: del note['k']

				if note: print(note)

			prev_pl = None
			for pl in xtrack_obj.placements.pl_notes:
				endpos = pl.time.duration+pl.time.position
				if endsong<endpos: endsong = endpos
				if pl.time.duration < 600: 
					pl.time.duration = 600
					pl.visual.name = 'N.'+pl.visual.name

			xtrack_obj.placements.pl_notes.remove_overlaps()

		if eprev_pl:
			eprev_pl.time.duration = max(endsong-eprev_pl.time.position, 0)

		convproj_obj.do_actions.append('do_singlenotelistcut')