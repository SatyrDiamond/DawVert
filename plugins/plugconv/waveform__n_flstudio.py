# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog
from objects import globalstore

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native-flstudio', None]]
		in_dict['in_daws'] = ['flp']
		in_dict['out_plugins'] = [['native-tracktion', None]]
		in_dict['out_daws'] = ['waveform_edit']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):
		if plugin_obj.type.subtype == None: plugin_obj.type.subtype = ''
	
		if plugin_obj.type.subtype.lower() == 'fruity balance':  
			extpluglog.convinternal('FL Studio', 'Fruity Balance', 'Waveform', 'Volume')

			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('pan', 'pan', 0)
			manu_obj.from_param('vol', 'vol', 256)
			manu_obj.calc('vol', 'div', 256, 0, 0, 0)
			manu_obj.calc('pan', 'div', 128, 0, 0, 0)
			plugin_obj.replace('native-tracktion', 'volume')
			manu_obj.to_param('vol', 'volume', None)
			manu_obj.to_param('pan', 'pan', None)
			return 1
			
		return 2
