# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import pathlib

from functions import audio_wav
from functions import plugin_vst2

from functions_plugparams import params_various_inst
from functions_plugparams import data_nullbytegroup

def convert_inst(instdata):
	slicerdata = instdata['plugindata']
	params_various_inst.ninjas2_init()
	params_various_inst.ninjas2_slicerdata(slicerdata)
	ninjas2out = params_various_inst.ninjas2_get()
	plugin_vst2.replace_data(instdata, 'any', 'Ninjas 2', 'chunk', data_nullbytegroup.make(ninjas2out), None)