# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

from functions import audio_wav
from functions import plugin_vst2
from functions import vst_inst

from functions_plugparams import data_vc2xml

def convert_inst(instdata, out_daw):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']

	if pluginname == 'opn2':
		xmlout = vst_inst.opnplug_convert(plugindata)
		plugin_vst2.replace_data(instdata, 'any', 'OPNplug', 'chunk', data_vc2xml.make(xmlout), None)
