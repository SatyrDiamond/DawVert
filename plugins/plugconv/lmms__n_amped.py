# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import plugins

from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self, plugconv_obj): 
		plugconv_obj.in_plugins = [['native-amped', None]]
		plugconv_obj.in_daws = ['amped']
		plugconv_obj.out_plugins = [['native-lmms', None]]
		plugconv_obj.out_daws = ['lmms']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):
		if plugin_obj.type.subtype == 'Reverb':
			extpluglog.convinternal('Amped', 'Reverb', 'LMMS', 'ReverbSC')
			plugin_obj.plugts_transform('./data_main/plugts/amped_lmms.pltr', 'reverb', convproj_obj, pluginid)
			return 0
		return 2