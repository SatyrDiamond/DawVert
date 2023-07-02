# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
from functions import plugin_vst2
from functions import plugins

def convert(cvpj_l, pluginid, plugintype):

	if plugintype[1] == 'distort':
		distlevel = 0.5
		distort_type = plugins.get_plug_param(cvpj_l, pluginid, 'distort_type', 0)[0]
		if distort_type == [10, 6]: distlevel = 0.3
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Density2', 'chunk', struct.pack('<ffff', distlevel, 0, 1, 1), None)
		return True

	if plugintype[1] == 'delay':
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'ZamDelay', 'param', None, 8)
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_0', 0, 'float', "Invert")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_1', 0.019877, 'float', "Time")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_2', 1, 'float', "Sync BPM")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_3', 1, 'float', "LPF")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_4', 0.75, 'float', "Divisor")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_5', 1, 'float', "Output Gain")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_6', 0.24, 'float', "Dry/Wet")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_7', 0.265, 'float', "Feedback")
		return True

	elif plugintype[1] == 'eq':
		eq_high = plugins.get_plug_param(cvpj_l, pluginid, 'eq_high', 0)[0]
		eq_mid = plugins.get_plug_param(cvpj_l, pluginid, 'eq_mid', 0)[0]
		eq_high = plugins.get_plug_param(cvpj_l, pluginid, 'eq_high', 0)[0]
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', '3 Band EQ', 'param', None, 6)
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_0', (eq_high/96)+0.5, 'float', "Low")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_1', (eq_mid/96)+0.5, 'float', "Mid")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_2', (eq_high/96)+0.5, 'float', "High")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_3', 0.5, 'float', "Master")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_4', 0.22, 'float', "Low-Mid Freq")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_5', 0.3, 'float', "Mid-High Freq")
		return True
