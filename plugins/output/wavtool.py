# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import io
import zipfile
import uuid
import lxml.etree as ET
import os
import math
import base64
from functions import xtramath

def addsample(zip_wt, filepath, alredyexists): 
	global audio_id
	datauuid = str(uuid.uuid4())
	if alredyexists == False:
		if filepath not in audio_id:
			audio_id[filepath] = datauuid
			if os.path.exists(filepath):
				filename, filetype = os.path.basename(filepath).split('.')

				if datauuid not in zip_wt.namelist():
					if filetype in ['wav', 'mp3']:
						zip_wt.write(filepath, datauuid+'.'+filetype)
					else:
						zip_wt.writestr(datauuid+'.wav', audio.convert_to_wav(filepath))

				zip_wt.write(filepath, datauuid+'.'+filetype)
			datauuid = audio_id[filepath]
		else:
			datauuid = audio_id[filepath]
	else:
		if os.path.exists(filepath):
			filetype = os.path.basename(filepath).split('.')[1]
			zip_wt.write(filepath, datauuid+'.'+filetype)

	return datauuid
		   

def make_automation(autoid, trackid, autoname, stripdevice, trackdevice, autopoints, color, istrack):
	from objects.file_proj import proj_wavtool
	endtext = (autoid+'-'+trackid) if istrack == True else autoname
	wt_autoid_AutoTrack = 'DawVert-AutoTrack-'+endtext
	wt_autoid_AutoRec = 'DawVert-AutoRec-'+endtext
	wt_autoid_AutoStrip = 'DawVert-AutoStrip-'+endtext
	wt_autoid_AutoPortalIn = 'DawVert-AutoPortalIn-'+endtext
	wt_autoid_AutoPortalOut = 'DawVert-AutoPortalOut-'+endtext
	wt_autoid_ChanStrip = 'DawVert-ChanStrip-'+trackid

	wavtool_obj.devices.add_track(wt_autoid_AutoTrack)

	device_obj = wavtool_obj.devices.add_device(wt_autoid_AutoTrack, wt_autoid_AutoRec)
	device_obj.name = 'Track Automation'
	device_obj.type = 'PortalOut'
	device_obj.data['portalType'] = 'Mono'
	device_obj.x = 10
	device_obj.y = 35.75

	device_obj = wavtool_obj.devices.add_device(wt_autoid_AutoTrack, wt_autoid_AutoStrip)
	device_obj.name = 'Channel Strip'
	device_obj.type = 'JS'
	device_obj.sourceId = '689d5a16-8812-4b98-989a-1444069cded3'
	device_obj.x = 210
	device_obj.y = 10

	device_obj = wavtool_obj.devices.add_device(wt_autoid_AutoTrack, wt_autoid_AutoPortalIn)
	device_obj.name = 'Gain'
	device_obj.type = 'PortalIn'
	device_obj.data['portalType'] = 'Mono'
	device_obj.x = 590
	device_obj.y = 35.75

	device_obj = wavtool_obj.devices.add_device(trackdevice, wt_autoid_AutoPortalOut)
	device_obj.name = 'Gain'
	device_obj.type = 'PortalOut'
	device_obj.data['portalType'] = 'Mono'
	device_obj.x = 10
	device_obj.y = 85.75
	
	wavtool_obj.devices.add_cable(wt_autoid_AutoTrack, 'output', wt_autoid_AutoRec, 'input')
	wavtool_obj.devices.add_cable(wt_autoid_AutoRec, 'output', wt_autoid_AutoStrip, 'input')
	wavtool_obj.devices.add_cable(wt_autoid_AutoPortalIn, 'output', wt_autoid_AutoPortalOut, 'input')
	wavtool_obj.devices.add_cable(wt_autoid_AutoPortalOut, 'output', stripdevice, autoname)
	wavtool_obj.devices.add_cable(wt_autoid_AutoStrip, 'output', wt_autoid_AutoPortalIn, 'input')

	wt_points = []
	for point in autopoints:
		wt_points.append({"time": point.pos, "value": point.value, "exponent": 1, "lifted": False})

	wavtool_track = proj_wavtool.wavtool_track(None)
	wavtool_track.id = wt_autoid_AutoTrack
	wavtool_track.type = "Automation"
	wavtool_track.name = autoname
	wavtool_track.height = 60
	wavtool_track.color = "#"+color
	wavtool_track.points = wt_points
	wavtool_track.channelStripId = wt_autoid_AutoStrip
	return wavtool_track



