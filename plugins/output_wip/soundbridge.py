# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import struct
import os
import numpy as np
import base64
from objects import globalstore
from functions import data_values
from functions import xtramath
from objects.data_bytes import bytewriter
import shutil
import logging

logger_output = logging.getLogger('output')

sb_notes_dtype = np.dtype([('id', '>I'),('pos', '>I'),('dur', '>I'),('key', 'B'),('vol', 'B'),('unk1', 'B'),('unk2', 'B')])

native_names = {}
native_names['eq'] = ['2ed34074c14566409f62442c8545929f', 'ZPlane', 'EQ']
native_names['filter_unit'] = ['544d1ae3e2c91548b932574932c83885', 'ZPlane', 'Filter Unit']
native_names['analyzer'] = ['1423f146b5fcaa40904b2c3fe24495fa', 'ZPlane', 'Analyzer']
native_names['chorus_flanger'] = ['f487b09e6f329a41b2cfc280068079a4', 'ZPlane', 'Chorus/Flanger']
native_names['delay'] = ['0d47d236d52df342bf3b8635a4b89f07', 'ZPlane', 'Delay']
native_names['phaser'] = ['b2a57c0cc1996d468f38a87332010bc9', 'ZPlane', 'Phaser']
native_names['reverb'] = ['8f64f7b97060ca449e89456f9a2684d0', 'ZPlane', 'Reverb']
native_names['bit_crusher'] = ['2793169f4a4b554087755fafff91b3e9', 'ZPlane', 'Bit Crusher']
native_names['resonance_filter'] = ['0b44f1c343a1de4ab108069e3ec0f7e4', 'ZPlane', 'Resonance Filter']
native_names['compressor_expander'] = ['1158f6956478e749a123534b7d943e3d', 'ZPlane', 'Compressor/Expander']
native_names['noise_gate'] = ['ee2b5cce1faeb54f9081ad2575736075', 'ZPlane', 'Noise Gate']
native_names['limiter'] = ['80700b7cbbf6234189e21d862baf0d19', 'ZPlane', 'Limiter']

def encode_chunk(inbytes):
	statedata = base64.b64encode(inbytes).decode("ascii")
	statedata = statedata.replace('/', '.')
	return statedata

def set_params(params_obj):
	mute = 0.5 if params_obj.get('enabled', True).value else 1
	vol = params_obj.get('vol', 1).value*0.824999988079071
	pan = params_obj.get('pan', 0).value/2 + 0.5
	return encode_chunk(struct.pack('>ffff', *(mute, vol, vol, pan)))

def make_group(convproj_obj, groupid, groups_data, sb_maintrack):
	from objects.file_proj import proj_soundbridge
	if groupid not in groups_data and groupid in convproj_obj.groups:
		group_obj = convproj_obj.groups[groupid]
		sb_grouptrack = proj_soundbridge.soundbridge_track(None)
		make_plugins_fx(convproj_obj, sb_grouptrack, group_obj.fxslots_audio)
		sb_grouptrack.type = 1
		#sb_grouptrack.state = set_params(group_obj.params)

		make_autocontains_master(convproj_obj, sb_grouptrack, group_obj.params, ['group', groupid])

		sb_maintrack.tracks.append(sb_grouptrack)
		if group_obj.visual.name: sb_grouptrack.name = group_obj.visual.name
		sb_grouptrack.metadata["SequencerTrackCollapsedState"] = 8
		sb_grouptrack.metadata["SequencerTrackHeightState"] = 43
		if group_obj.visual.color: 
			sb_grouptrack.metadata["TrackColor"] = '#'+group_obj.visual.color.get_hex()
		else:
			sb_grouptrack.metadata["TrackColor"] = '#b0ff91'

		groups_data[groupid] = sb_grouptrack

sb_auto_dtype = np.dtype([('pos', '>I'), ('val', '>f'),('unk1', '>f'),('unk2', '>f')])

