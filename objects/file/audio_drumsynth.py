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

def parse_env(i_env):
	parsed_env = [x.split(',') for x in i_env.split(' ')]
	return [[int(x[0]),int(x[1])] for x in parsed_env]

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

	def read(self, filename):
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
			if 'FilterEnv' in section_general: self.FilterEnv = parse_env(section_general['FilterEnv'])

		if 'Tone' in ds_parsed:
			section_tone = ds_parsed['Tone'] 
			if 'On' in section_tone: self.Tone.On = section_tone['On']
			if 'Level' in section_tone: self.Tone.Level = section_tone['Level']
			if 'F1' in section_tone: self.Tone.F1 = section_tone['F1']
			if 'F2' in section_tone: self.Tone.F2 = section_tone['F2']
			if 'Droop' in section_tone: self.Tone.Droop = section_tone['Droop']
			if 'Phase' in section_tone: self.Tone.Phase = section_tone['Phase']
			if 'Envelope' in section_tone: self.Tone.Envelope = parse_env(section_tone['Envelope'])

		if 'Noise' in ds_parsed:
			section_noise = ds_parsed['Noise'] 
			if 'On' in section_noise: self.Noise.On = section_noise['On']
			if 'Level' in section_noise: self.Noise.Level = section_noise['Level']
			if 'Slope' in section_noise: self.Noise.Slope = section_noise['Slope']
			if 'Envelope' in section_noise: self.Noise.Envelope = parse_env(section_noise['Envelope'])
			if 'FixedSeq' in section_noise: self.Noise.FixedSeq = section_noise['FixedSeq']

		if 'Overtones' in ds_parsed:
			section_overtones = ds_parsed['Overtones'] 
			if 'On' in section_overtones: self.Overtones.On = section_overtones['On']
			if 'Track1' in section_overtones: self.Overtones.Track1 = section_overtones['Track1']
			if 'Wave1' in section_overtones: self.Overtones.Wave1 = section_overtones['Wave1']
			if 'Envelope1' in section_overtones: self.Overtones.Envelope1 = parse_env(section_overtones['Envelope1'])
			if 'F1' in section_overtones: self.Overtones.F1 = section_overtones['F1']
			if 'Track2' in section_overtones: self.Overtones.Track2 = section_overtones['Track2']
			if 'Wave2' in section_overtones: self.Overtones.Wave2 = section_overtones['Wave2']
			if 'Envelope2' in section_overtones: self.Overtones.Envelope2 = parse_env(section_overtones['Envelope2'])
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
			if 'Envelope' in section_noiseband: self.NoiseBand.Envelope = parse_env(section_noiseband['Envelope'])

		if 'NoiseBand2' in ds_parsed:
			section_noiseband = ds_parsed['NoiseBand2'] 
			if 'On' in section_noiseband: self.NoiseBand2.On = section_noiseband['On']
			if 'Level' in section_noiseband: self.NoiseBand2.Level = section_noiseband['Level']
			if 'F' in section_noiseband: self.NoiseBand2.F = section_noiseband['F']
			if 'dF' in section_noiseband: self.NoiseBand2.dF = section_noiseband['dF']
			if 'Envelope' in section_noiseband: self.NoiseBand2.Envelope = parse_env(section_noiseband['Envelope'])

		if 'Distortion' in ds_parsed:
			section_distortion = ds_parsed['Distortion'] 
			if 'On' in section_distortion: self.Distortion.On = section_distortion['On']
			if 'Clipping' in section_distortion: self.Distortion.Clipping = section_distortion['Clipping']
			if 'Bits' in section_distortion: self.Distortion.Bits = section_distortion['Bits']
			if 'Rate' in section_distortion: self.Distortion.Rate = section_distortion['Rate']