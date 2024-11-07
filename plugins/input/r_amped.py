# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import xtramath
from objects import globalstore
import xml.etree.ElementTree as ET
import plugins
import json
import os
import zipfile
from objects.exceptions import ProjectFileParserException

AMPED_COLORS = {
				'mint': [0.20, 0.80, 0.63],
				'lime': [0.54, 0.92, 0.16],
				'yellow': [0.97, 0.91, 0.11],
				'amber': [1.00, 0.76, 0.33],
				'orange': [0.98, 0.61, 0.38],
				'red': [0.96, 0.38, 0.43],
				'magenta': [0.87, 0.44, 0.96],
				'purple': [0.64, 0.48, 0.96],
				'blue': [0.13, 0.51, 0.96],
				'cyan': [0.20, 0.80, 0.63]
				}

def get_dev_auto(amped_autodata, devid, paramsdata): 
	out = []
	if devid in amped_autodata:
		devauto = amped_autodata[devid]
		for param in paramsdata:
			if 'name' in param:
				if param.name in devauto:
					out.append([param.name, devauto[param.name]])
	return out

def eq_calc_q(band_type, q_val):
	if band_type in ['low_pass', 'high_pass']: q_val = xtramath.logpowmul(q_val, 2) if q_val != 0 else 1
	if band_type in ['peak']: q_val = xtramath.logpowmul(q_val, -1) if q_val != 0 else 1
	return q_val

def do_idparams(paramsdata, plugin_obj, pluginname):
	fldso = globalstore.dataset.get_obj('amped', 'plugin', pluginname)
	if fldso:
		for param in paramsdata:
			dset_param = fldso.params.get(param.name)
			if dset_param: plugin_obj.dset_param__add(param.name, param.value, dset_param)

def do_idauto(convproj_obj, amped_autodata, devid, amped_auto, pluginid):
	if amped_autodata:
		if devid in amped_autodata:
			autoparams = amped_autodata[devid]
			for autop, apoints in autoparams.items():
				autoloc = ['plugin',str(pluginid),autop.replace('/', '__')]
				for point in apoints:
					convproj_obj.automation.add_autopoint(autoloc, 'float', point[0], point[1], 'normal')

def get_contentGuid(contentGuid):
	if isinstance(contentGuid, dict): return str(contentGuid['userAudio']['exportedId'])
	else: return contentGuid

def volt_lfo(plugin_obj, starttxt, asdrtype, amtgain):
	lfo_wave = int(plugin_obj.params.get(starttxt+"wave", 0).value)
	lfo_rate = plugin_obj.params.get(starttxt+"rate", 0).value
	lfo_amp = plugin_obj.params.get(starttxt+"amp", 0).value
	lfo_delay = plugin_obj.params.get(starttxt+"delay", 0).value

	lfo_obj = plugin_obj.lfo_add(asdrtype)
	lfo_obj.predelay = lfo_delay
	lfo_obj.prop.shape = ['sine','triangle','square','saw','random'][lfo_wave]
	lfo_obj.time.set_hz(lfo_rate)
	lfo_obj.amount = lfo_amp*amtgain

def volt_adsr(plugin_obj, starttxt, env_name, amount):
	eg_A = plugin_obj.params.get(starttxt+"A", 0).value*10
	eg_D = plugin_obj.params.get(starttxt+"D", 0).value*10
	eg_S = plugin_obj.params.get(starttxt+"S", 0).value
	eg_R = plugin_obj.params.get(starttxt+"R", 0).value*10

	eg_curveA = plugin_obj.params.get(starttxt+"curveA", 0).value
	eg_curveD = plugin_obj.params.get(starttxt+"curveD", 0).value
	eg_curveR = plugin_obj.params.get(starttxt+"curveR", 0).value

	asdr_obj = plugin_obj.env_asdr_add(env_name, 0, eg_A, 0, eg_D, eg_S, eg_R, amount)
	asdr_obj.attack_tension = eg_curveA
	asdr_obj.decay_tension = eg_curveD
	asdr_obj.release_tension = eg_curveR

def get_wampreset(amped_tr_device):
	return json.loads(amped_tr_device.data['wamPreset']) if 'wamPreset' in amped_tr_device.data else {}

