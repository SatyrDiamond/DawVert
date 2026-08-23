# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import numpy as np
from functions import xtramath
from objects import globalstore
from objects import colors
from external.easybinrw import easybinrw
import os

def conv_color(b_color):
	color = b_color.to_bytes(4, "little")
	return [color[2],color[1],color[0]]

def do_visual(track_obj, track, track_node, colorset):
	track_obj.visual.name = str(track_node.name)
	if 'Farb' in track.additional_attributes:
		farbcolor = track.additional_attributes['Farb']
		try:
			color_get = colorset[farbcolor]['Color']
			track_obj.visual.color.set_int(conv_color(color_get))
		except:
			pass

def do_params(track_obj, track_device):
	if 'Volume' in track_device.deviceattributes:
		voldata = track_device.deviceattributes['Volume']
		track_obj.params.add('vol', voldata['Value']/25856, 'float')
	if 'Panner' in track_device.deviceattributes:
		pandata = track_device.deviceattributes['Panner']
		if 'audioComponent' in pandata:
			ebrw_readstr = easybinrw.binread()
			ebrw_readstr.load_data(pandata['audioComponent'])
			pandata = ebrw_readstr.float()
			track_obj.params.add('pan', (pandata-0.5)*2, 'float')

def do_autopoints(convproj_obj, autoloc, auto_node, v_min, v_max, instant):
	auto_obj = convproj_obj.automation.create(autoloc, 'float' if not instant else 'bool', True)
	if 'Events' in auto_node:
		autoevents = auto_node['Events']
		if not instant:
			for x in autoevents:
				auto_obj.add_autopoint(x.start, xtramath.between_from_one(v_min, v_max, x.value), None)
		else:
			for x in autoevents:
				auto_obj.add_autopoint(x.start, xtramath.between_from_one(v_min, v_max, x.value), 'instant')

def do_auto(track_obj, convproj_obj, seq_automation, autoloc_start, proj_sequel):
	globalids = proj_sequel.globalids
	for autotrack in seq_automation.tracks:
		nodeid = autotrack.node.idnum
		trackdeviceid = autotrack.track_device.idnum

		auto_node = None
		auto_device = None
		if nodeid in globalids: auto_node = globalids[nodeid]
		if trackdeviceid in globalids: auto_device = globalids[trackdeviceid]
		trackflags = autotrack.trackflags
		
		if auto_node is not None and auto_device is not None:
			con_type = auto_device['Connection Type']
			#dev_name = auto_device['Device Name'] if 'Device Name' in auto_device else None

			if con_type==2 and trackflags==0:
				do_autopoints(convproj_obj, autoloc_start+['vol'], auto_node, 0, 1, False)
			if con_type==2 and trackflags==1:
				do_autopoints(convproj_obj, autoloc_start+['enabled'], auto_node, 0, 1, True)
			if con_type==7 and trackflags==2:
				do_autopoints(convproj_obj, autoloc_start+['pan'], auto_node, 1, -1, False)
			#print(con_type, trackflags)

def do_effect_param(ebrw_readstr):
	name = ebrw_readstr.string(128)
	unkv = ebrw_readstr.int_u32()
	value = ebrw_readstr.double()
	return name, value

native_names = {}
native_names['001DCD3345D14A13B59DAECF75A37536'] = 'stereodelay'
native_names['1CA6E894E4624F73ADEB29CD01DDE9EE'] = 'autopan'
native_names['25B0872DB12B44B89E32ABBC1D0B3D8A'] = 'morphfilter'
native_names['341FC589831D46A7A506BC0799E882AE'] = 'chorus'
native_names['37A3AA84E3A24D069C39030EC68768E1'] = 'pingpongdelay'
native_names['3B660266B3CA4B57BBD487AE1E6C0D2A'] = 'gate'
native_names['44A0C349905B45D0B97C72D2C6F5B565'] = 'maximizer'
native_names['54B0BB1DD40B4222BE4E876A87430F64'] = 'rotary'
native_names['56535452655642726F6F6D776F726B73'] = 'reverb'
native_names['5B38F28281144FFE80285FF7CCF20483'] = 'compressor'
native_names['6143DAECD6184AE2A570FE9F35065E24'] = 'dualfilter'
native_names['77BBA7CA90F14C9BB298BA9010D6DD78'] = 'stereoenhancer'
native_names['A990C1062CDE43839ECEF8FE91743DA5'] = 'distortion'
native_names['B11C7FF1D1C04E1CB83892F669540710'] = 'vibrato'
native_names['DDE3D98C0F22423AA2B32486ABEB2846'] = 'phaser'
native_names['E4B91D8420B74C48A8B10F2DB9CB707E'] = 'ampsimulator'
native_names['E97A6873690F40E986F3EE1007B5C8FC'] = 'tremolo'
native_names['FDD7243578EF434A833705ECC4E4CE46'] = 'flanger'

