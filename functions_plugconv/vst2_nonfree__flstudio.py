# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import plugin_vst2
from functions import plugins

def getparam(paramname):
	global pluginid_g
	global cvpj_l_g
	paramval = plugins.get_plug_param(cvpj_l_g, pluginid_g, paramname, 0)
	return paramval[0]

def convert(cvpj_l, pluginid, plugintype):
	global pluginid_g
	global cvpj_l_g
	pluginid_g = pluginid
	cvpj_l_g = cvpj_l
	
	paramvals = [getparam('preband')/10000, getparam('color')/10000, getparam('preamp')/10000,
	getparam('x100'), getparam('postfilter')/10000, getparam('postgain')/10000]

	if plugintype[1].lower() == 'fruity blood overdrive':
		plugin_vst2.replace_data(cvpj_l, pluginid, 'win', 'BloodOverdrive', 'param', None, 6)
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_0', paramvals[0], 'float', " PreBand  ")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_1', paramvals[1], 'float', "  Color   ")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_2', paramvals[2], 'float', "  PreAmp  ")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_3', paramvals[3], 'float', "  x 100   ")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_4', paramvals[4], 'float', "PostFilter")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_5', paramvals[5], 'float', " PostGain ")
		return True