# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import plugins
from functions import idvals

def convert(cvpj_l, pluginid, plugintype):
	epsmregs = plugins.get_plug_dataval(cvpj_l, pluginid, 'regs', None)

	if epsmregs != None:
		epsmopregs = [epsmregs[2:9], epsmregs[9:16], epsmregs[16:23], epsmregs[23:30]]

		plugins.replace_plug(cvpj_l, pluginid, 'fm', 'opn2')
		plugins.add_plug_param(cvpj_l, pluginid, "algorithm", epsmregs[0]&0x0F, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, "feedback", ((epsmregs[0]>>3)*2)+1, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, "ams", (epsmregs[1]>>4)&0x03, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, "fms", epsmregs[1]&0x0F, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, "lfo_enable", epsmregs[30]>>3, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, "lfo_frequency", epsmregs[30]&0x07, 'int', "")

		for opnum in range(4):
			op_reg = epsmopregs[opnum]
			op_num = 'op'+str(opnum)
			plugins.add_plug_param(cvpj_l, pluginid, op_num+'_am', op_reg[3] >> 7, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, op_num+'_env_attack', op_reg[2] & 0x3F, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, op_num+'_env_decay', op_reg[3] & 0x3F, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, op_num+'_freqmul', op_reg[0] & 0x0F, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, op_num+'_env_release', op_reg[5] & 0x0F, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, op_num+'_env_sustain', op_reg[5] >> 4, 'int', "") #SusLvl
			plugins.add_plug_param(cvpj_l, pluginid, op_num+'_level', (op_reg[1]*-1)+127, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, op_num+'_detune2', 0, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, op_num+'_ratescale', op_reg[2] >> 6, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, op_num+'_detune', op_reg[0] >> 4, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, op_num+'_env_decay2', op_reg[4], 'int', "") #SusRate
			plugins.add_plug_param(cvpj_l, pluginid, op_num+'_ssg_enable', op_reg[6] >> 3, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, op_num+'_ssg_mode', op_reg[6] & 0x08, 'int', "")

	return True