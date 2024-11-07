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
logger_output = logging.getLogger('output')

def make_volpan_plugin(convproj_obj, track_obj, iddat, wf_track, startn):
	from objects.file_proj import proj_waveform
	wf_plugin = proj_waveform.waveform_plugin()
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
	from objects.file_proj import proj_waveform
	wf_plugin = proj_waveform.waveform_plugin()
	wf_plugin.plugtype = 'level'
	wf_plugin.enabled = 1
	wf_track.plugins.append(wf_plugin)

def add_auto_curves(convproj_obj, autoloc, wf_plugin, param_id):
	from objects.file_proj import proj_waveform
	if_found, autopoints = convproj_obj.automation.get_autopoints(autoloc)
	if if_found:
		autopoints.remove_instant()
		autocurve_obj = proj_waveform.waveform_automationcurve()
		autocurve_obj.paramid = param_id
		autocurve_obj.points = [[x.pos_real, x.value, None] for x in autopoints]
		wf_plugin.automationcurves.append(autocurve_obj)

def get_plugin(convproj_obj, cvpj_fxid, isinstrument):
	from objects.file_proj import proj_waveform
	from objects.inst_params import juce_plugin

	plugin_found, plugin_obj = convproj_obj.plugin__get(cvpj_fxid)
	if plugin_found: 
		fx_on, fx_wet = plugin_obj.fxdata_get()
		if plugin_obj.check_wildmatch('external', 'vst2', None):
			juceobj = juce_plugin.juce_plugin()
			juceobj.from_cvpj(convproj_obj, plugin_obj)
			fourid = plugin_obj.datavals_global.get('fourid', None)

			if fourid: 
				fx_on, fx_wet = plugin_obj.fxdata_get()
				wf_plugin = proj_waveform.waveform_plugin()
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
			wf_plugin = proj_waveform.waveform_plugin()
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
		wf_plugin = proj_waveform.waveform_plugin()
		wf_plugin.plugtype = '4osc'
		wf_plugin.presetDirty = 1
		return wf_plugin

def get_plugins(convproj_obj, wf_plugins, cvpj_fxids):
	for cvpj_fxid in cvpj_fxids:
		wf_plugin = get_plugin(convproj_obj, cvpj_fxid, False)
		if wf_plugin:
			wf_plugins.append(wf_plugin)

def make_group(convproj_obj, groupid, groups_data, counter_id, wf_maintrack):
	from objects.file_proj import proj_waveform
	if groupid not in groups_data:
		group_obj = convproj_obj.fx__group__get(groupid)
		if group_obj:
			wf_foldertrack = proj_waveform.waveform_foldertrack()
			wf_foldertrack.id_num = counter_id.get()
			wf_maintrack.append(wf_foldertrack)
			if group_obj.visual.name: wf_foldertrack.name = group_obj.visual.name
			if group_obj.visual.color: wf_foldertrack.colour ='ff'+group_obj.visual.color.get_hex()
			get_plugins(convproj_obj, wf_foldertrack.plugins, group_obj.fxslots_audio)
			make_volpan_plugin(convproj_obj, group_obj, groupid, wf_foldertrack, 'group')
			make_level_plugin(wf_foldertrack)
			groups_data[groupid] = wf_foldertrack

