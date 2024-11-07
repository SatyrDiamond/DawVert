# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import io
import os
import zipfile
import math
import lxml.etree as ET
from functions import data_values
from functions import xtramath
from objects import counter
from functions_plugin import synth_nonfree_values

audioidnum = 0

def convauto(autopoints, param_obj):
	ampedauto = []
	for autopoint in autopoints:
		value = xtramath.between_to_one(param_obj.min, param_obj.max, autopoint.value)
		ampedauto.append({"pos": autopoint.pos/4, "value": value})
	return ampedauto

def createclip(audiopl_obj, audio_id):
	from objects.file_proj import proj_amped
	amped_audclip = proj_amped.amped_clip(None)
	amped_audclip.contentGuid.is_custom = True
	amped_audclip.contentGuid.id = audio_id[audiopl_obj.sample.sampleref] if audiopl_obj.sample.sampleref in audio_id else ''
	amped_audclip.position = 0
	amped_audclip.gain = audiopl_obj.sample.vol
	amped_audclip.length = audiopl_obj.time.duration*4
	amped_audclip.offset = 0
	amped_audclip.stretch = audiopl_obj.sample.stretch.calc_real_size
	amped_audclip.pitchShift = audiopl_obj.sample.pitch
	return amped_audclip

def do_idparams(amped_track, convproj_obj, plugin_obj, pluginid, amped_device, amped_auto):
	paramout = []
	paramlist = plugin_obj.params.list()
	for paramnum, paramid in enumerate(paramlist):
		ampedpid = paramid.replace('__', '/')
		param_obj = plugin_obj.params.get(ampedpid, 0)

		ap_f, ap_d = convproj_obj.automation.get(['plugin', pluginid, paramid], 'float')
		#if ap_f: print(ap_d)
		if ap_f: 
			if ap_d.u_nopl_points:
				autospec = {"type": "numeric", "min": param_obj.min, "max": param_obj.max, "curve": 0, "step": 0}
				amped_auto = amped_track.add_auto(paramid, True, amped_device.id, convauto(cvpj_points, param_obj), autospec)

		amped_device.add_param(paramnum, ampedpid, param_obj.value)
	return paramout

def amped_parse_effects(amped_track, convproj_obj, fxchain_audio, amped_auto):
	outdata = []
	for pluginid in fxchain_audio:
		out_auto = []
		plugin_found, plugin_obj = convproj_obj.plugin__get(pluginid)
		if plugin_found: 
			fx_on, fx_wet = plugin_obj.fxdata_get()
			fx_on = not fx_on
			#if plugin_obj.check_match('universal', 'delay-c'):
			#	d_time_type = plugin_obj.datavals.get('time_type', 'seconds')
			#	d_time = plugin_obj.datavals.get('time', 1)
			#	d_wet = plugin_obj.datavals.get('wet', fx_wet)
			#	d_feedback = plugin_obj.datavals.get('feedback', 0.0)
			#	amped_device = amped_track.add_device('Delay', 'Delay', counter_devid.get())

			#	device_params = []
			#	if d_time_type == 'seconds': device_params.append({'id': 0, 'name': 'time', 'value': d_time})
			#	if d_time_type == 'steps': device_params.append({'id': 0, 'name': 'time', 'value': (d_time/8)*((amped_obj.tempo)/120) })
			#	device_params.append({'id': 1, 'name': 'fb', 'value': d_feedback})
			#	device_params.append({'id': 2, 'name': 'mix', 'value': d_wet})
			#	device_params.append({'id': 3, 'name': 'damp', 'value': 0})
			#	device_params.append({'id': 4, 'name': 'cross', 'value': 0})
			#	device_params.append({'id': 5, 'name': 'offset', 'value': 0})
			#	amped_device.bypass = fx_on
			#	amped_device['params'] = device_params
			#	outdata.append(amped_device)

			#if plugin_obj.check_matchmulti('native', 'amped', ["Amp Sim Utility", 'Clean Machine', 'Distortion Machine', 'Metal Machine']):
			#	amped_device = amped_track.add_device('WAM', 'Amp Sim Utility', counter_devid.get())
			#	amped_device.bypass = fx_on
			#	if plugin_obj.type.subtype == "Amp Sim Utility": wamClassName = "WASABI_SC.Utility"
			#	if plugin_obj.type.subtype == "Clean Machine": wamClassName = 'WASABI_SC.CleanMachine'
			#	if plugin_obj.type.subtype == "Distortion Machine": wamClassName = 'WASABI_SC.DistoMachine'
			#	if plugin_obj.type.subtype == "Metal Machine": wamClassName = 'WASABI_SC.MetalMachine'
			#	amped_device.data['wamClassName'] = wamClassName
			#	amped_device.data['wamPreset'] = plugin_obj.datavals.get('data', '{}')
			#	outdata.append(amped_device)

			if plugin_obj.check_matchmulti('native', 'amped', ['BitCrusher', 'Chorus', 
		'CompressorMini', 'Delay', 'Distortion', 'Equalizer', 
		'Flanger', 'Gate', 'Limiter', 'LimiterMini', 'Phaser', 
		'Reverb', 'Tremolo', 'Vibrato', 'Compressor', 'Expander', 'EqualizerPro']):
				classname = plugin_obj.type.subtype
				classlabel = plugin_obj.type.subtype
				if classname == 'CompressorMini': classlabel = 'Equalizer Mini'
				if classname == 'Equalizer': classlabel = 'Equalizer Mini'
				if classname == 'LimiterMini': classlabel = 'Limiter Mini'
				if classname == 'EqualizerPro': classlabel = 'Equalizer'
				amped_device = amped_track.add_device(classname, classlabel, counter_devid.get())
				deviceid = amped_device.id

				amped_device.bypass = fx_on
				do_idparams(amped_track, convproj_obj, plugin_obj, pluginid, amped_device, out_auto)
				outdata.append(amped_device)
		
		if amped_auto != None: amped_auto += out_auto

	return outdata

