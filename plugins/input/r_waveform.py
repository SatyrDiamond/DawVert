# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore
from lxml import etree
from objects import counter
import plugins
import json
import math

def sampler_get_size(sampler_data):
	sampler_data.magic_check(b'\x01')
	sizedata = sampler_data.uint8()
	return sizedata

def sampler_decode_chunk(sampler_data):
	chunk_name = sampler_data.string_t()
	chunk_size = sampler_get_size(sampler_data)-1
	chunk_type = sampler_data.uint8()
	if chunk_type == 1: chunk_data = sampler_data.uint32()
	elif chunk_type == 2: chunk_data = True
	elif chunk_type == 3: chunk_data = False
	elif chunk_type == 4: chunk_data = sampler_data.double()
	elif chunk_type == 5: chunk_data = sampler_data.string(chunk_size)
	else: chunk_data = [chunk_type, sampler_data.raw(chunk_size)]
	return chunk_name, chunk_data

def sampler_decode_dict(sampler_data, indict):
	set_name = sampler_data.string_t()
	set_num = sampler_get_size(sampler_data)
	dictpart = {}
	for _ in range(set_num):
		chunk_name, chunk_data = sampler_decode_chunk(sampler_data)
		dictpart[chunk_name] = chunk_data
	indict[set_name] = dictpart
	return set_name, dictpart

def sampler_parse(indata): 
	from objects.data_bytes import bytereader
	sampler_data = bytereader.bytereader()
	sampler_data.load_raw(indata)
	sampleheader = {}
	sampler_decode_dict(sampler_data, sampleheader)
	sampler_get_size(sampler_data)
	sampler_decode_dict(sampler_data, sampleheader)
	sampler_get_size(sampler_data)
	sampledata = []
	while sampler_data.remaining():
		sampledata.append(sampler_decode_dict(sampler_data, {}))
		sampler_data.skip(1)
	return sampleheader, sampledata

def soundlayer_samplepart(sp_obj, soundlayer): 
	sp_obj.visual.name = soundlayer['name'] if 'name' in soundlayer else ''
	sp_obj.point_value_type = 'samples'
	if 'sampleDataName' in soundlayer: sp_obj.sampleref = soundlayer['sampleDataName']
	if 'sampleIn' in soundlayer: sp_obj.start = soundlayer['sampleIn']
	if 'sampleOut' in soundlayer: sp_obj.end = soundlayer['sampleOut']
	if 'reverse' in soundlayer: sp_obj.reverse = soundlayer['reverse']
	if 'lowVelocity' in soundlayer: sp_obj.vel_min = soundlayer['lowVelocity']/127
	if 'highVelocity' in soundlayer: sp_obj.vel_max = soundlayer['highVelocity']/127
	if 'sampleLoopIn' in soundlayer: sp_obj.loop_start = soundlayer['sampleLoopIn']
	if 'sampleLoopOut' in soundlayer: sp_obj.loop_end = soundlayer['sampleLoopOut']
	if 'looped' in soundlayer: sp_obj.loop_active = soundlayer['looped']