class output_waveform_edit(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'output'
	def get_name(self): return 'Waveform Edit'
	def get_shortname(self): return 'waveform_edit'
	def gettype(self): return 'r'
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'tracktionedit'
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv']
		in_dict['time_seconds'] = True
		in_dict['audio_stretch'] = ['rate']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['plugin_included'] = ['native:tracktion']
		in_dict['plugin_ext'] = ['vst2']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['projtype'] = 'r'
	def parse(self, convproj_obj, output_file):
		from objects.file_proj import proj_waveform
		global dataset

		convproj_obj.change_timings(4, True)

		globalstore.dataset.load('waveform', './data_main/dataset/waveform.dset')

		project_obj = proj_waveform.waveform_edit()
		project_obj.appVersion = "Waveform 11.5.18"
		project_obj.modifiedBy = "DawVert"

		bpm = convproj_obj.params.get('bpm', 140).value
		tempomul = 120/bpm

		project_obj.temposequence.tempo[0] = [bpm, 1]
		project_obj.temposequence.timesig[0] = convproj_obj.timesig

		counter_id = counter.counter(1000, '')

		get_plugins(convproj_obj, project_obj.masterplugins, convproj_obj.track_master.fxslots_audio)

		groups_data = {}

		for groupid, insidegroup in convproj_obj.group__iter_inside():
			wf_tracks = project_obj.tracks

			if insidegroup: 
				make_group(convproj_obj, groupid, groups_data, counter_id, groups_data[insidegroup].tracks)
			else:
				make_group(convproj_obj, groupid, groups_data, counter_id, wf_tracks)

		for trackid, track_obj in convproj_obj.track__iter():
			wf_tracks = project_obj.tracks

			if track_obj.group: wf_tracks = groups_data[track_obj.group].tracks

			wf_track = proj_waveform.waveform_track()
			wf_track.id_num = counter_id.get()
			if track_obj.visual.name: wf_track.name = track_obj.visual.name
			if track_obj.visual.color: wf_track.colour ='ff'+track_obj.visual.color.get_hex()
			
			wf_inst_plugin = get_plugin(convproj_obj, track_obj.inst_pluginid, True)
			middlenote = track_obj.datavals.get('middlenote', 0)

			plugin_found, plugin_obj = convproj_obj.plugin__get(track_obj.inst_pluginid)
			if plugin_found: middlenote += plugin_obj.datavals_global.get('middlenotefix', 0)

			if middlenote != 0:
				wf_plugin = proj_waveform.waveform_plugin()
				wf_plugin.plugtype = 'midiModifier'
				wf_plugin.presetDirty = 1
				wf_plugin.params['semitonesUp'] = -middlenote
				wf_track.plugins.append(wf_plugin)

			if wf_inst_plugin: wf_track.plugins.append(wf_inst_plugin)

			get_plugins(convproj_obj, wf_track.plugins, track_obj.fxslots_audio)

			for notespl_obj in track_obj.placements.pl_notes:
				wf_midiclip = proj_waveform.waveform_midiclip()
				wf_midiclip.id_num = counter_id.get()

				offset, loopstart, loopend = notespl_obj.time.get_loop_data()

				wf_midiclip.start = notespl_obj.time.position_real
				wf_midiclip.length = notespl_obj.time.duration_real

				if notespl_obj.time.cut_type == 'cut':
					wf_midiclip.offset = (offset/8)*tempomul
				elif notespl_obj.time.cut_type in ['loop', 'loop_off', 'loop_adv']:
					wf_midiclip.offset = (offset/8)*tempomul
					wf_midiclip.loopStartBeats = (loopstart/4)
					wf_midiclip.loopLengthBeats = (loopend/4)

				if notespl_obj.visual.name: wf_midiclip.name = notespl_obj.visual.name
				if notespl_obj.visual.color: wf_midiclip.colour = 'ff'+notespl_obj.visual.color.get_hex()
				wf_midiclip.mute = int(notespl_obj.muted)

				notespl_obj.notelist.sort()
				for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
					for t_key in t_keys:
						wf_note = proj_waveform.waveform_note()
						wf_note.key = t_key+60
						wf_note.pos = t_pos/4
						wf_note.dur = t_dur/4
						wf_note.vel = int(xtramath.clamp(t_vol*127, 0, 127))
						wf_midiclip.sequence.notes.append(wf_note)

				wf_track.midiclips.append(wf_midiclip)

			make_volpan_plugin(convproj_obj, track_obj, trackid, wf_track, 'track')
			make_level_plugin(wf_track)

			wf_tracks.append(wf_track)

		project_obj.save_to_file(output_file)