# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import base64
import numpy as np
import io
import os
import struct
from objects.convproj import fileref
from functions import xtramath
import math
from objects import globalstore
from objects.data_bytes import bytereader

sb_auto_dtype = np.dtype([('pos', '>I'), ('val', '>f'),('unk1', '>f'),('unk2', '>f')])

native_names = {}
native_names['2ed34074c14566409f62442c8545929f'] = 'eq'
native_names['544d1ae3e2c91548b932574932c83885'] = 'filter_unit'
native_names['1423f146b5fcaa40904b2c3fe24495fa'] = 'analyzer'
native_names['f487b09e6f329a41b2cfc280068079a4'] = 'chorus_flanger'
native_names['0d47d236d52df342bf3b8635a4b89f07'] = 'delay'
native_names['b2a57c0cc1996d468f38a87332010bc9'] = 'phaser'
native_names['8f64f7b97060ca449e89456f9a2684d0'] = 'reverb'
native_names['2793169f4a4b554087755fafff91b3e9'] = 'bit_crusher'
native_names['0b44f1c343a1de4ab108069e3ec0f7e4'] = 'resonance_filter'
native_names['1158f6956478e749a123534b7d943e3d'] = 'compressor_expander'
native_names['ee2b5cce1faeb54f9081ad2575736075'] = 'noise_gate'
native_names['80700b7cbbf6234189e21d862baf0d19'] = 'limiter'

def decode_chunk(statedata):
	statedata = statedata.replace('.', '/')
	return base64.b64decode(statedata)

def calc_vol(vol):
	vol = (vol/0.824999988079071)**4
	return vol
	
def parse_auto(blockdata):
	blockdata = io.BytesIO(decode_chunk(blockdata))
	unk_x = blockdata.read(4)
	dataread = blockdata.read()
	numnotes = len(dataread)//sb_auto_dtype.itemsize
	autodata = np.frombuffer(dataread[0:numnotes*sb_auto_dtype.itemsize], dtype=sb_auto_dtype)
	return autodata[np.where(autodata['unk1']!=0)]

def add_auto(valtype, convproj_obj, autoloc, sb_blocks, add, mul):
	for block in sb_blocks:
		autopl_obj = convproj_obj.automation.add_pl_points(autoloc, 'float')
		autopl_obj.time.position = block.position
		autopl_obj.time.duration = block.framesCount
		for point in parse_auto(block.blockData):
			autopoint_obj = autopl_obj.data.add_point()
			autopoint_obj.pos = point['pos']
			if valtype == 'vol':
				autopoint_obj.value = calc_vol(point['val'])
			else:
				autopoint_obj.value = (point['val']+add)*mul
			autopoint_obj.type = 'normal'

sb_notes_dtype = np.dtype([('id', '>I'),('pos', '>I'),('dur', '>I'),('key', 'B'),('vol', 'B'),('unk1', 'B'),('unk2', 'B')])

def parse_notes(notes_data):
	unk_x = notes_data.read(4)
	dataread = notes_data.read()
	numnotes = len(dataread)//sb_notes_dtype.itemsize
	notedata = np.frombuffer(dataread[0:numnotes*sb_notes_dtype.itemsize], dtype=sb_notes_dtype)
	outdata = notedata[np.where(notedata['dur']!=0)]
	return outdata

def add_params(stateobj, params_obj):
	statebin = decode_chunk(stateobj)
	mute, vol, unk, pan = struct.unpack('>ffff', statebin)
	params_obj.add('enabled', mute!=1, 'bool')
	params_obj.add('vol', calc_vol(vol), 'float')
	params_obj.add('pan', (pan-0.5)*2, 'float')

global_returnids = 0

def make_sendauto(convproj_obj, sb_track, track_obj, cvpj_trackid):
	for x in sb_track.sendsAutomationContainer.automationTracks:
		splitret = x.returnTrackPath.split('/')
		if len(splitret) == 3:
			if splitret[0]=='' and splitret[1].isnumeric() and splitret[2]=='R':
				sendautoid = cvpj_trackid+'__'+'return__'+str(splitret[1])
				track_obj.sends.add('return__'+str(splitret[1]), sendautoid, x.defaultValue)
				add_auto(None, convproj_obj, ['send', sendautoid, 'amount'], x.blocks, 0, 1)

