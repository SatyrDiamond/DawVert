# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import shlex
import plugin_input
import json
from functions import data_values
from functions import xtramath

from objects import dv_dataset
from objects_file import audio_wav
from objects_proj import proj_famistudiotxt

dpcm_rate_arr = [4181.71,4709.93,5264.04,5593.04,6257.95,7046.35,7919.35,8363.42,9419.86,11186.1,12604.0,13982.6,16884.6,21306.8,24858.0,33143.9]

def add_envelope(plugin_obj, fst_Instrument, cvpj_name, fst_name):
	if fst_name in fst_Instrument.Envelopes:
		f_env_data = fst_Instrument.Envelopes[fst_name]
		envdata = {}
		if fst_name == 'FDSWave':
			envdata['values'] = f_env_data.Values
			envdata['loop'] = f_env_data.Loop
			envdata['release'] = f_env_data.Release
			plugin_obj.datavals.add('wave', envdata)
		elif fst_name == 'N163Wave':
			envdata['values'] = f_env_data.Values
			envdata['loop'] = f_env_data.Loop
			envdata['preset'] = fst_Instrument.N163WavePreset
			envdata['size'] = fst_Instrument.N163WaveSize
			envdata['pos'] = fst_Instrument.N163WavePos
			envdata['count'] = fst_Instrument.N163WaveCount
			plugin_obj.datavals.add('wave', envdata)

			waveids = []
			namco163_wave_chunks = data_values.list_chunks(envdata['values'], int(envdata['size']))
			for wavenum in range(len(namco163_wave_chunks)):
				wavedata = namco163_wave_chunks[wavenum]
				if len(wavedata) == int(envdata['size']):
					wave_obj = plugin_obj.wave_add(str(wavenum))
					wave_obj.set_all_range(wavedata, 0, 15)
					waveids.append(str(wavenum))
			wavetable_obj = plugin_obj.wavetable_add('N163')
			wavetable_obj.ids = waveids
			wavetable_obj.locs = None
			wavetable_obj.phase = envdata['loop']/((envdata['size']*envdata['count'])-1)

		else:
			envdata_values = f_env_data.Values
			envdata_loop = f_env_data.Loop
			envdata_release = f_env_data.Release
			plugin_obj.env_blocks_add(cvpj_name, envdata_values, 0.05, 15, envdata_loop, envdata_release)

def add_envelopes(plugin_obj, fst_Instrument):
	add_envelope(plugin_obj, fst_Instrument, 'vol', 'Volume')
	add_envelope(plugin_obj, fst_Instrument, 'duty', 'DutyCycle')
	add_envelope(plugin_obj, fst_Instrument, 'pitch', 'Pitch')

