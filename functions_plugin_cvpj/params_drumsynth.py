# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def env_ds_to_cvpj(plugin_obj, env_name, dsenv):
	autopoints_obj = plugin_obj.env_points_add(env_name, 44100, False, 'int')
	for pp, pv in dsenv:
		autopoint_obj = autopoints_obj.add_point()
		autopoint_obj.pos = pp
		autopoint_obj.value = pv

def to_cvpj(drumsynth_obj, plugin_obj):
	plugin_obj.datavals.add('tuning', drumsynth_obj.Tuning)
	plugin_obj.datavals.add('stretch', drumsynth_obj.Stretch)
	plugin_obj.datavals.add('level', drumsynth_obj.Level)
	plugin_obj.datavals.add('filter', drumsynth_obj.Filter)
	plugin_obj.datavals.add('highpass', drumsynth_obj.HighPass)
	plugin_obj.datavals.add('resonance', drumsynth_obj.Resonance)
	env_ds_to_cvpj(plugin_obj, 'drumsynth_filter', drumsynth_obj.FilterEnv)
	
	plugin_obj.datavals.add('tone_on', drumsynth_obj.Tone.On)
	plugin_obj.datavals.add('tone_level', drumsynth_obj.Tone.Level)
	plugin_obj.datavals.add('tone_f1', drumsynth_obj.Tone.F1)
	plugin_obj.datavals.add('tone_f2', drumsynth_obj.Tone.F2)
	plugin_obj.datavals.add('tone_droop', drumsynth_obj.Tone.Droop)
	plugin_obj.datavals.add('tone_phase', drumsynth_obj.Tone.Phase)
	env_ds_to_cvpj(plugin_obj, 'drumsynth_tone', drumsynth_obj.Tone.Envelope)

	plugin_obj.datavals.add('noise_on', drumsynth_obj.Noise.On)
	plugin_obj.datavals.add('noise_level', drumsynth_obj.Noise.Level)
	plugin_obj.datavals.add('noise_slope', drumsynth_obj.Noise.Slope)
	env_ds_to_cvpj(plugin_obj, 'drumsynth_noise', drumsynth_obj.Noise.Envelope)
	plugin_obj.datavals.add('noise_fixedseq', drumsynth_obj.Noise.FixedSeq)

	plugin_obj.datavals.add('noise_on', drumsynth_obj.Noise.On)
	plugin_obj.datavals.add('noise_level', drumsynth_obj.Noise.Level)
	plugin_obj.datavals.add('noise_slope', drumsynth_obj.Noise.Slope)
	env_ds_to_cvpj(plugin_obj, 'drumsynth_noise', drumsynth_obj.Noise.Envelope)
	plugin_obj.datavals.add('noise_fixedseq', drumsynth_obj.Noise.FixedSeq)

	plugin_obj.datavals.add('overtone_on', drumsynth_obj.Overtones.On)
	plugin_obj.datavals.add('overtone_track1', drumsynth_obj.Overtones.Track1)
	plugin_obj.datavals.add('overtone_wave1', drumsynth_obj.Overtones.Wave1)
	env_ds_to_cvpj(plugin_obj, 'drumsynth_overtone1', drumsynth_obj.Overtones.Envelope1)
	plugin_obj.datavals.add('overtone_f1', drumsynth_obj.Overtones.F1)
	plugin_obj.datavals.add('overtone_track2', drumsynth_obj.Overtones.Track2)
	plugin_obj.datavals.add('overtone_wave2', drumsynth_obj.Overtones.Wave2)
	env_ds_to_cvpj(plugin_obj, 'drumsynth_overtone2', drumsynth_obj.Overtones.Envelope2)
	plugin_obj.datavals.add('overtone_f2', drumsynth_obj.Overtones.F2)
	plugin_obj.datavals.add('overtone_method', drumsynth_obj.Overtones.Method)
	plugin_obj.datavals.add('overtone_param', drumsynth_obj.Overtones.Param)
	plugin_obj.datavals.add('overtone_level', drumsynth_obj.Overtones.Level)
	plugin_obj.datavals.add('overtone_filter', drumsynth_obj.Overtones.Filter)

	plugin_obj.datavals.add('noiseband1_on', drumsynth_obj.NoiseBand.On)
	plugin_obj.datavals.add('noiseband1_level', drumsynth_obj.NoiseBand.Level)
	plugin_obj.datavals.add('noiseband1_f', drumsynth_obj.NoiseBand.F)
	plugin_obj.datavals.add('noiseband1_df', drumsynth_obj.NoiseBand.dF)
	env_ds_to_cvpj(plugin_obj, 'drumsynth_noiseband1', drumsynth_obj.NoiseBand.Envelope)

	plugin_obj.datavals.add('noiseband2_on', drumsynth_obj.NoiseBand2.On)
	plugin_obj.datavals.add('noiseband2_level', drumsynth_obj.NoiseBand2.Level)
	plugin_obj.datavals.add('noiseband2_f', drumsynth_obj.NoiseBand2.F)
	plugin_obj.datavals.add('noiseband2_df', drumsynth_obj.NoiseBand2.dF)
	env_ds_to_cvpj(plugin_obj, 'drumsynth_noiseband2', drumsynth_obj.NoiseBand2.Envelope)

	plugin_obj.datavals.add('distortion_on', drumsynth_obj.Distortion.On)
	plugin_obj.datavals.add('distortion_clipping', drumsynth_obj.Distortion.Clipping)
	plugin_obj.datavals.add('distortion_bits', drumsynth_obj.Distortion.Bits)
	plugin_obj.datavals.add('distortion_rate', drumsynth_obj.Distortion.Rate)