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
from functions import data_values
from objects import globalstore

def europa_vals():
	return ["Curve1","Curve2","Curve3","Curve4","Curve","Amp Attack","Amp Decay","Amp Sustain","Amp Release","Reverb Damp","Reverb Size","Reverb Decay","Reverb Amount","Effect On","LFO 1 Rate","Mod1 Dest1 Amt","Mod1 Dest2 Amt","Mod1 Dest1","Mod1 Dest2","Mod1 Scale Amt","Mod1 Scale","Mod1 Source","Routing X","Routing Y","Routing Selected","Mod2 Dest1 Amt","Mod2 Dest2 Amt","Mod2 Dest1","Mod2 Dest2","Mod2 Scale Amt","Mod2 Scale","Mod2 Source","Mod3 Dest1 Amt","Mod3 Dest2 Amt","Mod3 Dest1","Mod3 Dest2","Mod3 Scale Amt","Mod3 Scale","Mod3 Source","Mod4 Dest1 Amt","Mod4 Dest2 Amt","Mod4 Dest1","Mod4 Dest2","Mod4 Scale Amt","Mod4 Scale","Mod4 Source","Mod5 Dest1 Amt","Mod5 Dest2 Amt","Mod5 Dest1","Mod5 Dest2","Mod5 Scale Amt","Mod5 Scale","Mod5 Source","Mod6 Dest1 Amt","Mod6 Dest2 Amt","Mod6 Dest1","Mod6 Dest2","Mod6 Scale Amt","Mod6 Scale","Mod6 Source","Mod7 Dest1 Amt","Mod7 Dest2 Amt","Mod7 Dest1","Mod7 Dest2","Mod7 Scale Amt","Mod7 Scale","Mod7 Source","Mod8 Dest1 Amt","Mod8 Dest2 Amt","Mod8 Dest1","Mod8 Dest2","Mod8 Scale Amt","Mod8 Scale","Mod8 Source","LFO 1 Delay","pitch_wheel","mod_wheel","PitchBend CV Amount","ModWheel CV Amount","Osc1 Semi","Osc1 Oct","Osc1 Tune","Osc1 Pitch Kbd","Portamento","Key Mode","Portamento Mode","Pitchbend Range","Env Select","Env 1 Rate","Env 2 Rate","Env 3 Rate","Env 4 Rate","Env 1 Syncrate","Env 2 Syncrate","Env 3 Syncrate","Env 4 Syncrate","Mouse Down","Env Preset","Env Edit Mode","Effect Select","Effect Order","Reverb On","Delay On","Dist On","Comp On","Phaser On","Eq On","LFO 1 SyncRate","LFO 1 KeySync","LFO 1 Global","LFO 1 TempoSync","LFO 1 Wave","LFO 2 Rate","LFO 2 Delay","LFO 2 SyncRate","LFO 2 KeySync","LFO 2 Global","LFO 2 TempoSync","LFO 2 Wave","LFO 3 Rate","LFO 3 Delay","LFO 3 SyncRate","LFO 3 KeySync","LFO 3 Global","LFO 3 TempoSync","LFO 3 Wave","LFO Select","Amp Gain","Amp Velocity","Pan","Filter Freq","Filter Reso","Filter Type","Filter Kbd","Filter Mod","Filter Vel","Osc1 Level","Dist Drive","Dist Type","Dist Tone","Mod Effect Amount","Mod Effect Rate","Mod Effect Depth","Mod Effect Spread","Delay Amount","Delay FB","Delay Sync","Delay PingPong","Delay Time","Delay Synced Time","EQ Gain","EQ Q","EQ Freq","Comp Release","Comp Attack","Comp Threshold","Comp Ratio","Mod Effect Type","Delay Pan","Dist Amount","Voices","Osc1 Shape","Osc1 Wave","Master Volume","Osc1 Mod1","Osc1 Mod1 Amt","Osc1 Filter","Osc1 Filter Freq","Osc1 Filter Reso","Osc1 Pan","Osc1 Filter Kbd","Osc1 Count","Osc1 Detune","Osc1 Blend","Osc1 Spread","Osc1 Unison Mode","Osc1 Harm","Osc1 Harm Pos","Osc1 Mod2","Osc1 Mod2 Amt","Filter Drive","Osc1 Unison On","Osc1 Filter On","Osc1 Harm On","Osc1 Mod1 On","Osc1 Mod2 On","Osc1 To Filter","Osc1 Harm Amt","Osc1 SyncPhase","Osc1 Shape Source","Osc1 Shape Amt","Osc1 Shape Vel","Osc1 Filter Source","Osc1 Filter Mod","Osc1 Filter Vel","Osc1 Mod1 Source","Osc1 Mod1 Mod","Osc1 Mod2 Source","Osc1 Mod2 Mod","Filter Mod Source","Osc1 On","OscSel","Osc2 Semi","Osc2 Oct","Osc2 Tune","Osc2 Pitch Kbd","Osc2 Shape","Osc2 Wave","Osc2 Mod1","Osc2 Mod1 Amt","Osc2 Filter","Osc2 Filter Freq","Osc2 Filter Reso","Osc2 Pan","Osc2 Filter Kbd","Osc2 Count","Osc2 Detune","Osc2 Blend","Osc2 Spread","Osc2 Unison Mode","Osc2 Harm","Osc2 Harm Pos","Osc2 Mod2","Osc2 Mod2 Amt","Osc2 Unison On","Osc2 Filter On","Osc2 Harm On","Osc2 Mod1 On","Osc2 Mod2 On","Osc2 To Filter","Osc2 Harm Amt","Osc2 SyncPhase","Osc2 Shape Source","Osc2 Shape Amt","Osc2 Shape Vel","Osc2 Filter Source","Osc2 Filter Mod","Osc2 Filter Vel","Osc2 Mod1 Source","Osc2 Mod1 Mod","Osc2 Mod2 Source","Osc2 Mod2 Mod","Osc2 On","Osc3 Semi","Osc3 Oct","Osc3 Tune","Osc3 Pitch Kbd","Osc3 Level","Osc3 Shape","Osc3 Wave","Osc3 Mod1","Osc3 Mod1 Amt","Osc3 Filter","Osc3 Filter Freq","Osc3 Filter Reso","Osc3 Pan","Osc3 Filter Kbd","Osc3 Count","Osc3 Detune","Osc3 Blend","Osc3 Spread","Osc3 Unison Mode","Osc3 Harm","Osc3 Harm Pos","Osc3 Mod2","Osc3 Mod2 Amt","Osc3 Unison On","Osc3 Filter On","Osc3 Harm On","Osc3 Mod1 On","Osc3 Mod2 On","Osc3 To Filter","Osc3 Harm Amt","Osc3 SyncPhase","Osc3 Shape Source","Osc3 Shape Amt","Osc3 Shape Vel","Osc3 Filter Source","Osc3 Filter Mod","Osc3 Filter Vel","Osc3 Mod1 Source","Osc3 Mod1 Mod","Osc3 Mod2 Source","Osc3 Mod2 Mod","Osc3 On","Osc2 Level","Osc WCurve","Osc FCurve","Osc Unison","Env Pos","Click Timer","Filter Dist","Always Render","NoteOn","builtin_onoffbypass"]

