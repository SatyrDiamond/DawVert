# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import os
import math

from functions import note_data
from functions import data_bytes
from functions import data_values
from functions import plugin_vst2
from functions import plugins
from functions import xtramath
from functions_plugparams import wave

import plugin_plugconv

class plugconv(plugin_plugconv.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self): return ['native-jummbox', None, 'jummbox'], ['native-lmms', None, 'lmms'], True, False
	def convert(self, cvpj_l, pluginid, plugintype, extra_json):
		if plugintype[1] in ['custom chip', 'chip', 'harmonics']:
			print('[plug-conv] Beepbox to LMMS: '+plugintype[1]+' > TripleOscillator:',pluginid)
			plugdata = plugins.get_plug_data(cvpj_l, pluginid)
			plugins.replace_plug(cvpj_l, pluginid, 'native-lmms', 'tripleoscillator')

			samplefolder = extra_json['samplefolder']
			os.makedirs(extra_json['samplefolder'], exist_ok=True)
			wave_path = os.path.join(samplefolder, pluginid+'_wave.wav')

			if plugintype[1] in ['custom chip', 'chip']:
				wave.wave2file(cvpj_l, pluginid, 'chipwave', wave_path)
			if plugintype[1] in ['harmonics']:
				wave.harm2file(cvpj_l, pluginid, 'harmonics', wave_path)

			unisontype = plugins.get_plug_dataval(cvpj_l, pluginid, 'unison', 'none')

			plugins.add_plug_param(cvpj_l, pluginid, 'vol0', 15, 'int', "")
			plugins.add_fileref(cvpj_l, pluginid, 'osc_1', wave_path)
			plugins.add_fileref(cvpj_l, pluginid, 'osc_2', wave_path)
			plugins.add_fileref(cvpj_l, pluginid, 'osc_3', wave_path)
			plugins.add_plug_param(cvpj_l, pluginid, 'wavetype0', 7, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, 'wavetype1', 7, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, 'wavetype2', 7, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, 'coarse0', -12, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, 'coarse1', -12, 'int', "")
			plugins.add_plug_param(cvpj_l, pluginid, 'coarse2', -12, 'int', "")
			return True
		else: return False