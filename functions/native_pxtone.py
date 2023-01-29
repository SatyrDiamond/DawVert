# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
from functions import data_bytes
from functions import list_vst
from functions import params_vst
from functions import params_vital
from functions import params_vital_wavetable

def convert(instdata):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']
	if plugindata['name'] == 'ptvoice':
		unit_num = 1
		params_vital.create()
		for unitdata in plugindata['data']['units']:

			ptv_vol = unitdata['vol']
			ptv_pan = unitdata['pan']
			ptv_detune = unitdata['detune']
			ptv_release = unitdata['release']
			ptv_vol_points = unitdata['vol_points']

			ptv_wave_type = unitdata['wave_type']
			if ptv_wave_type == 'points': 
				ptv_wave_data = unitdata['wave_points']
				ptv_wave_data.append([255, ptv_wave_data[0][1]])
				wavetable = []
				for num in range(len(ptv_wave_data)-1):
					if ptv_wave_data[num][0] != ptv_wave_data[num+1][0]:
						pos_start, val_start = ptv_wave_data[num]
						pos_end, val_end = ptv_wave_data[num+1]
						duration = int(pos_end-pos_start)
						for samplenum in range(duration):
							valbetween = samplenum/duration
							wavetable.append((val_start*(1-valbetween)) + (val_end*valbetween)) 
				params_vital.replacewave(unit_num, params_vital_wavetable.resizewave(wavetable))

			if ptv_wave_type == 'harm': 
				ptv_wave_data = unitdata['wave_harm']
				wavetable = []
				for num in range(2048):
					s_pos = num/2048
					sample = 0
					for harm_num in range(31):
						sine_add = 0
						sine_pitch = s_pos*(harm_num+1)
						sine_vol = ptv_wave_data[harm_num]/(harm_num+1)
						sample += params_vital_wavetable.wave_sine(sine_pitch+sine_add)*sine_vol
					wavetable.append(sample)
				params_vital.replacewave(unit_num, wavetable)

			params_vital.setvalue('osc_'+str(unit_num)+'_on', 1)
			params_vital.setvalue('osc_'+str(unit_num)+'_tune', ptv_detune/100)
			params_vital.setvalue('osc_'+str(unit_num)+'_pan', ptv_pan)
			params_vital.setvalue('env_'+str(unit_num)+'_attack', 0)
			params_vital.setvalue('env_'+str(unit_num)+'_decay', 0)
			params_vital.setvalue('env_'+str(unit_num)+'_sustain', 1)
			params_vital.setvalue('env_'+str(unit_num)+'_release', ptv_release/1000)
			params_vital.setvalue('env_'+str(unit_num)+'_release_power', 0)

			unit_num += 1

		vitaldata = params_vital.getdata()
		list_vst.replace_data(instdata, 'Vital', vitaldata.encode('utf-8'))
