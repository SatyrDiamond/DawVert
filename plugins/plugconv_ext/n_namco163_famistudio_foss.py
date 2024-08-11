# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def getplugconvinfo(self, plugconv_ext_obj): 
		plugconv_ext_obj.in_plugin = ['namco163_famistudio', None]
		plugconv_ext_obj.ext_formats = ['vst2']
		plugconv_ext_obj.plugincat = ['foss']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype):
		extpluglog.extpluglist.add('FOSS', 'VST', 'Vital', '')
		exttype = plugins.base.extplug_exists('vital', extplugtype, None)
		if exttype:
			extpluglog.extpluglist.success('Famistudio', 'N163')
			wavedata = plugin_obj.datavals.get('wave', {})
			plugin_obj.replace('matt_tytel', 'vital')
			plugin_obj.params.add('volume', 4000, 'float')
			plugin_obj.params.add('osc_1_level', 0.5, 'float')
			plugin_obj.params.add('osc_1_on', 1, 'float')
			plugin_obj.params.add('osc_1_wave_frame', 128, 'float')

			autopoints_obj = plugin_obj.env_points_add('vital_lfo_1', 1, False, 'float')

			autopoint_obj = autopoints_obj.add_point()
			autopoint_obj.pos = 0
			autopoint_obj.value = 0
	
			autopoint_obj = autopoints_obj.add_point()
			autopoint_obj.pos = 1
			autopoint_obj.value = 1

			if 'values' in wavedata and 'size' in wavedata: 
				wavepoints = [((x/15)-0.5)*2 for x in wavedata['values']]
				wavetable_obj = plugin_obj.wavetable_add('N163')
				wavetable_src = wavetable_obj.add_source()
				wavetable_src.wave_add_stream_wave(wavepoints, int(wavedata['size']), plugin_obj, 'N163_')

			osc_obj = plugin_obj.osc_add()
			osc_obj.prop.type = 'wavetable'
			osc_obj.prop.nameid = 'N163'

			plugin_obj.params.add('lfo_1_frequency', 1.8, 'float')
			plugin_obj.params.add('lfo_1_sync', 0.0, 'float')
			plugin_obj.params.add('lfo_1_sync_type', 4.0, 'float')
			plugin_obj.params.add('osc_1_wave_frame', 0, 'float')

			modulation_obj = plugin_obj.modulation_add_native('lfo_1', 'osc_1_wave_frame')
			modulation_obj.amount = 1

			plugin_obj.env_points_from_blocks('vol')
			plugin_obj.env_points_copy('vol', 'vital_import_lfo_2')
			plugin_obj.to_ext_plugin(convproj_obj, pluginid, exttype, 'any')
			return True
