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

def conv_color(b_color):
	color = b_color.to_bytes(4, "little")
	return [color[2],color[1],color[1]]

class stored_vals():
	def __init__(self):
		self.tempomul = 1
		self.zip_data = None
		self.zip_namelist = []
		self.zip_start_path = []
		self.samplefolder = None
		self.dawvert_intent = None

	def tempo_calc(self, v):
		return (v/self.tempomul)*8
	
	def zip_get_path(self, cata, filename):
		outpath = self.zip_start_path+['Assets', cata, filename]
		return '/'.join(outpath)

	def zip_get_exists(self, cata, filename):
		return self.zip_get_path(cata, filename) in self.zip_data.namelist()

	def zip_extract(self, cata, filename):
		zippath = self.zip_get_path(cata, filename)
		if zippath in self.zip_data.namelist():
			outpath = os.path.join(self.samplefolder, filename)
			return self.zip_data.extract(zippath, outpath, pwd=None)

	def zip_getdata(self, cata, filename):
		zippath = self.zip_get_path(cata, filename)
		if zippath in self.zip_data.namelist():
			outpath = os.path.join(self.samplefolder, filename)
			return self.zip_data.read(zippath)

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
		traits_obj.track_arranger = True

		convproj_obj.set_timings(4.0)

		project_obj = proj_cakewalk_cxf.cxf_project()

		stored_vals_obj = stored_vals()
		stored_vals_obj.samplefolder = dawvert_intent.path_samples['extracted']
		stored_vals_obj.dawvert_intent = dawvert_intent

		success = False
		try:
			if dawvert_intent.input_mode == 'file':
				zip_data = stored_vals_obj.zip_data = zipfile.ZipFile(dawvert_intent.input_file, 'r')
				stored_vals_obj.zip_namelist = [x.replace('/', '\\').split('\\') for x in zip_data.namelist()]
				if True in [x.startswith('Sonar/') for x in zip_data.namelist()]:
					raise ProjectFileParserException('Sonar-Created CXF is not supported.')
				else:

					for jsonname in zip_data.namelist():
						if '.cxf' in jsonname: 
							json_filename = jsonname
							zip_start_path = jsonname.replace('/', '\\').split('\\')
							if zip_start_path: stored_vals_obj.zip_start_path = zip_start_path[:-1]

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

		globalstore.datapack.load('bandlab', './data/datapack/app/bandlab.xml')

		bpm = project_obj.metronome.bpm
		convproj_obj.params.add('bpm', bpm, 'float')
		stored_vals_obj.tempomul = 120/bpm

		convproj_obj.metadata.name = project_obj.song.name
		convproj_obj.metadata.comment_text = project_obj.description

		debugvis_id_store = debug.id_visual_name()
		debugvis_id_store.add(project_obj.song.id, 'Song ID')
		debugvis_id_store.add(project_obj.mainBusId, 'mainBusId')

		for cxf_sample in project_obj.samples:
			if not cxf_sample.isMidi:
				add_sample(convproj_obj, cxf_sample, stored_vals_obj)

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
				track_obj.visual_track.group_expanded = False
				if cxf_auxChannel.id not in groups: groups.append(cxf_auxChannel.id)
				autoloc = ['group', cxf_auxChannel.id]

				for cxf_auxSend in cxf_auxChannel.auxSends:
					sendautoid = cxf_auxChannel.id+'__'+'return__'+str(cxf_auxSend.id)
					track_obj.sends.add(cxf_auxSend.id, sendautoid, cxf_auxSend.sendLevel)
				#if cxf_auxChannel.idOutput != project_obj.mainBusId:
				#	track_obj.group = cxf_auxChannel.idOutput

			if track_obj:
				track_obj.visual.name = cxf_auxChannel.name
				if cxf_auxChannel.color: track_obj.visual.color.set_hex(cxf_auxChannel.color)
				track_obj.params.add('vol', cxf_auxChannel.volume, 'float')
				track_obj.params.add('pan', cxf_auxChannel.pan, 'float')
				track_obj.params.add('enabled', not cxf_auxChannel.isMuted, 'float')

				for k, a in cxf_auxChannel.automation.items():
					if k == 'volume': do_automation(convproj_obj, a, autoloc+['vol'], stored_vals_obj)
					if k == 'pan': do_automation(convproj_obj, a, autoloc+['pan'], stored_vals_obj)


		cxf_tracks = sorted(project_obj.tracks, key=lambda x: x.order, reverse=False)
		
		for cxf_track in cxf_tracks:
			debugvis_id_store.add(cxf_track.id, 'Track %i: %s' % (cxf_track.order, cxf_track.name))

			track_obj = None
			if cxf_track.type == 'Audio':
				track_obj = convproj_obj.track__add(cxf_track.id, 'audio', 1, False)
			elif cxf_track.type == 'Instrument':
				track_obj = convproj_obj.track__add(cxf_track.id, 'instrument', 1, False)

			if cxf_track.soundbank:
				if not track_obj.visual_inst.from_datapack('bandlab', 'inst', cxf_track.soundbank, False):
					track_obj.visual_inst.name = cxf_track.soundbank

			if track_obj:
				do_track_common(convproj_obj, track_obj, cxf_track, stored_vals_obj)

				for cxf_auxSend in cxf_track.auxSends:
					debugvis_id_store.add(cxf_track.id, 'TrackSend: '+cxf_auxSend.id+' <<< '+cxf_auxChannel.name)
					sendautoid = cxf_track.id+'__'+'return__'+str(cxf_auxSend.id)
					track_obj.sends.add(cxf_auxSend.id, sendautoid, cxf_auxSend.sendLevel)
					for k, a in cxf_auxSend.automation.items():
						if k == 'sendLevel': do_automation(convproj_obj, a, ['send', sendautoid, 'amount'], stored_vals_obj)

				if cxf_track.type == 'Instrument':
					if cxf_track.parentId:
						if cxf_track.parentId in groups:
							track_obj.group = cxf_track.parentId

					plugin_obj = None
					if cxf_track.synth:
						startid = cxf_track.id
						fxid = startid+'_-1'
						plugin_obj, middlenote, pitch = do_plugin(convproj_obj, cxf_track.id, cxf_track.synth, -1, fxid, stored_vals_obj)
						if plugin_obj: 
							track_obj.plugslots.set_synth(fxid)
							track_obj.params.add('pitch', pitch/100, 'float')
							track_obj.datavals.add('middlenote', middlenote)

					if (not plugin_obj) and cxf_track.soundbank:
						plugin_obj = convproj_obj.plugin__add(cxf_track.id, 'native', 'bandlab', 'instrument')
						plugin_obj.datavals.add('instrument', cxf_track.soundbank)
						plugin_obj.role = 'synth'
						plugin_obj.midi_fallback__add_from_datapack('bandlab', 'inst', cxf_track.soundbank)
						track_obj.plugslots.set_synth(cxf_track.id)

					for cxf_region in cxf_track.regions:
						placement_obj = track_obj.placements.add_midi()
						time_obj = placement_obj.time
						time_obj.set_pos(stored_vals_obj.tempo_calc(cxf_region.startPosition))
						time_obj.set_dur(stored_vals_obj.tempo_calc(cxf_region.endPosition-cxf_region.startPosition))
						if cxf_region.name: placement_obj.visual.name = cxf_region.name
						do_loop(time_obj, cxf_region, stored_vals_obj, 1)
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
						time_obj.set_pos(stored_vals_obj.tempo_calc(cxf_region.startPosition))
						time_obj.set_dur(stored_vals_obj.tempo_calc(cxf_region.endPosition-cxf_region.startPosition))
						if cxf_region.name: placement_obj.visual.name = cxf_region.name

						reverse = cxf_region.playbackRate<0
						speed = abs(cxf_region.playbackRate)

						do_loop(time_obj, cxf_region, stored_vals_obj, speed)

						sp_obj = placement_obj.sample
						sp_obj.sampleref = cxf_region.sampleId
						
						stretch_obj = sp_obj.stretch
						stretch_obj.timing.set__real_rate(bpm, speed)
						stretch_obj.preserve_pitch = True

						#cxf_region.printtime()

		arranger = project_obj.arranger
		arrangerTracks = arranger.arrangerTracks
		if arrangerTracks:
			for section in arrangerTracks[0].sections:
				timemarker_obj = convproj_obj.arranger.add()
				timemarker_obj.type = 'region'
				timemarker_obj.time.set_posdur(
					(section.startTimeArrTicks/240), 
					((section.endTimeArrTicks/240)-timemarker_obj.position)
					)
				timemarker_obj.visual.name = section.name
				timemarker_obj.visual.color.set_int(conv_color(section.color))

