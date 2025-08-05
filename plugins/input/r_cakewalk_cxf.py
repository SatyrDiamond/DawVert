# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import value_midi
from objects.convproj import fileref
from objects import globalstore
from objects import colors
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
		return 'cakewalk_cxf'
	
	def get_name(self):
		return 'Cakewalk Interchange'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['native:bandlab']
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import cakewalk_cxf as proj_cakewalk_cxf

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'

		traits_obj = convproj_obj.traits
		traits_obj.audio_filetypes = ['wav', 'mp3', 'flac', 'm4a']
		traits_obj.audio_stretch = ['rate']
		traits_obj.auto_types = ['nopl_points']
		traits_obj.notes_midi = True
		traits_obj.placement_cut = True
		traits_obj.placement_loop = ['loop', 'loop_eq', 'loop_off', 'loop_adv', 'loop_adv_off']
		traits_obj.time_seconds = False

		convproj_obj.set_timings(4.0)

		project_obj = proj_cakewalk_cxf.cxf_project()

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		globalstore.dataset.load('bandlab', './data_main/dataset/bandlab.dset')

		bpm = project_obj.metronome.bpm

		convproj_obj.params.add('bpm', bpm, 'float')

		tempomul = 120/bpm

		for blx_sample in project_obj.samples:
			if not blx_sample.isMidi:
				add_sample(convproj_obj, dawvert_intent, blx_sample)

		groups = []

		for blx_auxChannel in project_obj.auxChannels:
			track_obj = None
			if blx_auxChannel.type == 'Bus': 
				if blx_auxChannel.id == project_obj.mainBusId:
					track_obj = convproj_obj.track_master
				else:
					track_obj = convproj_obj.track_master.fx__return__add(blx_auxChannel.id)
			if blx_auxChannel.type == 'AuxFolder': 
				track_obj = convproj_obj.fx__group__add(blx_auxChannel.id)
				if blx_auxChannel.id not in groups: groups.append(blx_auxChannel.id)

				#if blx_auxChannel.idOutput != project_obj.mainBusId:
				#	track_obj.group = blx_auxChannel.idOutput

			if track_obj:
				track_obj.visual.name = blx_auxChannel.name
				if blx_auxChannel.color: track_obj.visual.color.set_hex(blx_auxChannel.color)
				track_obj.params.add('vol', blx_auxChannel.volume, 'float')
				track_obj.params.add('pan', blx_auxChannel.pan, 'float')
				track_obj.params.add('enabled', not blx_auxChannel.isMuted, 'float')

		blx_tracks = sorted(project_obj.tracks, key=lambda x: x.order, reverse=False)
		
		for blx_track in blx_tracks:
			track_obj = None
			if blx_track.type == 'Audio':
				track_obj = convproj_obj.track__add(blx_track.id, 'audio', 1, False)
			elif blx_track.type == 'Instrument':
				track_obj = convproj_obj.track__add(blx_track.id, 'instrument', 1, False)

			if blx_track.soundbank:
				if not track_obj.visual_inst.from_dset('bandlab', 'inst', blx_track.soundbank, False):
					track_obj.visual_inst.name = blx_track.soundbank

			if track_obj:
				do_track_common(convproj_obj, track_obj, blx_track, tempomul, dawvert_intent)

				if blx_track.type == 'Instrument':
					if blx_track.parentId:
						if blx_track.parentId in groups:
							track_obj.group = blx_track.parentId

					plugin_obj = None
					if blx_track.synth:
						startid = blx_track.id
						fxid = startid+'_-1'
						plugin_obj = do_plugin(convproj_obj, blx_track.id, blx_track.synth, -1, fxid, dawvert_intent, tempomul)
						if plugin_obj: track_obj.plugslots.set_synth(fxid)

					if (not plugin_obj) and blx_track.soundbank:
						plugin_obj = convproj_obj.plugin__add(blx_track.id, 'native', 'bandlab', 'instrument')
						plugin_obj.datavals.add('instrument', blx_track.soundbank)
						plugin_obj.role = 'synth'
						plugin_obj.midi_fallback__add_from_dset('bandlab', 'inst', blx_track.soundbank)
						track_obj.plugslots.set_synth(blx_track.id)

					for blx_region in blx_track.regions:
						placement_obj = track_obj.placements.add_midi()
						time_obj = placement_obj.time
						time_obj.set_pos(tempo_calc(tempomul, blx_region.startPosition))
						time_obj.set_dur(tempo_calc(tempomul, blx_region.endPosition-blx_region.startPosition))
						if blx_region.name: placement_obj.visual.name = blx_region.name
						midipath = os.path.join(dawvert_intent.input_folder, 'Assets', 'MIDI', blx_region.sampleId+'.mid')
						do_loop(time_obj, blx_region, tempomul, 1)
						placement_obj.midi_from(midipath)

				if blx_track.type == 'Audio':
					if blx_track.parentId: track_obj.group = blx_track.parentId
					for blx_region in blx_track.regions:
						placement_obj = track_obj.placements.add_audio()
						time_obj = placement_obj.time
						time_obj.set_pos(tempo_calc(tempomul, blx_region.startPosition))
						time_obj.set_dur(tempo_calc(tempomul, blx_region.endPosition-blx_region.startPosition))
						if blx_region.name: placement_obj.visual.name = blx_region.name

						reverse = blx_region.playbackRate<0
						speed = abs(blx_region.playbackRate)

						do_loop(time_obj, blx_region, tempomul, speed)

						sp_obj = placement_obj.sample
						sp_obj.sampleref = blx_region.sampleId
						
						stretch_obj = sp_obj.stretch
						stretch_obj.timing.set__real_rate(bpm, speed)
						stretch_obj.preserve_pitch = True

