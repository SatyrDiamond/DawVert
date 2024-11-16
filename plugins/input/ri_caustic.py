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
		controls_data = caustic_fx_data.controls.data

		fx_pluginid = start_plugid+'_slot'+str(slotnum+1)

		if caustic_fx_data.fx_type not in [4294967295, -1]:
			fxtype = caustic_fxtype[caustic_fx_data.fx_type]
			plugin_obj = convproj_obj.plugin__add(fx_pluginid, 'native', 'caustic', fxtype)
			plugin_obj.role = 'fx'
			plugin_obj.fxdata_add(bool(not int(controls_data[5])), 1)
			plugin_obj.visual.from_dset('caustic', 'plugin_fx', fxtype, True)

			for param_id, dset_param in globalstore.dataset.get_params('caustic', 'plugin_fx', fxtype):
				if param_id != '5':
					outval = controls_data[int(param_id)] if int(param_id) in controls_data else None
					plugin_obj.dset_param__add(param_id, outval, dset_param)

			track_obj.plugslots.slots_audio.append(fx_pluginid)

def loopmode_cvpj(wavdata, sp_obj): 
	lm = wavdata['mode']
	sp_obj.end = wavdata['end']
	if lm in [0,1,2,3]: sp_obj.start = wavdata['start']
	if lm in [4,5]: sp_obj.start = 0
	sp_obj.trigger = 'normal' if lm == 0 else 'oneshot'

	if lm in [2,3,4,5]: 
		sp_obj.loop_active = True
		sp_obj.loop_start = wavdata['start']
		sp_obj.loop_end = wavdata['end']
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
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'caustic'
	def get_name(self): return 'Caustic 3'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['caustic']
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop']
		in_dict['audio_stretch'] = ['warp']
		in_dict['auto_types'] = ['pl_points', 'nopl_points']
		in_dict['plugin_included'] = ['native:caustic','universal:sampler:single','universal:sampler:multi']
		in_dict['fxchain_mixer'] = True
		in_dict['audio_filetypes'] = ['wav']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['projtype'] = 'ri'
	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects import audio_data
		from objects.file_proj import proj_caustic
		
		global dataset

		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.type = 'ri'
		convproj_obj.set_timings(1, True)

		globalstore.dataset.load('caustic', './data_main/dataset/caustic.dset')

		project_obj = proj_caustic.caustic_project()
		if not project_obj.load_from_file(input_file): exit()

		samplefolder = dv_config.path_samples_extracted

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

			# -------------------------------- PCMSynth --------------------------------
			if machine.mach_id == 'PCMS':
				middlenote = 0
				track_obj.params.add('usemasterpitch', True, 'bool')
				if len(machine.samples) == 1:
					singlewav = machine.samples[0]
					if singlewav[0]['key_lo'] == 24 and singlewav[0]['key_hi'] == 108: isMultiSampler = False
					else: isMultiSampler = True
				else: isMultiSampler = True

				if not isMultiSampler:
					region_data, wave_data = machine.samples[0]

					sampleref = machid + '_PCMSynth_0'
					wave_path = samplefolder+sampleref+'.wav'

					if region_data['samp_ch'] != 0: 
						audio_obj = audio_data.audio_obj()
						audio_obj.channels = region_data['samp_ch']
						audio_obj.rate = region_data['samp_hz']
						audio_obj.set_codec('int16')
						audio_obj.pcm_from_bytes(wave_data)
						if region_data['mode'] not in [0, 1]: audio_obj.loop = [region_data['start'], region_data['end']]
						audio_obj.to_file_wav(wave_path)

					plugin_obj, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler(pluginid, wave_path, None)
					loopmode_cvpj(region_data, sp_obj)
					sp_obj.point_value_type = "samples"

					middlenote += region_data['key_root']-60
				else:
					plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'sampler', 'multi')
					plugin_obj.role = 'synth'
					for samplecount, data in enumerate(machine.samples):
						region_data, wave_data = data
						loopdata = None
						sampleref = machid + '_PCMSynth_'+str(samplecount)
						wave_path = samplefolder+sampleref+'.wav'

						audio_obj = audio_data.audio_obj()
						audio_obj.channels = region_data['samp_ch']
						audio_obj.rate = region_data['samp_hz']
						audio_obj.set_codec('int16')
						audio_obj.pcm_from_bytes(wave_data)
						if region_data['mode'] not in [0, 1]: audio_obj.loop = [region_data['start'], region_data['end']]
						audio_obj.to_file_wav(wave_path)

						sampleref_obj = convproj_obj.sampleref__add(wave_path, wave_path, None)
						sp_obj = plugin_obj.sampleregion_add(region_data['key_lo']-60, region_data['key_hi']-60, region_data['key_root']-60, None)
						sp_obj.vol = region_data['volume']
						sp_obj.pan = (region_data['pan']-0.5)*2
						loopmode_cvpj(region_data, sp_obj)
						sp_obj.length = sp_obj.end
						sp_obj.sampleref = wave_path
						sp_obj.point_value_type = 'samples'

				if machine.samples:
					pcms_c = machine.controls.data

					middlenote += int(pcms_c[1]*12)
					middlenote += int(pcms_c[2])

					track_obj.params.add('pitch', pcms_c[3]/100, 'float')
					track_obj.datavals.add('middlenote', -middlenote)
					plugin_obj.env_asdr_add('vol', 0, pcms_c[5], 0, pcms_c[6], pcms_c[7], pcms_c[8], 1)

			# -------------------------------- BeatBox --------------------------------
			elif machine.mach_id == 'BBOX':
				plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'sampler', 'multi')
				plugin_obj.role = 'synth'
				track_obj.params.add('usemasterpitch', False, 'bool')
				track_obj.is_drum = True
				samplecount = 0
				for samplecount, bbox_sample in enumerate(machine.samples):
					region_data, wave_data = bbox_sample
					sampleref = machid + '_BeatBox_'+str(samplecount)
					wave_path = samplefolder+sampleref+'.wav'
					if region_data['chan'] != 0 and region_data['hz'] != 0: 
						audio_obj = audio_data.audio_obj()
						audio_obj.channels = region_data['chan']
						audio_obj.rate = region_data['hz']
						audio_obj.set_codec('int16')
						audio_obj.pcm_from_bytes(wave_data)
						audio_obj.to_file_wav(wave_path)

					midkey = samplecount-12

					sampleref_obj = convproj_obj.sampleref__add(wave_path, wave_path, None)
					sp_obj = plugin_obj.sampleregion_add(midkey, midkey, midkey, None)
					sp_obj.visual.name = region_data['name']
					sp_obj.start = 0
					sp_obj.end = region_data['len']
					sp_obj.trigger = 'oneshot'
					sp_obj.sampleref = wave_path
					sp_obj.point_value_type = "samples"

			elif machine.mach_id == 'NULL':
				pass
			else:
				plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'caustic', machine.mach_id)
				plugin_obj.role = 'synth'

				fldso = globalstore.dataset.get_obj('caustic', 'plugin_inst', machine.mach_id)
				if fldso:
					for param_id, dset_param in fldso.params.iter():
						outval = machine.controls.data[int(param_id)] if int(param_id) in machine.controls.data else None
						plugin_obj.dset_param__add(param_id, outval, dset_param)

				if machine.mach_id == 'VCDR':
					for samplenum, sd in enumerate(machine.samples):
						sampleinfo, sample_data = sd
						if sample_data:
							sampleref = machid + '_Vocoder_'+str(samplenum)
							wave_path = samplefolder+sampleref+'.wav'
							audio_obj = audio_data.audio_obj()

							audio_obj.channels = 1
							audio_obj.rate = sampleinfo['hz']
							audio_obj.set_codec('int16')
							audio_obj.pcm_from_bytes(sample_data)
							audio_obj.to_file_wav(wave_path)

							plugin_obj, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler(pluginid, wave_path, None)
							sp_obj.point_value_type = "samples"

				if machine.customwaveform1: 
					wave_obj = plugin_obj.wave_add('customwaveform1')
					wave_obj.set_all_range(machine.customwaveform1, -157, 157)
					
				if machine.customwaveform2: 
					wave_obj = plugin_obj.wave_add('customwaveform2')
					wave_obj.set_all_range(machine.customwaveform2, -157, 157)

			track_obj.params.add('vol', mixer_tracks[machnum].vol, 'float')
			track_obj.params.add('pan', mixer_tracks[machnum].pan, 'float')
			track_obj.params.add('enabled', int(not bool(mixer_tracks[machnum].mute)), 'bool')
			track_obj.params.add('solo', mixer_tracks[machnum].solo, 'bool')

			if machine.mach_id != 'NULL':
				for num, pattern in enumerate(machine.patterns.data):
					patid = patids[num]
					nle_obj = track_obj.notelistindex__add(patid)
					nle_obj.visual.name = patid
					for n in pattern.notes: 
						nle_obj.notelist.add_r(n['pos'], n['dur'], n['key']-60, n['vol'], None)

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

			patmeasures = project_obj.machines[x['mach']].patterns.data[x['key']].measures*16
			autodata = project_obj.machines[x['mach']].patterns.auto[x['key']]
			if patmeasures == 0: patmeasures = 16
			patid = patids[x['key']]

			placement_obj = cvpj_tracks[x['mach']].placements.add_notes_indexed()
			placement_obj.time.set_posdur(x['pos'], x['dur'])
			placement_obj.time.set_loop_data(0, 0, patmeasures/4)
			placement_obj.fromindex = patid

			if autodata:
				cutpoints = xtramath.cutloop(x['pos'], x['dur'], 0, 0, patmeasures/4)

				for position, duration, loopstart, loopend in cutpoints:
					for autoid, sauto in autodata.items():
						autopl_obj = convproj_obj.automation.add_pl_points(['plugin', 'machine'+str(x['mach']+1), str(autoid)], 'float')
						autopl_obj.time.set_posdur(position, duration)
						autopl_obj.data.from_steps(sauto.data, sauto.smooth, 1)

		for pos, val in project_obj.seqn.tempoauto: 
			convproj_obj.automation.add_autopoint(['main', 'bpm'], 'float', pos, val, 'normal')

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