def create_plugin(convproj_obj, sb_plugin, issynth):
	from functions_plugin_ext import plugin_vst2
	uiddata = decode_chunk(sb_plugin.uid)
	statedata = decode_chunk(sb_plugin.state)
	pluginid = None

	if len(uiddata) == 16 and statedata:
		hexdata = uiddata.hex()

		if uiddata[0:8] == b'\x00\x00\x00\x00SV2T':
			fourid = struct.unpack('>I', uiddata[8:12])[0]

			plugin_obj, pluginid = convproj_obj.plugin__add__genid('external', 'vst2', 'win')
			plugin_obj.role = 'synth' if issynth else 'fx'
			plugin_obj.datavals_global.add('name', sb_plugin.name)
			plugin_obj.datavals_global.add('fourid', fourid)
			plugin_obj.datavals_global.add('creator', sb_plugin.vendor)

			statereader = bytereader.bytereader()
			statereader.load_raw(statedata)

			#print(len(statedata), statedata[0:300])

			if statereader.magic_check(b'CcnK'):
				statereader.skip(8)
				disabled = statereader.float_b()
				plugin_obj.fxdata_add(not disabled, None)
				programnum = statereader.uint32_b()
				plugin_obj.clear_prog_keep(programnum)
				if statereader.magic_check(b'CcnK'):
					statereader.skip(4)
					chunk_type = statereader.read(4)
					if chunk_type == b'FBCh':
						statereader.skip(16)
						statereader.skip(128)
						chunkdata = statereader.raw(statereader.uint32_b())
						plugin_obj.clear_prog_keep(programnum)
						plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', None, fourid, 'chunk', chunkdata, None)
						plugin_obj.datavals_global.add('is_bank', True)
					if chunk_type == b'FxBk':
						statereader.skip(16)
						statereader.skip(128)
						plugin_obj.clear_prog_keep(programnum)
						plugin_vst2.import_presetdata_raw(convproj_obj, plugin_obj, statereader.rest(), 'win')

					for x in sb_plugin.automationContainer.automationTracks:
						paramid = 'ext_param_'+str(x.parameterIndex-1)
						plugin_obj.params.add(paramid, x.defaultValue, 'float')
						add_auto(None, convproj_obj, ['plugin', pluginid, paramid], x.blocks, 0, 1)

		elif hexdata in native_names:
			plugin_enabled = struct.unpack('>f', statedata[0:4])[0]
			native_name = native_names[hexdata]
			plugin_obj, pluginid = convproj_obj.plugin__add__genid('native', 'soundbridge', native_name)
			plugin_obj.from_bytes(statedata[4:], 'soundbridge', 'soundbridge', 'plugin', native_name, native_name)

	return pluginid

def do_fx(convproj_obj, sb_track, track_obj):
	for x in sb_track.audioUnits:
		pluginid = create_plugin(convproj_obj, x, False)
		if pluginid:
			track_obj.plugslots.slots_audio.append(pluginid)

