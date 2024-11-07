# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import shlex
import plugins
import json
from functions import data_values
from functions import xtramath

from objects import globalstore

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
			wave_obj = plugin_obj.wave_add('n163')
			wave_obj.set_all_range(f_env_data.Values, 0, 15)
			wavetable_obj = plugin_obj.wavetable_add('main')
			wt_src_obj = wavetable_obj.add_source()
			wt_src_obj.type = 'retro'
			wt_src_obj.retro_id = 'n163'
			wt_src_obj.retro_size = fst_Instrument.N163WaveSize
			wt_src_obj.retro_count = fst_Instrument.N163WaveCount
			wt_src_obj.retro_pos = fst_Instrument.N163WavePos
			wt_src_obj.retro_loop = f_env_data.Loop
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
	inst_obj = convproj_obj.instrument__add(cvpj_instid)
	inst_obj.fxrack_channel = fx_num
	inst_obj.params.add('vol', 0.2, 'float')

	if WaveType == 'Square1' or WaveType == 'Square2' or WaveType == 'Triangle' or WaveType == 'Noise':
		if WaveType == 'Square1' or WaveType == 'Square2': wavetype = 'square'
		if WaveType == 'Triangle': wavetype = 'triangle'
		if WaveType == 'Noise': wavetype = 'noise'
		plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
		osc_data = plugin_obj.osc_add()
		osc_data.prop.shape = wavetype
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'VRC7FM':
		inst_obj.params.add('vol', 1, 'float')
		opl2_obj = fst_Instrument.FM.to_opl2()
		plugin_obj, inst_obj.pluginid = opl2_obj.to_cvpj_genid(convproj_obj)
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'VRC6Square' or WaveType == 'VRC6Saw':
		if WaveType == 'VRC6Saw': wavetype = 'saw'
		if WaveType == 'VRC6Square': wavetype = 'square'
		plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
		osc_data = plugin_obj.osc_add()
		osc_data.prop.shape = wavetype
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'FDS':
		plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('chip', 'fds', None)
		add_envelopes(plugin_obj, fst_Instrument)
		add_envelope(plugin_obj, fst_Instrument, 'wave', 'FDSWave')

	if WaveType == 'N163':
		inst_obj.params.add('vol', 1, 'float')
		plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('native', 'namco163_famistudio', None)
		osc_obj = plugin_obj.osc_add()
		osc_obj.prop.type = 'wavetable'
		osc_obj.prop.nameid = 'main'
		add_envelopes(plugin_obj, fst_Instrument)
		add_envelope(plugin_obj, fst_Instrument, 'wave', 'N163Wave')

	if WaveType == 'S5B':
		plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
		osc_data = plugin_obj.osc_add()
		osc_data.prop.shape = 'square'
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'MMC5':
		plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
		osc_data = plugin_obj.osc_add()
		osc_data.prop.shape = 'square'

	if WaveType == 'EPSMSquare':
		plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
		osc_data = plugin_obj.osc_add()
		osc_data.prop.shape = 'square'
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'EPSMFM':
		inst_obj.params.add('vol', 0.6, 'float')
		instvolume = 0.7
		opn2_obj = fst_Instrument.FM.to_opn2()
		plugin_obj, inst_obj.pluginid = opn2_obj.to_cvpj_genid(convproj_obj)
		instpan = 0
		instpan += int(bool(fst_Instrument.Regs[1] & 0x80))*-1
		instpan += int(bool(fst_Instrument.Regs[1] & 0x40))
		inst_obj.params.add('pan', instpan, 'float')

	if WaveType == 'EPSM_Kick': plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('chip', 'epsm_rhythm', 'kick')
	if WaveType == 'EPSM_Snare': plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('chip', 'epsm_rhythm', 'snare')
	if WaveType == 'EPSM_Cymbal': plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('chip', 'epsm_rhythm', 'cymbal')
	if WaveType == 'EPSM_HiHat': plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('chip', 'epsm_rhythm', 'hihat')
	if WaveType == 'EPSM_Tom': plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('chip', 'epsm_rhythm', 'tom')
	if WaveType == 'EPSM_Rimshot': plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('chip', 'epsm_rhythm', 'rimshot')

	plugin_obj.role = 'synth'

	inst_obj.visual.name = instname
	inst_obj.visual.from_dset('famistudio', 'chip', WaveType, False)

	if WaveType in ['VRC7FM']: inst_obj.datavals.add('middlenote', 12)

