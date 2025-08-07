# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import value_midi
from functions import xtramath
from objects.convproj import fileref
from objects import globalstore
from objects import colors
import xml.etree.ElementTree as ET
import plugins
import json
import os
import glob
import zipfile
from objects import debug
from objects.exceptions import ProjectFileParserException

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

		samplefolder = dawvert_intent.path_samples['extracted']

		zip_data = None
		success = False
		zip_start_path = []
		try:
			if dawvert_intent.input_mode == 'file':
				zip_data = zipfile.ZipFile(dawvert_intent.input_file, 'r')
				zip_namelist = zip_data.namelist()
				if True in [x.startswith('Sonar/') for x in zip_namelist]:
					raise ProjectFileParserException('Sonar-Created CXF is not supported.')
				else:

					for jsonname in zip_data.namelist():
						if '.cxf' in jsonname: 
							json_filename = jsonname
							zip_start_path = jsonname.split('/')
							if zip_start_path: zip_start_path = zip_start_path[:-1]

							cxf_project = zip_data.read(json_filename)
							cxf_proj = json.loads(cxf_project)
							success = project_obj.read(cxf_proj)
							break

		except:
			pass

		try:
			success = project_obj.load_from_file(dawvert_intent.input_file)
		except:
			pass

		if not success: exit()

		globalstore.dataset.load('bandlab', './data_main/dataset/bandlab.dset')

		bpm = project_obj.metronome.bpm

		convproj_obj.params.add('bpm', bpm, 'float')

		convproj_obj.metadata.name = project_obj.song.name
		convproj_obj.metadata.comment_text = project_obj.description

		tempomul = 120/bpm

		debugvis_id_store = debug.id_visual_name()
		debugvis_id_store.add(project_obj.song.id, 'Song ID')
		debugvis_id_store.add(project_obj.mainBusId, 'mainBusId')

		for cxf_sample in project_obj.samples:
			if not cxf_sample.isMidi:
				add_sample(convproj_obj, dawvert_intent, cxf_sample, zip_data, zip_start_path, samplefolder)

		groups = []

		for cxf_auxChannel in project_obj.auxChannels:
			debugvis_id_store.add(cxf_auxChannel.id, 'Aux %i: %s' % (cxf_auxChannel.order, cxf_auxChannel.name))
			track_obj = None
			autoloc = None
			if cxf_auxChannel.type == 'Bus': 
				if cxf_auxChannel.id == project_obj.mainBusId:
					track_obj = convproj_obj.track_master
					autoloc = ['master']
				else:
					track_obj = convproj_obj.track_master.fx__return__add(cxf_auxChannel.id)
					autoloc = ['return', cxf_auxChannel.id]
			if cxf_auxChannel.type == 'AuxFolder': 
				track_obj = convproj_obj.fx__group__add(cxf_auxChannel.id)
				if cxf_auxChannel.id not in groups: groups.append(cxf_auxChannel.id)
				autoloc = ['group', cxf_auxChannel.id]

				#if cxf_auxChannel.idOutput != project_obj.mainBusId:
				#	track_obj.group = cxf_auxChannel.idOutput

			if track_obj:
				track_obj.visual.name = cxf_auxChannel.name
				if cxf_auxChannel.color: track_obj.visual.color.set_hex(cxf_auxChannel.color)
				track_obj.params.add('vol', cxf_auxChannel.volume, 'float')
				track_obj.params.add('pan', cxf_auxChannel.pan, 'float')
				track_obj.params.add('enabled', not cxf_auxChannel.isMuted, 'float')

				for k, a in cxf_auxChannel.automation.items():
					if k == 'volume': do_automation(convproj_obj, a, autoloc+['vol'], tempomul)
					if k == 'pan': do_automation(convproj_obj, a, autoloc+['pan'], tempomul)


		cxf_tracks = sorted(project_obj.tracks, key=lambda x: x.order, reverse=False)
		
		for cxf_track in cxf_tracks:
			debugvis_id_store.add(cxf_track.id, 'Track %i: %s' % (cxf_track.order, cxf_track.name))

			track_obj = None
			if cxf_track.type == 'Audio':
				track_obj = convproj_obj.track__add(cxf_track.id, 'audio', 1, False)
			elif cxf_track.type == 'Instrument':
				track_obj = convproj_obj.track__add(cxf_track.id, 'instrument', 1, False)

			if cxf_track.soundbank:
				if not track_obj.visual_inst.from_dset('bandlab', 'inst', cxf_track.soundbank, False):
					track_obj.visual_inst.name = cxf_track.soundbank

			if track_obj:
				do_track_common(convproj_obj, track_obj, cxf_track, tempomul, dawvert_intent, zip_data, zip_start_path)

				for cxf_auxSend in cxf_track.auxSends:
					debugvis_id_store.add(cxf_track.id, 'TrackSend: '+cxf_auxSend.id+' <<< '+cxf_auxChannel.name)
					sendautoid = cxf_track.id+'__'+'return__'+str(cxf_auxSend.id)
					track_obj.sends.add(cxf_auxSend.id, sendautoid, cxf_auxSend.sendLevel)
					for k, a in cxf_auxSend.automation.items():
						if k == 'sendLevel': do_automation(convproj_obj, a, ['send', sendautoid, 'amount'], tempomul)

				if cxf_track.type == 'Instrument':
					if cxf_track.parentId:
						if cxf_track.parentId in groups:
							track_obj.group = cxf_track.parentId

					plugin_obj = None
					if cxf_track.synth:
						startid = cxf_track.id
						fxid = startid+'_-1'
						plugin_obj, middlenote, pitch = do_plugin(convproj_obj, cxf_track.id, cxf_track.synth, -1, fxid, dawvert_intent, tempomul, zip_data, zip_start_path)
						if plugin_obj: 
							track_obj.plugslots.set_synth(fxid)
							track_obj.params.add('pitch', pitch/100, 'float')
							track_obj.datavals.add('middlenote', middlenote)

					if (not plugin_obj) and cxf_track.soundbank:
						plugin_obj = convproj_obj.plugin__add(cxf_track.id, 'native', 'bandlab', 'instrument')
						plugin_obj.datavals.add('instrument', cxf_track.soundbank)
						plugin_obj.role = 'synth'
						plugin_obj.midi_fallback__add_from_dset('bandlab', 'inst', cxf_track.soundbank)
						track_obj.plugslots.set_synth(cxf_track.id)

					for cxf_region in cxf_track.regions:
						placement_obj = track_obj.placements.add_midi()
						time_obj = placement_obj.time
						time_obj.set_pos(tempo_calc(tempomul, cxf_region.startPosition))
						time_obj.set_dur(tempo_calc(tempomul, cxf_region.endPosition-cxf_region.startPosition))
						if cxf_region.name: placement_obj.visual.name = cxf_region.name
						do_loop(time_obj, cxf_region, tempomul, 1)
						if zip_data is None:
							midipath = os.path.join(dawvert_intent.input_folder, 'Assets', 'MIDI', cxf_region.sampleId+'.mid')
							placement_obj.midi_from(midipath)
						else:
							midipath = "/".join(zip_start_path+['Assets', 'MIDI', cxf_region.sampleId+'.mid'])
							placement_obj.midi_from_bin(zip_data.read(midipath))

				if cxf_track.type == 'Audio':
					if cxf_track.parentId: track_obj.group = cxf_track.parentId
					for cxf_region in cxf_track.regions:
						placement_obj = track_obj.placements.add_audio()
						time_obj = placement_obj.time
						time_obj.set_pos(tempo_calc(tempomul, cxf_region.startPosition))
						time_obj.set_dur(tempo_calc(tempomul, cxf_region.endPosition-cxf_region.startPosition))
						if cxf_region.name: placement_obj.visual.name = cxf_region.name

						reverse = cxf_region.playbackRate<0
						speed = abs(cxf_region.playbackRate)

						do_loop(time_obj, cxf_region, tempomul, speed)

						sp_obj = placement_obj.sample
						sp_obj.sampleref = cxf_region.sampleId
						
						stretch_obj = sp_obj.stretch
						stretch_obj.timing.set__real_rate(bpm, speed)
						stretch_obj.preserve_pitch = True


		#for cxf_auxChannel in project_obj.auxChannels:
		#	print('AUX_IN',
		#		debugvis_id_store.get(cxf_auxChannel.id), 
		#		debugvis_id_store.get(cxf_auxChannel.idOutput)
		#		)
