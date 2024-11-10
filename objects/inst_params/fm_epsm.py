# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.inst_params import fm_opn2

class epsm_op:
	def __init__(self):
		self.am = 0
		self.detune = 0
		self.detune2 = 0
		self.env_attack = 0
		self.env_decay = 0
		self.env_decay2 = 0
		self.env_release = 0
		self.env_sustain = 0
		self.freqmul = 0
		self.level = 0
		self.ratescale = 0
		self.ssg_enable = False
		self.ssg_mode = 0

	def ssg_byte(self, ssgmode):
		self.ssg_enable = bool(ssgmode & 0b0001000)
		self.ssg_mode = ssgmode & 0b00001111

class epsm_inst:
	def __init__(self):
		self.name = ''
		self.name_long = ''

		self.patch = 0

		self.algorithm = 0
		self.feedback = 0
		self.fms = 0
		self.ams = 0
		self.lfo_enable = 0
		self.lfo_frequency = 0
		self.ops = [epsm_op() for _ in range(4)]
		
	def from_patch(self):
		pass

	def from_regs(self, epsmregs):
		epsmopregs = [epsmregs[2:9], epsmregs[9:16], epsmregs[16:23], epsmregs[23:30]]

		self.algorithm = epsmregs[0]&0x0F
		self.feedback = epsmregs[0]>>3
		self.ams = (epsmregs[1]>>4)&0x03
		self.fms = epsmregs[1]&0x0F
		self.lfo_enable = epsmregs[30]>>3
		self.lfo_frequency = epsmregs[30]&0x07

		for opnum in range(4):
			op_obj = self.ops[opnum]
			op_regs = epsmopregs[opnum]
			op_obj.freqmul = op_regs[0] & 0x0F
			op_obj.detune = op_regs[0] >> 4
			op_obj.level = op_regs[1]
			op_obj.env_attack = op_regs[2] & 0x3F
			op_obj.ratescale = op_regs[2] >> 6
			op_obj.am = op_regs[3] >> 7
			op_obj.env_decay = op_regs[3] & 0x3F
			op_obj.env_decay2 = op_regs[4]
			op_obj.env_release = op_regs[5] & 0x0F
			op_obj.env_sustain = op_regs[5] >> 4
			op_obj.ssg_enable = op_regs[6] >> 3
			op_obj.ssg_mode = op_regs[6] & 0x08

	def to_opn2(self):
		opn_obj = fm_opn2.opn2_inst()
		opn_obj.algorithm = self.algorithm
		opn_obj.feedback = ((self.feedback)*2)+1
		opn_obj.ams = self.ams
		opn_obj.fms = self.fms
		opn_obj.lfo_enable = self.lfo_enable
		opn_obj.lfo_frequency = self.lfo_frequency

		for opnum in range(4):
			opn_op_obj = opn_obj.ops[opnum]
			epsm_op_obj = self.ops[opnum]
			opn_op_obj.freqmul = epsm_op_obj.freqmul
			opn_op_obj.detune = epsm_op_obj.detune
			opn_op_obj.level = (epsm_op_obj.level*-1)+127
			opn_op_obj.env_attack = epsm_op_obj.env_attack
			opn_op_obj.ratescale = epsm_op_obj.ratescale
			opn_op_obj.am = epsm_op_obj.am
			opn_op_obj.env_decay = epsm_op_obj.env_decay
			opn_op_obj.env_decay2 = epsm_op_obj.env_decay2
			opn_op_obj.env_release = epsm_op_obj.env_release
			opn_op_obj.env_sustain = epsm_op_obj.env_sustain
			opn_op_obj.ssg_enable = epsm_op_obj.ssg_enable
			opn_op_obj.ssg_mode = epsm_op_obj.ssg_mode

		return opn_obj

	def to_cvpj_genid(self, convproj_obj):
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('chip', 'fm', 'epsm')
		self.internal_add_params(plugin_obj)
		return plugin_obj, pluginid

	def to_cvpj(self, convproj_obj, pluginid):
		plugin_obj = convproj_obj.plugin__add(pluginid, 'chip', 'fm', 'epsm')
		self.internal_add_params(plugin_obj)
		return plugin_obj

	def internal_add_params(self, plugin_obj):
		plugin_obj.params.add('algorithm', self.vibrato_depth, 'int')
		plugin_obj.params.add('feedback', self.fm_1, 'int')
		plugin_obj.params.add('fms', self.fm_2, 'int')
		plugin_obj.params.add('ams', self.feedback_1, 'int')
		plugin_obj.params.add('lfo_enable', self.feedback_1, 'int')
		plugin_obj.params.add('lfo_frequency', self.feedback_1, 'int')

		for opnum, opdata in enumerate(4):
			oppv = 'op'+str(opnum+1)+'/'
			vnam = 'OP '+str(opnum+1)+': '

			plugin_obj.params.add(oppv+'am', opdata.env_attack, 'int')
			plugin_obj.params.add(oppv+'detune', opdata.env_decay, 'int')
			plugin_obj.params.add(oppv+'detune2', opdata.env_sustain, 'int')
			plugin_obj.params.add(oppv+'env_attack', opdata.env_release, 'int')
			plugin_obj.params.add(oppv+'env_decay', opdata.freqmul, 'int')
			plugin_obj.params.add(oppv+'env_decay2', opdata.tremolo, 'int')
			plugin_obj.params.add(oppv+'env_release', opdata.vibrato, 'int')
			plugin_obj.params.add(oppv+'env_sustain', opdata.sustained, 'int')
			plugin_obj.params.add(oppv+'freqmul', opdata.ksr, 'int')
			plugin_obj.params.add(oppv+'level', opdata.level, 'int')
			plugin_obj.params.add(oppv+'ratescale', opdata.ksl, 'int')
			plugin_obj.params.add(oppv+'ssg_enable', opdata.waveform, 'bool')
			plugin_obj.params.add(oppv+'ssg_mode', opdata.waveform, 'int')











