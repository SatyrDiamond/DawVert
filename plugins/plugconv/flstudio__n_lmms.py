# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import os
import math
from functions import extpluglog

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'
	
	def get_priority(self):
		return -100
	
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'lmms', None]]
		in_dict['in_daws'] = ['lmms']
		in_dict['out_plugins'] = [['native', 'flstudio', None]]
		in_dict['out_daws'] = ['flp']
		
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.type.check_wildmatch('native', 'lmms', 'stereomatrix'):
			extpluglog.convinternal('LMMS', 'Stereo Matrix', 'FL Studio', 'Fruity Stereo Shaper')
			plugin_obj.plugts_transform('./data_main/plugts/lmms_flstudio.pltr', 'stereomatrix', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.check_wildmatch('native', 'lmms', 'spectrumanalyzer'):
			extpluglog.convinternal('LMMS', 'Spectrum Analyzer', 'FL Studio', 'Fruity Spectroman')
			plugin_obj.plugts_transform('./data_main/plugts/lmms_flstudio.pltr', 'spectrumanalyzer', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.check_wildmatch('native', 'lmms', 'stereoenhancer'):
			extpluglog.convinternal('LMMS', 'Stereo Enhancer', 'FL Studio', 'Fruity Stereo Enhancer')
			plugin_obj.plugts_transform('./data_main/plugts/lmms_flstudio.pltr', 'stereoenhancer', convproj_obj, pluginid)
			return 0

		return 2