#
		#for cxf_track in cxf_tracks:
		#	print('TRACK_IN',
		#		debugvis_id_store.get(cxf_track.parentId), 
		#		debugvis_id_store.get(cxf_track.idOutput)
		#		)


def add_sample(convproj_obj, dawvert_intent, cxf_sample, zip_data, zip_start_path, samplefolder):
	filename = os.path.join(dawvert_intent.input_folder, 'Assets', 'Audio', cxf_sample.file)
	if zip_data is None:
		sampleref_obj = convproj_obj.sampleref__add(cxf_sample.id, filename, None)
		sampleref_obj.convert__path__fileformat()
	else:
		audiopath = "/".join(zip_start_path+['Assets', 'Audio', cxf_sample.file])
		if audiopath in zip_data.namelist(): 
			audio_filename = samplefolder+cxf_sample.file
			try:
				outpath = zip_data.extract(audiopath, path=samplefolder, pwd=None)
				sampleref_obj = convproj_obj.sampleref__add(cxf_sample.id, outpath, None)
				sampleref_obj.convert__path__fileformat()
			except:
				pass

def do_loop(time_obj, cxf_region, tempomul, speed):
	loopLength = tempo_calc(tempomul, cxf_region.loopLength)
	sampleOffset = tempo_calc(tempomul, cxf_region.sampleOffset)
	duration = tempo_calc(tempomul, cxf_region.startPosition-cxf_region.endPosition)

	if loopLength == 0:
		time_obj.set_offset(sampleOffset)
	else:
		time_obj.set_loop_data(sampleOffset, sampleOffset, loopLength)

