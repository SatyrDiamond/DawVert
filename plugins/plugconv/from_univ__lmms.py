# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

from functions import data_bytes
from functions import xtramath
from objects import globalstore
import os

def filternum(i_filtertype):
	i_type = i_filtertype.type
	i_subtype = i_filtertype.subtype

	lmms_filternum = 0
	if i_type == 'all_pass': lmms_filternum = 5

	if i_type == 'band_pass':
		if i_subtype == 'csg': lmms_filternum = 2
		if i_subtype == 'czpg': lmms_filternum = 3
		if i_subtype == 'rc12': lmms_filternum = 9
		if i_subtype == 'rc24': lmms_filternum = 12
		if i_subtype == 'sv': lmms_filternum = 17

	if i_type == 'formant':
		lmms_filternum = 14
		if i_subtype == 'fast': lmms_filternum = 20

	if i_type == 'high_pass':
		lmms_filternum = 1
		if i_subtype == 'rc12': lmms_filternum = 10
		if i_subtype == 'rc24': lmms_filternum = 13
		if i_subtype == 'sv': lmms_filternum = 18

	if i_type == 'low_pass':
		lmms_filternum = 0
		if i_subtype == 'double': lmms_filternum = 7
		if i_subtype == 'rc12': lmms_filternum = 8
		if i_subtype == 'rc24': lmms_filternum = 11
		if i_subtype == 'sv': lmms_filternum = 16

	if i_type == 'moog':
		lmms_filternum = 6
		if i_subtype == 'double': lmms_filternum = 15

	if i_type == 'notch':
		lmms_filternum = 4
		if i_subtype == 'sv': lmms_filternum = 19

	if i_type == 'tripole':
		lmms_filternum = 21

	return lmms_filternum

