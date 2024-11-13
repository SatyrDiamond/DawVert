# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

from functions import extpluglog

from functions_plugin_ext import plugin_vst2

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'flstudio', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['nonfree', 'old']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype):
		flpluginname = plugin_obj.type.subtype.lower()

		use_vst2 = 'vst2' in extplugtype

		# ---------------------------------------- Fruity Blood Overdrive ----------------------------------------
		if flpluginname == 'fruity blood overdrive' and use_vst2:
			extpluglog.extpluglist.add('Old', 'VST2', 'Blood Overdrive', '')

			if plugin_vst2.check_exists('id', 1112297284):
				extpluglog.extpluglist.success('FL Studio', 'Fruity Blood Overdrive')
				plugin_obj.plugts_transform('./data_ext/plugts/flstudio_vst.pltr', 'nf_vst2_fruity_blood_overdrive', convproj_obj, pluginid)
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name', 'win', 'BloodOverdrive', 'param', None, 6)
				return True