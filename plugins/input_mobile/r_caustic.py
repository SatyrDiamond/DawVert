# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass

from objects import globalstore
from functions import xtramath

import json
import os.path
import plugins
import struct

caustic_fxtype = {}
caustic_fxtype[0] = 'delay'
caustic_fxtype[1] = 'reverb'
caustic_fxtype[2] = 'distortion'
caustic_fxtype[3] = 'compressor'
caustic_fxtype[4] = 'bitcrush'
caustic_fxtype[5] = 'flanger'
caustic_fxtype[6] = 'phaser'
caustic_fxtype[7] = 'chorus'
caustic_fxtype[8] = 'auto_wah'
caustic_fxtype[9] = 'parameq'
caustic_fxtype[10] = 'limiter'
caustic_fxtype[11] = 'vinylsim'
caustic_fxtype[12] = 'comb'
caustic_fxtype[14] = 'cabsim'
caustic_fxtype[16] = 'staticflanger'
caustic_fxtype[17] = 'filter'
caustic_fxtype[18] = 'octaver'
caustic_fxtype[19] = 'vibrato'
caustic_fxtype[20] = 'tremolo'
caustic_fxtype[21] = 'autopan'

patletters = ['A','B','C','D']
patids = []
for x in patletters:
	for v in range(16):
		patids.append(x+str(v+1))

def add_caustic_fx(convproj_obj, track_obj, caustic_fx, start_plugid):
	for slotnum, caustic_fx_data in enumerate(caustic_fx):
		fx_pluginid = start_plugid+'_slot'+str(slotnum+1)

		if caustic_fx_data.fx_type not in [4294967295, -1]:
			fxtype = caustic_fxtype[caustic_fx_data.fx_type]
			controls_data = caustic_fx_data.controls.data

			plugin_obj = convproj_obj.plugin__add(fx_pluginid, 'native', 'caustic', fxtype)
			plugin_obj.role = 'fx'
			plugin_obj.fxdata_add(bool(not int(controls_data[5])), 1)
			plugin_obj.visual.from_dset('caustic', 'plugin_fx', fxtype, True)
			plugin_obj.datavals.add('mode', caustic_fx_data.mode)
			for param_id, dset_param in globalstore.dataset.get_params('caustic', 'plugin_fx', fxtype):
				if param_id != '5':
					outval = controls_data[int(param_id)] if int(param_id) in controls_data else None
					plugin_obj.dset_param__add(param_id, outval, dset_param)

			track_obj.plugslots.slots_audio.append(fx_pluginid)

def add_controls(plugin_obj, mach_id, controls):
	fldso = globalstore.dataset.get_obj('caustic', 'plugin_inst', mach_id)
	if fldso:
		for param_id, dset_param in fldso.params.iter():
			outval = controls.data[int(param_id)] if int(param_id) in controls.data else None
			plugin_obj.dset_param__add(param_id, outval, dset_param)

def loopmode_cvpj(wavdata, sp_obj): 
	lm = wavdata.mode
	sp_obj.end = wavdata.end
	if lm in [0,1,2,3]: sp_obj.start = wavdata.start
	if lm in [4,5]: sp_obj.start = 0
	sp_obj.trigger = 'normal' if lm == 0 else 'oneshot'

	if lm in [2,3,4,5]: 
		sp_obj.loop_active = True
		sp_obj.loop_start = wavdata.start
		sp_obj.loop_end = wavdata.end
	if lm in [0,1]: sp_obj.loop_active = False
	if lm in [2,4]: sp_obj.loop_mode = "normal"
	if lm in [3,5]: sp_obj.loop_mode = "pingpong"

@dataclass
class mixertrack:
	vol: float = 1
	pan: float = 0
	send_reverb: float = 0
	send_delay: float = 0
	eq_low: float = 1
	eq_mid: float = 1
	eq_high: float = 1
	width: float = 0
	mute: bool = False
	solo: bool = False

