# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.inst_params import fm_opl

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

class vrc7_op:
	def __init__(self):
		self.env_attack = 0
		self.env_decay = 0
		self.env_sustain = 0
		self.env_release = 0

		self.freqmul = 0
		self.tremolo = False
		self.vibrato = False
		self.sustained = False
		self.ksr = False

		self.level = 0
		self.ksl = 0

		self.waveform = 0

	def avekf(self, inval):
		self.freqmul = inval&15
		self.tremolo = bool(inval&128)
		self.vibrato = bool(inval&64)
		self.sustained = bool(inval&32)
		self.ksr = bool(inval&16)

	def ksl_lvl(self, inval):
		self.level = inval&63
		self.ksl = inval>>6

	def att_dec(self, inval):
		self.env_attack = inval>>4
		self.env_decay = inval&15

	def sus_rel(self, inval):
		self.env_sustain = inval>>4
		self.env_release = inval&15

class vrc7_inst:
	def __init__(self):
		self.name = ''
		self.name_long = ''
		self.patch = 0
		self.feedback = 0
		self.ops = [vrc7_op() for _ in range(2)]
		
	def from_patch(self):
		self.from_regs(vrc7patch[self.patch])

	def from_regs(self, regs):
		self.ops[0].avekf(regs[0])
		self.ops[1].avekf(regs[1])
		self.ops[0].ksl_lvl(regs[2])
		self.ops[1].ksl_lvl(regs[3])
		self.feedback = regs[3] & 0x07
		self.ops[0].waveform = int(bool(regs[3] & 0x08))
		self.ops[1].waveform = int(bool(regs[3] & 0x10))
		self.ops[0].att_dec(regs[4])
		self.ops[1].att_dec(regs[5])
		self.ops[0].sus_rel(regs[6])
		self.ops[1].sus_rel(regs[7])

	def to_opl2(self):
		opl_obj = fm_opl.opl_inst()
		opl_obj.set_opl2()
		opl_obj.feedback_1 = self.feedback
		opl_obj.fm_1 = False

		self.tremolo_depth = True
		self.vibrato_depth = True

		opl_obj.ops[0].level = self.ops[0].level
		opl_obj.ops[1].level = 0

		for opnum in range(2):
			opl_op_obj = opl_obj.ops[opnum]
			vrc7_op_obj = self.ops[opnum]
			opl_op_obj.env_attack = vrc7_op_obj.env_attack
			opl_op_obj.env_decay = vrc7_op_obj.env_decay
			opl_op_obj.env_sustain = vrc7_op_obj.env_sustain
			opl_op_obj.env_release = vrc7_op_obj.env_release
			opl_op_obj.freqmul = vrc7_op_obj.freqmul
			opl_op_obj.tremolo = vrc7_op_obj.tremolo
			opl_op_obj.vibrato = vrc7_op_obj.vibrato
			opl_op_obj.sustained = vrc7_op_obj.sustained
			opl_op_obj.ksr = vrc7_op_obj.ksr
			opl_op_obj.ksl = vrc7_op_obj.ksl
			opl_op_obj.waveform = vrc7_op_obj.waveform
			if not opnum: opl_op_obj.level = vrc7_op_obj.level

		return opl_obj

	def to_cvpj_genid(self, convproj_obj):
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('chip', 'fm', 'vrc7')
		plugin_obj.role = 'synth'
		self.internal_add_params(plugin_obj)
		return plugin_obj, pluginid

	def to_cvpj(self, convproj_obj, pluginid):
		plugin_obj = convproj_obj.plugin__add(pluginid, 'chip', 'fm', 'vrc7')
		plugin_obj.role = 'synth'
		self.internal_add_params(plugin_obj)
		return plugin_obj

	def internal_add_params(self, plugin_obj):
		plugin_obj.params.add('feedback', self.feedback, 'int')

		for opnum, opdata in enumerate(self.ops):
			oppv = 'op'+str(opnum)+'/'
			vnam = 'OP '+str(opnum+1)+': '

			plugin_obj.params.add(oppv+'env_attack', opdata.env_attack, 'int')
			plugin_obj.params.add(oppv+'env_decay', opdata.env_decay, 'int')
			plugin_obj.params.add(oppv+'env_sustain', opdata.env_sustain, 'int')
			plugin_obj.params.add(oppv+'env_release', opdata.env_release, 'int')

			plugin_obj.params.add(oppv+'freqmul', opdata.freqmul, 'int')
			plugin_obj.params.add(oppv+'tremolo', opdata.tremolo, 'bool')
			plugin_obj.params.add(oppv+'vibrato', opdata.vibrato, 'bool')
			plugin_obj.params.add(oppv+'sustained', opdata.sustained, 'bool')
			plugin_obj.params.add(oppv+'ksr', opdata.ksr, 'bool')

			plugin_obj.params.add(oppv+'level', opdata.level if not opnum else 63, 'int')
			plugin_obj.params.add(oppv+'ksl', opdata.ksl, 'int')
			plugin_obj.params.add(oppv+'waveform', opdata.waveform, 'int')

		return plugin_obj