def encode_devices(convproj_obj, amped_tr_devices, track_obj, amped_autodata):
	for amped_tr_device in amped_tr_devices:
		devid = amped_tr_device.id
		pluginid = str(devid)
		devicetype = [amped_tr_device.className, amped_tr_device.label]

		if amped_tr_device.className == 'WAM':

			if amped_tr_device.label == 'OBXD': 
				plugin_obj = convproj_obj.plugin__add(pluginid, 'synth', 'discodsp', 'obxd')
				wampreset = get_wampreset(amped_tr_device)
				if 'data' in wampreset:
					for n, v in enumerate(wampreset['data']): plugin_obj.params.add('obxd_'+str(n), v, 'float')

			elif amped_tr_device.label == 'Augur': 
				plugin_obj = convproj_obj.plugin__add(pluginid, 'synth', 'smartelectronix', 'augur')
				wampreset = get_wampreset(amped_tr_device)
				if 'data' in wampreset:
					for n, v in enumerate(wampreset['data']):
						paramname = 'augur_'+str(n)
						if isinstance(v, int): plugin_obj.params.add(paramname, v, 'int')
						if isinstance(v, float): plugin_obj.params.add(paramname, v, 'float')
						if isinstance(v, bool): plugin_obj.params.add(paramname, v, 'bool')

			elif amped_tr_device.label == 'Dexed': 
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'amped', amped_tr_device.label)
				plugin_obj.datavals.add('data', amped_tr_device.data['wamPreset'])
				wampreset = get_wampreset(amped_tr_device)

			elif amped_tr_device.label == 'Europa': 
				plugin_obj = convproj_obj.plugin__add(pluginid, 'user', 'reasonstudios', 'europa')

				wampreset = get_wampreset(amped_tr_device)
				europa_xml = ET.fromstring(wampreset['settings'])
				europa_xml_prop = europa_xml.findall('Properties')[0]

				europa_params = {}

				for xmlsub in europa_xml_prop:
					if xmlsub.tag == 'Object':
						object_name = xmlsub.get('name')
						for objsub in xmlsub:
							if objsub.tag == 'Value':
								value_name = objsub.get('property')
								value_type = objsub.get('type')
								value_value = float(objsub.text) if value_type == 'number' else objsub.text
								europa_params[value_name] = [value_type, value_value]

				dataset_synth_nonfree = globalstore.dataset.get_obj('synth_nonfree', 'plugin', 'europa')
				if dataset_synth_nonfree:
					for param_id, dset_param in dataset_synth_nonfree.params.iter():
						if dset_param.name in europa_params:
							param_type, param_value = europa_params[dset_param.name]
							if param_type == 'number': plugin_obj.dset_param__add(param_id, param_value, dset_param)
							else:
								if dset_param.name in ['Curve1','Curve2','Curve3','Curve4','Curve']: param_value = list(bytes.fromhex(param_value))
								plugin_obj.datavals.add(param_id, param_value)

				if 'encodedSampleData' in wampreset: plugin_obj.datavals.add('encodedSampleData', wampreset['encodedSampleData'])

			elif amped_tr_device.label == 'Amp Sim Utility': 
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'amped', amped_tr_device.label)
				plugin_obj.datavals.add('data', amped_tr_device.data['wamPreset'])
				plugin_obj.role = 'fx'
				track_obj.fxslots_audio.append(pluginid)

			if amped_tr_device.label in ['OBXD', 'Augur', 'Dexed', 'Europa']:
				track_obj.inst_pluginid = pluginid
				plugin_obj.role = 'synth'

		elif devicetype == ['Drumpler', 'Drumpler']:
			plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'sampler', 'multi')
			plugin_obj.role = 'synth'
			track_obj.inst_pluginid = pluginid
			track_obj.is_drum = True

			drumplerdata = {}
			for param in amped_tr_device.params: data_values.dict__nested_add_value(drumplerdata, param.name.split('/'), param.value)

			paddata = []
			if 'kit' in amped_tr_device.data:
				drumkit = amped_tr_device.data['kit']
				if 'pads' in drumkit: 
					paddata = drumkit['pads']

			if 'pad' in drumplerdata:
				for num, data in drumplerdata['pad'].items():
					keynum = int(num)-1
					sp_obj = plugin_obj.sampleregion_add(keynum, keynum, keynum, None)
					sp_obj.start = data['start']
					sp_obj.end = data['end']
					sp_obj.pitch = data['pitch']
					sp_obj.vol = data['level']
					sp_obj.pan = data['pan']
					sp_obj.point_value_type = 'percent'
					sp_obj.trigger = 'oneshot'
					if paddata: 
						padpart = paddata[keynum-1]
						if 'url' in padpart: sp_obj.sampleref = padpart['url']
						if 'name' in padpart: sp_obj.visual.name = padpart['name']

		elif devicetype == ['SF2', 'GM Player']:
			track_obj.inst_pluginid = pluginid

			value_patch = 0
			value_bank = 0
			value_gain = 0.75
			for param in amped_tr_device.params:
				if param.name == 'patch': value_patch = param.value
				if param.name == 'bank': value_bank = param.value
				if param.name == 'gain': value_gain = param.value

			plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'midi', None)
			plugin_obj.role = 'synth'
			plugin_obj.midi.from_sf2(value_bank, value_patch)
			param_obj = plugin_obj.params.add_named('gain', value_gain, 'float', 'Gain')

		elif devicetype == ['Granny', 'Granny']:
			track_obj.inst_pluginid = pluginid
			plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'amped', 'Granny')
			plugin_obj.role = 'synth'

			#sampleuuid = amped_tr_device.grannySampleGuid
			#sampleref_obj = convproj_obj.sampleref__add(sampleuuid, '')
			#sampleref_obj.visual.name = amped_tr_device.grannySampleName
			#plugin_obj.samplerefs['sample'] = sampleuuid
			do_idparams(amped_tr_device.params, plugin_obj, amped_tr_device.className)
			do_idauto(convproj_obj, amped_autodata, devid, amped_tr_device.params, pluginid)

		elif devicetype == ['Volt', 'VOLT']:
			track_obj.inst_pluginid = pluginid
			plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'amped', 'Volt')
			plugin_obj.role = 'synth'
			do_idparams(amped_tr_device.params, plugin_obj, amped_tr_device.className)
			do_idauto(convproj_obj, amped_autodata, devid, amped_tr_device.params, pluginid)

		elif devicetype == ['VoltMini', 'VOLT Mini']:
			track_obj.inst_pluginid = pluginid
			plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'amped', 'VoltMini')
			plugin_obj.role = 'synth'
			do_idparams(amped_tr_device.params, plugin_obj, amped_tr_device.className)
			do_idauto(convproj_obj, amped_autodata, devid, amped_tr_device.params, pluginid)

			filt_lvl = plugin_obj.params.get("part/1/eg/3/L", 0).value
			modlvl = plugin_obj.params.get("part/1/eg/1/L", 0).value

			filt_bypass = plugin_obj.params.get("part/1/filter/bypass", 0).value
			filt_fc = plugin_obj.params.get("part/1/filter/fc", 0).value
			filt_Q = plugin_obj.params.get("part/1/filter/Q", 0).value

			filt_fc = ((filt_fc*2)**3.14)*800

			plugin_obj.filter.type.set('low_pass', None)
			plugin_obj.filter.on = not bool(filt_bypass)
			plugin_obj.filter.freq = filt_fc
			plugin_obj.filter.q = 1+(filt_Q*2.5)

			volt_adsr(plugin_obj, 'part/1/eg/4/', 'vol', 1)
			volt_adsr(plugin_obj, 'part/1/eg/3/', 'cutoff', filt_lvl*6000)
			volt_adsr(plugin_obj, 'part/1/eg/1/', 'modenv', modlvl)
			volt_lfo(plugin_obj, 'part/1/lfo/3/', 'cutoff', 8000)
			volt_lfo(plugin_obj, 'part/1/lfo/1/', 'modenv', 1)

		elif devicetype == ['Sampler', 'Sampler']:
			track_obj.inst_pluginid = pluginid
			samplerdata = {}
			for param in amped_tr_device.params: data_values.dict__nested_add_value(samplerdata, param.name.split('/'), param.value)

			plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'sampler', 'multi')
			plugin_obj.role = 'synth'
			plugin_obj.datavals.add('point_value_type', "percent")

			samplerdata_voiceLimit = samplerdata['voiceLimit']
			samplerdata_filter = samplerdata['filter']
			samplerdata_eg = samplerdata['eg']
			samplerdata_zone = samplerdata['zone']
			#samplerdata_zonefile = amped_tr_device.zonefile
			
			for samplerdata_zp in samplerdata_zone:
				amped_samp_part = samplerdata_zone[samplerdata_zp]
				sp_obj = plugin_obj.sampleregion_add(int(amped_samp_part['key']['min'])-60, int(amped_samp_part['key']['max'])-60, amped_samp_part['key']['root']-60, None)
				sp_obj.loop_active = 0
				sp_obj.loop_start = amped_samp_part['looping']['startPositionNorm']
				sp_obj.loop_end = amped_samp_part['looping']['endPositionNorm']
				#sp_obj.sampleref = get_contentGuid(samplerdata_zonefile[samplerdata_zp])

		elif devicetype == ['EqualizerPro', 'Equalizer']:
			track_obj.fxslots_audio.append(pluginid)
			plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'amped', 'EqualizerPro')
			plugin_obj.role = 'fx'
			do_idparams(amped_tr_device.params, plugin_obj, amped_tr_device.className)
			do_idauto(convproj_obj, amped_autodata, devid, amped_tr_device.params, pluginid)

		elif amped_tr_device.className in ['Chorus',  
		'CompressorMini', 'Delay', 'Distortion', 'Equalizer', 
		'Flanger', 'Gate', 'Limiter', 'LimiterMini', 'Phaser', 
		'Reverb', 'Tremolo', 'BitCrusher', 'Tremolo', 'Vibrato', 'Compressor', 'Expander']:
			track_obj.fxslots_audio.append(pluginid)
			plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'amped', amped_tr_device.className)
			plugin_obj.role = 'fx'
			do_idparams(amped_tr_device.params, plugin_obj, amped_tr_device.className)
			do_idauto(convproj_obj, amped_autodata, devid, amped_tr_device.params, pluginid)

		plugin_obj.fxdata_add(not amped_tr_device.bypass, None)

