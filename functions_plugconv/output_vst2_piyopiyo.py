# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
import math
from functions_plugparams import params_vital
from functions_plugparams import params_vital_wavetable
from functions import plugin_vst2

def convert_inst(instdata):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']
	if pluginname == 'native-piyopiyo':
		params_vital.create()
		params_vital.setvalue('osc_1_on', 1)
		params_vital.setvalue('osc_1_level', 0.5)
		params_vital.setvalue('volume', 4000)
		params_vital.setvalue_timed('env_1_release', 20)
		params_vital.replacewave(0, params_vital_wavetable.resizewave(plugindata['wave']))

		vital_points = []
		vital_powers = []
		for pointnum in range(64):
			envpoint = plugindata['env'][pointnum]
			vital_points.append(pointnum/63)
			vital_points.append(((envpoint*-1)+128)/128)
			vital_powers.append(0.0)

		params_vital.set_lfo(1, 64, vital_points, vital_powers, False, 'PiyoPiyo')
		params_vital.setvalue('lfo_1_sync_type', 2.0)
		params_vital.set_modulation(1, 'lfo_1', 'osc_1_level', 1, 0, 1, 0, 0)

		vitaldata = params_vital.getdata()
		plugin_vst2.replace_data(instdata, 'any', 'Vital', 'chunk', vitaldata.encode('utf-8'), None)