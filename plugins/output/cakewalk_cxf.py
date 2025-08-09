# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import uuid
import os
import io
import logging
import zipfile
import json
from objects import globalstore
from functions import data_values
from functions import xtramath
from objects import debug

def to_color(color_obj):
	outcolor = color_obj.copy()
	if 'saturate' in outcolor.fx_allowed:
		outcolor *= 0.9
		outcolor += 0.1
		outcolor.fx_pow(0.4)
		outcolor.fx_saturate(0.2)
	return '#'+outcolor.get_hex()

def do_visual(btrack_obj, visual_obj, fallbackname):
	btrack_obj.name = visual_obj.name if visual_obj.name else fallbackname
	if visual_obj.color:
		btrack_obj.color = to_color(visual_obj.color)
		btrack_obj.colorName = 'Custom'
	else:
		btrack_obj.color = '#EEEEEE'
		btrack_obj.colorName = 'Custom'

def do_params(btrack_obj, params_obj):
	btrack_obj.isMuted = not params_obj.get('enabled', True).value
	btrack_obj.isSolo = params_obj.get('solo', False).value
	btrack_obj.volume = params_obj.get('vol', 1).value
	btrack_obj.pan = params_obj.get('pan', 0).value

def plugin_supported(plugin_obj):
	if plugin_obj.check_wildmatch('native', 'bandlab', None): return True
	if plugin_obj.check_wildmatch('external', 'vst2', None):
		if plugin_obj.external_info.fourid: return True
	#if plugin_obj.check_wildmatch('external', 'vst3', None): 
	#	if plugin_obj.external_info.id: return True

def get_pluginfileid(startid, uniqueId, num):
	filename = '%s-%i-%s.bin' % (startid.replace('-', ''), uniqueId, num)
	return '\\'.join(['Assets', 'Plugins', filename])

def do_plugin(convproj_obj, plugin_obj, pluginid, cxf_fx, ids_obj, trackid, num):
	fx_on, fx_wet = plugin_obj.fxdata_get()

	cxf_fx.bypass = not fx_on

	if plugin_obj.check_wildmatch('native', 'bandlab', None): 
		cxf_fx.format = "BandLab"
		cxf_fx.slug = plugin_obj.type.subtype
		
		dseto_obj = globalstore.dataset.get_obj('bandlab', 'fx', cxf_fx.slug)
		if dseto_obj:
			if 'uniqueId' in dseto_obj.data: cxf_fx.uniqueId = int(dseto_obj.data['uniqueId'])
			for param_id, dset_param in dseto_obj.params.iter():
				if not dset_param.noauto: 
					cxf_fx.params[param_id] = plugin_obj.params.get(param_id, dset_param.defv).value
					do_automation(convproj_obj, ['plugin', pluginid, param_id], param_id, cxf_fx.automation, ids_obj)
				else:
					cxf_fx.params[param_id] = plugin_obj.datavals.get(param_id, dset_param.defv)
		else:
			dvallist = plugin_obj.datavals.list()
			paramlist = plugin_obj.params.list()
			if dvallist:
				for param_id in dvallist:
					cxf_fx.params[param_id] = plugin_obj.datavals.get(param_id, '')
			if paramlist:
				for param_id in paramlist:
					cxf_fx.params[param_id] = plugin_obj.params.get(param_id, 0).value
					do_automation(convproj_obj, ['plugin', pluginid, param_id], param_id, cxf_fx.automation, ids_obj)

	if plugin_obj.check_wildmatch('external', 'vst2', None): 
		cxf_fx.format = "VST"
		cxf_fx.uniqueId = plugin_obj.external_info.fourid
		if plugin_obj.external_info.name: cxf_fx.name = plugin_obj.external_info.name
		extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, pluginid)
		fxpdata = extmanu_obj.vst2__export_presetdata(None)
		ids_obj.zipfile.writestr(get_pluginfileid(trackid, cxf_fx.uniqueId, num), fxpdata)
		for _, _, paramnum in convproj_obj.automation.iter_nopl_points_external(pluginid):
			do_automation(convproj_obj, ['plugin', pluginid, 'ext_param_'+str(paramnum)], str(paramnum), cxf_fx.automation, ids_obj)

	#if plugin_obj.check_wildmatch('external', 'vst3', None): 
	#	cxf_fx.format = "VST"
	#	cxf_fx.uniqueId = 3
	#	if plugin_obj.external_info.name: cxf_fx.name = plugin_obj.external_info.name
	#	extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, pluginid)
	#	fxpdata = extmanu_obj.vst3__exportstate_juce()
	#	ids_obj.zipfile.writestr(get_pluginfileid(trackid, cxf_fx.uniqueId, num), fxpdata)
	#	for _, _, paramnum in convproj_obj.automation.iter_nopl_points_external(pluginid):
	#		do_automation(convproj_obj, ['plugin', pluginid, 'ext_param_'+str(paramnum)], param_id, cxf_fx.automation, ids_obj)

