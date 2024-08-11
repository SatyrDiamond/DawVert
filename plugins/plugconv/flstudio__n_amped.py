# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self, plugconv_obj): 
		plugconv_obj.in_plugins = [['native-amped', None]]
		plugconv_obj.in_daws = ['amped']
		plugconv_obj.out_plugins = [['native-flstudio', None]]
		plugconv_obj.out_daws = ['flp']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):
		
		if plugin_obj.type.subtype == 'Phaser':
			extpluglog.convinternal('Amped', 'Phaser', 'FL Studio', 'Fruity Phaser')
			plugin_obj.plugts_transform('./data_main/plugts/flstudio_amped.pltr', 'phaser', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.subtype == 'Flanger':
			extpluglog.convinternal('Amped', 'Flanger', 'FL Studio', 'Fruity Flanger')
			plugin_obj.plugts_transform('./data_main/plugts/flstudio_amped.pltr', 'flanger', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.subtype == 'Delay':
			extpluglog.convinternal('Amped', 'Delay', 'FL Studio', 'Fruity Delay 3')
			plugin_obj.plugts_transform('./data_main/plugts/flstudio_amped.pltr', 'delay', convproj_obj, pluginid)
			return 0

		return 2
