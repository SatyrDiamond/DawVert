# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import plugins

from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return -100
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'amped', None]]
		in_dict['in_daws'] = ['amped']
		in_dict['out_plugins'] = [['native', 'lmms', None]]
		in_dict['out_daws'] = ['lmms']
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.type.check_wildmatch('native', 'amped', 'Reverb'):
			extpluglog.convinternal('Amped', 'Reverb', 'LMMS', 'ReverbSC')
			plugin_obj.plugts_transform('./data_main/plugts/amped_lmms.pltr', 'reverb', convproj_obj, pluginid)
			return 0
		return 2