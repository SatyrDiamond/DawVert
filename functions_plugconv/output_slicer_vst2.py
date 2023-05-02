# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import audio_wav
from functions import plugin_vst2
from functions import vst_inst
import xml.etree.ElementTree as ET
import pathlib

from functions_plugparams import data_nullbytegroup

def convert_inst(instdata):
	slicerdata = instdata['plugindata']
	vst_inst.ninjas2_init()
	vst_inst.ninjas2_slicerdata(slicerdata)
	ninjas2out = vst_inst.ninjas2_get()
	plugin_vst2.replace_data(instdata, 'any', 'Ninjas 2', 'raw', data_nullbytegroup.make(ninjas2out), None)