# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_plugin_ext import plugin_vst2

import io
import math

class kickmess_data:
	def __init__(self):
		self.params = {}
		self.params['pub'] = {}
		self.params['pub']['freq_start'] = 440
		self.params['pub']['freq_end'] = 440
		self.params['pub']['f_env_release'] = 1000
		self.params['pub']['dist_start'] = 0
		self.params['pub']['dist_end'] = 0
		self.params['pub']['gain'] = 0.5
		self.params['pub']['env_slope'] = 0.5
		self.params['pub']['freq_slope'] = 0.5
		self.params['pub']['noise'] = 0
		self.params['pub']['freq_note_start'] = 0.25
		self.params['pub']['freq_note_end'] = 0.25
		self.params['pub']['env_release'] = 0
		self.params['pub']['phase_offs'] = 0
		self.params['pub']['dist_on'] = 0
		self.params['pub']['f1_cutoff'] = 1
		self.params['pub']['f1_res'] = 0
		self.params['pub']['f1_drive'] = 0.2
		self.params['pub']['main_gain'] = 0.70710677
		self.params['pub']['e1_attack'] = 0.1
		self.params['pub']['e1_decay'] = 0.14142135
		self.params['pub']['e1_sustain'] = 0.75
		self.params['pub']['e1_release'] = 0.1
		self.params['priv'] = {}
		self.params['priv']['f1_type'] = 0.5
		self.params['priv']['f1_on'] = 0.25
		self.params['priv']['midi_chan'] = 0

	def set_param(self, i_cat, i_name, i_value):
		self.params[i_cat][i_name] = i_value

	def data_out(self):
		out = io.BytesIO()
		out.write(b'!PARAMS;\n')

		for paramcat in self.params:
			for paramval in self.params[paramcat]:
				o_value = self.params[paramcat][paramval]
				if paramval == 'freq_start': o_value = math.sqrt((o_value-2.51)/3000)
				if paramval == 'freq_end': o_value = math.sqrt((o_value-2.51)/2000)
				if paramval == 'f_env_release': 
					if o_value > 2.4: o_value = math.sqrt((o_value-2.51)/5000)
				out.write(str.encode(paramcat+' : '+paramval+'='+str(o_value)+';\n'))

		out.seek(0)
		return out.read()

	def to_cvpj_vst2(self, convproj_obj, plugin_obj):
		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 934843292, 'chunk', self.data_out(), None)