def do_track_effects(btrack_obj, plugslots, convproj_obj, ids_obj):
	fx_num = 0
	for pluginid in plugslots.slots_audio:
		plugin_found, plugin_obj = convproj_obj.plugin__get(pluginid)

		if plugin_supported(plugin_obj):
			cxf_fx = btrack_obj.add_effect()
			do_plugin(convproj_obj, plugin_obj, pluginid, cxf_fx, ids_obj, btrack_obj.id, fx_num)
			fx_num += 1

def do_track_auto_params(btrackauto_obj, convproj_obj, ids_obj, autoloc):
	do_automation(convproj_obj, autoloc+['vol'], 'volume', btrackauto_obj, ids_obj)
	do_automation(convproj_obj, autoloc+['pan'], 'pan', btrackauto_obj, ids_obj)

def create_group(convproj_obj, project_obj, groupid, group_obj, ids_obj):
	group_aux = project_obj.add_auxChannel()
	group_aux.type = "AuxFolder"
	group_aux.id = ids_obj.groupids[groupid]
	group_aux.order = ids_obj.track_order.get()
	do_visual(group_aux, group_obj.visual, groupid)
	do_params(group_aux, group_obj.params)
	do_track_effects(group_aux, group_obj.plugslots, convproj_obj, ids_obj)
	do_track_auto_params(group_aux.automation, convproj_obj, ids_obj, ['group', groupid])
	group_aux.idOutput = project_obj.mainBusId
	#group_aux.idOutput = ids_obj.groupids[group_obj.group] if group_obj.group else project_obj.mainBusId

	for returnid, send_obj in group_obj.sends.data.items():
		if returnid in ids_obj.returnids:
			cxf_auxSend = group_aux.add_auxSend()
			cxf_auxSend.id = ids_obj.returnids[returnid]
			cxf_auxSend.sendLevel = send_obj.params.get('amount', 1).value
			if send_obj.sendautoid:
				do_automation(convproj_obj, ['send', send_obj.sendautoid, 'amount'], 'sendLevel', cxf_auxSend.automation, ids_obj)

def create_return(convproj_obj, project_obj, returnid, return_obj, ids_obj):
	group_bus = project_obj.add_auxChannel()
	group_bus.type = "Bus"
	group_bus.id = ids_obj.returnids[returnid]
	group_bus.order = ids_obj.track_order.get()
	do_visual(group_bus, return_obj.visual, returnid)
	do_params(group_bus, return_obj.params)
	do_track_effects(group_bus, return_obj.plugslots, convproj_obj, ids_obj)
	do_track_auto_params(group_bus.automation, convproj_obj, ids_obj, ['return', returnid])
	group_bus.idOutput = project_obj.mainBusId

