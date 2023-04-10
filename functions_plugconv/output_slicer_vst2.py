# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import audio_wav
from functions import list_vst
from functions import vst_inst
import xml.etree.ElementTree as ET
import pathlib

from functions_plugparams import data_nullbytegroup

def convert_inst(instdata):
	slicerdata = instdata['plugindata']
	vst_inst.ninjas2_init()
	vst_inst.ninjas2_slicerdata(slicerdata)
	ninjas2out = vst_inst.ninjas2_get()
	list_vst.replace_data(instdata, 2, 'any', 'Ninjas 2', 'raw', data_nullbytegroup.make(ninjas2out), None)