def getslope(slopeval):
	outval = 0
	if slopeval > 24: outval = 1
	if slopeval > 48: outval = 2
	return outval

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'
	
	def get_priority(self):
		return 100
	
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = 'universal'
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = ['native:lmms']
		in_dict['out_daws'] = ['lmms']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.type.check_wildmatch('universal', 'synth-osc', None):
			samplefolder = dawvert_intent.path_samples['generated']

			osc_data = plugin_obj.state.oscs

			if len(osc_data) == 1 and not plugin_obj.env_blocks_get_exists('vol')[0] and not plugin_obj.env_points_get_exists('vol')[0]:
				osc_obj = osc_data[0]

				if osc_obj.prop.shape == 'square':
					plugin_obj.replace('native', 'lmms', 'monstro')
					plugin_obj.params.add('o1vol', 50, 'int')
					plugin_obj.params.add('o2vol', 0, 'int')
					plugin_obj.params.add('o3vol', 0, 'int')
					plugin_obj.params.add('o1crs', -12, 'int')
					plugin_obj.params.add('o1pw', osc_obj.prop.pulse_width*100, 'int')
					return True

				elif osc_obj.prop.shape in ['triangle', 'pulse', 'saw', 'sine'] or osc_obj.prop.type == 'wave':
					plugin_obj.replace('native', 'lmms', 'tripleoscillator')
					plugin_obj.params.add('coarse0', -12, 'int')
					plugin_obj.params.add('finel0', 0, 'int')
					plugin_obj.params.add('finer0', 0, 'int')
					plugin_obj.params.add('pan0', 0, 'int')
					plugin_obj.params.add('phoffset0', 0, 'int')
					plugin_obj.params.add('stphdetun0', 0, 'int')
					plugin_obj.params.add('vol0', 33, 'int')
					plugin_obj.params.add('vol1', 0, 'int')
					plugin_obj.params.add('vol2', 0, 'int')
					plugin_obj.params.add('wavetype0', 0, 'int')
					if osc_obj.prop.shape == 'sine': plugin_obj.params.add('wavetype0', 0, 'int')
					if osc_obj.prop.shape == 'pulse': plugin_obj.params.add('wavetype0', 3, 'int')
					if osc_obj.prop.shape == 'square': plugin_obj.params.add('wavetype0', 3, 'int')
					if osc_obj.prop.shape == 'triangle': plugin_obj.params.add('wavetype0', 1, 'int')
					if osc_obj.prop.shape == 'saw': plugin_obj.params.add('wavetype0', 2, 'int')
					if osc_obj.prop.type == 'wave':
						plugin_obj.params.add('wavetype0', 7, 'int')
						wave_path = os.path.join(samplefolder, pluginid+'_wave.wav')
						wave_obj = plugin_obj.wave_get(osc_obj.prop.nameid)
						wave_obj.to_audio(wave_path)
						convproj_obj.sampleref__add(pluginid+'_wave', wave_path, None)
						sp_obj = plugin_obj.samplepart_add('userwavefile0')
						sp_obj.sampleref = pluginid+'_wave'
					return True

		if plugin_obj.eq_to_bands(convproj_obj, pluginid):
			eqbands = [x for x in plugin_obj.state.eq]
			fil_hp = plugin_obj.named_filter_get('high_pass')
			fil_ls = plugin_obj.named_filter_get('low_shelf')
			fil_pd = [plugin_obj.named_filter_get('peak_'+str(peak_num+1)) for peak_num in range(4)]
			fil_hs = plugin_obj.named_filter_get('high_shelf')
			fil_lp = plugin_obj.named_filter_get('low_pass')

			plugin_obj.replace('native', 'lmms', 'eq')

			plugin_obj.params.add('HPactive', int(fil_hp.on), 'float')
			plugin_obj.params.add('HPfreq', fil_hp.freq, 'float')
			plugin_obj.params.add('HPres', fil_hp.q, 'float')
			plugin_obj.params.add('HP', getslope(fil_hp.slope), 'float')
			convproj_obj.automation.move(['n_filter', pluginid, 'high_pass', 'on'], ['plugin', pluginid, "HPactive"])
			convproj_obj.automation.move(['n_filter', pluginid, 'high_pass', 'freq'], ['plugin', pluginid, "HPfreq"])

			plugin_obj.params.add('Lowshelfactive', int(fil_ls.on), 'float')
			plugin_obj.params.add('LowShelffreq', fil_ls.freq, 'float')
			plugin_obj.params.add('Lowshelfgain', fil_ls.gain, 'float')
			plugin_obj.params.add('LowShelfres', fil_ls.q, 'float')
			convproj_obj.automation.move(['n_filter', pluginid, 'low_shelf', 'on'], ['plugin', pluginid, "Lowshelfactive"])
			convproj_obj.automation.move(['n_filter', pluginid, 'low_shelf', 'freq'], ['plugin', pluginid, "LowShelffreq"])
			convproj_obj.automation.move(['n_filter', pluginid, 'low_shelf', 'gain'], ['plugin', pluginid, "Lowshelfgain"])

			for peak_num in range(4):
				fil_p = fil_pd[peak_num]
				peak_txt = 'Peak'+str(peak_num+1)
				filt_txt = 'peak_'+str(peak_num+1)
				plugin_obj.params.add(peak_txt+'active', int(fil_p.on), 'float')
				plugin_obj.params.add(peak_txt+'freq', fil_p.freq, 'float')
				plugin_obj.params.add(peak_txt+'gain', fil_p.gain, 'float')
				plugin_obj.params.add(peak_txt+'bw', fil_p.q**0.5, 'float')
				convproj_obj.automation.move(['n_filter', pluginid, filt_txt, 'on'], ['plugin', pluginid, peak_txt+'active'])
				convproj_obj.automation.move(['n_filter', pluginid, filt_txt, 'freq'], ['plugin', pluginid, peak_txt+'freq'])
				convproj_obj.automation.move(['n_filter', pluginid, filt_txt, 'gain'], ['plugin', pluginid, peak_txt+'gain'])

			plugin_obj.params.add('Highshelfactive', int(fil_hs.on), 'float')
			plugin_obj.params.add('Highshelffreq', fil_hs.freq, 'float')
			plugin_obj.params.add('HighShelfgain', fil_hs.gain, 'float')
			plugin_obj.params.add('HighShelfres', fil_hs.q, 'float')
			convproj_obj.automation.move(['n_filter', pluginid, 'high_shelf', 'on'], ['plugin', pluginid, "Highshelfactive"])
			convproj_obj.automation.move(['n_filter', pluginid, 'high_shelf', 'freq'], ['plugin', pluginid, "Highshelffreq"])
			convproj_obj.automation.move(['n_filter', pluginid, 'high_shelf', 'gain'], ['plugin', pluginid, "HighShelfgain"])

			plugin_obj.params.add('LPactive', int(fil_lp.on), 'float')
			plugin_obj.params.add('LPfreq', fil_lp.freq, 'float')
			plugin_obj.params.add('LPres', fil_lp.q, 'float')
			plugin_obj.params.add('LP', getslope(fil_lp.slope), 'float')
			convproj_obj.automation.move(['n_filter', pluginid, 'low_pass', 'on'], ['plugin', pluginid, "LPactive"])
			convproj_obj.automation.move(['n_filter', pluginid, 'low_pass', 'freq'], ['plugin', pluginid, "LPfreq"])
			return True
