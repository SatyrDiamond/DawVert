# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import math
from functions import xtramath
from functions import extpluglog

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'
	
	def get_priority(self):
		return -100
	
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'flstudio', None]]
		in_dict['in_daws'] = ['flp']
		in_dict['out_plugins'] = [['universal', 'midi', None]]
		in_dict['out_daws'] = []

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		flpluginname = plugin_obj.type.subtype.lower()

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'boobass'):
			extpluglog.convinternal('FL Studio', 'BooBass', 'MIDI', 'Electric Bass (finger)')
			plugin_obj.replace('universal', 'midi', None)
			plugin_obj.midi.bank = 0
			plugin_obj.midi.patch = 33
			plugin_obj.midi.drum = False
			plugin_obj.datavals_global.add('middlenotefix', 24)
			#print('[plug-conv] No Soundfont Argument Defined:',pluginid)
			return 1

		return 2