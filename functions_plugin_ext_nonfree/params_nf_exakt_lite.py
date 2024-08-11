# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_plugin_ext import plugin_vst2
from objects.data_bytes import dv_datadef

class exakt_lite_env:
	def __init__(self):
		self.point1_lvl = 0
		self.point2_lvl = 1
		self.point3_lvl = 1
		self.point4_lvl = 0
		self.point1_time = 0
		self.point2_time = 1
		self.point3_time = 1
		self.point4_time = 0
		self.sustain = False

	def out(self):
		return {
		"point0_lvl_end": self.point2_lvl,
		"point0_time": 0.0,
		"point0_unk": 1.0,
		"point1_lvl_start": self.point2_lvl,
		"point1_lvl_end": self.point3_lvl,
		"point1_time": self.point1_time,
		"point2_lvl_start": self.point3_lvl,
		"point2_lvl_end": self.point4_lvl,
		"point2_time": self.point2_time,
		"point2_unk": 1.0,
		"point3_lvl_start": self.point4_lvl,
		"point3_lvl_end": 0.0,
		"point3_time": self.point3_time,
		"point4_time": self.point4_time,
		"point4_unk": 1.0,
		"sustain": int(self.sustain),
		"unk1": 2,
		"unk2": 4
		}

class exakt_lite_op_params:
	def __init__(self):
		self.detune = 0
		self.invert = 0
		self.level = 0
		self.offset = 0.13
		self.pan = 0
		self.phase = 0
		self.rate = 1.0
		self.shape = 0
		self.vel_sens = 0

	def out(self):
		return {
		"detune": self.detune,
		"invert": self.invert,
		"level": self.level,
		"offset": self.offset,
		"pan": self.pan,
		"phase": self.phase,
		"rate": self.rate,
		"shape": self.shape,
		"vel_sens": self.vel_sens
		}

class exakt_lite_lfo:
	def __init__(self):
		self.lfo_cutoff = 0
		self.lfo_depth = 1.0
		self.lfo_free = 0.01
		self.lfo_level_a = 0
		self.lfo_level_b = 0
		self.lfo_level_c = 0
		self.lfo_level_d = 0
		self.lfo_pitch = 0
		self.lfo_rate_free = 0
		self.lfo_rate_sync = 0
		self.lfo_shape = 0
		self.lfo_sync = 0

	def out(self):
		return {
		"lfo_cutoff": self.lfo_cutoff,
		"lfo_depth": self.lfo_depth,
		"lfo_free": self.lfo_free,
		"lfo_level_a": self.lfo_level_a,
		"lfo_level_b": self.lfo_level_b,
		"lfo_level_c": self.lfo_level_c,
		"lfo_level_d": self.lfo_level_d,
		"lfo_pitch": self.lfo_pitch,
		"lfo_rate_free": self.lfo_rate_free,
		"lfo_rate_sync": self.lfo_rate_sync,
		"lfo_shape": self.lfo_shape,
		"lfo_sync": self.lfo_sync
		}

class exakt_lite_filter:
	def __init__(self):
		self.amount = 0
		self.cutoff = 50.0
		self.reso = 0
		self.type = 0
		self.vel_sens = 0

	def out(self):
		return {
		"amount": self.amount,
		"cutoff": self.cutoff,
		"reso": self.reso,
		"type": self.type,
		"vel_sens": self.vel_sens
		}

class exakt_lite_data:
	def __init__(self):
		self.params = {}
		self.algo = 0
		self.feedback = 0
		self.gain = 100
		self.name = 'DawVert'
	
		self.lfo = exakt_lite_lfo()
		self.filter = exakt_lite_filter()

		self.filter_env = exakt_lite_env()
		self.op1_env = exakt_lite_env()
		self.op2_env = exakt_lite_env()
		self.op3_env = exakt_lite_env()
		self.op4_env = exakt_lite_env()

		self.op1_params = exakt_lite_op_params()
		self.op2_params = exakt_lite_op_params()
		self.op3_params = exakt_lite_op_params()
		self.op4_params = exakt_lite_op_params()

	def out(self):
		return {
		"algo": self.algo,
		"feedback": self.feedback,
		"filter": self.filter.out(),
		"filter_env": self.filter_env.out(),
		"gain": self.gain,
		"header": 1885759092,
		"lfo": self.lfo.out(),
		"name": self.name,
		"op1_env": self.op1_env.out(),
		"op1_params": self.op1_params.out(),
		"op2_env": self.op2_env.out(),
		"op2_params": self.op2_params.out(),
		"op3_env": self.op3_env.out(),
		"op3_params": self.op3_params.out(),
		"op4_env": self.op4_env.out(),
		"op4_params": self.op4_params.out(),
		"unknown_0": 0,
		"unknown_1": 0,
		"unknown_2": 1,
		"unknown_3": 0,
		"unknown_4": 1,
		"unknown_5": 4,
		"unknown_6": 1,
		"unknown_7": 0
		}

	def to_cvpj_vst2(self, convproj_obj, plugin_obj):
		datadef = dv_datadef.datadef('./data_main/datadef/plugin_vst2/exakt_lite.ddef')
		datadef.create('main', self.out())
		outdata = datadef.bytestream.getvalue()
		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1349337720, 'chunk', datadef.bytestream.getvalue(), None)
		plugin_obj.datavals.add('current_program', 0)