def do_automation(convproj_obj, cxf_auto, autoloc, tempomul):
	auto_obj = convproj_obj.automation.create(autoloc, 'float', True)
	for p in cxf_auto.points:
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

def do_plugin(convproj_obj, startid, cxf_effect, num, fxid, dawvert_intent, tempomul, zip_data, zip_start_path):
	plugin_obj = None

	uniqueId = cxf_effect.uniqueId

	pitch = 0
	middlenote = 0

	if cxf_effect.format == 'BandLab':
		plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'bandlab', cxf_effect.slug)
		plugin_obj.role = 'fx'

		plugparams = cxf_effect.params

		dseto_obj = globalstore.dataset.get_obj('bandlab', 'fx', cxf_effect.slug)
		if dseto_obj:
			dseto_obj.visual.apply_cvpj_visual(plugin_obj.visual)
			for param_id, dset_param in dseto_obj.params.iter():
				paramv = plugparams[param_id] if param_id in plugparams else dset_param.defv
				if not dset_param.noauto:
					plugin_obj.params.add(param_id, paramv, 'float')
					if param_id in cxf_effect.automation: 
						do_automation(convproj_obj, cxf_effect.automation[param_id], ['plugin', fxid, param_id], tempomul)
				else:
					plugin_obj.datavals.add(param_id, paramv)
	
		else:
			for n, v in plugparams.items():
				if not isinstance(v, str) and isinstance(v, dict):
					plugparams.add(n, v, 'float')
					if param_id in cxf_effect.automation:
						do_automation(convproj_obj, cxf_effect.automation[param_id], ['plugin', fxid, param_id], tempomul)
				else:
					plugin_obj.datavals.add(n, v)

	elif uniqueId:

		plugdata = None
		if zip_data is None: plugdata = get_pluginfile(startid, uniqueId, num, dawvert_intent)
		else: 
			plugpath = "/".join(zip_start_path+['Assets', 'Plugins', get_pluginid(startid, uniqueId, num)])
			if plugpath in zip_data.namelist(): plugdata = zip_data.read(plugpath)

		if uniqueId == -1273960264:
			from functions.juce import data_vc2xml
			if plugdata is not None:
				xamplerdata = data_vc2xml.get(plugdata)
				if xamplerdata.tag == 'XSamplerPersistData':
					sampler_file = None
					sampler_params = {}
					for x in xamplerdata:
						if x.tag == 'SampleInformation': sampler_file = x.get('File')
						if x.tag == 'xsmpparameters': sampler_params = dict([(i.get('id'), i.get('value')) for i in x if i.tag == 'PARAM'])
	
					x_root = 60
					x_shift = 0
					x_fine = 0

					if sampler_file:
						plugin_obj, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler(fxid, sampler_file, 'win')
						plugin_obj.role = 'synth'
						sp_obj.point_value_type = "percent"

						filter_obj = plugin_obj.filter
						for paramid, val in sampler_params.items():
							val = float(val)

							if paramid == 'xsmpgain': sp_obj.vol = val/0.7876096963882446
							elif paramid == 'xsmppan': sp_obj.pan = (val-0.5)*2
							elif paramid == 'xsmpsamplestart': sp_obj.start = val
							elif paramid == 'xsmploopstart': sp_obj.loop_start = val
							elif paramid == 'xsmploopend': sp_obj.loop_end = val
							elif paramid == 'xsmpsampleend': sp_obj.end = val
							elif paramid == 'xsmproot': x_root = round(val*127)
							elif paramid == 'xsmpstshift': x_shift = (val-0.5)*24
							elif paramid == 'xsmpfineshift': x_fine = (val-0.5)*100
							elif paramid == 'xsmpplaymode': 
								sp_obj.loop_active = val==1.0
								sp_obj.trigger = 'oneshot' if val==0.5 else 'normal'
							elif paramid == 'xsmpfiltercutoff': 
								filter_obj.freq = 20 * 1000**val
							elif paramid == 'xsmpfilterres': 
								filter_obj.q = xtramath.between_from_one(0.1, 10.0, val)
							elif paramid == 'xsmpfiltertype': 
								filttypenum = round(val*3)
								filter_obj.on = filttypenum==0
								if filttypenum==1: filter_obj.type.set_list(['low_pass', None])
								if filttypenum==2: filter_obj.type.set_list(['band_pass', None])
								if filttypenum==3: filter_obj.type.set_list(['high_pass', None])
							else: 
								plugin_obj.params.add(paramid, val, 'float')

					pitch = x_shift+x_fine
					middlenote = x_root-60

		else:
			from objects.inst_params import juce_plugin

			if plugdata is not None:
				#try:
					juceobj = juce_plugin.juce_plugin()
					juceobj.name = cxf_effect.name
					if plugdata[0:4] == b'CcnK': juceobj.plugtype = 'vst2'
					if plugdata[0:4] == b'VC2!': juceobj.plugtype = 'vst3'
					juceobj.rawdata = plugdata
					plugin_obj, _ = juceobj.to_cvpj(convproj_obj, fxid)

					for param_id in cxf_effect.automation:
						do_automation(convproj_obj, cxf_effect.automation[param_id], ['plugin', fxid, 'ext_param_'+param_id], tempomul)

				#except:
				#	pass

	return plugin_obj, middlenote, pitch

