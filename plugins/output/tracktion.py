# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import lxml.etree as ET
from functions import xtramath
from objects import globalstore
from objects import counter
import math
import logging
import os
from random import randbytes

logger_output = logging.getLogger('output')

def gen_hexid(num):
	outv = num+randbytes(3).hex()
	while outv:
		if outv[0] == '0': outv = outv[1:]
		else: break
	return outv

def make_volpan_plugin(convproj_obj, track_obj, iddat, wf_track, startn):
	from objects.file_proj import tracktion_edit as proj_tracktion_edit
	wf_plugin = proj_tracktion_edit.tracktion_plugin()
	wf_plugin.plugtype = 'volume'
	wf_plugin.enabled = 1
	wf_plugin.presetDirty = 1
	wf_plugin.params['volume'] = track_obj.params.get('vol', 1.0).value
	wf_plugin.params['pan'] = track_obj.params.get('pan', 0).value
	add_auto_curves(convproj_obj, [startn, iddat, 'vol'], wf_plugin, 'volume')
	add_auto_curves(convproj_obj, [startn, iddat, 'pan'], wf_plugin, 'pan')
	wf_track.plugins.append(wf_plugin)
	return wf_plugin

def make_level_plugin(wf_track):
	from objects.file_proj import tracktion_edit as proj_tracktion_edit
	wf_plugin = proj_tracktion_edit.tracktion_plugin()
	wf_plugin.plugtype = 'level'
	wf_plugin.enabled = 1
	wf_track.plugins.append(wf_plugin)

def add_auto_curves(convproj_obj, autoloc, wf_plugin, param_id):
	from objects.file_proj import tracktion_edit as proj_tracktion_edit
	if_found, autopoints = convproj_obj.automation.get_autopoints(autoloc)
	if if_found:
		autopoints.remove_instant()
		autocurve_obj = proj_tracktion_edit.tracktion_automationcurve()
		autocurve_obj.paramid = param_id
		autocurve_obj.points = [[x.pos, x.value, None] for x in autopoints]
		wf_plugin.automationcurves.append(autocurve_obj)

def sampler_do_filter(soundlayer, filter_obj):
	layerparams = soundlayer.soundparameters
	layerparams['filterEnableParam'] = float(int(filter_obj.on))
	layerparams['cuttoffParam'] = filter_obj.freq

	filtertype = filter_obj.type
	i_type = filtertype.type
	i_subtype = filtertype.subtype

	outfilter = 0

	if i_type == 'low_pass':
		if filter_obj.slope>12: outfilter = 2
		elif filter_obj.slope<12: outfilter = 0
		else: outfilter = 1

	if i_type == 'band_pass':
		if filter_obj.slope>12: outfilter = 4
		else: outfilter = 3

	if i_type == 'high_pass':
		if filter_obj.slope>12: outfilter = 7
		elif filter_obj.slope<12: outfilter = 5
		else: outfilter = 6

	if i_type == 'notch':
		if filter_obj.slope>12: outfilter = 9
		else: outfilter = 8

	layerparams['filterModeParam'] = float(outfilter)

