# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
from functions import plugins
from functions import plugin_vst2
from functions_plugparams import params_vital
from functions_plugparams import wave

def convert(cvpj_l, pluginid, plugintype):
	print(plugintype[1])
	params_vital.create()
	params_vital.setvalue('osc_1_on', 1)
	params_vital.setvalue('osc_1_random_phase', 0)
	params_vital.setvalue('osc_2_random_phase', 0)
	params_vital.setvalue('osc_3_random_phase', 0)

	if plugintype[1] in ['chip','custom chip']:
		params_vital.importcvpj_wave(cvpj_l, pluginid, 1, None)
		params_vital.importcvpj_wave(cvpj_l, pluginid, 2, None)
		params_vital.importcvpj_wave(cvpj_l, pluginid, 3, None)
	if plugintype[1] == 'harmonics':
		params_vital.importcvpj_harm(cvpj_l, pluginid, 1, None)
		params_vital.importcvpj_harm(cvpj_l, pluginid, 2, None)
		params_vital.importcvpj_harm(cvpj_l, pluginid, 3, None)
	if plugintype[1] == 'Picked String':
		params_vital.importcvpj_harm(cvpj_l, pluginid, 1, None)
		params_vital.importcvpj_harm(cvpj_l, pluginid, 2, None)
		params_vital.importcvpj_harm(cvpj_l, pluginid, 3, None)
		params_vital.setvalue('filter_fx_on', 1)
		params_vital.setvalue('filter_fx_cutoff', 20)
		params_vital.setvalue('filter_fx_resonance', 0)
		params_vital.set_modulation(2, 'env_1', 'filter_fx_cutoff', 0.5, 0, 0, 0, 0)

	params_vital.importcvpj_env_asdr(cvpj_l, pluginid, 1, 'vol')

	unisontype = plugins.get_plug_dataval(cvpj_l, pluginid, 'unison', 'none')

	out_cents = 0
	out_semi = 0
	start_level = 1

	if unisontype != 'none':
		if unisontype == 'shimmer':
			params_vital.setvalue('osc_1_unison_detune', 1.01)
			params_vital.setvalue('osc_1_unison_voices', 3)
		if unisontype == 'hum':
			params_vital.setvalue('osc_1_unison_detune', 1.6)
			params_vital.setvalue('osc_1_unison_voices', 6)
		if unisontype == 'honky tonk':
			params_vital.setvalue('osc_1_unison_detune', 2.3)
			params_vital.setvalue('osc_1_unison_voices', 6)
		if unisontype == 'dissonant':
			params_vital.setvalue('osc_1_unison_detune', 3.5)
			params_vital.setvalue('osc_1_unison_voices', 3)
		if unisontype == 'fifth':
			params_vital.setvalue('osc_2_on', 2)
			bb_pitch_fifth = 7 + bb_pitch
			out_cents_fifth = int(bb_pitch_fifth)
			out_semi_fifth = bb_pitch_fifth - out_cents_fifth
			params_vital.setvalue('osc_2_transpose', out_cents_fifth)
			params_vital.setvalue('osc_2_tune', out_semi_fifth)
			start_level = start_level/1.3
		if unisontype == 'octave':
			params_vital.setvalue('osc_2_on', 2)
			params_vital.setvalue('osc_2_transpose', out_cents+12)
			params_vital.setvalue('osc_2_tune', out_semi)
			start_level = start_level/1.3
		if unisontype == 'bowed':
			#params_vital.replacewave(1, wave.resizewave(t_sample_invert))
			params_vital.setvalue('osc_2_on', 2)
			params_vital.setvalue('osc_2_transpose', out_cents)
			params_vital.setvalue('osc_2_tune', out_semi+0.05)
			start_level = start_level/1.3
		if unisontype == 'piano':
			params_vital.setvalue('osc_2_on', 2)
			params_vital.setvalue('osc_2_transpose', out_cents)
			params_vital.setvalue('osc_2_tune', out_semi+0.02)
			start_level = start_level/1.3
		if unisontype == 'warbled':
			params_vital.setvalue('osc_1_unison_detune', 4)
			params_vital.setvalue('osc_1_unison_voices', 4)

	params_vital.setvalue('osc_1_level', start_level)
	params_vital.setvalue('osc_2_level', start_level)
	params_vital.setvalue('osc_3_level', start_level)

	vitaldata = params_vital.getdata()
	plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Vital', 'chunk', vitaldata.encode('utf-8'), None)
