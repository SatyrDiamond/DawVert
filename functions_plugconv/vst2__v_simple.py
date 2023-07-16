# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
from functions import plugin_vst2

def convert(cvpj_l, pluginid, plugintype):

	if plugintype[1] == 'reverb': 
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Reverb', 'chunk', struct.pack('<ff', 0.5, 0.5), None)
		return True
	if plugintype[1] == 'reverb-send': 
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Reverb', 'chunk', struct.pack('<ff', 0.5, 1), None)
		return True

	if plugintype[1] == 'chorus': 
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'ChorusEnsemble', 'chunk', struct.pack('<fff', 0.5, 0.5, 0.5), None)
		return True
	if plugintype[1] == 'chorus-send': 
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'ChorusEnsemble', 'chunk', struct.pack('<fff', 0.5, 0.5, 1), None)
		return True
	
	if plugintype[1] == 'tremelo': 
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Tremolo', 'chunk', struct.pack('<ff', 0.5, 0.5), None)
		return True