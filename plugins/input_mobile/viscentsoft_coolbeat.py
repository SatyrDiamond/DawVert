# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import xtramath
from objects.convproj import fileref

def do_sample(convproj_obj, soundPack, filename, dawvert_intent):
	from objects import audio_data
	samplefolder = dawvert_intent.path_samples['extracted']
	sampleid = str(soundPack)+'>>'+str(filename)
	fileref_obj = fileref.cvpj_fileref()
	fileref_obj.set_path(None, filename, 1)
	fileref_obj.search_local(dawvert_intent.input_folder)
	if fileref_obj.exists(None):
		audio_obj = audio_data.audio_obj()
		audio_obj.channels = 1
		audio_obj.rate = 44100
		audio_obj.set_codec('int16')
		audio_obj.pcm_from_file(fileref_obj.get_path(None, 0))
		wave_path = samplefolder+filename+'.wav'
		audio_obj.to_file_wav(wave_path)
		convproj_obj.sampleref__add(sampleid, wave_path, None)
	return sampleid

class output_coolbeat(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'viscentsoft_coolbeat'
	
	def get_name(self):
		return '玩酷电音/CoolBeat'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['audio_filetypes'] = ['wav', 'mp3']
		in_dict['file_ext'] = 'mlp'
		in_dict['auto_types'] = ['pl_points']
		in_dict['placement_loop'] = ['loop']
		in_dict['audio_stretch'] = ['rate']
		in_dict['fxtype'] = 'groupreturn'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_mobile import viscentsoft_coolbeat

		project_obj = viscentsoft_coolbeat.coolbeat_root()

		convproj_obj.fxtype = 'none'
		convproj_obj.type = 'r'

		convproj_obj.set_timings(480, False)

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		for n, track in enumerate(project_obj.tracks):
			trackid = 'track_'+str(n)
			tracktype = track.type
			if tracktype in [0, 1, 3]:
				track_obj = convproj_obj.track__add(trackid, 'instrument', 1, False)
				track_obj.visual.name = track.label
				track_obj.params.add('vol', track.volume, 'float')
				track_obj.params.add('pan', (track.pan-0.5)*2, 'float')
				track_obj.params.add('enabled', not track.muteState, 'bool')
				track_obj.params.add('solo', track.solo, 'bool')
				for section in track.sections:
					placement_obj = track_obj.placements.add_notes()
					placement_obj.time.set_posdur(section.startTick, section.length)
					cvpj_notelist = placement_obj.notelist
					noteoffset = 0 if tracktype == 1 else 60
					for note in section.notes:
						cvpj_notelist.add_r(note.startTick, note.length, note.key-noteoffset, note.volume, {})
					if cvpj_notelist:
						placement_obj.auto_dur(1920, 1920)
						loop_data = placement_obj.time.duration
						placement_obj.time.set_loop_data(0, 0, placement_obj.time.duration)
						placement_obj.time.duration *= (section.length)/loop_data

			if tracktype == 2:
				track_obj = convproj_obj.track__add(trackid, 'audio', 1, False)
				track_obj.visual.name = track.label
				track_obj.params.add('vol', track.volume, 'float')
				track_obj.params.add('pan', (track.pan-0.5)*2, 'float')
				track_obj.params.add('enabled', not track.muteState, 'bool')
				track_obj.params.add('solo', track.solo, 'bool')
				sampleid = do_sample(convproj_obj, track.soundPack, track.fileName, dawvert_intent)
				for section in track.sections:
					placement_obj = track_obj.placements.add_audio()
					placement_obj.time.set_posdur(section.startTick, section.length)

					sp_obj = placement_obj.sample
					sp_obj.stretch.set_rate_tempo(project_obj.tempo, 1, True)
					sp_obj.stretch.preserve_pitch = True
					sp_obj.sampleref = sampleid

		#print('d')