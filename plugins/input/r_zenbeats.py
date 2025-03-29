# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import struct
import os.path
import math
from objects import globalstore
from objects import colors
from functions import xtramath
from functions import data_xml
from functions.juce import juce_memoryblock

def do_visual(cvpj_visual, zb_visual, color_index, colordata):
	cvpj_visual.name = zb_visual.name
	if color_index != -1:
		colorfloat = colordata.getcolornum(color_index)
		cvpj_visual.color.set_int(colorfloat)

def do_auto(convproj_obj, autoloc, curve, parammode):
	valtype = 'float'
	if parammode == 1: valtype = 'bool'
	if parammode == 2: valtype = 'bool'
	for p in curve.points:
		if parammode == 0: val = p.value
		if parammode == 1: val = p.value>0.5
		if parammode == 2: val = p.value<0.5
		if parammode == 3: val = (p.value-0.5)*2
		convproj_obj.automation.add_autopoint(autoloc, valtype, p.position, val, 'normal')

filter_types = {
	'1': 'low_pass',
	'2': 'high_pass',
	'3': 'band_pass',
	'4': 'notch'
}

def set_filter_type(filter_obj, num):
	if num in filter_types: filter_obj.type.set(filter_types[num], None)

def param_find(plugin_obj, cvpjname, xmldata, xmlname, add, mul):
	paramdata = data_xml.find_first(xmldata, 'Gain')
	if paramdata is not None:
		paramval = float(paramdata.get('value'))
		if paramval is not None:
			param_obj = plugin_obj.params.add(cvpjname, (paramval+add)*mul, 'float')

def get_value(xmldata, xmlname, fallbackv):
	paramdata = data_xml.find_first(xmldata, xmlname)
	if paramdata is not None:
		paramval = float(paramdata.get('value'))
		return paramval if paramval is not None else fallbackv
	else: return fallbackv