def create_track(convproj_obj, project_obj, trackid, track_obj, ids_obj):
	if track_obj.type in [
	'instrument', 
	'audio'
	]:
		cxf_track = project_obj.add_track()
		cxf_track.id = ids_obj.trackids[trackid]
		if track_obj.group: 
			cxf_track.parentId = ids_obj.groupids[track_obj.group]
			cxf_track.idOutput = ids_obj.groupids[track_obj.group]
		else:
			cxf_track.idOutput = ids_obj.mainBusId
		cxf_track.order = ids_obj.track_order.get()
		do_visual(cxf_track, track_obj.visual, trackid)
		do_params(cxf_track, track_obj.params)
		do_track_effects(cxf_track, track_obj.plugslots, convproj_obj, ids_obj)
		do_track_auto_params(cxf_track.automation, convproj_obj, ids_obj, ['track', trackid])

		for returnid, send_obj in track_obj.sends.data.items():
			if returnid in ids_obj.returnids:
				cxf_auxSend = cxf_track.add_auxSend()
				cxf_auxSend.id = ids_obj.returnids[returnid]
				cxf_auxSend.sendLevel = send_obj.params.get('amount', 1).value
				if send_obj.sendautoid:
					do_automation(convproj_obj, ['send', send_obj.sendautoid, 'amount'], 'sendLevel', cxf_auxSend.automation, ids_obj)

		if track_obj.type == 'instrument':
			cxf_track.type = 'Instrument'

			inst_supported = 0

			pluginid = track_obj.plugslots.synth
			plugin_found, plugin_obj = convproj_obj.plugin__get(pluginid)
			if plugin_found:
				if plugin_obj.check_match('external', 'bandlab', 'instrument'):
					in_inst = track_obj.datavals.get('instrument', '')
					if in_inst:
						cxf_track.soundbank = in_inst
						dset_obj = globalstore.dataset.get_obj('bandlab', 'inst', in_inst)
						inst_supported = 1
				elif plugin_supported(plugin_obj):
					synth_obj = cxf_track.add_synth()
					do_plugin(convproj_obj, plugin_obj, pluginid, synth_obj, ids_obj, cxf_track.id, -1)
					inst_supported = 1

			if not inst_supported:
				midi_inst = track_obj.get_midi(convproj_obj)
				if midi_inst:
					o_midi_bank, o_midi_patch = midi_inst.to_sf2()
					if o_midi_bank != 127:
						if ids_obj.idvals_bandlab_inst:
							t_instid = ids_obj.idvals_bandlab_inst.get_idval(str(o_midi_patch), 'outid')
							if t_instid:
								dset_obj = globalstore.dataset.get_obj('bandlab', 'inst', t_instid)
								if dset_obj:
									cxf_track.soundbank = t_instid
					else:
						cxf_track.soundbank = 'general-midi-drums-v2-v4'
				else:
					inst_supported = -1

			if inst_supported == -1: 
				ids_obj.logger_output.info('track "%s" is muted because the instrument is not supported.' % trackid)
				cxf_track.isMuted = True

			for midipl_obj in track_obj.placements.pl_midi:
				midievents_obj = midipl_obj.midievents

				notebytes = midievents_obj.getvalue()
				uuiddata = str( data_values.bytes__to_uuid( notebytes ) )

				if uuiddata not in ids_obj.notelist_assoc:
					ids_obj.notelist_assoc[uuiddata] = midievents_obj
					bl_sample = project_obj.add_sample()
					bl_sample.id = uuiddata
					bl_sample.isMidi = True
					bl_sample.name = uuiddata
					bl_sample.file = uuiddata+'.mid'
					midipath = "/".join(['Assets', 'MIDI', uuiddata+'.mid'])
					ids_obj.zipfile.writestr(midipath, midievents_obj.midi_to_raw() )
					
				region_obj = cxf_track.add_region()
				add_region_common(region_obj, midipl_obj, ids_obj, 1)
				region_obj.file = uuiddata+'.mid'
				region_obj.sampleId = uuiddata

		if track_obj.type == 'audio':
			cxf_track.type = 'Audio'
			for audiopl_obj in track_obj.placements.pl_audio:
				sp_obj = audiopl_obj.sample

				ref_found, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)
				if sp_obj.sampleref not in ids_obj.sample_assoc:
					fileref_obj = sampleref_obj.fileref
					filepath = fileref_obj.get_path(None, False)
					filename = str(fileref_obj.file)

					uuiddata = str(uuid.uuid4())
					ids_obj.sample_assoc[sp_obj.sampleref] = uuiddata
					ids_obj.samplefilename_assoc[sp_obj.sampleref] = filename

					bl_sample = project_obj.add_sample()
					bl_sample.id = uuiddata
					bl_sample.isMidi = False
					bl_sample.name = uuiddata
					bl_sample.file = filename
					audiopath = "/".join(['Assets', 'Audio', filename])

					if os.path.exists(filepath) and audiopath not in ids_obj.zipfile.namelist(): 
						ids_obj.zipfile.write(filepath, audiopath)

				region_obj = cxf_track.add_region()
				region_obj.file = ids_obj.samplefilename_assoc[sp_obj.sampleref]
				region_obj.sampleId = ids_obj.sample_assoc[sp_obj.sampleref]
				if ref_found:
					region_obj.playbackRate = sp_obj.stretch.timing.get__real_rate(sampleref_obj, ids_obj.bpm)
				add_region_common(region_obj, audiopl_obj, ids_obj, 1)

