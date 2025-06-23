# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import value_midi
import xml.etree.ElementTree as ET
import plugins
import json

class input_cvpj_f(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'evolution_midi'
	
	def get_name(self):
		return 'Evolution Midi'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['projtype'] = 'multi'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_past import evolution_midi as proj_evolution_midi

		project_obj = proj_evolution_midi.evo_midi_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.set_timings(192)

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'cm'

		metadata_obj = convproj_obj.metadata

		traits_obj = convproj_obj.traits
		traits_obj.fxrack_params = ['vol','pan','pitch']
		traits_obj.auto_types = ['nopl_ticks']

		track_pl = []
		for n, evo_track in enumerate(project_obj.tracks):
			track_obj = convproj_obj.track__add(str(n), 'midi', 1, False)
			track_obj.visual.name = evo_track.name
			if evo_track.channel != -1:
				track_obj.midi.out_enabled = True
				track_obj.midi.out_chanport.chan = evo_track.channel
				track_obj.midi.out_chanport.port = 0
			if evo_track.patch != -1:
				track_obj.midi.out_inst.patch = evo_track.patch
			track_pl.append(track_obj)

		for evo_clip in project_obj.clips:
			track_obj = track_pl[evo_clip.tracknum]
			placement_obj = track_obj.placements.add_midi()
			placement_obj.visual.name = evo_clip.name
			placement_obj.time.set_startend(evo_clip.position, evo_clip.duration)

			events_obj = placement_obj.midievents
			events_obj.has_duration = True
			events_obj.ppq = int(192)

			events = (project_obj.clips[evo_clip.linked] if evo_clip.linked>-1 else evo_clip).events
			channel = track_obj.midi.out_chanport.chan
			for event in events:
				if event.type == 9:
					note, vel, dur = event.data
					events_obj.add_note_dur(event.pos, channel, note, vel, dur)
				if event.type == 11:
					ctrl, val = event.data
					events_obj.add_control(event.pos, channel, ctrl, val)