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
	from objects.file_proj import proj_tracktion_edit
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
	from objects.file_proj import proj_tracktion_edit
	wf_plugin = proj_tracktion_edit.tracktion_plugin()
	wf_plugin.plugtype = 'level'
	wf_plugin.enabled = 1
	wf_track.plugins.append(wf_plugin)

def add_auto_curves(convproj_obj, autoloc, wf_plugin, param_id):
	from objects.file_proj import proj_tracktion_edit
	if_found, autopoints = convproj_obj.automation.get_autopoints(autoloc)
	if if_found:
		autopoints.remove_instant()
		autocurve_obj = proj_tracktion_edit.tracktion_automationcurve()
		autocurve_obj.paramid = param_id
		autocurve_obj.points = [[x.pos_real, x.value, None] for x in autopoints]
		wf_plugin.automationcurves.append(autocurve_obj)

def sampler_param(bxml_obj, key, value): 
	bxml_param = bxml_obj.add_child('SOUNDPARAMETER')
	bxml_param.set('id', key)
	bxml_param.set('value', value)

def soundlayer_samplepart(plugin_obj, bxml_main, lowNote, highNote, rootNote, sp_obj, sampleref_assoc, sampleref_obj_assoc): 
	if sp_obj.sampleref in sampleref_assoc and sp_obj.sampleref in sampleref_obj_assoc:
		adsr_obj = plugin_obj.env_asdr_get('vol')
		sampleref_obj = sampleref_obj_assoc[sp_obj.sampleref]
		sp_obj.convpoints_samples(sampleref_obj)
		bxml_layer = bxml_main.add_child('SOUNDLAYER')
		bxml_layer.set('active', True)
		bxml_layer.set('name', '1')
		bxml_layer.set('reverse', bool(sp_obj.reverse))
		bxml_layer.set('sampleDataName', ':'+sampleref_assoc[sp_obj.sampleref])
		bxml_layer.set('sampleIn', int(sp_obj.start))
		bxml_layer.set('sampleLoopIn', int(sp_obj.loop_start))
		bxml_layer.set('sampleOut', int(sp_obj.end))
		bxml_layer.set('sampleLoopOut', int(sp_obj.loop_end))
		bxml_layer.set('rootNote', rootNote)
		bxml_layer.set('lowNote', lowNote)
		bxml_layer.set('highNote', highNote)
		bxml_layer.set('fineTune', 4294967289)
		bxml_layer.set('fixedPitch', False)
		bxml_layer.set('pitchShift', False)
		bxml_layer.set('looped', bool(sp_obj.loop_active))
		bxml_layer.set('loopMode', 1)
		sampler_param(bxml_layer, 'attackParam', float(adsr_obj.attack))
		sampler_param(bxml_layer, 'decayParam', float(adsr_obj.decay))
		sampler_param(bxml_layer, 'sustainParam', float(adsr_obj.sustain)*100)
		sampler_param(bxml_layer, 'releaseParam', float(adsr_obj.release))
		sampler_param(bxml_layer, 'envModeParam', float(sp_obj.trigger=='normal'))
		sampler_param(bxml_layer, 'pitchParam', float(sp_obj.pitch))

def get_plugin(convproj_obj, sampleref_assoc, sampleref_obj_assoc, cvpj_fxid, isinstrument):
	from objects.file_proj import proj_tracktion_edit
	from objects.inst_params import juce_plugin
	from objects.binary_fmt import juce_binaryxml
	from functions.juce import juce_memoryblock

	plugin_found, plugin_obj = convproj_obj.plugin__get(cvpj_fxid)

	if plugin_found: 
		fx_on, fx_wet = plugin_obj.fxdata_get()

		if plugin_obj.check_wildmatch('universal', 'sampler', None):
			wf_plugin = proj_tracktion_edit.tracktion_plugin()
			wf_plugin.plugtype = plugin_obj.type.subtype
			wf_plugin.presetDirty = 1
			wf_plugin.enabled = fx_on
			wf_plugin.params['type'] = 'vst'
			wf_plugin.params['uniqueId'] = '0'
			wf_plugin.params['uid'] = '0'
			wf_plugin.params['filename'] = 'Micro Sampler'
			wf_plugin.params['name'] = 'Micro Sampler'
			dsetfound = True

			bxml_data = juce_binaryxml.juce_binaryxml_element()
			bxml_data.tag = 'PROGRAM'
			bxml_data.set('presetDirty', True)

			bxml_main = bxml_data.add_child('TINYSAMPLER')
			bxml_main.set('version', 2)
			bxml_main.set('fxOrder1', "reverb,delay,comp,filter,eq,dist,chorus")
			bxml_main.set('fxOrder2', "delay,reverb,comp,filter,eq,dist,chorus")
			bxml_main.set('currentPage', 0)

			if plugin_obj.type.subtype == 'single':
				sp_obj = plugin_obj.samplepart_get('sample')
				soundlayer_samplepart(plugin_obj, bxml_main, 0, 127, 60, sp_obj, sampleref_assoc, sampleref_obj_assoc)
				outbytes = bxml_data.to_bytes()
				wf_plugin.params['state'] = juce_memoryblock.toJuceBase64Encoding(outbytes)
				return wf_plugin

			if plugin_obj.type.subtype == 'multi':
				for spn, sampleregion in enumerate(plugin_obj.sampleregions):
					key_l, key_h, key_r, samplerefid, extradata = sampleregion
					sp_obj = plugin_obj.samplepart_get(samplerefid)
					soundlayer_samplepart(plugin_obj, bxml_main, key_l+60, key_h+60, key_r+60, sp_obj, sampleref_assoc, sampleref_obj_assoc)
				outbytes = bxml_data.to_bytes()
				wf_plugin.params['state'] = juce_memoryblock.toJuceBase64Encoding(outbytes)
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

