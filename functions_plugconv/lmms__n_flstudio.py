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
from functions import plugins

# -- 3XOSC
# 0 Sine
# 1 Triangle
# 2 Square
# 3 Saw
# 4 PulseSine
# 5 Random
# 6 Custom
# -- LMMS
# 0 Sine
# 1 Triangle
# 2 Saw
# 3 Square
# 4 Moog
# 5 Exp
# 6 Random
# 7 Custom

threeosc_shapes = {
	0: 0,
	1: 1,
	2: 3,
	3: 2,
	4: 5,
	5: 6,
	6: 7}


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

	if plugintype[1] == None: plugintype[1] = ''

	#---------------------------------------- Fruit Kick ----------------------------------------
	if plugintype[1].lower() == '3x osc':
		fl_osc1_coarse = getparam('osc1_coarse')
		fl_osc1_detune = getparam('osc1_detune')
		fl_osc1_fine = getparam('osc1_fine')
		fl_osc1_invert = getparam('osc1_invert')
		fl_osc1_mixlevel = getparam('osc1_mixlevel')/128
		fl_osc1_ofs = getparam('osc1_ofs')/64
		fl_osc1_pan = getparam('osc1_pan')/64
		fl_osc1_shape = getparam('osc1_shape')

		fl_osc2_coarse = getparam('osc2_coarse')
		fl_osc2_detune = getparam('osc2_detune')
		fl_osc2_fine = getparam('osc2_fine')
		fl_osc2_invert = getparam('osc2_invert')
		fl_osc2_mixlevel = getparam('osc2_mixlevel')/128
		fl_osc2_ofs = getparam('osc2_ofs')/64
		fl_osc2_pan = getparam('osc2_pan')/64
		fl_osc2_shape = getparam('osc2_shape')

		fl_osc3_coarse = getparam('osc3_coarse')
		fl_osc3_detune = getparam('osc3_detune')
		fl_osc3_fine = getparam('osc3_fine')
		fl_osc3_invert = getparam('osc3_invert')
		fl_osc3_ofs = getparam('osc3_ofs')/64
		fl_osc3_pan = getparam('osc3_pan')/64
		fl_osc3_shape = getparam('osc3_shape')

		fl_osc3_am = getparam('osc3_am')
		fl_phase_rand = getparam('phase_rand')

		lmms_coarse0 = fl_osc1_coarse
		lmms_coarse1 = fl_osc2_coarse
		lmms_coarse2 = fl_osc3_coarse
		lmms_finel0 = fl_osc1_fine
		lmms_finel1 = fl_osc2_fine
		lmms_finel2 = fl_osc3_fine
		lmms_finer0 = fl_osc1_fine+fl_osc1_detune
		lmms_finer1 = fl_osc2_fine+fl_osc2_detune
		lmms_finer2 = fl_osc3_fine+fl_osc3_detune
		lmms_modalgo1 = 2
		lmms_modalgo2 = 2
		lmms_modalgo3 = 2
		lmms_pan0 = int(fl_osc1_pan*100)
		lmms_pan1 = int(fl_osc2_pan*100)
		lmms_pan2 = int(fl_osc3_pan*100)
		lmms_phoffset0 = 0
		lmms_phoffset1 = 0
		lmms_phoffset2 = 0
		lmms_stphdetun0 = int(fl_osc1_ofs*360)
		if lmms_stphdetun0 < 0: lmms_stphdetun0 + 360
		lmms_stphdetun1 = int(fl_osc2_ofs*360)
		if lmms_stphdetun1 < 0: lmms_stphdetun1 + 360
		lmms_stphdetun2 = int(fl_osc3_ofs*360)
		if lmms_stphdetun2 < 0: lmms_stphdetun2 + 360
		lmms_vol0 = 1.0*(-fl_osc1_mixlevel+1)*(-fl_osc2_mixlevel+1)
		lmms_vol1 = fl_osc1_mixlevel*(-fl_osc2_mixlevel+1)
		lmms_vol2 = fl_osc2_mixlevel
		lmms_wavetype0 = threeosc_shapes[fl_osc1_shape]
		lmms_wavetype1 = threeosc_shapes[fl_osc2_shape]
		lmms_wavetype2 = threeosc_shapes[fl_osc3_shape]
		lmms_userwavefile0 = 0
		lmms_userwavefile1 = 0
		lmms_userwavefile2 = 0

		filedata = plugins.get_fileref(cvpj_l, pluginid, 'audiofile')

		plugins.replace_plug(cvpj_l, pluginid, 'native-lmms', 'tripleoscillator')

		plugins.add_plug_param(cvpj_l, pluginid, 'coarse0', lmms_coarse0, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'coarse1', lmms_coarse1, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'coarse2', lmms_coarse2, 'int', "")

		plugins.add_plug_param(cvpj_l, pluginid, 'finel0', lmms_finel0, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'finel1', lmms_finel1, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'finel2', lmms_finel2, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'finer0', lmms_finer0, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'finer1', lmms_finer1, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'finer2', lmms_finer2, 'int', "")

		plugins.add_plug_param(cvpj_l, pluginid, 'modalgo1', lmms_modalgo1, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'modalgo2', lmms_modalgo2, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'modalgo3', lmms_modalgo3, 'int', "")

		plugins.add_plug_param(cvpj_l, pluginid, 'pan0', lmms_pan0, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'pan1', lmms_pan1, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'pan2', lmms_pan2, 'int', "")

		plugins.add_plug_param(cvpj_l, pluginid, 'phoffset0', lmms_phoffset0, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'phoffset1', lmms_phoffset1, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'phoffset2', lmms_phoffset2, 'int', "")

		plugins.add_plug_param(cvpj_l, pluginid, 'stphdetun0', lmms_stphdetun0, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'stphdetun1', lmms_stphdetun1, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'stphdetun2', lmms_stphdetun2, 'int', "")

		plugins.add_plug_param(cvpj_l, pluginid, 'vol0', lmms_vol0*33, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'vol1', lmms_vol1*33, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'vol2', lmms_vol2*33, 'int', "")

		plugins.add_plug_param(cvpj_l, pluginid, 'wavetype0', lmms_wavetype0, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'wavetype1', lmms_wavetype1, 'int', "")
		plugins.add_plug_param(cvpj_l, pluginid, 'wavetype2', lmms_wavetype2, 'int', "")

		if filedata != None:
			plugins.add_fileref(cvpj_l, pluginid, 'osc_1', filedata['path'])
			plugins.add_fileref(cvpj_l, pluginid, 'osc_2', filedata['path'])
			plugins.add_fileref(cvpj_l, pluginid, 'osc_3', filedata['path'])
