# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
from functions import data_bytes
from functions import plugin_vst2

def convert_inst(instdata):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']
	
	if pluginname == 'vrc7':
		if plugindata['use_patch'] == False: vrcregs = plugindata['regs']
		else: vrcregs = vrc7patch[plugindata['patch']]

		print('REGS', vrcregs)

		vrc_mod_flags, vrc_mod_mul = data_bytes.splitbyte(vrcregs[0]) 
		vrc_mod_trem, vrc_mod_vib, vrc_mod_sust, vrc_mod_krs = data_bytes.to_bin(vrc_mod_flags, 4)
		#print('MOD FLAGS', vrc_mod_trem, vrc_mod_vib, vrc_mod_sust, vrc_mod_krs, vrc_mod_mul)

		vrc_car_flags, vrc_car_mul = data_bytes.splitbyte(vrcregs[1])
		vrc_car_trem, vrc_car_vib, vrc_car_sust, vrc_car_krs = data_bytes.to_bin(vrc_car_flags, 4)
		#print('CAR FLAGS', vrc_car_trem, vrc_car_vib, vrc_car_sust, vrc_car_krs, vrc_car_mul)

		vrc_mod_kls = vrcregs[2] >> 6
		vrc_mod_out = vrcregs[2] & 0x3F
		#print('MOD KLS', vrc_mod_kls, 'MOD OUT', vrc_mod_out)

		vrc_car_kls = vrcregs[3] >> 6
		vrc_fb = vrcregs[3] & 0x07
		vrc_mod_wave = int(bool(vrcregs[3] & 0x08))
		vrc_car_wave = int(bool(vrcregs[3] & 0x10))
		#print('CAR KLS', vrc_mod_kls, 'FB', vrc_fb)
		#print('MOD WAVE', vrc_mod_wave, 'CAR WAVE', vrc_car_wave)

		vrc_mod_att, vrc_mod_dec = data_bytes.splitbyte(vrcregs[4]) 
		vrc_car_att, vrc_car_dec = data_bytes.splitbyte(vrcregs[5]) 
		vrc_mod_sus, vrc_mod_rel = data_bytes.splitbyte(vrcregs[6]) 
		vrc_car_sus, vrc_car_rel = data_bytes.splitbyte(vrcregs[7]) 
		#print('CAR ASDR', vrc_car_att, vrc_car_dec, vrc_car_sus, vrc_car_rel)
		#print('MOD ASDR', vrc_mod_att, vrc_mod_dec, vrc_mod_sus, vrc_mod_rel)

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

	if pluginname == 'epsm_fm':

		epsmregs = plugindata['regs']

		epsmopregs = [epsmregs[2:9], epsmregs[9:16], epsmregs[16:23], epsmregs[23:30]]
		epsmopnums = [1,2,3,4]

		fmdata = {}

		fmdata['algorithm'] = epsmregs[0] & 0x0F
		fmdata['feedback'] = (epsmregs[0] >> 4)*2
		#fmdata['ams'] = (epsmregs[1] >> 4) & 0x03
		#fmdata['fms'] = epsmregs[1] & 0x0F
		fmdata['ams'] = 0
		fmdata['fms'] = 0
		fmdata['lfo_enable'] = (epsmregs[30] >> 3)
		fmdata['lfo_frequency'] = epsmregs[30] & 0x07


		print(epsmregs)
		#print(epsmregs[0], (epsmregs[0] >> 4), epsmregs[0] & 0x0f)
		#exit()

		for opnum in range(4):
			op_reg = epsmopregs[opnum]
			op_num = epsmopnums[opnum]
			operator_param = {}
			operator_param['am'] = op_reg[3] >> 7
			operator_param['env_attack'] = op_reg[2] & 0x3F
			operator_param['env_decay'] = op_reg[3] & 0x3F
			operator_param['freqmul'] = op_reg[0] & 0x0F
			operator_param['env_release'] = op_reg[5] & 0x0F
			operator_param['env_sustain'] = op_reg[5] >> 4 #SusLvl
			operator_param['level'] = (op_reg[1]*-1)+127
			operator_param['detune2'] = 0
			operator_param['ratescale'] = op_reg[2] >> 6
			operator_param['detune'] = op_reg[0] >> 4
			operator_param['env_decay2'] = op_reg[4] #SusRate
			operator_param['ssg_enable'] = op_reg[6] >> 3
			operator_param['ssg_mode'] = op_reg[6] & 0x08
			fmdata['op'+str(epsmopnums[opnum])] = operator_param

		instdata['plugin'] = 'opn2'
		instdata['plugindata'] = fmdata
