# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib
import json

from functions import audio_wav
from functions import plugin_vst2
from functions import data_bytes

from functions_plugparams import params_various_inst
from functions_plugparams import data_vc2xml

vrc7patch = {}
vrc7patch[1] = [3,33,5,6,232,129,66,39]
vrc7patch[2] = [19,65,20,13,216,246,35,18]
vrc7patch[3] = [17,17,8,8,250,178,32,18]
vrc7patch[4] = [49,97,12,7,168,100,97,39]
vrc7patch[5] = [50,33,30,6,225,118,1,40]
vrc7patch[6] = [2,1,6,0,163,226,244,244]
vrc7patch[7] = [33,97,29,7,130,129,17,7]
vrc7patch[8] = [35,33,34,23,162,114,1,23]
vrc7patch[9] = [53,17,37,0,64,115,114,1]
vrc7patch[10] = [181,1,15,15,168,165,81,2]
vrc7patch[11] = [23,193,36,7,248,248,34,18]
vrc7patch[12] = [113,35,17,6,101,116,24,22]
vrc7patch[13] = [1,2,211,5,201,149,3,2]
vrc7patch[14] = [97,99,12,0,148,192,51,246]
vrc7patch[15] = [33,114,13,0,193,213,86,6]

def convert_inst(instdata, out_daw):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']

	if pluginname in ['retro', '2a03', 'vrc6', 'mmc5', 'sunsoft_5b']:
		params_various_inst.m8bp_init()

		if 'env_arp' in plugindata:
			params_various_inst.m8bp_setvalue("isPitchSequenceEnabled_raw", 1.0)
			params_various_inst.m8bp_setenv('pitch', plugindata['env_arp']['values'])

		if 'env_duty' in plugindata:
			params_various_inst.m8bp_setvalue("isDutySequenceEnabled_raw", 1.0)
			params_various_inst.m8bp_setenv('duty', plugindata['env_duty']['values'])

		if 'env_vol' in plugindata:
			params_various_inst.m8bp_setvalue("isVolumeSequenceEnabled_raw", 1.0)
			params_various_inst.m8bp_setenv('volume', plugindata['env_vol']['values'])

		if 'wave' in plugindata:
			if plugindata['wave'] == 'square': params_various_inst.m8bp_setvalue("osc", 0.0)
			if plugindata['wave'] == 'triangle': params_various_inst.m8bp_setvalue("osc", 1.0)
			if plugindata['wave'] == 'noise': params_various_inst.m8bp_setvalue("osc", 2.0)

		plugin_vst2.replace_data(instdata, 'any', 'Magical 8bit Plug 2', 'chunk', data_vc2xml.make(params_various_inst.m8bp_out()), None)

	if pluginname == 'opn2':
		xmlout = params_various_inst.opnplug_convert(plugindata)
		plugin_vst2.replace_data(instdata, 'any', 'OPNplug', 'chunk', data_vc2xml.make(xmlout), None)

	if pluginname == 'opl2':

		opl2_car = plugindata['op1']
		opl2_mod = plugindata['op2']
		print(plugindata)

		outputjson = {}

		outputjson['Program_Index'] = 0
		outputjson['Carrier_Wave'] = float(opl2_car['waveform']/7)
		outputjson['Modulator_Wave'] = float(opl2_mod['waveform']/7)
		outputjson['Carrier_Frequency_Multiplier'] = opl2_car['freqmul']/15
		outputjson['Modulator_Frequency_Multiplier'] = opl2_mod['freqmul']/15
		outputjson['Carrier_Attenuation'] = 0.0
		outputjson['Modulator_Attenuation'] = 0.0
		outputjson['Tremolo_Depth'] = plugindata['tremolo_depth']
		outputjson['Vibrato_Depth'] = plugindata['vibrato_depth']
		outputjson['Carrier_Tremolo'] = opl2_car['tremolo']
		outputjson['Carrier_Vibrato'] = opl2_car['vibrato']
		outputjson['Carrier_Sustain'] = 0.0
		outputjson['Carrier_Keyscale_Rate'] = opl2_car['ksr']
		outputjson['Modulator_Tremolo'] = opl2_mod['tremolo']
		outputjson['Modulator_Vibrato'] = opl2_mod['vibrato']
		outputjson['Modulator_Sustain'] = 0.0
		outputjson['Modulator_Keyscale_Rate'] = opl2_mod['ksr']
		outputjson['Carrier_Keyscale_Level'] = 0.0
		outputjson['Modulator_Keyscale_Level'] = 0.0
		outputjson['Algorithm'] = (plugindata['fm']*-1)+1
		outputjson['Modulator_Feedback'] = plugindata['feedback']/7
		outputjson['Carrier_Attack'] = opl2_car['env_attack']/15
		outputjson['Carrier_Decay'] = opl2_car['env_decay']/15
		outputjson['Carrier_Sustain_Level'] = opl2_car['env_sustain']/15
		outputjson['Carrier_Release'] = opl2_car['env_release']/15
		outputjson['Modulator_Attack'] = opl2_mod['env_attack']/15
		outputjson['Modulator_Decay'] = opl2_mod['env_decay']/15
		outputjson['Modulator_Sustain_Level'] = opl2_mod['env_sustain']/15
		outputjson['Modulator_Release'] = opl2_mod['env_release']/15
		outputjson['Carrier_Velocity_Sensitivity'] = 0.0
		outputjson['Modulator_Velocity_Sensitivity'] = 0.0
		outputjson['Emulator'] = 0.0
		if 'perctype' in plugindata: outputjson['Percussion_Mode'] = float(plugindata['perctype']/5)
		else: outputjson['Percussion_Mode'] = 0.0
		outputjson['lastLoadFile'] = ""
		outputjson['selectedIdxFile'] = -1

		oplvstbytes = json.dumps(outputjson, indent=2).replace("\n", "\r\n").encode('ascii')
		print(oplvstbytes)

		plugin_vst2.replace_data(instdata, 'any', 'OPL', 'chunk', oplvstbytes, None)