def get_plugins(convproj_obj, sampleref_assoc, sampleref_obj_assoc, wf_plugins, cvpj_fxids):
	for cvpj_fxid in cvpj_fxids:
		wf_plugin = get_plugin(convproj_obj, sampleref_assoc, sampleref_obj_assoc, cvpj_fxid, False)
		if wf_plugin:
			wf_plugins.append(wf_plugin)

def make_group(convproj_obj, sampleref_assoc, sampleref_obj_assoc, groupid, groups_data, counter_id, wf_maintrack):
	from objects.file_proj import proj_tracktion_edit
	if groupid not in groups_data:
		group_obj = convproj_obj.fx__group__get(groupid)
		if group_obj:
			wf_foldertrack = proj_tracktion_edit.tracktion_foldertrack()
			wf_foldertrack.id_num = counter_id.get()
			wf_maintrack.append(wf_foldertrack)
			if group_obj.visual.name: wf_foldertrack.name = group_obj.visual.name
			if group_obj.visual.color: wf_foldertrack.colour ='ff'+group_obj.visual.color.get_hex()
			get_plugins(convproj_obj, sampleref_assoc, sampleref_obj_assoc, wf_foldertrack.plugins, group_obj.plugslots.slots_audio)
			make_volpan_plugin(convproj_obj, group_obj, groupid, wf_foldertrack, 'group')
			make_level_plugin(wf_foldertrack)
			groups_data[groupid] = wf_foldertrack

class output_tracktion_edit(plugins.base):
	def is_dawvert_plugin(self):
		return 'output'
	
	def get_name(self):
		return 'Waveform Edit'
	
	def get_shortname(self):
		return 'tracktion_edit'
	
	def gettype(self):
		return 'r'
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'tracktionedit'
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_eq']
		in_dict['time_seconds'] = True
		in_dict['track_hybrid'] = True
		in_dict['audio_stretch'] = ['rate']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['plugin_included'] = ['native:tracktion','universal:sampler:single','universal:sampler:multi']
		in_dict['plugin_ext'] = ['vst2']
		in_dict['plugin_ext_arch'] = [32, 64]
		in_dict['plugin_ext_platforms'] = ['win', 'unix']
		in_dict['audio_filetypes'] = ['wav','flac','ogg','mp3']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['projtype'] = 'r'
		
	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import proj_tracktion_edit
		from objects.file_proj import proj_tracktion_project
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

		get_plugins(convproj_obj, sampleref_assoc, sampleref_obj_assoc, project_obj.masterplugins, convproj_obj.track_master.plugslots.slots_audio)

		groups_data = {}

		for groupid, insidegroup in convproj_obj.group__iter_inside():
			wf_tracks = project_obj.tracks

			if insidegroup: 
				make_group(convproj_obj, sampleref_assoc, sampleref_obj_assoc, groupid, groups_data, counter_id, groups_data[insidegroup].tracks)
			else:
				make_group(convproj_obj, sampleref_assoc, sampleref_obj_assoc, groupid, groups_data, counter_id, wf_tracks)

		for trackid, track_obj in convproj_obj.track__iter():
			wf_tracks = project_obj.tracks

			if track_obj.group: wf_tracks = groups_data[track_obj.group].tracks

			wf_track = proj_tracktion_edit.tracktion_track()
			wf_track.id_num = counter_id.get()
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
				wf_inst_plugin = get_plugin(convproj_obj, sampleref_assoc, sampleref_obj_assoc, track_obj.plugslots.synth, track_obj.type in ['instrument', 'hybrid'])
				if wf_inst_plugin:
					wf_track.plugins.append(wf_inst_plugin)

			get_plugins(convproj_obj, sampleref_assoc, sampleref_obj_assoc, wf_track.plugins, track_obj.plugslots.slots_audio)

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

				notespl_obj.notelist.sort()
				for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
					for t_key in t_keys:
						wf_note = proj_tracktion_edit.tracktion_note()
						wf_note.key = t_key+60
						wf_note.pos = t_pos/4
						wf_note.dur = max(t_dur/4, 0.01)
						wf_note.vel = int(xtramath.clamp(t_vol*127, 0, 127))
						wf_midiclip.sequence.notes.append(wf_note)

				wf_track.midiclips.append(wf_midiclip)

			for audiopl_obj in track_obj.placements.pl_audio:
				wf_audioclip = proj_tracktion_edit.tracktion_audioclip()
				wf_audioclip.id_num = counter_id.get()

				offset, loopstart, loopend = audiopl_obj.time.get_loop_data()

				wf_audioclip.start = audiopl_obj.time.position_real
				wf_audioclip.length = audiopl_obj.time.duration_real

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

				if audiopl_obj.visual.name: wf_audioclip.name = audiopl_obj.visual.name
				if audiopl_obj.visual.color: wf_audioclip.colour = 'ff'+audiopl_obj.visual.color.get_hex()
				wf_audioclip.mute = int(audiopl_obj.muted)

				sp_obj = audiopl_obj.sample
				if sp_obj.sampleref in sampleref_assoc:
					wf_audioclip.source = sampleref_assoc[sp_obj.sampleref]
					sampleref_obj = sampleref_obj_assoc[sp_obj.sampleref]

					dur_sec = sampleref_obj.dur_sec*2
					numBeats = audiopl_obj.sample.stretch.calc_tempo_size*dur_sec
					wf_audioclip.loopinfo.numBeats = numBeats

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