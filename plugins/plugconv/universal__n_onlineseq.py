# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self, plugconv_obj): 
		plugconv_obj.priority = 50
		plugconv_obj.in_plugins = [['native-onlineseq', None]]
		plugconv_obj.in_daws = ['onlineseq']
		plugconv_obj.out_plugins = [['universal', None]]
		plugconv_obj.out_daws = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):
		
		if plugin_obj.type.subtype == 'eq':
			extpluglog.convinternal('Online Sequencer', 'EQ', 'Universal', '3-Band EQ')
			plugin_obj.plugts_transform('./data_main/plugts/onlineseq_univ.pltr', 'eq', convproj_obj, pluginid)
			return 1

		return 2