def make_track(convproj_obj, sb_track, groupname, num, pfreq):
	global global_returnids

	from functions_plugin_ext import plugin_vst2
	from functions_plugin_ext import plugin_vst3
	metadata = sb_track.metadata
	trackcolor = metadata['TrackColor'] if 'TrackColor' in metadata else None
	cvpj_trackid = ('main' if not groupname else groupname)+'__'+str(num)

	if sb_track.type == 4:
		track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)
		track_visual(track_obj.visual, sb_track)
		add_params(sb_track.state, track_obj.params)
		do_fx(convproj_obj, sb_track, track_obj)

		track_obj.armed.on = bool(sb_track.armed)
		track_obj.armed.in_keys = bool(sb_track.armed)

		if groupname:
			track_obj.group = groupname
			track_obj.sends.to_master_active = False

		for block in sb_track.blocks:
			placement_obj = track_obj.placements.add_notes()
			placement_obj.time.set_posdur(block.position, block.positionEnd-block.positionStart)
			if block.loopEnabled: placement_obj.time.set_loop_data(block.loopOffset, block.loopOffset, block.framesCount)
			else: placement_obj.time.set_offset(block.positionStart)
			blockdata = decode_chunk(block.blockData)
			trackcolor = block.metadata['BlockColor'] if 'BlockColor' in block.metadata else None
			placement_obj.visual.color.set_hex(trackcolor)
			placement_obj.visual.name = block.name
			placement_obj.muted = bool(block.muted)
			for note in parse_notes(io.BytesIO(blockdata)): placement_obj.notelist.add_r(note['pos'], note['dur'], note['key']-60, note['vol']/127, None)
			for block in block.automationBlocks:
				valmul = 1
				valadd = 0
				ccnum = block.index-1
				if ccnum == -1: 
					mpetype = 'midi_pressure'
					valmul = 127
				elif ccnum == 0: 
					mpetype = 'midi_pitch'
					valmul = 8192*2
					valadd = 0.5
				else: 
					mpetype = 'midi_cc_'+str(ccnum)
					valmul = 127

				autopoints_obj = placement_obj.add_autopoints(mpetype)
				for a in parse_auto(block.blockData):
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = a['pos']-block.positionStart
					autopoint_obj.value = (a['val']-valadd)*valmul

		if sb_track.midiInstrument:
			midiinst = sb_track.midiInstrument
			track_obj.plugslots.set_synth( create_plugin(convproj_obj, midiinst, True) )

		if sb_track.midiInput:
			track_obj.midi.in_chan = sb_track.midiInput.channelIndex+1

		if sb_track.midiOutput:
			track_obj.midi.out_chan = sb_track.midiOutput.channelIndex+1

	if sb_track.type == 3:
		track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
		track_visual(track_obj.visual, sb_track)
		add_params(sb_track.state, track_obj.params)
		do_fx(convproj_obj, sb_track, track_obj)

		track_obj.armed.on = bool(sb_track.armed)
		track_obj.armed.in_audio = bool(sb_track.armed)

		if groupname:
			track_obj.group = groupname
			track_obj.sends.to_master_active = False

		if sb_track.blockContainers:
			for block in sb_track.blockContainers[0].blocks:
				placement_obj = track_obj.placements.add_nested_audio()
				clipmetadata = block.metadata
				placement_obj.visual.name = block.name
				placement_obj.muted = bool(block.muted)
				if 'BlockColor' in clipmetadata: 
					placement_obj.visual.color.set_hex(clipmetadata['BlockColor'])
				placement_obj.time.set_posdur(block.position, block.framesCount)
				for blockevent in block.events:
					placement_obj = placement_obj.add()
					placement_obj.time.set_posdur(blockevent.position, blockevent.framesCount)
					placement_obj.time.set_offset(blockevent.positionStart)

					if 'BlockColor' in clipmetadata: placement_obj.visual.color.set_hex(clipmetadata['BlockColor'])

					sp_obj = placement_obj.sample
					sp_obj.sampleref = blockevent.fileName

					sp_obj.vol = xtramath.from_db(blockevent.gain)
					sp_obj.pitch = math.log2(1/blockevent.pitch)*-12

					stretch_obj = sp_obj.stretch
					stretch_obj.preserve_pitch = True
					stretch_obj.is_warped = True

					placement_obj.fade_in.set_dur(blockevent.fadeInLength/pfreq, 'beats')
					placement_obj.fade_out.set_dur(blockevent.fadeOutLength/pfreq, 'beats')

					ref_found, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)

					for stretchMark in blockevent.stretchMarks:
						warp_point_obj = stretch_obj.add_warp_point()
						warp_point_obj.beat = stretchMark.newPosition/pfreq
						warp_point_obj.second = stretchMark.initPosition/(sampleref_obj.hz if sampleref_obj else pfreq)

					stretch_obj.calc_warp_points()
					#stretch_obj.debugtxt_warp()

					for autoblock in blockevent.automationBlocks:
						autopoints_obj = placement_obj.add_autopoints('gain', pfreq, True)
						for a in parse_auto(autoblock.blockData):
							autopoint_obj = autopoints_obj.add_point()
							autopoint_obj.pos = a['pos']-autoblock.positionStart
							autopoint_obj.value = a['val']

	if sb_track.type in [3,4]:
		make_sendauto(convproj_obj, sb_track, track_obj, cvpj_trackid)
		for x in sb_track.automationContainer.automationTracks:
			if x.parameterIndex == 2: add_auto('vol', convproj_obj, ['track', cvpj_trackid, 'vol'], x.blocks, 0, 1)
			if x.parameterIndex == 3: add_auto(None, convproj_obj, ['track', cvpj_trackid, 'pan'], x.blocks, -.5, 2)

	if sb_track.type == 2:
		returnid = 'return__'+str(global_returnids)
		track_obj = convproj_obj.track_master.fx__return__add(returnid)
		track_visual(track_obj.visual, sb_track)
		add_params(sb_track.state, track_obj.params)
		do_fx(convproj_obj, sb_track, track_obj)
		global_returnids += 1
		for x in sb_track.automationContainer.automationTracks:
			if x.parameterIndex == 2: add_auto('vol', convproj_obj, ['return', returnid, 'vol'], x.blocks, 0, 1)
			if x.parameterIndex == 3: add_auto(None, convproj_obj, ['return', returnid, 'pan'], x.blocks, -.5, 2)

	if sb_track.type == 1:
		track_obj = convproj_obj.fx__group__add(cvpj_trackid)
		track_visual(track_obj.visual, sb_track)
		add_params(sb_track.state, track_obj.params)
		do_fx(convproj_obj, sb_track, track_obj)

		do_markers(track_obj, sb_track.markers)

		for x in sb_track.automationContainer.automationTracks:
			if x.parameterIndex == 2: add_auto('vol', convproj_obj, ['group', cvpj_trackid, 'vol'], x.blocks, 0, 1)
			if x.parameterIndex == 3: add_auto(None, convproj_obj, ['group', cvpj_trackid, 'pan'], x.blocks, -.5, 2)

		for gnum, gb_track in enumerate(sb_track.tracks):
			make_track(convproj_obj, gb_track, cvpj_trackid, gnum, pfreq)

