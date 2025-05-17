# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import urllib.parse
import os
import copy
import json

contentpath = os.path.join(os.path.expanduser('~'), 'Music\\Serato Studio\\Content\\')

def parse_filepath(i_file):
	filename = urllib.parse.unquote(i_file)
	if filename.startswith('content://'): filepath = contentpath+filename[10:]
	elif filename.startswith('file://'): filepath = filename[8:]
	else: filepath = filename
	return filepath.replace("\\","/").replace("//","/")

def calcpos_stretch(orgpoint, original_bpm, bpm, playback_speed, printd):
	outpos = orgpoint
	outpos *= 2
	outpos /= 120/bpm
	outpos /= playback_speed
	outpos /= bpm/original_bpm
	return outpos

def calcspeed(playback_speed, bpm, original_bpm, modchange):
	playspeed = playback_speed*modchange
	playspeed *= 120/bpm
	playspeed *= bpm/original_bpm
	return playspeed

def add_vst_data(vstdata, pluginid, convproj_obj, state, params):
	from objects.inst_params import juce_plugin
	
	if 'plugin_format_name' in vstdata:
		vsttype = vstdata['plugin_format_name']
		juceobj = juce_plugin.juce_plugin()
		if 'descriptive_name' in vstdata: juceobj.name = vstdata['descriptive_name']
		if 'manufacturer_name' in vstdata: juceobj.manufacturer = vstdata['manufacturer_name']
		if 'file_or_identifier' in vstdata: juceobj.filename = vstdata['file_or_identifier']
		if vsttype == 'VST': juceobj.plugtype = 'vst2'
		if vsttype == 'VST3': juceobj.plugtype = 'vst3'
		juceobj.memoryblock = state
		plugin_obj, _ = juceobj.to_cvpj(convproj_obj, pluginid)
		if 'is_instrument' in vstdata: plugin_obj.role = 'synth' if vstdata['is_instrument'] else 'effect'

		if params:
			for param in params:
				paramnum = param['index']
				paramname = param['name'] if 'name' in param else None
				paramval = param['value']
				cvpj_paramid = 'ext_param_'+str(paramnum)
				plugin_obj.params.add_named(cvpj_paramid, paramval, 'float', paramname)

		return plugin_obj

def do_chan_strip(eq_defined, convproj_obj, trackid, channel_strip, fxslots_audio):

	if not (channel_strip.low_eq == channel_strip.mid_eq == channel_strip.high_eq == 0):
		fxplugid = trackid+'_fx_eq'
		fxplugin_obj = convproj_obj.plugin__add(fxplugid, 'universal', 'eq', '3band')
		fxplugin_obj.params.add('low_gain', channel_strip.low_eq, 'float')
		fxplugin_obj.params.add('mid_gain', channel_strip.mid_eq, 'float')
		fxplugin_obj.params.add('high_gain', channel_strip.high_eq, 'float')
		fxplugin_obj.params.add('lowmid_freq', 500, 'float')
		fxplugin_obj.params.add('midhigh_freq', 5000, 'float')
		fxslots_audio.append(fxplugid)
		if trackid not in eq_defined: eq_defined.append(trackid)

	if channel_strip.post_fader_effects != None:
		for fxnum, pfe in enumerate(channel_strip.post_fader_effects):
			if pfe != None:
				fxplugid = trackid+'_post_fader_effect_'+str(fxnum)
				fx_effect = pfe['effect']
				if fx_effect.startswith(':/effects/'):
					fxtype = fx_effect[10:]
					fxplugin_obj = convproj_obj.plugin__add(fxplugid, 'native', 'serato-fx', fxtype)
					fxplugin_obj.role = 'fx'
					if 'value' in pfe: fxplugin_obj.params.add('amount', pfe['value'], 'float')
					fxslots_audio.append(fxplugid)
				else:
					try:
						vstdata = json.loads(fx_effect)
						add_vst_data(vstdata, fxplugid, convproj_obj, pfe['state'] if 'state' in pfe else None, pfe['parameters'] if 'parameters' in pfe else None)
						fxslots_audio.append(fxplugid)
					except:
						pass


