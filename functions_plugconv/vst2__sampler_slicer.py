# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import pathlib

from functions import audio_wav
from functions import plugin_vst2

from functions_plugparams import params_ninjas2
from functions_plugparams import data_nullbytegroup

def convert(cvpj_l, pluginid, plugintype):
	params_ninjas2.initparams()
	params_ninjas2.slicerdata(cvpj_l, pluginid)
	ninjas2out = params_ninjas2.getparams()
	plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Ninjas 2', 'chunk', data_nullbytegroup.make(ninjas2out), None)
	return True