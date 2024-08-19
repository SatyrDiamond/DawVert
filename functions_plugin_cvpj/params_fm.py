# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

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

g_paramnames['opm'] = [ 
	['alg','ams','fb','lfo_amd','lfo_frq','lfo_pmd','nfrq','noise','opmsk','pms'], 
	4, 
	['tl','ar','d1r','d1l','d2r','rr','ks','ml','dt1','dt2','ams-en'] ]

g_paramnames['vrc7'] = [ 
	['feedback'], 
	2, 
	['env_attack','env_decay','env_release','env_sustain','freqmul','ksr','level','ksl','tremolo','vibrato','waveform','sustained'] ]

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

class fm_data:
	def __init__(self, fmtype):
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

	def to_cvpj(self, convproj_obj, pluginid):
		plugin_obj = convproj_obj.add_plugin(pluginid, 'fm', self.fmtype)
		for paramname in self.fm_paramnames[0]: 
			param_obj = plugin_obj.params.add(paramname, self.params[paramname], 'int')
			param_obj.visual.name = paramname

		for opnum in range(self.fm_paramnames[1]):
			for opparamname in self.fm_paramnames[2]: 
				cvpj_opparamname = 'op'+str(opnum+1)+'/'+opparamname
				param_obj = plugin_obj.params.add(cvpj_opparamname, self.operator[opnum][opparamname], 'int')
				param_obj.visual.name = 'OP '+str(opnum+1)+': '+opparamname







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









	def vrc7_regs(self, inregs, use_patch, patch_num):
		if use_patch == True: vrcregs = vrc7patch[patch_num]
		else: vrcregs = inregs
	
		vrc_mod_flags, vrc_mod_mul = data_bytes.splitbyte(vrcregs[0]) 
		vrc_mod_trem, vrc_mod_vib, vrc_mod_sust, vrc_mod_krs = data_bytes.to_bin(vrc_mod_flags, 4)
		vrc_car_flags, vrc_car_mul = data_bytes.splitbyte(vrcregs[1])
		vrc_car_trem, vrc_car_vib, vrc_car_sust, vrc_car_krs = data_bytes.to_bin(vrc_car_flags, 4)
		vrc_mod_kls = vrcregs[2] >> 6
		vrc_mod_out = vrcregs[2] & 0x3F
		vrc_car_kls = vrcregs[3] >> 6
		vrc_fb = vrcregs[3] & 0x07
		vrc_mod_wave = int(bool(vrcregs[3] & 0x08))
		vrc_car_wave = int(bool(vrcregs[3] & 0x10))
		vrc_mod_att, vrc_mod_dec = data_bytes.splitbyte(vrcregs[4]) 
		vrc_car_att, vrc_car_dec = data_bytes.splitbyte(vrcregs[5]) 
		vrc_mod_sus, vrc_mod_rel = data_bytes.splitbyte(vrcregs[6]) 
		vrc_car_sus, vrc_car_rel = data_bytes.splitbyte(vrcregs[7])
	
		self.set_param("feedback", vrc_fb)

		self.set_op_param(0, "scale", vrc_mod_kls)
		self.set_op_param(0, "freqmul", vrc_mod_mul)
		self.set_op_param(0, "env_attack", (vrc_mod_att*-1)+15)
		self.set_op_param(0, "env_sustain", (vrc_mod_sus*-1)+15)
		self.set_op_param(0, "env_decay", (vrc_mod_dec*-1)+15)
		self.set_op_param(0, "env_release", vrc_mod_rel)
		self.set_op_param(0, "level", (vrc_mod_out*-1)+63)
		self.set_op_param(0, "tremolo", vrc_mod_trem)
		self.set_op_param(0, "vibrato", vrc_mod_vib)
		self.set_op_param(0, "ksr", vrc_mod_krs)
		self.set_op_param(0, "waveform", vrc_mod_wave)
	
		self.set_op_param(1, "scale", vrc_car_kls)
		self.set_op_param(1, "freqmul", vrc_car_mul)
		self.set_op_param(1, "env_attack", (vrc_car_att*-1)+15)
		self.set_op_param(1, "env_sustain", (vrc_car_sus*-1)+15)
		self.set_op_param(1, "env_decay", (vrc_car_dec*-1)+15)
		self.set_op_param(1, "env_release", vrc_car_rel)
		self.set_op_param(1, "level", 63)
		self.set_op_param(1, "tremolo", vrc_car_trem)
		self.set_op_param(1, "vibrato", vrc_car_vib)
		self.set_op_param(1, "ksr", vrc_car_krs)
		self.set_op_param(1, "waveform", vrc_car_wave)