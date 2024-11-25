# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import math
from functions import extpluglog
from functions import xtramath

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv_ext'

	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'namco163_famistudio', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):
		extpluglog.extpluglist.add('FOSS', 'VST', 'Vital', '')
		exttype = plugins.base.extplug_exists('vital', extplugtype, None)
		if exttype:
			extpluglog.extpluglist.success('Famistudio', 'N163')
			wavedata = plugin_obj.datavals.get('wave', {})
			plugin_obj.replace('user', 'matt_tytel', 'vital')
			plugin_obj.params.add('volume', 6000, 'float')
			plugin_obj.params.add('osc_1_level', 0.8, 'float')
			plugin_obj.params.add('osc_1_on', 1, 'float')

			wavesize = wavedata['size']/32
			pitch = math.log2(1/wavesize)*12

			transpose, finetune = xtramath.transpose_tune(pitch)

			plugin_obj.params.add('osc_1_tune', -finetune, 'float')

			plugin_obj.env_points_from_blocks('vol')
			plugin_obj.env_points_copy('vol', 'vital_import_lfo_2')
			plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')

			plugin_obj.datavals_global.add('middlenotefix', (-transpose)+12)
			return True