def do_tracks(convproj_obj, project_obj, current_grouptab, ids_obj):
	for tracktype, tid, track_obj in current_grouptab:
		if tracktype == 'GROUP' and tid not in ids_obj.used_groups and tid in ids_obj.track_group:
			create_group(convproj_obj, project_obj, tid, track_obj, ids_obj)
			ids_obj.used_groups.append(tid)
			do_tracks(convproj_obj, project_obj, ids_obj.track_group[tid], ids_obj)
		if tracktype == 'TRACK':
			create_track(convproj_obj, project_obj, tid, track_obj, ids_obj)

class stored_vals():
	def __init__(self, convproj_obj):
		self.track_order = data_values.counter(0)
		self.songid = str(uuid.uuid4())
		self.master_returns = convproj_obj.track_master.returns
		self.groupids = dict([[x, str(uuid.uuid4())] for x in convproj_obj.groups])
		self.returnids = dict([[x, str(uuid.uuid4())] for x in self.master_returns])
		self.trackids = dict([[x, str(uuid.uuid4())] for x in convproj_obj.track_data])
		self.filename = str(uuid.uuid4())
		self.mainBusId = str(uuid.uuid4())
		self.audiodeviceid = str(uuid.uuid4())
		self.used_groups = []
		self.track_group = {}
		self.track_nongroup = []
		self.bpm = convproj_obj.params.get('bpm', 120).value
		self.tempomul = 120/self.bpm
		self.debugvis = debug.id_visual_name()
		for k, v in self.groupids.items(): self.debugvis.add(k, 'MID_AuxGroup: '+str(v))
		for k, v in self.trackids.items(): self.debugvis.add(k, 'MID_Track: '+str(v))
		self.debugvis.add(self.songid, 'songid')
		self.debugvis.add(self.filename, 'filename')
		self.debugvis.add(self.mainBusId, 'mainBusId')
		self.debugvis.add(self.audiodeviceid, 'audiodeviceid')
		self.zip_bio = io.BytesIO()
		self.zipfile = zipfile.ZipFile(self.zip_bio, mode='w', compresslevel=None)
		self.notelist_assoc = {}
		self.sample_assoc = {}
		self.samplefilename_assoc = {}
		self.idvals_bandlab_inst = globalstore.idvals.get('bandlab_midi_map')
		self.logger_output = logging.getLogger('output')
	
