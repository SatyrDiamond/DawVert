# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import struct
import os
import math
import lxml.etree as ET

from functions import note_data
from functions import data_bytes
from functions import xtramath
from functions import extpluglog
from objects.convproj import wave

from functions_plugin_ext import plugin_vst2

from functions_plugin_ext import params_os_juicysfplugin
from functions_plugin_ext import params_os_tal_chorus

simsynth_shapes = {0.4: 'random', 0.3: 'sine', 0.2: 'square', 0.1: 'saw', 0.0: 'triangle'}
wasp_shapes = {3: 'random', 2: 'sine', 1: 'square', 0: 'saw'}

def sinesq(x, i_var):
	return (((max(x-0.25, 0)*(5/4))**0.1)-0.5)*2

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'flstudio', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype):
		flpluginname = plugin_obj.type.subtype.lower()

		use_vst2 = 'vst2' in extplugtype

		#---------------------------------------- Fruit Kick ----------------------------------------
		if flpluginname == '3x osc':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Vital', '')
			exttype = plugins.base.extplug_exists('vital', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('FL Studio', '3x osc')

				fl_osc1_mixlevel = plugin_obj.params.get('osc1_mixlevel', 0).value/128
				fl_osc2_mixlevel = plugin_obj.params.get('osc2_mixlevel', 0).value/128

				fl_vol0 = 1.0*(-fl_osc1_mixlevel+1)*(-fl_osc2_mixlevel+1)
				fl_vol1 = fl_osc1_mixlevel*(-fl_osc2_mixlevel+1)
				fl_vol2 = fl_osc2_mixlevel

				oscdata = []
				for oscnum in range(3):
					starttxt = 'osc'+str(oscnum+1)+'_'
					fl_coarse = plugin_obj.params.get(starttxt+'coarse', 0).value
					fl_detune = plugin_obj.params.get(starttxt+'detune', 0).value
					fl_fine = plugin_obj.params.get(starttxt+'fine', 0).value
					fl_invert = plugin_obj.params.get(starttxt+'invert', 0).value
					fl_ofs = plugin_obj.params.get(starttxt+'ofs', 0).value/64
					fl_pan = plugin_obj.params.get(starttxt+'pan', 0).value/64
					fl_shape = plugin_obj.params.get(starttxt+'shape', 0).value
					oscdata.append([fl_coarse,fl_detune,fl_fine,fl_invert,fl_ofs,fl_pan,fl_shape,[fl_vol0,fl_vol1,fl_vol2][oscnum]])
	
				plugin_obj.replace('user', 'matt_tytel', 'vital')

				fl_osc3_am = plugin_obj.params.get('osc3_am', 0).value
				fl_phase_rand = plugin_obj.params.get('phase_rand', 0).value
	
				fl_vol0 = 1.0*(-fl_osc1_mixlevel+1)*(-fl_osc2_mixlevel+1)
				fl_vol1 = fl_osc1_mixlevel*(-fl_osc2_mixlevel+1)
				fl_vol2 = fl_osc2_mixlevel

				env_data = plugin_obj.env_asdr_get('vital_env_2')

				vollvl = abs(env_data.amount)
				osclvl = 1-vollvl
				noiselvl = 0

				plugin_obj.env_asdr_copy('vol', 'vital_env_2')

				plugin_obj.params.add('volume', 6000, 'float')

				plugin_obj.datavals_global.add('middlenotefix', -12)

				for oscnum, oscdata in enumerate(oscdata):
					fl_coarse,fl_detune,fl_fine,fl_invert,fl_ofs,fl_pan,fl_shape,fl_vol = oscdata
					#print(fl_coarse,fl_detune,fl_fine,fl_invert,fl_ofs,fl_pan,fl_shape,fl_vol)
					vital_oscnum = 'osc_'+str(oscnum+1)

					plugin_obj.params.add(vital_oscnum+'_on', 1, 'float')
					plugin_obj.params.add(vital_oscnum+'_level', (fl_vol)*2, 'float')
					plugin_obj.params.add(vital_oscnum+'_transpose', fl_coarse, 'float')
					plugin_obj.params.add(vital_oscnum+'_pan', fl_pan/100, 'float')
					plugin_obj.params.add(vital_oscnum+'_tune', fl_fine/100 , 'float')
					plugin_obj.params.add(vital_oscnum+'_unison_detune', (fl_detune*3.5)/50, 'float')
					plugin_obj.params.add(vital_oscnum+'_unison_voices', 2, 'float')

					osc_obj = plugin_obj.osc_add()
					osc_obj.prop.type = 'wave'
					osc_obj.prop.nameid = vital_oscnum

					wave_obj = plugin_obj.wave_add(vital_oscnum)
					wave_obj.set_numpoints(2048)
					if fl_shape == 0: wave_obj.add_wave('sine', 0, 1, 1)
					if fl_shape == 1: wave_obj.add_wave('triangle', 0, 1, 1)
					if fl_shape == 2: wave_obj.add_wave('square', 0, 1, 1)
					if fl_shape == 3: wave_obj.add_wave('saw', 0, 1, 1)
					if fl_shape == 4: wave_obj.add_wave_func(sinesq, 0, 1, 1)
					if fl_shape == 5: 
						noiselvl += (fl_vol/100)
						plugin_obj.datavals.add('sample_generate_noise', True)
						plugin_obj.params.add('sample_on', 1, 'float')

				plugin_obj.params.add('sample_level', min(noiselvl, 1), 'float')
				
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')

		#---------------------------------------- Fruit Kick ----------------------------------------
		if flpluginname == 'fruit kick':
			extpluglog.extpluglist.add('FOSS', 'VST2', 'Kickmess', '')
			exttype = plugins.base.extplug_exists('kickmess', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('FL Studio', 'Fruit Kick')

				osc_dist = plugin_obj.params.get('osc_dist', 0).value/1280
				plugin_obj.plugts_transform('./data_ext/plugts/flstudio_vst.pltr', 'vst2_fruit_kick', convproj_obj, pluginid)
				if osc_dist != 0:
					plugin_obj.params.add('dist_on', 1, 'float')
					plugin_obj.params.add('dist_start', osc_dist, 'float')
					plugin_obj.params.add('dist_end', osc_dist, 'float')

				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		# ---------------------------------------- FL Keys ----------------------------------------
		if flpluginname == 'fl keys' and use_vst2:
			instrument = plugin_obj.datavals.get('instrument', 'mda Piano')
			if instrument in ['mda Piano', 'Grand Piano']:
				extpluglog.extpluglist.add('FOSS', 'VST2', 'Piano', 'MDA')
				if plugin_vst2.check_exists('id', 1296318832):
					extpluglog.extpluglist.success('FL Studio', 'FL Keys')
					plugin_obj.plugts_transform('./data_ext/plugts/flstudio_vst.pltr', 'vst2_fl_keys_piano', convproj_obj, pluginid)
					plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1296318832, 'param', None, 12)
					return True
			if instrument == 'Rhodes (mda ePiano)':
				extpluglog.extpluglist.add('FOSS', 'VST2', 'ePiano', 'MDA')
				if plugin_vst2.check_exists('id', 1296318821):
					extpluglog.extpluglist.success('FL Studio', 'FL Keys')
					plugin_obj.plugts_transform('./data_ext/plugts/flstudio_vst.pltr', 'vst2_fl_keys_epiano', convproj_obj, pluginid)
					plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1296318821, 'param', None, 12)
					return True

		# ---------------------------------------- DX10 ----------------------------------------
		elif flpluginname == 'fruity dx10' and use_vst2:
			extpluglog.extpluglist.add('FOSS', 'VST2', 'DX10', 'MDA')
			if plugin_vst2.check_exists('id', 1296318840):
				extpluglog.extpluglist.success('FL Studio', 'Fruity DX10')
				plugin_obj.plugts_transform('./data_ext/plugts/flstudio_vst.pltr', 'vst2_fruity_dx10', convproj_obj, pluginid)
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1296318840, 'param', None, 16)
				return True

		# ---------------------------------------- SimSynth ----------------------------------------
		elif flpluginname == 'simsynth':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Vital', '')
			exttype = plugins.base.extplug_exists('vital', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('FL Studio', 'SimSynth')

				osc_data = []
				for oscnum in range(3):
					starttextparam = 'osc'+str(oscnum+1)
					osc_shape = plugin_obj.params.get(starttextparam+'_shape', 0).value
					osc_pw = plugin_obj.params.get(starttextparam+'_pw', 0).value
					osc_o1 = int(plugin_obj.params.get(starttextparam+'_o1', 0).value)
					osc_o2 = int(plugin_obj.params.get(starttextparam+'_o2', 0).value)
					osc_on = float(plugin_obj.params.get(starttextparam+'_on', 0).value)
					osc_crs = plugin_obj.params.get(starttextparam+'_crs', 0).value
					osc_fine = plugin_obj.params.get(starttextparam+'_fine', 0).value
					osc_lvl = plugin_obj.params.get(starttextparam+'_lvl', 0).value
					osc_warm = int(plugin_obj.params.get(starttextparam+'_warm', 0).value)
					osc_lfo = float(plugin_obj.params.get(starttextparam+'_lfo', 0).value)
					osc_env = float(plugin_obj.params.get(starttextparam+'_env', 0).value)

					osc_pw = (osc_pw-0.5)*2

					osc_data.append([osc_shape,osc_pw,osc_o1,osc_o2,osc_on,osc_crs,osc_fine,osc_lvl,osc_warm,osc_lfo,osc_env])

					osc_obj = plugin_obj.osc_add()
					osc_obj.prop.type = 'wave'
					osc_obj.prop.nameid = starttextparam

					osc_shape = simsynth_shapes[osc_shape]

					wave_obj = plugin_obj.wave_add(starttextparam)
					wave_obj.set_numpoints(2048)
					wave_obj.add_wave(osc_shape, osc_pw, 1, 1)
					if osc_o1: wave_obj.add_wave(osc_shape, osc_pw, 2, 0.5)
					if osc_o2: wave_obj.add_wave(osc_shape, osc_pw, 4, 0.5)

				svf_cut = plugin_obj.params.get('svf_cut', 0).value
				svf_kb = plugin_obj.params.get('svf_kb', 0).value
				svf_emph = plugin_obj.params.get('svf_emph', 0).value
				svf_env = plugin_obj.params.get('svf_env', 0).value
				osc1_env = plugin_obj.params.get('osc1_env', 0).value
				osc2_env = plugin_obj.params.get('osc2_env', 0).value
				osc3_env = plugin_obj.params.get('osc3_env', 0).value

				lfo_del = plugin_obj.params.get('lfo_del', 0).value
				lfo_rate = plugin_obj.params.get('lfo_rate', 0).value
				lfo_shape = plugin_obj.params.get('lfo_shape', 0).value
				lfo_on = plugin_obj.params.get('lfo_on', 0).value
				lfo_retrigger = plugin_obj.params.get('lfo_retrigger', 0).value

				chorus_on = plugin_obj.params.get('svf_on', 0).value

				plugin_obj.replace('user', 'matt_tytel', 'vital')

				noisevol = 1

				for oscnum, osc_part in enumerate(osc_data):
					osc_shape,osc_pw,osc_o1,osc_o2,osc_on,osc_crs,osc_fine,osc_lvl,osc_warm,osc_lfo,osc_env = osc_part
					v_starttxt = 'osc_'+str(oscnum+1)

					plugin_obj.params.add(v_starttxt+'_on', osc_on, 'float')
					plugin_obj.params.add(v_starttxt+'_transpose', (osc_crs-0.5)*48, 'float')
					plugin_obj.params.add(v_starttxt+'_tune', (osc_fine-0.5)*2, 'float')
					plugin_obj.params.add(v_starttxt+'_level', osc_lvl, 'float')
					if osc_warm == 1:
						plugin_obj.params.add(v_starttxt+'_unison_detune', 2.2, 'float')
						plugin_obj.params.add(v_starttxt+'_unison_voices', 6, 'float')

					modulation_obj = plugin_obj.modulation_add_native('env_2', v_starttxt+'_transpose')
					modulation_obj.amount = (osc_env-0.5)*0.5
					modulation_obj.bipolar = True

					modulation_obj = plugin_obj.modulation_add()
					modulation_obj.source = ['lfo', 'simsynth_lfo']
					modulation_obj.destination = ['native', v_starttxt+'_transpose']
					modulation_obj.amount = ((osc_lfo-0.5)*0.5)/2

					if osc_shape == 0.4:
						plugin_obj.params.add('sample_on', 1, 'float')
						plugin_obj.datavals.add('sample_generate_noise', True)
						noisevol *= osc_lvl
					
				plugin_obj.params.add('sample_level', noisevol, 'float')

				plugin_obj.env_asdr_copy('vol', 'vital_env_1')
				plugin_obj.env_asdr_copy('cutoff', 'vital_env_2')

				outfilter = 100
				outfilter += (svf_cut-0.5)*40
				outfilter += (svf_kb-0.5)*10

				plugin_obj.params.add('filter_fx_resonance', svf_emph*0.8, 'float')
				plugin_obj.params.add('filter_fx_cutoff', outfilter, 'float')
				plugin_obj.params.add('filter_fx_on', 1, 'float')

				modulation_obj = plugin_obj.modulation_add_native('env_2', 'filter_fx_cutoff')
				modulation_obj.amount = svf_env*0.6

				hzdata = 2**(((1+(lfo_rate*998))-500)/100)

				outlfoname = 'simsynth_lfo'
				lfo_obj = plugin_obj.lfo_add(outlfoname)
				lfo_obj.time.set_hz(hzdata*2 if lfo_shape in [0.1, 0.4] else hzdata)
				lfo_obj.prop.type = 'shape'
				lfo_obj.prop.shape = simsynth_shapes[lfo_shape]

				plugin_obj.params.add('chorus_mod_depth', 0.35, 'float')
				plugin_obj.params.add('chorus_delay_1', -9.5, 'float')
				plugin_obj.params.add('chorus_delay_2', -9.0, 'float')
				if chorus_on != 0: plugin_obj.params.add('chorus_on', 1.0, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		# ---------------------------------------- Wasp ----------------------------------------
		elif flpluginname == 'wasp':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Vital', '')
			exttype = plugins.base.extplug_exists('vital', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('FL Studio', 'WASP')

				fade12 = plugin_obj.params.get('12_fade', 0).value/128
				pw = plugin_obj.params.get('pw', 0).value/128

				crs_1 = plugin_obj.params.get('1_crs', 0).value
				fine_1 = plugin_obj.params.get('1_fine', 0).value
				shape_1 = plugin_obj.params.get('1_shape', 0).value

				crs_2 = plugin_obj.params.get('2_crs', 0).value
				fine_2 = plugin_obj.params.get('2_fine', 0).value
				shape_2 = plugin_obj.params.get('2_shape', 0).value

				amt_3 = plugin_obj.params.get('3_amt', 0).value/128
				shape_3 = plugin_obj.params.get('3_shape', 0).value

				amp_A = (plugin_obj.params.get('amp_A', 0).value/64)**5
				amp_D = (plugin_obj.params.get('amp_D', 0).value/64)**5
				amp_S = plugin_obj.params.get('amp_S', 0).value/128
				amp_R = (plugin_obj.params.get('amp_R', 0).value/64)**5

				fil_A = (plugin_obj.params.get('fil_A', 0).value/64)**5
				fil_D = (plugin_obj.params.get('fil_D', 0).value/64)**5
				fil_S = plugin_obj.params.get('fil_S', 0).value/128
				fil_R = (plugin_obj.params.get('fil_R', 0).value/64)**5

				fil_cut = plugin_obj.params.get('fil_cut', 0).value/512
				fil_env = plugin_obj.params.get('fil_env', 0).value/128
				fil_kbtrack = plugin_obj.params.get('fil_kbtrack', 0).value
				fil_qtype = plugin_obj.params.get('fil_qtype', 0).value
				fil_res = plugin_obj.params.get('fil_res', 0).value/128

				crs_1 = ((crs_1-64)/(64/36)).__floor__()
				crs_2 = ((crs_2-64)/(64/36)).__floor__()

				fine_1 = ((fine_1-64)/(64/50)).__floor__()
				fine_2 = ((fine_2-64)/(64/50)).__floor__()

				asdr_obj = plugin_obj.env_asdr_add('vital_env_1', 0, amp_A/4, 0, amp_D/4, amp_S/4, amp_R/4, 1)
				asdr_obj.attack_tension = -5
				asdr_obj.decay_tension = -5
				asdr_obj.release_tension = -5

				asdr_obj = plugin_obj.env_asdr_add('vital_env_2', 0, fil_A/4, 0, fil_D/4, fil_S/4, fil_R/4, 1)
				asdr_obj.attack_tension = -5
				asdr_obj.decay_tension = -5
				asdr_obj.release_tension = -5

				osc_obj = plugin_obj.osc_add()
				osc_obj.prop.type = 'shape'
				osc_obj.prop.shape = wasp_shapes[shape_1]
				osc_obj.prop.pulse_width = (pw/2)+0.5

				osc_obj = plugin_obj.osc_add()
				osc_obj.prop.type = 'shape'
				osc_obj.prop.shape = wasp_shapes[shape_2]
				osc_obj.prop.pulse_width = (pw/2)+0.5

				osc_obj = plugin_obj.osc_add()
				osc_obj.prop.type = 'shape'
				osc_obj.prop.shape = 'square' if shape_3 else 'saw'

				for x in range(1,3):
					w_starttxt = 'lfo'+str(x)+'_'
					amt = (plugin_obj.params.get(w_starttxt+'amt', 0).value/128)**2
					reset = plugin_obj.params.get(w_starttxt+'reset', 0).value
					shape = plugin_obj.params.get(w_starttxt+'shape', 0).value
					spd = (plugin_obj.params.get(w_starttxt+'spd', 0).value/128)
					sync = plugin_obj.params.get(w_starttxt+'sync', 0).value
					target = plugin_obj.params.get(w_starttxt+'target', 0).value

					modto = []
					if x == 1:
						if target == 0: modto += [['osc_1_transpose', 0.1], ['osc_2_transpose', 0.1], ['osc_3_transpose', 0.1]]
						if target == 1: modto += [['filter_1_cutoff', 0.5]]
						if target == 2: modto += [['osc_1_wave_frame', 1], ['osc_2_wave_frame', 1], ['osc_3_wave_frame', 1]]

					if x == 2:
						if target == 0: modto += [['osc_1_transpose', 1], ['osc_3_transpose', 1]]
						if target == 1: modto += [['osc_1_level', -1], ['osc_2_level', 1]]
						if target == 2: modto += [['volume', 0.5]]

					outlfoname = 'wasp_lfo'+str(x)
					lfo_obj = plugin_obj.lfo_add(outlfoname)
					lfo_obj.time.set_seconds(1/((spd+0.1)*3))

					lfo_obj.prop.type = 'shape'
					lfo_obj.prop.shape = wasp_shapes[shape_1]

					if shape == 0: lfo_obj.prop.shape = 'saw'
					if shape == 1: lfo_obj.prop.shape = 'square'
					if shape == 2: lfo_obj.prop.shape = 'sine'
					if shape == 3: lfo_obj.prop.shape = 'random'

					for m, v in modto:
						modulation_obj = plugin_obj.modulation_add()
						modulation_obj.source = ['lfo', outlfoname]
						modulation_obj.destination = ['native', m]
						modulation_obj.amount = v*(amt**1.2)
						modulation_obj.bipolar = True

				plugin_obj.replace('user', 'matt_tytel', 'vital')

				plugin_obj.params.add('osc_1_on', 1, 'float')
				plugin_obj.params.add('osc_1_transpose', crs_1, 'float')
				plugin_obj.params.add('osc_1_tune', fine_1/100, 'float')
				plugin_obj.params.add('osc_1_level', 1-fade12, 'float')
				plugin_obj.params.add('osc_1_destination', 0, 'float')

				plugin_obj.params.add('osc_2_on', 1, 'float')
				plugin_obj.params.add('osc_2_transpose', crs_2, 'float')
				plugin_obj.params.add('osc_2_tune', fine_2/100, 'float')
				plugin_obj.params.add('osc_2_level', fade12, 'float')
				plugin_obj.params.add('osc_2_destination', 0, 'float')

				plugin_obj.params.add('osc_3_on', 1, 'float')
				plugin_obj.params.add('osc_3_transpose', crs_1-12, 'float')
				plugin_obj.params.add('osc_3_level', amt_3/2, 'float')
				plugin_obj.params.add('osc_3_destination', 0, 'float')

				plugin_obj.params.add('sample_destination', 0, 'float')

				plugin_obj.params.add('filter_1_on', 1, 'float')
				plugin_obj.params.add('filter_1_cutoff', (fil_cut**0.6)*128, 'float')
				plugin_obj.params.add('filter_1_model', 3, 'float')
				plugin_obj.params.add('filter_1_resonance', (fil_res**0.2)/1.3, 'float')
				plugin_obj.params.add('filter_1_keytrack', fil_kbtrack/2, 'float')
				if fil_qtype == [1, 2, 3]: plugin_obj.params.add('filter_1_style', 2, 'float')
				if fil_qtype == 3: 
					plugin_obj.params.add('filter_1_blend', 1, 'float')
					plugin_obj.params.add('filter_1_style', 2, 'float')
				if fil_qtype == 4: plugin_obj.params.add('filter_1_blend', 1, 'float')
				if fil_qtype == 5: plugin_obj.params.add('filter_1_blend', 2, 'float')

				modulation_obj = plugin_obj.modulation_add_native('env_2', 'filter_1_cutoff')
				modulation_obj.amount = fil_env/2
				modulation_obj.bipolar = True

				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True


		# ---------------------------------------- fruity bass boost ----------------------------------------
		elif flpluginname == 'fruity bass boost':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Weight', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Weight')
			if exttype:
				extpluglog.extpluglist.success('FL Studio', 'Fruity Bass Boost')
				plugin_obj.plugts_transform('./data_ext/plugts/flstudio_vst.pltr', 'vst2_fruity_bass_boost', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		# ---------------------------------------- Fruity Fast Dist ----------------------------------------
		elif flpluginname == 'fruity fast dist':
			d_type = plugin_obj.params.get('type', 0).value
			if d_type == 0:
				extpluglog.extpluglist.add('FOSS', 'VST', 'Mackity', 'Airwindows')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Mackity')
				if exttype:
					extpluglog.extpluglist.success('FL Studio', 'Fruity Fast Dist')
					plugin_obj.plugts_transform('./data_ext/plugts/flstudio_vst.pltr', 'vst2_fruity_fast_dist_type1', convproj_obj, pluginid)
					plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
					return True
			if d_type == 1 and use_vst2:
				extpluglog.extpluglist.add('FOSS', 'VST2', 'Overdrive', 'MDA')
				if plugin_vst2.check_exists('id', 1835295055):
					extpluglog.extpluglist.success('FL Studio', 'Fruity Fast Dist')
					plugin_obj.plugts_transform('./data_ext/plugts/flstudio_vst.pltr', 'vst2_fruity_fast_dist_type2', convproj_obj, pluginid)
					plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1835295055, 'param', None, 3)
					return True

		# ---------------------------------------- fruity phase inverter ----------------------------------------
		elif flpluginname == 'fruity phase inverter':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Flipity', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Flipity')
			if exttype:
				extpluglog.extpluglist.success('FL Studio', 'Fruity Phase Inverter')
				stateval = int((plugin_obj.params.get('state', 0).value/1024)*3)
				flipstate = 0
				if stateval == 1: flipstate = 1
				if stateval == 2: flipstate = 2
				outval = (flipstate/8)+0.01
				plugin_obj.replace('user', 'airwindows', 'Flipity')
				plugin_obj.params.add('flipity', outval, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		# ---------------------------------------- fruity phaser ----------------------------------------
		elif flpluginname == 'fruity phaser' and use_vst2:
			extpluglog.extpluglist.add('FOSS', 'VST2', 'SupaPhaser', '')
			if plugin_vst2.check_exists('id', 1095988560):
				extpluglog.extpluglist.success('FL Studio', 'Fruity Phaser')
				plugin_obj.plugts_transform('./data_ext/plugts/flstudio_vst.pltr', 'vst2_fruity_phaser', convproj_obj, pluginid)
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1095988560, 'param', None, 16)
				return True

		# ---------------------------------------- fruity spectroman ----------------------------------------
		elif flpluginname == 'fruity spectroman':
			extpluglog.extpluglist.add('FOSS', 'VST', 'SpectrumAnalyzer', 'SocaLabs')
			exttype = plugins.base.extplug_exists('socalabs', extplugtype, 'spectrumanalyzer')
			if exttype:
				extpluglog.extpluglist.success('FL Studio', 'Fruity Spectroman')
				plugin_obj.plugts_transform('./data_ext/plugts/flstudio_vst.pltr', 'fruity_spectroman__socalabs', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		# ---------------------------------------- fruity stereo enhancer ----------------------------------------
		elif flpluginname == 'fruity stereo enhancer':
			extpluglog.extpluglist.add('FOSS', 'VST', 'StereoProcessor', 'SocaLabs')
			exttype = plugins.base.extplug_exists('socalabs', extplugtype, 'stereoprocessor')
			if exttype:
				extpluglog.extpluglist.success('FL Studio', 'Fruity Stereo Enhancer')
				plugin_obj.plugts_transform('./data_ext/plugts/flstudio_vst.pltr', 'fruity_stereo_enhancer__socalabs', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		# ---------------------------------------- fruity waveshaper ----------------------------------------
		elif flpluginname == 'fruity waveshaper':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Wolf Shaper', '')
			exttype = plugins.base.extplug_exists('wolfshaper', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('FL Studio', 'Fruity Waveshaper')
				plugin_obj.plugts_transform('./data_ext/plugts/flstudio_vst.pltr', 'fruity_waveshaper__wolfshaper', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		# ---------------------------------------- Vintage Chorus ----------------------------------------
		elif flpluginname == 'vintage chorus' and use_vst2:
			extpluglog.extpluglist.add('FOSS', 'VST2', 'TAL-Chorus-LX', '')
			if plugin_vst2.check_exists('id', 1665682481):
				extpluglog.extpluglist.success('FL Studio', 'Vintage Chorus')
				c_mode = plugin_obj.params.get('mode', 0).value
				data_tal_c = params_os_tal_chorus.tal_chorus_data()
				data_tal_c.set_param('volume', 0.5)
				data_tal_c.set_param('drywet', 0.5)
				data_tal_c.set_param('stereowidth', 1.0)
				data_tal_c.set_param('chorus1enable', float(c_mode == 0))
				data_tal_c.set_param('chorus2enable', float(c_mode > 0))
				data_tal_c.to_cvpj_vst2(convproj_obj, plugin_obj)
				return True
