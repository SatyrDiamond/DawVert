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

sb_auto_dtype = np.dtype([('val', '>f'),('unk1', '>f'),('unk2', '>f'),('pos', '>I')])

def decode_chunk(statedata):
	statedata = statedata.replace('.', '/')
	return base64.b64decode(statedata)

def parse_auto(notes_data):
	unk_x = notes_data.read(4)
	unk_y = notes_data.read(4)
	dataread = notes_data.read()
	numnotes = len(dataread)//sb_auto_dtype.itemsize
	autodata = np.frombuffer(dataread[0:numnotes*sb_auto_dtype.itemsize], dtype=sb_auto_dtype)
	return autodata[np.where(autodata['unk1']!=0)]

def add_auto(convproj_obj, autoloc, sb_blocks, add, mul):
	for block in sb_blocks:
		autopl_obj = convproj_obj.automation.add_pl_points(autoloc, 'float')
		autopl_obj.time.position = block.position
		autopl_obj.time.duration = block.framesCount
		for point in parse_auto(io.BytesIO(decode_chunk(block.blockData))):
			autopoint_obj = autopl_obj.data.add_point()
			autopoint_obj.pos = point['pos']
			autopoint_obj.value = (point['val']+add)*mul
			autopoint_obj.type = 'normal'

def add_auto_eq(convproj_obj, autoloc, sb_blocks, val, invert):
	for block in sb_blocks:
		autopl_obj = convproj_obj.automation.add_pl_points(autoloc, 'float')
		autopl_obj.time.position = block.position
		autopl_obj.time.duration = block.framesCount
		for point in parse_auto(io.BytesIO(decode_chunk(block.blockData))):
			autopoint_obj = autopl_obj.data.add_point()
			autopoint_obj.pos = point['pos']
			autopoint_obj.value = point['val']==val
			if invert: autopoint_obj.value = not autopoint_obj.value
			autopoint_obj.type = 'instant'

sb_notes_dtype = np.dtype([('id', '>I'),('pos', '>I'),('dur', '>I'),('key', 'B'),('vol', 'B'),('unk1', 'B'),('unk2', 'B')])

def parse_notes(notes_data):
	unk_x = notes_data.read(4)
	dataread = notes_data.read()
	numnotes = len(dataread)//sb_notes_dtype.itemsize
	notedata = np.frombuffer(dataread[0:numnotes*sb_notes_dtype.itemsize], dtype=sb_notes_dtype)
	return notedata[np.where(notedata['dur']!=0)]

def add_params(stateobj, params_obj):
	statebin = decode_chunk(stateobj)
	mute, vol, unk, pan = struct.unpack('>ffff', statebin)
	params_obj.add('enabled', mute!=1, 'bool')
	params_obj.add('vol', vol, 'float')
	params_obj.add('pan', (pan-0.5)*2, 'float')

