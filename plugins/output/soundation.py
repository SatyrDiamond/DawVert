# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import os
import struct
import math
import zipfile
import io
import uuid
from functions import xtramath
from functions import colors
from functions import data_values
from objects import globalstore
from objects.file_proj import proj_soundation
from functions_plugin import soundation_values

def autopoints_get(autoloc, add, mul):
	sngauto = []
	if_found, autopoints = convproj_obj.automation.get_autopoints(autoloc)
	if if_found:
		for autopoint in autopoints.iter():
			sngauto.append({"pos": autopoint.pos, "value": (autopoint.value/mul)-add})
	return sngauto

def add_fx(convproj_obj, soundation_channel, fxchain_audio):
	for pluginid in fxchain_audio:
		plugin_found, plugin_obj = convproj_obj.get_plugin(pluginid)
		if plugin_found: 
			if plugin_obj.check_wildmatch('native-soundation', None):
				fx_on, fx_wet = plugin_obj.fxdata_get()

				soundation_effect = proj_soundation.soundation_device(None)
				soundation_effect.identifier = plugin_obj.type.subtype
				soundation_effect.bypass = not fx_on
				for param_id, dset_param in globalstore.dataset.get_params('lmms', 'plugin', plugin_obj.type.subtype):
					param_cvpj2sng(param_id, soundation_effect, plugin_obj, pluginid)
				soundation_channel.effects.append(soundation_effect)

def set_asdr(soundation_device, plugin_obj):
	adsr_obj = plugin_obj.env_asdr_get('vol')
	soundation_device.params.add('sustain', adsr_obj.sustain, [])
	soundation_device.params.add('release', adsr_obj.release, [])
	soundation_device.params.add('decay', adsr_obj.decay, [])
	soundation_device.params.add('attack', adsr_obj.attack, [])

def param_cvpj2sng(name, soundation_device, plugin_obj, pluginid):
	global convproj_obj
	cvpj_param = plugin_obj.params.get(name, 0).value
	soundation_device.params.add(name, cvpj_param, [])

def dataval_cvpj2sng(name, soundation_device, plugin_obj, useval):
	dataval = plugin_obj.datavals.get(name, '')
	soundation_device.data[name] = dataval if not useval else {'value': dataval}

def addsample(zip_sngz, filepath, alredyexists): 
	global audio_id
	datauuid = str(uuid.uuid4())

	if filepath not in audio_id:
		if os.path.exists(filepath):
			filename, filetype = os.path.basename(filepath).split('.')
			zipfilename = datauuid+'.'+filetype
			if zipfilename not in zip_sngz.namelist(): zip_sngz.write(filepath, zipfilename)
			audio_id[filepath] = zipfilename
		else:
			audio_id[filepath] = None
	zipfilename = audio_id[filepath]

	return zipfilename