def make_auto(convproj_obj, autoloc, blocks, add, mul, trackmeta):
	from objects.file_proj import proj_soundbridge
	aid_found, aid_data = convproj_obj.automation.get(autoloc, 'float')

	if aid_found:
		if aid_data.pl_points:
			for autopl_obj in aid_data.pl_points:
				autopl_obj.data.remove_instant()

				block = proj_soundbridge.soundbridge_block(None)
				block.name = ""
				block.timeBaseMode = 0
				block.position = autopl_obj.time.position
				block.positionStart = 0
				block.positionEnd = autopl_obj.time.duration
				block.loopOffset = 0
				block.framesCount = autopl_obj.time.duration
				block.loopEnabled = 0
				block.muted = 0
				block.version = 1

				if autopl_obj.time.cut_type == 'cut':
					block.positionStart, block.loopOffset, block.positionEnd = autopl_obj.time.get_loop_data()
					block.loopOffset = max(block.loopOffset, 0)
					block.positionStart = max(block.positionStart, 0)

				if 'TrackColor' in trackmeta:
					block.metadata["BlockColor"] = trackmeta["TrackColor"]

				autoarray = np.zeros(len(autopl_obj.data), dtype=sb_auto_dtype)
				autoarray['unk1'] = 0.99
				autoarray['unk2'] = 1
				for n, a in enumerate(autopl_obj.data):
					autoarray[n]['pos'] = int(a.pos)
					autoarray[n]['val'] = (a.value/mul)-add

				block.blockData = encode_chunk(b'\x00\x00\x00\x14'+autoarray.tobytes()+(b'\x00'*16))

				blocks.append(block)

def make_autocontains_master(convproj_obj, sb_track, params_obj, startauto):
	from objects.file_proj import proj_soundbridge
	automationTracks = sb_track.automationContainer.automationTracks

	vol = params_obj.get('vol', 1).value*0.824999988079071
	pan = params_obj.get('pan', 0).value/0.5 + 0.5

	automationTrack = proj_soundbridge.soundbridge_automationTrack(None)
	automationTrack.parameterIndex = 2
	automationTrack.mode = 3
	automationTrack.enabled = 1
	automationTrack.defaultValue = vol
	make_auto(convproj_obj, startauto+['vol'], automationTrack.blocks, 0, 1, sb_track.metadata)
	automationTracks.append(automationTrack)

	automationTrack = proj_soundbridge.soundbridge_automationTrack(None)
	automationTrack.parameterIndex = 3
	automationTrack.mode = 3
	automationTrack.enabled = 1
	automationTrack.defaultValue = pan
	make_auto(convproj_obj, startauto+['pan'], automationTrack.blocks, -.5, 2, sb_track.metadata)
	automationTracks.append(automationTrack)

def make_autocontains(convproj_obj, sb_track, params_obj, n, startauto):
	from objects.file_proj import proj_soundbridge
	automationTracks = sb_track.automationContainer.automationTracks

	vol = params_obj.get('vol', 1).value*0.824999988079071
	pan = params_obj.get('pan', 0).value/0.5 + 0.5

	automationTrack = proj_soundbridge.soundbridge_automationTrack(None)
	automationTrack.parameterIndex = 0
	automationTrack.mode = 3
	automationTrack.enabled = 1
	automationTrack.defaultValue = 0.5 if params_obj.get('enabled', True).value else 1
	automationTracks.append(automationTrack)

	if n == 0:
		automationTrack = proj_soundbridge.soundbridge_automationTrack(None)
		automationTrack.parameterIndex = 1
		automationTrack.mode = 3
		automationTrack.enabled = 1
		automationTrack.defaultValue = 0.5
		automationTracks.append(automationTrack)

	automationTrack = proj_soundbridge.soundbridge_automationTrack(None)
	automationTrack.parameterIndex = 2
	automationTrack.mode = 3
	automationTrack.enabled = 1
	automationTrack.defaultValue = vol
	make_auto(convproj_obj, startauto+['vol'], automationTrack.blocks, 0, 1, sb_track.metadata)
	automationTracks.append(automationTrack)

	automationTrack = proj_soundbridge.soundbridge_automationTrack(None)
	automationTrack.parameterIndex = 3
	automationTrack.mode = 3
	automationTrack.enabled = 1
	automationTrack.defaultValue = pan
	make_auto(convproj_obj, startauto+['pan'], automationTrack.blocks, -.5, 2, sb_track.metadata)
	automationTracks.append(automationTrack)

