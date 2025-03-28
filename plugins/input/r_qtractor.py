# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
import math

import logging
logger_input = logging.getLogger('input')

def calcsec(val, ppq):
	return (val/ppq)/50

class input_midi(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'qtractor'
	
	def get_name(self):
		return 'Qtractor'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['audio_filetypes'] = ['wav']
		in_dict['file_ext'] = ['qtr']
		in_dict['auto_types'] = ['nopl_ticks']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['projtype'] = 'r'
		in_dict['time_seconds'] = True

	def get_detect_info(self, detectdef_obj):
		detectdef_obj.headers.append([0, b'MThd'])

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import qtractor as proj_qtractor
		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		project_obj = proj_qtractor.qtractor_project()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		ppq = project_obj.properties.ticks_per_beat
		tempo = project_obj.properties.tempo
		tempomul = tempo/120

		convproj_obj.params.add('bpm', tempo, 'float')
		
		#for audioid, filename in project_obj.files.audio_list.items():
		#	sampleref_obj = convproj_obj.sampleref__add(audioid, filename, None)

		for tracknum, qtrack in enumerate(project_obj.tracks):
			cvpj_trackid = str(tracknum)

			if qtrack.type == 'audio':
				track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
			if qtrack.type == 'midi':
				track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)

			track_obj.visual.name = qtrack.name
			if qtrack.view.foreground_color:
				track_obj.visual.color.set_hex(qtrack.view.foreground_color)

			track_obj.params.add('vol', qtrack.state.gain, 'float')
			track_obj.params.add('pan', qtrack.state.panning, 'float')
			track_obj.params.add('enabled', bool(not qtrack.state.mute), 'bool')
			track_obj.params.add('solo', bool(qtrack.state.solo), 'bool')

			clipcolor = qtrack.view.background_color
			
			if qtrack.type == 'audio':
				for clip in qtrack.clips:
					placement_obj = track_obj.placements.add_audio()
					placement_obj.time.position_real = calcsec(clip.properties.start, ppq)
					placement_obj.time.duration_real = calcsec(clip.properties.length, ppq)
					placement_obj.visual.name = clip.name

					if clipcolor: placement_obj.visual.color.set_hex(clipcolor)
					filepath = clip.audioclip.filename

					pitch = math.log2(1/clip.audioclip.pitch_shift)*-12
					placement_obj.sample.pitch = pitch
					sp_obj = placement_obj.sample
					sp_obj.sampleref = filepath
					sp_obj.vol = clip.properties.gain
					sp_obj.pan = clip.properties.panning
					placement_obj.fade_in.set_dur(calcsec(clip.properties.fade_in, ppq), 'seconds')
					placement_obj.fade_out.set_dur(calcsec(clip.properties.fade_out, ppq), 'seconds')
					sampleref_obj = convproj_obj.sampleref__add(filepath, filepath, None)
					sampleref_obj.search_local(os.path.dirname(dawvert_intent.input_file))
					stretch_obj = placement_obj.sample.stretch
					stretch_obj.preserve_pitch = True
					if clip.audioclip.time_stretch:
						stretch_obj.set_rate_tempo(tempo, (clip.audioclip.time_stretch)*tempomul, True)

			if qtrack.type == 'midi':
				for clip in qtrack.clips:
					placement_obj = track_obj.placements.add_notes()
					placement_obj.time.position_real = calcsec(clip.properties.start, ppq)
					placement_obj.time.duration_real = calcsec(clip.properties.length, ppq)
					placement_obj.visual.name = clip.name

					if clipcolor: placement_obj.visual.color.set_hex(clipcolor)
					filepath = clip.midiclip.filename

					fileref_obj = convproj_obj.fileref__add(filepath, filepath, None)
					fileref_obj.search_local(os.path.dirname(dawvert_intent.input_file))

					placement_obj.notelist.midi_from(fileref_obj.get_path(None, False))