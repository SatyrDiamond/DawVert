# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import configparser

class drumsynth_tone:
	def __init__(self):
		self.On = 0
		self.Level = 100
		self.F1 = 10000
		self.F2 = 10000
		self.Droop = 0
		self.Phase = 0
		self.Envelope = []

class drumsynth_noise:
	def __init__(self):
		self.On = 0
		self.Level = 0
		self.Slope = 50
		self.Envelope = []
		self.FixedSeq = 0

class drumsynth_overtones:
	def __init__(self):
		self.On = 0
		self.Track1 = 0
		self.Wave1 = 0
		self.Envelope1 = []
		self.F1 = 200
		self.Track2 = 0
		self.Wave2 = 0
		self.Envelope2 = []
		self.F2 = 120
		self.Method = 1
		self.Param = 0
		self.Level = 128
		self.Filter = 0

class drumsynth_noiseband:
	def __init__(self):
		self.On = 0
		self.Level = 0
		self.F = 1000
		self.dF = 50
		self.Envelope = []

class drumsynth_distortion:
	def __init__(self):
		self.On = 0
		self.Clipping = 0
		self.Bits = 0
		self.Rate = 0

def env_from_txt(i_env):
	parsed_env = [x.split(',') for x in i_env.split(' ')]
	return [[int(x[0]),int(x[1])] for x in parsed_env]

def env_to_cvpj_env(plugin_obj, env_name, dsenv):
	autopoints_obj = plugin_obj.env_points_add(env_name, 44100, False, 'int')
	for pp, pv in dsenv:
		autopoints_obj.points__add_normal(pp, pv, 0, None)

