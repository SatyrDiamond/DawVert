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

def create_inst(vol, convproj_obj, WaveType, fst_Instrument, fxchannel_obj, fx_num):
	instname = fst_Instrument.Name

	cvpj_instid = WaveType+'-'+instname
	inst_obj = convproj_obj.instrument__add(cvpj_instid)
	inst_obj.fxrack_channel = fx_num
	inst_obj.params.add('vol', 0.2*vol, 'float')

	synthid = None

	if WaveType == 'Square1' or WaveType == 'Square2' or WaveType == 'Triangle' or WaveType == 'Noise':
		plugin_obj, synthid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
		if WaveType == 'Square1' or WaveType == 'Square2':
			wavetype = 'square'
			plugin_obj.midi_fallback__add_inst(80)
		if WaveType == 'Triangle':
			wavetype = 'triangle'
			plugin_obj.midi_fallback__add_inst(95)
		if WaveType == 'Noise':
			wavetype = 'noise'
		osc_data = plugin_obj.osc_add()
		osc_data.prop.shape = wavetype
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'VRC7FM':
		inst_obj.params.add('vol', 1, 'float')
		opl2_obj = fst_Instrument.FM.to_opl2()
		plugin_obj, synthid = opl2_obj.to_cvpj_genid(convproj_obj)
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'VRC6Square' or WaveType == 'VRC6Saw':
		plugin_obj, synthid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
		if WaveType == 'VRC6Saw':
			plugin_obj.midi_fallback__add_inst(81)
			wavetype = 'saw'
		if WaveType == 'VRC6Square':
			wavetype = 'square'
			plugin_obj.midi_fallback__add_inst(80)
		osc_data = plugin_obj.osc_add()
		osc_data.prop.shape = wavetype
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'FDS':
		plugin_obj, synthid = convproj_obj.plugin__add__genid('chip', 'fds', None)
		add_envelopes(plugin_obj, fst_Instrument)
		add_envelope(plugin_obj, fst_Instrument, 'wave', 'FDSWave')

	if WaveType == 'N163':
		inst_obj.params.add('vol', 1, 'float')
		plugin_obj, synthid = convproj_obj.plugin__add__genid('native', 'namco163_famistudio', None)
		osc_obj = plugin_obj.osc_add()
		osc_obj.prop.type = 'wavetable'
		osc_obj.prop.nameid = 'main'
		add_envelopes(plugin_obj, fst_Instrument)
		add_envelope(plugin_obj, fst_Instrument, 'wave', 'N163Wave')

	if WaveType == 'S5B':
		plugin_obj, synthid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
		plugin_obj.midi_fallback__add_inst(80)
		osc_data = plugin_obj.osc_add()
		osc_data.prop.shape = 'square'
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'MMC5':
		plugin_obj, synthid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
		plugin_obj.midi_fallback__add_inst(80)
		osc_data = plugin_obj.osc_add()
		osc_data.prop.shape = 'square'

	if WaveType == 'EPSMSquare':
		plugin_obj, synthid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
		plugin_obj.midi_fallback__add_inst(80)
		osc_data = plugin_obj.osc_add()
		osc_data.prop.shape = 'square'
		add_envelopes(plugin_obj, fst_Instrument)

	if WaveType == 'EPSMFM':
		inst_obj.params.add('vol', 0.6, 'float')
		opn2_obj = fst_Instrument.FM.to_opn2()
		plugin_obj, synthid = opn2_obj.to_cvpj_genid(convproj_obj)
		instpan = 0
		instpan += int(bool(fst_Instrument.Regs[1] & 0x80))*-1
		instpan += int(bool(fst_Instrument.Regs[1] & 0x40))
		inst_obj.params.add('pan', instpan, 'float')

	if WaveType == 'EPSM_Kick': plugin_obj, synthid = convproj_obj.plugin__add__genid('chip', 'epsm_rhythm', 'kick')
	if WaveType == 'EPSM_Snare': plugin_obj, synthid = convproj_obj.plugin__add__genid('chip', 'epsm_rhythm', 'snare')
	if WaveType == 'EPSM_Cymbal': plugin_obj, synthid = convproj_obj.plugin__add__genid('chip', 'epsm_rhythm', 'cymbal')
	if WaveType == 'EPSM_HiHat': plugin_obj, synthid = convproj_obj.plugin__add__genid('chip', 'epsm_rhythm', 'hihat')
	if WaveType == 'EPSM_Tom': plugin_obj, synthid = convproj_obj.plugin__add__genid('chip', 'epsm_rhythm', 'tom')
	if WaveType == 'EPSM_Rimshot': plugin_obj, synthid = convproj_obj.plugin__add__genid('chip', 'epsm_rhythm', 'rimshot')

	plugin_obj.role = 'synth'

	if synthid: inst_obj.plugslots.set_synth(synthid)

	inst_obj.visual.name = instname
	inst_obj.visual.from_dset('famistudio', 'chip', WaveType, False)
	if fst_Instrument.Color: inst_obj.visual.color.set_hex(fst_Instrument.Color)

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
	plugin_obj, synthid = convproj_obj.plugin__add__genid('universal', 'sampler', 'drums')
	plugin_obj.role = 'synth'

	inst_obj.plugslots.set_synth(synthid)

	for key, dpcmmap in DPCMMappings.data.items():
		dpcm_pitch = int(dpcmmap['Pitch'])
		dpcm_sample = dpcmmap['Sample']

		if dpcm_sample in DPCMSamples:
			if instname: filename = samplefolder+'dpcm_'+instname+'_'+dpcm_sample+'_'+str(dpcm_pitch)+'.wav'
			else: filename = samplefolder+'dpcmg_'+dpcm_sample+'_'+str(dpcm_pitch)+'.wav'
			sampleref_obj = convproj_obj.sampleref__add(filename, filename, None)
			audio_obj = audio_data.audio_obj()
			audio_obj.decode_from_codec('dpcm', DPCMSamples[dpcm_sample].data_bytes)
			audio_obj.rate = dpcm_rate_arr[dpcm_pitch]
			audio_obj.to_file_wav(filename)
			
			sampleref_obj.set_fileformat('wav')
			audio_obj.to_sampleref_obj(sampleref_obj)

			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = key+24
			drumpad_obj.visual.name = dpcm_sample

			layer_obj.samplepartid = 'drum_%i' % key
			sp_obj = plugin_obj.samplepart_add(layer_obj.samplepartid)
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