def soundlayer_samplepart(plugin_obj, gpitch, programdata, lowNote, highNote, rootNote, sp_obj, sampleref_assoc, sampleref_obj_assoc): 
	if sp_obj.sampleref in sampleref_assoc and sp_obj.sampleref in sampleref_obj_assoc:
		adsr_obj = plugin_obj.env_asdr_get(sp_obj.envs['vol'] if 'vol' in sp_obj.envs else 'vol')
		sampleref_obj = sampleref_obj_assoc[sp_obj.sampleref]
		sp_obj.convpoints_samples(sampleref_obj)
		soundlayer = programdata.add_layer()
		soundlayer.name = str(sp_obj.visual.name) if sp_obj.visual.name else sp_obj.sampleref
		soundlayer.reverse = bool(sp_obj.reverse)
		soundlayer.sampleDataName = ':'+sampleref_assoc[sp_obj.sampleref]
		soundlayer.sampleIn = int(sp_obj.start)
		soundlayer.sampleLoopIn = int(sp_obj.loop_start)
		soundlayer.sampleOut = int(sp_obj.end)
		soundlayer.sampleLoopOut = int(sp_obj.loop_end)
		soundlayer.rootNote = int(rootNote)
		soundlayer.lowNote = int(lowNote)
		soundlayer.highNote = int(highNote)
		soundlayer.looped = bool(sp_obj.loop_active)
		soundlayer.fixedPitch = bool(sp_obj.no_pitch)
		if sp_obj.stretch.preserve_pitch: soundlayer.pitchShift = True
		soundparameters = soundlayer.soundparameters
		soundparameters['attackParam'] = float(adsr_obj.attack)
		soundparameters['decayParam'] = float(adsr_obj.decay)
		soundparameters['sustainParam'] = float(adsr_obj.sustain)*100
		soundparameters['releaseParam'] = float(adsr_obj.release)
		soundparameters['envModeParam'] = float(sp_obj.trigger=='normal')
		soundparameters['pitchParam'] = float(sp_obj.pitch+gpitch)
		if 'vel_sens' in sp_obj.data: soundparameters['sensParam'] = float(sp_obj.data['vel_sens'])
		return soundlayer

