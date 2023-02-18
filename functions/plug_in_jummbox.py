# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
from functions import data_bytes
from functions import list_vst
from functions import params_vst
from functions import params_vital
from functions import params_vital_wavetable

rawChipWaves = {}
rawChipWaves["rounded"] = {"expression": 0.94, "samples": [0,0.2,0.4,0.5,0.6,0.7,0.8,0.85,0.9,0.95,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0.95,0.9,0.85,0.8,0.7,0.6,0.5,0.4,0.2,0,-0.2,-0.4,-0.5,-0.6,-0.7,-0.8,-0.85,-0.9,-0.95,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-0.95,-0.9,-0.85,-0.8,-0.7,-0.6,-0.5,-0.4,-0.2]}
rawChipWaves["triangle"] = {"expression": 1, "samples": [1/15,0.2,5/15,7/15,0.6,11/15,13/15,1,1,13/15,11/15,0.6,7/15,5/15,0.2,1/15,-1/15,-0.2,-5/15,-7/15,-0.6,-11/15,-13/15,-1,-1,-13/15,-11/15,-0.6,-7/15,-5/15,-0.2,-1/15]}
rawChipWaves["square"] = {"expression": 0.5, "samples": [1,-1]}
rawChipWaves["1/4 pulse"] = {"expression": 0.5, "samples": [1,-1,-1,-1]}
rawChipWaves["1/8 pulse"] = {"expression": 0.5, "samples": [1,-1,-1,-1,-1,-1,-1,-1]}
rawChipWaves["sawtooth"] = {"expression": 0.65, "samples": [1/31,3/31,5/31,7/31,9/31,11/31,13/31,15/31,17/31,19/31,21/31,23/31,25/31,27/31,29/31,1,-1,-29/31,-27/31,-25/31,-23/31,-21/31,-19/31,-17/31,-15/31,-13/31,-11/31,-9/31,-7/31,-5/31,-3/31,-1/31]}
rawChipWaves["double saw"] = {"expression": 0.5, "samples": [0,-0.2,-0.4,-0.6,-0.8,-1,1,-0.8,-0.6,-0.4,-0.2,1,0.8,0.6,0.4,0.2]}
rawChipWaves["double pulse"] = {"expression": 0.4, "samples": [1,1,1,1,1,-1,-1,-1,1,1,1,1,-1,-1,-1,-1]}
rawChipWaves["spiky"] = {"expression": 0.4, "samples": [1,-1,1,-1,1,0]}
rawChipWaves["sine"] = {"expression": 0.88, "samples": [8,9,11,12,13,14,15,15,15,15,14,14,13,11,10,9,7,6,4,3,2,1,0,0,0,0,1,1,2,4,5,6]}
rawChipWaves["flute"] = {"expression": 0.8, "samples": [3,4,6,8,10,11,13,14,15,15,14,13,11,8,5,3]}
rawChipWaves["harp"] = {"expression": 0.8, "samples": [0,3,3,3,4,5,5,6,7,8,9,11,11,13,13,15,15,14,12,11,10,9,8,7,7,5,4,3,2,1,0,0]}
rawChipWaves["sharp clarinet"] = {"expression": 0.38, "samples": [0,0,0,1,1,8,8,9,9,9,8,8,8,8,8,9,9,7,9,9,10,4,0,0,0,0,0,0,0,0,0,0]}
rawChipWaves["soft clarinet"] = {"expression": 0.45, "samples": [0,1,5,8,9,9,9,9,9,9,9,11,11,12,13,12,10,9,7,6,4,3,3,3,1,1,1,1,1,1,1,1]}
rawChipWaves["alto sax"] = {"expression": 0.3, "samples": [5,5,6,4,3,6,8,7,2,1,5,6,5,4,5,7,9,11,13,14,14,14,14,13,10,8,7,7,4,3,4,2]}
rawChipWaves["bassoon"] = {"expression": 0.35, "samples": [9,9,7,6,5,4,4,4,4,5,7,8,9,10,11,13,13,11,10,9,7,6,4,2,1,1,1,2,2,5,11,14]}
rawChipWaves["trumpet"] = {"expression": 0.22, "samples": [10,11,8,6,5,5,5,6,7,7,7,7,6,6,7,7,7,7,7,6,6,6,6,6,6,6,6,7,8,9,11,14]}
rawChipWaves["electric guitar"] = {"expression": 0.2, "samples": [11,12,12,10,6,6,8,0,2,4,8,10,9,10,1,7,11,3,6,6,8,13,14,2,0,12,8,4,13,11,10,13]}
rawChipWaves["organ"] = {"expression": 0.2, "samples": [11,10,12,11,14,7,5,5,12,10,10,9,12,6,4,5,13,12,12,10,12,5,2,2,8,6,6,5,8,3,2,1]}
rawChipWaves["pan flute"] = {"expression": 0.35, "samples": [1,4,7,6,7,9,7,7,11,12,13,15,13,11,11,12,13,10,7,5,3,6,10,7,3,3,1,0,1,0,1,0]}
rawChipWaves["glitch"] = {"expression": 0.5, "samples": [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1]}

def convert(instdata):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']
	bb_type = plugindata['type']
	bb_data = plugindata['data']
	if bb_data['type'] == 'chip':
		bb_sample = rawChipWaves[bb_data['wave']]['samples']
		dur_bb = len(bb_sample)
		params_vital.create()
		params_vital.setvalue('osc_1_on', 1)
		bb_sample = rawChipWaves[bb_data['wave']]['samples']
		params_vital.replacewave(0, params_vital_wavetable.resizewave(bb_sample))
		vitaldata = params_vital.getdata()
		list_vst.replace_data(instdata, 'Vital', vitaldata.encode('utf-8'))