def make_auto(convproj_obj, fs_pattern, NoteLength, timemul, patpos, patdur, channum):
	fs_notes = fs_pattern.Notes
	vol_auto = []
	for notedata in fs_notes:
		if notedata.Volume:
			notepos = notedata.Time*timemul/NoteLength
			vol_auto.append([notepos, notedata.Volume, notedata.VolumeSlideTarget])

	if vol_auto:
		autopl_obj = convproj_obj.automation.add_pl_points(['fxmixer', str(channum), 'vol'], 'float')
		time_obj = autopl_obj.time
		time_obj.set_posdur(patpos, patdur)
		if fs_pattern.Color: autopl_obj.visual.color.set_hex(fs_pattern.Color)

		autopoints_obj = autopl_obj.data

		prev_slidetarg = None
		for c_pos, c_val, slitarget in vol_auto:
			if prev_slidetarg != None:
				autopoints_obj.points__add_normal(c_pos, prev_slidetarg/15, 0, None)
			autopoints_obj.points__add_instant(c_pos, c_val/15)
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
						cvpj_notelist.add_m(t_instrument, t_position, t_duration, t_key, 1, None)

						if notedata.SlideTarget:
							t_slidenote = notedata.SlideTarget + 24
							cvpj_notelist.last_add_slide(0, t_duration, t_slidenote, 1, {})
							cvpj_notelist.last_add_auto('pitch', 0, 0)
							cvpj_notelist.last_add_auto('pitch', t_duration, t_slidenote-t_key)

						if notedata.Arpeggio:
							if notedata.Arpeggio in arpeggios:
								multikeys = arpeggios[notedata.Arpeggio].Values
								multikeys_r = []
								[multikeys_r.append(x) for x in multikeys if x not in multikeys_r]
								cvpj_notelist.last_arpeggio(multikeys_r)

			else:
				t_key = notedata.Value + 24
				if notedata.Instrument: 
					cvpj_notelist.add_m('DPCM'+'-'+notedata.Instrument, t_position, t_duration, t_key, 1, None)
				else: 
					cvpj_notelist.add_m('DPCM', t_position, t_duration, t_key, 1, None)
	cvpj_notelist.only_one()