def make_track(convproj_obj, sb_track, groupname, num):
	from functions_plugin_ext import plugin_vst2
	from functions_plugin_ext import plugin_vst3
	metadata = sb_track.metadata
	trackcolor = metadata['TrackColor'] if 'TrackColor' in metadata else None
	cvpj_trackid = ('main' if not groupname else groupname)+'__'+str(num)

	returnids = 0

	if sb_track.type == 4:
		track_obj = convproj_obj.add_track(cvpj_trackid, 'instrument', 1, False)
		track_obj.visual.name = sb_track.name
		track_obj.visual.color.set_hex(trackcolor)
		add_params(sb_track.state, track_obj.params)
		if groupname:
			track_obj.group = groupname
			track_obj.sends.to_master_active = False
		for block in sb_track.blocks:
			placement_obj = track_obj.placements.add_notes()
			placement_obj.time.set_posdur(block.position, block.positionEnd-block.positionStart)
			if block.loopEnabled: placement_obj.time.set_loop_data(block.loopOffset, block.loopOffset, block.framesCount)
			else: placement_obj.time.set_offset(block.positionStart)
			blockdata = decode_chunk(block.blockData)
			for note in parse_notes(io.BytesIO(blockdata)): placement_obj.notelist.add_r(note['pos'], note['dur'], note['key']-60, note['vol']/127, None)
		if sb_track.midiInstrument:
			midiinst = sb_track.midiInstrument
			uiddata = decode_chunk(midiinst.uid)
			statedata = decode_chunk(midiinst.state)
			try:
				if len(uiddata) == 16 and statedata:
					if uiddata[0:8] == b'\x00\x00\x00\x00SV2T':
						plugin_obj, track_obj.inst_pluginid = convproj_obj.add_plugin_genid('external', 'vst2', 'win')
						plugin_obj.role = 'synth'
						if statedata[28:32] == b'FBCh':
							plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', None, struct.unpack('>I', uiddata[8:12])[0], 'chunk', statedata[180:], None)
			except:
				pass

	if sb_track.type == 3:
		track_obj = convproj_obj.add_track(cvpj_trackid, 'audio', 1, False)
		track_obj.visual.name = sb_track.name
		track_obj.visual.color.set_hex(trackcolor)
		add_params(sb_track.state, track_obj.params)

		if groupname:
			track_obj.group = groupname
			track_obj.sends.to_master_active = False
		if sb_track.blockContainers:
			for block in sb_track.blockContainers[0].blocks:
				placement_obj = track_obj.placements.add_nested_audio()
				clipmetadata = sb_track.metadata
				placement_obj.visual.name = block.name
				if 'TrackColor' in clipmetadata: placement_obj.visual.color.set_hex(clipmetadata['TrackColor'])
				placement_obj.time.set_posdur(block.position, block.framesCount)
				for blockevent in block.events:
					placement_obj = placement_obj.add()
					placement_obj.time.set_posdur(blockevent.position, blockevent.framesCount)
					placement_obj.time.set_offset(blockevent.positionStart)
					sp_obj = placement_obj.sample
					sp_obj.sampleref = blockevent.fileName

					sp_obj.vol = xtramath.from_db(blockevent.gain)
					sp_obj.pitch = math.log2(1/blockevent.pitch)*-12

					stretch_obj = sp_obj.stretch
					stretch_obj.preserve_pitch = True
					stretch_obj.is_warped = True

					placement_obj.fade_in.set_dur(blockevent.fadeInLength/22050, 'beats')
					placement_obj.fade_out.set_dur(blockevent.fadeOutLength/22050, 'beats')

					for stretchMark in blockevent.stretchMarks:
						warp_point_obj = stretch_obj.add_warp_point()
						warp_point_obj.beat = stretchMark.newPosition/44100
						warp_point_obj.second = stretchMark.initPosition/(44100*2)
					stretch_obj.calc_warp_points()

	if sb_track.type in [3,4]:
		for x in sb_track.sendsAutomationContainer.automationTracks:
			splitret = x.returnTrackPath.split('/')
			if len(splitret) == 3:
				if splitret[0]=='' and splitret[1].isnumeric() and splitret[2]=='R':
					sendautoid = cvpj_trackid+'__'+'return__'+str(splitret[1])
					track_obj.sends.add('return__'+str(splitret[1]), sendautoid, x.defaultValue)
					add_auto(convproj_obj, ['send', sendautoid, 'amount'], x.blocks, 0, 1)
		for x in sb_track.automationContainer.automationTracks:
			if x.parameterIndex == 2: add_auto(convproj_obj, ['track', cvpj_trackid, 'vol'], x.blocks, 0, 1)
			if x.parameterIndex == 3: add_auto(convproj_obj, ['track', cvpj_trackid, 'pan'], x.blocks, -.5, 2)

	if sb_track.type == 2:
		returnid = 'return__'+str(returnids)
		track_obj = convproj_obj.track_master.add_return(returnid)
		track_obj.visual.name = sb_track.name
		track_obj.visual.color.set_hex(trackcolor)
		add_params(sb_track.state, track_obj.params)
		returnids += 1
		for x in sb_track.automationContainer.automationTracks:
			if x.parameterIndex == 2: add_auto(convproj_obj, ['return', returnid, 'vol'], x.blocks, 0, 1)
			if x.parameterIndex == 3: add_auto(convproj_obj, ['return', returnid, 'pan'], x.blocks, -.5, 2)

	if sb_track.type == 1:
		track_obj = convproj_obj.add_group(cvpj_trackid)
		track_obj.visual.name = sb_track.name
		track_obj.visual.color.set_hex(trackcolor)
		add_params(sb_track.state, track_obj.params)
		for x in sb_track.automationContainer.automationTracks:
			if x.parameterIndex == 2: add_auto(convproj_obj, ['group', cvpj_trackid, 'vol'], x.blocks, 0, 1)
			if x.parameterIndex == 3: add_auto(convproj_obj, ['group', cvpj_trackid, 'pan'], x.blocks, -.5, 2)

		for gnum, gb_track in enumerate(sb_track.tracks):
			make_track(convproj_obj, gb_track, cvpj_trackid, gnum)


class input_cvpj_f(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'soundbridge'
	def get_name(self): return 'SoundBridge'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['audio_filetypes'] = ['wav']
		in_dict['auto_types'] = ['pl_points']
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv']
		in_dict['audio_stretch'] = ['warp']
		in_dict['audio_nested'] = True
	def supported_autodetect(self): return True
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_soundbridge

		convproj_obj.type = 'r'
		convproj_obj.set_timings(88200/4, False)

		project_obj = proj_soundbridge.soundbridge_song()
		project_obj.load_from_file(input_file+'\\project.xml')

		for audiosource in project_obj.pool.audioSources:
			filename = audiosource.fileName
			ofilename = filename
			if input_file.endswith('.soundbridge'): ofilename = os.path.join(input_file, filename)
			sampleref_obj = convproj_obj.add_sampleref(filename, ofilename, None)

		master_track = project_obj.masterTrack

		for num, sb_track in enumerate(master_track.tracks):
			make_track(convproj_obj, sb_track, None, num)

		sb_timeSignature = project_obj.timeline.timeSignature
		sb_tempo = project_obj.timeline.tempo

		for marker in project_obj.timeline.markers:
			timemarker_obj = convproj_obj.add_timemarker()
			timemarker_obj.position = marker.position
			if marker.label: timemarker_obj.visual.name = marker.label
			if marker.tag: 
				try:
					timemarker_obj.visual.color.set_hex(marker.tag)
				except:
					pass

		convproj_obj.timesig[0] = sb_timeSignature.timeSigNumerator
		convproj_obj.timesig[1] = sb_timeSignature.timeSigDenominator
		convproj_obj.params.add('bpm', sb_tempo.tempo, 'float')

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
