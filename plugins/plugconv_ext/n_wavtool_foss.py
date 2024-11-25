# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import struct
from functions_plugin_ext import plugin_vst2
from functions import extpluglog

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv_ext'

	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'wavtool', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):
		if plugin_obj.type.check_match('native', 'wavtool', 'wavetable'):
			extpluglog.extpluglist.add('FOSS', 'VST', 'Vital', '')
			exttype = plugins.base.extplug_exists('vital', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('Wavtool', 'Wavetable')

				wt_filterA = not plugin_obj.datavals.get('filterA', True)
				wt_filterB = not plugin_obj.datavals.get('filterB', True)
				wt_filterSub = not plugin_obj.datavals.get('filterSub', True)

				wt_wtPosA = plugin_obj.params.get('wtPosA', 0.5).value*256
				wt_wtPosB = plugin_obj.params.get('wtPosB', 0.5).value*256

				wt_oscAEnabled = int(plugin_obj.datavals.get('oscAEnabled', True))
				wt_oscBEnabled = int(plugin_obj.datavals.get('oscBEnabled', False))
				wt_subEnabled = int(plugin_obj.datavals.get('subEnabled', False))

				wt_levelA = plugin_obj.params.get('levelA', 0.5).value
				wt_levelB = plugin_obj.params.get('levelB', 0.5).value

				wt_panA = plugin_obj.params.get('panA', 0).value
				wt_panB = plugin_obj.params.get('panB', 0).value

				wt_transposeA = plugin_obj.params.get('transposeA', 0).value//1
				wt_transposeB = plugin_obj.params.get('transposeB', 0).value//1

				wt_transposeSub = plugin_obj.params.get('transposeSub', 0).value//1
				wt_subLevel = plugin_obj.params.get('subLevel', 0.5).value

				wt_unisonA = int(plugin_obj.datavals.get('unisonA', 1))
				wt_unisonB = int(plugin_obj.datavals.get('unisonB', 1))

				wt_spreadA = plugin_obj.datavals.get('spreadA', 0)**0.5
				wt_spreadB = plugin_obj.datavals.get('spreadB', 0)**0.5

				matrix = plugin_obj.datavals.get('matrix', {})

				plugin_obj.replace('user', 'matt_tytel', 'vital')

				plugin_obj.params.add('osc_1_destination', wt_filterA, 'float')
				plugin_obj.params.add('osc_2_destination', wt_filterB, 'float')
				plugin_obj.params.add('osc_3_destination', wt_filterSub, 'float')

				plugin_obj.params.add('osc_1_wave_frame', wt_wtPosA, 'float')
				plugin_obj.params.add('osc_2_wave_frame', wt_wtPosB, 'float')

				plugin_obj.params.add('osc_1_on', wt_oscAEnabled, 'float')
				plugin_obj.params.add('osc_2_on', wt_oscBEnabled, 'float')
				plugin_obj.params.add('osc_3_on', wt_subEnabled, 'float')

				plugin_obj.params.add('osc_1_level', wt_levelA, 'float')
				plugin_obj.params.add('osc_2_level', wt_levelB, 'float')

				plugin_obj.params.add('osc_1_pan', wt_panA, 'float')
				plugin_obj.params.add('osc_2_pan', wt_panB, 'float')

				plugin_obj.params.add('osc_1_transpose', wt_transposeA, 'float')
				plugin_obj.params.add('osc_2_transpose', wt_transposeB, 'float')

				plugin_obj.params.add('osc_3_transpose', wt_transposeSub, 'float')
				plugin_obj.params.add('osc_3_level', wt_subLevel, 'float')

				plugin_obj.params.add('osc_1_unison_voices', wt_unisonA, 'float')
				plugin_obj.params.add('osc_2_unison_voices', wt_unisonB, 'float')

				plugin_obj.params.add('osc_1_unison_detune', wt_spreadA, 'float')
				plugin_obj.params.add('osc_2_unison_detune', wt_spreadB, 'float')

				modenv = []
				for num in range(1,5):
					adsrname = 'custom'+str(num)
					plugin_obj.env_asdr_copy(adsrname, 'vital_env_'+str(num))
					env_data = plugin_obj.env_asdr_get('vital_env_'+str(num))


				modnum = 1
				for target_id, target_data in matrix.items():
					for from_id, from_data in target_data.items():

						vital_from = None
						vital_to = None

						modamt = plugin_obj.params.get(from_data, 1).value * 1/4

						if from_id == 'envelope1': 
							vital_from = 'env_1'
							#modamt *= modenv[0]
						if from_id == 'envelope2': 
							vital_from = 'env_2'
							#modamt *= modenv[1]
						if from_id == 'envelope3': 
							vital_from = 'env_3'
							#modamt *= modenv[2]
						if from_id == 'envelope4': 
							vital_from = 'env_4'
							#modamt *= modenv[3]

						if from_id == 'lfo1': 
							vital_from = 'lfo_1'
						if from_id == 'lfo2': 
							vital_from = 'lfo_2'
						if from_id == 'lfo3': 
							vital_from = 'lfo_3'

						if target_id == 'transposeA': vital_to = 'osc_1_transpose'
						if target_id == 'transposeB': vital_to = 'osc_2_transpose'
						if target_id == 'transposeSub': vital_to = 'osc_3_transpose'
						if target_id == 'spreadA': vital_to = 'osc_1_unison_detune'
						if target_id == 'spreadB': vital_to = 'osc_2_unison_detune'
						if target_id == 'filterCutoff': vital_to = 'filter_1_cutoff'
						if target_id == 'wtPosA': 
							vital_to = 'osc_1_wave_frame'
							modamt*=2
						if target_id == 'wtPosB': 
							vital_to = 'osc_2_wave_frame'
							modamt*=2

						if vital_from and vital_to:
							modulation_obj = plugin_obj.modulation_add_native(vital_from, vital_to)
							modulation_obj.amount = modamt

						modnum += 1
						#print(from_id, target_id, modamt)

				plugin_obj.env_asdr_copy('custom1', 'vital_env_1')
				plugin_obj.env_asdr_copy('custom2', 'vital_env_2')
				plugin_obj.env_asdr_copy('custom3', 'vital_env_3')
				plugin_obj.env_asdr_copy('custom4', 'vital_env_4')

				#params_vital.importcvpj_lfo('custom1')
				#params_vital.importcvpj_lfo('custom2')
				#params_vital.importcvpj_lfo('custom3')

				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		else: return False