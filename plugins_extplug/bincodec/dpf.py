# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins_extplug
import sys
from objects.data_bytes import bytewriter

class dpf_params():
	def __init__(self):
		self.dpf_state = {}
		self.dpf_params = {}

class plugin_extplug(plugins_extplug.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'bincodec'
	def get_shortname(self): return 'dpf'
	def get_prop(self, in_dict): pass

	def data_create(self): 
		return dpf_params()

	def data_decode(self, byr_stream, exttype, params): 
		dpf_obj = dpf_params()
		cur_state = None
		if exttype == 'vst2':
			cur_state = 'state'
			while byr_stream.remaining():
				d = byr_stream.string_t()
				if d:
					v = byr_stream.string_t()
					if cur_state == 'state': dpf_obj.dpf_state[d] = v
					if cur_state == 'parameters': dpf_obj.dpf_params[d] = v
				else:
					if cur_state == 'parameters': break
					if cur_state == 'state': cur_state = 'parameters'
			return dpf_obj
		if exttype == 'vst3':
			while byr_stream.remaining():
				d = byr_stream.string_t()
				if d == '__dpf_state_begin__': cur_state = 'state'
				elif d == '__dpf_state_end__': cur_state = None
				elif d == '__dpf_parameters_begin__': cur_state = 'parameters'
				elif d == '__dpf_parameters_end__': 
					cur_state = None
					break
				elif cur_state:
					v = byr_stream.string_t()
					if cur_state == 'state': dpf_obj.dpf_state[d] = v
					if cur_state == 'parameters': dpf_obj.dpf_params[d] = v

			return dpf_obj

	def data_encode(self, out_obj, exttype, params): 
		byw_stream = bytewriter.bytewriter()
		if exttype == 'vst2':
			for n, v in out_obj.dpf_state.items():
				byw_stream.string_t(n)
				byw_stream.string_t(str(v))
			byw_stream.string_t('')
			for n, v in out_obj.dpf_params.items():
				byw_stream.string_t(n)
				byw_stream.string_t(str(v))
			byw_stream.string_t('')
		if exttype == 'vst3':
			byw_stream.string_t('__dpf_state_begin__')
			for n, v in out_obj.dpf_state.items():
				byw_stream.string_t(n)
				byw_stream.string_t(str(v))
			byw_stream.string_t('__dpf_state_end__')
			byw_stream.string_t('__dpf_parameters_begin__')
			for n, v in out_obj.dpf_params.items():
				byw_stream.string_t(n)
				byw_stream.string_t(str(v))
			byw_stream.string_t('__dpf_parameters_end__')
		return byw_stream.getvalue()