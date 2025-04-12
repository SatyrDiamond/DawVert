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
		in_dict['out_plugins'] = [['native', 'ableton', None]]
		in_dict['out_daws'] = ['ableton']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.type.check_wildmatch('native', 'amped', 'Vibrato'):
			extpluglog.convinternal('Amped', 'Vibrato', 'Ableton', 'Chorus2')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_amped.pltr', 'vibrato', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Tremolo'):
			extpluglog.convinternal('Amped', 'Tremolo', 'Ableton', 'AutoPan')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_amped.pltr', 'tremolo', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Phaser'):
			extpluglog.convinternal('Amped', 'Phaser', 'Ableton', 'PhaserNew')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_amped.pltr', 'phaser', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Flanger'):
			extpluglog.convinternal('Amped', 'Flanger', 'Ableton', 'PhaserNew')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_amped.pltr', 'flanger', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Chorus'):
			extpluglog.convinternal('Amped', 'Chorus', 'Ableton', 'Chorus2')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_amped.pltr', 'chorus', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.check_wildmatch('native', 'amped', 'Delay'):
			extpluglog.convinternal('Amped', 'Delay', 'Ableton', 'Delay')
			cross_val = plugin_obj.params.get("cross", 0).value
			plugin_obj.plugts_transform('./data_main/plugts/ableton_amped.pltr', 'delay', convproj_obj, pluginid)
			plugin_obj.params.add('DelayLine_PingPong', cross_val>=0.5, 'bool')
			return 0

		return 2
