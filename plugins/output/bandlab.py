# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import uuid
import os
import shutil
from functions import data_values
from functions import xtramath

class output_bandlab(plugins.base):
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
		in_dict['audio_stretch'] = ['rate']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['file_ext'] = 'blx'
		in_dict['placement_cut'] = True
		in_dict['plugin_included'] = ['native:bandlab']

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import proj_bandlab

		convproj_obj.change_timings(1, True)
		
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
		project_obj.creator['id'] = creatorId
		project_obj.song = {
			"author": {
				"conversationId": None,
				"id": creatorId,
				"name": "DawVert",
				"type": "Computer Software",
				"username": ""
			},
			"canEdit": True,
			"counters": {
				"collaborators": 0,
				"comments": 0,
				"forks": 0,
				"likes": 0,
				"plays": 0,
				"publicRevisions": 0
			},
			"id": "026f6166-72ae-ef11-88cd-6045bd345b20",
			"isFork": False,
			"isForkable": False,
			"isPublic": False,
			"name": "audioc",
			"original": None,
			"originalSongId": None,
			"picture": {
				"color": None,
				"isDefault": True,
				"url": "https://bandlabimages.azureedge.net/v1.0/songs/default/"
			},
			"slug": "dawvert_created",
			"source": {
				"id": "00000000-0000-0000-0000-000000000000",
				"type": "Revision"
			},
			"stamp": None
		}

		sampleref_assoc = {}
		sampleref_ext = {}

		notelist_assoc = {}

		for sampleref_id, sampleref_obj in convproj_obj.sampleref__iter():
			uuiddata = str( data_values.bytes__to_uuid( sampleref_id.encode() ) )
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
				blx_track.id = str(uuid.uuid4())
				auxsend_obj = proj_bandlab.bandlab_auxSend(None)
				auxsend_obj.id = 'aux1'
				blx_track.auxSends.append(auxsend_obj)

				do_automation(convproj_obj, ['track', trackid, 'pan'], blx_track.automation.pan)
				do_automation(convproj_obj, ['track', trackid, 'vol'], blx_track.automation.volume)

				blx_track.order = tracknum

				blx_track.name = track_obj.visual.name
				if track_obj.visual.color:
					blx_track.color = '#'+track_obj.visual.color.get_hex().upper()
					blx_track.colorName = 'Custom'

				blx_track.isMuted = not track_obj.params.get('enabled', False).value
				blx_track.isSolo = track_obj.params.get('solo', False).value
				blx_track.volume = track_obj.params.get('vol', 1).value
				blx_track.pan = track_obj.params.get('pan', 0).value

				make_plugins_fx(convproj_obj, blx_track.effects, track_obj.plugslots.slots_audio)

				if track_obj.type == 'audio':
					blx_track.effectsData = {"displayName": None, "link": None, "originalPresetId": None}
					blx_track.autoPitch = proj_bandlab.bandlab_autoPitch(None)
					track_obj.placements.pl_audio.sort()
					for audiopl_obj in track_obj.placements.pl_audio:
						blx_region = proj_bandlab.bandlab_region(None)

						sp_obj = audiopl_obj.sample

						add_region_common(blx_region, audiopl_obj, blx_track, tempomul, False)

						blx_region.pitchShift = sp_obj.pitch
						blx_region.gain = sp_obj.vol
						blx_region.playbackRate = sp_obj.stretch.calc_tempo_speed/tempomul

						blx_region.fadeIn = audiopl_obj.fade_in.get_dur_seconds(bpm)
						blx_region.fadeOut = audiopl_obj.fade_out.get_dur_seconds(bpm)

						blx_region.sampleId = sampleref_assoc[sp_obj.sampleref]
						blx_region.file = sampleref_assoc[sp_obj.sampleref]+'.'+sampleref_ext[sp_obj.sampleref]
						blx_track.regions.append(blx_region)

				if track_obj.type == 'instrument':
					blx_track.type = 'piano'
					blx_track.soundbank = 'studio-grand-v2-v4'

					track_obj.placements.pl_audio.sort()
					for notespl_obj in track_obj.placements.pl_notes:
						notebytes = notespl_obj.notelist.getvalue()
						uuiddata = str( data_values.bytes__to_uuid( notebytes ) )

						if uuiddata not in notelist_assoc:
							notelist_assoc[uuiddata] = notespl_obj.notelist
							bl_sample = proj_bandlab.bandlab_sample(None) 
							bl_sample.creatorId = creatorId
							bl_sample.isMidi = True
							bl_sample.id = uuiddata
							project_obj.samples.append(bl_sample)

						blx_region = proj_bandlab.bandlab_region(None)
						add_region_common(blx_region, notespl_obj, blx_track, tempomul, True)
						blx_region.file = uuiddata+'.mid'
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

			for notelist_id, notelist_obj in notelist_assoc.items():
				notelist_obj.midi_to(os.path.join(folder, namet, 'Assets', 'MIDI', notelist_id+'.mid'), bpm)

			for sampleref_id, sampleref_obj in convproj_obj.sampleref__iter():
				outfile = sampleref_assoc[sampleref_id]+'.'+sampleref_ext[sampleref_id]
				a_in = sampleref_obj.fileref.get_path(None, False)
				a_out = os.path.join(folder, namet, 'Assets', 'Audio', outfile)
				try:
					sampleref_obj.copy_resample(None, a_out)
				except:
					pass

			os.makedirs(foldpath, exist_ok=True)
			outpath = os.path.join(folder, namet, filename)
			project_obj.save_to_file(outpath)

def do_automation(convproj_obj, autoloc, blx_auto):
	ap_f, ap_d = convproj_obj.automation.get(autoloc, 'float')
	if ap_f: 
		if ap_d.u_nopl_points:
			for autopoint in ap_d.nopl_points:
				blx_auto.add_point(autopoint.pos, autopoint.value)

def make_plugins_fx(convproj_obj, effects, fxslots_audio):
	from objects.file_proj import proj_bandlab
	for pluginid in fxslots_audio:
		plugin_found, plugin_obj = convproj_obj.plugin__get(pluginid)
		if plugin_found: 
			if plugin_obj.check_wildmatch('native', 'bandlab', None):
				blx_effect = proj_bandlab.bandlab_effect(None)
				blx_effect.slug = plugin_obj.type.subtype

				paramlist = plugin_obj.datavals.list()
				if paramlist:
					for param_id in paramlist:
						blx_effect.params[param_id] = plugin_obj.datavals.get(param_id, '')
						blx_effect.automation[param_id] = proj_bandlab.bandlab_automation()

				paramlist = plugin_obj.params.list()
				if paramlist:
					for param_id in paramlist:
						blx_effect.params[param_id] = plugin_obj.params.get(param_id, 0).value
						blx_effect.automation[param_id] = proj_bandlab.bandlab_automation()
						do_automation(convproj_obj, ['plugin', pluginid, param_id], blx_effect.automation[param_id])

				effects.append(blx_effect)

def add_region_common(blx_region, audiopl_obj, blx_track, tempomul, ismidi):
	blx_region.trackId = blx_track.id
	blx_region.id = str(uuid.uuid4())
	blx_region.startPosition = (audiopl_obj.time.position/2)*tempomul
	blx_region.endPosition = ((audiopl_obj.time.position+audiopl_obj.time.duration)/2)*tempomul
	blx_region.name = audiopl_obj.visual.name

	cut_type = audiopl_obj.time.cut_type

	blx_region.sampleStartPosition += blx_region.startPosition

	cut_start = audiopl_obj.time.cut_start

	if cut_type == 'cut':
		blx_region.sampleOffset += (cut_start/2)*tempomul