def do_plugin(convproj_obj, wf_plugin, track_obj): 
	from functions_plugin import juce_memoryblock

	if wf_plugin.plugtype == 'vst':
		vstname = wf_plugin.params['name'] if "name" in wf_plugin.params else ''

		if vstname in ['Micro Sampler', 'Micro Drum Sampler']:
			try:
				chunkdata = juce_memoryblock.fromJuceBase64Encoding(wf_plugin.params['state']) if "state" in wf_plugin.params else b''
				sampleheader, sampledata = sampler_parse(chunkdata)
				soundlayers = []
				for wf_smpl_part, wf_smpl_data in sampledata:
					if wf_smpl_part == 'SOUNDLAYER': soundlayers.append(wf_smpl_data)
				if len(soundlayers)>1:
					plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'multi')
					track_obj.inst_pluginid = pluginid
					for soundlayer in soundlayers:
						sl_rootNote = soundlayer['rootNote'] if 'rootNote' in soundlayer else 60
						sl_lowNote = soundlayer['lowNote'] if 'lowNote' in soundlayer else 60
						sl_highNote = soundlayer['highNote'] if 'highNote' in soundlayer else 60
						sp_obj = plugin_obj.sampleregion_add(sl_lowNote-60, sl_highNote-60, sl_rootNote-60, None)
						soundlayer_samplepart(sp_obj, soundlayer)
				elif len(soundlayers)==1:
					soundlayer = soundlayers[0]
					plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'single')
					track_obj.inst_pluginid = pluginid
					sp_obj = plugin_obj.samplepart_add('sample')
					soundlayer_samplepart(sp_obj, soundlayer)
			except:
				pass
		else:
			try:
				from objects.inst_params import juce_plugin
				juceobj = juce_plugin.juce_plugin()
				juceobj.uniqueId = wf_plugin.params['uniqueId'] if "uniqueId" in wf_plugin.params else ''
				juceobj.name = wf_plugin.params['name'] if "name" in wf_plugin.params else ''
				juceobj.filename = wf_plugin.params['filename'] if "filename" in wf_plugin.params else ''
				juceobj.manufacturer = wf_plugin.params['manufacturer'] if "manufacturer" in wf_plugin.params else ''
				juceobj.memoryblock = wf_plugin.params['state']
	
				plugin_obj, pluginid = juceobj.to_cvpj(convproj_obj, None)
				plugin_obj.fxdata_add(bool(wf_plugin.enabled), None)
	
				track_obj.plugin_autoplace(plugin_obj, pluginid)
	
				if pluginid:
					if wf_plugin.windowX and wf_plugin.windowY:
						windata_obj = convproj_obj.viswindow__add(['plugin',pluginid])
						windata_obj.pos_x = wf_plugin.windowX
						windata_obj.pos_y = wf_plugin.windowY

					for autocurves in wf_plugin.automationcurves:
						if autocurves.paramid:
							for time, val, curve in autocurves.points:
								convproj_obj.automation.add_autopoint_real(['plugin',pluginid,'ext_param_'+autocurves.paramid], 'float', time, val, 'normal')

			except:
				pass

	elif wf_plugin.plugtype not in ['volume', 'level'] and wf_plugin.plugtype != '':
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('native', 'tracktion', wf_plugin.plugtype)
		plugin_obj.role = 'effect'
		plugin_obj.fxdata_add(wf_plugin.enabled, None)

		if wf_plugin.windowX and wf_plugin.windowY:
			windata_obj = convproj_obj.viswindow__add(['plugin',pluginid])
			windata_obj.pos_x = wf_plugin.windowX
			windata_obj.pos_y = wf_plugin.windowY

		for param_id, dset_param in globalstore.dataset.get_params('waveform', 'plugin', wf_plugin.plugtype):
			paramval = wf_plugin.params[param_id] if param_id in wf_plugin.params else None
			plugin_obj.dset_param__add(param_id, paramval, dset_param)

		for autocurves in wf_plugin.automationcurves:
			if autocurves.paramid:
				for time, val, curve in autocurves.points:
					convproj_obj.automation.add_autopoint_real(['plugin',pluginid,autocurves.paramid], 'float', time, val, 'normal')

		plugin_obj.fxdata_add(wf_plugin.enabled, 1)
		if wf_plugin.plugtype not in ['4osc']: track_obj.fxslots_audio.append(pluginid)
		else: track_obj.inst_pluginid = pluginid

autonames = {
	'PITCHBEND': 'pitch',
	'TIMBRE': 'timbre',
	'PRESSURE': 'pressure',
}

def do_foldertrack(convproj_obj, wf_track, counter_track): 
	groupid = str(wf_track.id_num)
	track_obj = convproj_obj.fx__group__add(groupid)
	track_obj.visual.name = wf_track.name
	track_obj.visual.color.set_hex(wf_track.colour)
	track_obj.visual_ui.height = wf_track.height/35.41053828354546

	vol = 1
	pan = 0

	for wf_plugin in wf_track.plugins:
		if wf_plugin.plugtype == 'volume':
			if 'volume' in wf_plugin.params: vol *= wf_plugin.params['volume']
			if 'pan' in wf_plugin.params: pan = wf_plugin.params['pan']

			for autocurves in wf_plugin.automationcurves:
				if autocurves.paramid == 'volume':
					for time, val, curve in autocurves.points:
						convproj_obj.automation.add_autopoint_real(['group',groupid,'vol'], 'float', time, val, 'normal')

				if autocurves.paramid == 'pan':
					for time, val, curve in autocurves.points:
						convproj_obj.automation.add_autopoint_real(['group',groupid,'pan'], 'float', time, val, 'normal')

		else:
			do_plugin(convproj_obj, wf_plugin, track_obj)

	track_obj.params.add('vol', vol, 'float')
	track_obj.params.add('pan', pan, 'float')
	do_tracks(convproj_obj, wf_track.tracks, counter_track, groupid)