def do_effects(convproj_obj, cxf_effects, startid, plugslots, dawvert_intent, tempomul, zip_data, zip_start_path):
	for n, cxf_effect in enumerate(cxf_effects):
		fxid = startid+'_'+str(n)

		plugin_obj, _, _ = do_plugin(convproj_obj, startid, cxf_effect, n, fxid, dawvert_intent, tempomul, zip_data, zip_start_path)

		if plugin_obj:
			plugin_obj.fxdata_add(not cxf_effect.bypass, 1)
			plugslots.plugin_autoplace(plugin_obj, fxid)

def do_track_common(convproj_obj, track_obj, cxf_track, tempomul, dawvert_intent, zip_data, zip_start_path):
	track_obj.visual.name = cxf_track.name
	track_obj.visual.color.set_hex(cxf_track.color)
	track_obj.params.add('enabled', not cxf_track.isMuted, 'bool')
	track_obj.params.add('solo', cxf_track.isSolo, 'bool')
	track_obj.params.add('vol', cxf_track.volume, 'float')
	track_obj.params.add('pan', cxf_track.pan, 'float')

	for cxf_auxSend in cxf_track.auxSends:
		sendautoid = cxf_track.id+'__'+'return__'+str(cxf_auxSend.id)
		track_obj.sends.add(cxf_auxSend.id, sendautoid, cxf_auxSend.sendLevel)
		#do_automation(convproj_obj, cxf_auxSend.automation, ['send', sendautoid, 'amount'])

	for name, cxf_auto in cxf_track.automation.items():
		if name == 'volume': do_automation(convproj_obj, cxf_auto, ['track', cxf_track.id, 'vol'], tempomul)
		if name == 'pan': do_automation(convproj_obj, cxf_auto, ['track', cxf_track.id, 'pan'], tempomul)
		
	do_effects(convproj_obj, cxf_track.effects, cxf_track.id, track_obj.plugslots, dawvert_intent, tempomul, zip_data, zip_start_path)
