# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import struct
import os.path
import math
from objects import globalstore
from objects import colors
from functions import xtramath
from functions import data_xml
from functions.juce import juce_memoryblock

def do_visual(cvpj_visual, zb_visual, color_index, colordata):
	cvpj_visual.name = zb_visual.name
	if color_index != -1:
		colorfloat = colordata.getcolornum(color_index)
		cvpj_visual.color.set_int(colorfloat)
		cvpj_visual.color.fx_allowed = ['saturate', 'brighter']

def do_auto(convproj_obj, autoloc, curve, parammode):
	valtype = 'float'
	if parammode == 1: valtype = 'bool'
	if parammode == 2: valtype = 'bool'
	for p in curve.points:
		if parammode == 0: val = p.value
		if parammode == 1: val = p.value>0.5
		if parammode == 2: val = p.value<0.5
		if parammode == 3: val = (p.value-0.5)*2
		convproj_obj.automation.add_autopoint(autoloc, valtype, p.position, val, 'normal')

filter_types = {
	'1': 'low_pass',
	'2': 'high_pass',
	'3': 'band_pass',
	'4': 'notch'
}

def set_filter_type(filter_obj, num):
	if num in filter_types: filter_obj.type.set(filter_types[num], None)

def param_find(plugin_obj, cvpjname, xmldata, xmlname, add, mul):
	paramdata = data_xml.find_first(xmldata, xmlname)
	if paramdata is not None:
		paramval = float(paramdata.get('value'))
		if paramval is not None:
			param_obj = plugin_obj.params.add(cvpjname, (paramval+add)*mul, 'float')

def get_value(xmldata, xmlname, fallbackv):
	paramdata = data_xml.find_first(xmldata, xmlname)
	if paramdata is not None:
		paramval = float(paramdata.get('value'))
		return paramval if paramval is not None else fallbackv
	else: return fallbackv

def set_param_attrib(params_obj, cvpj_name, xml_name, attribvals, add, div):
	if xml_name in attribvals:
		params_obj.add(cvpj_name, (float(attribvals[xml_name])+add)/div, 'float')

def add_dataval(datavals_obj, plugin_xml_data, cvpj_name, xml_name, attribname, inval):
	x_firstv = data_xml.find_first(plugin_xml_data, xml_name)

	if x_firstv is not None: 
		paramv = x_firstv.get(attribname)
		if paramv is not None: datavals_obj.add(cvpj_name, inval(paramv))

