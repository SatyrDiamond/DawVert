# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
import math
from functions_plugparams import params_vital
from functions_plugparams import params_vital_wavetable
from functions import plugins
from functions import plugin_vst2

def convert(cvpj_l, pluginid, plugintype, extra_json):
	sffile = extra_json['soundfont']
	v_bank = plugins.get_plug_dataval(cvpj_l, pluginid, 'bank', 0)
	v_inst = plugins.get_plug_dataval(cvpj_l, pluginid, 'inst', 0)
	plugins.replace_plug(cvpj_l, pluginid, 'soundfont2', None)
	plugins.add_plug_data(cvpj_l, pluginid, 'bank', v_bank)
	plugins.add_plug_data(cvpj_l, pluginid, 'patch', v_inst)
	plugins.add_plug_data(cvpj_l, pluginid, 'file', sffile)
	return True