def track_visual(visual_obj, ab_track):
	visual_obj.name = ab_track.name
	visual_obj.color.set_hex(ab_track.metadata['TrackColor'] if 'TrackColor' in ab_track.metadata else None)

def do_markers(convproj_obj, sb_markers):
	for marker in sb_markers:
		timemarker_obj = convproj_obj.timemarker__add()
		timemarker_obj.position = marker.position
		if marker.label: timemarker_obj.visual.name = marker.label
		if marker.comment: timemarker_obj.visual.comment = marker.comment
		if marker.tag: 
			try:
				timemarker_obj.visual.color.set_hex(marker.tag)
			except:
				pass

class input_cvpj_f(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'soundbridge'
	def get_name(self): return 'SoundBridge'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['audio_filetypes'] = ['wav']
		in_dict['audio_stretch'] = ['warp']
		in_dict['auto_types'] = ['pl_points']
		in_dict['file_ext'] = ['soundbridge']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv', 'loop_adv_off']
		in_dict['plugin_ext'] = ['vst2']
		in_dict['plugin_included'] = ['native:soundbridge']
		in_dict['audio_nested'] = True
	def supported_autodetect(self): return True
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_soundbridge

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'

		project_obj = proj_soundbridge.soundbridge_song()
		project_obj.load_from_file(input_file+'\\project.xml')

		pfreq = int(project_obj.sampleRate)/2
		convproj_obj.set_timings(pfreq, False)

		globalstore.datadef.load('soundbridge', './data_main/datadef/soundbridge.ddef')
		globalstore.dataset.load('soundbridge', './data_main/dataset/soundbridge.dset')

		for audiosource in project_obj.pool.audioSources:
			filename = audiosource.fileName
			ofilename = filename
			if input_file.endswith('.soundbridge'): ofilename = os.path.join(input_file, filename)
			sampleref_obj = convproj_obj.sampleref__add(filename, ofilename, None)

		master_track = project_obj.masterTrack

		add_params(project_obj.masterTrack.state, convproj_obj.track_master.params)
		track_visual(convproj_obj.track_master.visual, project_obj.masterTrack)
		do_fx(convproj_obj, project_obj.masterTrack, convproj_obj.track_master)

		for x in master_track.automationContainer.automationTracks:
			if x.parameterIndex == 2: add_auto('vol', convproj_obj, ['master', 'vol'], x.blocks, 0, 1)
			if x.parameterIndex == 3: add_auto(None, convproj_obj, ['master', 'pan'], x.blocks, -.5, 2)

		for num, sb_track in enumerate(master_track.tracks):
			make_track(convproj_obj, sb_track, None, num, pfreq)

		sb_timeSignature = project_obj.timeline.timeSignature
		sb_tempo = project_obj.timeline.tempo

		do_markers(convproj_obj, project_obj.timeline.markers)

		convproj_obj.timesig[0] = sb_timeSignature.timeSigNumerator
		convproj_obj.timesig[1] = sb_timeSignature.timeSigDenominator
		convproj_obj.params.add('bpm', project_obj.tempo, 'float')

		for x in sb_tempo.sections:
			autopl_obj = convproj_obj.automation.add_pl_points(['main', 'bpm'], 'float')
			autopl_obj.time.position = x.position
			autopl_obj.time.duration = x.length

			autopoint_obj = autopl_obj.data.add_point()
			autopoint_obj.pos = 0
			autopoint_obj.value = x.startTempo
			autopoint_obj.type = 'normal'
		
			autopoint_obj = autopl_obj.data.add_point()
			autopoint_obj.pos = x.length-1
			autopoint_obj.value = x.endTempo
			autopoint_obj.type = 'normal'

		projmeta = project_obj.metadata
		if 'TransportLoop' in projmeta: convproj_obj.loop_active = projmeta['TransportLoop'] == 'true'
		if 'TransportPlayPositionL' in projmeta: convproj_obj.loop_start = int(projmeta['TransportPlayPositionL'])
		if 'TransportPlayPositionR' in projmeta: convproj_obj.loop_end = int(projmeta['TransportPlayPositionR'])