class output_amped(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'output'
	def get_name(self): return 'Amped Studio'
	def get_shortname(self): return 'amped'
	def gettype(self): return 'r'
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'amped'
		in_dict['audio_filetypes'] = ['wav', 'mp3', 'ogg', 'flac']
		in_dict['placement_cut'] = True
		in_dict['auto_types'] = ['nopl_points']
		in_dict['track_hybrid'] = True
		in_dict['audio_stretch'] = ['rate']
		in_dict['audio_nested'] = True
		in_dict['plugin_included'] = ['native:amped', 'universal:midi', 'user:reasonstudios:europa', 'universal:sampler:multi']
	def parse(self, convproj_obj, output_file):
		from objects.file_proj import proj_amped

		global counter_id
		global counter_devid
		global amped_obj
		global europa_vals

		convproj_obj.change_timings(4, True)

		counter_id = counter.counter(10000, '')
		counter_devid = counter.counter(30000, '')

		europa_vals = synth_nonfree_values.europa_valnames()

		zip_bio = io.BytesIO()
		zip_amped = zipfile.ZipFile(zip_bio, mode='w', compresslevel=None)

		amped_obj = proj_amped.amped_project(None)
		amped_obj.tempo = int(convproj_obj.params.get('bpm', 120).value)
		amped_obj.timesig_num, amped_obj.timesig_den = convproj_obj.timesig
		amped_obj.loop_active = convproj_obj.loop_active
		amped_obj.loop_start = convproj_obj.loop_start
		amped_obj.loop_end = convproj_obj.loop_end

		amped_obj.createdWith = "DawVert"
		amped_obj.settings = {"deviceDelayCompensation": True}
		amped_obj.masterTrack.volume = convproj_obj.track_master.params.get('vol', 1).value
		#amped_obj.masterTrack.devices = amped_parse_effects(None, convproj_obj, convproj_obj.track_master.fxslots_audio, None)

		audio_id = {}
		amped_filenames = {}
		audioidnum = 0

		for sampleref_id, sampleref_obj in convproj_obj.sampleref__iter():
			audio_id[sampleref_id] = audioidnum
			filepath = sampleref_obj.fileref.get_path(None, False)
			if os.path.exists(filepath): zip_amped.write(filepath, str(audioidnum))
			amped_filenames[audioidnum] = sampleref_obj.fileref.file.basename
			audioidnum += 1

		for trackid, track_obj in convproj_obj.track__iter():
			amped_track = proj_amped.amped_track(None)
			amped_track.id = counter_id.get()
			amped_track.name = track_obj.visual.name if track_obj.visual.name else ''
			amped_track.pan = track_obj.params.get('pan', 0).value
			amped_track.volume = track_obj.params.get('vol', 1.0).value
			amped_track.mute = not track_obj.params.get('on', True).value
			amped_track.solo = bool(track_obj.params.get('solo', False).value)

			amped_track.armed = {
				'mic': track_obj.armed.in_audio,
				'keys': track_obj.armed.in_keys
			}

			inst_supported = False
			plugin_found, plugin_obj = convproj_obj.plugin__get(track_obj.inst_pluginid)
			if plugin_found:

				if plugin_obj.check_match('external', 'discodsp', 'obxd'):
					inst_supported = True
					amped_device = amped_track.add_device('WAM', 'OBXD', counter_devid.get())
					wamPreset = {}
					wamPreset['bank'] = ''
					wamPreset['bankName'] = ''
					wamPreset['patchIndex'] = 0
					wamPreset['data'] = [plugin_obj.params.get('obxd_'+str(x), 0).value for x in range(71)]
					amped_device.data['wamClassName'] = 'OBXD'
					amped_device.data['wamPreset'] = json.dumps(wamPreset)
					amped_device.bypass = False

				if plugin_obj.check_match('external', 'smartelectronix', 'augur'):
					inst_supported = True
					amped_device = amped_track.add_device('WAM', 'Augur', counter_devid.get())
					wamPreset = {}
					wamPreset['bank'] = ''
					wamPreset['bankName'] = ''
					wamPreset['patchIndex'] = 0
					wamPreset['data'] = [plugin_obj.params.get('augur_'+str(x), 0).value for x in range(183)]
					amped_device.data['wamClassName'] = 'AUGUR'
					amped_device.data['wamPreset'] = json.dumps(wamPreset)
					amped_device.bypass = False

				#if plugin_obj.check_matchmulti('native', 'amped', ['Augur', 'Dexed']):
				#	inst_supported = True
				#	amped_device = amped_track.add_device('WAM', plugin_obj.type.subtype, counter_devid.get())
#
				#	if plugin_obj.type.subtype == "Dexed": wamClassName = 'DEXED'
				#	amped_device.data['wamClassName'] = wamClassName
				#	amped_device.data['wamPreset'] = plugin_obj.datavals.get('data', '{}')
				#	amped_track.devices.append(amped_device)
				#	amped_device.bypass = False

				if plugin_obj.check_matchmulti('native', 'amped', ['Volt', 'VoltMini', 'Granny']):
					inst_supported = True
					if plugin_obj.type.subtype == "Volt": amped_device = amped_track.add_device('Volt', 'VOLT', counter_devid.get())
					if plugin_obj.type.subtype == "VoltMini": amped_device = amped_track.add_device('VoltMini', 'VOLT Mini', counter_devid.get())
					if plugin_obj.type.subtype == "Granny": amped_device = amped_track.add_device('Granny', 'Granny', counter_devid.get())
					do_idparams(amped_track, convproj_obj, plugin_obj, track_obj.inst_pluginid, amped_device, amped_track.automations)
					amped_track.devices.append(amped_device)
					amped_device.bypass = False

				if plugin_obj.check_match('user', 'reasonstudios', 'europa'):
					inst_supported = True
					amped_device = amped_track.add_device('WAM','Europa',counter_devid.get())
					amped_device.data['wamClassName'] = 'Europa'
					wamPreset = {}
					wamPreset['patch'] = 'DawVert'
					europa_patch = ET.Element("JukeboxPatch")
					europa_name = ET.SubElement(europa_patch, "DeviceNameInEnglish")
					europa_name.text = "Europa Shapeshifting Synthesizer"
					europa_prop = ET.SubElement(europa_patch, "Properties")
					europa_prop.set('deviceProductID','se.propellerheads.Europa')
					europa_prop.set('deviceVersion','2.0.0f')
					europa_obj = ET.SubElement(europa_prop, "Object")
					europa_obj.set('name','custom_properties')
					for eur_value_name in europa_vals:
						eur_value_type, cvpj_val_name = europa_vals[eur_value_name]
						if eur_value_type == 'number':
							eur_value_value = plugin_obj.params.get(cvpj_val_name, 0).value
						else:
							eur_value_value = plugin_obj.datavals.get(cvpj_val_name, '')
							if eur_value_name in ['Curve1','Curve2','Curve3','Curve4','Curve']: 
								eur_value_value = bytes(eur_value_value).hex().upper()

						europa_value_obj = ET.SubElement(europa_obj, "Value")
						europa_value_obj.set('property',eur_value_name)
						europa_value_obj.set('type',eur_value_type)
						europa_value_obj.text = str(eur_value_value)
					wamPreset['settings'] = ET.tostring(europa_patch).decode()
					wamPreset['encodedSampleData'] = plugin_obj.datavals.get('encodedSampleData', [])
					amped_device.data['wamPreset'] = json.dumps(wamPreset)
					amped_track.devices.append(amped_device)
					amped_device.bypass = False

				#if plugin_obj.check_match('vst2', 'win'):
				#	inst_supported = True
				#	vstcondata = amped_track.add_device('VSTConnection',"VST/Remote Beta", counter_devid.get())
				#	vstdatatype = plugin_obj.datavals.get('datatype', '')
				#	if vstdatatype == 'chunk':
				#		vstcondata['pluginPath'] = plugin_obj.getpath_fileref(convproj_obj, 'file', None, True)
				#		vstcondata['pluginState'] = plugin_obj.rawdata_get_b64('chunk')
				#	amped_track.devices.append(vstcondata)

			if not inst_supported:
				midi_found, midi_inst = track_obj.get_midi(convproj_obj)
				o_midi_bank, o_midi_patch = midi_inst.to_sf2()
				amped_device = amped_track.add_device('SF2','GM Player',counter_devid.get())
				amped_device.add_param(0, 'patch', 0)
				amped_device.add_param(1, 'bank', o_midi_bank)
				amped_device.add_param(2, 'preset', o_midi_patch)
				amped_device.add_param(3, 'gain', 0.75)
				amped_device.add_param(4, 'omni', 1)
				amped_device.data['sf2Preset'] = {"bank": o_midi_bank, "preset": o_midi_patch, "name": ""}
				amped_track.devices.append(amped_device)
				amped_device.bypass = False

			for notespl_obj in track_obj.placements.pl_notes:
				amped_offset = 0
				if notespl_obj.time.cut_type == 'cut': amped_offset = notespl_obj.time.cut_start

				amped_region = amped_track.add_region(notespl_obj.time.position, notespl_obj.time.duration, amped_offset, counter_id.get())
				amped_region.name = notespl_obj.visual.name if notespl_obj.visual.name else ''

				notespl_obj.notelist.sort()
				for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
					for t_key in t_keys:
						if 0 <= t_key+60 <= 128:
							amped_region.midi_notes.append({
								"position": float(t_pos)/4, 
								"length": float(t_dur)/4, 
								"key": int(t_key+60),
								"velocity": t_vol*100, 
								"channel": 0
								})

			for audiopl_obj in track_obj.placements.pl_audio:
				amped_offset = 0
				if audiopl_obj.time.cut_type == 'cut': amped_offset = audiopl_obj.time.cut_start
				amped_region = amped_track.add_region(audiopl_obj.time.position, audiopl_obj.time.duration, amped_offset, counter_id.get())
				amped_audclip = createclip(audiopl_obj, audio_id)
				amped_audclip.fadeIn = audiopl_obj.fade_in.get_dur_beat(amped_obj.tempo)
				amped_region.clips = [amped_audclip]

			for nestedaudiopl_obj in track_obj.placements.pl_audio_nested:
				if len(nestedaudiopl_obj.events):
					amped_region = amped_track.add_region(nestedaudiopl_obj.time.position, nestedaudiopl_obj.time.duration, 0, counter_id.get())
					for insideaudiopl_obj in nestedaudiopl_obj.events: 
						amped_audclip = createclip(insideaudiopl_obj, audio_id)
						amped_audclip.position = insideaudiopl_obj.time.position/4
						amped_audclip.length = insideaudiopl_obj.time.duration/4
						amped_audclip.fadeIn = insideaudiopl_obj.fade_in.get_dur_beat(amped_obj.tempo)
						if insideaudiopl_obj.time.cut_type == 'cut': 
							amped_audclip.offset = (insideaudiopl_obj.time.cut_start/4)
						amped_region.clips.append(amped_audclip)

			amped_track.devices += amped_parse_effects(amped_track, convproj_obj, track_obj.fxslots_audio, amped_track.automations)
			amped_obj.tracks.append(amped_track)

		amped_obj.metronome = {"active": False, "level": 1}
		amped_obj.playheadPosition = 0

		zip_amped.writestr('amped-studio-project.json', json.dumps(amped_obj.write()))
		zip_amped.writestr('filenames.json', json.dumps(amped_filenames))
		zip_amped.close()
		open(output_file, 'wb').write(zip_bio.getbuffer())