def make_sends(convproj_obj, sb_track, sends_obj):
	from objects.file_proj import proj_soundbridge
	cur_returns = {}
	automationTracks = sb_track.sendsAutomationContainer.automationTracks

	values = []
	for n, x in enumerate(sb_returns):
		automationTrack = proj_soundbridge.soundbridge_automationTrack(None)
		automationTrack.parameterIndex = n
		automationTrack.mode = 3
		automationTrack.enabled = 1
		automationTrack.defaultValue = 0
		automationTrack.returnTrackPath = '/'+str(n)+'/R'
		automationTracks.append(automationTrack)
		cur_returns[x] = automationTrack
		values.append(0)

	for i, x in sends_obj.iter():
		automationTrack = cur_returns[i]
		automationTrack.defaultValue = x.params.get('amount', 0).value
		if x.sendautoid: make_auto(convproj_obj, ['send', x.sendautoid, 'amount'], automationTrack.blocks, 0, 1, sb_track.metadata)
		values[sb_returns.index(i)] = automationTrack.defaultValue

	sb_track.sendsAutomationContainer.state = encode_chunk(struct.pack('>'+('f'*len(values)), *values))

def make_plugins_fx(convproj_obj, sb_track, fxslots_audio):
	from objects.file_proj import proj_soundbridge
	for pluginid in fxslots_audio:
		plugin_found, plugin_obj = convproj_obj.get_plugin(pluginid)
		if plugin_found: 
			if plugin_obj.check_wildmatch('native', 'soundbridge', None):
				if plugin_obj.type.subtype in native_names:
					fx_on, fx_wet = plugin_obj.fxdata_get()
					uuid, vendor, name = native_names[plugin_obj.type.subtype]
					auplug = proj_soundbridge.soundbridge_audioUnit(None)
					auplug.uid = encode_chunk(bytearray.fromhex(uuid))
					auplug.vendor = vendor
					auplug.name = name
					outbytes = plugin_obj.to_bytes('soundbridge', 'soundbridge', 'plugin', plugin_obj.type.subtype, plugin_obj.type.subtype)
					auplug.state = encode_chunk(struct.pack('>f', int(not fx_on)) + outbytes)
					sb_track.audioUnits.append(auplug)

			if plugin_obj.check_wildmatch('external', 'vst2', None):
				auplug = make_vst2(convproj_obj, plugin_obj, False, pluginid, sb_track)
				if auplug:
					sb_track.audioUnits.append(auplug)