def get_plugin(convproj_obj, tparams_obj, sampleref_assoc, sampleref_obj_assoc, cvpj_fxid, isinstrument):
	from objects.file_proj import tracktion_edit as proj_tracktion_edit
	from objects.file_proj._waveform import sampler
	from objects.inst_params import juce_plugin
	from objects.binary_fmt import juce_binaryxml
	from functions.juce import juce_memoryblock

	plugin_found, plugin_obj = convproj_obj.plugin__get(cvpj_fxid)

	if plugin_found: 
		fx_on, fx_wet = plugin_obj.fxdata_get()

		if plugin_obj.check_wildmatch('universal', 'sampler', None):
			gpitch = tparams_obj.get('pitch', 0).value

			if plugin_obj.type.subtype == 'single':
				wf_plugin = proj_tracktion_edit.tracktion_plugin()
				wf_plugin.plugtype = plugin_obj.type.subtype
				wf_plugin.presetDirty = 1
				wf_plugin.enabled = fx_on
				wf_plugin.params['type'] = 'vst'
				wf_plugin.params['uniqueId'] = '0'
				wf_plugin.params['uid'] = '0'
				wf_plugin.params['manufacturer'] = 'Tracktion'
				dsetfound = True

				sampler_obj = sampler.waveform_sampler_main()
				sampler_obj.program.presetDirty = True

				sp_obj = plugin_obj.samplepart_get('sample')

				if sp_obj.pitch or sp_obj.stretch.calc_real_size!=1 or plugin_obj.filter.on:
					programdata = sampler_obj.set_prosampler()
					wf_plugin.params['filename'] = 'Multi Sampler'
					wf_plugin.params['name'] = 'Multi Sampler'
				else:
					programdata = sampler_obj.set_tinysampler()
					wf_plugin.params['filename'] = 'Micro Sampler'
					wf_plugin.params['name'] = 'Micro Sampler'

				soundlayer = soundlayer_samplepart(plugin_obj, gpitch, programdata, 0, 127, 60, sp_obj, sampleref_assoc, sampleref_obj_assoc)
				if soundlayer:
					soundlayer.offlinePitchShift = sp_obj.pitch
					soundlayer.offlineTimeStretch = sp_obj.stretch.calc_real_size
					sampler_do_filter(soundlayer, plugin_obj.filter)

				wf_plugin.params['state'] = juce_memoryblock.toJuceBase64Encoding(sampler_obj.write())
				return wf_plugin

			if plugin_obj.type.subtype == 'slicer':
				wf_plugin = proj_tracktion_edit.tracktion_plugin()
				wf_plugin.plugtype = plugin_obj.type.subtype
				wf_plugin.presetDirty = 1
				wf_plugin.enabled = fx_on
				wf_plugin.params['type'] = 'vst'
				wf_plugin.params['uniqueId'] = '0'
				wf_plugin.params['uid'] = '0'
				wf_plugin.params['filename'] = 'Micro Sampler'
				wf_plugin.params['name'] = 'Micro Sampler'
				wf_plugin.params['manufacturer'] = 'Tracktion'
				dsetfound = True

				sampler_obj = sampler.waveform_sampler_main()
				sampler_obj.program.presetDirty = True
				sp_obj = plugin_obj.samplepart_get('sample')
				programdata = sampler_obj.set_tinysampler()
				if sp_obj.sampleref in sampleref_assoc and sp_obj.sampleref in sampleref_obj_assoc:
					sp_obj.add_slice_endpoints()

					samp_hz = sampleref_obj.get_hz()

					sampleref_obj = sampleref_obj_assoc[sp_obj.sampleref]
					hzmod = samp_hz/44100 if samp_hz else 1

					for n, slice_obj in enumerate(sp_obj.slicer_slices):
						key = 60+slice_obj.custom_key if slice_obj.is_custom_key else 60+n
						soundlayer = programdata.add_layer()
						soundlayer.active = True
						soundlayer.name = str(slice_obj.name) if slice_obj.name else 'Slice #'+str(n+1)
						soundlayer.reverse = bool(slice_obj.reverse)
						soundlayer.sampleDataName = ':'+sampleref_assoc[sp_obj.sampleref]
						soundlayer.sampleIn = int(slice_obj.start*hzmod)
						soundlayer.sampleOut = int(slice_obj.end*hzmod)
						soundlayer.rootNote = key
						soundlayer.lowNote = key
						soundlayer.highNote = key
				wf_plugin.params['state'] = juce_memoryblock.toJuceBase64Encoding(sampler_obj.write())
				return wf_plugin

			if plugin_obj.type.subtype == 'multi':
				wf_plugin = proj_tracktion_edit.tracktion_plugin()
				wf_plugin.plugtype = plugin_obj.type.subtype
				wf_plugin.presetDirty = 1
				wf_plugin.enabled = fx_on
				wf_plugin.params['type'] = 'vst'
				wf_plugin.params['uniqueId'] = '0'
				wf_plugin.params['uid'] = '0'
				wf_plugin.params['filename'] = 'Multi Sampler'
				wf_plugin.params['name'] = 'Multi Sampler'
				wf_plugin.params['manufacturer'] = 'Tracktion'
				dsetfound = True

				sampler_obj = sampler.waveform_sampler_main()
				sampler_obj.program.presetDirty = True
				programdata = sampler_obj.set_prosampler()

				multi_mode = plugin_obj.datavals.get('multi_mode', 'all')
				if multi_mode == 'round_robin': programdata.playMode = 1
				if multi_mode == 'random': programdata.playMode = 2
				programdata.mono = plugin_obj.poly.mono

				for spn, sampleregion in enumerate(plugin_obj.sampleregion_getall()):
					key_l, key_h, key_r, samplerefid, extradata = sampleregion
					sp_obj = plugin_obj.samplepart_get(samplerefid)
					soundlayer = soundlayer_samplepart(plugin_obj, gpitch, programdata, key_l+60, key_h+60, key_r+60, sp_obj, sampleref_assoc, sampleref_obj_assoc)
					if soundlayer:
						soundlayer.lowVelocity = int(sp_obj.vel_min*127)
						soundlayer.highVelocity = int(sp_obj.vel_max*127)
						soundlayer.offlinePitchShift = sp_obj.pitch
						soundlayer.offlineTimeStretch = sp_obj.stretch.calc_real_size
						filt_exists, filt_obj = plugin_obj.named_filter_get_exists(sp_obj.filter_assoc)
						if filt_exists: sampler_do_filter(soundlayer, filt_obj)

				wf_plugin.params['state'] = juce_memoryblock.toJuceBase64Encoding(sampler_obj.write())
				return wf_plugin

			if plugin_obj.type.subtype == 'drums':
				wf_plugin = proj_tracktion_edit.tracktion_plugin()
				wf_plugin.plugtype = plugin_obj.type.subtype
				wf_plugin.presetDirty = 1
				wf_plugin.enabled = fx_on
				wf_plugin.params['type'] = 'vst'
				wf_plugin.params['uniqueId'] = '0'
				wf_plugin.params['uid'] = '0'
				wf_plugin.params['filename'] = 'Micro Drum Sampler'
				wf_plugin.params['name'] = 'Micro Drum Sampler'
				wf_plugin.params['manufacturer'] = 'Tracktion'
				dsetfound = True

				sampler_obj = sampler.waveform_sampler_main()
				sampler_obj.program.presetDirty = True
				programdata = sampler_obj.set_microsampler()
				useddrums = []
				for spn, sampleregion in enumerate(plugin_obj.sampleregion_getall()):
					key_l, key_h, key_r, samplerefid, extradata = sampleregion
					drumkey = key_r+60
					if drumkey not in useddrums:
						sp_obj = plugin_obj.samplepart_get(samplerefid)
						soundlayer_samplepart(plugin_obj, gpitch, programdata, drumkey, drumkey, drumkey, sp_obj, sampleref_assoc, sampleref_obj_assoc)
						pad_obj = programdata.add_pad(drumkey)
						if sp_obj.visual.name: pad_obj.name = sp_obj.visual.name
						useddrums.append(drumkey)
				wf_plugin.params['state'] = juce_memoryblock.toJuceBase64Encoding(sampler_obj.write())
				return wf_plugin

		if plugin_obj.check_wildmatch('external', 'vst2', None):
			juceobj = juce_plugin.juce_plugin()
			juceobj.from_cvpj(convproj_obj, plugin_obj)
			fourid = plugin_obj.external_info.fourid

			if fourid: 
				fx_on, fx_wet = plugin_obj.fxdata_get()
				wf_plugin = proj_tracktion_edit.tracktion_plugin()
				wf_plugin.enabled = int(fx_on)
				wf_plugin.params['type'] = 'vst'
				if juceobj.name: wf_plugin.params['name'] = juceobj.name
				if juceobj.filename: wf_plugin.params['filename'] = juceobj.filename
				if juceobj.manufacturer: wf_plugin.params['manufacturer'] = juceobj.manufacturer
				if juceobj.fourid: 
					wf_plugin.params['uniqueId'] = f'{juceobj.fourid:x}'
					wf_plugin.params['uid'] = f'{juceobj.fourid:x}'
				wf_plugin.params['state'] = juceobj.memoryblock

				for _, _, paramnum in convproj_obj.automation.iter_nopl_points_external(cvpj_fxid):
					add_auto_curves(convproj_obj, ['plugin', cvpj_fxid, 'ext_param_'+str(paramnum)], wf_plugin, str(paramnum))
					
				return wf_plugin

			else:
				logger_output.warning('VST2 plugin not placed: no ID found.')

		if plugin_obj.check_wildmatch('native', 'tracktion', None):
			wf_plugin = proj_tracktion_edit.tracktion_plugin()
			wf_plugin.plugtype = plugin_obj.type.subtype
			wf_plugin.presetDirty = 1
			wf_plugin.enabled = fx_on
			dsetfound = False
			for param_id, dset_param in globalstore.dataset.get_params('waveform', 'plugin', wf_plugin.plugtype):
				wf_plugin.params[param_id] = plugin_obj.params.get(param_id, dset_param.defv).value
				add_auto_curves(convproj_obj, ['plugin', cvpj_fxid, param_id], wf_plugin, param_id)
				dsetfound = True

			if dsetfound == False:
				paramlist = plugin_obj.params.list()
				if paramlist:
					for param_id in paramlist:
						wf_plugin.params[param_id] = plugin_obj.params.get(param_id, 0).value
						add_auto_curves(convproj_obj, ['plugin', cvpj_fxid, param_id], wf_plugin, param_id)
			return wf_plugin

			

	elif isinstrument:
		wf_plugin = proj_tracktion_edit.tracktion_plugin()
		wf_plugin.plugtype = '4osc'
		wf_plugin.presetDirty = 1
		return wf_plugin

