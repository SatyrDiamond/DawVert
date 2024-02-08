# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import data_nullbytegroup

class dragonfly_hall_data:
	def __init__(self):
		self.params = {}
		self.params['dry_level'] = 100
		self.params['early_level'] = 0
		self.params['early_send'] = 25
		self.params['late_level'] = 0

		self.params['size'] = 24
		self.params['width'] = 100
		self.params['delay'] = 0
		self.params['diffuse'] = 0

		self.params['low_cut'] = 0
		self.params['low_xo'] = 200
		self.params['low_mult'] = 1

		self.params['high_cut'] = 16000
		self.params['high_xo'] = 16000
		self.params['high_mult'] = 0.2

		self.params['spin'] = 0
		self.params['wander'] = 0
		self.params['decay'] = 1
		self.params['modulation'] = 0

	def set_param(self, name, value):
		self.params[name] = value
	
	def to_cvpj_vst2(self, convproj_obj, plugin_obj):
		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name', 'any', 'Dragonfly Hall Reverb', 'chunk', data_nullbytegroup.make([{'preset': 'Small Dark Hall'}, self.params]), None)