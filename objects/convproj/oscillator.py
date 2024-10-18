# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from functions import data_values
from functions import data_bytes
from objects.convproj import time
from objects import audio_data
import struct
import math

class cvpj_osc_prop:
	def __init__(self):
		self.type = 'shape'
		self.shape = 'sine'
		self.pulse_width = 0.5
		self.random_type = ''
		self.nameid = ''

class cvpj_osc:
	def __init__(self):
		self.prop = cvpj_osc_prop()
		self.params = {}
		self.env = {}

class cvpj_lfo:
	def __init__(self):
		self.prop = cvpj_osc_prop()
		self.phase = 0
		self.stereo = 0
		self.time = time.cvpj_time()
		self.data = {}

		self.loop_on = True
		self.mode = 'normal'
		self.retrigger = True

		self.sustained = False

		self.env_time_real = False
		self.env_startpos = 0

		self.predelay = 0
		self.attack = 0
		self.amount = 0

class cvpj_wavetable_part:
	def __init__(self):
		self.data = {}
		self.wave_id = ''
		self.line_envid = ''
		self.audio_pos = 0
		self.audio_window_fade = 1
		self.audio_window_size = 2048

class cvpj_wavetable_parts:
	def __init__(self):
		self.data = {}

	def add_pos(self, pos):
		self.data[pos] = cvpj_wavetable_part()
		return self.data[pos]

	def items(self):
		for x in self.data.items():
			yield x

class cvpj_wavetable_modifier:
	def __init__(self):
		self.type = ''
		self.parts = {}

class cvpj_wavetable_source:
	def __init__(self):
		self.type = 'wave'
		self.parts = cvpj_wavetable_parts()
		self.data = {}
		self.fade_style = None
		self.phase_style = None
		self.blend_smooth = False
		self.blend_mode = 'normal'
		self.blend_on = False
		self.audio_id = ''
		self.audio_window_size = 2048
		self.audio_normalize_gain = False
		self.audio_normalize_mult = False
		self.retro_id = ''
		self.retro_size = 1
		self.retro_count = 0
		self.retro_pos = 0
		self.retro_time = 0.28
		self.retro_loop = 0
		self.modifiers = []

	def add_modifier(self, i_type):
		mod_obj = cvpj_wavetable_modifier()
		self.modifiers.append(mod_obj)
		return mod_obj

	def wave_add_stream_wave(self, i_values, i_size, plugin_obj, starttxt):
		self.type = 'wave'
		wave_chunks = data_values.list__chunks(i_values, i_size)
		total = (len(i_values)/i_size).__ceil__()
		for wavenum, wavedata in enumerate(wave_chunks):
			if len(wavedata) == int(i_size):
				wave_obj = plugin_obj.wave_add(starttxt+str(wavenum))
				wave_obj.set_all_range(wavedata, -1, 1)
				wt_part = self.parts.add_pos(wavenum/total)
				wt_part.wave_id = starttxt+str(wavenum)

class cvpj_wavetable:
	def __init__(self):
		self.phase = 0
		self.full_normalize = True
		self.remove_all_dc = True
		self.sources = []

		self.author = ''
		self.name = ''

	def add_source(self):
		src_obj = cvpj_wavetable_source()
		self.sources.append(src_obj)
		return src_obj