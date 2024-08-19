# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import math
from functions import xtramath
from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self, plugconv_obj): 
		plugconv_obj.in_plugins = [['native-flstudio', None]]
		plugconv_obj.in_daws = ['flp']
		plugconv_obj.out_plugins = [['midi', None]]
		plugconv_obj.out_daws = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):
		flpluginname = plugin_obj.type.subtype.lower()

		if flpluginname == 'boobass':
			extpluglog.convinternal('FL Studio', 'BooBass', 'MIDI', 'Electric Bass (finger)')
			plugin_obj.replace('midi', None)
			plugin_obj.midi.bank = 0
			plugin_obj.midi.patch = 33
			plugin_obj.midi.drum = False
			plugin_obj.datavals_global.add('middlenotefix', 24)
			#print('[plug-conv] No Soundfont Argument Defined:',pluginid)
			return 1

		return 2