# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import ctypes

openmpt_log_func = ctypes.CFUNCTYPE(
    None, ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p
)

openmpt_error_func = ctypes.CFUNCTYPE(
    None, ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p
)

def log_callback(user_data, level, message):
    pass

def error_callback(user_data, message):
    pass

class openmpt():
	def __init__(self):
		self.error = ctypes.c_int()
		self.error_message = ctypes.c_char_p()
		self.error = ctypes.c_int()
		self.error_message = ctypes.c_char_p()
		self.ctls = ctypes.c_void_p()
		self.libopenmpt = None
		self.mod = None

	def load_lib(self):
		libloadstat = globalstore.extlib.load_native('libopenmpt', "libopenmpt")
		self.libopenmpt = globalstore.extlib.get('libopenmpt')
		if libloadstat == 1: 
			self.libopenmpt.openmpt_module_get_order_name.restype = ctypes.c_char_p
			self.libopenmpt.openmpt_module_get_pattern_name.restype = ctypes.c_char_p
			self.libopenmpt.openmpt_module_get_sample_name.restype = ctypes.c_char_p
			self.libopenmpt.openmpt_module_get_metadata_keys.restype = ctypes.c_char_p
			self.libopenmpt.openmpt_module_get_metadata.restype = ctypes.c_char_p
			self.libopenmpt.openmpt_module_get_instrument_name.restype = ctypes.c_char_p
			self.libopenmpt.openmpt_module_get_channel_name.restype = ctypes.c_char_p

	def openmpt_module_create_from_memory2(self, filedata):
		if not self.libopenmpt: exit('[error] libopenmpt not found')
		self.mod = self.libopenmpt.openmpt_module_create_from_memory2(
		filedata, len(filedata),
		openmpt_log_func(log_callback), None,
		openmpt_error_func(error_callback), None,
		ctypes.byref(self.error),ctypes.byref(self.error_message),self.ctls)

	def openmpt_module_get_channel_name(self, index):
		return self.libopenmpt.openmpt_module_get_channel_name(self.mod, index)

	def openmpt_module_get_instrument_name(self, index):
		return self.libopenmpt.openmpt_module_get_instrument_name(self.mod, index)

	def openmpt_module_get_metadata_keys(self):
		return self.libopenmpt.openmpt_module_get_metadata_keys(self.mod).decode().split(';')

	def openmpt_module_get_metadata(self, key):
		return self.libopenmpt.openmpt_module_get_metadata(self.mod, key).decode()

	def openmpt_module_get_num_channels(self):
		return self.libopenmpt.openmpt_module_get_num_channels(self.mod)

	def openmpt_module_get_num_instruments(self):
		return self.libopenmpt.openmpt_module_get_num_instruments(self.mod)

	def openmpt_module_get_num_orders(self):
		return self.libopenmpt.openmpt_module_get_num_orders(self.mod)

	def openmpt_module_get_num_patterns(self):
		return self.libopenmpt.openmpt_module_get_num_patterns(self.mod)

	def openmpt_module_get_num_samples(self):
		return self.libopenmpt.openmpt_module_get_num_samples(self.mod)

	def openmpt_module_get_num_subsongs(self):
		return self.libopenmpt.openmpt_module_get_num_subsongs(self.mod)

	def openmpt_module_get_order_name(self, index):
		return self.libopenmpt.openmpt_module_get_order_name(self.mod, index)

	def openmpt_module_get_order_pattern(self, order):
		return self.libopenmpt.openmpt_module_get_order_pattern(self.mod, order)

	def openmpt_module_get_pattern_name(self, index):
		return self.libopenmpt.openmpt_module_get_pattern_name(self.mod, index)

	def openmpt_module_get_pattern_num_rows(self, pattern):
		return self.libopenmpt.openmpt_module_get_pattern_num_rows(self.mod, pattern)

	def openmpt_module_get_pattern_row_channel_command(self, pattern, row, channel, command):
		return self.libopenmpt.openmpt_module_get_pattern_row_channel_command(self.mod, pattern, row, channel, command)

	def openmpt_module_get_sample_name(self, index):
		return self.libopenmpt.openmpt_module_get_sample_name(self.mod, index)

	def get_metadata(self):
		outdata = {}
		for key in self.openmpt_module_get_metadata_keys(): outdata[key] = self.libopenmpt.openmpt_module_get_metadata(self.mod, key.encode()).decode()
		return outdata

	def get_orderlist(self):
		return [self.libopenmpt.openmpt_module_get_order_pattern(self.mod, n) for n in range(self.libopenmpt.openmpt_module_get_num_orders(self.mod))]

	def get_patnote(self, pattern, row, channel):
		return [self.libopenmpt.openmpt_module_get_pattern_row_channel_command(self.mod, pattern, row, channel, n) for n in range(6)]