def get_plugins(convproj_obj, tparams_obj, sampleref_assoc, sampleref_obj_assoc, wf_plugins, cvpj_fxids):
	for cvpj_fxid in cvpj_fxids:
		wf_plugin = get_plugin(convproj_obj, tparams_obj, sampleref_assoc, sampleref_obj_assoc, cvpj_fxid, False)
		if wf_plugin:
			wf_plugins.append(wf_plugin)

def make_group(convproj_obj, sampleref_assoc, sampleref_obj_assoc, groupid, groups_data, counter_id, wf_maintrack):
	from objects.file_proj import tracktion_edit as proj_tracktion_edit
	if groupid not in groups_data:
		group_obj = convproj_obj.fx__group__get(groupid)
		if group_obj:
			wf_foldertrack = proj_tracktion_edit.tracktion_foldertrack()
			wf_foldertrack.id_num = counter_id.get()
			wf_foldertrack.height = group_obj.visual_ui.height*35.41053828354546
			wf_maintrack.append(wf_foldertrack)
			if group_obj.visual.name: wf_foldertrack.name = group_obj.visual.name
			if group_obj.visual.color: wf_foldertrack.colour ='ff'+group_obj.visual.color.get_hex()
			get_plugins(convproj_obj, group_obj.params, sampleref_assoc, sampleref_obj_assoc, wf_foldertrack.plugins, group_obj.plugslots.slots_audio)
			make_volpan_plugin(convproj_obj, group_obj, groupid, wf_foldertrack, 'group')
			make_level_plugin(wf_foldertrack)
			groups_data[groupid] = wf_foldertrack