def add_sample(convproj_obj, cxf_sample, stored_vals_obj):
	filename = os.path.join(stored_vals_obj.dawvert_intent.input_folder, 'Assets', 'Audio', cxf_sample.file)
	zip_data = stored_vals_obj.zip_data
	if zip_data is None:
		sampleref_obj = convproj_obj.sampleref__add(cxf_sample.id, filename, None)
		sampleref_obj.convert__path__fileformat()
	else:
		outpath = stored_vals_obj.zip_extract('Audio', cxf_sample.file)
		if outpath:
			sampleref_obj = convproj_obj.sampleref__add(cxf_sample.id, outpath, None)
			sampleref_obj.convert__path__fileformat()

def do_loop(time_obj, cxf_region, stored_vals_obj, speed):
	loopLength = stored_vals_obj.tempo_calc(cxf_region.loopLength)
	sampleOffset = stored_vals_obj.tempo_calc(cxf_region.sampleOffset)/speed
	duration = stored_vals_obj.tempo_calc(cxf_region.startPosition-cxf_region.endPosition)

	if loopLength == 0:
		time_obj.set_offset(sampleOffset)
	else:
		time_obj.set_loop_data(sampleOffset, sampleOffset, loopLength)

def do_automation(convproj_obj, cxf_auto, autoloc, stored_vals_obj):
	auto_obj = convproj_obj.automation.create(autoloc, 'float', True)
	for p in cxf_auto.points:
		pos = tempo_calc(stored_vals_obj.tempomul, p.position)
		auto_obj.add_autopoint(pos, p.value, None)