def create_inst(convproj_obj, WaveType, fst_Instrument, fxchannel_obj, fx_num):
	instname = fst_Instrument.Name

	cvpj_instid = WaveType+'-'+instname
	inst_obj = convproj_obj.add_instrument(cvpj_instid)
	inst_obj.fxrack_channel = fx_num
	inst_obj.params.add('vol', 0.2, 'float')

	if WaveType == 'Square1' or WaveType == 'Square2' or WaveType == 'Triangle' or WaveType == 'Noise':
		if WaveType == 'Square1' or WaveType == 'Square2': wavetype = 'square'
		if WaveType == 'Triangle': wavetype = 'triangle'
		if WaveType == 'Noise': wavetype = 'noise'
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
		osc_data = plugin_obj.osc_add()
		osc_data.shape = wavetype
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'VRC7FM':
		inst_obj.params.add('vol', 1, 'float')
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('fm', 'vrc7')
		add_envelopes(plugin_obj, fst_Instrument)
		plugin_obj.datavals.add('patch', fst_Instrument.Patch)
		plugin_obj.datavals.add('use_patch', bool(fst_Instrument.Patch))
		plugin_obj.datavals.add('regs', fst_Instrument.Regs)

	if WaveType == 'VRC6Square' or WaveType == 'VRC6Saw':
		if WaveType == 'VRC6Saw': wavetype = 'saw'
		if WaveType == 'VRC6Square': wavetype = 'square'
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
		osc_data = plugin_obj.osc_add()
		osc_data.shape = wavetype
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'FDS':
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('fds', None)
		add_envelopes(plugin_obj, fst_Instrument)
		add_envelope(plugin_obj, fst_Instrument, 'wave', 'FDSWave')

	if WaveType == 'N163':
		inst_obj.params.add('vol', 1, 'float')
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('namco163_famistudio', None)
		add_envelopes(plugin_obj, fst_Instrument)
		add_envelope(plugin_obj, fst_Instrument, 'wave', 'N163Wave')

	if WaveType == 'S5B':
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
		osc_data = plugin_obj.osc_add()
		osc_data.shape = 'square'
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'MMC5':
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
		osc_data = plugin_obj.osc_add()
		osc_data.shape = 'square'

	if WaveType == 'EPSMSquare':
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
		osc_data = plugin_obj.osc_add()
		osc_data.shape = 'square'
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'EPSMFM':
		instvolume = 0.7
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('fm', 'epsm')
		plugin_obj.datavals.add('regs', fst_Instrument.Regs)
		instpan = 0
		instpan += int(bool(fst_Instrument.Regs[1] & 0x80))*-1
		instpan += int(bool(fst_Instrument.Regs[1] & 0x40))
		inst_obj.params.add('pan', instpan, 'float')

	if WaveType == 'EPSM_Kick': 
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('epsm_rhythm', 'kick')
	if WaveType == 'EPSM_Snare': 
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('epsm_rhythm', 'snare')
	if WaveType == 'EPSM_Cymbal': 
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('epsm_rhythm', 'cymbal')
	if WaveType == 'EPSM_HiHat': 
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('epsm_rhythm', 'hihat')
	if WaveType == 'EPSM_Tom': 
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('epsm_rhythm', 'tom')
	if WaveType == 'EPSM_Rimshot': 
		plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('epsm_rhythm', 'rimshot')

	plugin_obj.role = 'synth'
	#print('DATA ------------' , fst_Instrument)
	#print('OUT ------------' , plugname, cvpj_plugdata)

	_, inst_color = dataset.object_get_name_color('chip', WaveType)

	inst_obj.visual.name = instname
	inst_obj.visual.color = inst_color

	if WaveType in ['EPSMFM', 'EPSMSquare']: inst_obj.datavals.add('middlenote', 12)

def create_dpcm_inst(DPCMMappings, DPCMSamples, fx_num, fst_instrument):
	global samplefolder
	global dpcm_rate_arr

	instname = fst_instrument.Name if fst_instrument != None else None
	cvpj_instid = 'DPCM-'+instname if instname != None else 'DPCM'

	inst_obj = convproj_obj.add_instrument(cvpj_instid)
	inst_obj.params.add('vol', 0.6, 'float')
	inst_obj.params.add('usemasterpitch', False, 'bool')
	_, inst_obj.visual.color = dataset.object_get_name_color('chip', 'DPCM')
	inst_obj.visual.name = 'DPCM'
	inst_obj.fxrack_channel = fx_num
	plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('sampler', 'multi')
	plugin_obj.role = 'synth'

	for key, dpcmmap in DPCMMappings.data.items():
		dpcm_pitch = int(dpcmmap['Pitch'])
		dpcm_sample = dpcmmap['Sample']

		if dpcm_sample in DPCMSamples:
			if instname: filename = samplefolder+'dpcm_'+instname+'_'+dpcm_sample+'_'+str(dpcm_pitch)+'.wav'
			else: filename = samplefolder+'dpcmg_'+dpcm_sample+'_'+str(dpcm_pitch)+'.wav'
			wavfile_obj = audio_wav.wav_main()
			wavfile_obj.set_freq(int(dpcm_rate_arr[dpcm_pitch]))
			wavfile_obj.data_add_data(8, 1, False, DPCMSamples[dpcm_sample].data_bytes)
			wavfile_obj.write(filename)
			correct_key = key+24
			sampleref_obj = convproj_obj.add_sampleref(filename, filename)
			regionparams = {}
			regionparams['name'] = dpcm_sample
			regionparams['middlenote'] = correct_key
			regionparams['sampleref'] = filename
			plugin_obj.regions.add(correct_key, correct_key, regionparams)

