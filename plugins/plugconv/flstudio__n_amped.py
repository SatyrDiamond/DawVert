# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'
	
	def get_priority(self):
		return -100
	
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'amped', None]]
		in_dict['in_daws'] = ['amped']
		in_dict['out_plugins'] = [['native', 'flstudio', None]]
		in_dict['out_daws'] = ['flp']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.type.check_wildmatch('native', 'amped', 'Phaser'):
			extpluglog.convinternal('Amped', 'Phaser', 'FL Studio', 'Fruity Phaser')
			plugin_obj.plugts_transform('./data_main/plugts/flstudio_amped.pltr', 'phaser', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Flanger'):
			extpluglog.convinternal('Amped', 'Flanger', 'FL Studio', 'Fruity Flanger')
			plugin_obj.plugts_transform('./data_main/plugts/flstudio_amped.pltr', 'flanger', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Delay'):
			extpluglog.convinternal('Amped', 'Delay', 'FL Studio', 'Fruity Delay 3')
			plugin_obj.plugts_transform('./data_main/plugts/flstudio_amped.pltr', 'delay', convproj_obj, pluginid)
			return 0

		return 2