def get_pluginid(startid, uniqueId, num):
	return '%s-%i-%s.bin' % (startid.replace('-', ''), uniqueId, num)

def get_pluginfile(startid, uniqueId, num, dawvert_intent):
	filename = get_pluginid(startid, uniqueId, num)
	filepath = os.path.join(dawvert_intent.input_folder, 'Assets', 'Plugins', filename)
	if os.path.exists(filepath):
		binplug = open(filepath, 'rb')
		return binplug.read()

def do_plugin(convproj_obj, startid, cxf_effect, num, fxid, stored_vals_obj):
	plugin_obj = None

	uniqueId = cxf_effect.uniqueId

	pitch = 0
	middlenote = 0

	if cxf_effect.format == 'BandLab':
		plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'bandlab', cxf_effect.slug)
		plugin_obj.role = 'fx'

		plugparams = cxf_effect.params

		dseto_obj = globalstore.datapack.get_obj('bandlab', 'fx', cxf_effect.slug)
		if dseto_obj:
			dseto_obj.visual.apply_cvpj_visual(plugin_obj.visual)
			for param_id, dset_param in dseto_obj.params.iter():
				paramv = plugparams[param_id] if param_id in plugparams else dset_param.defv
				if not dset_param.noauto:
					plugin_obj.params.add(param_id, paramv, 'float')
					if param_id in cxf_effect.automation: 
						do_automation(convproj_obj, cxf_effect.automation[param_id], ['plugin', fxid, param_id], stored_vals_obj)
				else:
					plugin_obj.datavals.add(param_id, paramv)
	
		else:
			for n, v in plugparams.items():
				if not isinstance(v, str) and isinstance(v, dict):
					plugparams.add(n, v, 'float')
					if param_id in cxf_effect.automation:
						do_automation(convproj_obj, cxf_effect.automation[param_id], ['plugin', fxid, param_id], stored_vals_obj)
				else:
					plugin_obj.datavals.add(n, v)

	elif uniqueId == -1273960264:
		plugdata = None
		if stored_vals_obj.zip_data is None: plugdata = get_pluginfile(startid, uniqueId, num, stored_vals_obj.dawvert_intent)
		else: plugdata = stored_vals_obj.zip_getdata('Plugins', get_pluginid(startid, uniqueId, num))
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

	elif cxf_effect.format == 'VST':
		plugdata = None
		if stored_vals_obj.zip_data is None: plugdata = get_pluginfile(startid, uniqueId, num, stored_vals_obj.dawvert_intent)
		else: plugdata = stored_vals_obj.zip_getdata('Plugins', get_pluginid(startid, uniqueId, num))

		from objects.inst_params import juce_plugin
		if plugdata is not None:
			try:
				if plugdata[0:4] == b'CcnK':
					juceobj = juce_plugin.juce_plugin()
					juceobj.plugtype = 'vst2'
					juceobj.name = cxf_effect.name
					juceobj.rawdata = plugdata
					juceobj.uniqueId = uniqueId
					plugin_obj, _ = juceobj.to_cvpj(convproj_obj, fxid)
					for param_id in cxf_effect.automation:
						do_automation(convproj_obj, cxf_effect.automation[param_id], ['plugin', fxid, 'ext_param_'+param_id], stored_vals_obj)
			except:
				pass

	elif cxf_effect.format == 'VST3':
		plugdata = None
		if stored_vals_obj.zip_data is None: plugdata = get_pluginfile(startid, uniqueId, num, stored_vals_obj.dawvert_intent)
		else: plugdata = stored_vals_obj.zip_getdata('Plugins', get_pluginid(startid, uniqueId, num))

		from objects.inst_params import juce_plugin
		if plugdata is not None:
			try:
				if plugdata[0:4] == b'VC2!':
					juceobj = juce_plugin.juce_plugin()
					juceobj.plugtype = 'vst3'
					juceobj.name = cxf_effect.name
					juceobj.rawdata = plugdata
					juceobj.uniqueId = uniqueId
					plugin_obj, _ = juceobj.to_cvpj(convproj_obj, fxid)
					for param_id in cxf_effect.automation:
						do_automation(convproj_obj, cxf_effect.automation[param_id], ['plugin', fxid, 'ext_param_'+param_id], stored_vals_obj)
			except:
				pass
	return plugin_obj, middlenote, pitch

def do_effects(convproj_obj, cxf_effects, startid, plugslots, stored_vals_obj):
	for n, cxf_effect in enumerate(cxf_effects):
		fxid = startid+'_'+str(n)

		plugin_obj, _, _ = do_plugin(convproj_obj, startid, cxf_effect, n, fxid, stored_vals_obj)

		if plugin_obj:
			plugin_obj.fxdata_add(not cxf_effect.bypass, 1)
			plugslots.plugin_autoplace(plugin_obj, fxid)

def do_track_common(convproj_obj, track_obj, cxf_track, stored_vals_obj):
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
		if name == 'volume': do_automation(convproj_obj, cxf_auto, ['track', cxf_track.id, 'vol'], stored_vals_obj)
		if name == 'pan': do_automation(convproj_obj, cxf_auto, ['track', cxf_track.id, 'pan'], stored_vals_obj)
		
	do_effects(convproj_obj, cxf_track.effects, cxf_track.id, track_obj.plugslots, stored_vals_obj)