def do_plugin(plugslots, slot, convproj_obj, issynth):
	if 'State' in slot:
		if slot['State']:
			PluginisA = str(slot['Plugin isA'])
			if PluginisA == 'VstCtrlInternalEffect':
				plugin = slot['Plugin']
				if 'Plugin UID' in plugin:
					if 'GUID' in plugin['Plugin UID']:
						guid = str(plugin['Plugin UID']['GUID'])
						IDString = str(plugin['IDString'])

						plugin_obj = None

						if guid in native_names:
							plugname = native_names[guid]

							plugin_obj = convproj_obj.plugin__add(IDString, 'native', 'sequel', plugname)

							ebrw_readstr = easybinrw.binread()
							ebrw_readstr.load_data(plugin['audioComponent'])
		
							sizemaybe = ebrw_readstr.int_u32()

							params = {}
							while ebrw_readstr.remaining():
								name, value = do_effect_param(ebrw_readstr)
								params[name] = value

							if 'bypass' in params:
								plugin_obj.fxdata_add(not bool(params['bypass']), None)
							
							for param_id, dset_param in globalstore.datapack.get_params('sequel', 'fx_plugin', plugname):
								paramval = params[param_id] if param_id in params else dset_param.defv
								plugin_obj.params.add(param_id, paramval, 'float')

						else:
							plugin_obj = convproj_obj.plugin__add(IDString, 'external', 'vst3', None)
							extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, IDString)
							plugin_obj.external_info.name = plugin['Plugin Name']
							extmanu_obj.vst3__replace_data('id', guid, plugin['audioComponent'], None)

						if plugin_obj: 
							if not issynth: plugin_obj.role = 'fx'
							else: plugin_obj.role = 'synth' 

						if not issynth: plugslots.slots_audio.append(IDString)
						else: plugslots.set_synth(IDString)

def do_effects(track_obj, track_device, convproj_obj):
	deviceattributes = track_device.deviceattributes
	#if 'hasEQ' in deviceattributes:
	#	if deviceattributes['hasEQ']:
	#		if 'EQ' in deviceattributes:
	#			seq_eq = deviceattributes['EQ']

	#			plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'eq', 'bands')
	#			plugin_obj.role = 'effect'
	#			track_obj.plugslots.slots_audio.append(pluginid)

	#			eqbands = seq_eq['Band']
	#			for num, band in enumerate(eqbands):
	#				filter_obj, filter_id = plugin_obj.eq_add()
	#				filter_obj.on = bool(band['Enable'])
	#				filter_obj.gain = band['Gain']
	#				filter_obj.type.set('peak', None)
	#				filter_obj.freq = band['Freq']
	#				#filter_obj.q = 1/(band['Q']/0.08851316571235657)
	#				if band['Type']:
	#					if num==0: filter_obj.type.set('high_pass', None)
	#					elif num==(len(eqbands)-1): filter_obj.type.set('low_pass', None)

	if 'InsertFolder' in deviceattributes:
		insertfolder = deviceattributes['InsertFolder']
		if 'Slot' in insertfolder:
			insertslots = insertfolder['Slot']
			for slot in insertslots:
				do_plugin(track_obj.plugslots, slot, convproj_obj, 0)