def do_plugin(convproj_obj, strproc, track_obj, dawvert_intent):
	pluginid = strproc.uid
	#plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', strproc.plugin.name)
	#if strproc.stream_processor_type == 4:
	#	plugin_obj.role = 'synth'
	#	track_obj.plugslots.set_synth(pluginid)
	#if strproc.stream_processor_type == 3:
	#	plugin_obj.role = 'effect'
	#	track_obj.plugslots.slots_audio.append(pluginid)

	plugin_xml_data = strproc.plugin_xml_data

	if plugin_xml_data is not None:

		if strproc.plugin.format == 'StageLight':

			# ------------------------- Native -------------------------

			if strproc.plugin.name == 'ZC1':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'ZC1')
				plugin_obj.role = 'synth'
				track_obj.plugslots.set_synth(pluginid)
				attrib = plugin_xml_data.attrib
				if 'voice_count' in attrib: 
					plugin_obj.poly.max = int(attrib['voice_count'])
				if 'mod_wheel_value' in attrib: 
					plugin_obj.datavals.add('mod_wheel_value', float(attrib['mod_wheel_value']))
				for x_part in plugin_xml_data:
					if x_part.tag == 'zn':
						for x_inpart in x_part:
							if x_inpart.tag == 'state':
								extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, pluginid)
								try: 
									statedata = juce_memoryblock.fromJuceBase64Encoding(x_inpart.text)
									extmanu_obj.vst2__import_presetdata('raw', statedata, None)
								except: pass

			if strproc.plugin.name == 'Zenbeats Chorus':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'roland_chorus')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'RolandChorus')
				if xmlparams is not None:
					attribvals = xmlparams.attrib
					for pname in ['Sync', 'BeatDiv', 'BeatMult', 'Speed', 'Depth', 'Feedback', 'Spread', 'Mix']:
						set_param_attrib(plugin_obj.params, pname.lower(), pname, attribvals, 0, 1)

			if strproc.plugin.name == 'Zenbeats MultiVerb':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'roland_reverb')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'RolandReverb')
				if xmlparams is not None:
					attribvals = xmlparams.attrib
					for pname in ['Type', 'Time', 'PreDelay', 'HiPass', 'LoPass', 'Density']:
						set_param_attrib(plugin_obj.params, pname.lower(), pname, attribvals, 0, 1)

			if strproc.plugin.name == 'Zenbeats SC-Comp':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'roland_sccomp')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'RolandDynamics')
				if xmlparams is not None:
					attribvals = xmlparams.attrib
					for pname in ['RMSMode', 'CmpAutoGain', 'CmpAttack', 'CmpRelease', 
						'CmpThreshold', 'CmpRatio', 'CmpKnee', 'CmpMakeupGain', 'ExpAttack', 
						'ExpRelease', 'ExpThreshold', 'ExpRatio', 'ExpKnee', 
						'ExpHold', 'HiPassFreq', 'SidechainMode', 'Sidechain']:
						set_param_attrib(plugin_obj.params, pname.lower(), pname, attribvals, 0, 1)

			if strproc.plugin.name == 'Zenbeats SC-Pump':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'roland_scpump')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'ZenbeatsSCPump')
				if xmlparams is not None:
					add_dataval(plugin_obj.datavals, xmlparams, 'input_trigger_type', 'input_trigger_type', 'type', int)
					add_dataval(plugin_obj.datavals, xmlparams, 'envelope_action', 'envelope_action', 'action', int)
					add_dataval(plugin_obj.datavals, xmlparams, 'filter_index', 'filter_index', 'index', int)
					add_dataval(plugin_obj.datavals, xmlparams, 'window_len', 'window_len', 'beats', float)
					add_dataval(plugin_obj.datavals, xmlparams, 'random', 'random', 'seed', int)

					for pname in ['CrossfadeTime', 'InputTriggerLevel', 'RandomFloor', 'RandomCeiling', 
						'RandomStartAttack', 'RandomEndAttack', 'RandomStartRelease', 'RandomEndRelease', 
						'FilterResonance', 'RandomResonance', 'AttackStartX', 'AttackStartY', 'AttackControlX1', 
						'AttackControlY', 'AttackEndX', 'AttackEndY', 'ReleaseStartX', 'ReleaseStartY', 
						'ReleaseControlX1', 'ReleaseControlY', 'ReleaseEndX', 'ReleaseEndY']:
						param_find(plugin_obj, pname.lower(), xmlparams, pname, 0, 1)

			if strproc.plugin.name == 'Zenbeats SC-Envelope':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'zenbeats_scenvelope')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'ZenbeatsSCEnvelope')
				if xmlparams is not None:
					add_dataval(plugin_obj.datavals, xmlparams, 'input_trigger_type', 'input_trigger_type', 'type', int)
					add_dataval(plugin_obj.datavals, xmlparams, 'envelope_action', 'envelope_action', 'action', int)
					add_dataval(plugin_obj.datavals, xmlparams, 'filter_index', 'filter_index', 'index', int)
					add_dataval(plugin_obj.datavals, xmlparams, 'window_len', 'window_len', 'beats', float)
					add_dataval(plugin_obj.datavals, xmlparams, 'random', 'random', 'seed', int)

					for pname in ['CrossfadeTime', 'InputTriggerLevel', 'RandomFloor', 'RandomCeiling', 
						'RandomStartAttack', 'RandomEndAttack', 'RandomStartRelease', 'RandomEndRelease', 
						'FilterResonance', 'RandomResonance', 'AttackStartX', 'AttackStartY', 'AttackControlX1', 
						'AttackControlY', 'AttackEndX', 'AttackEndY', 'ReleaseStartX', 'ReleaseStartY', 
						'ReleaseControlX1', 'ReleaseControlY', 'ReleaseEndX', 'ReleaseEndY']:
						param_find(plugin_obj, pname.lower(), xmlparams, pname, 0, 1)

			if strproc.plugin.name == 'AutoWah':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'autowah')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'AutoWah')
				if xmlparams is not None:
					filterdata = data_xml.find_first(xmlparams, 'Filter')
					if filterdata is not None:
						plugin_obj.filter.on = True
						set_filter_type(plugin_obj.filter, filterdata.get('filterType'))
						plugin_obj.filter.freq = get_value(filterdata, 'Freq', 18007)
						plugin_obj.filter.q = get_value(filterdata, 'Res', 1)
						lfodata = data_xml.find_first(filterdata, 'LFO')
						if lfodata is not None:
							lfo_obj = plugin_obj.lfo_add('cutoff')
							lfo_obj.time.set_steps(get_value(lfodata, 'LFOF', 1)*4, convproj_obj)
					for pname in ['Threshold', 'Attack', 'Release', 'Base', 'Strength']:
						param_find(plugin_obj, pname.lower(), xmlparams, pname, 0, 1)

			if strproc.plugin.name == 'Chorus':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'chorus')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'Chorus')
				if xmlparams is not None:
					lfodata = data_xml.find_first(xmlparams, 'LFO')
					if lfodata is not None:
						lfo_obj = plugin_obj.lfo_add('chorus')
						lfo_obj.time.set_hz(get_value(lfodata, 'Speed', 1)*4)
					for pname in ['Delay', 'Depth', 'Stereo']:
						param_find(plugin_obj, pname.lower(), xmlparams, pname, 0, 1)

			if strproc.plugin.name == 'BitCrusher':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'bitcrusher')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'BitCrusher')
				if xmlparams is not None:
					for pname in ['Noise', 'Bits', 'Rate']:
						param_find(plugin_obj, pname.lower(), xmlparams, pname, 0, 1)

			if strproc.plugin.name == 'Delay':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'delay')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				attrib = plugin_xml_data.attrib
				if 'Quantize' in attrib: plugin_obj.datavals.add('quantize', float(attrib['Quantize']))
				if 'linking' in attrib: plugin_obj.datavals.add('linking', float(attrib['linking']))
				xmlparams = data_xml.find_first(plugin_xml_data, 'Delay')
				if xmlparams is not None:
					for txt_end in ['1', '2']:
						for txt_start in ['Gain', 'Feedback', 'Rate', 'Pan', 'LowCut', 'HighCut']:
							pname = txt_start+txt_end
							param_find(plugin_obj, pname.lower(), xmlparams, pname, 0, 1)

			if strproc.plugin.name == 'Drive':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'drive')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'Drive')
				if xmlparams is not None:
					for pname in ['PreGain', 'Hardness', 'Threshold', 'Overdrive']:
						param_find(plugin_obj, pname.lower(), xmlparams, pname, 0, 1)

			if strproc.plugin.name == 'Reverb':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'reverb')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'Reverb')
				if xmlparams is not None:
					for pname in ['Size', 'Damping', 'Width', 'HighCut', 'LowCut', 'PreDelay']:
						param_find(plugin_obj, pname.lower(), xmlparams, pname, 0, 1)

			if strproc.plugin.name == 'Zenbeats EQ':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'zenbeats_eq')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'RolandEQ')
				if xmlparams is not None:
					attribvals = xmlparams.attrib
					for eq_start in ['Hi', 'Lo']:
						for eq_end in ['Enable', 'Freq', 'Gain', 'Q', 'Shelf']:
							pname = eq_start+eq_end
							set_param_attrib(plugin_obj.params, pname, pname, attribvals, 0, 1)
					for eq_start in ['HiMid', 'Mid', 'LoMid']:
						for eq_end in ['Enable', 'Freq', 'Gain', 'Q']:
							pname = eq_start+eq_end
							set_param_attrib(plugin_obj.params, pname, pname, attribvals, 0, 1)

			if strproc.plugin.name == 'AutoFilter':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'zenbeats', 'autofilter')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'AutoFilter')
				if xmlparams is not None:
					attribvals = xmlparams.attrib
					set_param_attrib(plugin_obj.params, 'filterType', 'filterType', attribvals, 0, 1)
					param_find(plugin_obj, 'lfo', xmlparams, 'LFO', 0, 1)
					param_find(plugin_obj, 'freq', xmlparams, 'Freq', 0, 1)
					param_find(plugin_obj, 'res', xmlparams, 'Res', 0, 1)
					param_find(plugin_obj, 'lfof', xmlparams, 'LFOF', 0, 1)

			# ------------------------- Universal -------------------------

			if strproc.plugin.name == 'Drums':
				track_obj.is_drum = True
				xmlparams = data_xml.find_first(plugin_xml_data, 'drumkit')
				plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'sampler', 'drums')
				plugin_obj.role = 'synth'
				track_obj.plugslots.set_synth(pluginid)

				if xmlparams is not None:
					soundnum = 0
					for x in xmlparams:
						if x.tag == 'sound':
							attribvals = x.attrib

							drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()

							drumpad_obj.key = soundnum-24
							if 'name' in attribvals: drumpad_obj.visual.name = attribvals['name']
							if 'gain' in attribvals: drumpad_obj.vol = float(attribvals['gain'])
							if 'mute' in attribvals: drumpad_obj.enabled = not bool(int(attribvals['mute']))

							layer_obj.samplepartid = 'drum_%i' % soundnum
							sp_obj = plugin_obj.samplepart_add(layer_obj.samplepartid)
							if 'pitch' in attribvals:
								sp_obj.pitch = (float(attribvals['pitch'])-0.5)*24
							if 'fine_pitch_offset' in attribvals:
								sp_obj.pitch += (float(attribvals['fine_pitch_offset']))
							if 'timestretch' in attribvals:
								timestretch = float(attribvals['timestretch'])
								if timestretch:
									stretch_obj = sp_obj.stretch
									stretch_obj.timing.set__speed(timestretch)
									stretch_obj.preserve_pitch = True
							if 'reverse' in attribvals:
								sp_obj.reverse = bool(int(attribvals['reverse']))

							sampledata = x.findall('sample')
							if sampledata:
								sampattrib = sampledata[0].attrib
								if 'filename' in sampattrib:
									filename = sampattrib['filename']
									filepath = os.path.join(dawvert_intent.input_folder, 'Drum Sampler Files', filename)
									sampleref_obj = convproj_obj.sampleref__add(filepath, filepath, 'win')
									sampleref_obj.search_local(dawvert_intent.input_folder)
									sp_obj.from_sampleref(convproj_obj, filepath)

							soundnum += 1

			if strproc.plugin.name == 'Zenbeats Limiter':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'limiter', None)
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'ZBLimiter')
				if xmlparams is not None:
					attribvals = xmlparams.attrib

					set_param_attrib(plugin_obj.params, 'release', 'Release', attribvals, 0, 100)
					set_param_attrib(plugin_obj.params, 'threshold', 'Threshold', attribvals, 0, 1)
					set_param_attrib(plugin_obj.params, 'ceiling', 'Ceiling', attribvals, 0, 1)
	
			if strproc.plugin.name == 'Equalizer':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'eq', '8limited')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'Equalizer')
				if xmlparams is not None:
					for fnum in range(4):
						filterparams = data_xml.find_first(xmlparams, 'filter%i'%(fnum))
						if filterparams:
							dynamicfilter = data_xml.find_first(filterparams, 'DynamicFilter')
							if dynamicfilter:
								if fnum == 0: 
									filter_obj = plugin_obj.named_filter_add('low_shelf')
									filter_obj.type.set('low_shelf', None)
								if fnum == 1: 
									filter_obj = plugin_obj.named_filter_add('peak_1')
									filter_obj.type.set('peak', None)
								if fnum == 2: 
									filter_obj = plugin_obj.named_filter_add('peak_2')
									filter_obj.type.set('peak', None)
								if fnum == 3: 
									filter_obj = plugin_obj.named_filter_add('high_shelf')
									filter_obj.type.set('high_shelf', None)
								filter_obj.on = True
								filter_obj.freq = get_value(dynamicfilter, 'Freq%i'%(fnum+1), 10000)
								filter_obj.gain = get_value(dynamicfilter, 'Gain', 0)

			if strproc.plugin.name == 'Limiter':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'limiter', None)
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'Limiter')
				if xmlparams is not None:
					param_find(plugin_obj, 'pregain', xmlparams, 'Gain', 0, 1)
					param_find(plugin_obj, 'release', xmlparams, 'Release', 0, 0.001)
					param_find(plugin_obj, 'threshold', xmlparams, 'Threshold', 0, 1)

			if strproc.plugin.name == 'Compressor':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'compressor', None)
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'Compressor')
				if xmlparams is not None:
					param_find(plugin_obj, 'threshold', xmlparams, 'Threshold', 0, 1)
					param_find(plugin_obj, 'ratio', xmlparams, 'Ratio', 0, 1)
					param_find(plugin_obj, 'attack', xmlparams, 'Attack', 0, 0.001)
					param_find(plugin_obj, 'release', xmlparams, 'Release', 0, 0.001)
					param_find(plugin_obj, 'lookahead', xmlparams, 'Lookahead', 0, 0.001)
					param_find(plugin_obj, 'gain', xmlparams, 'Gain', 0, 1)
					param_find(plugin_obj, 'knee', xmlparams, 'Knee', 0, 1)

			if strproc.plugin.name == 'Filter':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'filter', None)
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)
				xmlparams = data_xml.find_first(plugin_xml_data, 'Filter')
				if xmlparams is not None:
					plugin_obj.filter.on = True
					set_filter_type(plugin_obj.filter, xmlparams.get('filterType'))
					plugin_obj.filter.freq = get_value(xmlparams, 'Freq', 18007)
					plugin_obj.filter.q = get_value(xmlparams, 'Res', 1)

