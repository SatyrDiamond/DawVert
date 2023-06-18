# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import os
import math
import lxml.etree as ET

from functions import note_data
from functions import data_bytes
from functions import data_values
from functions import plugin_vst2
from functions import params_vst

def convert_fx(fxdata):
	global temp_count
	pluginname = fxdata['plugin']
	plugindata = fxdata['plugindata']
	fl_plugdata = base64.b64decode(plugindata['data'])
	fl_plugstr = data_bytes.to_bytesio(fl_plugdata)

	pluginname = plugindata['plugin'].lower()

	if pluginname == 'fruity blood overdrive':
		flpbod = struct.unpack('IIIIIIIII', fl_plugdata)
		bodparams = {}
		params_vst.add_param(bodparams, 0, " PreBand  ", flpbod[1]/10000)
		params_vst.add_param(bodparams, 1, "  Color   ", flpbod[2]/10000)
		params_vst.add_param(bodparams, 2, "  PreAmp  ", flpbod[3]/10000)
		params_vst.add_param(bodparams, 3, "  x 100   ", flpbod[4])
		params_vst.add_param(bodparams, 4, "PostFilter", flpbod[5]/10000)
		params_vst.add_param(bodparams, 5, " PostGain ", flpbod[6]/10000)
		plugin_vst2.replace_data(fxdata, 'any', 'BloodOverdrive', 'param', bodparams, 6)
		return True