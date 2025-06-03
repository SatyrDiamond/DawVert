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
		sampleref_obj = convproj_obj.sampleref__add(sampleid, wave_path, None)
		sampleref_obj.set_fileformat('wav')
		audio_obj.to_sampleref_obj(sampleref_obj)
	return sampleid

def calc_pan(i): return (i-0.5)*2

def do_auto(convproj_obj, autoloc, imin, imax, sections, defval):
	for section in sections:
		autopl_obj = convproj_obj.automation.add_pl_points(autoloc, 'float')
		time_obj = autopl_obj.time
		time_obj.set_posdur(section.startTick, section.length)
		autopoints_obj = autopl_obj.data
		for node in section.nodes: 
			autopoints_obj.points__add_normal(node.position, xtramath.between_from_one(imin, imax, node.value), 0, None)

	auto_obj = convproj_obj.automation.get_opt(autoloc)
	if auto_obj is not None: auto_obj.defualt_val = defval

class output_coolbeat(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'vs_coolbeat'
	
	def get_name(self):
		return '玩酷电音/CoolBeat'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:soundfont2']
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_mobile import viscentsoft_coolbeat

		project_obj = viscentsoft_coolbeat.coolbeat_root()

		convproj_obj.fxtype = 'none'
		convproj_obj.type = 'r'

		traits_obj = convproj_obj.traits
		traits_obj.audio_filetypes = ['wav', 'mp3']
		traits_obj.auto_types = ['pl_points']
		traits_obj.placement_loop = ['loop']
		traits_obj.audio_stretch = ['rate']

		convproj_obj.set_timings(480, False)

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.params.add('bpm', project_obj.tempo, 'float')
		convproj_obj.track_master.params.add('vol', project_obj.masterVolume, 'float')
		convproj_obj.track_master.params.add('pan', calc_pan(project_obj.masterPan), 'float')

		for an, masterAuto in enumerate(project_obj.masterAutos):
			if an == 0:
				do_auto(convproj_obj, ['main', 'bpm'], 50, 300, masterAuto.sections, project_obj.tempo)
			if an == 1:
				do_auto(convproj_obj, ['master', 'vol'], 0, 1, masterAuto.sections, project_obj.masterVolume)
			if an == 2:
				do_auto(convproj_obj, ['master', 'pan'], -1, 1, masterAuto.sections, calc_pan(project_obj.masterPan))

		for n, track in enumerate(project_obj.tracks):
			trackid = 'track_'+str(n)
			tracktype = track.type
			if tracktype in [0, 1, 3]:
				track_obj = convproj_obj.track__add(trackid, 'instrument', 1, False)
				track_obj.visual.name = track.label
				track_obj.params.add('vol', track.volume, 'float')
				track_obj.params.add('pan', calc_pan(track.pan), 'float')
				track_obj.params.add('enabled', not track.muteState, 'bool')
				track_obj.params.add('solo', track.solo, 'bool')

				if tracktype == 0:
					if track.fileName:
						track_obj.visual_inst.name = track.fileName

				if tracktype == 1:
					plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'drums')
					plugin_obj.role = 'synth'
					for cn, channel in enumerate(track.channels):
						sampleid = do_sample(convproj_obj, channel.soundPack, channel.fileName, dawvert_intent)

						drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
						drumpad_obj.key = cn
						drumpad_obj.vol = channel.volume
						drumpad_obj.pan = calc_pan(channel.pan)
						
						layer_obj.samplepartid = 'drum_%i' % cn
						sp_obj = plugin_obj.samplepart_add(layer_obj.samplepartid)
						sp_obj.sampleref = sampleid
						
					track_obj.plugslots.set_synth(pluginid)

				if tracktype == 3:
					plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'soundfont2', None)
					plugin_obj.role = 'synth'
					track_obj.plugslots.set_synth(pluginid)
					fileref_obj = convproj_obj.fileref__add(trackid, track.filePath, None)
					fileref_obj.search_local(dawvert_intent.input_folder)
					plugin_obj.fileref__set('file', trackid)
					if track.fileName:
						track_obj.visual_inst.name = track.fileName

				for section in track.sections:
					placement_obj = track_obj.placements.add_notes()
					time_obj = placement_obj.time
					time_obj.set_posdur(section.startTick, section.length)
					cvpj_notelist = placement_obj.notelist
					noteoffset = 0 if tracktype == 1 else 60
					for note in section.notes:
						cvpj_notelist.add_r(note.startTick, note.length, note.key-noteoffset, note.volume, {})
					if cvpj_notelist:
						placement_obj.auto_dur(1920, 1920)
						loop_data = time_obj.duration
						time_obj.set_loop_data(0, 0, time_obj.duration)
						time_obj.duration *= (section.length)/loop_data

			if tracktype == 2:
				track_obj = convproj_obj.track__add(trackid, 'audio', 1, False)
				track_obj.visual.name = track.label
				track_obj.params.add('vol', track.volume, 'float')
				track_obj.params.add('pan', calc_pan(track.pan), 'float')
				track_obj.params.add('enabled', not track.muteState, 'bool')
				track_obj.params.add('solo', track.solo, 'bool')
				sampleid = do_sample(convproj_obj, track.soundPack, track.fileName, dawvert_intent)
				for section in track.sections:
					placement_obj = track_obj.placements.add_audio()
					time_obj = placement_obj.time
					time_obj.set_posdur(section.startTick, section.length)

					sp_obj = placement_obj.sample
					sp_obj.stretch.timing.set__orgtempo(project_obj.tempo)
					sp_obj.stretch.preserve_pitch = True
					sp_obj.stretch.uses_tempo = True
					sp_obj.sampleref = sampleid

			for an, ta in enumerate(track.autos):
				if an == 0:
					do_auto(convproj_obj, ['track', trackid, 'vol'], 0, 1, ta.sections, track.volume)
				if an == 1:
					do_auto(convproj_obj, ['track', trackid, 'pan'], -1, 1, ta.sections, calc_pan(track.pan))

		convproj_obj.automation.set_persist_all(False)