def spc_vals():
	return ["pitch_2","gain_8","gain_4","pan_0","pan_14","gain_7","pan_12","pan_15","pan_10","pitch_1","pan_9","punch","pan_4","pan_13","gain_3","bite","pan_8","pan_11","msl","gain_15","pan_5","pitch_0","pitch_6","pan_7","pitch_14","gain_2","pitch_13","pitch_10","pitch_12","pan_3","pitch_5","pitch_8","pitch_11","pitch_9","pitch_15","pitch_4","gain_1","pan_2","pitch_3","pan_6","gain_0","gain_13","pitch_7","gain_14","gain_11","gain_10","gain_12","pan_1","gain_5","gain_9","gain_6"]

def autopoints_get(autoloc, add, mul):
	sngauto = []
	if_found, autopoints = convproj_obj.automation.get_autopoints(autoloc)
	if if_found:
		for autopoint in autopoints:
			sngauto.append({"pos": autopoint.pos, "value": (autopoint.value/mul)-add})
	return sngauto

def add_fx(convproj_obj, soundation_channel, fxchain_audio):
	from objects.file_proj import proj_soundation
	for pluginid in fxchain_audio:
		plugin_found, plugin_obj = convproj_obj.plugin__get(pluginid)
		if plugin_found: 
			if plugin_obj.check_wildmatch('native', 'soundation', None):
				fx_on, fx_wet = plugin_obj.fxdata_get()

				soundation_effect = proj_soundation.soundation_device(None)
				soundation_effect.identifier = plugin_obj.type.subtype
				soundation_effect.bypass = not fx_on
				for param_id, dset_param in globalstore.dataset.get_params('soundation', 'plugin', plugin_obj.type.subtype):
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
	def get_name(self): return 'Soundation'
	def get_shortname(self): return 'soundation'
	def gettype(self): return 'r'
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'sngz'
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = []
		in_dict['fxtype'] = 'route'
		in_dict['plugin_included'] = ['universal:sampler:single','user:reasonstudios:europa','native:soundation','universal:midi']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['placement_loop'] = ['loop']
		in_dict['projtype'] = 'r'

	def parse(self, i_convproj_obj, output_file):
		from objects.file_proj import proj_soundation

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

		add_fx(convproj_obj, soundation_channel, convproj_obj.track_master.plugslots.slots_audio)
		soundation_obj.channels.append(soundation_channel)

		#auto_volpan(convproj_obj, sng_master, ['master'])
		ts_numerator, ts_denominator = convproj_obj.timesig
		soundation_obj.timeSignature = str(ts_numerator)+'/'+str(ts_denominator)

		sng_channels = []

		for trackid, track_obj in convproj_obj.track__iter():
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

			add_fx(convproj_obj, soundation_channel, track_obj.plugslots.slots_audio)
			soundation_channel.volumeAutomation = autopoints_get(['track',trackid,'vol'], 0, 1)
			soundation_channel.panAutomation = autopoints_get(['track',trackid,'pan'], -1, 2)

			if track_obj.type == 'instrument':
				pluginid = track_obj.plugslots.synth
				soundation_instrument = proj_soundation.soundation_device(None)
				soundation_instrument.rackName = ''
				soundation_instrument.identifier = ''
				inst_supported = False
				plugin_found, plugin_obj = convproj_obj.plugin__get(pluginid)
				if plugin_found:
					if plugin_obj.check_match('universal', 'sampler', 'single'):
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
						_, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)
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

					if plugin_obj.check_match('user', 'reasonstudios', 'europa'):
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

					if plugin_obj.check_wildmatch('native', 'soundation', None):
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
							for paramname in spc_vals():
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

					soundation_region.position = int(notespl_obj.time.position)
					soundation_region.length = int(notespl_obj.time.duration)
					soundation_region.loopcount = 1
					soundation_region.contentPosition = 0

					if notespl_obj.time.cut_type in ['loop']:
						soundation_region.length = notespl_obj.time.cut_loopend
						soundation_region.loopcount = notespl_obj.time.duration/notespl_obj.time.cut_loopend

					if notespl_obj.time.cut_type == 'cut': 
						soundation_region.contentPosition = -(notespl_obj.time.cut_start)

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
					soundation_region.position = int(audiopl_obj.time.position)
					soundation_region.length = int(audiopl_obj.time.duration)
					soundation_region.loopcount = 1
					soundation_region.contentPosition = 0

					if audiopl_obj.time.cut_type in ['loop', 'loop_off']:
						soundation_region.length = audiopl_obj.time.cut_loopend
						soundation_region.loopcount = audiopl_obj.time.duration/audiopl_obj.time.cut_loopend

					if audiopl_obj.time.cut_type == 'cut': 
						soundation_region.contentPosition = -(audiopl_obj.time.cut_start)

					soundation_region.type = 1

					audiofilename = ''
					ref_found, sampleref_obj = convproj_obj.sampleref__get(audiopl_obj.sample.sampleref)
					if ref_found: audiofilename = sampleref_obj.fileref.get_path(None, False)

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

		#with open('soundation_debug', "w") as fileout: json.dump(jsonwrite, fileout, indent=4)