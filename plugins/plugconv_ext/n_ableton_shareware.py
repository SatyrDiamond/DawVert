# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import struct
from functions import extpluglog
from functions import xtramath
from functions_plugin_ext import plugin_vst2
import math

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv_ext'

	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'ableton', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['shareware']
		
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):

		if plugin_obj.type.subtype == 'GlueCompressor':
			if 'vst2' in extplugtype:
				extpluglog.extpluglist.add('Shareware', 'VST2', 'The Glue', '')
				if plugin_vst2.check_exists('id', 1132024935):
					extpluglog.extpluglist.success('Ableton', 'Glue Compressor')
					plugin_obj.plugts_transform('./data_ext/plugts/ableton_vst2.pltr', 'glue', convproj_obj, pluginid)
					plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1132024935, 'param', None, 12)
					return True