#		#if devicetype != ['VSTConnection', 'VST/Remote Beta']:
#		#	device_plugindata.fxvisual_add(amped_tr_device.label, None)
#		#	device_plugindata.to_cvpj(cvpj_l, pluginid)
#
def ampedauto_to_cvpjauto_specs(autopoints, autospecs):
	v_min = 0
	v_max = 1
	if autospecs['type'] == 'numeric':
		v_min = autospecs['min']
		v_max = autospecs['max']

	ampedauto = []
	for autopoint in autopoints: ampedauto.append([autopoint['pos'], xtramath.between_from_one(v_min, v_max, autopoint['value'])])
	return ampedauto

def ampedauto_to_cvpjauto(autopoints):
	for autopoint in autopoints: yield autopoint['pos'], autopoint['value']

class input_amped(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'amped'
	def get_name(self): return 'Amped Studio'
	def get_priority(self): return 0
	def supported_autodetect(self): return True
	def detect(self, input_file): 
		try:
			zip_data = zipfile.ZipFile(input_file, 'r')
			if 'amped-studio-project.json' in zip_data.namelist(): return True
			else: return False
		except:
			return False

	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['amped']
		in_dict['track_lanes'] = True
		in_dict['audio_filetypes'] = ['wav', 'mp3', 'ogg', 'flac']
		in_dict['placement_cut'] = True
		in_dict['auto_types'] = ['nopl_points']
		in_dict['track_hybrid'] = True
		in_dict['audio_stretch'] = ['rate']
		in_dict['audio_nested'] = True
		in_dict['plugin_included'] = ['native:amped', 'universal:midi', 'user:reasonstudios:europa', 'universal:sampler:multi']

	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_amped

		global samplefolder

		try:
			zip_data = zipfile.ZipFile(input_file, 'r')
		except zipfile.BadZipFile as t:
			raise ProjectFileParserException('amped: Bad ZIP File: '+str(t))

		convproj_obj.type = 'r'
		convproj_obj.set_timings(1, True)

		globalstore.dataset.load('amped', './data_main/dataset/amped.dset')
		globalstore.dataset.load('synth_nonfree', './data_main/dataset/synth_nonfree.dset')

		samplefolder = dv_config.path_samples_extracted

		try:
			jsonfilenames = zip_data.read('filenames.json')
		except KeyError as t:
			raise ProjectFileParserException('amped: filenames.json not found')

		amped_filenames = json.loads(jsonfilenames)
		for amped_filename, realfilename in amped_filenames.items():
			old_file = os.path.join(samplefolder,amped_filename)
			new_file = os.path.join(samplefolder,realfilename)
			if os.path.exists(new_file) == False:
				zip_data.extract(amped_filename, path=samplefolder, pwd=None)
				os.rename(old_file,new_file)
			sampleref_obj = convproj_obj.sampleref__add(str(amped_filename), new_file, None)

		try:
			jsonproject = zip_data.read('amped-studio-project.json')
		except KeyError as t:
			raise ProjectFileParserException('amped: amped-studio-project.json not found')

		amped_project = json.loads(jsonproject)
		amped_obj = proj_amped.amped_project(amped_project)
		convproj_obj.params.add('bpm', amped_obj.tempo, 'float')
		convproj_obj.timesig = [amped_obj.timesig_num, amped_obj.timesig_den]

		convproj_obj.track_master.params.add('vol', amped_obj.masterTrack.volume, 'float')

		encode_devices(convproj_obj, amped_obj.masterTrack.devices, convproj_obj.track_master, None)

		for amped_track in amped_obj.tracks:
			amped_tr_id = str(amped_track.id)
			amped_armed = amped_track.armed if amped_track.armed else None

			track_obj = convproj_obj.track__add(amped_tr_id, 'hybrid', 1, False)
			track_obj.visual.name = amped_track.name
			track_obj.visual.color.set_float(AMPED_COLORS[amped_track.color])
			track_obj.params.add('vol', amped_track.volume, 'float')
			track_obj.params.add('pan', amped_track.pan, 'float')
			track_obj.params.add('enabled', bool(not amped_track.mute), 'bool')
			track_obj.params.add('solo', bool(amped_track.solo), 'bool')

			if amped_track.armed:
				amped_armed = amped_track.armed
				track_obj.armed.in_audio = amped_armed['mic'] if 'mic' in amped_armed else False
				track_obj.armed.in_keys = amped_armed['keys'] if 'keys' in amped_armed else False
				track_obj.armed.on = track_obj.armed.in_audio or track_obj.armed.in_keys

			amped_autodata = {}
			for amped_automation in amped_track.automations:
				autoname = amped_automation.param

				if not amped_automation.is_device:
					autoloc = None
					if autoname == 'volume': autoloc = ['track', amped_tr_id, 'vol']
					if autoname == 'pan': autoloc = ['track', amped_tr_id, 'pan']
					if autoloc: 
						for p, v in ampedauto_to_cvpjauto(amped_automation.points):
							convproj_obj.automation.add_autopoint(autoloc, 'float', p, v, 'normal')
				else:
					deviceid = amped_automation.deviceid
					if deviceid not in amped_autodata: amped_autodata[deviceid] = {}
					amped_autodata[deviceid][autoname] = ampedauto_to_cvpjauto_specs(amped_automation.points, amped_automation.spec)

			encode_devices(convproj_obj, amped_track.devices, track_obj, amped_autodata)

			for amped_region in amped_track.regions:
				amped_reg_color = AMPED_COLORS[amped_region.color]

				if amped_region.midi_notes: 
					placement_obj = track_obj.placements.add_notes()
					placement_obj.time.set_posdur(amped_region.position, amped_region.length+amped_region.offset)
					placement_obj.time.set_offset(amped_region.offset)
					placement_obj.visual.name = amped_region.name
					placement_obj.visual.color.set_float(amped_reg_color)
					for amped_note in amped_region.midi_notes:
						if amped_note['position'] >= 0:
							placement_obj.notelist.add_r(amped_note['position'], amped_note['length'], amped_note['key']-60, amped_note['velocity']/127, {})

				if amped_region.clips != []: 
					placement_obj = track_obj.placements.add_nested_audio()
					placement_obj.time.set_posdur(amped_region.position, amped_region.length+amped_region.offset)
					placement_obj.time.set_offset(amped_region.offset)
					placement_obj.visual.name = amped_region.name
					placement_obj.visual.color.set_float(amped_reg_color)

					for amped_clip in amped_region.clips:
						npa_obj = placement_obj.add()
						npa_obj.time.position = amped_clip.position
						npa_obj.time.duration = amped_clip.length
						amped_clip_offset = amped_clip.offset
						npa_obj.time.set_offset(amped_clip_offset*(120/amped_obj.tempo))
						sample_obj = npa_obj.sample
						sample_obj.vol = amped_clip.gain
						sample_obj.pitch = amped_clip.pitchShift
						sample_obj.sampleref = str(amped_clip.contentGuid.id)
						sample_obj.stretch.set_rate_speed(amped_obj.tempo, amped_clip.stretch, True)
						sample_obj.stretch.uses_tempo = True
						sample_obj.stretch.algorithm = 'stretch'
						sample_obj.reverse = amped_clip.reversed