class output_tracktion_edit(plugins.base):
	def is_dawvert_plugin(self):
		return 'output'
	
	def get_name(self):
		return 'Waveform Pro'
	
	def get_shortname(self):
		return 'waveform'
	
	def gettype(self):
		return 'r'
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'tracktionedit'
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_eq']
		in_dict['time_seconds'] = True
		in_dict['track_hybrid'] = True
		in_dict['audio_stretch'] = ['rate', 'warp']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['plugin_included'] = ['native:tracktion','universal:sampler:single','universal:sampler:multi','universal:sampler:slicer','universal:sampler:drums']
		in_dict['plugin_ext'] = ['vst2']
		in_dict['plugin_ext_arch'] = [32, 64]
		in_dict['plugin_ext_platforms'] = ['win', 'unix']
		in_dict['audio_filetypes'] = ['wav','flac','ogg','mp3']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['projtype'] = 'r'
		
	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import tracktion_edit as proj_tracktion_edit
		from objects.file_proj import tracktion_project as proj_tracktion_project
		global dataset

		convproj_obj.change_timings(4, True)

		tr_projectid = gen_hexid('1')
		tr_editid = gen_hexid('2')

		globalstore.dataset.load('waveform', './data_main/dataset/waveform.dset')

		mainp_obj = proj_tracktion_project.tracktion_project()
		mainp_obj.projectId = tr_projectid
		mainp_obj.props = {'name': convproj_obj.metadata.name, 'description': ''}

		sampleref_assoc = {}
		sampleref_obj_assoc = {}

		for sampleref_id, sampleref_obj in convproj_obj.sampleref__iter():
			tr_waveid = gen_hexid('3')
			wave_obj = mainp_obj.objects[tr_waveid] = proj_tracktion_project.tracktion_project_object()
			wave_obj.name = sampleref_obj.fileref.file.filename if sampleref_obj.fileref.file.filename else ''
			wave_obj.type = 'wave'
			wave_obj.path = sampleref_obj.fileref.get_path(None, False)
			wave_obj.info = "Imported|MediaObjectCategory|5"
			wave_obj.id2 = '40120000'
			sampleref_assoc[sampleref_id] = tr_projectid+'/'+tr_waveid
			sampleref_obj_assoc[sampleref_id] = sampleref_obj
			
		edit_obj = mainp_obj.objects[tr_editid] = proj_tracktion_project.tracktion_project_object()
		edit_obj.name = 'Converted Edit'
		edit_obj.type = 'edit'
		edit_obj.info = '(Created as the default edit for this project)|MediaObjectCategory|1'

		if dawvert_intent.output_mode == 'file':
			basename = os.path.basename(dawvert_intent.output_file)
			filename = os.path.splitext(basename)[0]
			projfolder = os.path.dirname(dawvert_intent.output_file)
			projfolder = os.path.abspath(projfolder)
			edit_obj.path = basename
			mainp_obj.save_to_file(os.path.join(projfolder, filename+'.tracktion'))

		project_obj = proj_tracktion_edit.tracktion_edit()
		project_obj.appVersion = "Waveform 11.5.18"
		project_obj.modifiedBy = "DawVert"
		project_obj.projectID = tr_projectid+'/'+tr_editid

		bpm = convproj_obj.params.get('bpm', 140).value
		tempomul = 120/bpm

		project_obj.temposequence.tempo[0] = [bpm, 1]
		project_obj.temposequence.timesig[0] = convproj_obj.timesig

		transport_obj = project_obj.transport

		transport_obj.looping = int(convproj_obj.transport.loop_active)
		transport_obj.loopPoint1 = float(convproj_obj.transport.loop_start)
		transport_obj.loopPoint2 = float(convproj_obj.transport.loop_end)
		transport_obj.start = float(convproj_obj.transport.start_pos)
		transport_obj.position = float(convproj_obj.transport.current_pos)

		counter_id = counter.counter(1000, '')

		get_plugins(convproj_obj, convproj_obj.params, sampleref_assoc, sampleref_obj_assoc, project_obj.masterplugins, convproj_obj.track_master.plugslots.slots_audio)

		groups_data = {}

		for groupid, insidegroup in convproj_obj.group__iter_inside():
			wf_tracks = project_obj.tracks

			if insidegroup: 
				make_group(convproj_obj, sampleref_assoc, sampleref_obj_assoc, groupid, groups_data, counter_id, groups_data[insidegroup].tracks)
			else:
				make_group(convproj_obj, sampleref_assoc, sampleref_obj_assoc, groupid, groups_data, counter_id, wf_tracks)

		groupassoc = {}
		groupcounter = 20000

		for trackid, track_obj in convproj_obj.track__iter():
			wf_tracks = project_obj.tracks

			if track_obj.group: wf_tracks = groups_data[track_obj.group].tracks

			wf_track = proj_tracktion_edit.tracktion_track()
			wf_track.id_num = counter_id.get()
			wf_track.height = track_obj.visual_ui.height*35.41053828354546

			if track_obj.visual.name: wf_track.name = track_obj.visual.name
			if track_obj.visual.color: wf_track.colour ='ff'+track_obj.visual.color.get_hex()
			
			middlenote = track_obj.datavals.get('middlenote', 0)

			plugin_found, plugin_obj = convproj_obj.plugin__get(track_obj.plugslots.synth)
			if plugin_found: middlenote += plugin_obj.datavals_global.get('middlenotefix', 0)

			if middlenote != 0:
				wf_plugin = proj_tracktion_edit.tracktion_plugin()
				wf_plugin.plugtype = 'midiModifier'
				wf_plugin.presetDirty = 1
				wf_plugin.params['semitonesUp'] = -middlenote
				wf_track.plugins.append(wf_plugin)

			if track_obj.plugslots.synth:
				wf_inst_plugin = get_plugin(convproj_obj, track_obj.params, sampleref_assoc, sampleref_obj_assoc, track_obj.plugslots.synth, track_obj.type in ['instrument', 'hybrid'])
				if wf_inst_plugin:
					wf_track.plugins.append(wf_inst_plugin)

			get_plugins(convproj_obj, track_obj.params, sampleref_assoc, sampleref_obj_assoc, wf_track.plugins, track_obj.plugslots.slots_audio)

			for notespl_obj in track_obj.placements.pl_notes:
				wf_midiclip = proj_tracktion_edit.tracktion_midiclip()
				wf_midiclip.id_num = counter_id.get()

				offset, loopstart, loopend = notespl_obj.time.get_loop_data()

				wf_midiclip.start = notespl_obj.time.position_real
				wf_midiclip.length = notespl_obj.time.duration_real

				boffset = (offset/8)*tempomul
				toffset = (offset/4)*tempomul

				if notespl_obj.time.cut_type == 'cut':
					wf_midiclip.offset = boffset
				elif notespl_obj.time.cut_type == 'loop_eq':
					wf_midiclip.offset = 0
					wf_midiclip.loopStartBeats = toffset
					wf_midiclip.loopLengthBeats = (loopend/4)-toffset
				elif notespl_obj.time.cut_type in ['loop', 'loop_off']:
					wf_midiclip.offset = boffset
					wf_midiclip.loopStartBeats = (loopstart/4)
					wf_midiclip.loopLengthBeats = (loopend/4)

				if notespl_obj.visual.name: wf_midiclip.name = notespl_obj.visual.name
				if notespl_obj.visual.color: wf_midiclip.colour = 'ff'+notespl_obj.visual.color.get_hex()
				wf_midiclip.mute = int(notespl_obj.muted)

				if notespl_obj.group:
					groupidtr = trackid+'_'+notespl_obj.group
					if groupidtr not in groupassoc:
						groupassoc[groupidtr] = groupcounter
						groupcounter += 1
					wf_midiclip.groupID = groupassoc[groupidtr]

				notespl_obj.notelist.sort()
				for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_autopack in notespl_obj.notelist.iter():
					for t_key in t_keys:
						notepitch = 0
						if t_extra:
							if 'finepitch' in t_extra:
								notepitch = t_extra['finepitch']
						wf_note = proj_tracktion_edit.tracktion_note()
						wf_note.key = t_key+60
						wf_note.pos = t_pos/4
						wf_note.dur = max(t_dur/4, 0.01)
						wf_note.vel = int(xtramath.clamp(t_vol*127, 0, 127))
						if notepitch:
							nautop = wf_note.auto['PITCHBEND'] = {}
							nautop[0] = notepitch/100
						wf_midiclip.sequence.notes.append(wf_note)

				wf_track.midiclips.append(wf_midiclip)

			for audiopl_obj in track_obj.placements.pl_audio:
				wf_audioclip = proj_tracktion_edit.tracktion_audioclip()
				wf_audioclip.id_num = counter_id.get()

				wf_audioclip.start = audiopl_obj.time.position_real
				wf_audioclip.length = audiopl_obj.time.duration_real

				wf_audioclip.fadeIn = audiopl_obj.fade_in.get_dur_seconds(bpm)
				wf_audioclip.fadeOut = audiopl_obj.fade_out.get_dur_seconds(bpm)

				if audiopl_obj.visual.name: wf_audioclip.name = audiopl_obj.visual.name
				if audiopl_obj.visual.color: wf_audioclip.colour = 'ff'+audiopl_obj.visual.color.get_hex()
				wf_audioclip.mute = int(audiopl_obj.muted)

				if audiopl_obj.group:
					groupidtr = trackid+'_'+audiopl_obj.group
					if groupidtr not in groupassoc:
						groupassoc[groupidtr] = groupcounter
						groupcounter += 1
					wf_audioclip.groupID = groupassoc[groupidtr]

				sp_obj = audiopl_obj.sample
				stretch_obj = audiopl_obj.sample.stretch
				if sp_obj.sampleref in sampleref_assoc:
					wf_audioclip.source = sampleref_assoc[sp_obj.sampleref]
					sampleref_obj = sampleref_obj_assoc[sp_obj.sampleref]

					if stretch_obj.is_warped:
						warp_obj = stretch_obj.warp

						stretch_amt = warp_obj.speed

						numBeats = stretch_amt*warp_obj.seconds*2
						wf_audioclip.loopinfo.numBeats = numBeats

						loffset = warp_obj.get__offset()
						warpmove = max(0, loffset)

						audiopl_obj.time.cut_start += warpmove*4
						if audiopl_obj.time.cut_type == 'none':
							audiopl_obj.time.cut_type = 'cut'

						warp_obj.points__add__based_beat(0)
						warp_obj.fix__last()
						warp_obj.fix__fill()
						warp_obj.fix__round()

						warp_obj.manp__shift_beats(warpmove)

						warp_obj.fix__alwaysplus()
						warp_obj.fix__remove_dupe_sec()
						warp_obj.fix__sort()

						afx = proj_tracktion_edit.tracktion_audioclip_fx() 
						afx.fx_type = 'warpTime'
						warptime = afx.warptime = proj_tracktion_edit.tracktion_warptime()
						warptime.warpEndMarkerTime = warp_obj.seconds

						for num, warp_point_obj in enumerate(warp_obj.points__iter()):
							if warp_point_obj.beat>=0 and warp_point_obj.second>=0:
								warpmarker = proj_tracktion_edit.tracktion_warpmarker()
								warpmarker.warpTime = (warp_point_obj.beat/stretch_amt)/2
								warpmarker.sourceTime = warp_point_obj.second
								warptime.warpmarkers.append(warpmarker)

						wf_audioclip.effects.append(afx)
					else:
						dur_sec = sampleref_obj.get_dur_sec()
						if dur_sec:
							dur_sec = dur_sec*2
							numBeats = stretch_obj.calc_tempo_size*dur_sec
							wf_audioclip.loopinfo.numBeats = numBeats

				offset, loopstart, loopend = audiopl_obj.time.get_loop_data()

				boffset = (offset/8)*tempomul
				toffset = (offset/4)*tempomul

				if audiopl_obj.time.cut_type == 'cut':
					wf_audioclip.offset = boffset
				elif audiopl_obj.time.cut_type == 'loop_eq':
					wf_audioclip.offset = 0
					wf_audioclip.loopStartBeats = toffset
					wf_audioclip.loopLengthBeats = (loopend/4)-toffset
				elif audiopl_obj.time.cut_type in ['loop', 'loop_off']:
					wf_audioclip.offset = boffset
					wf_audioclip.loopStartBeats = (loopstart/4)
					wf_audioclip.loopLengthBeats = (loopend/4)

				wf_audioclip.gain = xtramath.to_db(sp_obj.vol)
				wf_audioclip.pan = sp_obj.pan

				if sp_obj.pitch != 0:
					afx = proj_tracktion_edit.tracktion_audioclip_fx()
					afx.fx_type = 'pitchShift'
					afx.plugin.plugtype = "pitchShifter"
					afx.plugin.params['semitonesUp'] = sp_obj.pitch
					wf_audioclip.effects.append(afx)

				if sp_obj.reverse:
					afx = proj_tracktion_edit.tracktion_audioclip_fx()
					afx.fx_type = 'reverse'
					wf_audioclip.effects.append(afx)

				wf_track.audioclips.append(wf_audioclip)

			make_volpan_plugin(convproj_obj, track_obj, trackid, wf_track, 'track')
			make_level_plugin(wf_track)

			wf_tracks.append(wf_track)

		if dawvert_intent.output_mode == 'file':
			project_obj.save_to_file(dawvert_intent.output_file)