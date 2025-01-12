# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import struct
import os.path
from objects import globalstore
from objects import colors

def do_visual(cvpj_visual, zb_visual, color_index, colordata):
	cvpj_visual.name = zb_visual.name
	if color_index != -1:
		colorfloat = colordata.getcolornum(color_index)
		cvpj_visual.color.set_float(colorfloat)

class input_zenbeats(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'zenbeats'
	
	def get_name(self):
		return 'ZenBeats'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['song']
		in_dict['plugin_included'] = []
		in_dict['auto_types'] = ['nopl_points']
		in_dict['projtype'] = 'r'
		in_dict['audio_stretch'] = ['rate']
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop', 'loop_eq', 'loop_off', 'loop_adv', 'loop_adv_off']
		in_dict['audio_filetypes'] = ['wav']
		in_dict['plugin_ext_platforms'] = ['win']
		in_dict['fxtype'] = 'groupreturn'

	def get_detect_info(self, detectdef_obj):
		detectdef_obj.headers.append([0, b'PMD'])

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import proj_zenbeats

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.set_timings(1, True)

		globalstore.dataset.load('zenbeats', './data_main/dataset/zenbeats.dset')
		colordata = colors.colorset.from_dataset('zenbeats', 'global', 'main')

		project_obj = proj_zenbeats.zenbeats_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.params.add('bpm', project_obj.bpm, 'float')

		added_samples = []

		master_id = None
		track_groups = []
		for zb_track in project_obj.tracks:
			if zb_track.type == 258: 
				track_groups.append(zb_track.uid)
				track_obj = convproj_obj.fx__group__add(zb_track.uid)
				do_visual(track_obj.visual, zb_track.visual, zb_track.color_index, colordata)

			if zb_track.type == 130: 
				return_obj = convproj_obj.track_master.fx__return__add(zb_track.uid)
				do_visual(return_obj.visual, zb_track.visual, zb_track.color_index, colordata)

			if zb_track.type == 18: 
				master_id = zb_track.uid
				do_visual(convproj_obj.track_master.visual, zb_track.visual, zb_track.color_index, colordata)

		for zb_track in project_obj.tracks:
			master_id = zb_track.sub_track_master_track_uid
			if master_id in track_groups or master_id==None:
				if zb_track.type in [0, 1, 97]:
					track_obj = convproj_obj.track__add(zb_track.uid, 'instrument', 1, False)
					do_visual(track_obj.visual, zb_track.visual, zb_track.color_index, colordata)
					if master_id: track_obj.group = master_id

					for zb_pattern in zb_track.patterns:
						placement_obj = track_obj.placements.add_notes()
						do_visual(placement_obj.visual, zb_pattern.visual, zb_pattern.color_index, colordata)
						placement_obj.time.set_startend(zb_pattern.start_beat, zb_pattern.end_beat)
						placement_obj.time.set_loop_data(zb_pattern.loop_play_start, zb_pattern.loop_start_beat, zb_pattern.loop_end_beat)

						for zb_note in zb_pattern.notes:
							note_dur = max(zb_note.end-zb_note.start, 0)
							placement_obj.notelist.add_r(zb_note.start, note_dur, zb_note.semitone-60, zb_note.velocity/127, None)
	
				if zb_track.type == 2:
					track_obj = convproj_obj.track__add(zb_track.uid, 'audio', 1, False)
					do_visual(track_obj.visual, zb_track.visual, zb_track.color_index, colordata)
					if master_id: track_obj.group = master_id

					for zb_pattern in zb_track.patterns:
						placement_obj = track_obj.placements.add_audio()
						do_visual(placement_obj.visual, zb_pattern.visual, zb_pattern.color_index, colordata)
						placement_obj.time.set_startend(zb_pattern.start_beat, zb_pattern.end_beat)
						placement_obj.time.set_loop_data(zb_pattern.loop_play_start, zb_pattern.loop_start_beat, zb_pattern.loop_end_beat)

						if zb_pattern.audio_file:
							if zb_pattern.audio_file not in added_samples:
								sampleref_obj = convproj_obj.sampleref__add(zb_pattern.audio_file, zb_pattern.audio_file, None)
								sampleref_obj.search_local(os.path.dirname(dawvert_intent.input_file))
								added_samples.append(zb_pattern.audio_file)
	
							sp_obj = placement_obj.sample
							sp_obj.sampleref = zb_pattern.audio_file
							speedrate = zb_pattern.preserve_pitch if zb_pattern.preserve_pitch is not None else 1
							sp_obj.stretch.set_rate_tempo(project_obj.bpm, speedrate, False)
							sp_obj.stretch.preserve_pitch = True
							sp_obj.stretch.algorithm = 'stretch'
				#else:
				#	print(zb_track.type, zb_track.visual.name)

		#exit()