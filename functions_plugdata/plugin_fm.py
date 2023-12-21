# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import plugins
from functions import data_bytes

g_paramnames = {}
g_paramnames['opl2'] = [ 
	['perctype','tremolo_depth','vibrato_depth','fm','feedback'], 
	2, 
	['env_attack','env_decay','env_release','env_sustain','freqmul','ksr','level','ksl','tremolo','vibrato','waveform','sustained', 'perc_env'] ]

g_paramnames['opl3'] = [ 
	['perctype','tremolo_depth','vibrato_depth','con_12','con_34','feedback_12','feedback_34'], 
	4, 
	['env_attack','env_decay','env_release','env_sustain','freqmul','ksr','level','ksl','tremolo','vibrato','waveform','sustained', 'perc_env'] ]

g_paramnames['opn2'] = [ 
	['algorithm','feedback','fms','ams','lfo_enable','lfo_frequency'], 
	4, 
	['am','env_attack','env_decay','freqmul','env_release','env_sustain','level','detune2','ratescale','detune','env_decay2','ssg_enable','ssg_mode'] ]

class fm_data:
	def __init__(self, fmtype):
		self.inst_plugindata = plugins.cvpj_plugin('deftype', 'fm', fmtype)
		self.params = {}
		self.operator = []
		self.fmtype = fmtype
		self.fm_paramnames = g_paramnames[fmtype]

		for paramname in self.fm_paramnames[0]: self.params[paramname] = 0

		for opnum in range(self.fm_paramnames[1]):
			op_data = {}
			for opparamname in self.fm_paramnames[2]: op_data[opparamname] = 0
			self.operator.append(op_data)

	def set_param(self, name, value):
		self.params[name] = value

	def set_op_param(self, opnum, name, value):
		self.operator[opnum][name] = value

	def to_cvpj(self, cvpj_l, pluginid):
		for paramname in self.fm_paramnames[0]: 
			self.inst_plugindata.param_add(paramname, self.params[paramname], 'int', paramname)

		for opnum in range(self.fm_paramnames[1]):
			for opparamname in self.fm_paramnames[2]: 
				cvpj_opparamname = 'op'+str(opnum+1)+'_'+opparamname
				self.inst_plugindata.param_add(cvpj_opparamname, self.operator[opnum][opparamname], 'int', 'OP '+str(opnum+1)+': '+opparamname)

		self.inst_plugindata.to_cvpj(cvpj_l, pluginid)










	def opl_sbi_part_op(self, opnum, i_input, isreversed):
		ixChar, ixScale, ixAttack, ixSustain, ixWaveSel = i_input

		opl_out_flags, opl_out_mul = data_bytes.splitbyte(ixChar) 
		opl_out_trem, opl_out_vib, opl_out_sust, opl_out_krs = data_bytes.to_bin(opl_out_flags, 4)
		opl_out_kls = ixScale >> 6
		opl_out_out = ixScale & 0x3F
		opl_out_wave = ixWaveSel
		opl_out_att, opl_out_dec = data_bytes.splitbyte(ixAttack) 
		opl_out_sus, opl_out_rel = data_bytes.splitbyte(ixSustain)

		if isreversed == False:
			self.set_op_param(opnum, 'env_attack', opl_out_att)
			self.set_op_param(opnum, 'env_decay', opl_out_dec)
			self.set_op_param(opnum, 'env_release', opl_out_rel)
		else:
			self.set_op_param(opnum, 'env_attack', (opl_out_att*-1)+15)
			self.set_op_param(opnum, 'env_decay', (opl_out_dec*-1)+15)
			self.set_op_param(opnum, 'env_release', (opl_out_rel*-1)+15)


		self.set_op_param(opnum, 'ksl', opl_out_kls)
		self.set_op_param(opnum, 'freqmul', opl_out_mul)
		self.set_op_param(opnum, 'env_sustain', opl_out_sus)
		self.set_op_param(opnum, 'sustained', opl_out_sust)
		self.set_op_param(opnum, 'level', opl_out_out)
		self.set_op_param(opnum, 'tremolo', opl_out_trem)
		self.set_op_param(opnum, 'vibrato', opl_out_vib)
		self.set_op_param(opnum, 'ksr', opl_out_krs)
		self.set_op_param(opnum, 'waveform', opl_out_wave)

	def opl_sbi_part_fbcon(self, iFeedback, txt_feedback, txt_fm):
		opl_fb = (iFeedback) >> 1
		opl_con = iFeedback & 0x01

		self.set_param(txt_feedback, opl_fb)
		self.set_param(txt_fm, opl_con)