class output_wavtool(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'output'
	def get_name(self): return 'Wavtool'
	def get_shortname(self): return 'wavtool'
	def gettype(self): return 'r'
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'zip'
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv']
		in_dict['audio_stretch'] = ['warp', 'rate']
		in_dict['plugin_included'] = ['universal:sampler:single']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['plugin_ext'] = ['vst2']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['projtype'] = 'r'
	def parse(self, convproj_obj, output_file):
		from functions_plugin_ext import plugin_vst2
		from objects.file_proj import proj_wavtool

		global audio_id
		global wavtool_obj

		convproj_obj.change_timings(1, True)

		audio_id = {}

		wavtool_obj = proj_wavtool.wavtool_project(None)

		zip_bio = io.BytesIO()
		zip_wt = zipfile.ZipFile(zip_bio, mode='w')

		bpm = convproj_obj.params.get('bpm',120).value
		bpmmul = (bpm/120)

		wavtool_obj.devices.add_track('master')

		device_obj = wavtool_obj.devices.add_device('master', 'master')
		device_obj.name = 'Master Out'
		device_obj.type = 'PortalIn'
		device_obj.data['portalType'] = 'Stereo'
		device_obj.x = 910
		device_obj.y = 35.75

		device_obj = wavtool_obj.devices.add_device('master', 'masterBus')
		device_obj.name = 'Master Bus'
		device_obj.type = 'JS'
		device_obj.sourceId = '66cff321-ae21-444d-a5dc-7c428a4fba25'
		device_obj.x = 10
		device_obj.y = 10
		device_obj.data_internal['order'] = 1

		device_obj = wavtool_obj.devices.add_device('master', 'metronome')
		device_obj.name = 'Metronome'
		device_obj.type = 'JS'
		device_obj.sourceId = '2bfdb690-b27e-441e-a2eb-f820b907f78e'
		device_obj.x = 320
		device_obj.y = 110
		device_obj.data_internal['order'] = 1

		device_obj = wavtool_obj.devices.add_device('master', 'masterFader')
		device_obj.name = 'Master Fader'
		device_obj.type = 'JS'
		device_obj.sourceId = '0c1291d9-cc0a-4d2f-949c-81e1c3e25106'
		device_obj.x = 310
		device_obj.y = 10
		device_obj.data['inputs'] = {"gain": convproj_obj.track_master.params.get('vol', 1).value}

		device_obj = wavtool_obj.devices.add_device('master', 'sendSum')
		device_obj.name = 'Send Sum'
		device_obj.type = 'JS'
		device_obj.sourceId = 'ec86ba8c-4336-4856-8a70-cf0a74a4b423'
		device_obj.x = 210
		device_obj.y = 10
		device_obj.data_internal['order'] = 1

		device_obj = wavtool_obj.devices.add_device('master', 'auxSum')
		device_obj.name = 'Aux Sum'
		device_obj.type = 'JS'
		device_obj.sourceId = 'ec86ba8c-4336-4856-8a70-cf0a74a4b423'
		device_obj.x = 610
		device_obj.y = 10
		device_obj.data_internal['order'] = 1

		wavtool_obj.devices.add_cable('auxSum', 'output', 'master', 'input')
		wavtool_obj.devices.add_cable('masterBus', 'output', 'sendSum', 'inputs[0]')
		wavtool_obj.devices.add_cable('sendSum', 'output', 'masterFader', 'input')
		wavtool_obj.devices.add_cable('masterFader', 'output', 'auxSum', 'inputs[0]')
		wavtool_obj.devices.add_cable('metronome', 'output', 'auxSum', 'inputs[1]')

		if_found, mas_cvpjauto_vol = convproj_obj.automation.get_autopoints(['master','vol'])
		if if_found:
			wt_trackauto = make_automation('vol', 'master', 'gain', 'masterFader', 'master', mas_cvpjauto_vol, 'AAAAAA', False)
			wavtool_obj.tracks[wt_trackauto.id] = wt_trackauto

		#for groupid, group_obj in convproj_obj.fx__group__iter():
#
		#	if True:
		#		wt_trackid = 'DawVert-Group-'+groupid
		#		wt_trackid_MIDIRec = 'DawVert-Group-MIDIRec-'+groupid
		#		wt_trackid_AudioRec = 'DawVert-Group-AudioRec-'+groupid
		#		wt_trackid_ChanStrip = 'DawVert-Group-ChanStrip-'+groupid
		#		wt_trackid_Instrument = 'DawVert-Group-Instrument-'+groupid
		#		wt_trackid_BusSend = 'DawVert-Group-BusSend-'+groupid
		#	else:
		#		wt_trackid = ("MIDITrack-" if group_obj.type == 'instrument' else "AudioTrack-")+str(uuid.uuid4())
		#		wt_trackid_MIDIRec = 'TrackMIDIReceiver-'+str(uuid.uuid4())
		#		wt_trackid_AudioRec = 'TrackAudioReceiver-'+str(uuid.uuid4())
		#		wt_trackid_ChanStrip = 'ChannelStrip-'+str(uuid.uuid4())
		#		wt_trackid_Instrument = 'MIDIInstrument-'+str(uuid.uuid4())
		#		wt_trackid_BusSend = 'MasterBusSend-'+str(uuid.uuid4())
#
		#	wavtool_track = proj_wavtool.wavtool_track(None)
		#	wavtool_track.name = group_obj.visual.name if group_obj.visual.name else ''
		#	wavtool_track.color = '#'+group_obj.visual.color.get_hex_fb(70,70,70)
		#	wavtool_track.gain = group_obj.params.get('vol', 1.0).value
		#	wavtool_track.balance = group_obj.params.get('pan', 0).value
#
		#	wavtool_track.type = "Audio"
#
		#	wavtool_obj.devices.add_track(wt_trackid)
		#	wavtool_obj.tracks[wt_trackid] = wavtool_track
#
		#	wavtool_obj.devices.add_cable(wt_trackid, 'output', wt_trackid_AudioRec, 'input')
		#	wavtool_obj.devices.add_cable(wt_trackid_AudioRec, 'output', wt_trackid_ChanStrip, 'input')
		#	wavtool_obj.devices.add_cable(wt_trackid_ChanStrip, 'output', wt_trackid_BusSend, 'input')
		#	wavtool_obj.devices.add_cable(wt_trackid_BusSend, 'output', 'masterBus', 'inputs['+wt_trackid+']')

		for cvpj_trackid, track_obj in convproj_obj.track__iter():

			if True:
				wt_trackid = 'DawVert-Track-'+cvpj_trackid
				wt_trackid_MIDIRec = 'DawVert-MIDIRec-'+cvpj_trackid
				wt_trackid_AudioRec = 'DawVert-AudioRec-'+cvpj_trackid
				wt_trackid_ChanStrip = 'DawVert-ChanStrip-'+cvpj_trackid
				wt_trackid_Instrument = 'DawVert-Instrument-'+cvpj_trackid
				wt_trackid_BusSend = 'DawVert-BusSend-'+cvpj_trackid
			else:
				wt_trackid = ("MIDITrack-" if track_obj.type == 'instrument' else "AudioTrack-")+str(uuid.uuid4())
				wt_trackid_MIDIRec = 'TrackMIDIReceiver-'+str(uuid.uuid4())
				wt_trackid_AudioRec = 'TrackAudioReceiver-'+str(uuid.uuid4())
				wt_trackid_ChanStrip = 'ChannelStrip-'+str(uuid.uuid4())
				wt_trackid_Instrument = 'MIDIInstrument-'+str(uuid.uuid4())
				wt_trackid_BusSend = 'MasterBusSend-'+str(uuid.uuid4())

			wavtool_obj.devices.add_track(wt_trackid)

			if track_obj.type in ['instrument', 'audio']:
				wavtool_track = proj_wavtool.wavtool_track(None)
				wavtool_track.type = "MIDI" if track_obj.type == 'instrument' else "Audio"
				wavtool_track.name = track_obj.visual.name if track_obj.visual.name else ''
				wavtool_track.height = 125 if track_obj.type == 'instrument' else 160
				wavtool_track.gain = track_obj.params.get('vol', 1.0).value
				wavtool_track.balance = track_obj.params.get('pan', 0).value
				wavtool_track.color = '#'+track_obj.visual.color.get_hex_fb(50,50,50)

				#print('[output-wavtool] '+wavtool_track.type+' Track: '+wavtool_track.name)

				device_obj = wavtool_obj.devices.add_device(wt_trackid, wt_trackid_MIDIRec if track_obj.type == 'instrument' else wt_trackid_AudioRec)
				device_obj.name = 'Track MIDI' if track_obj.type == 'instrument' else 'Track Audio'
				device_obj.data['portalType'] = 'MIDI' if track_obj.type == 'instrument' else 'Stereo'
				device_obj.type = 'PortalOut'
				device_obj.x = 10
				device_obj.y = 35.75

				device_obj = wavtool_obj.devices.add_device(wt_trackid, wt_trackid_ChanStrip)
				device_obj.name = 'Channel Strip'
				device_obj.type = 'JS'
				device_obj.sourceId = 'a19792b0-326f-4b82-93a8-2422ffe215b5'
				#if track_obj.type == 'audio': device_obj.data['inputs'] = {"gain": 0.5011872336272722}
				device_obj.x = 540
				device_obj.y = 10
				device_obj.data_internal['order'] = 2

				device_obj = wavtool_obj.devices.add_device(wt_trackid, wt_trackid_BusSend)
				device_obj.name = 'Master Bus'
				device_obj.type = 'PortalIn'
				device_obj.data['portalType'] = 'Stereo'
				device_obj.x = 730
				device_obj.y = 35.75

				if track_obj.type == 'instrument':
					pluginid = track_obj.inst_pluginid
					middlenote = track_obj.datavals.get('middlenote', 0)+60
					inst_supported = False
					plugin_found, plugin_obj = convproj_obj.plugin__get(pluginid)

					if plugin_found:
						adsr_obj = plugin_obj.env_asdr_get('vol')
						adsr_decay = xtramath.clamp(adsr_obj.decay, 0.001, 32)
						adsr_attack = xtramath.clamp(adsr_obj.attack, 0.001, 32)
						adsr_sustain = adsr_obj.sustain
						adsr_release = xtramath.clamp(adsr_obj.release, 0.001, 32)
					else:
						adsr_decay = 0
						adsr_attack = 0
						adsr_sustain = 1
						adsr_release = 0

					if plugin_found:
						if plugin_obj.check_match('universal', 'sampler', 'single'):
							inst_supported = True
							
							sp_obj = plugin_obj.samplepart_get('sample')
							_, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)

							filename = sp_obj.get_filepath(convproj_obj, None)
							audiouuid = addsample(zip_wt, filename, True) if os.path.exists(filename) else ''
							device_obj = wavtool_obj.devices.add_device(wt_trackid, wt_trackid_Instrument)
							device_obj.name = 'MonoSampler'
							device_obj.type = 'JS'
							device_obj.sourceId = 'c4888b49-3a72-4b0a-bd4a-a06e9937000a'
							device_obj.x = 160
							device_obj.y = 10
							device_obj.data['inputs'] = {"gain": 1,"decay": adsr_decay*48000,"attack": adsr_attack*48000,"sustain": adsr_sustain,"release": adsr_release*48000}
							device_obj.data['constants'] = {'sample1Pitch': middlenote, 'sample1All': audiouuid}
							device_obj.data_internal['order'] = 1

						#if plugin_obj.check_match('vst2', 'win'):
						#	inst_supported = True
						#	device_obj = wavtool_obj.devices.add_device(wt_trackid, wt_trackid_Instrument)
						#	device_obj.name = plugin_obj.datavals_global.get('name', '')
						#	device_obj.type = 'Bridge'
						#	device_obj.x = 160
						#	device_obj.y = 10
