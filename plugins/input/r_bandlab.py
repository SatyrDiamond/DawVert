# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import value_midi
from objects.convproj import fileref
from objects import globalstore
import xml.etree.ElementTree as ET
import plugins
import json
import os
import glob

def tempo_calc(mul, seconds):
	return ((seconds)/mul)*8

class input_bandlab(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'bandlab'
	
	def get_name(self):
		return 'BandLab BLX'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['audio_filetypes'] = ['wav', 'mp3', 'flac', 'm4a']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['audio_stretch'] = ['rate']
		in_dict['projtype'] = 'r'
		in_dict['fxtype'] = 'groupreturn'
		in_dict['time_seconds'] = False
		in_dict['file_ext'] = ['blx']
		in_dict['notes_midi'] = True
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop', 'loop_eq', 'loop_off', 'loop_adv', 'loop_adv_off']
		in_dict['plugin_included'] = ['native:bandlab']

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import bandlab as proj_bandlab

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.set_timings(4, True)

		project_obj = proj_bandlab.bandlab_project()

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		globalstore.dataset.load('bandlab', './data_main/dataset/bandlab.dset')

		bpm = 120
		if 'bpm' in project_obj.metronome:
			bpm = project_obj.metronome['bpm']

		convproj_obj.params.add('bpm', bpm, 'float')

		convproj_obj.track_master.params.add('vol', project_obj.volume, 'float')

		tempomul = 120/bpm

		for blx_auxChannel in project_obj.auxChannels:
			track_obj = convproj_obj.track_master.fx__return__add(blx_auxChannel.id)
			track_obj.params.add('vol', blx_auxChannel.returnLevel, 'float')

		for blx_sample in project_obj.samples:
			if not blx_sample.isMidi:
				add_sample(convproj_obj, dawvert_intent, blx_sample)

		blx_tracks = sorted(project_obj.tracks, key=lambda x: x.order, reverse=False)
		
		for blx_track in blx_tracks:
			if blx_track.type == 'voice':
				track_obj = convproj_obj.track__add(blx_track.id, 'audio', 1, False)
			else:
				track_obj = convproj_obj.track__add(blx_track.id, 'instrument', 1, False)

			if blx_track.type in ['voice', 'drum-machine', 'strings', 'guitar', 'piano']:
				track_obj.visual_inst.name = blx_track.soundbank
			if blx_track.type in ['creators-kit']:
				if 'displayName' in blx_track.samplerKit:
					track_obj.visual_inst.name = blx_track.samplerKit['displayName']
				elif 'id' in blx_track.samplerKit:
					track_obj.visual_inst.name = blx_track.samplerKit['id']

			if blx_track.autoPitch:
				autoPitch = blx_track.autoPitch
				fxid = blx_track.id+'_autopitch'
				plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'bandlab', 'autoPitch')
				plugin_obj.role = 'fx'
				plugin_obj.params.add('responseTime', autoPitch.responseTime, 'float')
				plugin_obj.datavals.add('algorithm', autoPitch.algorithm)
				plugin_obj.datavals.add('scale', autoPitch.scale)
				plugin_obj.datavals.add('slug', autoPitch.slug)
				plugin_obj.datavals.add('targetNotes', autoPitch.targetNotes)
				plugin_obj.datavals.add('tonic', autoPitch.tonic)
				plugin_obj.fxdata_add(not autoPitch.bypass, autoPitch.mix)
				track_obj.plugin_autoplace(plugin_obj, fxid)

			if blx_track.type == 'voice':
				do_track_common(convproj_obj, track_obj, blx_track, tempomul)
				for blx_region in blx_track.regions:
					placement_obj = track_obj.placements.add_audio()
					placement_obj.time.position = tempo_calc(tempomul, blx_region.startPosition)
					placement_obj.time.duration = tempo_calc(tempomul, blx_region.endPosition-blx_region.startPosition)
					if blx_region.name: placement_obj.visual.name = blx_region.name

					reverse = blx_region.playbackRate<0
					speed = abs(blx_region.playbackRate)

					do_loop(placement_obj.time, blx_region, tempomul, speed)

					sp_obj = placement_obj.sample
					sp_obj.pitch = blx_region.pitchShift
					sp_obj.sampleref = blx_region.sampleId
					sp_obj.vol = blx_region.gain
					sp_obj.stretch.set_rate_speed(bpm, (1/speed), True)
					sp_obj.stretch.uses_tempo = True
					sp_obj.stretch.preserve_pitch = True

					placement_obj.fade_in.set_dur(blx_region.fadeIn, 'seconds')
					placement_obj.fade_out.set_dur(blx_region.fadeOut, 'seconds')

			else:
				do_track_common(convproj_obj, track_obj, blx_track, tempomul)
				if blx_track.type == 'creators-kit':
					plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'multi')
					track_obj.plugslots.set_synth(pluginid)
					track_obj.is_drum = True
					samplerkit = blx_track.samplerKit
					if samplerkit:
						if 'kit' in samplerkit:
							kitdata = samplerkit['kit']
							if 'layers' in kitdata:
								for layer in kitdata['layers']:
									pitch = layer['pitch'] if 'pitch' in layer else 60
									minKeyRange = layer['minKeyRange'] if 'minKeyRange' in layer else pitch
									maxKeyRange = layer['maxKeyRange'] if 'maxKeyRange' in layer else pitch

									sp_obj = plugin_obj.sampleregion_add(minKeyRange-60, maxKeyRange-60, pitch-60, None)
									sp_obj.vel_min = layer['maxVelRange']/127 if 'maxVelRange' in layer else 1
									sp_obj.vel_max = layer['minVelRange']/127 if 'minVelRange' in layer else 0
									sp_obj.vol = layer['volume'] if 'volume' in layer else 0

				for blx_region in blx_track.regions:
					placement_obj = track_obj.placements.add_midi()
					placement_obj.time.position = tempo_calc(tempomul, blx_region.startPosition)
					placement_obj.time.duration = tempo_calc(tempomul, blx_region.endPosition-blx_region.startPosition)
					if blx_region.name: placement_obj.visual.name = blx_region.name
					midipath = os.path.join(dawvert_intent.input_folder, 'Assets', 'MIDI', blx_region.sampleId+'.mid')
					do_loop(placement_obj.time, blx_region, tempomul, 1)
					placement_obj.midi_from(midipath)