class output_bandlab(plugins.base):
	def is_dawvert_plugin(self):
		return 'output'
	
	def get_shortname(self):
		return 'cakewalk_cxf'
	
	def get_name(self):
		return 'Cakewalk Interchange'
	
	def gettype(self):
		return 'r'
	
	def get_prop(self, in_dict): 
		in_dict['audio_filetypes'] = ['wav']
		in_dict['audio_stretch'] = ['rate']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['notes_midi'] = True
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = []
		in_dict['time_seconds'] = False
		in_dict['plugin_included'] = ['native:bandlab']
		in_dict['file_ext'] = 'cxf'
		in_dict['fxtype'] = 'groupreturn'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import cakewalk_cxf as proj_cakewalk_cxf

		convproj_obj.change_timings(1.0)
		
		project_obj = proj_cakewalk_cxf.cxf_project()

		globalstore.dataset.load('bandlab', './data_main/dataset/bandlab.dset')
		globalstore.idvals.load('bandlab_midi_map', './data_main/idvals/bandlab_map_midi.csv')

		project_obj.stamp = 'LOCAL_XCD_'+str(uuid.uuid4())

		if convproj_obj.metadata.name: project_obj.song.name = convproj_obj.metadata.name
		if project_obj.description: project_obj.description = convproj_obj.metadata.comment_text

		ids_obj = stored_vals(convproj_obj)
		debugvis_id_store = ids_obj.debugvis
		debugvis_id_store.add(project_obj.song.id, 'Song ID')
		debugvis_id_store.add(project_obj.mainBusId, 'mainBusId')

		project_obj.song.id = ids_obj.songid
		project_obj.song.stamp = 'LOCAL_XCD_'+ids_obj.songid

		bpm = convproj_obj.params.get('bpm', 120).value
		tempomul = 120/bpm
		project_obj.metronome.bpm = bpm
		project_obj.metronome.signature = {"notesCount": 4, "noteValue": 4}

		project_obj.mainBusId = ids_obj.mainBusId

		track_master = convproj_obj.track_master

		master_bus = project_obj.add_auxChannel()
		master_bus.type = "Bus"
		master_bus.id = project_obj.mainBusId
		master_bus.order = ids_obj.track_order.get()
		do_visual(master_bus, convproj_obj.track_master.visual, 'Master')
		do_params(master_bus, convproj_obj.track_master.params)
		do_track_effects(master_bus, track_master.plugslots, convproj_obj, ids_obj)
		do_track_auto_params(master_bus.automation, convproj_obj, ids_obj, ['master'])
		master_bus.idOutput = ids_obj.audiodeviceid

		convproj_obj.fx__group__remove_unused()

		for groupid, group_obj in convproj_obj.fx__group__iter():
			if group_obj.group:
				if group_obj.group not in ids_obj.track_group: ids_obj.track_group[group_obj.group] = []
				ids_obj.track_group[group_obj.group].append(['GROUP', groupid, group_obj])
			else: ids_obj.track_nongroup.append(['GROUP', groupid, group_obj])

		for trackid, track_obj in convproj_obj.track__iter():
			if track_obj.group: 
				if track_obj.group not in ids_obj.track_group: ids_obj.track_group[track_obj.group] = []
				ids_obj.track_group[track_obj.group].append(['TRACK', trackid, track_obj])
			else: ids_obj.track_nongroup.append(['TRACK', trackid, track_obj])

		for returnid, x in ids_obj.master_returns.items():
			create_return(convproj_obj, project_obj, returnid, x, ids_obj)

		do_tracks(convproj_obj, project_obj, ids_obj.track_nongroup, ids_obj)

		jsonwrite = project_obj.write()
		if dawvert_intent.output_mode == 'file':
			ids_obj.zipfile.writestr(str(uuid.uuid4())+'.cxf', json.dumps(jsonwrite))
			ids_obj.zipfile.close()
			open(dawvert_intent.output_file, 'wb').write(ids_obj.zip_bio.getbuffer())

def do_automation(convproj_obj, autoloc, cfx_id, cfx_auto, ids_obj):
	from objects.file_proj import cakewalk_cxf as proj_cakewalk_cxf
	tempomul = ids_obj.tempomul
	ap_f, ap_d = convproj_obj.automation.get(autoloc, 'float')
	if ap_f: 
		if ap_d.u_nopl_points:
			cfx_points = cfx_auto[cfx_id] = proj_cakewalk_cxf.cxf_automation()
			ap_d.nopl_points.remove_instant()
			for autopoint in ap_d.nopl_points:
				cfx_points.add_point((autopoint.pos/2)*tempomul, autopoint.value)

def add_region_common(blx_region, audiopl_obj, ids_obj, pmod):
	time_obj = audiopl_obj.time
	tempomul = ids_obj.tempomul

	position, duration = time_obj.get_posdur()

	blx_region.startPosition = (position/2)*tempomul
	blx_region.endPosition = ((position+duration)/2)*tempomul
	blx_region.name = audiopl_obj.visual.name

	cut_type = time_obj.cut_type

	blx_region.sampleStartPosition += blx_region.startPosition

	cut_start = time_obj.get_offset()

	if cut_type == 'cut':
		blx_region.sampleOffset += ((cut_start/2)*tempomul)*pmod
