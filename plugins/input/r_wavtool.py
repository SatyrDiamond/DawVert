# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
from functions import data_xml
import plugins
import json
import os
import zipfile
import base64
import logging
import numpy as np

logger_input = logging.getLogger('input')

def extract_audio(audioname):
	audio_filename = None
	for s_file in zip_data.namelist():
		if audioname in s_file:
			audio_filename = samplefolder+s_file
			if os.path.exists(samplefolder+s_file) == False:
				zip_data.extract(s_file, path=samplefolder, pwd=None)
				break
	return audio_filename

def add_devices(convproj_obj, track_obj, trackid, devices_obj):
	from functions_plugin_ext import plugin_vst2
	from functions_plugin_ext import plugin_vst3
	from objects.inst_params import fx_delay
	from functions_plugin import juce_memoryblock
	from functions_plugin_ext import data_vc2xml
	if trackid in devices_obj.tracks:
		device_track = devices_obj.tracks[trackid]

		effects = []
		instrument_dev = None

		trackdevices = []
		TrackMIDIReceiver = None

		inst_fallback = None

		for deviceid, devicedata in device_track.items():
			if devicedata.type == 'PortalOut':
				if 'portalType' in devicedata.data:
					if devicedata.data['portalType'] == 'MIDI':
						TrackMIDIReceiver = deviceid

			if devicedata.type == 'JS':

				inputdata = devicedata.data['inputs'] if 'inputs' in devicedata.data else {}
				constantsdata = devicedata.data['constants'] if 'constants' in devicedata.data else {}
				matrix = devicedata.data['matrix'] if 'matrix' in devicedata.data else {}

				if devicedata.sourceId == 'df142a04-31c6-4495-a8a4-c49f8429d557':
					plugin_obj = convproj_obj.plugin__add(deviceid, 'native', 'wavtool', 'wavetable')
					instrument_dev = deviceid
					wavetableA = base64.b64decode(constantsdata["wavetableA"]) if "wavetableA" in constantsdata else None
					wavetableB = base64.b64decode(constantsdata["wavetableB"]) if "wavetableB" in constantsdata else None

					for name, value in constantsdata.items():
						if name not in ['wavetableA','wavetableB']:
							plugin_obj.datavals.add(name, value)

					for name, value in inputdata.items():
						plugin_obj.params.add(name, value, 'float')

					for envnum in range(4):
						strtxt = str(envnum+1)
						attack = plugin_obj.params.get('attack'+strtxt, 48).value/48000
						decay = plugin_obj.params.get('decay'+strtxt, 14400).value/48000
						sustain = plugin_obj.params.get('sustain'+strtxt, 1 if envnum==0 else 0).value
						release = plugin_obj.params.get('release'+strtxt, 4800).value/48000
						envAmplitude = plugin_obj.params.get('envAmplitude'+strtxt, 1).value
						plugin_obj.env_asdr_add('custom'+strtxt, 0, attack, 0, decay, sustain, release, envAmplitude)

					for lfonum in range(3):
						strtxt = str(lfonum+1)

						txt_waveform = 'waveform'+strtxt
						txt_sync = 'sync'+strtxt

						waveform = inputdata[txt_waveform] if txt_waveform in inputdata else 'Sine'
						sfree = (inputdata[txt_sync] if txt_sync in inputdata else "Free")=="Free"
						freq = plugin_obj.params.get('frequency'+strtxt, 1).value

						lfo_obj = plugin_obj.lfo_add('custom'+strtxt)
						lfo_obj.phase = plugin_obj.params.get('phase'+strtxt, 0).value
						lfo_obj.amount = plugin_obj.params.get('lfoAmplitude'+strtxt, 0.5).value
						if sfree: lfo_obj.time.set_seconds(freq)
						
						if waveform == 'Saw': lfo_obj.prop.shape = 'saw'
						if waveform == 'Sine': lfo_obj.prop.shape = 'sine'
						if waveform == 'Square': lfo_obj.prop.shape = 'square'

					plugin_obj.filter.on = True
					plugin_obj.filter.freq = plugin_obj.params.get('filterCutoff', 20000).value
					plugin_obj.filter.q = plugin_obj.params.get('filterResonance', 0.71).value

					filtertype = plugin_obj.datavals.get('filterType', 'Low Pass')
					if filtertype == 'Low Pass': plugin_obj.filter.type.set('low_pass', None)
					if filtertype == 'High Pass': plugin_obj.filter.type.set('high_pass', None)
					if filtertype == 'Band Pass': plugin_obj.filter.type.set('band_pass', None)
					if filtertype == 'Notch': plugin_obj.filter.type.set('notch', None)

					plugin_obj.datavals.add('matrix', matrix)
					inst_fallback = deviceid

				elif devicedata.sourceId == 'd694ef91-e624-404d-8e34-829d9c1c04b3':
					plugin_obj = convproj_obj.plugin__add(deviceid, 'universal', 'synth-osc', None)
					inst_fallback = deviceid
					instrument_dev = deviceid
					osc_data = plugin_obj.osc_add()
					osc_data.prop.shape = 'saw'

					attack = inputdata["attack"]/48000 if "attack" in inputdata else 0.001
					decay = inputdata["decay"]/48000 if "decay" in inputdata else 0.1
					sustain = inputdata["sustain"] if "sustain" in inputdata else 0.5
					release = inputdata["release"]/48000 if "release" in inputdata else 0.05
					track_obj.params.add('pitch', inputdata["transpose"] if "transpose" in inputdata else 0, 'float')

					plugin_obj.env_asdr_add('vol', 0, attack, 0, decay, sustain, release, 1)

				elif devicedata.sourceId == 'c2fc1730-9cc9-4643-bb54-9435a920c927':
					plugin_obj = convproj_obj.plugin__add(deviceid, 'universal', 'sampler', 'multi')
					inst_fallback = deviceid
					plugin_obj.role = 'synth'
					instrument_dev = deviceid

					plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 10, 1)

					for samplenum in range(1,13):
						endstr = str(samplenum)
						if "sample"+endstr in constantsdata:
							bufferid = constantsdata["sample"+endstr]
							wave_path = extract_audio(bufferid)
							convproj_obj.sampleref__add(bufferid, wave_path, None)
					
							attack = inputdata["attack"+endstr]/48000 if "attack"+endstr in inputdata else 0.1
							decay = inputdata["decay"+endstr]/48000 if "decay"+endstr in inputdata else 0.1
							sustain = inputdata["sustain"+endstr]/48000 if "sustain"+endstr in inputdata else 1
							release = inputdata["release"+endstr]/48000 if "release"+endstr in inputdata else 0.05

							plugin_obj.env_asdr_add('vol_'+endstr, 0, attack, 0, decay, sustain, release, 1)

							samp_key = samplenum-1

							sp_obj = plugin_obj.sampleregion_add(samp_key, samp_key, samp_key, None)
							sp_obj.sampleref = bufferid
							sp_obj.envs['vol'] = 'vol_'+endstr
							sp_obj.pan = inputdata["pan"+endstr] if "pan"+endstr in inputdata else 0
							sp_obj.vol = inputdata["gain"+endstr] if "gain"+endstr in inputdata else 1
							sp_obj.pitch = inputdata["pitch"+endstr] if "pitch"+endstr in inputdata else 0

							sp_obj = plugin_obj.sampleregion_add(samp_key-12, samp_key-12, samp_key-12, None)
							sp_obj.sampleref = bufferid
							sp_obj.envs['vol'] = 'vol_'+endstr
							sp_obj.pan = inputdata["pan"+endstr] if "pan"+endstr in inputdata else 0
							sp_obj.vol = inputdata["gain"+endstr] if "gain"+endstr in inputdata else 1
							sp_obj.pitch = inputdata["pitch"+endstr] if "pitch"+endstr in inputdata else 0

				elif devicedata.sourceId == 'c4888b49-3a72-4b0a-bd4a-a06e9937000a':
					inst_fallback = deviceid
					if 'sample1All' in constantsdata:
						bufferid = constantsdata['sample1All']
						wave_path = extract_audio(bufferid)
						plugin_obj, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler(deviceid, wave_path, None, sampleid=bufferid)
						instrument_dev = deviceid

						attack = inputdata["attack"]/48000 if "attack" in inputdata else 0.001
						decay = inputdata["decay"]/48000 if "decay" in inputdata else 0.1
						sustain = inputdata["sustain"] if "sustain" in inputdata else 1
						release = inputdata["release"]/48000 if "release" in inputdata else 0.05
						plugin_obj.env_asdr_add('vol', 0, attack, 0, decay, sustain, release, 1)

						sp_obj.vol = inputdata["gain"] if "gain" in inputdata else 1
						track_obj.datavals.add('middlenote', constantsdata["sample1Pitch"]-60 if "sample1Pitch" in constantsdata else 0)
						
				elif devicedata.sourceId == '84345e98-f3a7-43b2-b2f2-61bf7c475248':
					plugin_obj = convproj_obj.plugin__add(deviceid, 'universal', 'sampler', 'multi')
					inst_fallback = deviceid

					attack = inputdata["attack"]/48000 if "attack" in inputdata else 0.001
					decay = inputdata["decay"]/48000 if "decay" in inputdata else 0.1
					sustain = inputdata["sustain"] if "sustain" in inputdata else 1
					release = inputdata["release"]/48000 if "release" in inputdata else 0.05
					plugin_obj.env_asdr_add('vol', 0, attack, 0, decay, sustain, release, 1)

					LoudVel = constantsdata["LoudVelocity"] if "LoudVelocity" in constantsdata else 127
					MedLoudVel = constantsdata["MedLoudVelocity"] if "MedLoudVelocity" in constantsdata else 85
					MedSoftVel = constantsdata["MedSoftVelocity"] if "MedSoftVelocity" in constantsdata else 42
					SoftVel = constantsdata["SoftVelocity"] if "SoftVelocity" in constantsdata else 0

					sample1Pitch = constantsdata["sample1Pitch"] if "sample1Pitch" in constantsdata else 24
					sample2Pitch = constantsdata["sample2Pitch"] if "sample2Pitch" in constantsdata else 48
					sample3Pitch = constantsdata["sample3Pitch"] if "sample3Pitch" in constantsdata else 72
					sample4Pitch = constantsdata["sample4Pitch"] if "sample4Pitch" in constantsdata else 96

					btw12Pitch = (sample1Pitch+sample2Pitch)//2
					btw23Pitch = (sample2Pitch+sample3Pitch)//2
					btw34Pitch = (sample3Pitch+sample4Pitch)//2

					range_base = [sample1Pitch,sample2Pitch,sample3Pitch,sample4Pitch]
					range_vel = [[SoftVel,MedSoftVel-1],[MedSoftVel,MedLoudVel-1],[MedLoudVel,LoudVel-1],[LoudVel,127]]
					range_notes = [[0, btw12Pitch-1],[btw12Pitch, btw23Pitch-1],[btw23Pitch, btw34Pitch-1],[btw34Pitch, 127]]

					for velnum, velname in enumerate(['Soft','MedSoft','MedLoud','Loud']):
						for keynum in range(4):
							samplel = 'sample'+str(keynum+1)+velname
							if samplel in constantsdata:
								bufferid = constantsdata[samplel]
								if bufferid:
									kr = range_notes[keynum]
									vr = range_vel[velnum]
									wave_path = extract_audio(bufferid)
									sampleref_obj = convproj_obj.sampleref__add(bufferid, wave_path, None)
									sp_obj = plugin_obj.sampleregion_add(kr[0]-60, kr[1]-60, range_base[keynum]-60, None, samplepartid=deviceid+'_'+samplel)
									sp_obj.vel_min = vr[0]/127
									sp_obj.vel_max = vr[1]/127
									sp_obj.sampleref = bufferid

				elif devicedata.sourceId == 'bc24f717-88d0-4a99-b0ac-b61d4281c7c3':
					plugin_obj = convproj_obj.plugin__add(deviceid, 'universal', 'limiter', None)
					plugin_obj.role = 'effect'
					plugin_obj.params.add('attack', 0.05, 'float')
					plugin_obj.params.add('release', inputdata['release']/48000 if 'release' in inputdata else 0.3, 'float')
					plugin_obj.params.add('pregain', inputdata['gain'] if 'gain' in inputdata else 0, 'float')
					effects.append(deviceid)

				elif devicedata.sourceId == '50413fcd-de89-4db3-a308-095102c24f81':
					plugin_obj = convproj_obj.plugin__add(deviceid, 'universal', 'clipper', None)
					plugin_obj.role = 'effect'
					plugin_obj.params.add('pregain', inputdata['gain'] if 'gain' in inputdata else 0, 'float')
					effects.append(deviceid)

				elif devicedata.sourceId == 'ad949dc9-c921-429d-b08e-c62eaae5e382':
					plugin_obj = convproj_obj.plugin__add(deviceid, 'universal', 'compressor', None)
					plugin_obj.role = 'effect'
					plugin_obj.params.add('attack', inputdata['attack']/48000 if 'attack' in inputdata else 0.001, 'float')
					plugin_obj.params.add('release', inputdata['release']/48000 if 'release' in inputdata else 0.03, 'float')
					plugin_obj.params.add('gain', inputdata['gain'] if 'gain' in inputdata else 0, 'float')
					plugin_obj.params.add('threshold', inputdata['threshold'] if 'threshold' in inputdata else -20, 'float')
					plugin_obj.params.add('ratio', inputdata['ratio'] if 'ratio' in inputdata else 8, 'float')
					effects.append(deviceid)

				elif devicedata.sourceId == 'e0665a05-221d-42c6-9ff6-2ece5c20f80c':
					plugin_obj = convproj_obj.plugin__add(deviceid, 'universal', 'gate', None)
					plugin_obj.role = 'effect'
					plugin_obj.params.add('attack', inputdata['attack']/48000 if 'attack' in inputdata else 0.0001, 'float')
					plugin_obj.params.add('release', inputdata['release']/48000 if 'release' in inputdata else 0.015, 'float')
					plugin_obj.params.add('hold', inputdata['hold']/48000 if 'hold' in inputdata else 0.01, 'float')
					plugin_obj.params.add('threshold', inputdata['threshold'] if 'threshold' in inputdata else -20, 'float')
					plugin_obj.params.add('floor', inputdata['floor'] if 'floor' in inputdata else -40, 'float')
					effects.append(deviceid)

				elif devicedata.sourceId == 'c70556bf-0ba7-4283-a3cc-f2722ee390ec':
					plugin_obj = convproj_obj.plugin__add(deviceid, 'universal', 'reverb', None)
					plugin_obj.role = 'effect'
					plugin_obj.fxdata_add(1, inputdata['mix'] if 'mix' in inputdata else 1)
					plugin_obj.params.add('wet', 1, 'float')
					plugin_obj.params.add('decay', inputdata['time'] if 'time' in inputdata else 5, 'float')
					effects.append(deviceid)

				elif devicedata.sourceId == '3e2e3ece-476a-42f9-b740-7da8f5e37cc8':
					plugin_obj = convproj_obj.plugin__add(deviceid, 'universal', 'convolver', None)
					plugin_obj.role = 'effect'
					plugin_obj.fxdata_add(1, inputdata['mix'] if 'mix' in inputdata else 1)
					bufferid = constantsdata['impulseResponse'] if 'impulseResponse' in constantsdata else None
					if bufferid:
						wave_path = extract_audio(bufferid)
						convproj_obj.sampleref__add(bufferid, wave_path, None)
						samplepart_obj = plugin_obj.samplepart_add('sample')
						samplepart_obj.sampleref = wave_path
					effects.append(deviceid)

				elif devicedata.sourceId == '933cb96b-27e4-498f-8331-f155dce0050b':
					delay_obj = fx_delay.fx_delay()
					delay_obj.feedback[0] = inputdata['feedback'] if 'feedback' in inputdata else 0.5
					timing_obj = delay_obj.timing_add(0)
					timing_obj.set_steps((inputdata['beats'] if 'beats' in inputdata else 0.75)*4, convproj_obj)
					plugin_obj, deviceid = delay_obj.to_cvpj(convproj_obj, deviceid)
					plugin_obj.fxdata_add(1, inputdata['mix'] if 'mix' in inputdata else 1)
					effects.append(deviceid)

				elif devicedata.sourceId == '3aebda9f-fcb6-4700-bb2b-817b862656f1':
					seconds = inputdata['seconds'] if 'seconds' in inputdata else 0.75
					milliseconds = inputdata['milliseconds'] if 'milliseconds' in inputdata else 150
					delay_obj = fx_delay.fx_delay()
					delay_obj.feedback[0] = inputdata['feedback'] if 'feedback' in inputdata else 0.5
					timing_obj = delay_obj.timing_add(0)
					timing_obj.set_seconds(seconds+(milliseconds/1000))
					plugin_obj = delay_obj.to_cvpj(convproj_obj, deviceid)
					plugin_obj.fxdata_add(1, inputdata['mix'] if 'mix' in inputdata else 1)
					effects.append(deviceid)

				elif devicedata.sourceId == '833b0ed8-575a-4dec-baa0-8d8ef7910aca':
					plugin_obj = convproj_obj.plugin__add(deviceid, 'native', 'wavtool', 'Overdrive125')
					plugin_obj.role = 'effect'
					plugin_obj.params.add('pre', inputdata['pre'] if 'pre' in inputdata else 0, 'float')
					plugin_obj.params.add('post', inputdata['post'] if 'post' in inputdata else 0, 'float')
					effects.append(deviceid)

				elif devicedata.sourceId == 'b64cf1c9-db3b-4031-9325-2a933f9893c2':
					plugin_obj = convproj_obj.plugin__add(deviceid, 'universal', 'bitcrush', None)
					plugin_obj.role = 'effect'
					plugin_obj.params.add('bits', inputdata['bitDepth'] if 'bitDepth' in inputdata else 6, 'float')
					plugin_obj.params.add('freq', inputdata['targetSampleRate'] if 'targetSampleRate' in inputdata else 8000, 'float')
					effects.append(deviceid)

				elif devicedata.sourceId == '95c16c68-cd38-4459-8616-d0c1364650ac':
					plugin_obj = convproj_obj.plugin__add(deviceid, 'universal', 'flanger', None)
					plugin_obj.role = 'effect'

					lfoAmount = inputdata['lfoAmount'] if 'lfoAmount' in inputdata else 7.5
					lfoFreq = inputdata['lfoFreq'] if 'lfoFreq' in inputdata else 1
					feedback = inputdata['feedback'] if 'feedback' in inputdata else 0.5
					milliseconds = inputdata['milliseconds'] if 'milliseconds' in inputdata else 0.012

					lfo_obj = plugin_obj.lfo_add('flanger')
					lfo_obj.time.set_hz(lfoFreq)
					lfo_obj.amount = lfoAmount

					plugin_obj.params.add('delay', milliseconds, 'float')
					plugin_obj.fxdata_add(1, inputdata['mix'] if 'mix' in inputdata else 1)
					effects.append(deviceid)

			if devicedata.type == 'Bridge':
				encodedState = base64.b64decode(devicedata.data['encodedState']) if 'encodedState' in devicedata.data else ''
				sourceId = devicedata.data['sourceId'] if 'sourceId' in devicedata.data else ''
				sourceName = devicedata.data['sourceName'] if 'sourceName' in devicedata.data else ''
				sourceManufacturer = devicedata.data['sourceManufacturer'] if 'sourceManufacturer' in devicedata.data else ''
				inputSpec = devicedata.data['inputSpec'] if 'inputSpec' in devicedata.data else {}
				outputSpec = devicedata.data['outputSpec'] if 'outputSpec' in devicedata.data else {}

				isinst = 'midiInput' in inputSpec

				if len(encodedState)>96:
					encodedSig = encodedState[0:96]
					encodedData = encodedState[96:]
					if encodedData[0:4] == b'CcnK':
						plugin_obj = convproj_obj.plugin__add(deviceid, 'external', 'vst2', 'win')
						plugin_vst2.import_presetdata_raw(convproj_obj, plugin_obj, encodedData, None)
					if encodedData[0:4] == b'VC2!':
						pluginstate_x = data_vc2xml.get(encodedData)
						IComponent = data_xml.find_first(pluginstate_x, 'IComponent')
						if IComponent != None and sourceName:
							chunkdata = juce_memoryblock.fromJuceBase64Encoding(IComponent.text)
							plugin_vst3.replace_data(convproj_obj, plugin_obj, 'name', None, sourceName, chunkdata)

				if isinst: 
					instrument_dev = deviceid
					if plugin_obj: plugin_obj.role = 'synth'
				else:
					effects.append(deviceid)
					if plugin_obj: plugin_obj.role = 'effect'

			trackdevices.append(deviceid)

		if TrackMIDIReceiver:
			connections = {}
			for cable_obj in devices_obj.cables:
				if cable_obj.input_device in trackdevices and cable_obj.output_device in trackdevices:
					#print(cable_obj.input_device, cable_obj.input_id, cable_obj.output_device, cable_obj.output_id)
					connections[cable_obj.input_device] = cable_obj.output_device

			used_con = []
			d_in = TrackMIDIReceiver

			while True:
				if d_in in connections and d_in not in used_con:
					used_con.append(d_in)
					d_in = connections[d_in]
					if d_in == instrument_dev: 
						track_obj.inst_pluginid = instrument_dev
						logger_input.info('Instrument Device: '+instrument_dev)
					if d_in in effects: 
						track_obj.fxslots_audio.append(d_in)
						logger_input.info('FX Device: '+d_in)
				else:
					break

		if not track_obj.inst_pluginid: 
			track_obj.inst_pluginid = inst_fallback

