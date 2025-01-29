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
from functions.juce import juce_memoryblock

def do_visual(cvpj_visual, zb_visual, color_index, colordata):
	cvpj_visual.name = zb_visual.name
	if color_index != -1:
		colorfloat = colordata.getcolornum(color_index)
		cvpj_visual.color.set_float(colorfloat)

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
		print(val, p.position)

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

			break

		if rack.signal_chain:
			strprocs = rack.signal_chain.stream_processors
			for strproc in strprocs:
				if strproc.plugin:
					pluginid = strproc.uid
					#print(strproc.stream_processor_type, strproc.plugin.name)
					plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'native', strproc.plugin.name)
					if strproc.stream_processor_type == 4:
						plugin_obj.role = 'synth'
						track_obj.plugslots.set_synth(pluginid)
					if strproc.stream_processor_type == 3:
						plugin_obj.role = 'effect'
						track_obj.plugslots.slots_audio.append(pluginid)

					if strproc.plugin.name == 'ZC1':
						if strproc.plugin_xml_data is not None:
							plugin_xml_data = strproc.plugin_xml_data
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

						for zb_note in zb_pattern.notes:
							note_dur = max(zb_note.end-zb_note.start, 0)
							placement_obj.notelist.add_r(zb_note.start, note_dur, zb_note.semitone-60, zb_note.velocity/127, None)
	
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