class input_cvpj_r(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'caustic'
	
	def get_name(self):
		return 'Caustic 3'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['native:caustic','universal:sampler:single','universal:sampler:multi']
		in_dict['projtype'] = 'ri'

	def parse(self, convproj_obj, dawvert_intent):
		from objects import audio_data
		from objects.file_proj_past import caustic as proj_caustic
		
		global dataset

		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.type = 'ri'

		traits_obj = convproj_obj.traits
		traits_obj.placement_cut = True
		traits_obj.placement_loop = ['loop']
		traits_obj.audio_stretch = ['warp']
		traits_obj.auto_types = ['pl_points', 'nopl_points']
		traits_obj.fxchain_mixer = True
		traits_obj.audio_filetypes = ['wav']

		convproj_obj.set_timings(1.0)

		globalstore.dataset.load('caustic', './data_main/dataset/caustic.dset')

		project_obj = proj_caustic.caustic_project()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		samplefolder = dawvert_intent.path_samples['extracted']

		mixer_tracks = [mixertrack() for x in range(14)]

		for mixnum, ctrldata in enumerate(project_obj.mixr.controls):
			for paramnum in range(7): 
				paramnumid = paramnum+(mixnum*7)
				mixer_tracks[paramnumid].vol = ctrldata.data[paramnum]
				mixer_tracks[paramnumid].pan = (ctrldata.data[paramnum+64]-0.5)*2
				mixer_tracks[paramnumid].width = ctrldata.data[paramnum+72]
				mixer_tracks[paramnumid].send_delay = ctrldata.data[(paramnum*2)+8]
				mixer_tracks[paramnumid].send_reverb = ctrldata.data[(paramnum*2)+9]
				mixer_tracks[paramnumid].eq_low = ctrldata.data[paramnum+24]
				mixer_tracks[paramnumid].eq_mid = ctrldata.data[paramnum+32]
				mixer_tracks[paramnumid].eq_high = ctrldata.data[paramnum+40]

		for paramnum in range(14): 
			mixer_tracks[paramnum].mute = bool(project_obj.mixr.solo_mute[paramnum*2])
			mixer_tracks[paramnum].solo = bool(project_obj.mixr.solo_mute[(paramnum*2)+1])

		cvpj_tracks = []

		for machnum, machine in enumerate(project_obj.machines):
			machid = str(machnum)
			pluginid = 'machine'+machid
			cvpj_trackid = 'MACH'+machid

			track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, True)
			track_obj.visual.from_dset('caustic', 'plugin_inst', machine.mach_id, True)
			if machine.name: track_obj.visual.name = machine.name
			track_obj.plugslots.set_synth(pluginid)
			cvpj_tracks.append(track_obj)

			machdata = machine.data

			if machine.mach_id == 'PCMS':
				middlenote = 0
				if 'Select preset' not in machdata.presetname: track_obj.visual.name = machdata.presetname

				track_obj.params.add('usemasterpitch', True, 'bool')
				if len(machdata.samples) == 1:
					singlewav = machdata.samples[0]
					if singlewav.key_lo == 24 and singlewav.key_hi == 108: isMultiSampler = False
					else: isMultiSampler = True
				else: isMultiSampler = True

				if not isMultiSampler:
					region = machdata.samples[0]

					sampleref = machid + '_PCMSynth_0'
					wave_path = samplefolder+sampleref+'.wav'

					if region.samp_chan != 0: 
						audio_obj = audio_data.audio_obj()
						audio_obj.channels = region.samp_chan
						audio_obj.rate = region.samp_hz
						audio_obj.set_codec('int16')
						audio_obj.pcm_from_bytes(region.samp_data)
						if region.mode not in [0, 1]: audio_obj.loop = [region.start, region.end]
						audio_obj.to_file_wav(wave_path)

						plugin_obj, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler(pluginid, wave_path, None)

						sampleref_obj.set_fileformat('wav')
						audio_obj.to_sampleref_obj(sampleref_obj)

						loopmode_cvpj(region, sp_obj)
						sp_obj.point_value_type = "samples"

					middlenote += region.key_root-60
				else:
					plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'sampler', 'multi')
					plugin_obj.role = 'synth'
					for samplecount, data in enumerate(machdata.samples):
						region = data
						loopdata = None
						sampleref = machid + '_PCMSynth_'+str(samplecount)
						wave_path = samplefolder+sampleref+'.wav'

						audio_obj = audio_data.audio_obj()
						audio_obj.channels = region.samp_chan
						audio_obj.rate = region.samp_hz
						audio_obj.set_codec('int16')
						audio_obj.pcm_from_bytes(region.samp_data)
						if region.mode not in [0, 1]: audio_obj.loop = [region.start, region.end]
						audio_obj.to_file_wav(wave_path)

						sampleref_obj = convproj_obj.sampleref__add(wave_path, wave_path, None)
						sampleref_obj.set_fileformat('wav')
						audio_obj.to_sampleref_obj(sampleref_obj)

						sp_obj = plugin_obj.sampleregion_add(region.key_lo-60, region.key_hi-60, region.key_root-60, None)
						sp_obj.vol = region.volume
						sp_obj.pan = (region.pan-0.5)*2
						loopmode_cvpj(region, sp_obj)
						sp_obj.length = sp_obj.end
						sp_obj.sampleref = wave_path
						sp_obj.point_value_type = 'samples'

				if machdata.samples:
					pcms_c = machdata.controls.data

					middlenote += int(pcms_c[1]*12)
					middlenote += int(pcms_c[2])

					track_obj.params.add('pitch', pcms_c[3]/100, 'float')
					track_obj.datavals.add('middlenote', -middlenote)
					plugin_obj.env_asdr_add('vol', 0, pcms_c[5], 0, pcms_c[6], pcms_c[7], pcms_c[8], 1)

			if machine.mach_id == 'BBOX':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'sampler', 'drums')
				plugin_obj.role = 'synth'
				track_obj.params.add('usemasterpitch', False, 'bool')
				track_obj.is_drum = True

				drumdata = []

				for samplecount, bbox_sample in enumerate(machdata.samples):
					region = bbox_sample
					sampleref = machid + '_BeatBox_'+str(samplecount)
					wave_path = samplefolder+sampleref+'.wav'
					if region.chan != 0 and region.hz != 0: 
						audio_obj = audio_data.audio_obj()
						audio_obj.channels = region.chan
						audio_obj.rate = region.hz
						audio_obj.set_codec('int16')
						audio_obj.pcm_from_bytes(region.data)
						audio_obj.to_file_wav(wave_path)

					sampleref_obj = convproj_obj.sampleref__add(wave_path, wave_path, None)
					sampleref_obj.set_fileformat('wav')
					audio_obj.to_sampleref_obj(sampleref_obj)

					drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
					drumpad_obj.key = samplecount-12
					drumpad_obj.visual.name = region.name
					drumpad_obj.enabled = not bool(region.mute)

					layer_obj.samplepartid = 'drum_%i' % samplecount
					sp_obj = plugin_obj.samplepart_add(layer_obj.samplepartid)
					sp_obj.start = 0
					sp_obj.end = region.len
					sp_obj.point_value_type = "samples"
					sp_obj.sampleref = wave_path
					drumdata.append([drumpad_obj, sp_obj])

				controlsdata = machdata.controls.data
				
				try:
					for n, cd in enumerate(drumdata):
						drumpad_obj, sp_obj = cd
						vol = controlsdata[3+n]
						pan = controlsdata[35+n]
						tune = controlsdata[11+n]
						drumpad_obj.vol = vol
						drumpad_obj.pan = (pan-0.5)*2
						sp_obj.pitch = tune
				except:
					pass

				if 'Select Kit' not in machdata.presetname: track_obj.visual.name = machdata.presetname

			if machine.mach_id == 'SSYN':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'caustic', 'SSYN')
				plugin_obj.role = 'synth'
				add_controls(plugin_obj, 'SSYN', machdata.controls)
				if 'Select preset' not in machdata.presetname: track_obj.visual.name = machdata.presetname

				if machdata.customwaveform1: 
					wave_obj = plugin_obj.wave_add('customwaveform1')
					wave_obj.set_all_range(machdata.customwaveform1, -157, 157)

				if machdata.customwaveform2: 
					wave_obj = plugin_obj.wave_add('customwaveform2')
					wave_obj.set_all_range(machdata.customwaveform2, -157, 157)

			if machine.mach_id == 'BLNE':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'caustic', 'BLNE')
				plugin_obj.role = 'synth'
				add_controls(plugin_obj, 'BLNE', machdata.controls)
				if 'Select preset' not in machdata.presetname: track_obj.visual.name = machdata.presetname

				if machdata.customwaveform1: 
					wave_obj = plugin_obj.wave_add('customwaveform1')
					wave_obj.set_all_range(machdata.customwaveform1, -157, 157)

			if machine.mach_id == 'PADS':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'caustic', 'PADS')
				plugin_obj.role = 'synth'
				add_controls(plugin_obj, 'PADS', machdata.controls)
				if 'Select preset' not in machdata.presetname: track_obj.visual.name = machdata.presetname

				harmonics_obj = plugin_obj.harmonics_add('harm1')
				for n, i in enumerate(machdata.harm1): harmonics_obj.add(n+1, (i+96)/96, {})
				harmonics_obj = plugin_obj.harmonics_add('harm2')
				for n, i in enumerate(machdata.harm2): harmonics_obj.add(n+1, (i+96)/96, {})
				plugin_obj.datavals.add('harm1_vol', machdata.harm1vol)
				plugin_obj.datavals.add('harm2_vol', machdata.harm2vol)

			if machine.mach_id == 'ORGN':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'caustic', 'ORGN')
				plugin_obj.role = 'synth'
				add_controls(plugin_obj, 'ORGN', machdata.controls)
				if 'Select preset' not in machdata.presetname: track_obj.visual.name = machdata.presetname

			if machine.mach_id == 'FMSN':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'caustic', 'FMSN')
				plugin_obj.role = 'synth'
				add_controls(plugin_obj, 'FMSN', machdata.controls)
				plugin_obj.datavals.add('algorithm', machdata.algorithm)
				if 'Select preset' not in machdata.presetname: track_obj.visual.name = machdata.presetname

			if machine.mach_id == 'KSSN':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'caustic', 'KSSN')
				plugin_obj.role = 'synth'
				add_controls(plugin_obj, 'KSSN', machdata.controls)
				if 'Select preset' not in machdata.presetname: track_obj.visual.name = machdata.presetname

			if machine.mach_id == 'SAWS':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'caustic', 'SAWS')
				plugin_obj.role = 'synth'
				add_controls(plugin_obj, 'SAWS', machdata.controls)
				if 'Select preset' not in machdata.presetname: track_obj.visual.name = machdata.presetname

			if machine.mach_id == '8SYN':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'caustic', '8SYN')
				plugin_obj.role = 'synth'
				add_controls(plugin_obj, '8SYN', machdata.controls)
				plugin_obj.datavals.add('bitcode1', machdata.bitcode1)
				plugin_obj.datavals.add('bitcode2', machdata.bitcode2)
				if 'Select preset' not in machdata.presetname: track_obj.visual.name = machdata.presetname

			if machine.mach_id == 'VCDR':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'caustic', 'VCDR')
				plugin_obj.role = 'synth'
				add_controls(plugin_obj, 'VCDR', machdata.controls)
				plugin_obj.datavals.add('current_number', machdata.currentnumber)

				for samplenum, sd in enumerate(machdata.samples):
					sampleinfo = sd
					if sampleinfo.data:
						sampleref = machid + '_Vocoder_'+str(samplenum)
						wave_path = samplefolder+sampleref+'.wav'
						audio_obj = audio_data.audio_obj()

						audio_obj.channels = 1
						audio_obj.rate = sampleinfo.hz
						audio_obj.set_codec('int16')
						audio_obj.pcm_from_bytes(sampleinfo.data)
						audio_obj.to_file_wav(wave_path)

						plugin_obj, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler(pluginid, wave_path, None)
						sp_obj.point_value_type = "samples"

			if machine.mach_id == 'MDLR':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'caustic', 'MDLR')
				plugin_obj.role = 'synth'
				add_controls(plugin_obj, 'MDLR', machdata.controls)
				if 'Select preset' not in machdata.presetname: track_obj.visual.name = machdata.presetname

			track_obj.params.add('vol', mixer_tracks[machnum].vol, 'float')
			track_obj.params.add('pan', mixer_tracks[machnum].pan, 'float')
			track_obj.params.add('enabled', int(not bool(mixer_tracks[machnum].mute)), 'bool')
			track_obj.params.add('solo', mixer_tracks[machnum].solo, 'bool')

			if machine.mach_id != 'NULL':
				for num, pattern in enumerate(machdata.patterns.data):
					if len(pattern.notes):
						patid = patids[num]
						nle_obj = track_obj.notelistindex__add(patid)
						nle_obj.visual.name = patid
						cvpj_notelist = nle_obj.notelist
						for n in pattern.notes: 
							cvpj_notelist.add_r(n['pos'], n['dur'], n['key']-60, n['vol'], None)

			c_fxdata = project_obj.effx.fxslots[machnum*2:machnum*2+2]
			add_caustic_fx(convproj_obj, track_obj, c_fxdata, 'machine'+str(machnum))

			track_obj.sends.add('master_delay', cvpj_trackid+'_send_delay', mixer_tracks[machnum].send_delay)
			track_obj.sends.add('master_reverb', cvpj_trackid+'_send_reverb', mixer_tracks[machnum].send_reverb)

			mixereq_plugid = 'machine'+str(machnum)+'_eq'
			plugin_obj = convproj_obj.plugin__add(mixereq_plugid, 'native', 'caustic', 'mixer_eq')
			plugin_obj.visual.name = 'Mixer EQ'
			plugin_obj.visual.color.set_float([0.67, 0.67, 0.67])
			plugin_obj.params.add('bass', mixer_tracks[machnum].eq_low, 'float')
			plugin_obj.params.add('mid', mixer_tracks[machnum].eq_mid, 'float')
			plugin_obj.params.add('high', mixer_tracks[machnum].eq_high, 'float')
			track_obj.plugslots.slots_mixer.append(mixereq_plugid)

			width_plugid = 'machine'+str(machnum)+'_width'
			plugin_obj = convproj_obj.plugin__add(width_plugid, 'universal', 'width', None)
			plugin_obj.visual.name = 'Width'
			plugin_obj.visual.color.set_float([0.66, 0.61, 0.76])
			plugin_obj.params.add('width', mixer_tracks[machnum].width, 'float')
			track_obj.plugslots.slots_mixer.append(width_plugid)
		
		for x in project_obj.seqn.parts:
			x['key'] = x['key']%100 + (x['key']//100)*16

			machdata = project_obj.machines[x['mach']].data

			patmeasures = machdata.patterns.data[x['key']].measures*16
			autodata = machdata.patterns.auto[x['key']]
			if patmeasures == 0: patmeasures = 16
			patid = patids[x['key']]

			placement_obj = cvpj_tracks[x['mach']].placements.add_notes_indexed()
			time_obj = placement_obj.time
			time_obj.set_posdur(float(x['pos']), float(x['dur']))
			time_obj.set_loop_data(0, 0, float(patmeasures/4))
			placement_obj.fromindex = patid

			#if autodata:
			#	cutpoints = xtramath.cutloop(x['pos'], x['dur'], 0, 0, patmeasures/4)
#
			#	for position, duration, loopstart, loopend in cutpoints:
			#		for autoid, sauto in autodata.items():
			#			autopl_obj = convproj_obj.automation.add_pl_points(['plugin', 'machine'+str(x['mach']+1), str(autoid)], 'float')
			#			autopl_obj.data.from_steps(sauto.data, sauto.smooth, 1)
			#			time_obj = autopl_obj.time
			#			time_obj.set_posdur(position, duration)

		bpm_auto_obj = convproj_obj.automation.create(['main', 'bpm'], 'float', True)
		for pos, val in project_obj.seqn.tempoauto: bpm_auto_obj.add_autopoint(pos, val, None)

		for machnum, machauto in enumerate(project_obj.seqn.auto_mach):
			for ctrlid, s_machauto in machauto.data.items():

				twopoints = [[float(x['pos']), float(x['val'])] for x in s_machauto]

				convproj_obj.automation.add_autopoints_twopoints(['plugin', 'machine'+str(machnum+1), str(ctrlid)], 'float', twopoints)

		for fxsetnum, machauto in enumerate(project_obj.seqn.auto_mixer):
			fxsetnum = fxsetnum*7
			for ctrlid, s_machauto in machauto.data.items():
				ctrl_s, ctrl_g = ctrlid%8, ctrlid//8
				autoloc = None
				if ctrl_g == 0: autoloc = ['track', 'MACH'+str(ctrl_s+1+fxsetnum), 'vol']
				elif ctrl_g in [1,2]: 
					basev = ctrlid-8
					autoloc = ['send', 'MACH'+str((basev//2)+1+fxsetnum)+('_send_reverb' if basev%2 else '_send_delay'), 'amount']
				elif ctrl_g == 3: autoloc = ['plugin', 'machine'+str(ctrl_s+1+fxsetnum)+'_eq', 'bass']
				elif ctrl_g == 4: autoloc = ['plugin', 'machine'+str(ctrl_s+1+fxsetnum)+'_eq', 'mid']
				elif ctrl_g == 5: autoloc = ['plugin', 'machine'+str(ctrl_s+1+fxsetnum)+'_eq', 'high']
				elif ctrl_g == 8: autoloc = ['track', 'MACH'+str(ctrl_s+1+fxsetnum), 'pan']
				elif ctrl_g == 9: autoloc = ['plugin', 'machine'+str(ctrl_s+1+fxsetnum)+'_width', 'width']

				if autoloc: 
					twopoints = [[float(x['pos']), float(x['val'])] for x in s_machauto]
					if ctrl_g == 8: 
						for x in twopoints: x[1] = (x[1]-0.5)*2
					convproj_obj.automation.add_autopoints_twopoints(autoloc, 'float', twopoints)

		for fxsetnum, machauto in enumerate(project_obj.seqn.auto_fx):
			fxsetnum = fxsetnum*7
			for ctrlid, s_machauto in machauto.data.items():
				autofx_num = (ctrlid//16)
				autofx_slot = (ctrlid//8)-(autofx_num*2)
				autofx_ctrl = ctrlid-(autofx_slot*8)-(autofx_num*16)
				cvpj_fx_autoid = 'machine'+str(autofx_num+1+(fxsetnum))+'_slot'+str(autofx_slot+1)

				twopoints = [[float(x['pos']), float(x['val'])] for x in s_machauto]

				if autofx_ctrl == 5: 
					for x in twopoints: x[1] = (x[1]*-1)-1
					convproj_obj.automation.add_autopoints_twopoints(['slot', cvpj_fx_autoid, 'enabled'], 'bool', twopoints)
				else: 
					convproj_obj.automation.add_autopoints_twopoints(['plugin', cvpj_fx_autoid, str(autofx_ctrl)], 'float', twopoints)

		master_fxchaindata = []

		add_caustic_fx(convproj_obj, convproj_obj.track_master, project_obj.mstr.fxslots, 'master_slot')

		master_controls_data = project_obj.mstr.controls.data

		for fxid in ['master_delay','master_reverb','master_eq','master_limiter']:

			plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'caustic', fxid)
			plugin_obj.visual.from_dset('caustic', 'plugin_master_fx', fxid, True)

			if fxid in ['master_delay','master_reverb']:
				return_obj = convproj_obj.track_master.fx__return__add(fxid)
				return_obj.visual.name = plugin_obj.visual.name
				return_obj.visual.color = plugin_obj.visual.color.copy()
				return_obj.plugslots.slots_audio.append(fxid)
			else:
				convproj_obj.track_master.plugslots.slots_audio.append(fxid)

			if fxid == 'master_delay': plugin_obj.fxdata_add(not bool(master_controls_data[40]), 1)
			if fxid == 'master_reverb': plugin_obj.fxdata_add(not bool(master_controls_data[41]), 1)
			if fxid == 'master_eq': plugin_obj.fxdata_add(not bool(master_controls_data[42]), 1)
			if fxid == 'master_limiter': plugin_obj.fxdata_add(not bool(master_controls_data[43]), 1)

			fldso = globalstore.dataset.get_obj('caustic', 'plugin_master_fx', fxid)
			if fldso:
				for param_id, dset_param in fldso.params.iter():
					outval = master_controls_data[int(param_id)] if int(param_id) in master_controls_data else None
					plugin_obj.dset_param__add(param_id, outval, dset_param)

		for ctrlid, s_machauto in project_obj.seqn.auto_master.data.items():

			twopoints = [[float(x['pos']), float(x['val'])] for x in s_machauto]

			autoloc = None
			if 1 <= ctrlid <= 9: autoloc = ['plugin', 'master_delay', str(ctrlid)]
			elif 16 <= ctrlid <= 25: autoloc = ['plugin', 'master_reverb', str(ctrlid)]
			elif 30 <= ctrlid <= 34: autoloc = ['plugin', 'master_eq', str(ctrlid)]
			elif 35 <= ctrlid <= 38: autoloc = ['plugin', 'master_limiter', str(ctrlid)]
			elif ctrlid == 39: autoloc = ['master', 'vol']
			elif ctrlid >= 64:
				autonum_calc = ctrlid - 64
				autofx_slot = (autonum_calc//8)
				autofx_ctrl = ctrlid-(autofx_slot*8)
				cvpj_fx_autoid = 'master_slot'+str(autofx_slot+1)

				if autofx_ctrl-64 == 5:
					for x in twopoints: x[1] = (x[1]*-1)-1
					autoloc = ['slot', cvpj_fx_autoid, 'enabled']
				else:  autoloc = ['plugin', cvpj_fx_autoid, str(autofx_ctrl-64)]

			if autoloc: convproj_obj.automation.add_autopoints_twopoints(autoloc, 'float', twopoints)

		convproj_obj.track_master.params.add('vol', master_controls_data[39], 'float')
		convproj_obj.track_master.visual.name = 'Master'
		convproj_obj.track_master.visual.color.set_float([0.52, 0.52, 0.52])
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.params.add('bpm', project_obj.tempo, 'float')
		convproj_obj.timesig = [project_obj.numerator, 4]

