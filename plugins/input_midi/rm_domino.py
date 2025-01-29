# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
import plugins
import xml.etree.ElementTree as ET

class input_domino(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'domino'
	
	def get_name(self):
		return 'Domino'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['dms']
		in_dict['track_lanes'] = True
		in_dict['track_nopl'] = True
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['fxtype'] = 'rack'
		in_dict['projtype'] = 'rm'

	def get_detect_info(self, detectdef_obj):
		detectdef_obj.type = 'xml'
		detectdef_obj.headers.append(['MarioSequencerSong'])

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import domino as proj_domino
		from objects.songinput import midi_in

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'rm'

		project_obj = proj_domino.dms_project()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		song_obj = midi_in.midi_song(16, project_obj.ppq, 120, [4,4])

		for track in project_obj.tracks:
			channel = track.channel
			track_obj = song_obj.create_track(len(track.notes))
			track_obj.track_name = track.name

			for pos, key, vol, dur in track.notes:
				track_obj.note_dur(pos, channel, key, vol, dur)

			for pos, numerator, denominator in track.timesigs:
				track_obj.time_signature(pos, numerator, denominator)

			for progc in track.programchanges:
				track_obj.program_change(progc[0], channel, progc[1])

		song_obj.postprocess()

		song_obj.to_cvpj(convproj_obj)
		
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')