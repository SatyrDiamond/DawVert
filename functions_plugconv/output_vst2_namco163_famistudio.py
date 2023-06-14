# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
import math
from functions_plugparams import params_vital
from functions_plugparams import params_vital_wavetable
from functions import data_bytes
from functions import data_values
from functions import params_vst
from functions import plugin_vst2

def convert_inst(instdata):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']

	if pluginname == 'namco163_famistudio':
		namco163_wave = plugindata['wave']
		namco163_values = namco163_wave['values']
		namco163_loop = 0
		namco163_size = int(namco163_wave['size'])
		namco163_pos = int(namco163_wave['pos'])
		namco163_count = int(namco163_wave['count'])
		if 'loop' in namco163_wave: namco163_loop = int(namco163_wave['loop'])

		params_vital.create()
		params_vital.setvalue('osc_1_on', 1)
		params_vital.setvalue('osc_1_level', 0.5)
		params_vital.setvalue('osc_1_wave_frame', 128)
		params_vital.setvalue_timed('env_1_release', 0)

		params_vital.set_lfo(1, 2, [0, 1, 1, 0], [0, 0], False, '')
		params_vital.setvalue('lfo_1_frequency', 1.8)
		params_vital.setvalue('lfo_1_phase', namco163_loop/(namco163_size*namco163_count))
		params_vital.setvalue('lfo_1_sync', 0.0)
		params_vital.setvalue('lfo_1_sync_type', 4.0)
		params_vital.set_modulation(1, 'lfo_1', 'osc_1_wave_frame', 1, 0, 1, 0, 0)

		vital_points = []
		vital_powers = []
		if 'env_vol' in plugindata:
			vol163env = plugindata['env_vol']['values']
			vol163envlen = len(vol163env)

			params_vital.setvalue('lfo_2_frequency', pow(2, 1/(vol163envlen*0.8) ))
			params_vital.setvalue('lfo_2_sync', 0.0)
			params_vital.setvalue('lfo_2_sync_type', 2.0)

			for pointnum in range(vol163envlen):
				vital_points.append(pointnum/vol163envlen)
				vital_points.append(((vol163env[pointnum]*-1)+15)/15)
				vital_powers.append(0.0)
			params_vital.set_lfo(2, vol163envlen+1, vital_points+[1,1], vital_powers+[0], False, '')
			params_vital.set_modulation(2, 'lfo_2', 'osc_1_level', 1, 0, 1, 0, 0)

		namco163_wave_chunks = data_values.list_chunks(namco163_values, int(namco163_size))

		vital_keyframes = {}
		for chunknum in range(namco163_count):
			vital_keyframes[int((chunknum/namco163_count)*256)] = params_vital_wavetable.resizewave(namco163_wave_chunks[chunknum])

		params_vital.replacemultiwave(0, vital_keyframes)

		vitaldata = params_vital.getdata()
		plugin_vst2.replace_data(instdata, 'any', 'Vital', 'chunk', vitaldata.encode('utf-8'), None)