# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_musicphrase(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'musicphrase'
	
	def get_name(self):
		return 'MusicPhrase XL'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['projtype'] = 'cs'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_past import musicphrase as proj_musicphrase

		project_obj = proj_musicphrase.musicphrase_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.set_timings(96)

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'cs'

		metadata_obj = convproj_obj.metadata

		traits_obj = convproj_obj.traits
		traits_obj.fxrack_params = ['vol','pan','pitch']
		traits_obj.auto_types = ['nopl_ticks']

		convproj_obj.metadata.name = project_obj.name 
		convproj_obj.metadata.copyright = project_obj.copyright
		convproj_obj.metadata.author = project_obj.author
		convproj_obj.metadata.comment_text = project_obj.comment

		convproj_obj.transport.current_pos = project_obj.curpos/256
		convproj_obj.transport.loop_active = bool(project_obj.loop_on)
		convproj_obj.transport.loop_start = project_obj.loop_start/256
		convproj_obj.transport.loop_end = project_obj.loop_end/256

		convproj_obj.params.add('bpm', (project_obj.tempo/3072000)*120, 'float')

		track_pl = []
		for n, mpxl_track in enumerate(project_obj.tracks):
			track_obj = convproj_obj.track__add(str(n), 'midi', 1, False)
			track_obj.visual.name = mpxl_track.name
			track_obj.visual.color.set_int(list(mpxl_track.color[0:3]))
			track_obj.params.add('enabled', not mpxl_track.mute, 'bool')
			track_obj.params.add('solo', mpxl_track.solo, 'bool')
			track_obj.armed.on = bool(mpxl_track.record)
			track_obj.armed.in_keys = bool(mpxl_track.record)

			track_obj.midi.out_enabled = True
			track_obj.midi.out_chanport.chan = mpxl_track.channel
			track_obj.midi.out_chanport.port = 0

			if mpxl_track.program != -1:
				track_obj.midi.out_inst.patch = mpxl_track.program

			for clip in mpxl_track.clips:
				placement_obj = track_obj.placements.add_midi()
				placement_obj.visual.name = clip.name
				placement_obj.visual.color.set_int(list(clip.color[0:3]))
				placement_obj.time.set_posdur(clip.start, clip.size)

				channel = mpxl_track.channel

				events_obj = placement_obj.midievents
				events_obj.has_duration = True
				events_obj.ppq = 96
				for note in clip.notes:
					events_obj.add_note_dur_off_vel(note.pos, channel, note.note, note.vel, max(0, note.end-note.pos), note.vel_off)

				for ctrl in clip.ctrls:
					event_type = ctrl.type
					if event_type == 10: events_obj.add_note_pressure(ctrl.pos, channel, ctrl.data1, ctrl.data2)
					elif event_type == 11: events_obj.add_control(ctrl.pos, channel, ctrl.data1, ctrl.data2)
					elif event_type == 12: events_obj.add_program(ctrl.pos, channel, ctrl.data1)
					elif event_type == 13: events_obj.add_chan_pressure(ctrl.pos, channel, ctrl.data1)
					elif event_type == 14: events_obj.add_pitch_hi_lo(ctrl.pos, channel, ctrl.data2, ctrl.data1)