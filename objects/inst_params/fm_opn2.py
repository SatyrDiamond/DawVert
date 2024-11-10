# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class opn2_op:
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

class opn2_inst:
	def __init__(self):
		self.name = ''
		self.name_long = ''

		self.algorithm = 0
		self.feedback = 0
		self.fms = 0
		self.ams = 0
		self.lfo_enable = 0
		self.lfo_frequency = 0
		self.ops = [opn2_op() for _ in range(4)]
		
	def to_cvpj_genid(self, convproj_obj):
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('chip', 'fm', 'opn2')
		plugin_obj.role = 'synth'
		self.internal_add_params(plugin_obj)
		return plugin_obj, pluginid

	def to_cvpj(self, convproj_obj, pluginid):
		plugin_obj = convproj_obj.plugin__add(pluginid, 'chip', 'fm', 'opn2')
		plugin_obj.role = 'synth'
		self.internal_add_params(plugin_obj)
		return plugin_obj

	def internal_add_params(self, plugin_obj):
		plugin_obj.params.add('algorithm', self.algorithm, 'int')
		plugin_obj.params.add('feedback', self.feedback, 'int')
		plugin_obj.params.add('fms', self.fms, 'int')
		plugin_obj.params.add('ams', self.ams, 'int')
		plugin_obj.params.add('lfo_enable', self.lfo_enable, 'int')
		plugin_obj.params.add('lfo_frequency', self.lfo_frequency, 'int')

		for opnum, opdata in enumerate(self.ops):
			oppv = 'op'+str(opnum+1)+'/'
			vnam = 'OP '+str(opnum+1)+': '

			plugin_obj.params.add(oppv+'am', opdata.am, 'int')
			plugin_obj.params.add(oppv+'detune', opdata.detune, 'int')
			plugin_obj.params.add(oppv+'detune2', opdata.detune2, 'int')
			plugin_obj.params.add(oppv+'env_attack', opdata.env_attack, 'int')
			plugin_obj.params.add(oppv+'env_decay', opdata.env_decay, 'int')
			plugin_obj.params.add(oppv+'env_decay2', opdata.env_decay2, 'int')
			plugin_obj.params.add(oppv+'env_release', opdata.env_release, 'int')
			plugin_obj.params.add(oppv+'env_sustain', opdata.env_sustain, 'int')
			plugin_obj.params.add(oppv+'freqmul', opdata.freqmul, 'int')
			plugin_obj.params.add(oppv+'level', opdata.level, 'int')
			plugin_obj.params.add(oppv+'ratescale', opdata.ratescale, 'int')
			plugin_obj.params.add(oppv+'ssg_enable', opdata.ssg_enable, 'bool')
			plugin_obj.params.add(oppv+'ssg_mode', opdata.ssg_mode, 'int')

		return plugin_obj












