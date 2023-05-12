# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
from functions import plugin_vst2
from functions import params_vst

def convert_fx(fxdata):
	pluginname = fxdata['plugin']
	plugindata = fxdata['plugindata']

	osnat_data = plugindata['data']
	osnat_name = plugindata['name']

	if osnat_name == 'reverb': plugin_vst2.replace_data(fxdata, 'any', 'Reverb', 'chunk', struct.pack('<ff', 0.5, 0.5), None)
	if osnat_name == 'reverb-send': plugin_vst2.replace_data(fxdata, 'any', 'Reverb', 'chunk', struct.pack('<ff', 0.5, 1), None)

	if osnat_name == 'chorus': plugin_vst2.replace_data(fxdata, 'any', 'ChorusEnsemble', 'chunk', struct.pack('<fff', 0.5, 0.5, 0.5), None)
	if osnat_name == 'chorus-send': plugin_vst2.replace_data(fxdata, 'any', 'ChorusEnsemble', 'chunk', struct.pack('<fff', 0.5, 0.5, 1), None)
	
	if osnat_name == 'tremelo': plugin_vst2.replace_data(fxdata, 'any', 'Tremolo', 'chunk', struct.pack('<ff', 0.5, 0.5), None)