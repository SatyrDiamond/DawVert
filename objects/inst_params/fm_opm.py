# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore

class opm_op:
	def __init__(self):
		self.attack_rate = 0
		self.decay_rate = 0
		self.sustain_rate = 0
		self.release_rate = 0
		self.sustain_level = 0
		self.ksr = 0
		self.freqmul = 0
		self.level = 0
		self.detune = 0
		self.detune2 = 0

class opm_inst:
	def __init__(self):
		self.name = ''
		self.name_long = ''

		self.algorithm = 0
		self.feedback = 0
		self.block_freq = 0
		self.ops = [opm_op() for _ in range(4)]

	def from_valsound(self, valsoundid):
		globalstore.idvals.load('valsound_opm', './data_main/idvals/valsound_opm.csv')
		idvalvalsound = globalstore.idvals.get('valsound_opm')

		if idvalvalsound:
			if valsoundid not in [None, '']:
				fm_opm_main = idvalvalsound.get_idval(valsoundid, 'opm_main')
				fm_opm_op1 = idvalvalsound.get_idval(valsoundid, 'opm_op1')
				fm_opm_op2 = idvalvalsound.get_idval(valsoundid, 'opm_op2')
				fm_opm_op3 = idvalvalsound.get_idval(valsoundid, 'opm_op3')
				fm_opm_op4 = idvalvalsound.get_idval(valsoundid, 'opm_op4')

				if fm_opm_main and  fm_opm_op1 and fm_opm_op2 and  fm_opm_op3 and fm_opm_op4: 
					vs_main = [int(x) for x in fm_opm_main.split(',')]
					vs_op1 = [int(x) for x in fm_opm_op1.split(',')]
					vs_op2 = [int(x) for x in fm_opm_op2.split(',')]
					vs_op3 = [int(x) for x in fm_opm_op3.split(',')]
					vs_op4 = [int(x) for x in fm_opm_op4.split(',')]
					vs_ops = [vs_op1, vs_op2, vs_op3, vs_op4]

					self.algorithm = vs_main[0]
					self.feedback = vs_main[1]

					for opnum, o in enumerate(self.ops):
						vs_op = vs_ops[opnum]
						o.attack_rate = vs_op[0]
						o.decay_rate = vs_op[1]
						o.sustain_rate = vs_op[2]
						o.release_rate = vs_op[3]
						o.sustain_level = vs_op[4]
						o.level = vs_op[5]
						o.ksr = vs_op[6]
						o.freqmul = vs_op[7]
						o.detune = vs_op[8]
						o.detune2 = vs_op[9]

	def to_cvpj_genid(self, convproj_obj):
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('chip', 'fm', 'opm')
		plugin_obj.role = 'synth'
		self.internal_add_params(plugin_obj)
		return plugin_obj, pluginid

	def to_cvpj(self, convproj_obj, pluginid):
		plugin_obj = convproj_obj.plugin__add(pluginid, 'chip', 'fm', 'opm')
		plugin_obj.role = 'synth'
		self.internal_add_params(plugin_obj)
		return plugin_obj

	def internal_add_params(self, plugin_obj):
		plugin_obj.params.add('algorithm', self.algorithm, 'int')
		plugin_obj.params.add('feedback', self.feedback, 'int')

		for opnum, opdata in enumerate(self.ops):
			oppv = 'op'+str(opnum)+'/'
			vnam = 'OP '+str(opnum+1)+': '

			plugin_obj.params.add(oppv+'detune2', opdata.detune2, 'int')
			plugin_obj.params.add(oppv+'detune', opdata.detune, 'int')
			plugin_obj.params.add(oppv+'freqmul', opdata.freqmul, 'int')
			plugin_obj.params.add(oppv+'level', opdata.level, 'bool')
			plugin_obj.params.add(oppv+'ksr', opdata.ksr, 'bool')
			plugin_obj.params.add(oppv+'attack_rate', opdata.attack_rate, 'bool')
			plugin_obj.params.add(oppv+'decay_rate', opdata.decay_rate, 'bool')
			plugin_obj.params.add(oppv+'sustain_rate', opdata.sustain_rate, 'int')
			plugin_obj.params.add(oppv+'release_rate', opdata.release_rate, 'int')
			plugin_obj.params.add(oppv+'sustain_level', opdata.sustain_level, 'int')

		return plugin_obj