def create_dpcm_inst(DPCMMappings, DPCMSamples, fx_num, fst_instrument):
	from objects import audio_data
	global samplefolder
	global dpcm_rate_arr

	instname = fst_instrument.Name if fst_instrument != None else None
	cvpj_instid = 'DPCM-'+instname if instname != None else 'DPCM'

	inst_obj = convproj_obj.instrument__add(cvpj_instid)
	inst_obj.params.add('vol', 0.6, 'float')
	inst_obj.params.add('usemasterpitch', False, 'bool')
	inst_obj.visual.name = 'DPCM'
	inst_obj.visual.from_dset('famistudio', 'chip', 'DPCM', False)
	inst_obj.fxrack_channel = fx_num
	inst_obj.is_drum = True
	plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'multi')
	plugin_obj.role = 'synth'

	for key, dpcmmap in DPCMMappings.data.items():
		dpcm_pitch = int(dpcmmap['Pitch'])
		dpcm_sample = dpcmmap['Sample']

		if dpcm_sample in DPCMSamples:
			if instname: filename = samplefolder+'dpcm_'+instname+'_'+dpcm_sample+'_'+str(dpcm_pitch)+'.wav'
			else: filename = samplefolder+'dpcmg_'+dpcm_sample+'_'+str(dpcm_pitch)+'.wav'
			audio_obj = audio_data.audio_obj()
			audio_obj.decode_from_codec('dpcm', DPCMSamples[dpcm_sample].data_bytes)
			audio_obj.rate = dpcm_rate_arr[dpcm_pitch]
			audio_obj.to_file_wav(filename)
			correct_key = key+24
			sampleref_obj = convproj_obj.sampleref__add(filename, filename, None)
			sp_obj = plugin_obj.sampleregion_add(correct_key, correct_key, correct_key, None)
			sp_obj.visual.name = dpcm_sample
			sp_obj.sampleref = filename

def NoteToMidi(keytext):
	l_key = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
	s_octave = (int(keytext[-1])-5)*12
	lenstr = len(keytext)
	t_key = keytext[:-1]
	s_key = l_key.index(t_key)
	return s_key + s_octave

def get_instshape(InstShape):
	if InstShape == 'Square1': return 'Square1'
	elif InstShape == 'Square2': return 'Square2'
	elif InstShape == 'Triangle': return 'Triangle'
	elif InstShape == 'Noise': return 'Noise'
	elif InstShape.startswith('VRC6Saw'): return 'VRC6Saw'
	elif InstShape.startswith('VRC6Square'): return 'VRC6Square'
	elif InstShape.startswith('VRC7FM'): return 'VRC7FM'
	elif InstShape.startswith('N163Wave'): return 'N163'
	elif InstShape.startswith('S5BSquare'): return 'S5B'
	elif InstShape.startswith('MMC5Square'): return 'MMC5'
	elif InstShape.startswith('EPSMSquare'): return 'EPSMSquare'
	elif InstShape.startswith('EPSMFM'): return 'EPSMFM'
	elif InstShape == 'EPSMRythm1': return 'EPSM_Kick'
	elif InstShape == 'EPSMRythm2': return 'EPSM_Snare'
	elif InstShape == 'EPSMRythm3': return 'EPSM_Cymbal'
	elif InstShape == 'EPSMRythm4': return 'EPSM_HiHat'
	elif InstShape == 'EPSMRythm5': return 'EPSM_Tom'
	elif InstShape == 'EPSMRythm6': return 'EPSM_Rimshot'
	else: return 'DPCM'

def make_auto(convproj_obj, fs_notes, NoteLength, timemul, patpos, patdur, channum):
	vol_auto = []
	for notedata in fs_notes:
		if notedata.Volume:
			notepos = notedata.Time*timemul/NoteLength
			#print(notepos, notedata.Volume, notedata.VolumeSlideTarget)
			vol_auto.append([notepos, notedata.Volume, notedata.VolumeSlideTarget])

	if vol_auto:
		autopl_obj = convproj_obj.automation.add_pl_points(['fxmixer', str(channum), 'vol'], 'float')
		autopl_obj.time.set_posdur(patpos, patdur)

		prev_slidetarg = None
		for c_pos, c_val, slitarget in vol_auto:

			if prev_slidetarg != None:
				autopoint_obj = autopl_obj.data.add_point()
				autopoint_obj.pos = c_pos
				autopoint_obj.value = prev_slidetarg/15

			autopoint_obj = autopl_obj.data.add_point()
			autopoint_obj.pos = c_pos
			autopoint_obj.value = c_val/15
			autopoint_obj.type = 'instant'

			prev_slidetarg = slitarget

