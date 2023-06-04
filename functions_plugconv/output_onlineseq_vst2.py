# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import plugin_vst2
from functions import params_vst

def convert_fx(fxdata):
	pluginname = fxdata['plugin']
	plugindata = fxdata['plugindata']

	osnat_data = plugindata['data']
	osnat_name = plugindata['name']

	if osnat_name == 'delay':
		zamdelayparams = {}
		params_vst.add_param(zamdelayparams, 0, "Invert", 0)
		params_vst.add_param(zamdelayparams, 1, "Time", 0.019877)
		params_vst.add_param(zamdelayparams, 2, "Sync BPM", 1)
		params_vst.add_param(zamdelayparams, 3, "LPF", 1)
		params_vst.add_param(zamdelayparams, 4, "Divisor", 0.75)
		params_vst.add_param(zamdelayparams, 5, "Output Gain", 1)
		params_vst.add_param(zamdelayparams, 6, "Dry/Wet", 0.24)
		params_vst.add_param(zamdelayparams, 7, "Feedback", 0.265)
		plugin_vst2.replace_data(fxdata, 'any', 'ZamDelay', 'param', zamdelayparams, 8)

	if osnat_name == 'eq':
		threebandparams = {}
		params_vst.add_param(threebandparams, 0, "Low", (osnat_data['eq_high']/96)+0.5)
		params_vst.add_param(threebandparams, 1, "Mid", (osnat_data['eq_mid']/96)+0.5)
		params_vst.add_param(threebandparams, 2, "High", (osnat_data['eq_high']/96)+0.5)
		params_vst.add_param(threebandparams, 3, "Master", 0.5)
		params_vst.add_param(threebandparams, 4, "Low-Mid Freq", 0.22)
		params_vst.add_param(threebandparams, 5, "Mid-High Freq", 0.06)
		plugin_vst2.replace_data(fxdata, 'any', '3 Band EQ', 'param', threebandparams, 5)