def make_vst2(convproj_obj, plugin_obj, issynth, pluginid, sb_track):
	from objects.file_proj import proj_soundbridge
	from functions_plugin_ext import plugin_vst2
	fourid = plugin_obj.datavals_global.get('fourid', None)
	sb_plugin = None

	if fourid: 
		uid = b'\x00\x00\x00\x00SV2T'+struct.pack('>I', fourid)+b'\x00\x00\x00\x00'
		sb_plugin = proj_soundbridge.soundbridge_audioUnit(None)
		sb_plugin.uid = encode_chunk(uid)
		sb_plugin.name = plugin_obj.datavals_global.get('name', None)
		sb_plugin.vendor = plugin_obj.datavals_global.get('creator', None)
		if issynth: sb_plugin.metadata['AudioUnitType'] = 3
		vstchunk = plugin_vst2.export_presetdata(plugin_obj)

		if len(vstchunk)>12:
			vsttype = vstchunk[8:12]

			statewriter = bytewriter.bytewriter()
			statewriter.raw(b'CcnK')
			statewriter.raw(b'\x14\x00\x00\x00')
			statewriter.raw(b'\x00\x00\x00\x00'*3)
			statewriter.raw(b'CcnK')
			statewriter.raw(b'\x00\x00\x00\x00')

			if vsttype == b'FBCh':
				statewriter.raw(b'FBCh')
				statewriter.raw(vstchunk[12:16])
				statewriter.raw(b'\x00\x00\x00\x00')
				statewriter.raw(b'\x00\x00\x00\x00')
				statewriter.raw(vstchunk[24:28])
				statewriter.raw(b'\x00'*128)
				statewriter.raw(vstchunk[56:])
			if vsttype == b'FPCh':
				statewriter.raw(b'FPCh')
				statewriter.raw(vstchunk[12:16])
				statewriter.raw(b'\x00\x00\x00\x00')
				statewriter.raw(b'\x00\x00\x00\x00')
				statewriter.raw(vstchunk[24:28])
				statewriter.raw(b'\x00'*128)
				statewriter.raw(vstchunk[56:])
			if vsttype == b'FxBk':
				statewriter.raw(b'FxBk')
				statewriter.raw(vstchunk[12:16])
				statewriter.raw(b'\x00\x00\x00\x00')
				statewriter.raw(b'\x00\x00\x00\x00')
				statewriter.raw(vstchunk[24:28])
				statewriter.raw(b'\x00'*128)
				statewriter.raw(vstchunk)
			if vsttype == b'FxCk':
				statewriter.raw(b'FxBk')
				statewriter.raw(vstchunk[12:16])
				statewriter.raw(b'\x00\x00\x00\x00')
				statewriter.raw(b'\x00\x00\x00\x00')
				statewriter.raw(vstchunk[24:28])
				statewriter.raw(b'\x00'*128)
				statewriter.raw(vstchunk)

		state = statewriter.getvalue()

		sb_plugin.state = encode_chunk(state)

		for autoloc, autodata, paramnum in convproj_obj.automation.iter_pl_points_external(pluginid):
			paramid = 'ext_param_'+str(paramnum)
			automationTrack = proj_soundbridge.soundbridge_automationTrack(None)
			automationTrack.parameterIndex = paramnum
			automationTrack.mode = 3
			automationTrack.enabled = 1
			automationTrack.defaultValue = plugin_obj.params.get(paramid, 0)
			make_auto(convproj_obj, autoloc.get_list(), automationTrack.blocks, 0, 1, sb_track.metadata)
			sb_plugin.automationContainer.automationTracks.append(automationTrack)
	else:
		logger_output.warning('VST2 plugin not placed: no ID found.')

	return sb_plugin

def time_add(event, time_obj, otherblock):

	loop_1, loop_2, loop_3 = time_obj.get_loop_data()

	while loop_1<0:
		loop_1 += loop_3

	if time_obj.cut_type == 'cut':
		event.positionStart = time_obj.cut_start
		event.loopOffset = 0
		event.positionEnd = event.framesCount-time_obj.cut_start
		event.loopOffset = max(event.loopOffset, 0)
		event.positionStart = max(event.positionStart, 0)
		event.positionEnd = time_obj.duration+event.positionStart
		if otherblock:
			otherblock.framesCount = time_obj.duration+event.positionStart
		
	elif time_obj.cut_type == 'loop':
		event.positionStart = loop_1
		event.loopOffset = loop_2
		event.positionEnd = loop_3
		event.loopEnabled = 1
		event.loopOffset = max(event.loopOffset, 0)
		event.positionStart = max(event.positionStart, 0)

	elif time_obj.cut_type == 'loop_off':
		event.loopOffset = loop_1
		event.positionStart = loop_2
		event.positionEnd = loop_3
		event.loopEnabled = 1
		event.loopOffset = max(event.loopOffset, 0)
		event.positionStart = max(event.positionStart, 0)

