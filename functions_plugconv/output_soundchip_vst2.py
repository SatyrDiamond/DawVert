# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

from functions import audio_wav
from functions import plugin_vst2
from functions import data_bytes

from functions_plugparams import params_various_inst
from functions_plugparams import data_vc2xml

vrc7patch = {}
vrc7patch[1] = [3,33,5,6,232,129,66,39]
vrc7patch[2] = [19,65,20,13,216,246,35,18]
vrc7patch[3] = [17,17,8,8,250,178,32,18]
vrc7patch[4] = [49,97,12,7,168,100,97,39]
vrc7patch[5] = [50,33,30,6,225,118,1,40]
vrc7patch[6] = [2,1,6,0,163,226,244,244]
vrc7patch[7] = [33,97,29,7,130,129,17,7]
vrc7patch[8] = [35,33,34,23,162,114,1,23]
vrc7patch[9] = [53,17,37,0,64,115,114,1]
vrc7patch[10] = [181,1,15,15,168,165,81,2]
vrc7patch[11] = [23,193,36,7,248,248,34,18]
vrc7patch[12] = [113,35,17,6,101,116,24,22]
vrc7patch[13] = [1,2,211,5,201,149,3,2]
vrc7patch[14] = [97,99,12,0,148,192,51,246]
vrc7patch[15] = [33,114,13,0,193,213,86,6]

def convert_inst(instdata, out_daw):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']

	if pluginname == 'opn2':
		xmlout = params_various_inst.opnplug_convert(plugindata)
		plugin_vst2.replace_data(instdata, 'any', 'OPNplug', 'chunk', data_vc2xml.make(xmlout), None)

	if pluginname in ['2a03', 'vrc6', 'mmc5', 'sunsoft_5b']:
		params_various_inst.m8bp_init()

		if 'env_arp' in plugindata:
			params_various_inst.m8bp_setvalue("isPitchSequenceEnabled_raw", 1.0)
			params_various_inst.m8bp_setenv('pitch', plugindata['env_arp']['values'])

		if 'env_duty' in plugindata:
			params_various_inst.m8bp_setvalue("isDutySequenceEnabled_raw", 1.0)
			params_various_inst.m8bp_setenv('duty', plugindata['env_duty']['values'])

		if 'env_vol' in plugindata:
			params_various_inst.m8bp_setvalue("isVolumeSequenceEnabled_raw", 1.0)
			params_various_inst.m8bp_setenv('volume', plugindata['env_vol']['values'])

		if 'wave' in plugindata:
			if plugindata['wave'] == 'square': params_various_inst.m8bp_setvalue("osc", 0.0)
			if plugindata['wave'] == 'triangle': params_various_inst.m8bp_setvalue("osc", 1.0)
			if plugindata['wave'] == 'noise': params_various_inst.m8bp_setvalue("osc", 2.0)

		plugin_vst2.replace_data(instdata, 'any', 'Magical 8bit Plug 2', 'chunk', data_vc2xml.make(params_various_inst.m8bp_out()), None)

	if pluginname == 'vrc7':
		if plugindata['use_patch'] == False: vrcregs = plugindata['regs']
		else: vrcregs = vrc7patch[plugindata['patch']]

		print('REGS', vrcregs)

		vrc_mod_flags, vrc_mod_mul = data_bytes.splitbyte(vrcregs[0]) 
		vrc_mod_trem, vrc_mod_vib, vrc_mod_sust, vrc_mod_krs = data_bytes.to_bin(vrc_mod_flags, 4)
		print('MOD FLAGS', vrc_mod_trem, vrc_mod_vib, vrc_mod_sust, vrc_mod_krs, vrc_mod_mul)

		vrc_car_flags, vrc_car_mul = data_bytes.splitbyte(vrcregs[1])
		vrc_car_trem, vrc_car_vib, vrc_car_sust, vrc_car_krs = data_bytes.to_bin(vrc_car_flags, 4)
		print('CAR FLAGS', vrc_car_trem, vrc_car_vib, vrc_car_sust, vrc_car_krs, vrc_car_mul)

		vrc_mod_kls = vrcregs[2] >> 6
		vrc_mod_out = vrcregs[2] & 0x3F
		print('MOD KLS', vrc_mod_kls, 'MOD OUT', vrc_mod_out)

		vrc_car_kls = vrcregs[3] >> 6
		vrc_fb = vrcregs[3] & 0x07
		vrc_mod_wave = int(bool(vrcregs[3] & 0x08))
		vrc_car_wave = int(bool(vrcregs[3] & 0x10))
		print('CAR KLS', vrc_mod_kls, 'FB', vrc_fb)
		print('MOD WAVE', vrc_mod_wave, 'CAR WAVE', vrc_car_wave)

		vrc_mod_att, vrc_mod_dec = data_bytes.splitbyte(vrcregs[4]) 
		vrc_car_att, vrc_car_dec = data_bytes.splitbyte(vrcregs[5]) 
		vrc_mod_sus, vrc_mod_rel = data_bytes.splitbyte(vrcregs[6]) 
		vrc_car_sus, vrc_car_rel = data_bytes.splitbyte(vrcregs[7]) 
		print('CAR ASDR', vrc_car_att, vrc_car_dec, vrc_car_sus, vrc_car_rel)
		print('MOD ASDR', vrc_mod_att, vrc_mod_dec, vrc_mod_sus, vrc_mod_rel)

		instdata['plugin'] = 'opl2'

		plugindata = {}

		plugindata['percussive'] = 0
		plugindata['perctype'] = 0

		plugindata['tremolo_depth'] = 0
		plugindata['vibrato_depth'] = 0
		plugindata['fm'] = 1

		plugindata['op1'] = {}
		plugindata['op2'] = {}

		plugindata['feedback'] = vrc_fb

		plugindata['op1']['scale'] = vrc_mod_kls
		plugindata['op1']['freqmul'] = vrc_mod_mul
		plugindata['op1']['env_attack'] = (vrc_mod_att*-1)+15
		plugindata['op1']['env_sustain'] = (vrc_mod_sus*-1)+15
		plugindata['op1']['perc_env'] = 0
		plugindata['op1']['env_decay'] = (vrc_mod_dec*-1)+15
		plugindata['op1']['env_release'] = vrc_mod_rel
		plugindata['op1']['level'] = (vrc_mod_out*-1)+63
		plugindata['op1']['tremolo'] = vrc_mod_trem
		plugindata['op1']['vibrato'] = vrc_mod_vib
		plugindata['op1']['ksr'] = vrc_mod_krs
		plugindata['op1']['waveform'] = vrc_mod_wave

		plugindata['op2']['scale'] = vrc_car_kls
		plugindata['op2']['freqmul'] = vrc_car_mul
		plugindata['op2']['env_attack'] = (vrc_car_att*-1)+15
		plugindata['op2']['env_sustain'] = (vrc_car_sus*-1)+15
		plugindata['op2']['perc_env'] = 0
		plugindata['op2']['env_decay'] = (vrc_car_dec*-1)+15
		plugindata['op2']['env_release'] = vrc_car_rel
		plugindata['op2']['level'] = 63
		plugindata['op2']['tremolo'] = vrc_car_trem
		plugindata['op2']['vibrato'] = vrc_car_vib
		plugindata['op2']['ksr'] = vrc_car_krs
		plugindata['op2']['waveform'] = vrc_car_wave

		instdata['plugindata'] = plugindata