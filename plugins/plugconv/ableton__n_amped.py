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
		plugconv_obj.out_plugins = [['native-ableton', None]]
		plugconv_obj.out_daws = ['ableton']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):

		if plugin_obj.type.subtype == 'Vibrato':
			extpluglog.convinternal('Amped', 'Vibrato', 'Ableton', 'Chorus2')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_amped.pltr', 'vibrato', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.subtype == 'Tremolo':
			extpluglog.convinternal('Amped', 'Tremolo', 'Ableton', 'AutoPan')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_amped.pltr', 'tremolo', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.subtype == 'Phaser':
			extpluglog.convinternal('Amped', 'Phaser', 'Ableton', 'PhaserNew')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_amped.pltr', 'phaser', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.subtype == 'Flanger':
			extpluglog.convinternal('Amped', 'Flanger', 'Ableton', 'PhaserNew')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_amped.pltr', 'phaser', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.subtype == 'Chorus':
			extpluglog.convinternal('Amped', 'Chorus', 'Ableton', 'Chorus2')
			plugin_obj.plugts_transform('./data_main/plugts/ableton_amped.pltr', 'chorus', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.subtype == 'Delay':
			extpluglog.convinternal('Amped', 'Delay', 'Ableton', 'Delay')
			cross_val = plugin_obj.params.get("cross", 0).value
			plugin_obj.plugts_transform('./data_main/plugts/ableton_amped.pltr', 'delay', convproj_obj, pluginid)
			plugin_obj.params.add('DelayLine_PingPong', cross_val>=0.5, 'bool')
			return 0

		return 2
