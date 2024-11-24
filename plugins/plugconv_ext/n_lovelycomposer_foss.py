# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import struct
import math
from functions_plugin_ext import plugin_vst2
from functions import extpluglog

loaded_plugtransform = False

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'lovelycomposer', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):

		if plugin_obj.type.check_match('native', 'lovelycomposer', 'custom'):
			extpluglog.extpluglist.add('FOSS', 'VST', 'Vital', '')
			exttype = plugins.base.extplug_exists('vital', extplugtype, None)

			if exttype:
				customfx = plugin_obj.datavals.get('effect', None)

				plugin_obj.replace('user', 'matt_tytel', 'vital')
				plugin_obj.params.add('osc_1_on', 1, 'float')
				plugin_obj.params.add('osc_1_level', 1, 'float')

				if customfx == 'V':
					lfo_obj = plugin_obj.lfo_add('vital_lfo_1')
					lfo_obj.prop.shape = 'sine'
					lfo_obj.time.set_hz(8)
					modulation_obj = plugin_obj.modulation_add_native('lfo_1', 'osc_1_tune')
					modulation_obj.amount = 0.2
					modulation_obj.bipolar = 1

				if customfx == 'F':
					asdrdata_obj = plugin_obj.env_asdr_add('vital_env_1', 0, 0, 0, 0.25, 0, 0, 1)

				if customfx == 'I':
					asdrdata_obj = plugin_obj.env_asdr_add('vital_env_1', 0, 0.25, 0, 0, 0, 0, 1)

				if customfx in ['D', '-']:
					lfo_obj = plugin_obj.lfo_add('vital_lfo_1')
					lfo_obj.prop.type = 'env'
					lfo_obj.prop.nameid = 'lc_fx'
					lfo_obj.loop_on = False

					hzd = 8 if customfx == 'D' else 2

					lfo_obj.time.set_hz(hzd)
					autopoints_obj = plugin_obj.env_points_add('lc_fx', 1, True, 'float')

					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 0
					autopoint_obj.value = 0.5
					autopoint_obj.tension = 0.2
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 0.5
					autopoint_obj.value = 0
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 1
					autopoint_obj.value = 0

					modulation_obj = plugin_obj.modulation_add_native('lfo_1', 'osc_1_transpose')
					modulation_obj.amount = 0.5
					modulation_obj.bipolar = 1
					asdrdata_obj = plugin_obj.env_asdr_add('vital_env_1', 0, 0, (1/hzd)/2, 0, 0, 0, 1)

				if customfx == 'H':
					lfo_obj = plugin_obj.lfo_add('vital_lfo_1')
					lfo_obj.prop.type = 'env'
					lfo_obj.prop.nameid = 'lc_fx'
					lfo_obj.loop_on = False
					lfo_obj.time.set_hz(8)
					autopoints_obj = plugin_obj.env_points_add('lc_fx', 1, True, 'float')

					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 0
					autopoint_obj.value = 0.5
					autopoint_obj.tension = 0.2
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 0.5
					autopoint_obj.value = 1
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 1
					autopoint_obj.value = 1

					modulation_obj = plugin_obj.modulation_add_native('lfo_1', 'osc_1_transpose')
					modulation_obj.amount = 0.5
					modulation_obj.bipolar = 1
					asdrdata_obj = plugin_obj.env_asdr_add('vital_env_1', 0, 0, (1/8)/2, 0, 0, 0, 1)

				if customfx == 'T':
					lfo_obj = plugin_obj.lfo_add('vital_lfo_1')
					lfo_obj.prop.type = 'env'
					lfo_obj.prop.nameid = 'lc_fx'
					lfo_obj.loop_on = False
					lfo_obj.time.set_hz(4)
					autopoints_obj = plugin_obj.env_points_add('lc_fx', 1, True, 'float')

					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 0
					autopoint_obj.value = 0.5
					autopoint_obj.tension = 0.2
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 0.5
					autopoint_obj.value = 0
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 0.5
					autopoint_obj.value = 0.5
					autopoint_obj.tension = 0.2
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 1
					autopoint_obj.value = 0

					modulation_obj = plugin_obj.modulation_add_native('lfo_1', 'osc_1_transpose')
					modulation_obj.amount = 0.5
					modulation_obj.bipolar = 1
					asdrdata_obj = plugin_obj.env_asdr_add('vital_env_1', 0, 0, (1/4), 0, 0, 0, 1)

				if customfx == 'O':
					lfo_obj = plugin_obj.lfo_add('vital_lfo_1')
					lfo_obj.prop.type = 'env'
					lfo_obj.prop.nameid = 'lc_fx'
					lfo_obj.loop_on = False
					lfo_obj.time.set_hz(12)
					autopoints_obj = plugin_obj.env_points_add('lc_fx', 1, True, 'float')

					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 0/3
					autopoint_obj.value = 1
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 1/3
					autopoint_obj.value = 1
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 1/3
					autopoint_obj.value = 0.5
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 2/3
					autopoint_obj.value = 0.5
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 2/3
					autopoint_obj.value = 0
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = 3/3
					autopoint_obj.value = 0

					modulation_obj = plugin_obj.modulation_add_native('lfo_1', 'osc_1_transpose')
					modulation_obj.amount = 0.5
					modulation_obj.bipolar = 1
					asdrdata_obj = plugin_obj.env_asdr_add('vital_env_1', 0, 0, (1/12.1), 0, 0, 0, 1)


				if customfx == 'S':
					plugin_obj.params.add('polyphony', 1, 'float')
					plugin_obj.params.add('portamento_force', 1, 'float')
					plugin_obj.params.add('portamento_time', -2, 'float')

					#poly_obj = plugin_obj.poly
					#poly_obj.max = 1
					#poly_obj.porta_time.set_hz(2)
					
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		else: return False