#
						#	statedata = plugin_vst2.export_presetdata(plugin_obj)
#
						#	chunkdata = bytes.fromhex('7143c39fc5c129ac82cd46c16ed0d0b57240f0642c791db6bc97f5c9d36739ca')
						#	chunkdata += b'\x00'*64
						#	chunkdata += statedata
#
						#	device_obj.data['sourceName'] = plugin_obj.datavals_global.get('name', '')
						#	device_obj.data['sourceManufacturer'] = plugin_obj.datavals_global.get('creator', '')
						#	device_obj.data['inputSpec'] = {'midiInput': {'type': 'MIDI', 'name': 'In', 'expose': True}}
						#	device_obj.data['outputSpec'] = {'audioOutput': {'type': 'Stereo', 'name': 'Out', 'expose': True}}
						#	device_obj.data['encodedState'] = base64.b64encode(chunkdata).decode()
#
						#	#print(device_obj.data['encodedState'])
#
						#	device_obj.data_internal['order'] = 1

					if not inst_supported: 
						device_obj = wavtool_obj.devices.add_device(wt_trackid, wt_trackid_Instrument)
						device_obj.name = 'Simple Synth'
						device_obj.type = 'JS'
						device_obj.sourceId = 'd694ef91-e624-404d-8e34-829d9c1c04b3'
						device_obj.x = 160
						device_obj.y = 10
						device_obj.data['inputs'] = {"decay": adsr_decay*48000,"attack": adsr_attack*48000,"sustain": adsr_sustain,"release": adsr_release*48000}
						device_obj.data_internal['order'] = 3

					wavtool_obj.devices.add_cable(wt_trackid, 'output', wt_trackid_MIDIRec, 'input')
					wavtool_obj.devices.add_cable(wt_trackid_ChanStrip, 'output', wt_trackid_BusSend, 'input')
					wavtool_obj.devices.add_cable(wt_trackid_BusSend, 'output', 'masterBus', 'inputs['+wt_trackid+']')
					wavtool_obj.devices.add_cable(wt_trackid_MIDIRec, 'output', wt_trackid_Instrument, 'input')
					wavtool_obj.devices.add_cable(wt_trackid_Instrument, 'output', wt_trackid_ChanStrip, 'input')

				if track_obj.type == 'audio':
					wavtool_obj.devices.add_cable(wt_trackid, 'output', wt_trackid_AudioRec, 'input')
					wavtool_obj.devices.add_cable(wt_trackid_AudioRec, 'output', wt_trackid_ChanStrip, 'input')
					wavtool_obj.devices.add_cable(wt_trackid_ChanStrip, 'output', wt_trackid_BusSend, 'input')
					wavtool_obj.devices.add_cable(wt_trackid_BusSend, 'output', 'masterBus', 'inputs['+wt_trackid+']')

				wt_clips = []

				if track_obj.type == 'instrument':
					for notespl_obj in track_obj.placements.pl_notes:
						wavtool_clip = proj_wavtool.wavtool_clip(None)
						wavtool_clip.name = notespl_obj.visual.name if notespl_obj.visual.name else ''
						wavtool_clip.color = '#'+notespl_obj.visual.color.get_hex_fb(50,50,50)

						for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
							for t_key in t_keys:
								if 0 <= t_key+60 <= 128:
									wt_note = {}
									wt_note['pitch'] = int(t_key+60)
									wt_note['start'] = float(t_pos)
									wt_note['end'] = float(t_pos+t_dur)
									wt_note['lifted'] = False
									wt_note['velocity'] = float(t_vol)
									wavtool_clip.notes.append(wt_note)

						wavtool_clip.timelineStart = notespl_obj.time.position
						wavtool_clip.timelineEnd = notespl_obj.time.position+notespl_obj.time.duration
						wavtool_clip.loopEnd = notespl_obj.time.duration

						wavtool_clip.readStart, wavtool_clip.loopStart, wavtool_clip.loopEnd = notespl_obj.time.get_loop_data()
						if notespl_obj.time.cut_type in ['loop', 'loop_off', 'loop_adv']: wavtool_clip.loopEnabled = True
						if notespl_obj.time.cut_type == 'cut': wavtool_clip.loopEnd = (wavtool_clip.readStart+notespl_obj.time.duration)
						wavtool_track.clips.append(wavtool_clip)

				if track_obj.type == 'audio':
					for audiopl_obj in track_obj.placements.pl_audio:
						wavtool_clip = proj_wavtool.wavtool_clip(None)
						wavtool_clip.name = audiopl_obj.visual.name if audiopl_obj.visual.name else ''
						wavtool_clip.color = '#'+audiopl_obj.visual.color.get_hex_fb(50,50,50)
						wavtool_clip.timelineStart = audiopl_obj.time.position
						wavtool_clip.timelineEnd = audiopl_obj.time.position+audiopl_obj.time.duration
						wavtool_clip.loopEnd = audiopl_obj.time.duration

						if audiopl_obj.time.cut_type in ['loop', 'loop_off', 'loop_adv']:
							wavtool_clip.loopEnabled = True
							wavtool_clip.readStart, wavtool_clip.loopStart, wavtool_clip.loopEnd = audiopl_obj.time.get_loop_data()
						if audiopl_obj.time.cut_type == 'cut': wavtool_clip.loopEnd = (wavtool_clip.readStart+audiopl_obj.time.duration)

						wavtool_clip.type = "Audio"

						audiofilename = ''
						ref_found, sampleref_obj = convproj_obj.sampleref__get(audiopl_obj.sample.sampleref)
						if ref_found: audiofilename = sampleref_obj.fileref.get_path(None, False)

						audioBufferId = addsample(zip_wt, audiofilename, False)
						wavtool_clip.audioBufferId = audioBufferId

						if not audiopl_obj.sample.stretch.is_warped:
							warprate = audiopl_obj.sample.stretch.calc_tempo_speed
							if not audiopl_obj.sample.stretch.preserve_pitch:
								wavtool_clip.transpose = (math.log2(audiopl_obj.sample.stretch.calc_real_speed)*12)
							else:
								dur_sec = sampleref_obj.dur_sec
								warpdata = {}
								warpdata['sourceBPM'] = 120
								warpdata['anchors'] = {}
								warpdata['enabled'] = True
								warpdata['algorithm'] = 'Pro'
								
								warpdata['anchors']["0"] = {"destination": 0, "pinned": True}
								warpdata['anchors']["%g" % (dur_sec*2)] = {"destination": (dur_sec*2)/warprate, "pinned": True}

								wavtool_clip.warp = warpdata
								wavtool_clip.transpose = audiopl_obj.sample.pitch

						else:
							warpdata = {}
							warpdata['sourceBPM'] = 120
							warpdata['anchors'] = {}
							warpdata['enabled'] = True

							for warp_point_obj in audiopl_obj.sample.stretch.iter_warp_points():
								wt_warp_pos = (warp_point_obj.beat)
								wt_warp_pos_real = (warp_point_obj.second)*2
								warpdata['anchors']["%g" % wt_warp_pos_real] = {"destination": wt_warp_pos, "pinned": False}

							wavtool_clip.warp = warpdata

						wavtool_track.clips.append(wavtool_clip)


				wavtool_track.mute = not track_obj.params.get('on', True).value
				wavtool_track.solo = bool(track_obj.params.get('solo', False).value)
				wavtool_track.channelStripId = wt_trackid_ChanStrip
				wavtool_track.monitorInput = 1
				
				if track_obj.type == 'instrument': wavtool_track.input = None
				wavtool_obj.tracks[wt_trackid] = wavtool_track

				for autoname in [['vol','gain'],['pan','balance']]:
					if_found, autopoints = convproj_obj.automation.get_autopoints(['track',cvpj_trackid,autoname[0]])
					if if_found: 
						if autoname[0] == 'pan': autopoints.calc('addmul', 1, 0.5, 0, 0)
						autopoints.remove_instant()
						wt_trackauto = make_automation(autoname[0], cvpj_trackid, autoname[1], wt_trackid_ChanStrip, wt_trackid, autopoints, wavtool_track.color, True)
						wavtool_obj.tracks[wt_trackauto.id] = wt_trackauto

		wavtool_obj.id = "DawVertConverted-"+str(uuid.uuid4())
		wavtool_obj.loopStart = max(convproj_obj.loop_start, 0)
		wavtool_obj.loopEnd = max(convproj_obj.loop_end, 0)
		wavtool_obj.loopEnabled = convproj_obj.loop_active
		wavtool_obj.bpm = bpm
		wavtool_obj.beatNumerator, wavtool_obj.beatDenominator = convproj_obj.timesig
		wavtool_obj.name = convproj_obj.metadata.name
		wavtool_obj.arrangementFocusCategory = "TrackContent"
		wavtool_obj.headerAnchorTrackId = ('DawVert-Track-'+convproj_obj.track_order[0]) if convproj_obj.track_order else ''
		wavtool_obj.timelineAnchorTrackId = ('DawVert-Track-'+convproj_obj.track_order[0]) if convproj_obj.track_order else ''

		wavtool_obj.panelTree = {"type": "Auto", "size": 1, "units": "fr", "state": None}
		wavtool_obj.focusedTrackId = 'DawVert-Track-'+convproj_obj.track_order[0]
		wavtool_obj.selectedDeviceId = "metronome"

		wavtool_obj.loopStart = convproj_obj.loop_start
		wavtool_obj.loopEnd = convproj_obj.loop_end
		wavtool_obj.loopEnabled = convproj_obj.loop_active

		zip_wt.writestr('WavTool Project.json', json.dumps(wavtool_obj.write()))
		zip_wt.close()
		open(output_file, 'wb').write(zip_bio.getbuffer())

		with open('wavtool_debug.json', "w") as fileout:
			json.dump(wavtool_obj.write(), fileout, indent=4)