def do_plugin(convproj_obj, strproc, track_obj):
	pluginid = strproc.uid
	plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', strproc.plugin.name)
	if strproc.stream_processor_type == 4:
		plugin_obj.role = 'synth'
		track_obj.plugslots.set_synth(pluginid)
	if strproc.stream_processor_type == 3:
		plugin_obj.role = 'effect'
		track_obj.plugslots.slots_audio.append(pluginid)

	plugin_xml_data = strproc.plugin_xml_data

	if plugin_xml_data is not None:
		if strproc.plugin.name == 'ZC1':
			attrib = plugin_xml_data.attrib
			if 'voice_count' in attrib: 
				plugin_obj.poly.max = int(attrib['voice_count'])
			if 'mod_wheel_value' in attrib: 
				plugin_obj.datavals.add('mod_wheel_value', float(attrib['mod_wheel_value']))
			for x_part in plugin_xml_data:
				if x_part.tag == 'zn':
					for x_inpart in x_part:
						if x_inpart.tag == 'state':
							extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, pluginid)
							try: 
								statedata = juce_memoryblock.fromJuceBase64Encoding(x_inpart.text)
								extmanu_obj.vst2__import_presetdata('raw', statedata, None)
							except: pass

		# Native

		# Universal

		if strproc.plugin.format == 'StageLight':

			if strproc.plugin.name == 'Zenbeats EQ':
				plugin_obj.type_set('universal', 'eq', 'bands')
				xmlparams = data_xml.find_first(plugin_xml_data, 'RolandEQ')
				if xmlparams is not None:
					attribvals = xmlparams.attrib

					filter_obj, filterid = plugin_obj.eq_add()
					filter_obj.type.set('peak', None)
					if 'LoEnable' in attribvals: filter_obj.on = bool(float(attribvals['LoEnable']))
					if 'LoFreq' in attribvals: filter_obj.freq = float(attribvals['LoFreq'])
					if 'LoGain' in attribvals: filter_obj.gain = float(attribvals['LoGain'])
					if 'LoQ' in attribvals: filter_obj.q = float(attribvals['LoQ'])

					filter_obj, filterid = plugin_obj.eq_add()
					filter_obj.type.set('peak', None)
					if 'LoMidEnable' in attribvals: filter_obj.on = bool(float(attribvals['LoMidEnable']))
					if 'LoMidFreq' in attribvals: filter_obj.freq = float(attribvals['LoMidFreq'])
					if 'LoMidGain' in attribvals: filter_obj.gain = float(attribvals['LoMidGain'])
					if 'LoMidQ' in attribvals: filter_obj.q = float(attribvals['LoMidQ'])

					filter_obj, filterid = plugin_obj.eq_add()
					filter_obj.type.set('peak', None)
					if 'MidEnable' in attribvals: filter_obj.on = bool(float(attribvals['MidEnable']))
					if 'MidFreq' in attribvals: filter_obj.freq = float(attribvals['MidFreq'])
					if 'MidGain' in attribvals: filter_obj.gain = float(attribvals['MidGain'])
					if 'MidQ' in attribvals: filter_obj.q = float(attribvals['MidQ'])

					filter_obj, filterid = plugin_obj.eq_add()
					filter_obj.type.set('peak', None)
					if 'HiMidEnable' in attribvals: filter_obj.on = bool(float(attribvals['HiMidEnable']))
					if 'HiMidFreq' in attribvals: filter_obj.freq = float(attribvals['HiMidFreq'])
					if 'HiMidGain' in attribvals: filter_obj.gain = float(attribvals['HiMidGain'])
					if 'HiMidQ' in attribvals: filter_obj.q = float(attribvals['HiMidQ'])

					filter_obj, filterid = plugin_obj.eq_add()
					filter_obj.type.set('peak', None)
					if 'HiEnable' in attribvals: filter_obj.on = bool(float(attribvals['HiEnable']))
					if 'HiFreq' in attribvals: filter_obj.freq = float(attribvals['HiFreq'])
					if 'HiGain' in attribvals: filter_obj.gain = float(attribvals['HiGain'])
					if 'HiQ' in attribvals: filter_obj.q = float(attribvals['HiQ'])

			if strproc.plugin.name == 'Zenbeats Limiter':
				plugin_obj.type_set('universal', 'limiter', None)
				xmlparams = data_xml.find_first(plugin_xml_data, 'ZBLimiter')
				if xmlparams is not None:
					attribvals = xmlparams.attrib

					if 'Release' in attribvals:
						plugin_obj.params.add('release', float(attribvals['Release'])/100, 'float')
					if 'Threshold' in attribvals:
						plugin_obj.params.add('threshold', float(attribvals['Threshold']), 'float')
					if 'Ceiling' in attribvals:
						plugin_obj.params.add('ceiling', float(attribvals['Ceiling']), 'float')
	
			if strproc.plugin.name == 'Equalizer':
				plugin_obj.type_set('universal', 'eq', '8limited')
				xmlparams = data_xml.find_first(plugin_xml_data, 'Equalizer')
				if xmlparams is not None:
					for fnum in range(4):
						filterparams = data_xml.find_first(xmlparams, 'filter%i'%(fnum))
						if filterparams:
							dynamicfilter = data_xml.find_first(filterparams, 'DynamicFilter')
							if dynamicfilter:
								if fnum == 0: 
									filter_obj = plugin_obj.named_filter_add('low_shelf')
									filter_obj.type.set('low_shelf', None)
								if fnum == 1: 
									filter_obj = plugin_obj.named_filter_add('peak_1')
									filter_obj.type.set('peak', None)
								if fnum == 2: 
									filter_obj = plugin_obj.named_filter_add('peak_2')
									filter_obj.type.set('peak', None)
								if fnum == 3: 
									filter_obj = plugin_obj.named_filter_add('high_shelf')
									filter_obj.type.set('high_shelf', None)
								filter_obj.on = True
								filter_obj.freq = get_value(dynamicfilter, 'Freq%i'%(fnum+1), 10000)
								filter_obj.gain = get_value(dynamicfilter, 'Gain', 0)

			if strproc.plugin.name == 'Limiter':
				plugin_obj.type_set('universal', 'limiter', None)
				xmlparams = data_xml.find_first(plugin_xml_data, 'Limiter')
				if xmlparams is not None:
					param_find(plugin_obj, 'pregain', xmlparams, 'Gain', 0, 1)
					param_find(plugin_obj, 'release', xmlparams, 'Release', 0, 0.001)
					param_find(plugin_obj, 'threshold', xmlparams, 'Threshold', 0, 1)

			if strproc.plugin.name == 'Compressor':
				plugin_obj.type_set('universal', 'compressor', None)
				xmlparams = data_xml.find_first(plugin_xml_data, 'Compressor')
				if xmlparams is not None:
					param_find(plugin_obj, 'threshold', xmlparams, 'Threshold', 0, 1)
					param_find(plugin_obj, 'ratio', xmlparams, 'Ratio', 0, 1)
					param_find(plugin_obj, 'attack', xmlparams, 'Attack', 0, 0.001)
					param_find(plugin_obj, 'release', xmlparams, 'Release', 0, 0.001)
					param_find(plugin_obj, 'lookahead', xmlparams, 'Lookahead', 0, 0.001)
					param_find(plugin_obj, 'gain', xmlparams, 'Gain', 0, 1)
					param_find(plugin_obj, 'knee', xmlparams, 'Knee', 0, 1)

			if strproc.plugin.name == 'Limiter':
				plugin_obj.type_set('universal', 'limiter', None)
				xmlparams = data_xml.find_first(plugin_xml_data, 'Limiter')
				if xmlparams is not None:
					param_find(plugin_obj, 'pregain', xmlparams, 'Gain', 0, 1)
					param_find(plugin_obj, 'release', xmlparams, 'Release', 0, 0.001)
					param_find(plugin_obj, 'threshold', xmlparams, 'Threshold', 0, 1)
	
			if strproc.plugin.name == 'Filter':
				plugin_obj.type_set('universal', 'filter', None)
				xmlparams = data_xml.find_first(plugin_xml_data, 'Filter')
				if xmlparams is not None:
					plugin_obj.filter.on = True
					set_filter_type(plugin_obj.filter, xmlparams.get('filterType'))
					plugin_obj.filter.freq = get_value(xmlparams, 'Freq', 18007)
					plugin_obj.filter.q = get_value(xmlparams, 'Res', 1)

