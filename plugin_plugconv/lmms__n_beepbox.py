# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import plugin_plugconv

class plugconv(plugin_plugconv.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self): return ['native-jummbox', None, 'jummbox'], ['native-lmms', None, 'lmms'], True, False
	def convert(self, convproj_obj, plugin_obj, pluginid, extra_json):
		if plugin_obj.plugin_subtype in ['custom chip', 'chip', 'harmonics']:
			print('[plug-conv] Beepbox to LMMS: '+plugin_obj.plugin_subtype+' > TripleOscillator:',pluginid)

			samplefolder = extra_json['samplefolder']

			os.makedirs(samplefolder, exist_ok=True)
			wave_path = os.path.join(samplefolder, pluginid+'_wave.wav')

			if plugin_obj.plugin_subtype in ['custom chip', 'chip']: plugin_obj.wave_get('chipwave').to_audio(wave_path)
			if plugin_obj.plugin_subtype in ['harmonics']: plugin_obj.harmonics_get('harmonics').to_audio(wave_path)

			plugin_obj.replace('native-lmms', 'tripleoscillator')
			convproj_obj.add_sampleref(pluginid+'_wave', wave_path)
			plugin_obj.samplerefs['userwavefile1'] = pluginid+'_wave'
			plugin_obj.samplerefs['userwavefile2'] = pluginid+'_wave'
			plugin_obj.samplerefs['userwavefile3'] = pluginid+'_wave'

			plugin_obj.params.add('vol0', 15, 'int')
			plugin_obj.params.add('wavetype0', 7, 'int')
			plugin_obj.params.add('wavetype1', 7, 'int')
			plugin_obj.params.add('wavetype2', 7, 'int')
			plugin_obj.params.add('coarse0', -12, 'int')
			plugin_obj.params.add('coarse1', -12, 'int')
			plugin_obj.params.add('coarse2', -12, 'int')
			return 0
		else: 
			return 2