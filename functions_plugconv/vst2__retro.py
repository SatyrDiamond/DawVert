# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import pathlib

from functions import audio_wav
from functions import plugin_vst2
from functions import plugins

from functions_plugparams import params_various_inst
from functions_plugparams import data_vc2xml
from functions_plugparams import params_vital
from functions_plugparams import params_vital_wavetable

def convert(cvpj_l, pluginid, plugintype):
	blk_env_pitch = plugins.get_env_blocks(cvpj_l, pluginid, 'pitch')
	blk_env_duty = plugins.get_env_blocks(cvpj_l, pluginid, 'duty')
	blk_env_vol = plugins.get_env_blocks(cvpj_l, pluginid, 'vol')

	m8bp_out = True
	if blk_env_vol != None:
		if blk_env_vol['max'] != 15: m8bp_out = False

	if plugintype[1] in ['square', 'triangle', 'noise'] and m8bp_out == True:
		params_various_inst.m8bp_init()

		a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = plugins.get_asdr_env(cvpj_l, pluginid, 'volume')
		params_various_inst.m8bp_setvalue("attack", a_attack)
		params_various_inst.m8bp_setvalue("decay", a_decay)
		params_various_inst.m8bp_setvalue("suslevel", a_sustain)
		params_various_inst.m8bp_setvalue("release", a_release)

		if plugintype[1] != 'noise':	
			r_duty = plugins.get_plug_dataval(cvpj_l, pluginid, 'duty', 0)
			if r_duty == 0: params_various_inst.m8bp_setvalue("duty", 2)
			if r_duty == 1: params_various_inst.m8bp_setvalue("duty", 1)
			if r_duty == 2: params_various_inst.m8bp_setvalue("duty", 0)
		else:
			r_type = plugins.get_plug_dataval(cvpj_l, pluginid, 'type', 0)
			if r_type == '1bit_short': params_various_inst.m8bp_setvalue("duty", 0)
			if r_type == '4bit': params_various_inst.m8bp_setvalue("duty", 1)

		if blk_env_pitch:
			params_various_inst.m8bp_setvalue("isPitchSequenceEnabled_raw", 1.0)
			params_various_inst.m8bp_setenv('pitch', blk_env_pitch['values'])

		if blk_env_duty:
			params_various_inst.m8bp_setvalue("isDutySequenceEnabled_raw", 1.0)
			params_various_inst.m8bp_setenv('duty', blk_env_duty['values'])

		if blk_env_vol:
			params_various_inst.m8bp_setvalue("isVolumeSequenceEnabled_raw", 1.0)
			params_various_inst.m8bp_setenv('volume', blk_env_vol['values'])

		if plugintype[1] == 'square': params_various_inst.m8bp_setvalue("osc", 0.0)
		if plugintype[1] == 'triangle': params_various_inst.m8bp_setvalue("osc", 1.0)
		if plugintype[1] == 'noise': params_various_inst.m8bp_setvalue("osc", 2.0)

		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Magical 8bit Plug 2', 'chunk', data_vc2xml.make(params_various_inst.m8bp_out()), None)
		return True
	else:
		params_vital.create()
		params_vital.setvalue('osc_1_on', 1)
		params_vital.setvalue('osc_1_level', 0.5)
		params_vital.setvalue('volume', 4000)

		r_duty = plugins.get_plug_dataval(cvpj_l, pluginid, 'duty', 0)
		if r_duty == 0: vital_duty = 0.5
		if r_duty == 1: vital_duty = 0.25
		if r_duty == 2: vital_duty = 0.125

		if plugintype[1] == 'sine': vital_shape = params_vital_wavetable.create_wave('sine', 0, None)
		if plugintype[1] == 'square': vital_shape = params_vital_wavetable.create_wave('square', 0, vital_duty)
		if plugintype[1] == 'triangle': vital_shape = params_vital_wavetable.create_wave('triangle', 0, None)
		if plugintype[1] == 'saw': vital_shape = params_vital_wavetable.create_wave('saw', 0, None)

		params_vital.replacewave(0, vital_shape)

		env_found = params_vital.importcvpj_env_block(cvpj_l, pluginid, 1, 'vol')
		if env_found: params_vital.set_modulation(1, 'lfo_1', 'osc_1_level', 1, 0, 1, 0, 0)

		env_found = params_vital.importcvpj_env_block(cvpj_l, pluginid, 2, 'pitch')
		#if env_found: params_vital.set_modulation(1, 'lfo_1', 'osc_1_level', 1, 0, 1, 0, 0)

		vitaldata = params_vital.getdata()
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Vital', 'chunk', vitaldata.encode('utf-8'), None)
		return True