def NoteToMidi(keytext):
	l_key = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
	s_octave = (int(keytext[-1])-5)*12
	lenstr = len(keytext)
	if lenstr == 3: t_key = keytext[:-1]
	else: t_key = keytext[:-1]
	s_key = l_key.index(t_key)
	return s_key + s_octave

InstShapes = {'Square1': 'Square1', 
		'Square2': 'Square2', 
		'Triangle': 'Triangle', 
		'Noise': 'Noise', 

		'VRC6Square1': 'VRC6Square', 
		'VRC6Square2': 'VRC6Square', 
		'VRC6Saw': 'VRC6Saw', 

		'VRC7FM1': 'VRC7FM', 
		'VRC7FM2': 'VRC7FM', 
		'VRC7FM3': 'VRC7FM', 
		'VRC7FM4': 'VRC7FM', 
		'VRC7FM5': 'VRC7FM', 
		'VRC7FM6': 'VRC7FM', 

		'FDS': 'FDS', 

		'N163Wave1': 'N163', 
		'N163Wave2': 'N163', 
		'N163Wave3': 'N163', 
		'N163Wave4': 'N163', 

		'S5BSquare1': 'S5B', 
		'S5BSquare2': 'S5B', 
		'S5BSquare3': 'S5B',

		'MMC5Square1': 'MMC5', 
		'MMC5Square2': 'MMC5',

		'EPSMSquare1': 'EPSMSquare',
		'EPSMSquare2': 'EPSMSquare',
		'EPSMSquare3': 'EPSMSquare',

		'EPSMFM1': 'EPSMFM',
		'EPSMFM2': 'EPSMFM',
		'EPSMFM3': 'EPSMFM',
		'EPSMFM4': 'EPSMFM',
		'EPSMFM5': 'EPSMFM',
		'EPSMFM6': 'EPSMFM',

		'EPSMRythm1': 'EPSM_Kick',
		'EPSMRythm2': 'EPSM_Snare',
		'EPSMRythm3': 'EPSM_Cymbal',
		'EPSMRythm4': 'EPSM_HiHat',
		'EPSMRythm5': 'EPSM_Tom',
		'EPSMRythm6': 'EPSM_Rimshot',
		}