class output_soundbridge(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'output'
	def get_shortname(self): return 'soundbridge'
	def get_name(self): return 'SoundBridge (WIP)'
	def gettype(self): return 'r'
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'soundbridge'
		in_dict['auto_types'] = ['pl_points']
		in_dict['placement_loop'] = ['loop', 'loop_off']
		in_dict['plugin_included'] = []
		in_dict['audio_stretch'] = ['warp']
		in_dict['placement_cut'] = True
		in_dict['plugin_included'] = ['native:soundbridge']
		in_dict['plugin_ext'] = ['vst2']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['audio_filetypes'] = ['wav', 'mp3']
	def parse(self, convproj_obj, output_file):
		from objects.file_proj import proj_soundbridge
		from functions_plugin_ext import plugin_vst2
		global sb_returns

		convproj_obj.change_timings(22050, False)

		project_obj = proj_soundbridge.soundbridge_song()
		project_obj.masterTrack.defualts_master()
		project_obj.pool.defualts()
		project_obj.videoTrack.defualts()

		globalstore.datadef.load('soundbridge', './data_main/datadef/soundbridge.ddef')
		globalstore.dataset.load('soundbridge', './data_main/dataset/soundbridge.dset')

		tempo = convproj_obj.params.get('bpm', 120).value

		sb_timeSignature = project_obj.timeline.timeSignature
		sb_tempo = project_obj.timeline.tempo

		sb_timeSignature.timeSigNumerator = convproj_obj.timesig[0]
		sb_timeSignature.timeSigDenominator = convproj_obj.timesig[1]
		project_obj.tempo = tempo
		sb_tempo.tempo = tempo

		master_track = convproj_obj.track_master

		make_plugins_fx(convproj_obj, project_obj.masterTrack, convproj_obj.track_master.fxslots_audio)

		if master_track.visual.color: project_obj.masterTrack.metadata["TrackColor"] = '#'+master_track.visual.color.get_hex()

		project_obj.masterTrack.state = set_params(master_track.params)
		make_autocontains_master(convproj_obj, project_obj.masterTrack, master_track.params, ['master'])

		master_returns = master_track.returns

		sb_returns = [x for x in master_track.returns]

		audio_ids = {}
		used_filenames = {}
		for sampleref_id, sampleref_obj in convproj_obj.iter_samplerefs():
			if sampleref_obj.fileref.exists('win'):
				filename = str(sampleref_obj.fileref.file)
				if filename not in used_filenames: used_filenames[filename] = 0
				used_filenames[filename] += 1
				outaud_filename = filename+('_'+str(used_filenames[filename]) if used_filenames[filename]>1 else '')
				movefilename = sampleref_obj.fileref.get_path('win', False)
				shutil.copyfile(movefilename, os.path.join(output_file, outaud_filename))
				audio_ids[sampleref_id] = sampleref_obj.fileref.file

				audioSource = proj_soundbridge.soundbridge_audioSource(None)
				audioSource.fileName = str(sampleref_obj.fileref.file)
				audioSource.sourceFileName = movefilename.replace('\\', '/')
				project_obj.pool.audioSources.append(audioSource)

		groups_data = {}
		for groupid, insidegroup in convproj_obj.iter_group_inside():
			sb_tracks = project_obj.masterTrack

			if insidegroup: 
				make_group(convproj_obj, groupid, groups_data, groups_data[insidegroup])
			else: 
				make_group(convproj_obj, groupid, groups_data, sb_tracks)

		for trackid, track_obj in convproj_obj.iter_track():
			sb_tracks = project_obj.masterTrack.tracks

			if track_obj.group: sb_tracks = groups_data[track_obj.group].tracks

			if track_obj.type == 'instrument':
				sb_track = proj_soundbridge.soundbridge_track(None)
				sb_track.state = set_params(track_obj.params)
				if track_obj.visual.name: sb_track.name = track_obj.visual.name
				if track_obj.visual.color: sb_track.metadata["TrackColor"] = '#'+track_obj.visual.color.get_hex()
				sb_track.midiInput = proj_soundbridge.soundbridge_deviceRoute(None)
				sb_track.midiInput.externalDeviceIndex = 0
				sb_track.midiOutput = proj_soundbridge.soundbridge_deviceRoute(None)
				sb_track.blocks = []
				make_autocontains(convproj_obj, sb_track, track_obj.params, 0, ['track', trackid])
				make_sends(convproj_obj, sb_track, track_obj.sends)
				make_plugins_fx(convproj_obj, sb_track, track_obj.fxslots_audio)

				if track_obj.inst_pluginid:
					plugin_found, plugin_obj = convproj_obj.get_plugin(track_obj.inst_pluginid)
					if plugin_found: 
						if plugin_obj.check_wildmatch('external', 'vst2', None):
							sb_track.midiInstrument = make_vst2(convproj_obj, plugin_obj, True, track_obj.inst_pluginid, sb_track)


				for notespl_obj in track_obj.placements.pl_notes:
					notespl_obj.notelist.mod_limit(-60, 67)
					numnotes = len(notespl_obj.notelist)
					notearray = np.zeros(numnotes, dtype=sb_notes_dtype)

					block = proj_soundbridge.soundbridge_block(None)
					if notespl_obj.visual.name: block.name = notespl_obj.visual.name
					block.timeBaseMode = 0
					block.position = notespl_obj.time.position
					block.positionStart = 0
					block.positionEnd = notespl_obj.time.duration
					block.loopOffset = 0
					block.framesCount = notespl_obj.time.duration
					block.loopEnabled = 0
					block.muted = 0

					time_add(block, notespl_obj.time, None)

					numnote = 0
					for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
						for t_key in t_keys:
							notearray[numnote]['id'] = numnote
							notearray[numnote]['pos'] = t_pos
							notearray[numnote]['dur'] = t_dur
							notearray[numnote]['key'] = t_key+60
							notearray[numnote]['vol'] = min(t_vol*127, 127)
							numnote += 1

					if notespl_obj.visual.color: 
						block.metadata["BlockColor"] = '#'+notespl_obj.visual.color.get_hex()

					datasize = sb_notes_dtype.itemsize*numnotes

					outbytes = b'\x00\x00\x00\x14'+notearray.tobytes()
					padsize = 4*numnotes
					outbytes += b'\x00'*padsize
					#print(len(outbytes)-4)
					#print(notearray)

					block.blockData = encode_chunk(outbytes)
					block.automationBlocks = []

					sb_track.blocks.append(block)

				sb_track.midiUnits = []
				sb_track.type = 4

			if track_obj.type == 'audio':
				sb_track = proj_soundbridge.soundbridge_track(None)
				sb_track.state = set_params(track_obj.params)
				if track_obj.visual.name: sb_track.name = track_obj.visual.name
				if track_obj.visual.color: sb_track.metadata["TrackColor"] = '#'+track_obj.visual.color.get_hex()
				sb_track.type = 3
				sb_track.channelCount = 2
				sb_track.pitchTempoProcessorMode = 2
				sb_track.audioInput = proj_soundbridge.soundbridge_deviceRoute(None)
				sb_track.blockContainers = []
				make_autocontains(convproj_obj, sb_track, track_obj.params, 0, ['track', trackid])
				make_sends(convproj_obj, sb_track, track_obj.sends)
				make_plugins_fx(convproj_obj, sb_track, track_obj.fxslots_audio)

				blockContainer = proj_soundbridge.soundbridge_blockContainer(None)

				for audiopl_obj in track_obj.placements.pl_audio:
					block = proj_soundbridge.soundbridge_block(None)

					if audiopl_obj.visual.name: blockContainer.name = audiopl_obj.visual.name
					if audiopl_obj.visual.name: block.name = audiopl_obj.visual.name

					block.position = audiopl_obj.time.position
					block.framesCount = audiopl_obj.time.duration
					block.muted = 0
					block.timeBaseMode = 0

					if audiopl_obj.visual.color: 
						block.metadata["BlockColor"] = '#'+audiopl_obj.visual.color.get_hex()

					block.crossfades = []
					block.events = []

					sp_obj = audiopl_obj.sample
					ref_found, sampleref_obj = convproj_obj.get_sampleref(sp_obj.sampleref)

					if ref_found:
						if sampleref_obj.found:
							event = proj_soundbridge.soundbridge_event(None)
							event.position = 0
							event.positionStart = 0
							event.positionEnd = audiopl_obj.time.duration
							event.loopOffset = 0
							event.framesCount = audiopl_obj.time.duration
							event.loopEnabled = 0
							event.tempo = 120
							event.inverse = 0
							event.gain = xtramath.to_db(sp_obj.vol)
							event.fadeInLength = int(audiopl_obj.fade_in.get_dur_beat(tempo)*22050)
							event.fadeOutLength = int(audiopl_obj.fade_out.get_dur_beat(tempo)*22050)
							event.fadeInCurve = 4
							event.fadeOutCurve = 4
							event.fadeInConvexity = 0.5
							event.fadeOutConvexity = 0.5
							event.pitch = pow(2, sp_obj.pitch/12)
							event.fileName = audio_ids[sp_obj.sampleref]

							time_add(event, audiopl_obj.time, block)

							event.stretchMarks = []

							stretch_obj = audiopl_obj.sample.stretch

							stretch_obj.fix_single_warp(convproj_obj, sp_obj)

							warp_offset = stretch_obj.fix_warps(convproj_obj, sp_obj)

							#stretch_obj.debugtxt_warp()

							event.positionStart += warp_offset*22050
							event.loopOffset += warp_offset*22050
							event.positionEnd += warp_offset*22050

							event.positionStart = int(event.positionStart)
							event.loopOffset = int(event.loopOffset)
							event.positionEnd = int(event.positionEnd)

							warp_points = [x for x in stretch_obj.iter_warp_points()]

							for warp_point_obj in warp_points:
								stretchMark = proj_soundbridge.soundbridge_stretchMark(None)
								stretchMark.newPosition = warp_point_obj.beat
								stretchMark.initPosition = warp_point_obj.second

								stretchMark.newPosition *= 44100/2
								stretchMark.initPosition *= sampleref_obj.hz

								stretchMark.newPosition = int(stretchMark.newPosition)
								stretchMark.initPosition = int(stretchMark.initPosition)
								event.stretchMarks.append(stretchMark)

							#print(warp_points)

							block.events.append(event)
					blockContainer.blocks.append(block)

				sb_track.blockContainers.append(blockContainer)

			sb_tracks.append(sb_track)

		for returnid, return_obj in master_returns.items():
			sb_track = proj_soundbridge.soundbridge_track(None)
			sb_track.state = set_params(track_obj.params)
			if return_obj.visual.name: sb_track.name = return_obj.visual.name
			if return_obj.visual.color: sb_track.metadata["TrackColor"] = '#'+return_obj.visual.color.get_hex()
			sb_track.type = 2
			sb_track.sourceBufferType = 2
			sb_track.audioOutput = proj_soundbridge.soundbridge_deviceRoute(None)
			sb_track.blockContainers = []
			make_autocontains(convproj_obj, sb_track, return_obj.params, 1, ['return', returnid])
			make_sends(convproj_obj, sb_track, return_obj.sends)
			make_plugins_fx(convproj_obj, sb_track, return_obj.fxslots_audio)
			sb_tracks.append(sb_track)

		if convproj_obj.loop_active:
			project_obj.metadata['TransportLoop'] = 'true'
			project_obj.metadata['TransportPlayPositionL'] = convproj_obj.loop_start
			project_obj.metadata['TransportPlayPositionR'] = convproj_obj.loop_end
		else:
			project_obj.metadata['TransportLoop'] = 'false'
			project_obj.metadata['TransportPlayPositionL'] = convproj_obj.start_pos
			project_obj.metadata['TransportPlayPositionR'] = convproj_obj.get_dur()

		outfile = os.path.join(output_file, '')
		os.makedirs(output_file, exist_ok=True)
		project_obj.write_to_file(os.path.join(output_file, 'project.xml'))