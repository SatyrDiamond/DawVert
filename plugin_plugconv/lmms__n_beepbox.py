# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import plugin_plugconv
from functions_plugdata import data_wave

class plugconv(plugin_plugconv.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self): return ['native-jummbox', None, 'jummbox'], ['native-lmms', None, 'lmms'], True, False
	def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
		plugintype = cvpj_plugindata.type_get()
		if plugintype[1] in ['custom chip', 'chip', 'harmonics']:
			print('[plug-conv] Beepbox to LMMS: '+plugintype[1]+' > TripleOscillator:',pluginid)

			samplefolder = extra_json['samplefolder']

			os.makedirs(samplefolder, exist_ok=True)
			wave_path = os.path.join(samplefolder, pluginid+'_wave.wav')

			if plugintype[1] in ['custom chip', 'chip']: data_wave.wave2file(cvpj_plugindata, 'chipwave', wave_path)
			if plugintype[1] in ['harmonics']: data_wave.harm2file(cvpj_plugindata, 'harmonics', wave_path)

			cvpj_plugindata.replace('native-lmms', 'tripleoscillator')

			cvpj_plugindata.param_add('vol0', 15, 'int', "")
			cvpj_plugindata.fileref_add('osc_1', wave_path)
			cvpj_plugindata.fileref_add('osc_2', wave_path)
			cvpj_plugindata.fileref_add('osc_3', wave_path)
			cvpj_plugindata.param_add('wavetype0', 7, 'int', "")
			cvpj_plugindata.param_add('wavetype1', 7, 'int', "")
			cvpj_plugindata.param_add('wavetype2', 7, 'int', "")
			cvpj_plugindata.param_add('coarse0', -12, 'int', "")
			cvpj_plugindata.param_add('coarse1', -12, 'int', "")
			cvpj_plugindata.param_add('coarse2', -12, 'int', "")
			return 0
		else: 
			return 2