def do_rack(convproj_obj, project_obj, track_obj, zb_track, autoloc):

	for rack in project_obj.bank.racks:

		if rack.uid==zb_track.output_rack_uid:
			track_obj.params.add('vol', rack.gain, 'float')
			track_obj.params.add('solo', bool(rack.solo), 'bool')
			track_obj.params.add('mute', bool(rack.mute), 'bool')

			for send_track in rack.send_tracks:
				track_obj.sends.add(send_track.send_track_uid, None, send_track.send_amount)

			for curve in rack.automation_set.curves:
				if rack.uid==curve.target_object:
					if curve.target == 'DT_RACK':
						if curve.function == 'DF_POST_GAIN': do_auto(convproj_obj, autoloc+['vol'], curve, 0)
						if curve.function == 'DF_PAN': do_auto(convproj_obj, autoloc+['pan'], curve, 3)
						if curve.function == 'DF_MUTE': do_auto(convproj_obj, autoloc+['enabled'], curve, 2)
						if curve.function == 'DF_SOLO': do_auto(convproj_obj, autoloc+['solo'], curve, 1)

			if rack.signal_chain:
				strprocs = rack.signal_chain.stream_processors
	
				for strproc in strprocs:
					if strproc.plugin:
						do_plugin(convproj_obj, strproc, track_obj)
	
			break


