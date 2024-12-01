# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import uuid
import os
import shutil
from functions import xtramath

class output_midi(plugins.base):
	def is_dawvert_plugin(self):
		return 'output'
	
	def get_shortname(self):
		return 'bandlab_blx'
	
	def get_name(self):
		return 'BandLab BLX'
	
	def gettype(self):
		return 'r'
	
	def get_prop(self, in_dict): 
		in_dict['audio_filetypes'] = ['wav', 'mp3', 'flac']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['projtype'] = 'r'
		in_dict['fxtype'] = 'groupreturn'
		in_dict['time_seconds'] = True
		in_dict['file_ext'] = 'blx'
		in_dict['placement_cut'] = True
		in_dict['plugin_included'] = ['native:bandlab']

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import proj_bandlab

		convproj_obj.change_timings(4, False)
		
		project_obj = proj_bandlab.bandlab_project()

		auxchannel_obj = proj_bandlab.bandlab_auxChannel(None)
		auxchannel_obj.id = 'aux1'
		project_obj.auxChannels.append(auxchannel_obj)

		project_obj.genres = [{"id": "other", "name": "Other"}]
		project_obj.id = str(uuid.uuid4())

		bpm = convproj_obj.params.get('bpm', 120).value

		project_obj.volume = convproj_obj.track_master.params.get('vol', 1).value

		tempomul = 120/bpm

		project_obj.metronome['bpm'] = int(bpm)
		project_obj.metronome['signature'] = {"notesCount": 4, "noteValue": 4}

		project_obj.parentId = str(uuid.uuid4())

		self.samplerKits = proj_bandlab.bandlab_samplerKits(None)

		creatorId = str(uuid.uuid4())

		sampleref_assoc = {}
		sampleref_ext = {}
		for sampleref_id, sampleref_obj in convproj_obj.sampleref__iter():
			uuiddata = str(uuid.uuid4())
			sampleref_assoc[sampleref_id] = uuiddata
			sampleref_ext[sampleref_id] = sampleref_obj.fileref.file.extension

			bl_sample = proj_bandlab.bandlab_sample(None) 
			bl_sample.creatorId = creatorId
			bl_sample.duration = sampleref_obj.dur_sec
			bl_sample.id = uuiddata

			project_obj.samples.append(bl_sample)

		tracknum = 0
		for trackid, track_obj in convproj_obj.track__iter():

			if track_obj.type in ['instrument', 'audio']:
				blx_track = proj_bandlab.bandlab_track(None) 
				blx_track.automation = proj_bandlab.bandlab_track_automation(None)
				blx_track.automation.id = str(uuid.uuid4())
				blx_track.autoPitch = proj_bandlab.bandlab_autoPitch(None)
				blx_track.id = str(uuid.uuid4())
				blx_track.effectsData = {"displayName": None, "link": None, "originalPresetId": None}
				auxsend_obj = proj_bandlab.bandlab_auxSend(None)
				auxsend_obj.id = 'aux1'
				blx_track.auxSends.append(auxsend_obj)

				blx_track.order = tracknum

				blx_track.name = track_obj.visual.name
				if track_obj.visual.color:
					blx_track.color = '#'+track_obj.visual.color.get_hex().upper()
					blx_track.colorName = 'Custom'

				blx_track.isMuted = not track_obj.params.get('enabled', False).value
				blx_track.isSolo = track_obj.params.get('solo', False).value
				blx_track.volume = track_obj.params.get('vol', 1).value
				blx_track.pan = track_obj.params.get('pan', 0).value

				if track_obj.type == 'audio':
					track_obj.placements.pl_audio.sort()
					for audiopl_obj in track_obj.placements.pl_audio:
						blx_region = proj_bandlab.bandlab_region(None)

						add_region_common(blx_region, audiopl_obj, blx_track, tempomul)

						sp_obj = audiopl_obj.sample
						blx_region.pitchShift = sp_obj.pitch
						blx_region.gain = sp_obj.vol
						blx_region.playbackRate = sp_obj.stretch.calc_real_speed

						blx_region.fadeIn = audiopl_obj.fade_in.get_dur_seconds(bpm)
						blx_region.fadeOut = audiopl_obj.fade_out.get_dur_seconds(bpm)

						blx_region.sampleId = sampleref_assoc[sp_obj.sampleref]
						blx_region.file = sampleref_assoc[sp_obj.sampleref]+'.'+sampleref_ext[sp_obj.sampleref]
						blx_track.regions.append(blx_region)

				project_obj.tracks.append(blx_track)

			tracknum += 1

		if dawvert_intent.output_mode == 'file':
			folder, filename = os.path.split(dawvert_intent.output_file)
			namet = os.path.splitext(filename)[0]
			foldpath = os.path.join(folder, namet)
			
			os.makedirs(os.path.join(folder, namet, 'Assets'), exist_ok=True)
			os.makedirs(os.path.join(folder, namet, 'Assets', 'Audio'), exist_ok=True)
			os.makedirs(os.path.join(folder, namet, 'Assets', 'MIDI'), exist_ok=True)

			for sampleref_id, sampleref_obj in convproj_obj.sampleref__iter():
				outfile = sampleref_assoc[sampleref_id]+'.'+sampleref_ext[sampleref_id]
				a_in = sampleref_obj.fileref.get_path(None, False)
				a_out = os.path.join(folder, namet, 'Assets', 'Audio', outfile)
				try:
					shutil.copyfile(a_in, a_out)
				except:
					pass

			os.makedirs(foldpath, exist_ok=True)
			outpath = os.path.join(folder, namet, filename)
			project_obj.save_to_file(outpath)

def add_region_common(blx_region, audiopl_obj, blx_track, tempomul):
	blx_region.trackId = blx_track.id
	blx_region.id = str(uuid.uuid4())
	blx_region.startPosition = audiopl_obj.time.position_real
	blx_region.endPosition = blx_region.startPosition+audiopl_obj.time.duration_real
	blx_region.name = audiopl_obj.visual.name

	cut_type = audiopl_obj.time.cut_type

	blx_region.sampleStartPosition += blx_region.startPosition

	cut_start = (audiopl_obj.time.cut_start*tempomul)/8
	cut_loopend = (audiopl_obj.time.cut_loopend*tempomul)/8

	if cut_type == 'cut':
		blx_region.sampleOffset += cut_start