class input_sequel3(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'sequel3'
	
	def get_name(self):
		return 'Steinberg Sequel 2+'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_past import cubasexml as proj_sequel
		from objects import audio_data

		samplefolder = dawvert_intent.path_samples['extracted']

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'

		traits_obj = convproj_obj.traits
		traits_obj.audio_stretch = ['warp', 'rate']
		traits_obj.audio_filetypes = ['wav']
		traits_obj.auto_types = ['nopl_points']
		traits_obj.notes_midi = True
		traits_obj.placement_cut = True
		traits_obj.track_arranger = True
		traits_obj.notepl_pitch = True

		project_obj = proj_sequel.sequel_project()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		seq_project = project_obj.obj_project
		obj_devices = project_obj.obj_devices.data
		data_root = seq_project.data_root
		project_attributes = data_root.additional_attributes
		colorset = project_attributes['EvCo'] if 'EvCo' else project_attributes

		timebase = 480
		convproj_obj.set_timings(timebase)

		globalids = proj_sequel.globalids

		if 'Transport' in obj_devices:
			Transport = obj_devices['Transport']
			if 'Cycle Left' in Transport:
				if 'Time' in Transport['Cycle Left']:
					convproj_obj.transport.loop_start = Transport['Cycle Left']['Time']
			if 'Cycle Right' in Transport:
				if 'Time' in Transport['Cycle Right']:
					convproj_obj.transport.loop_end = Transport['Cycle Right']['Time']


		tempoid = data_root.tempo_track.idnum
		if tempoid in globalids:
			tempo_track = proj_sequel.get_object(globalids[tempoid])
			convproj_obj.params.add('bpm', tempo_track.rehearsaltempo, 'float')
			#for tempoevent in tempo_track.tempoevent:
			#	convproj_obj.automation.add_autotick(['main', 'bpm'], 'float', 0, tempoevent.bpm)

		tracklist = data_root.node
		for num, track in enumerate(tracklist.tracks):
			tracknum = 'track_'+str(num)

			if isinstance(track, proj_sequel.class_MPlayRangeTrackEvent):
				track_node = track.node
				for event in track_node.events:
					timemarker_obj = convproj_obj.arranger.add()
					timemarker_obj.time.set_posdur(event.start, event.length)
					timemarker_obj.type = 'region'
					timemarker_obj.visual.name = str(event.name)
					if 'Farb' in event.additional_attributes:
						farbcolor = event.additional_attributes['Farb']
						try: timemarker_obj.visual.color.set_int(conv_color(colorset[farbcolor]['Color']))
						except: pass

			if isinstance(track, proj_sequel.class_MDeviceTrackEvent):
				track_node = track.node
				track_device = track.track_device
				deviceattributes = track_device.deviceattributes

				busuid = 0

				if 'OwnInputBus' in deviceattributes:
					OwnInputBus = deviceattributes['OwnInputBus']
					if 'Bus UID' in OwnInputBus and 'Bus Type' in OwnInputBus:
						if OwnInputBus['Bus Type'] == 17:
							busuid = OwnInputBus['Bus UID']

				if busuid:
					return_obj = convproj_obj.track_master.fx__return__add('return_'+str(busuid))
					do_visual(return_obj, track, track_node, colorset)
					do_params(return_obj, track_device)

			if isinstance(track, proj_sequel.class_MInstrumentTrackEvent):
				track_node = track.node
				track_device = track.track_device

				track_obj = convproj_obj.track__add(tracknum, 'instrument', 1, False)
				do_visual(track_obj, track, track_node, colorset)
				do_params(track_obj, track_device)
				do_effects(track_obj, track_device, convproj_obj)
				do_auto(track_obj, convproj_obj, track.automation, ['track', tracknum], proj_sequel)
				deviceattributes = track_device.deviceattributes

				do_plugin(track_obj.plugslots, deviceattributes['Synth Slot'], convproj_obj, 1)

				for event in track_node.events:
					placement_obj = track_obj.placements.add_midi()
					delaystart = -min(event.offset, 0)
					realoffset = max(event.offset, 0)

					placement_obj.time.set_posdur(event.start, event.length+delaystart)
					placement_obj.time.set_offset(realoffset)
					placement_obj.pitch = event.transpose

					events_obj = placement_obj.midievents
					events_obj.has_duration = True
					events_obj.ppq = int(convproj_obj.time_ppq)

					if event.node_idnum in globalids:
						mmidipart = proj_sequel.get_object(globalids[event.node_idnum])
						placement_obj.visual.name = str(mmidipart.name)

						for event in mmidipart.events:
							startpos = max(0, event.start)+delaystart
							if isinstance(event, proj_sequel.class_MMidiNote):
								events_obj.add_note_dur_off_vel(startpos, 0, event.data1, event.data2, event.length, event.data3)
							elif isinstance(event, proj_sequel.class_MMidiController):
								events_obj.add_control(startpos, 0, event.data1, event.data2)
							elif isinstance(event, proj_sequel.class_MMidiPitchBend):
								events_obj.add_pitch_hi_lo(startpos, 0, event.data2, event.data1)
							elif isinstance(event, proj_sequel.class_MMidiAfterTouch):
								events_obj.add_chan_pressure(startpos, 0, event.data1)

			if isinstance(track, proj_sequel.class_MAudioTrackEvent):
				track_node = track.node
				track_device = track.track_device

				track_obj = convproj_obj.track__add(tracknum, 'audio', 1, False)
				do_visual(track_obj, track, track_node, colorset)
				do_params(track_obj, track_device)
				do_effects(track_obj, track_device, convproj_obj)
				do_auto(track_obj, convproj_obj, track.automation, ['track', tracknum], proj_sequel)
				deviceattributes = track_device.deviceattributes

				#if 'SendFolder' in deviceattributes:
				#	SendFolder = deviceattributes['SendFolder']
				#	if 'Slot' in SendFolder:
				#		for slot in SendFolder['Slot']:
				#			if 'Output' in slot:
				#				returnid = 'return_'+str(slot['Output']['Value'])
				#				track_obj.sends.add(returnid, None, 1)

				for event in track_node.events:
					placement_obj = track_obj.placements.add_audio()

					placement_obj.time.set_posdur(event.start, event.length)
					placement_obj.time.set_offset(event.offset)
					if event.clip_idnum in globalids:
						paudioclip = proj_sequel.get_object(globalids[event.clip_idnum])
						placement_obj.visual.name = str(paudioclip.name)

						if isinstance(paudioclip.path, proj_sequel.class_FNPath):
							audiopath = paudioclip.path
						if isinstance(paudioclip.path, proj_sequel.obj_pointer):
							audiopath = proj_sequel.get_object(globalids[paudioclip.path.idnum])
						filepath = str(audiopath.path)+str(audiopath.name)

						if event.flags == 2: placement_obj.muted = True

						sp_obj = placement_obj.sample
						sp_obj.vol = event.volume

						additional_attributes = event.additional_attributes
						if 'PitF' in additional_attributes:
							pitch = xtramath.speed_to_pitch(additional_attributes['PitF'])
							sp_obj.pitch = pitch
						if 'TransposeLock' in additional_attributes:
							sp_obj.usemasterpitch = not bool(paudioclip.additional_attributes['TransposeLock'])

						audiocluster = paudioclip.cluster.substreams

						if audiocluster:
							audiofile = audiocluster[0]
							partapath = audiopath

							afilepath = str(partapath.path)+str(partapath.name) if partapath else filepath
							sampleref_obj = convproj_obj.sampleref__add(afilepath, afilepath, None)
							sampleref_obj.search_local(dawvert_intent.input_folder)
							sampleref_obj.set_hz(audiofile.rate)
							sampleref_obj.set_dur_samples(audiofile.framecount)
							sampleref_obj.set_channels(audiofile.channels)

							#sampleref_obj.search_local(dawvert_intent.input_folder)
							sp_obj.sampleref = filepath
							#for event in maudioevent.events:
	
							stretch_obj = sp_obj.stretch
							s_timing_obj = stretch_obj.timing
					
							stretch_obj.preserve_pitch = True

							is_rate = False
							if paudioclip.domain.dtype == 10:
								placement_obj.time.set_dur_real(event.length/audiofile.rate)
								placement_obj.time.set_offset(event.offset/audiofile.rate)
								s_timing_obj.set__speed(1)
								is_rate = True
							else:
								if 'Warpscale' in paudioclip.additional_attributes:
									Warpscale = paudioclip.additional_attributes['Warpscale']
	
									with s_timing_obj.setup_warp(True) as warp_obj:
										dur_sec = sampleref_obj.get_dur_sec()
										hz = sampleref_obj.get_hz()
										dur_samples = sampleref_obj.get_dur_samples()
										if dur_sec: warp_obj.seconds = dur_sec
										for x in Warpscale.warptab:
											warp_pos = x.warped/timebase
											warp_sec = x.position/hz
											warp_obj.points__add_beatsec(warp_pos, warp_sec)

							if 'StretchPreset' in paudioclip.additional_attributes:
								StretchPreset = paudioclip.additional_attributes['StretchPreset']
								stretch_algo = stretch_obj.algorithm
								if isinstance(StretchPreset, proj_sequel.class_ElastiquePreset):
									stretch_algo.type = 'elastique_v3'
									stretch_algo.preserve_formants = int(bool(StretchPreset.formantpreservation))
									stretch_obj.preserve_pitch = not StretchPreset.tapestylemode