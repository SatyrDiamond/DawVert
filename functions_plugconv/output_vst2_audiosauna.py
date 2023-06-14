# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
import math
from functions import data_bytes
from functions import params_vst
from functions import plugin_vst2

def convert_inst(instdata):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']
	if pluginname == 'native-audiosauna':
		as_type = plugindata['type']
		as_data = plugindata['data']
		as_asdrlfo = plugindata['asdrlfo']
	
def convert_fx(fxdata):
	pluginname = fxdata['plugin']
	plugindata = fxdata['plugindata']
	as_type = plugindata['name']
	as_data = plugindata['data']