def parse_notes(cvpj_notelist, fs_notes, chiptype, NoteLength, arpeggios):
	for notedata in fs_notes:
		if notedata.Duration != None:
			t_duration = notedata.Duration/NoteLength
			t_position = notedata.Time/NoteLength
			if chiptype != 'DPCM':
				if notedata.Instrument:
					if notedata.Value not in ['Stop', None]:
						t_key = notedata.Value + 24
						if chiptype[0:6] == 'EPSMFM': t_key -= 12
						t_instrument = get_instshape(chiptype)+'-'+notedata.Instrument
						cvpj_notelist.add_m(t_instrument, t_position, t_duration, t_key, 1, {})

						if notedata.SlideTarget:
							t_slidenote = notedata.SlideTarget + 24
							cvpj_notelist.last_add_slide(0, t_duration, t_slidenote, None, {})
							autopoint_obj = cvpj_notelist.last_add_auto('pitch')
							autopoint_obj = cvpj_notelist.last_add_auto('pitch')
							autopoint_obj.pos = t_duration
							autopoint_obj.value = t_slidenote-t_key

						if notedata.Arpeggio:
							if notedata.Arpeggio in arpeggios:
								multikeys = arpeggios[notedata.Arpeggio].Values
								multikeys_r = []
								[multikeys_r.append(x) for x in multikeys if x not in multikeys_r]
								cvpj_notelist.last_arpeggio(multikeys_r)

			else:
				t_key = notedata.Value + 24
				if notedata.Instrument: 
					cvpj_notelist.add_m('DPCM'+'-'+notedata.Instrument, t_position, t_duration, t_key, 1, {})
				else: 
					cvpj_notelist.add_m('DPCM', t_position, t_duration, t_key, 1, {})


