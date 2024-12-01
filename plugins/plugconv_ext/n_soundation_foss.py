# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import struct
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import params_os_tal_filter
from functions import extpluglog
from functions import xtramath

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv_ext'

	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'soundation', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):
		if plugin_obj.type.check_match('native', 'soundation', 'com.soundation.distortion'):
			mode = int(plugin_obj.params.get('mode', 0).value)
			gain = plugin_obj.params.get('gain', 0).value

			if mode in [0,4]:
				extpluglog.extpluglist.add('FOSS', 'VST2', 'Drive', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Drive')
				if exttype:
					extpluglog.extpluglist.success('Soundation', 'Distortion')
					driveval = ((gain**0.2)*2)-1
					drive = max(driveval, 0)
					vol = min(driveval, 0)+1

					plugin_obj.replace('user', 'airwindows', 'Drive')
					plugin_obj.params.add('drive', drive, 'float')
					plugin_obj.params.add('highpass', 0, 'float')
					plugin_obj.params.add('out_level', vol, 'float')
					plugin_obj.params.add('dry_wet', 1, 'float')
					plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
					return True

			if mode in [1]:
				extpluglog.extpluglist.add('FOSS', 'VST2', 'Fracture2', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Fracture2')
				if exttype:
					extpluglog.extpluglist.success('Soundation', 'Distortion')
					plugin_obj.replace('user', 'airwindows', 'Fracture2')
					plugin_obj.params.add('drive', gain, 'float')
					plugin_obj.params.add('fractre', 0.2, 'float')
					plugin_obj.params.add('thresh', 0.5, 'float')
					plugin_obj.params.add('output', 1, 'float')
					plugin_obj.params.add('dry_wet', 1, 'float')
					plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
					return True

			if mode in [2,3]:
				extpluglog.extpluglist.add('FOSS', 'VST2', 'Drive', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Drive')
				if exttype:
					extpluglog.extpluglist.success('Soundation', 'Distortion')
					plugin_obj.replace('user', 'airwindows', 'Drive')
					plugin_obj.params.add('drive', gain, 'float')
					plugin_obj.params.add('highpass', 0, 'float')
					plugin_obj.params.add('out_level', 1, 'float')
					plugin_obj.params.add('dry_wet', 1, 'float')
					plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
					return True

		if plugin_obj.type.check_match('native', 'soundation', 'com.soundation.fakie') and 'vst2' in extplugtype:
			extpluglog.extpluglist.add('FOSS', 'VST2', 'TAL-Filter-2', '')
			if plugin_vst2.check_exists('id', 808596837):
				extpluglog.extpluglist.success('Soundation', 'Fakie')
				attack = plugin_obj.params.get('attack', 0).value
				depth = plugin_obj.params.get('depth', 0).value
				hold = plugin_obj.params.get('hold', 0).value
				release = plugin_obj.params.get('release', 0).value

				start_end = xtramath.clamp(attack, 0.001, 1)
				end_start = xtramath.clamp(attack+hold, 0.001, 1)
				end_end = xtramath.clamp(attack+hold+release, 0.001, 1)

				tal_obj = params_os_tal_filter.tal_filter_data()

				tal_obj.set_param('filtertypeNew', 0.2)
				tal_obj.set_param('speedFactor', 5)

				tal_obj.add_point(0, 1, 1, 0)
				tal_obj.add_point(start_end, 1-depth, 0, 0)
				tal_obj.add_point(end_start, 1-depth, 0, 0)
				tal_obj.add_point(end_end, 1, 0, 0)
				tal_obj.add_point(1, 1, 0, 1)
				tal_obj.to_cvpj_vst2(convproj_obj, plugin_obj)
				return True

		if plugin_obj.type.check_match('native', 'soundation', 'com.soundation.reverb'):
			extpluglog.extpluglist.add('FOSS', 'VST', 'MatrixVerb', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'MatrixVerb')
			if exttype:
				extpluglog.extpluglist.success('Soundation', 'Reverb')
				damp = plugin_obj.params.get('damp', 0).value
				dry = plugin_obj.params.get('dry', 0).value
				size = plugin_obj.params.get('size', 0).value
				wet = plugin_obj.params.get('wet', 0).value
				plugin_obj.replace('user', 'airwindows', 'MatrixVerb')
				plugin_obj.params.add('filter', 1, 'float')
				plugin_obj.params.add('damping', damp, 'float')
				plugin_obj.params.add('speed', 0, 'float')
				plugin_obj.params.add('vibrato', 0, 'float')
				plugin_obj.params.add('rmsize', 0.5, 'float')
				plugin_obj.params.add('flavor', (size**2)/2, 'float')
				plugin_obj.params.add('dry_wet', xtramath.wetdry(wet, dry), 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		if plugin_obj.type.check_match('native', 'soundation', 'com.soundation.tremolo'):
			extpluglog.extpluglist.add('FOSS', 'VST', 'AutoPan', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'AutoPan')
			if exttype:
				extpluglog.extpluglist.success('Soundation', 'Tremolo')
				plugin_obj.plugts_transform('./data_ext/plugts/soundation_ext.pltr', 'tremolo_airwindows', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		return False