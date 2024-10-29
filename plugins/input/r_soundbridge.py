# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import base64
import numpy as np
import io
import os
from objects.convproj import fileref

vl_dtype = np.dtype([('id', '>I'),('pos', '>I'),('dur', '>I'),('key', 'B'),('vol', 'B'),('unk1', 'B'),('unk2', 'B')])

def parse_notes(notes_data):
	unk_x = notes_data.read(4)
	dataread = notes_data.read()
	numnotes = len(dataread)//vl_dtype.itemsize
	notedata = np.frombuffer(dataread[0:numnotes*vl_dtype.itemsize], dtype=vl_dtype)
	return notedata[np.where(notedata['dur']!=0)]

def make_track(convproj_obj, sb_track, groupname, num):
	metadata = sb_track.metadata
	trackcolor = metadata['TrackColor'] if 'TrackColor' in metadata else None
	cvpj_trackid = ('main' if not groupname else groupname)+'__'+str(num)

	if sb_track.type == 4:
		track_obj = convproj_obj.add_track(cvpj_trackid, 'instrument', 1, False)
		track_obj.visual.name = sb_track.name
		track_obj.visual.color.set_hex(trackcolor)
		if groupname:
			track_obj.group = groupname
			track_obj.sends.to_master_active = False
		for block in sb_track.blocks:
			placement_obj = track_obj.placements.add_notes()
			placement_obj.time.set_posdur(block.position, block.positionEnd-block.positionStart)
			if block.loopEnabled: placement_obj.time.set_loop_data(block.loopOffset, block.loopOffset, block.framesCount)
			blockdata = base64.b64decode(block.blockData + '==')
			for note in parse_notes(io.BytesIO(blockdata)): placement_obj.notelist.add_r(note['pos'], note['dur'], note['key']-60, note['vol']/127, None)

	if sb_track.type == 3:
		track_obj = convproj_obj.add_track(cvpj_trackid, 'audio', 1, False)
		track_obj.visual.name = sb_track.name
		track_obj.visual.color.set_hex(trackcolor)
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

					stretch_obj = sp_obj.stretch
					stretch_obj.preserve_pitch = True
					stretch_obj.is_warped = True

					for stretchMark in blockevent.stretchMarks:
						warp_point_obj = stretch_obj.add_warp_point()
						warp_point_obj.beat = stretchMark.newPosition/44100
						warp_point_obj.second = stretchMark.initPosition/(44100*2)
						#print(stretchMark.initPosition, stretchMark.newPosition)
					stretch_obj.calc_warp_points()

	if sb_track.type == 2:
		return_obj = convproj_obj.track_master.add_return(cvpj_trackid)
		return_obj.visual.name = sb_track.name
		return_obj.visual.color.set_hex(trackcolor)

	if sb_track.type == 1:
		track_obj = convproj_obj.add_group(cvpj_trackid)
		track_obj.visual.name = sb_track.name
		track_obj.visual.color.set_hex(trackcolor)
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