def add_sample(convproj_obj, dawvert_intent, blx_sample):
	filename = os.path.join(dawvert_intent.input_folder, 'Assets', 'Audio', blx_sample.file)
	for file in glob.glob(filename):
		sampleref_obj = convproj_obj.sampleref__add(blx_sample.id, file, None)
		sampleref_obj.convert__path__fileformat()
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
	auto_obj = convproj_obj.automation.create(autoloc, 'float', True)
	for p in blx_auto.points:
		pos = tempo_calc(tempomul, p.position)
		auto_obj.add_autopoint(pos, p.value, None)

def get_pluginid(startid, uniqueId, num):
	return '%s-%i-%s.bin' % (startid.replace('-', ''), uniqueId, num)

def get_pluginfile(startid, uniqueId, num, dawvert_intent):
	filename = get_pluginid(startid, uniqueId, num)
	filepath = os.path.join(dawvert_intent.input_folder, 'Assets', 'Plugins', filename)
	if os.path.exists(filepath):
		binplug = open(filepath, 'rb')
		return binplug.read()

def do_plugin(convproj_obj, startid, blx_effect, num, fxid, dawvert_intent, tempomul):
	plugin_obj = None

	uniqueId = blx_effect.uniqueId

	if blx_effect.format == 'BandLab':
		plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'bandlab', blx_effect.slug)
		plugin_obj.role = 'fx'

		plugparams = blx_effect.params
	
		dseto_obj = globalstore.dataset.get_obj('bandlab', 'fx', blx_effect.slug)
		if dseto_obj:
			dseto_obj.visual.apply_cvpj_visual(plugin_obj.visual)
			for param_id, dset_param in dseto_obj.params.iter():
				paramv = plugparams[param_id] if param_id in plugparams else dset_param.defv
				if not dset_param.noauto:
					plugin_obj.params.add(param_id, paramv, 'float')
					if param_id in blx_effect.automation: 
						do_automation(convproj_obj, blx_effect.automation[param_id], ['plugin', fxid, param_id], tempomul)
				else:
					plugin_obj.datavals.add(param_id, paramv)
	
		else:
			for n, v in plugparams.items():
				if not isinstance(v, str) and isinstance(v, dict):
					plugparams.add(n, v, 'float')
					if param_id in blx_effect.automation:
						do_automation(convproj_obj, blx_effect.automation[param_id], ['plugin', fxid, param_id], tempomul)
				else:
					plugin_obj.datavals.add(n, v)

	elif uniqueId:
		if uniqueId == -1273960264:
			from functions.juce import data_vc2xml
			if True:
			#try:
				plugdata = get_pluginfile(startid, uniqueId, num, dawvert_intent)
				xamplerdata = data_vc2xml.get(plugdata)
				if xamplerdata.tag == 'XSamplerPersistData':
					sampler_file = None
					sampler_params = {}
					for x in xamplerdata:
						if x.tag == 'SampleInformation': sampler_file = x.get('File')
						if x.tag == 'xsmpparameters': sampler_params = dict([(i.get('id'), i.get('value')) for i in x if i.tag == 'PARAM'])

					if sampler_file:
						plugin_obj, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler(fxid, sampler_file, 'win')
						plugin_obj.role = 'synth'
					#for sampler_param in sampler_params.items():
					#	print(sampler_param)
			#except:
			#	pass
	
		else:
			from objects.inst_params import juce_plugin
			plugdata = get_pluginfile(startid, uniqueId, num, dawvert_intent)
			if plugdata is not None:
				try:
					juceobj = juce_plugin.juce_plugin()
					juceobj.name = blx_effect.name
					if plugdata[0:4] == b'CcnK': juceobj.plugtype = 'vst2'
					if plugdata[0:4] == b'VC2!': juceobj.plugtype = 'vst3'
					juceobj.rawdata = plugdata
					plugin_obj, _ = juceobj.to_cvpj(convproj_obj, fxid)
				except:
					pass

	return plugin_obj

def do_effects(convproj_obj, blx_effects, startid, plugslots, dawvert_intent, tempomul):
	for n, blx_effect in enumerate(blx_effects):
		fxid = startid+'_'+str(n)

		plugin_obj = do_plugin(convproj_obj, startid, blx_effect, n, fxid, dawvert_intent, tempomul)

		if plugin_obj:
			plugin_obj.fxdata_add(not blx_effect.bypass, 1)
			plugslots.plugin_autoplace(plugin_obj, fxid)

def do_track_common(convproj_obj, track_obj, blx_track, tempomul, dawvert_intent):
	track_obj.visual.name = blx_track.name
	track_obj.visual.color.set_hex(blx_track.color)
	track_obj.params.add('enabled', not blx_track.isMuted, 'bool')
	track_obj.params.add('solo', blx_track.isSolo, 'bool')
	track_obj.params.add('vol', blx_track.volume, 'float')
	track_obj.params.add('pan', blx_track.pan, 'float')

	for blx_auxSend in blx_track.auxSends:
		sendautoid = blx_track.id+'__'+'return__'+str(blx_auxSend.id)
		track_obj.sends.add(blx_auxSend.id, sendautoid, blx_auxSend.sendLevel)
		#do_automation(convproj_obj, blx_auxSend.automation, ['send', sendautoid, 'amount'])

	for name, blx_auto in blx_track.automation.items():
		if name == 'volume': do_automation(convproj_obj, blx_auto, ['track', blx_track.id, 'vol'], tempomul)
		if name == 'pan': do_automation(convproj_obj, blx_auto, ['track', blx_track.id, 'pan'], tempomul)
		
	do_effects(convproj_obj, blx_track.effects, blx_track.id, track_obj.plugslots, dawvert_intent, tempomul)