class drumsynth_main:
	def __init__(self):
		self.Version = 'DrumSynth v2.0'
		self.Comment = None
		self.Tuning = 0
		self.Stretch = 100
		self.Level = 0
		self.Filter = 0
		self.HighPass = 0
		self.Resonance = 0
		self.FilterEnv = []
		self.Tone = drumsynth_tone()
		self.Noise = drumsynth_noise()
		self.Overtones = drumsynth_overtones()
		self.NoiseBand = drumsynth_noiseband()
		self.NoiseBand2 = drumsynth_noiseband()
		self.Distortion = drumsynth_distortion()

	def load_from_file(self, filename):
		ds_parsed = configparser.ConfigParser()
		ds_parsed.read(filename)
		if 'General' in ds_parsed:
			section_general = ds_parsed['General'] 
			if 'Version' in section_general: self.Version = section_general['Version']
			if 'Comment' in section_general: self.Comment = section_general['Comment']
			if 'Tuning' in section_general: self.Tuning = section_general['Tuning']
			if 'Stretch' in section_general: self.Stretch = section_general['Stretch']
			if 'Level' in section_general: self.Level = section_general['Level']
			if 'Filter' in section_general: self.Filter = section_general['Filter']
			if 'HighPass' in section_general: self.HighPass = section_general['HighPass']
			if 'Resonance' in section_general: self.Resonance = section_general['Resonance']
			if 'FilterEnv' in section_general: self.FilterEnv = env_from_txt(section_general['FilterEnv'])

		if 'Tone' in ds_parsed:
			section_tone = ds_parsed['Tone'] 
			if 'On' in section_tone: self.Tone.On = section_tone['On']
			if 'Level' in section_tone: self.Tone.Level = section_tone['Level']
			if 'F1' in section_tone: self.Tone.F1 = section_tone['F1']
			if 'F2' in section_tone: self.Tone.F2 = section_tone['F2']
			if 'Droop' in section_tone: self.Tone.Droop = section_tone['Droop']
			if 'Phase' in section_tone: self.Tone.Phase = section_tone['Phase']
			if 'Envelope' in section_tone: self.Tone.Envelope = env_from_txt(section_tone['Envelope'])

		if 'Noise' in ds_parsed:
			section_noise = ds_parsed['Noise'] 
			if 'On' in section_noise: self.Noise.On = section_noise['On']
			if 'Level' in section_noise: self.Noise.Level = section_noise['Level']
			if 'Slope' in section_noise: self.Noise.Slope = section_noise['Slope']
			if 'Envelope' in section_noise: self.Noise.Envelope = env_from_txt(section_noise['Envelope'])
			if 'FixedSeq' in section_noise: self.Noise.FixedSeq = section_noise['FixedSeq']

		if 'Overtones' in ds_parsed:
			section_overtones = ds_parsed['Overtones'] 
			if 'On' in section_overtones: self.Overtones.On = section_overtones['On']
			if 'Track1' in section_overtones: self.Overtones.Track1 = section_overtones['Track1']
			if 'Wave1' in section_overtones: self.Overtones.Wave1 = section_overtones['Wave1']
			if 'Envelope1' in section_overtones: self.Overtones.Envelope1 = env_from_txt(section_overtones['Envelope1'])
			if 'F1' in section_overtones: self.Overtones.F1 = section_overtones['F1']
			if 'Track2' in section_overtones: self.Overtones.Track2 = section_overtones['Track2']
			if 'Wave2' in section_overtones: self.Overtones.Wave2 = section_overtones['Wave2']
			if 'Envelope2' in section_overtones: self.Overtones.Envelope2 = env_from_txt(section_overtones['Envelope2'])
			if 'F2' in section_overtones: self.Overtones.F2 = section_overtones['F2']
			if 'Method' in section_overtones: self.Overtones.Method = section_overtones['Method']
			if 'Param' in section_overtones: self.Overtones.Param = section_overtones['Param']
			if 'Level' in section_overtones: self.Overtones.Level = section_overtones['Level']
			if 'Filter' in section_overtones: self.Overtones.Filter = section_overtones['Filter']

		if 'NoiseBand' in ds_parsed:
			section_noiseband = ds_parsed['NoiseBand'] 
			if 'On' in section_noiseband: self.NoiseBand.On = section_noiseband['On']
			if 'Level' in section_noiseband: self.NoiseBand.Level = section_noiseband['Level']
			if 'F' in section_noiseband: self.NoiseBand.F = section_noiseband['F']
			if 'dF' in section_noiseband: self.NoiseBand.dF = section_noiseband['dF']
			if 'Envelope' in section_noiseband: self.NoiseBand.Envelope = env_from_txt(section_noiseband['Envelope'])

		if 'NoiseBand2' in ds_parsed:
			section_noiseband = ds_parsed['NoiseBand2'] 
			if 'On' in section_noiseband: self.NoiseBand2.On = section_noiseband['On']
			if 'Level' in section_noiseband: self.NoiseBand2.Level = section_noiseband['Level']
			if 'F' in section_noiseband: self.NoiseBand2.F = section_noiseband['F']
			if 'dF' in section_noiseband: self.NoiseBand2.dF = section_noiseband['dF']
			if 'Envelope' in section_noiseband: self.NoiseBand2.Envelope = env_from_txt(section_noiseband['Envelope'])

		if 'Distortion' in ds_parsed:
			section_distortion = ds_parsed['Distortion'] 
			if 'On' in section_distortion: self.Distortion.On = section_distortion['On']
			if 'Clipping' in section_distortion: self.Distortion.Clipping = section_distortion['Clipping']
			if 'Bits' in section_distortion: self.Distortion.Bits = section_distortion['Bits']
			if 'Rate' in section_distortion: self.Distortion.Rate = section_distortion['Rate']

	def to_plugin(self, plugin_obj):
		plugin_obj.datavals.add('tuning', self.Tuning)
		plugin_obj.datavals.add('stretch', self.Stretch)
		plugin_obj.datavals.add('level', self.Level)
		plugin_obj.datavals.add('filter', self.Filter)
		plugin_obj.datavals.add('highpass', self.HighPass)
		plugin_obj.datavals.add('resonance', self.Resonance)
		env_to_cvpj_env(plugin_obj, 'drumsynth_filter', self.FilterEnv)
		
		plugin_obj.datavals.add('tone_on', self.Tone.On)
		plugin_obj.datavals.add('tone_level', self.Tone.Level)
		plugin_obj.datavals.add('tone_f1', self.Tone.F1)
		plugin_obj.datavals.add('tone_f2', self.Tone.F2)
		plugin_obj.datavals.add('tone_droop', self.Tone.Droop)
		plugin_obj.datavals.add('tone_phase', self.Tone.Phase)
		env_to_cvpj_env(plugin_obj, 'drumsynth_tone', self.Tone.Envelope)
	
		plugin_obj.datavals.add('noise_on', self.Noise.On)
		plugin_obj.datavals.add('noise_level', self.Noise.Level)
		plugin_obj.datavals.add('noise_slope', self.Noise.Slope)
		env_to_cvpj_env(plugin_obj, 'drumsynth_noise', self.Noise.Envelope)
		plugin_obj.datavals.add('noise_fixedseq', self.Noise.FixedSeq)
	
		plugin_obj.datavals.add('noise_on', self.Noise.On)
		plugin_obj.datavals.add('noise_level', self.Noise.Level)
		plugin_obj.datavals.add('noise_slope', self.Noise.Slope)
		env_to_cvpj_env(plugin_obj, 'drumsynth_noise', self.Noise.Envelope)
		plugin_obj.datavals.add('noise_fixedseq', self.Noise.FixedSeq)
	
		plugin_obj.datavals.add('overtone_on', self.Overtones.On)
		plugin_obj.datavals.add('overtone_track1', self.Overtones.Track1)
		plugin_obj.datavals.add('overtone_wave1', self.Overtones.Wave1)
		env_to_cvpj_env(plugin_obj, 'drumsynth_overtone1', self.Overtones.Envelope1)
		plugin_obj.datavals.add('overtone_f1', self.Overtones.F1)
		plugin_obj.datavals.add('overtone_track2', self.Overtones.Track2)
		plugin_obj.datavals.add('overtone_wave2', self.Overtones.Wave2)
		env_to_cvpj_env(plugin_obj, 'drumsynth_overtone2', self.Overtones.Envelope2)
		plugin_obj.datavals.add('overtone_f2', self.Overtones.F2)
		plugin_obj.datavals.add('overtone_method', self.Overtones.Method)
		plugin_obj.datavals.add('overtone_param', self.Overtones.Param)
		plugin_obj.datavals.add('overtone_level', self.Overtones.Level)
		plugin_obj.datavals.add('overtone_filter', self.Overtones.Filter)
	
		plugin_obj.datavals.add('noiseband1_on', self.NoiseBand.On)
		plugin_obj.datavals.add('noiseband1_level', self.NoiseBand.Level)
		plugin_obj.datavals.add('noiseband1_f', self.NoiseBand.F)
		plugin_obj.datavals.add('noiseband1_df', self.NoiseBand.dF)
		env_to_cvpj_env(plugin_obj, 'drumsynth_noiseband1', self.NoiseBand.Envelope)
	
		plugin_obj.datavals.add('noiseband2_on', self.NoiseBand2.On)
		plugin_obj.datavals.add('noiseband2_level', self.NoiseBand2.Level)
		plugin_obj.datavals.add('noiseband2_f', self.NoiseBand2.F)
		plugin_obj.datavals.add('noiseband2_df', self.NoiseBand2.dF)
		env_to_cvpj_env(plugin_obj, 'drumsynth_noiseband2', self.NoiseBand2.Envelope)
	
		plugin_obj.datavals.add('distortion_on', self.Distortion.On)
		plugin_obj.datavals.add('distortion_clipping', self.Distortion.Clipping)
		plugin_obj.datavals.add('distortion_bits', self.Distortion.Bits)
		plugin_obj.datavals.add('distortion_rate', self.Distortion.Rate)

		return plugin_obj