class input_serato(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'serato'
	
	def get_name(self):
		return 'Serato Studio'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'ms'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import serato as proj_serato
		from objects.convproj import sample_entry

		convproj_obj.type = 'ms'
		convproj_obj.fxtype = 'groupreturn'

		traits_obj = convproj_obj.traits
		traits_obj.audio_filetypes = ['wav']
		traits_obj.audio_stretch = ['rate']
		traits_obj.auto_types = ['pl_points']
		traits_obj.track_lanes = True

		convproj_obj.set_timings(960, True)

		useaudioclips = True

		project_obj = proj_serato.serato_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		sample_data = {}

		eq_track = {}
		eq_defined = []

		for num, scene_deck in enumerate(project_obj.scene_decks):
			cvpj_trackid = 'track_'+str(num+1)

			scene_strip = scene_deck.channel_strip

			cvpj_instid = cvpj_trackid+'_0'

			if scene_deck.type == 'drums':
				track_obj = convproj_obj.track__add(cvpj_trackid, 'instruments', 1, False)
				track_obj.visual.name = scene_deck.name
				base_trk_id = 'track_'+str(num+1)
				group_obj = convproj_obj.fx__group__add(base_trk_id)
				group_obj.visual.name = scene_deck.name
				group_obj.params.add('vol', scene_strip.gain*scene_strip.volume, 'float')
				group_obj.params.add('pan', scene_strip.pan, 'float')
				group_obj.params.add('enabled', scene_strip.mute!=1, 'bool')
				group_obj.datavals.add('pan_mode', 'stereo')
				do_chan_strip(eq_defined, convproj_obj, base_trk_id, scene_strip, group_obj.plugslots.slots_audio)
				eq_track[cvpj_trackid] = track_obj.plugslots.slots_audio
				for dnum, drumdata in enumerate(scene_deck.drums):
					cvpj_instid_p = base_trk_id+'_'+str(dnum)
					if drumdata.used:
						drumsamp = drumdata.sample

						samplefile = drumsamp.file

						channel_strip = drumdata.channel_strip

						if samplefile:
							inst_obj = convproj_obj.instrument__add(cvpj_instid_p)
							inst_obj.group = base_trk_id
							inst_obj.is_drum = True
							inst_obj.plugslots.set_synth(cvpj_instid_p)
							eq_track[cvpj_instid_p] = inst_obj.plugslots.slots_audio
							if channel_strip.gain: inst_obj.params.add('vol', channel_strip.gain*channel_strip.volume, 'float')
							inst_obj.params.add('pan', channel_strip.pan, 'float')
							inst_obj.params.add('enabled', scene_strip.mute!=1, 'bool')
							do_chan_strip(eq_defined, convproj_obj, cvpj_instid_p, channel_strip, inst_obj.plugslots.slots_audio)

							samplepath = parse_filepath(drumsamp.file)

							plugin_obj, sampleref_obj, samplepart_obj = convproj_obj.plugin__addspec__sampler(cvpj_instid_p, samplepath, 'win')

							inst_obj.visual.name = urllib.parse.unquote(samplefile).split('/')[-1]

							if drumsamp.color:
								inst_obj.visual.color.set_hex(drumsamp.color[3:])

							samplepart_obj.point_value_type = 'percent'
							dur_sec = sampleref_obj.get_dur_sec()
							if dur_sec is not None:
								samplepart_obj.start = drumsamp.start/dur_sec
								samplepart_obj.end = drumsamp.end/dur_sec
							else:
								samplepart_obj.start = 0
								samplepart_obj.end = 1
							samplepart_obj.stretch.preserve_pitch = True
							samplepart_obj.pitch = drumsamp.pitch_shift
							samplepart_obj.stretch.set_rate_speed(project_obj.bpm, drumsamp.playback_speed, False)
							samplepart_obj.trigger = 'oneshot'


			if scene_deck.type == 'plugin':
				track_obj = convproj_obj.track__add(cvpj_trackid, 'instruments', 1, False)
				track_obj.visual.name = scene_deck.name
				inst_obj = convproj_obj.instrument__add(cvpj_instid)
				inst_obj.visual.name = scene_deck.name
				inst_obj.visual.color.set_float([0.3,0.3,0.3])
				plugin_obj = add_vst_data(json.loads(scene_deck.plugin_description), cvpj_instid, convproj_obj, scene_deck.state, scene_deck.parameters)
				inst_obj.plugslots.set_synth(cvpj_instid)
				eq_track[cvpj_trackid] = group_obj.plugslots.slots_audio

				track_obj.params.add('vol', 0.7*scene_strip.gain*scene_strip.volume, 'float')
				track_obj.params.add('pan', scene_strip.pan, 'float')
				track_obj.datavals.add('pan_mode', 'stereo')
				track_obj.params.add('enabled', scene_strip.mute!=1, 'bool')
				do_chan_strip(eq_defined, convproj_obj, cvpj_trackid, scene_strip, track_obj.plugslots.slots_audio)

			if scene_deck.type == 'instrument':
				track_obj = convproj_obj.track__add(cvpj_trackid, 'instruments', 1, False)
				track_obj.visual.name = scene_deck.name
				inst_obj = convproj_obj.instrument__add(cvpj_instid)
				inst_obj.visual.name = scene_deck.name
				inst_obj.visual.color.set_float([0.48, 0.35, 0.84])
				plugin_obj, synthid = convproj_obj.plugin__add__genid('native', 'serato-inst', 'instrument')
				inst_obj.plugslots.set_synth(synthid)
				instrument_file = parse_filepath(scene_deck.instrument_file)
				convproj_obj.fileref__add(scene_deck.instrument_file, instrument_file, 'win')
				plugin_obj.state.filerefs['instrument'] = scene_deck.instrument_file
				adsr_obj = plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, scene_deck.release, 1)
				adsr_obj.release_tension = -1
				eq_track[cvpj_trackid] = group_obj.plugslots.slots_audio

				inst_obj.params.add('vol', 0.7*scene_strip.gain*scene_strip.volume, 'float')
				inst_obj.params.add('pan', scene_strip.pan, 'float')
				inst_obj.datavals.add('pan_mode', 'stereo')
				inst_obj.params.add('enabled', scene_strip.mute!=1, 'bool')
				do_chan_strip(eq_defined, convproj_obj, cvpj_trackid, scene_strip, inst_obj.plugslots.slots_audio)

			if scene_deck.type == 'sample':
				track_obj = convproj_obj.track__add(cvpj_trackid, 'audio' if scene_deck.type == 'sample' else 'instruments', 1, False)
				track_obj.visual.name = scene_deck.name

				if useaudioclips == False:
					inst_obj = convproj_obj.instrument__add(cvpj_instid)
					plugin_obj, synthid = convproj_obj.plugin__add__genid('native', 'serato-inst', 'sampler')
					inst_obj.plugslots.set_synth(synthid)

					if scene_deck.sample_file:
						inst_obj.visual.name = urllib.parse.unquote(scene_deck.sample_file).split('/')[-1]
						samplepath = parse_filepath(scene_deck.sample_file)
						convproj_obj.sampleref__add(samplepath, samplepath)
						samplepart_obj = plugin_obj.samplepart_add('sample')
						samplepart_obj.sampleref = samplepath
						samplepart_obj.stretch.set_rate_speed(project_obj.bpm, scene_deck.playback_speed, False)
	
					plugin_obj.datavals.add('type', scene_deck.type)
					plugin_obj.datavals.add('name', scene_deck.name)
					plugin_obj.datavals.add('original_key', scene_deck.original_key)
					plugin_obj.datavals.add('tempo_map', scene_deck.tempo_map)
					plugin_obj.datavals.add('original_bpm', scene_deck.original_bpm)
					plugin_obj.datavals.add('bpm', scene_deck.bpm)
					plugin_obj.datavals.add('bar_mode_enabled', scene_deck.bar_mode_enabled)
	
					colorlist = []
	
					for kn, sample_region in enumerate(scene_deck.cues):
						if sample_region: 
							plugin_obj.regions.add(kn, kn, sample_region)
							if 'color' in sample_region: colorlist.append(sample_region['color'])
	
					colorocc = dict([[colorlist.count(x),x] for x in set(colorlist)])
					maxnum = max(list(colorocc))
					if colorocc:
						coloro = colorocc[maxnum][3:]
						inst_obj.visual.color.set_hex(coloro)
				else:
					s_sample_entry = sample_data[num] = {}
					s_sample_entry['deck'] = scene_deck

					if scene_deck.sample_file:
						playspeed = calcspeed(scene_deck.playback_speed, project_obj.bpm, scene_deck.original_bpm, 1)

						samplepath = parse_filepath(scene_deck.sample_file)
						sampleref_obj = convproj_obj.sampleref__add(samplepath, samplepath, 'win')
						sampleref_obj.visual.name = urllib.parse.unquote(scene_deck.sample_file).split('/')[-1]
						samplepart_obj = sample_entry.cvpj_sample_entry()
						samplepart_obj.sampleref = samplepath
						samplepart_obj.pitch = scene_deck.key_shift
						samplepart_obj.stretch.set_rate_tempo(project_obj.bpm, playspeed, False)
						samplepart_obj.stretch.preserve_pitch = True

						s_sample_entry['part'] = samplepart_obj
						s_sample_entry['sampleref'] = sampleref_obj

				track_obj.params.add('vol', 0.7*scene_strip.gain*scene_strip.volume, 'float')
				track_obj.params.add('pan', scene_strip.pan, 'float')
				track_obj.datavals.add('pan_mode', 'stereo')
				track_obj.params.add('enabled', scene_strip.mute!=1, 'bool')
				do_chan_strip(eq_defined, convproj_obj, cvpj_trackid, scene_strip, track_obj.plugslots.slots_audio)


		for num, scene in enumerate(project_obj.scenes):
			sceneid = 'scene_'+str(num+1)
			scene_obj = convproj_obj.scene__add(sceneid)
			scene_obj.visual.name = scene.name
			scene_obj.visual.color.set_hex(project_obj.audio_deck_color_collection[num])

			for decknum, deck_sequence in enumerate(scene.deck_sequences):
				cvpj_trackid = 'track_'+str(decknum+1)

				scene_deck = project_obj.scene_decks[decknum]
				usechannel = 1 if scene_deck.type == 'drums' else 0

				has_eq = []

				if deck_sequence.automation_curves:
					for sauto in deck_sequence.automation_curves:
						if sauto.type == 'parameter':
							#if True:
							try:
								autoloc = ['track' if not usechannel else 'group', cvpj_trackid, None]

								param_id = sauto.parameter
								param_drum = -1
								param_is_fx = None
								param_fxparam = None
								toadd_eq = False

								trackid = cvpj_trackid
								valtype = 'float'
								if param_id.startswith('drum_'): 
									param_drum, param_id = param_id[5:].split('_', 1)
									param_drum = int(param_drum)
								if param_id.startswith('post_fader_effect_'): param_is_fx, param_id = param_id[18:].split('_', 1)
								if param_id.startswith('plugin_'): param_id = param_id[7:].split('_', 1)[0]

								if param_drum != -1: 
									autoloc[1] += '_'+str(param_drum)
									autoloc[0] = 'track'
									trackid += '_'+str(param_drum)

								if param_id == 'high_eq': 
									autoloc[0] = 'plugin'
									autoloc[1] += '_fx_eq'
									autoloc[2] = 'low_gain'
									has_eq.append(param_drum)
									toadd_eq = True

								if param_id == 'mid_eq': 
									autoloc[0] = 'plugin'
									autoloc[1] += '_fx_eq'
									autoloc[2] = 'mid_gain'
									toadd_eq = True
									has_eq.append(param_drum)

								if param_id == 'low_eq': 
									autoloc[0] = 'plugin'
									autoloc[1] += '_fx_eq'
									autoloc[2] = 'high_gain'
									toadd_eq = True
									has_eq.append(param_drum)

								if param_id == 'pan': autoloc[2] = 'pan'

								if param_is_fx: 
									autoloc[1] += '_post_fader_effect_'+param_is_fx
									if param_id == 'value':
										autoloc[0] = 'plugin'
										autoloc[2] = 'amount'
									elif param_id == 'on':
										valtype = 'bool'
										autoloc[0] = 'slot'
										autoloc[2] = 'wet'
									else:
										autoloc[0] = 'plugin'
										autoloc[2] = 'ext_param_'+param_id

								if toadd_eq and trackid not in eq_defined:
									plugslotsaudio = eq_track[trackid]
									fxplugid = trackid+'_fx_eq'
									fxplugin_obj = convproj_obj.plugin__add(fxplugid, 'universal', 'eq', '3band')
									fxplugin_obj.params.add('lowmid_freq', 500, 'float')
									fxplugin_obj.params.add('midhigh_freq', 5000, 'float')
									plugslotsaudio.append(fxplugid)
									eq_defined.append(trackid)

								autoseries = scene_obj.automation.create(autoloc, valtype, False)
								pl_points = autoseries.add_pl_points()

								autopoints_obj = pl_points.data
								for kf in sauto.keyframes:
									autopoints_obj.points__add_normal(kf.time, kf.value, kf.curvature*-2, None)

								pl_points.time.set_posdur(0, max(960*4, pl_points.data.get_dur()))

							except:
								pass

				if deck_sequence.notes:
					trscene_obj = convproj_obj.track__add_scene(cvpj_trackid, sceneid, 'main')

					if scene_deck.type == 'drums':
						placement_obj = trscene_obj.add_notes()
						scenedur = scene.length if scene.length else max([note.start+note.duration for note in deck_sequence.notes])
						placement_obj.time.set_posdur(0, scenedur)
						cvpj_notelist = placement_obj.notelist
						for note in deck_sequence.notes:
							valid = False
							if scene.length != None:
								if note.start < scene.length:
									valid = True
							else: valid = True
							if valid:
								key = note.number+note.channel
								if key >= 60: key -= 60
								cvpj_notelist.add_m('track_'+str(decknum+1)+'_'+str(key), note.start, note.duration, 0, note.velocity/100, None)
						cvpj_notelist.sort()

					if scene_deck.type in ['instrument', 'plugin']:
						placement_obj = trscene_obj.add_notes()
						scenedur = scene.length if scene.length else max([note.start+note.duration for note in deck_sequence.notes])
						placement_obj.time.set_posdur(0, scenedur)
						for note in deck_sequence.notes:
							if note.start < scenedur:
								key = note.number-60
								placement_obj.notelist.add_m('track_'+str(decknum+1)+'_0', note.start, note.duration, key+project_obj.transpose, note.velocity/100, None)

					if scene_deck.type == 'sample':
						scenedur = scene.length if scene.length else max([note.start+note.duration for note in deck_sequence.notes])
						if useaudioclips == False:
							placement_obj = trscene_obj.add_notes()
							placement_obj.time.set_posdur(0, scene.length)
							for note in deck_sequence.notes:
								if note.start < scenedur:
									key = note.number
									placement_obj.notelist.add_m('track_'+str(decknum+1)+'_0', note.start, note.duration, key, note.velocity/100, None)
						else:
							placement_obj = None
							s_sample_entry = sample_data[decknum]
							if 'part' in s_sample_entry:
								sampledeck = s_sample_entry['deck']
								samplepart = s_sample_entry['part']
								sampleref = s_sample_entry['sampleref']

								extendlast = not sampledeck.momentary

								samplenotes = {}

								for note in deck_sequence.notes:
									key = note.number
									cuedata = sampledeck.cues[key]

									c_start = cuedata['start'] if 'start' in cuedata else 0
									c_end = cuedata['end'] if 'end' in cuedata else 10
									color = cuedata['color'][3:] if 'color' in cuedata else None
									reverse = cuedata['reverse'] if 'reverse' in cuedata else False 
									if reverse: 
										dur_sec = sampleref_obj.get_dur_sec()
										if dur_sec:
											c_start = dur_sec-c_start
											c_end = dur_sec-c_end

									startoffset = calcpos_stretch(c_start, scene_deck.original_bpm, project_obj.bpm, sampledeck.playback_speed, True)
									endoffset = calcpos_stretch(c_end, scene_deck.original_bpm, project_obj.bpm, sampledeck.playback_speed, False)

									samplenotes[note.start] = [note.duration, startoffset*960, endoffset*960, color, cuedata, note.velocity/100]

								samplenotes = dict(sorted(samplenotes.items()))
								if extendlast and samplenotes:
									poslist = list(samplenotes)
									for n in range(len(poslist)-1):
										curpos = poslist[n+1]
										prevpos = poslist[n]
										curnote = samplenotes[poslist[n]][0] = curpos-prevpos
									lastpos = poslist[-1]
									samplenotes[lastpos][0] = scene.length-lastpos

								for nstart, ndata in samplenotes.items():
									nend, startoffset, endoffset, color, cuedata, vol = ndata
	
									if endoffset-startoffset:

										if scene.length != None:
											duration = min(nend, endoffset-startoffset, scene.length-nstart)
											cond_scene = min(endoffset-startoffset, duration) > 3
										else:
											duration = min(nend, endoffset-startoffset)
											cond_scene = True

										if cond_scene:
											playback_speed = cuedata['playback_speed'] if 'playback_speed' in cuedata else 1

											placement_obj = trscene_obj.add_audio()
											samplepart_copy = placement_obj.sample = copy.deepcopy(samplepart)
											placement_obj.time.set_posdur(nstart, duration)
											placement_obj.time.set_offset(startoffset/playback_speed)
											placement_obj.visual.color.set_hex(color)

											if 'channel_strip' in cuedata:
												cuestrip = cuedata['channel_strip']
												if 'gain' in cuestrip: samplepart_copy.vol += cuestrip['gain']
												if 'volume' in cuestrip: samplepart_copy.vol += cuestrip['volume']
												if 'pan' in cuestrip: samplepart_copy.pan = cuestrip['pan']

											samplepart_copy.vol *= vol

											playspeed = calcspeed(scene_deck.playback_speed, project_obj.bpm, scene_deck.original_bpm, playback_speed)
											samplepart_copy.stretch.set_rate_tempo(project_obj.bpm, playspeed, False)

											samplepart_copy.pitch += project_obj.transpose
											if 'pitch_shift' in cuedata: samplepart_copy.pitch += cuedata['pitch_shift']
											if 'reverse' in cuedata: samplepart_copy.reverse = cuedata['reverse']

		convproj_obj.transport.loop_active = project_obj.arrangement.loop_active
		convproj_obj.transport.loop_start = project_obj.arrangement.loop_start
		convproj_obj.transport.loop_end = project_obj.arrangement.loop_end
		
		for arrangement in project_obj.arrangement.tracks:
			if arrangement.type == 'scene':
				for clip in arrangement.clips:
					scenepl_obj = convproj_obj.scene__add_pl()
					scenepl_obj.position = clip.start
					scenepl_obj.duration = clip.length
					scenepl_obj.id = 'scene_'+str(clip.scene_slot_number+1)
				break
			if arrangement.type == 'master':
				master_strip = arrangement.channel_strip
				master_obj = convproj_obj.track_master
				if arrangement.name: master_obj.visual.name = arrangement.name
				master_obj.params.add('vol', 0.7*master_strip.gain*master_strip.volume, 'float')
				master_obj.params.add('pan', master_strip.pan, 'float')
				master_obj.datavals.add('pan_mode', 'stereo')
				do_chan_strip(eq_defined, convproj_obj, 'master', master_strip, master_obj.plugslots.slots_audio)

		if 'name' in project_obj.metadata: convproj_obj.metadata.name = project_obj.metadata['name']
		if 'artist' in project_obj.metadata: convproj_obj.metadata.author = project_obj.metadata['artist']
		if 'genre' in project_obj.metadata: convproj_obj.metadata.genre = project_obj.metadata['genre']
		if 'label' in project_obj.metadata: convproj_obj.metadata.comment_text = project_obj.metadata['label']

		#for trackid, track_obj in convproj_obj.track__iter():
		#	print(track_obj.plugslots.slots_audio)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('markers_from_scene')
		convproj_obj.params.add('bpm', project_obj.bpm, 'float')