class output_soundation(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'output'
	def getname(self): return 'Soundation'
	def getshortname(self): return 'soundation'
	def gettype(self): return 'r'
	def plugin_archs(self): return None
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Soundation'
		dawinfo_obj.file_ext = 'sngz'
		dawinfo_obj.placement_cut = True
		dawinfo_obj.placement_loop = []
		dawinfo_obj.fxtype = 'track'
		dawinfo_obj.plugin_included = ['sampler:single','synth-nonfree:europa','native-soundation','midi']
		dawinfo_obj.auto_types = ['nopl_points']

	def parse(self, i_convproj_obj, output_file):
		global convproj_obj
		global audio_id

		audio_id = {}
		convproj_obj = i_convproj_obj

		globalstore.dataset.load('soundation', './data_main/dataset/soundation.dset')
		globalstore.dataset.load('synth_nonfree', './data_main/dataset/synth_nonfree.dset')

		globalstore.idvals.load('gm_inst', './data_main/dataset/soundation_gm_inst.csv')
		idvals_inst_gm2 = globalstore.idvals.get('gm_inst')

		zip_bio = io.BytesIO()
		zip_sngz = zipfile.ZipFile(zip_bio, mode='w', compresslevel=None)

		soundation_obj = proj_soundation.soundation_project(None)

		bpm = int(convproj_obj.params.get('bpm', 120).value)
		bpm, notelen = xtramath.get_lower_tempo(bpm, 1, 240)

		soundation_obj.bpm = int(bpm)
		timing = 22050*(120/soundation_obj.bpm)

		convproj_obj.change_timings(timing*notelen, False)

		soundation_obj.version = 2.3
		soundation_obj.studio = "3.10.7"
		beatNumerator, beatDenominator = convproj_obj.timesig
		soundation_obj.timeSignature = str(beatNumerator)+'/'+str(beatDenominator)

		soundation_obj.looping = convproj_obj.loop_active
		soundation_obj.loopStart = convproj_obj.loop_start
		soundation_obj.loopEnd = convproj_obj.loop_end

		bpmdiv = 120/bpm

		soundation_channel = proj_soundation.soundation_channel(None)
		soundation_channel.userSetName = convproj_obj.track_master.visual.name if convproj_obj.track_master.visual.name else "Master Channel"
		soundation_channel.volume = convproj_obj.track_master.params.get('vol', 1).value
		soundation_channel.name = "Master Channel"
		soundation_channel.type = "master"
		soundation_channel.volumeAutomation = autopoints_get(['master','vol'], 0, 1)
		soundation_channel.panAutomation = autopoints_get(['master','pan'], -1, 2)

		add_fx(convproj_obj, soundation_channel, convproj_obj.track_master.fxslots_audio)
		soundation_obj.channels.append(soundation_channel)

		#auto_volpan(convproj_obj, sng_master, ['master'])
		ts_numerator, ts_denominator = convproj_obj.timesig
		soundation_obj.timeSignature = str(ts_numerator)+'/'+str(ts_denominator)

		sng_channels = []

		for trackid, track_obj in convproj_obj.iter_track():
			soundation_channel = proj_soundation.soundation_channel(None)

			if track_obj.type == 'instrument': soundation_channel.type = 'instrument'
			if track_obj.type == 'fx': soundation_channel.type = 'effect'
			if track_obj.type == 'audio': soundation_channel.type = 'audio'

			trackcolor = track_obj.visual.color.get_hex_fb(128,128,128)
			if track_obj.visual.name: soundation_channel.userSetName = track_obj.visual.name
			soundation_channel.color = '#'+trackcolor.upper()
			soundation_channel.volume = track_obj.params.get('vol', 1).value
			soundation_channel.pan = 0.5 + track_obj.params.get('pan', 0).value/2
			soundation_channel.mute = not track_obj.params.get('enabled', True).value

			add_fx(convproj_obj, soundation_channel, track_obj.fxslots_audio)
			soundation_channel.volumeAutomation = autopoints_get(['track',trackid,'vol'], 0, 1)
			soundation_channel.panAutomation = autopoints_get(['track',trackid,'pan'], -1, 2)

			if track_obj.type == 'instrument':
				pluginid = track_obj.inst_pluginid
				soundation_instrument = proj_soundation.soundation_device(None)
				soundation_instrument.rackName = ''
				soundation_instrument.identifier = ''
				inst_supported = False
				plugin_found, plugin_obj = convproj_obj.get_plugin(pluginid)
				if plugin_found:
					if plugin_obj.check_match('sampler', 'single'):
						inst_supported = True
						soundation_instrument.identifier = 'com.soundation.simple-sampler'

						middlenote = track_obj.datavals.get('middlenote', 0)
						pitch = track_obj.params.get('pitch', 0).value

						negpitch = -1 if pitch<0 else 1
						transpose = round(pitch)
						detune = pitch-transpose

						transpose = xtramath.between_to_one(-48, 48, transpose)
						detune = xtramath.between_to_one(-1, 1, detune*negpitch)

						set_asdr(soundation_instrument, plugin_obj)
						soundation_instrument.params.add('playback_mode', 2, [])
						soundation_instrument.params.add('gain', 0.25, [])
						soundation_instrument.params.add('end', 1, [])
						soundation_instrument.params.add('crossfade', 0, [])
						soundation_instrument.params.add('coarse', transpose, [])
						soundation_instrument.params.add('fine', detune, [])
						soundation_instrument.params.add('root_note', middlenote+72, [])
						soundation_instrument.params.add('playback_direction', 0, [])
						soundation_instrument.params.add('interpolation_mode', 2, [])
						soundation_instrument.params.add('release_mode', 1, [])
						soundation_instrument.params.add('portamento_time', 0.1, [])

						sp_obj = plugin_obj.samplepart_get('sample')
						_, sampleref_obj = convproj_obj.get_sampleref(sp_obj.sampleref)
						sp_obj.convpoints_percent(sampleref_obj)

						filename = sp_obj.get_filepath(convproj_obj, None)
						zipfilename = addsample(zip_sngz, filename, False)

						if zipfilename == None:
							soundation_instrument.data['sample'] = None
						else:
							soundation_instrument.data['sample'] = {"url": zipfilename, "name": ""}

						soundation_instrument.params.add('start', sp_obj.start, [])
						soundation_instrument.params.add('loop_start', sp_obj.loop_start, [])
						soundation_instrument.params.add('loop_end', sp_obj.loop_end, [])
							 
						if sp_obj.loop_active:
							soundation_instrument.params.add('loop_mode', 1, [])
						else:
							soundation_instrument.params.add('loop_mode', 0, [])

					if plugin_obj.check_match('synth-nonfree', 'europa'):
						inst_supported = True
						soundation_instrument.identifier = 'com.soundation.europa'
						europaparamlist = dataset_synth_nonfree.params_list('plugin', 'europa')
						for param_id, dset_param in globalstore.dataset.get_params('synth_nonfree', 'plugin', 'europa'):
							if not dset_param.noauto: 
								eur_value_value = plugin_obj.params.get(param_id, 0).value
							else:
								eur_value_value = plugin_obj.datavals.get(param_id, 0)
								if paramname in ['Curve1','Curve2','Curve3','Curve4','Curve']: eur_value_value = ','.join([str(x).zfill(2) for x in eur_value_value])
							soundation_instrument.params.add("/custom_properties/"+dset_param.name, eur_value_value, [])
						soundation_instrument.params.add("/soundation/sample/", None, [])

					if plugin_obj.check_wildmatch('native-soundation', None):
						inst_supported = True
						soundation_instrument.identifier = plugin_obj.type.subtype

						if plugin_obj.type.subtype == 'com.soundation.supersaw':
							set_asdr(soundation_instrument, plugin_obj)
							for snd_param in ["detune", "spread"]:
								param_cvpj2sng(snd_param, soundation_instrument, plugin_obj, pluginid)

						if plugin_obj.type.subtype == 'com.soundation.simple':
							for oscnum in range(4):
								for paramtype in ['detune','pitch','type','vol']:
									param_cvpj2sng('osc_'+str(oscnum)+'_'+paramtype, soundation_instrument, plugin_obj, pluginid)
							filt_adsr_obj = plugin_obj.env_asdr_get('cutoff')

							soundation_instrument.params.add('filter_attack', filt_adsr_obj.attack, [])
							soundation_instrument.params.add('filter_decay', filt_adsr_obj.sustain, [])
							soundation_instrument.params.add('filter_sustain', filt_adsr_obj.decay, [])
							soundation_instrument.params.add('filter_release', filt_adsr_obj.release, [])
							soundation_instrument.params.add('filter_int', filt_adsr_obj.amount, [])
							soundation_instrument.params.add('filter_cutoff', xtramath.between_to_one(20, 7500, plugin_obj.filter.freq), [])
							soundation_instrument.params.add('filter_resonance', plugin_obj.filter.q, [])
							for snd_param in ['noise_vol', 'noise_color']:
								param_cvpj2sng(snd_param, soundation_instrument, plugin_obj, pluginid)

						if plugin_obj.type.subtype == 'com.soundation.GM-2':
							dataval_cvpj2sng('sample_pack', soundation_instrument, plugin_obj, True)
							set_asdr(soundation_instrument, plugin_obj)

						if plugin_obj.type.subtype == 'com.soundation.noiser':
							set_asdr(soundation_instrument, plugin_obj)

						if plugin_obj.type.subtype == 'com.soundation.SAM-1':
							sample_pack = plugin_obj.datavals.get('sample_pack', None)
							soundation_instrument.data['sample_pack'] = sample_pack
							set_asdr(soundation_instrument, plugin_obj)

						if plugin_obj.type.subtype == 'com.soundation.drummachine':
							for paramname in ["gain_2", "hold_1", "pitch_6", "gain_1", "decay_5", "gain_5", "hold_0", "hold_2", "pitch_7", "gain_0", "decay_6", "gain_3", "hold_5", "pitch_3", "decay_4", "pitch_4", "gain_6", "decay_7", "pitch_2", "hold_6", "decay_1", "decay_3", "decay_0", "decay_2", "gain_7", "pitch_0", "pitch_5", "hold_3", "pitch_1", "hold_4", "hold_7", "gain_4"]:
								param_cvpj2sng(paramname, soundation_instrument, plugin_obj, pluginid)
							dataval_cvpj2sng('kit_name', soundation_instrument, plugin_obj, True)

						if plugin_obj.type.subtype == 'com.soundation.spc':
							for paramname in soundation_values.spc_vals():
								param_cvpj2sng(paramname, soundation_instrument, plugin_obj, pluginid)
							for dataname in ['cuts','envelopes']:
								dataval_cvpj2sng(dataname, soundation_instrument, plugin_obj, False)

						if plugin_obj.type.subtype in ['com.soundation.va_synth','com.soundation.fm_synth','com.soundation.the_wub_machine','com.soundation.mono']:
							if plugin_obj.type.subtype == 'com.soundation.va_synth': snd_params = ["aatt", "adec", "arel", "asus", "fatt", "fdec", "fdyn", "feg", "ffreq", "frel", "fres", "fsus", "glide_bend", "glide_mode", "glide_rate", "lfolpf", "lfoosc", "lforate", "octave", "osc_2_fine", "osc_2_mix", "osc_2_noise", "osc_2_octave", "tune"]
							elif plugin_obj.type.subtype == 'com.soundation.fm_synth': snd_params = ['p'+str(x) for x in range(137)]
							elif plugin_obj.type.subtype == 'com.soundation.mono': snd_params = ['filter_int','cutoff','resonance','pw','filter_decay','mix','amp_decay','glide']
							elif plugin_obj.type.subtype == 'com.soundation.the_wub_machine': snd_params = ['filter_cutoff','filter_drive','filter_resonance','filter_type','filth_active','filth_amount','lfo_depth','lfo_keytracking','lfo_loop','lfo_phase','lfo_retrigger','lfo_speed','lfo_type','msl_amount','osc1_gain','osc1_glide','osc1_pan','osc1_pitch','osc1_shape','osc1_type','osc2_gain','osc2_glide','osc2_pan','osc2_pitch','osc2_shape','osc2_type','osc_sub_bypass_filter','osc_sub_gain','osc_sub_glide','osc_sub_shape','osc_sub_volume_lfo','reese_active','unison_active','unison_amount','unison_count']
							for snd_param in snd_params:
								param_cvpj2sng(snd_param, soundation_instrument, plugin_obj, pluginid)

				if not inst_supported:
					soundation_instrument.identifier = 'com.soundation.GM-2'
					gm2_samplepack = '2_0_Bright_Yamaha_Grand.smplpck'

					if plugin_found:
						if len(plugin_obj.oscs) == 1:
							s_osc = plugin_obj.oscs[0]
							if s_osc.prop.shape == 'sine': gm2_samplepack = '81_8_Sine_Wave.smplpck'
							if s_osc.prop.shape == 'square': gm2_samplepack = '81_0_Square_Lead.smplpck'
							if s_osc.prop.shape == 'triangle': gm2_samplepack = '85_0_Charang.smplpck'
							if s_osc.prop.shape == 'saw': gm2_samplepack = '82_0_Saw_Wave.smplpck'
							set_asdr(soundation_instrument, plugin_obj)
						else:
							midi_found, midi_inst = track_obj.get_midi(convproj_obj)
							bank, patch = midi_inst.to_sf2()
							if idvals_inst_gm2: 
								gm2_samplepack = idvals_inst_gm2.get_idval(str(patch+1)+'_'+str(bank), 'url')
							set_asdr(soundation_instrument, plugin_obj)
					else:
						soundation_instrument.params.add('sustain', 1, [])
						soundation_instrument.params.add('release', 0, [])
						soundation_instrument.params.add('decay', 0, [])
						soundation_instrument.params.add('attack', 0, [])

					soundation_instrument.data['sample_pack'] = {'value': gm2_samplepack}

				soundation_channel.instrument = soundation_instrument

				for notespl_obj in track_obj.placements.pl_notes:
					soundation_region = proj_soundation.soundation_region(None)

					if notespl_obj.visual.color: soundation_region.color =  '#'+notespl_obj.visual.color.get_hex_fb(128,128,128)

					soundation_region.position = int(notespl_obj.position)
					soundation_region.length = int(notespl_obj.duration)
					soundation_region.loopcount = 1
					soundation_region.contentPosition = 0

					if notespl_obj.cut_type in ['loop']:
						soundation_region.length = notespl_obj.cut_loopend
						soundation_region.loopcount = notespl_obj.duration/notespl_obj.cut_loopend

					if notespl_obj.cut_type == 'cut': 
						soundation_region.contentPosition = -(notespl_obj.cut_start)

					soundation_region.type = 2

					soundation_region.notes = []
					soundation_region.isPattern = False

					notespl_obj.notelist.sort()

					for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
						for t_key in t_keys:
							if 0 <= t_key+60 <= 128:
								sng_note = {}
								sng_note["note"] = int(t_key+60)
								sng_note["velocity"] = float(t_vol)
								sng_note["position"] = int(t_pos)
								sng_note["length"] = int(t_dur)
								soundation_region.notes.append(sng_note)

					soundation_channel.regions.append(soundation_region)

			if track_obj.type == 'audio':
				for audiopl_obj in track_obj.placements.pl_audio:
					soundation_region = proj_soundation.soundation_region(None)

					if audiopl_obj.visual.color: soundation_region.color = '#'+audiopl_obj.visual.color.get_hex_fb(128,128,128)
					soundation_region.position = int(audiopl_obj.position)
					soundation_region.length = int(audiopl_obj.duration)
					soundation_region.loopcount = 1
					soundation_region.contentPosition = 0

					if audiopl_obj.cut_type in ['loop', 'loop_off']:
						soundation_region.length = audiopl_obj.cut_loopend
						soundation_region.loopcount = audiopl_obj.duration/audiopl_obj.cut_loopend

					if audiopl_obj.cut_type == 'cut': 
						soundation_region.contentPosition = -(audiopl_obj.cut_start)

					soundation_region.type = 1

					audiofilename = ''
					ref_found, sampleref_obj = convproj_obj.get_sampleref(audiopl_obj.sample.sampleref)
					if ref_found: audiofilename = sampleref_obj.fileref.get_path(None, True)

					zipfilename = addsample(zip_sngz, audiofilename, False)

					soundation_region.file = {"url": zipfilename, "name": ""}
					soundation_region.reversed = audiopl_obj.sample.reverse

					soundation_region.stretchRate = audiopl_obj.sample.stretch.calc_real_speed
					soundation_region.stretchMode = 3 if audiopl_obj.sample.stretch.preserve_pitch else 2

					if audiopl_obj.sample.stretch.uses_tempo == False:
						soundation_region.stretchRate = audiopl_obj.sample.stretch.calc_real_speed
						soundation_region.isAutoStretched = False
					else:
						soundation_region.autoStretchBpm = bpm
						soundation_region.isAutoStretched = True

					soundation_channel.regions.append(soundation_region)

			sng_channels.append(soundation_channel)

		soundation_obj.looping = convproj_obj.loop_active
		soundation_obj.loopStart = int(convproj_obj.loop_start)
		soundation_obj.loopEnd = int(convproj_obj.loop_end)

		#iseffectexists = 'fx' in [convproj_obj.track_data[x].type for x in convproj_obj.track_order]
#
		#if iseffectexists:
#
		#	for trackid, sends_obj in convproj_obj.trackroute.items():
		#		tracksendnum = convproj_obj.track_order.index(trackid)
	#
		#		isallfx = True
		#		for target, send_obj in sends_obj.iter():
		#			amount = send_obj.params.get('amount', 1).value
		#			pan = send_obj.params.get('pan', 0).value
		#			trackrecnum = convproj_obj.track_order.index(target)
		#			soundation_effect = proj_soundation.soundation_device(None)
		#			soundation_effect.identifier = 'com.soundation.send'
		#			soundation_effect.params.add('send', amount, [])
		#			soundation_effect.params.add('pan', (pan/2+0.5), [])
		#			soundation_effect.params.add('output', 1, [])
		#			soundation_effect.data['channelIndex'] = trackrecnum
		#			sng_channels[tracksendnum].effects.append(soundation_effect)
#
		#		if not sends_obj.to_master_active:
		#			soundation_effect = proj_soundation.soundation_device(None)
		#			soundation_effect.identifier = 'com.soundation.send'
		#			soundation_effect.params.add('send', 1, [])
		#			soundation_effect.params.add('pan', 0.5, [])
		#			soundation_effect.params.add('output', int(sends_obj.to_master_active), [])
		#			sng_channels[tracksendnum].effects.append(soundation_effect)

		for x in sng_channels: soundation_obj.channels.append(x)

		jsonwrite = soundation_obj.write()

		zip_sngz.writestr('song.sng', json.dumps(jsonwrite))
		zip_sngz.close()
		open(output_file, 'wb').write(zip_bio.getbuffer())

		with open('soundation_debug', "w") as fileout: json.dump(jsonwrite, fileout, indent=4)