class input_zenbeats(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'zenbeats'
	
	def get_name(self):
		return 'ZenBeats'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['song']
		in_dict['plugin_included'] = []
		in_dict['auto_types'] = ['nopl_points']
		in_dict['projtype'] = 'r'
		in_dict['audio_stretch'] = ['rate']
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop', 'loop_eq', 'loop_off', 'loop_adv', 'loop_adv_off']
		in_dict['audio_filetypes'] = ['wav']
		in_dict['plugin_ext_platforms'] = ['win']
		in_dict['fxtype'] = 'groupreturn'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import zenbeats as proj_zenbeats

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.set_timings(1, True)

		globalstore.dataset.load('zenbeats', './data_main/dataset/zenbeats.dset')
		colordata = colors.colorset.from_dataset('zenbeats', 'global', 'main')

		project_obj = proj_zenbeats.zenbeats_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.params.add('bpm', project_obj.bpm, 'float')
		convproj_obj.timesig = [project_obj.time_signature_numerator, project_obj.time_signature_denominator]

		convproj_obj.transport.loop_active = bool(project_obj.loop)
		convproj_obj.transport.loop_start = project_obj.loop_start
		convproj_obj.transport.loop_end = project_obj.loop_end
		convproj_obj.transport.current_pos = project_obj.play_start_marker

		added_samples = []

		master_id = None
		track_groups = []

		assoc_rack = {}

		for zb_track in project_obj.tracks:
			assoc_rack[zb_track.output_rack_uid] = zb_track.uid

			if zb_track.type == 258: 
				track_groups.append(zb_track.uid)
				track_obj = convproj_obj.fx__group__add(zb_track.uid)
				do_rack(convproj_obj, project_obj, track_obj, zb_track, ['group', zb_track.uid])
				do_visual(track_obj.visual, zb_track.visual, zb_track.color_index, colordata)

			if zb_track.type == 130: 
				return_obj = convproj_obj.track_master.fx__return__add(zb_track.uid)
				do_rack(convproj_obj, project_obj, return_obj, zb_track, ['return', zb_track.uid])
				do_visual(return_obj.visual, zb_track.visual, zb_track.color_index, colordata)

			if zb_track.type == 18: 
				master_id = zb_track.uid
				do_rack(convproj_obj, project_obj, convproj_obj.track_master, zb_track, ['master'])
				do_visual(convproj_obj.track_master.visual, zb_track.visual, zb_track.color_index, colordata)

		for zb_track in project_obj.tracks:
			master_id = zb_track.sub_track_master_track_uid
			if master_id in track_groups or master_id==None:
				if zb_track.type in [0, 1, 97]:
					track_obj = convproj_obj.track__add(zb_track.uid, 'instrument', 1, False)
					do_rack(convproj_obj, project_obj, track_obj, zb_track, ['track', zb_track.uid])
					do_visual(track_obj.visual, zb_track.visual, zb_track.color_index, colordata)
					if master_id: track_obj.group = master_id

					track_obj.armed.in_keys = bool(zb_track.arm_record)
					track_obj.armed.on = track_obj.armed.in_keys

					for zb_pattern in zb_track.patterns:
						placement_obj = track_obj.placements.add_notes()
						do_visual(placement_obj.visual, zb_pattern.visual, zb_pattern.color_index, colordata)
						placement_obj.time.set_startend(zb_pattern.start_beat, zb_pattern.end_beat)
						placement_obj.time.set_loop_data(zb_pattern.loop_play_start, zb_pattern.loop_start_beat, zb_pattern.loop_end_beat)

						placement_obj.muted = not zb_pattern.active
						placement_obj.locked = zb_pattern.locked

						for zb_note in zb_pattern.notes:
							pan = (zb_note.pan_linear-0.5)*2
							note_dur = max(zb_note.end-zb_note.start, 0)
							extradata = {}
							if pan: extradata['pan'] = pan
							if zb_note.probability != 1: extradata['probability'] = zb_note.probability
							if zb_note.pitch_offset != 0: extradata['finepitch'] = zb_note.pitch_offset
							placement_obj.notelist.add_r(zb_note.start, note_dur, zb_note.semitone-60, zb_note.velocity/127, extradata if extradata else None)
	
				if zb_track.type == 2:
					track_obj = convproj_obj.track__add(zb_track.uid, 'audio', 1, False)
					do_rack(convproj_obj, project_obj, track_obj, zb_track, ['track', zb_track.uid])
					do_visual(track_obj.visual, zb_track.visual, zb_track.color_index, colordata)
					if master_id: track_obj.group = master_id

					track_obj.armed.in_audio = bool(zb_track.arm_record)
					track_obj.armed.on = track_obj.armed.in_audio

					for zb_pattern in zb_track.patterns:
						placement_obj = track_obj.placements.add_audio()
						do_visual(placement_obj.visual, zb_pattern.visual, zb_pattern.color_index, colordata)
						placement_obj.time.set_startend(zb_pattern.start_beat, zb_pattern.end_beat)
						placement_obj.time.set_loop_data(zb_pattern.loop_play_start, zb_pattern.loop_start_beat, zb_pattern.loop_end_beat)

						placement_obj.muted = not zb_pattern.active
						placement_obj.locked = zb_pattern.locked

						if zb_pattern.audio_file:
							if zb_pattern.audio_file not in added_samples:
								sampleref_obj = convproj_obj.sampleref__add(zb_pattern.audio_file, zb_pattern.audio_file, None)
								sampleref_obj.search_local(os.path.dirname(dawvert_intent.input_file))
								added_samples.append(zb_pattern.audio_file)
	
							sp_obj = placement_obj.sample
							sp_obj.sampleref = zb_pattern.audio_file
							speedrate = zb_pattern.preserve_pitch if zb_pattern.preserve_pitch is not None else 1
							if zb_pattern.preserve_pitch: speedrate *= 120/zb_pattern.audio_file_original_bpm
							sp_obj.stretch.set_rate_tempo(project_obj.bpm, speedrate, False)
							sp_obj.stretch.algorithm = 'stretch'
							sp_obj.stretch.preserve_pitch = True
							if zb_pattern.audio_pitch is not None: sp_obj.pitch += math.log2(1/zb_pattern.audio_pitch)*-12
							if zb_pattern.audio_gain is not None: sp_obj.vol = zb_pattern.audio_gain
							if zb_pattern.audio_pan is not None: sp_obj.pan = zb_pattern.audio_pan
							if zb_pattern.reverse_audio is not None: sp_obj.reverse = zb_pattern.reverse_audio
							if zb_pattern.preserve_pitch is not None: sp_obj.stretch.preserve_pitch = bool(zb_pattern.preserve_pitch)

				#else:
				#	print(zb_track.type, zb_track.visual.name)

		#exit()