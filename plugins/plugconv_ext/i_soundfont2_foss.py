# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

from functions_plugin_ext import params_os_juicysfplugin
from functions_plugin_ext import plugin_vst2
from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def getplugconvinfo(self, plugconv_ext_obj): 
		plugconv_ext_obj.in_plugin = ['soundfont2', None]
		plugconv_ext_obj.ext_formats = ['vst2']
		plugconv_ext_obj.plugincat = ['foss']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype):
		if 'vst2' in extplugtype:
			extpluglog.extpluglist.add('FOSS', 'VST2', 'juicysfplugin', '')
			if plugin_vst2.check_exists('id', 1249076848):
				extpluglog.extpluglist.success('SoundFont2', 'SoundFont2')
				bank, patch = plugin_obj.midi.to_sf2()
				ref_found, fileref_obj = plugin_obj.get_fileref('file', convproj_obj)
				sf2_filename = fileref_obj.get_path(None, False) if ref_found else ''
				jsf2data = params_os_juicysfplugin.juicysfplugin_data()
				jsf2data.set_bankpatch(bank, patch, sf2_filename)
				jsf2data.to_cvpj_vst2(convproj_obj, plugin_obj)
				return True