class input_famistudio(plugin_input.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'famistudio_txt'
	def gettype(self): return 'mi'
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'FamiStudio Text'
		dawinfo_obj.file_ext = 'txt'
		dawinfo_obj.auto_types = ['nopl_points']
		dawinfo_obj.track_lanes = True
		dawinfo_obj.fxtype = 'rack'
		dawinfo_obj.audio_filetypes = ['wav']
		dawinfo_obj.plugin_included = ['epsm_rhythm','fds','fm:epsm','fm:vrc7','namco163_famistudio','sampler:multi','universal:synth-osc']
	def supported_autodetect(self): return False
	def parse(self, i_convproj_obj, input_file, dv_config):
		global samplefolder
		global dataset
		global convproj_obj
		convproj_obj = i_convproj_obj

		convproj_obj.type = 'mi'
		convproj_obj.set_timings(4, True)

		dataset = dv_dataset.dataset('./data_dset/famistudio.dset')
		samplefolder = dv_config.path_samples_extracted

		project_obj = proj_famistudiotxt.famistudiotxt_project()
		project_obj.load_from_file(input_file)

		songnamelist = list(project_obj.Songs.keys())

		fst_currentsong = project_obj.Songs[songnamelist[dv_config.songnum-1]]

		PatternLengthList = [fst_currentsong.PatternLength for x in range(fst_currentsong.PatternSettings.Length)]
		for n, d in fst_currentsong.PatternCustomSettings.items(): PatternLengthList[n] = d.Length

		NoteLength = fst_currentsong.PatternSettings.NoteLength

		PointsPos = []
		PointsAdd = 0
		for length in PatternLengthList:
			PointsPos.append(PointsAdd)
			PointsAdd += length

		for channum, fst_channel in enumerate(fst_currentsong.Channels):
			playlistnum = str(channum+1)
			WaveType = InstShapes[fst_channel.Type] if fst_channel.Type in InstShapes else 'DPCM'
			used_insts = []
			for pattern_name, fs_pattern in fst_channel.Patterns.items():
				for x in fs_pattern.Notes:
					if x.Instrument != None and x.Instrument not in used_insts:
						used_insts.append(x.Instrument)
			fxchannel_obj = convproj_obj.add_fxchan(channum+1)

			if WaveType != 'DPCM':
				fxchannel_obj.visual.name, fxchannel_obj.visual.color = dataset.object_get_name_color('chip', WaveType)
				for inst in used_insts: 
					create_inst(convproj_obj, WaveType, project_obj.Instruments[inst], fxchannel_obj, channum+1)
			else: 
				create_dpcm_inst(project_obj.DPCMMappings, project_obj.DPCMSamples, channum+1, None)
				for inst in used_insts: create_dpcm_inst(project_obj.Instruments[inst].DPCMMappings, project_obj.DPCMSamples, channum, project_obj.Instruments[inst])
				fxchannel_obj.visual.name, fxchannel_obj.visual.color = dataset.object_get_name_color('chip', 'DPCM')

			playlist_obj = convproj_obj.add_playlist(channum, 1, True)
			playlist_obj.visual.name = fst_channel.Type
			playlist_obj.visual.color = [0.13, 0.15, 0.16]

			for patid, patdata in fst_channel.Patterns.items():
				nle_obj = convproj_obj.add_notelistindex(fst_channel.Type+'-'+patid)
				nle_obj.visual.name = patid+' ('+fst_channel.Type+')'
				nle_obj.visual.color = [0.13, 0.15, 0.16]

				for notedata in patdata.Notes:
					if notedata.Duration != None:
						t_duration = notedata.Duration/NoteLength
						t_position = notedata.Time/NoteLength
						if fst_channel.Type != 'DPCM':
							if notedata.Instrument:
								if notedata.Value not in ['Stop', None]:
									t_key = notedata.Value + 24
									if fst_channel.Type[0:6] == 'EPSMFM': t_key -= 12
									t_instrument = InstShapes[fst_channel.Type]+'-'+notedata.Instrument
									nle_obj.notelist.add_m(t_instrument, t_position, t_duration, t_key, 1, {})

									if notedata.SlideTarget:
										t_slidenote = notedata.SlideTarget + 24
										nle_obj.notelist.last_add_slide(0, t_duration, t_slidenote, None, {})
										autopoint_obj = nle_obj.notelist.last_add_auto('pitch')
										autopoint_obj = nle_obj.notelist.last_add_auto('pitch')
										autopoint_obj.pos = t_duration
										autopoint_obj.value = t_slidenote-t_key

									if notedata.Arpeggio:
										if notedata.Arpeggio in project_obj.Arpeggios:
											multikeys = project_obj.Arpeggios[notedata.Arpeggio].Values
											nle_obj.notelist.last_arpeggio(multikeys)

						else:
							if notedata.Instrument: 
								nle_obj.notelist.add_m('DPCM'+'-'+notedata.Instrument, t_position, t_duration, t_key, 1, {})
							else: 
								nle_obj.notelist.add_m('DPCM', t_position, t_duration, t_key, 1, {})

			for pattime, patid in fst_channel.Instances.items():
				cvpj_placement = playlist_obj.placements.add_notes_indexed()
				cvpj_placement.fromindex = fst_channel.Type+'-'+patid
				cvpj_placement.position = PointsPos[pattime]
				cvpj_placement.duration = PatternLengthList[pattime]

		convproj_obj.add_timesig_lengthbeat(fst_currentsong.PatternLength, fst_currentsong.PatternSettings.BeatLength)
		convproj_obj.patlenlist_to_timemarker(PatternLengthList, fst_currentsong.LoopPoint)

		if project_obj.Name: convproj_obj.metadata.name = project_obj.Name
		if project_obj.Author: convproj_obj.metadata.author = project_obj.Author

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.params.add('bpm', fst_currentsong.PatternSettings.bpm, 'float')