def add_sample(convproj_obj, dawvert_intent, blx_sample):
	filename = os.path.join(dawvert_intent.input_folder, 'Assets', 'Audio', blx_sample.id+'.*')

	for file in glob.glob(filename):
		sampleref_obj = convproj_obj.sampleref__add(blx_sample.id, file, None)
		sampleref_obj.convert__path__fileformat()
		if blx_sample.duration:
			sampleref_obj.set_dur_sec(blx_sample.duration)
		else:
			sampleref_obj.get_dur_sec()
		break

def do_loop(time_obj, blx_region, tempomul, speed):
	loopLength = tempo_calc(tempomul, blx_region.loopLength)
	sampleOffset = tempo_calc(tempomul, blx_region.sampleOffset)
	duration = tempo_calc(tempomul, blx_region.startPosition-blx_region.endPosition)

	if loopLength == 0:
		time_obj.set_offset(sampleOffset)
	else:
		time_obj.set_loop_data(sampleOffset, sampleOffset, loopLength)

def do_automation(convproj_obj, blx_auto, autoloc, tempomul):
	for p in blx_auto.points:
		convproj_obj.automation.add_autopoint(autoloc, 'float', p.position, p.value, 'normal')

def do_track_common(convproj_obj, track_obj, blx_track, tempomul):
	track_obj.visual.name = blx_track.name
	track_obj.visual.color.set_hex(blx_track.color)
	track_obj.params.add('enabled', not blx_track.isMuted, 'bool')
	track_obj.params.add('solo', blx_track.isSolo, 'bool')
	track_obj.params.add('vol', blx_track.volume, 'float')
	track_obj.params.add('pan', blx_track.pan, 'float')

	for blx_auxSend in blx_track.auxSends:
		sendautoid = blx_track.id+'__'+'return__'+str(blx_auxSend.id)
		track_obj.sends.add(blx_auxSend.id, sendautoid, blx_auxSend.sendLevel)
		do_automation(convproj_obj, blx_auxSend.automation, ['send', sendautoid, 'amount'], tempomul)

	if blx_track.automation:
		do_automation(convproj_obj, blx_track.automation.pan, ['track', blx_track.id, 'pan'], tempomul)
		do_automation(convproj_obj, blx_track.automation.volume, ['track', blx_track.id, 'vol'], tempomul)
		
	for n, blx_effect in enumerate(blx_track.effects):
		fxid = blx_track.id+'_'+str(n)

		plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'bandlab', blx_effect.slug)
		plugin_obj.role = 'fx'
		plugin_obj.fxdata_add(not blx_effect.bypass, 1)

		plugparams = blx_effect.params

		dseto_obj = globalstore.dataset.get_obj('bandlab', 'fx', blx_effect.slug)
		if dseto_obj:
			dseto_obj.visual.apply_cvpj_visual(plugin_obj.visual)
			for param_id, dset_param in dseto_obj.params.iter():
				paramv = plugparams[param_id] if param_id in plugparams else dset_param.defv
				if not dset_param.noauto:
					plugin_obj.params.add(param_id, paramv, 'float')
					if n in blx_effect.automation: 
						do_automation(convproj_obj, blx_effect.automation[n], ['plugin', fxid, n], tempomul)
				else:
					plugin_obj.datavals.add(param_id, paramv)

		else:
			for n, v in plugparams.items():
				if not isinstance(v, str) and isinstance(v, dict):
					plugparams.add(n, v, 'float')
					if n in blx_effect.automation:
						do_automation(convproj_obj, blx_effect.automation[n], ['plugin', fxid, n], tempomul)
				else:
					plugin_obj.datavals.add(n, v)

		track_obj.plugin_autoplace(plugin_obj, fxid)