class input_famistudio(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'famistudio_txt'
	
	def get_name(self):
		return 'FamiStudio Text'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['chip:epsm_rhythm','chip:fds','chip:fm:epsm','chip:fm:vrc7','chip:namco163_famistudio','universal:sampler:multi','universal:synth-osc']
		in_dict['projtype'] = 'mi'
		
	def parse(self, i_convproj_obj, dawvert_intent):
		from objects.file_proj import famistudiotxt as proj_famistudiotxt
		
		global samplefolder
		global convproj_obj
		convproj_obj = i_convproj_obj

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'mi'

		traits_obj = convproj_obj.traits
		traits_obj.audio_filetypes = ['wav']
		traits_obj.auto_types = ['nopl_points', 'pl_points']

		convproj_obj.set_timings(4, True)

		globalstore.dataset.load('famistudio', './data_main/dataset/famistudio.dset')
		samplefolder = dawvert_intent.path_samples['extracted']

		defualt_pattern_color = None
		def_ds_obj = globalstore.dataset.get_obj('famistudio', 'defualt', 'pattern')
		if def_ds_obj: defualt_pattern_color = def_ds_obj.visual.color

		defualt_track_color = None
		def_ds_obj = globalstore.dataset.get_obj('famistudio', 'defualt', 'track')
		if def_ds_obj: defualt_track_color = def_ds_obj.visual.color

		project_obj = proj_famistudiotxt.famistudiotxt_project()

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		songnamelist = list(project_obj.Songs.keys())

		fst_currentsong = project_obj.Songs[songnamelist[dawvert_intent.songnum]]

		if fst_currentsong.Color: convproj_obj.track_master.visual.color.set_hex(fst_currentsong.Color)
		if fst_currentsong.Name: convproj_obj.metadata.name = fst_currentsong.Name

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

			TrebleDb = 0
			TrebleRolloffHz = -1

			if WaveType != 'DPCM':
				if not fxchannel_obj.visual.from_dset('famistudio', 'chip', WaveType, True):
					fxchannel_obj.visual.name = WaveType

				outvol = 0
				if WaveType in ['Square1','Square2','Triangle','Noise']:
					outvol = project_obj.VolumeDb
					TrebleDb = project_obj.TrebleDb
					TrebleRolloffHz = project_obj.TrebleRolloffHz
				if WaveType == 'VRC7FM': 
					outvol = project_obj.VRC7VolumeDb
					TrebleDb = project_obj.VRC7TrebleDb
					TrebleRolloffHz = project_obj.VRC7TrebleRolloffHz
				if WaveType in ['VRC6Square','VRC6Saw']:
					outvol = project_obj.VRC6VolumeDb
					TrebleDb = project_obj.VRC6TrebleDb
					TrebleRolloffHz = project_obj.VRC6TrebleRolloffHz
				if WaveType == 'FDS':
					outvol = project_obj.FDSVolumeDb
					TrebleDb = project_obj.FDSTrebleDb
					TrebleRolloffHz = project_obj.FDSTrebleRolloffHz
				if WaveType == 'N163':
					outvol = project_obj.N163VolumeDb
					TrebleDb = project_obj.N163TrebleDb
					TrebleRolloffHz = project_obj.N163TrebleRolloffHz
				if WaveType == 'S5B':
					outvol = project_obj.S5BVolumeDb
					TrebleDb = project_obj.S5BTrebleDb
					TrebleRolloffHz = project_obj.S5BTrebleRolloffHz
				if WaveType == 'MMC5':
					outvol = project_obj.MMC5VolumeDb
					TrebleDb = project_obj.MMC5TrebleDb
					TrebleRolloffHz = project_obj.MMC5TrebleRolloffHz
				if WaveType in ['EPSMSquare','EPSMFM','EPSM_Kick','EPSM_Snare','EPSM_Cymbal','EPSM_HiHat','EPSM_Tom','EPSM_Rimshot']:
					outvol = project_obj.EPSMVolumeDb
					TrebleDb = project_obj.EPSMTrebleDb
					TrebleRolloffHz = project_obj.EPSMTrebleRolloffHz

				for inst in used_insts: 
					create_inst(xtramath.from_db(outvol), convproj_obj, WaveType, project_obj.Instruments[inst], fxchannel_obj, fxchan)
			else: 
				create_dpcm_inst(project_obj.DPCMMappings, project_obj.DPCMSamples, fxchan, None)
				for inst in used_insts: create_dpcm_inst(project_obj.Instruments[inst].DPCMMappings, project_obj.DPCMSamples, channum, project_obj.Instruments[inst])
				if not fxchannel_obj.visual.from_dset('famistudio', 'chip', 'DPCM', True):
					fxchannel_obj.visual.name = 'DPCM'

			if TrebleRolloffHz != -1:
				fx_id = str(channum)+'_filter'
				plugin_obj = convproj_obj.plugin__add(fx_id, 'universal', 'filter', None)
				plugin_obj.role = 'fx'
				plugin_obj.filter.on = True
				plugin_obj.filter.type.set('high_shelf', None)
				plugin_obj.filter.gain = TrebleDb
				plugin_obj.filter.freq = TrebleRolloffHz+6000
				fxchannel_obj.plugslots.slots_audio.append(fx_id)

			playlist_obj = convproj_obj.playlist__add(channum, 1, True)
			playlist_obj.visual.name = fst_channel.Type
			playlist_obj.visual.color.set_int(defualt_track_color)

			modpatbpm = {}
			for t, i in fst_channel.Instances.items():
				if i not in modpatbpm: modpatbpm[i] = []
				if BPMList[t] != fst_currentsong.PatternSettings.bpm: modpatbpm[i].append(BPMList[t])

			for patid, patdata in fst_channel.Patterns.items():
				cvpj_patid = fst_channel.Type+'-'+patid+'-'+str(fst_currentsong.PatternSettings.bpm)
				nle_obj = convproj_obj.notelistindex__add(cvpj_patid)
				visual_obj = nle_obj.visual
				visual_obj.name = patid+' ('+fst_channel.Type+')'
				if patdata.Color: visual_obj.color.set_hex(patdata.Color)
				else: visual_obj.color.set_int(defualt_pattern_color)
				parse_notes(nle_obj.notelist, patdata.Notes, fst_channel.Type, NoteLength, project_obj.Arpeggios)

				if patid in modpatbpm:
					pattemps = modpatbpm[patid]
					for pattemp in pattemps:
						notemul = fst_currentsong.PatternSettings.bpm/pattemp
						cvpj_patid = fst_channel.Type+'-'+patid+'-'+str(pattemp)
						nle_obj = convproj_obj.notelistindex__add(cvpj_patid)
						nle_obj.visual.name = patid+' ('+fst_channel.Type+')'
						nle_obj.visual.color.set_int(defualt_pattern_color)
						parse_notes(nle_obj.notelist, patdata.Notes, fst_channel.Type, NoteLength*notemul, project_obj.Arpeggios)

			for pattime, patid in fst_channel.Instances.items():
				placement_obj = playlist_obj.placements.add_notes_indexed()
				placement_obj.fromindex = fst_channel.Type+'-'+patid+'-'+str(BPMList[pattime])
				time_obj = placement_obj.time
				time_obj.set_posdur(PointsPos[pattime], PatternLengthList[pattime])

				if patid in fst_channel.Patterns:
					make_auto(convproj_obj, fst_channel.Patterns[patid], NoteLength, BPMNoteMul[pattime], time_obj.position, time_obj.duration, fxchan)

		convproj_obj.add_timesig_lengthbeat(fst_currentsong.PatternLength, fst_currentsong.PatternSettings.BeatLength)
		convproj_obj.timemarker__from_patlenlist(PatternLengthList, fst_currentsong.LoopPoint)

		if not convproj_obj.metadata.name:
			if project_obj.Name: convproj_obj.metadata.name = project_obj.Name
		if project_obj.Author: convproj_obj.metadata.author = project_obj.Author
		if project_obj.Copyright: convproj_obj.metadata.copyright = project_obj.Copyright

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.params.add('bpm', fst_currentsong.PatternSettings.bpm, 'float')