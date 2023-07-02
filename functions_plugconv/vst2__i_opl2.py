# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import plugin_vst2
from functions import plugins
from functions_plugparams import data_vc2xml
import math
import json
import struct
import xml.etree.ElementTree as ET

def getparam(paramname):
	global pluginid_g
	global cvpj_l_g
	paramval = plugins.get_plug_param(cvpj_l_g, pluginid_g, paramname, 0)
	return paramval[0]

def convert(cvpj_l, pluginid, plugintype):
	global pluginid_g
	global cvpj_l_g
	pluginid_g = pluginid
	cvpj_l_g = cvpj_l

	outputjson = {}

	outputjson['Algorithm'] = (getparam('fm')*-1)+1
	outputjson['Carrier_Attack'] = ((getparam('op1_env_attack')/15)*-1)+1
	outputjson['Carrier_Attenuation'] = 0.0
	outputjson['Carrier_Decay'] = ((getparam('op1_env_decay')/15)*-1)+1
	outputjson['Carrier_Frequency_Multiplier'] = ((getparam('op1_freqmul')/15)*-1)+1
	outputjson['Carrier_Keyscale_Level'] = 0.0
	outputjson['Carrier_Keyscale_Rate'] = getparam('op1_ksr')
	outputjson['Carrier_Release'] = ((getparam('op1_env_release')/15)*-1)+1
	outputjson['Carrier_Sustain'] = 0.0
	outputjson['Carrier_Sustain_Level'] = ((getparam('op1_env_sustain')/15)*-1)+1
	outputjson['Carrier_Tremolo'] = getparam('op1_tremolo')
	outputjson['Carrier_Velocity_Sensitivity'] = 0.0
	outputjson['Carrier_Vibrato'] = getparam('op1_vibrato')
	outputjson['Carrier_Wave'] = float(getparam('op1_waveform')/7)
	outputjson['Emulator'] = 0.0
	outputjson['lastLoadFile'] = ""
	outputjson['Modulator_Attack'] = ((getparam('op2_env_attack')/15)*-1)+1
	outputjson['Modulator_Attenuation'] = 0.0
	outputjson['Modulator_Decay'] = ((getparam('op2_env_decay')/15)*-1)+1
	outputjson['Modulator_Feedback'] = getparam('feedback')/7
	outputjson['Modulator_Frequency_Multiplier'] = ((getparam('op2_freqmul')/15)*-1)+1
	outputjson['Modulator_Keyscale_Level'] = 0.0
	outputjson['Modulator_Keyscale_Rate'] = getparam('op2_ksr')
	outputjson['Modulator_Release'] = ((getparam('op2_env_release')/15)*-1)+1
	outputjson['Modulator_Sustain'] = 0.0
	outputjson['Modulator_Sustain_Level'] = ((getparam('op2_env_sustain')/15)*-1)+1
	outputjson['Modulator_Tremolo'] = getparam('op2_tremolo')
	outputjson['Modulator_Velocity_Sensitivity'] = 0.0
	outputjson['Modulator_Vibrato'] = getparam('op2_vibrato')
	outputjson['Modulator_Wave'] = float(getparam('op2_waveform')/7)
	outputjson['Percussion_Mode'] = float(getparam('perctype')/5)
	outputjson['Program_Index'] = 0
	outputjson['selectedIdxFile'] = -1
	outputjson['Tremolo_Depth'] = getparam('tremolo_depth')
	outputjson['Vibrato_Depth'] = getparam('vibrato_depth')

	oplvstbytes = json.dumps(outputjson, indent=2).replace("\n", "\r\n").encode('ascii')

	plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'JuceOPLVSTi', 'chunk', oplvstbytes, None)
	return True