def do_rack(convproj_obj, project_obj, track_obj, zb_track, autoloc, dawvert_intent):

	for rack in project_obj.bank.racks:

		if rack.uid==zb_track.output_rack_uid:
			track_obj.params.add('vol', rack.gain, 'float')
			track_obj.params.add('solo', bool(rack.solo), 'bool')
			track_obj.params.add('mute', bool(rack.mute), 'bool')

			for send_track in rack.send_tracks:
				track_obj.sends.add(send_track.send_track_uid, None, send_track.send_amount)

			for curve in rack.automation_set.curves:
				if rack.uid==curve.target_object:
					if curve.target == 'DT_RACK':
						if curve.function == 'DF_POST_GAIN': do_auto(convproj_obj, autoloc+['vol'], curve, 0)
						if curve.function == 'DF_PAN': do_auto(convproj_obj, autoloc+['pan'], curve, 3)
						if curve.function == 'DF_MUTE': do_auto(convproj_obj, autoloc+['enabled'], curve, 2)
						if curve.function == 'DF_SOLO': do_auto(convproj_obj, autoloc+['solo'], curve, 1)

			if rack.signal_chain:
				strprocs = rack.signal_chain.stream_processors
	
				for strproc in strprocs:
					if strproc.plugin:
						do_plugin(convproj_obj, strproc, track_obj, dawvert_intent)
	
			break