class input_wavtool(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'wavtool'
	def get_name(self): return 'Wavtool'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['zip']
		in_dict['fxtype'] = 'track'
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv']
		in_dict['audio_stretch'] = ['warp']
		in_dict['audio_filetypes'] = ['wav','flac','ogg','mp3']
		in_dict['plugin_included'] = ['native:wavtool','universal:sampler:single','universal:sampler:multi']
		in_dict['plugin_ext'] = ['vst2', 'vst3']
	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_wavtool

		global zip_data
		global samplefolder

		convproj_obj.type = 'r'
		convproj_obj.set_timings(1, True)

		try:
			zip_data = zipfile.ZipFile(input_file, 'r')
		except zipfile.BadZipFile as t:
			raise ProjectFileParserException('wavtool: Bad ZIP File: '+str(t))

		json_filename = None
		samplefolder = dv_config.path_samples_extracted
		for jsonname in zip_data.namelist():
			if '.json' in jsonname: json_filename = jsonname
		if not json_filename:
			raise ProjectFileParserException('wavtool: JSON file not found')

		t_wavtool_project = zip_data.read(json_filename)
		wt_proj = json.loads(t_wavtool_project)
		wavtool_obj = proj_wavtool.wavtool_project(wt_proj)

		for trackid, wavtool_track in wavtool_obj.tracks.items(): 

			logger_input.info(''+wavtool_track.type+' Track: '+wavtool_track.name)
			if wavtool_track.type == 'MIDI':
				track_obj = convproj_obj.track__add(trackid, 'instrument', 1, False)
				track_obj.visual.name = wavtool_track.name
				track_obj.visual.color.set_hex(wavtool_track.color)
				track_obj.params.add('vol', wavtool_track.gain, 'float')
				track_obj.params.add('pan', wavtool_track.balance, 'float')
				track_obj.params.add('enabled', int(not wavtool_track.mute), 'bool')
				for wavtool_clip in wavtool_track.clips:
					placement_obj = track_obj.placements.add_notes()
					placement_obj.visual.color.set_hex(wavtool_clip.color)
					placement_obj.visual.name = wavtool_clip.name
					placement_obj.time.set_startend(wavtool_clip.timelineStart, wavtool_clip.timelineEnd)
					placement_obj.time.set_loop_data(wavtool_clip.readStart, wavtool_clip.loopStart, wavtool_clip.loopEnd)
					for note in wavtool_clip.notes:
						placement_obj.notelist.add_r(note['start'], note['end']-note['start'], note['pitch']-60, note['velocity'], {})
				add_devices(convproj_obj, track_obj, trackid, wavtool_obj.devices)

			if wavtool_track.type == 'Audio':
				track_obj = convproj_obj.track__add(trackid, 'audio', 1, False)
				track_obj.visual.name = wavtool_track.name
				track_obj.visual.color.set_hex(wavtool_track.color)
				track_obj.params.add('vol', wavtool_track.gain, 'float')
				track_obj.params.add('pan', wavtool_track.balance, 'float')
				track_obj.params.add('enabled', int(not wavtool_track.mute), 'bool')
				for wavtool_clip in wavtool_track.clips:
					placement_obj = track_obj.placements.add_audio()
					placement_obj.visual.color.set_hex(wavtool_clip.color)
					placement_obj.visual.name = wavtool_clip.name
					placement_obj.time.set_startend(wavtool_clip.timelineStart, wavtool_clip.timelineEnd)

					sp_obj = placement_obj.sample

					audio_filename = extract_audio(wavtool_clip.audioBufferId)
					convproj_obj.sampleref__add(wavtool_clip.audioBufferId, audio_filename, None)
					sp_obj.sampleref = wavtool_clip.audioBufferId

					loopon = True
					if not wavtool_clip.loopEnabled: loopon = wavtool_clip.loopEnabled

					placement_obj.fade_in.set_dur(wavtool_clip.fadeIn, 'beats')
					placement_obj.fade_out.set_dur(wavtool_clip.fadeOut, 'beats')

					wt_clip_transpose = wavtool_clip.transpose
					wt_warp_enabled = wavtool_clip.warp['enabled'] if 'enabled' in wavtool_clip.warp else False
					wt_warp_anchors = wavtool_clip.warp['anchors'] if 'anchors' in wavtool_clip.warp else {}
					wt_warp_sourceBPM = wavtool_clip.warp['sourceBPM'] if 'sourceBPM' in wavtool_clip.warp else 120
					wt_warp_numanchors = len(wt_warp_anchors)

					sourcebpmmod = wt_warp_sourceBPM/120

					stretch_obj = sp_obj.stretch

					if wt_warp_enabled:
						stretch_obj.preserve_pitch = True
						sp_obj.pitch = wt_clip_transpose
						if wt_warp_numanchors<2: 
							stretch_obj.set_rate_tempo(wavtool_obj.bpm, sourcebpmmod, True)
						else:
							stretch_obj.is_warped = True
							for anchor in wt_warp_anchors: 
								warp_point_obj = stretch_obj.add_warp_point()
								warp_point_obj.beat = (float(anchor))/2
								warp_point_obj.second = (wt_warp_anchors[anchor]['destination']/4)/sourcebpmmod
							stretch_obj.calc_warp_points()

					else: 
						stretch_obj.set_rate_speed(wavtool_obj.bpm, pow(2, wavtool_clip.transpose/12), False)
						stretch_obj.preserve_pitch = False

					sp_obj.vol = wavtool_clip.gain

					if loopon:
						placement_obj.time.set_loop_data(wavtool_clip.readStart, wavtool_clip.loopStart, wavtool_clip.loopEnd)
					else:
						placement_obj.time.set_offset(wavtool_clip.readStart)

				add_devices(convproj_obj, track_obj, trackid, wavtool_obj.devices)

		convproj_obj.track_master.visual.name = 'Master'
		convproj_obj.track_master.visual.color.set_float([0.14, 0.14, 0.14])
		convproj_obj.track_master.params.add('vol', 1, 'float')

		convproj_obj.timesig = [wavtool_obj.beatNumerator, wavtool_obj.beatDenominator]
		convproj_obj.params.add('bpm', wavtool_obj.bpm, 'float')

		convproj_obj.metadata.name = wavtool_obj.name