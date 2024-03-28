# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import plugin_plugconv

from objects import plugts
loaded_plugtransform = False

class plugconv(plugin_plugconv.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self): return ['native-amped', None, 'amped'], ['native-lmms', None, 'lmms'], True, False
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):
		global loaded_plugtransform
		global plugts_obj

		if loaded_plugtransform == False:
			plugts_obj = plugts.plugtransform()
			plugts_obj.load_file('./data_plugts/amped_lmms.pltr')
			loaded_plugtransform = True

		if plugin_obj.plugin_subtype == 'Reverb':
			print('[plug-conv] Amped to LMMS: Reverb > ReverbSC:', pluginid)
			plugts_obj.transform('reverb', convproj_obj, plugin_obj, pluginid, dv_config)
			return 0
		else: 
			return 2