def do_track(convproj_obj, wf_track, track_obj): 
	track_obj.visual.name = wf_track.name
	track_obj.visual.color.set_hex(wf_track.colour)
	track_obj.visual_ui.height = wf_track.height/35.41053828354546

	vol = 1
	pan = 0

	middlenote = 0

	for wf_plugin in wf_track.plugins:
		if wf_plugin.plugtype == 'volume':
			if 'volume' in wf_plugin.params: vol *= wf_plugin.params['volume']
			if 'pan' in wf_plugin.params: pan = wf_plugin.params['pan']

		elif wf_plugin.plugtype == 'midiModifier':
			if 'semitonesUp' in wf_plugin.params: middlenote -= int(wf_plugin.params['semitonesUp'])

		else:
			do_plugin(convproj_obj, wf_plugin, track_obj)

	track_obj.params.add('vol', vol, 'float')
	track_obj.params.add('pan', pan, 'float')
	track_obj.params.add('enabled', int(not wf_track.mute), 'bool')
	track_obj.params.add('solo', wf_track.solo, 'bool')

	for midiclip in wf_track.midiclips:
		placement_obj = track_obj.placements.add_notes()

		placement_obj.time.position_real = midiclip.start
		placement_obj.time.duration_real = midiclip.length
		if midiclip.loopStartBeats == 0 and midiclip.loopLengthBeats == 0:
			placement_obj.time.set_offset(midiclip.offset)
		else:
			placement_obj.cut_loop_data(midiclip.offset, midiclip.loopStartBeats, midiclip.loopStartBeats+midiclip.loopLengthBeats)
	
		for note in midiclip.sequence.notes:
			placement_obj.notelist.add_r(note.pos*4, note.dur*4, note.key-60, note.vel/100, {})
			for a_type, a_data in note.auto.items():
				autoname = autonames[a_type] if a_type in autonames else None
				if autoname:
					for pos, val in a_data.items():
						autopoint_obj = placement_obj.notelist.last_add_auto(autoname)
						autopoint_obj.pos = pos*4
						autopoint_obj.value = val
						autopoint_obj.type = 'instant'

	track_obj.datavals.add('middlenote', middlenote)

def do_tracks(convproj_obj, in_tracks, counter_track, groupid):
	from objects.file_proj import proj_waveform
	for wf_track in in_tracks:
		tracknum = counter_track.get()
		if isinstance(wf_track, proj_waveform.waveform_track):
			track_obj = convproj_obj.track__add(str(tracknum), 'instrument', 1, False)
			if groupid: track_obj.group = groupid
			do_track(convproj_obj, wf_track, track_obj)
		if isinstance(wf_track, proj_waveform.waveform_foldertrack):
			do_foldertrack(convproj_obj, wf_track, counter_track)


class input_cvpj_f(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'waveform_edit'
	def get_name(self): return 'Waveform'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['tracktionedit']
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv']
		in_dict['time_seconds'] = True
		in_dict['audio_stretch'] = ['rate']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['plugin_included'] = ['native:tracktion']
		in_dict['plugin_ext'] = ['vst2', 'vst3']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['projtype'] = 'r'
	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_waveform
		global cvpj_l

		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		globalstore.dataset.load('waveform', './data_main/dataset/waveform.dset')

		project_obj = proj_waveform.waveform_edit()
		if not project_obj.load_from_file(input_file): exit()

		if project_obj.temposequence.tempo:
			pos, tempo = next(iter(project_obj.temposequence.tempo.items()))
			convproj_obj.params.add('bpm', tempo[0], 'float')
			for pos, tempo in project_obj.temposequence.tempo.items():
				convproj_obj.automation.add_autopoint_real(['main', 'bpm'], 'float', pos, tempo[0], 'normal')

		if project_obj.temposequence.timesig:
			pos, timesig = next(iter(project_obj.temposequence.timesig.items()))
			convproj_obj.timesig = timesig
			for pos, timesig in project_obj.temposequence.timesig.items():
				convproj_obj.timesig_auto.add_point(pos, timesig)

		for wf_plugin in project_obj.masterplugins:
			do_plugin(convproj_obj, wf_plugin, convproj_obj.track_master)

		tracknum = 0
		counter_track = counter.counter(1000, '')

		do_tracks(convproj_obj, project_obj.tracks, counter_track, None)