class input_famistudio(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'famistudio_txt'
	def get_name(self): return 'FamiStudio Text'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['txt']
		in_dict['file_ext_detect'] = False
		in_dict['auto_types'] = ['nopl_points', 'pl_points']
		in_dict['track_lanes'] = True
		in_dict['audio_filetypes'] = ['wav']
		in_dict['plugin_included'] = ['chip:epsm_rhythm','chip:fds','chip:fm:epsm','chip:fm:vrc7','chip:namco163_famistudio','universal:sampler:multi','universal:synth-osc']
		in_dict['fxtype'] = 'rack'
		in_dict['projtype'] = 'mi'
	def supported_autodetect(self): return False
	def parse(self, i_convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_famistudiotxt
		
		global samplefolder
		global convproj_obj
		convproj_obj = i_convproj_obj

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'mi'
		convproj_obj.set_timings(4, True)

		globalstore.dataset.load('famistudio', './data_main/dataset/famistudio.dset')
		samplefolder = dv_config.path_samples_extracted

		project_obj = proj_famistudiotxt.famistudiotxt_project()
		if not project_obj.load_from_file(input_file): exit()

		songnamelist = list(project_obj.Songs.keys())

		fst_currentsong = project_obj.Songs[songnamelist[dv_config.songnum-1]]

		PatternLengthList = [fst_currentsong.PatternLength for x in range(fst_currentsong.PatternSettings.Length)]
		BPMList = [fst_currentsong.PatternSettings.bpm for x in range(fst_currentsong.PatternSettings.Length)]
		BPMNoteMul = [1 for x in range(fst_currentsong.PatternSettings.Length)]
		for n, d in fst_currentsong.PatternCustomSettings.items(): PatternLengthList[n] = d.Length
		for n, d in fst_currentsong.PatternCustomSettings.items(): 
			if d.bpm: 
				BPMList[n] = d.bpm
				BPMNoteMul[n] = d.bpm/fst_currentsong.PatternSettings.bpm

		BPMDiff = [n for n, x in enumerate(BPMNoteMul) if x != 1]

		NoteLength = fst_currentsong.PatternSettings.NoteLength

		PointsPos = []
		PointsAdd = 0
		for length in PatternLengthList:
			PointsPos.append(PointsAdd)
			PointsAdd += length

		prevtempo = fst_currentsong.PatternSettings.bpm
		for n, p in enumerate(PatternLengthList):
			cur_tempo = BPMList[n]
			convproj_obj.automation.add_autopoint(['main', 'bpm'], 'float', PointsPos[n], BPMList[n]*(fst_currentsong.PatternSettings.BeatLength/4), 'instant')
			prevtempo = cur_tempo

		for channum, fst_channel in enumerate(fst_currentsong.Channels):
			fxchan = channum+1
			playlistnum = str(fxchan)
			WaveType = get_instshape(fst_channel.Type)
			used_insts = []
			for pattern_name, fs_pattern in fst_channel.Patterns.items():
				for x in fs_pattern.Notes:
					if x.Instrument != None and x.Instrument not in used_insts:
						used_insts.append(x.Instrument)
			fxchannel_obj = convproj_obj.fx__chan__add(fxchan)

			if WaveType != 'DPCM':
				fxchannel_obj.visual.from_dset('famistudio', 'chip', WaveType, True)
				for inst in used_insts: 
					create_inst(convproj_obj, WaveType, project_obj.Instruments[inst], fxchannel_obj, fxchan)
			else: 
				create_dpcm_inst(project_obj.DPCMMappings, project_obj.DPCMSamples, fxchan, None)
				for inst in used_insts: create_dpcm_inst(project_obj.Instruments[inst].DPCMMappings, project_obj.DPCMSamples, channum, project_obj.Instruments[inst])
				fxchannel_obj.visual.from_dset('famistudio', 'chip', 'DPCM', True)

			playlist_obj = convproj_obj.playlist__add(channum, 1, True)
			playlist_obj.visual.name = fst_channel.Type
			playlist_obj.visual.color.set_float([0.13, 0.15, 0.16])

			modpatbpm = {}
			for t, i in fst_channel.Instances.items():
				if i not in modpatbpm: modpatbpm[i] = []
				if BPMList[t] != fst_currentsong.PatternSettings.bpm: modpatbpm[i].append(BPMList[t])

			for patid, patdata in fst_channel.Patterns.items():
				cvpj_patid = fst_channel.Type+'-'+patid+'-'+str(fst_currentsong.PatternSettings.bpm)
				nle_obj = convproj_obj.notelistindex__add(cvpj_patid)
				nle_obj.visual.name = patid+' ('+fst_channel.Type+')'
				nle_obj.visual.color.set_float([0.13, 0.15, 0.16])
				parse_notes(nle_obj.notelist, patdata.Notes, fst_channel.Type, NoteLength, project_obj.Arpeggios)

				if patid in modpatbpm:
					pattemps = modpatbpm[patid]
					for pattemp in pattemps:
						notemul = fst_currentsong.PatternSettings.bpm/pattemp
						cvpj_patid = fst_channel.Type+'-'+patid+'-'+str(pattemp)
						nle_obj = convproj_obj.notelistindex__add(cvpj_patid)
						nle_obj.visual.name = patid+' ('+fst_channel.Type+')'
						nle_obj.visual.color.set_float([0.13, 0.15, 0.16])
						parse_notes(nle_obj.notelist, patdata.Notes, fst_channel.Type, NoteLength*notemul, project_obj.Arpeggios)

			for pattime, patid in fst_channel.Instances.items():
				cvpj_placement = playlist_obj.placements.add_notes_indexed()
				cvpj_placement.fromindex = fst_channel.Type+'-'+patid+'-'+str(BPMList[pattime])
				cvpj_placement.time.set_posdur(PointsPos[pattime], PatternLengthList[pattime])

				if patid in fst_channel.Patterns:
					make_auto(convproj_obj, fst_channel.Patterns[patid].Notes, NoteLength, BPMNoteMul[pattime], cvpj_placement.time.position, cvpj_placement.time.duration, fxchan)

		convproj_obj.add_timesig_lengthbeat(fst_currentsong.PatternLength, fst_currentsong.PatternSettings.BeatLength)
		convproj_obj.timemarker__from_patlenlist(PatternLengthList, fst_currentsong.LoopPoint)

		if project_obj.Name: convproj_obj.metadata.name = project_obj.Name
		if project_obj.Author: convproj_obj.metadata.author = project_obj.Author

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.params.add('bpm', fst_currentsong.PatternSettings.bpm, 'float')