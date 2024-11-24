# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'onlineseq', None]]
		in_dict['in_daws'] = ['onlineseq']
		in_dict['out_plugins'] = [['universal', None, None]]
		in_dict['out_daws'] = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		
		if plugin_obj.type.check_wildmatch('native', 'onlineseq', 'eq'):
			extpluglog.convinternal('Online Sequencer', 'EQ', 'Universal', '3-Band EQ')
			plugin_obj.plugts_transform('./data_main/plugts/onlineseq_univ.pltr', 'eq', convproj_obj, pluginid)
			return 1

		return 2