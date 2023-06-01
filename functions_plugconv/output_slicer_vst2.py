# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import pathlib

from functions import audio_wav
from functions import plugin_vst2

from functions_plugparams import params_ninjas2
from functions_plugparams import data_nullbytegroup

def convert_inst(instdata):
	slicerdata = instdata['plugindata']
	params_ninjas2.initparams()
	params_ninjas2.slicerdata(slicerdata)
	ninjas2out = params_ninjas2.getparams()
	plugin_vst2.replace_data(instdata, 'any', 'Ninjas 2', 'chunk', data_nullbytegroup.make(ninjas2out), None)