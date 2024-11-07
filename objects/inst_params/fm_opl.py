# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class opl_op:
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

class opl_inst:
	def __init__(self):
		self.name = ''
		self.name_long = ''

		self.version = 3
		self.vel_offset = 0
		self.is_blank = False

		self.perc_key = 0
		self.perc_on = False
		self.perc_type = 0
		self.perc_voicenum = 0

		self.pseudo4 = False
		self.key_offs1 = 0
		self.key_offs2 = 0
		self.second_detune = 0

		self.ms_on = 0
		self.ms_off = 0

		self.tremolo_depth = False
		self.vibrato_depth = False
		self.fm_1 = False
		self.fm_2 = False
		self.feedback_1 = 0
		self.feedback_2 = 0
		self.numops = 4
		self.ops = [opl_op() for _ in range(4)]
		
	def fmfb1(self, inval):
		self.fm_1 = bool(inval&1)
		self.feedback_1 = inval>>1

	def fmfb2(self, inval):
		self.fm_2 = bool(inval&1)
		self.feedback_2 = inval>>1

	def set_opl2(self):
		self.version = 2
		self.numops = 2
		self.pseudo4 = False

	def to_cvpj_genid(self, convproj_obj):
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('chip', 'fm', 'opl'+str(self.version))
		plugin_obj.role = 'synth'
		self.internal_add_params(plugin_obj)
		return plugin_obj, pluginid

	def to_cvpj(self, convproj_obj, pluginid):
		plugin_obj = convproj_obj.plugin__add(pluginid, 'chip', 'fm', 'opl'+str(self.version))
		plugin_obj.role = 'synth'
		self.internal_add_params(plugin_obj)
		return plugin_obj

	def internal_add_params(self, plugin_obj):
		plugin_obj.params.add('vel_offset', self.vel_offset, 'int')

		plugin_obj.params.add('perc_key', self.perc_key, 'int')
		plugin_obj.params.add('perc_on', self.perc_on, 'bool')
		plugin_obj.params.add('perc_type', self.perc_type, 'int')
		plugin_obj.params.add('perc_voicenum', self.perc_voicenum, 'int')

		plugin_obj.params.add('pseudo4', self.pseudo4, 'int')
		plugin_obj.params.add('key_offs1', self.key_offs1, 'int')
		plugin_obj.params.add('key_offs2', self.key_offs2, 'int')
		plugin_obj.params.add('second_detune', self.second_detune, 'int')

		plugin_obj.params.add('ms_on', self.ms_on, 'int')
		plugin_obj.params.add('ms_off', self.ms_off, 'int')

		plugin_obj.params.add('tremolo_depth', self.tremolo_depth, 'bool')
		plugin_obj.params.add('vibrato_depth', self.vibrato_depth, 'bool')
		plugin_obj.params.add('fm_1', self.fm_1, 'bool')
		plugin_obj.params.add('fm_2', self.fm_2, 'bool')
		plugin_obj.params.add('feedback_1', self.feedback_1, 'int')
		plugin_obj.params.add('feedback_2', self.feedback_2, 'int')

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

			plugin_obj.params.add(oppv+'level', opdata.level, 'int')
			plugin_obj.params.add(oppv+'ksl', opdata.ksl, 'int')
			plugin_obj.params.add(oppv+'waveform', opdata.waveform, 'int')

		return plugin_obj