class input_zenbeats(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'zenbeats'
	
	def get_name(self):
		return 'ZenBeats'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import zenbeats as proj_zenbeats

		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.type = 'r'

		traits_obj = convproj_obj.traits
		traits_obj.audio_filetypes = ['wav']
		traits_obj.audio_stretch = ['rate']
		traits_obj.auto_types = ['nopl_points']
		traits_obj.placement_cut = True
		traits_obj.placement_loop = ['loop', 'loop_eq', 'loop_off', 'loop_adv', 'loop_adv_off']
		traits_obj.plugin_ext_platforms = ['win']

		convproj_obj.set_timings(1, True)

		globalstore.dataset.load('zenbeats', './data_main/dataset/zenbeats.dset')
		colordata = colors.colorset.from_dataset('zenbeats', 'global', 'main')

		project_obj = proj_zenbeats.zenbeats_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.params.add('bpm', project_obj.bpm, 'float')
		convproj_obj.timesig = [project_obj.time_signature_numerator, project_obj.time_signature_denominator]

		convproj_obj.transport.loop_active = bool(project_obj.loop)
		convproj_obj.transport.loop_start = project_obj.loop_start
		convproj_obj.transport.loop_end = project_obj.loop_end
		convproj_obj.transport.current_pos = project_obj.play_start_marker

		added_samples = []

		master_id = None
		track_groups = []

		assoc_rack = {}

		for zb_track in project_obj.tracks:
			assoc_rack[zb_track.output_rack_uid] = zb_track.uid

			if zb_track.type == 258: 
				track_groups.append(zb_track.uid)
				track_obj = convproj_obj.fx__group__add(zb_track.uid)
				do_rack(convproj_obj, project_obj, track_obj, zb_track, ['group', zb_track.uid], dawvert_intent)
				do_visual(track_obj.visual, zb_track.visual, zb_track.color_index, colordata)

			if zb_track.type == 130: 
				return_obj = convproj_obj.track_master.fx__return__add(zb_track.uid)
				do_rack(convproj_obj, project_obj, return_obj, zb_track, ['return', zb_track.uid], dawvert_intent)
				do_visual(return_obj.visual, zb_track.visual, zb_track.color_index, colordata)

			if zb_track.type == 18: 
				master_id = zb_track.uid
				do_rack(convproj_obj, project_obj, convproj_obj.track_master, zb_track, ['master'], dawvert_intent)
				do_visual(convproj_obj.track_master.visual, zb_track.visual, zb_track.color_index, colordata)

		for zb_track in project_obj.tracks:
			master_id = zb_track.sub_track_master_track_uid
			if master_id in track_groups or master_id==None:
				if zb_track.type in [0, 1, 97]:
					track_obj = convproj_obj.track__add(zb_track.uid, 'instrument', 1, False)
					do_rack(convproj_obj, project_obj, track_obj, zb_track, ['track', zb_track.uid], dawvert_intent)
					do_visual(track_obj.visual, zb_track.visual, zb_track.color_index, colordata)
					if master_id: track_obj.group = master_id

					track_obj.armed.in_keys = bool(zb_track.arm_record)
					track_obj.armed.on = track_obj.armed.in_keys

					for zb_pattern in zb_track.patterns:
						placement_obj = track_obj.placements.add_notes()
						time_obj = placement_obj.time
						do_visual(placement_obj.visual, zb_pattern.visual, zb_pattern.color_index, colordata)
						time_obj.set_startend(zb_pattern.start_beat, zb_pattern.end_beat)
						time_obj.set_loop_data(zb_pattern.loop_play_start, zb_pattern.loop_start_beat, zb_pattern.loop_end_beat)

						placement_obj.muted = not zb_pattern.active
						placement_obj.locked = zb_pattern.locked

						cvpj_notelist = placement_obj.notelist

						for zb_note in zb_pattern.notes:
							note_dur = max(zb_note.end-zb_note.start, 0)
							extradata = {}
							if zb_note.probability != 1: extradata['probability'] = zb_note.probability
							cvpj_notelist.add_r(zb_note.start, note_dur, zb_note.semitone-60, zb_note.velocity/127, extradata if extradata else None)
							cvpj_notelist.last_add_pan((zb_note.pan_linear-0.5)*2)
							cvpj_notelist.last_add_finepitch(zb_note.pitch_offset)

				if zb_track.type == 2:
					track_obj = convproj_obj.track__add(zb_track.uid, 'audio', 1, False)
					do_rack(convproj_obj, project_obj, track_obj, zb_track, ['track', zb_track.uid], dawvert_intent)
					do_visual(track_obj.visual, zb_track.visual, zb_track.color_index, colordata)
					if master_id: track_obj.group = master_id

					track_obj.armed.in_audio = bool(zb_track.arm_record)
					track_obj.armed.on = track_obj.armed.in_audio

					for zb_pattern in zb_track.patterns:
						placement_obj = track_obj.placements.add_audio()
						do_visual(placement_obj.visual, zb_pattern.visual, zb_pattern.color_index, colordata)
						time_obj = placement_obj.time
						time_obj.set_startend(zb_pattern.start_beat, zb_pattern.end_beat)
						time_obj.set_loop_data(zb_pattern.loop_play_start, zb_pattern.loop_start_beat, zb_pattern.loop_end_beat)

						placement_obj.muted = not zb_pattern.active
						placement_obj.locked = zb_pattern.locked

						if zb_pattern.audio_file:
							if zb_pattern.audio_file not in added_samples:
								sampleref_obj = convproj_obj.sampleref__add(zb_pattern.audio_file, zb_pattern.audio_file, None)
								sampleref_obj.search_local(os.path.dirname(dawvert_intent.input_file))
								added_samples.append(zb_pattern.audio_file)
	
							sp_obj = placement_obj.sample
							sp_obj.sampleref = zb_pattern.audio_file
							speedrate = zb_pattern.preserve_pitch if zb_pattern.preserve_pitch is not None else 1
							if zb_pattern.preserve_pitch: speedrate *= 120/zb_pattern.audio_file_original_bpm

							stretch_obj = sp_obj.stretch
							stretch_obj.timing.set__orgtempo(zb_pattern.audio_file_original_bpm)

							stretch_obj.preserve_pitch = True
							if zb_pattern.audio_pitch is not None: sp_obj.pitch += math.log2(1/zb_pattern.audio_pitch)*-12
							if zb_pattern.audio_gain is not None: sp_obj.vol = zb_pattern.audio_gain
							if zb_pattern.audio_pan is not None: sp_obj.pan = zb_pattern.audio_pan
							if zb_pattern.reverse_audio is not None: sp_obj.reverse = zb_pattern.reverse_audio
							if zb_pattern.preserve_pitch is not None: stretch_obj.preserve_pitch = bool(zb_pattern.preserve_pitch)

				#else:
				#	print(zb_track.type, zb_track.visual.name)

		#exit()