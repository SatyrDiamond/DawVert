# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import struct
from functions_plugin_ext import plugin_vst2
from objects.convproj import wave
from functions import extpluglog
from functions import xtramath
import numpy as np
import math
import logging

logger_plugconv = logging.getLogger('plugconv')

WAVE_SIZE = 2048
WAVE_NUMPOINTS = 32

class wavestore():
	waves = {}

	def create(shape, plugin_obj): 
		if shape not in wavestore.waves:
			shapedata = np.zeros([WAVE_NUMPOINTS, WAVE_SIZE], dtype=np.float32)

			shapedata[::] = np.arange(WAVE_SIZE)
			shapedata[::] /= WAVE_SIZE

			if shape == 'sine':
				for n, w in enumerate(shapedata):
					for p in range(WAVE_SIZE): 
						w[p] = math.sin(((w[p]-0.25)*math.pi)*2)

			if shape == 'triangle':
				for n, w in enumerate(shapedata):
					amt = n/WAVE_NUMPOINTS
					w *= 1+(amt*10)
					np.minimum(w, 1, out=w)
					for p in range(WAVE_SIZE): 
						w[p] = (abs(((w[p]+0.25)*2)%(2)-1)-0.5)*2

			if shape == 'square':
				shapedata[::] = -1
				for n, w in enumerate(shapedata):
					amt = n/WAVE_NUMPOINTS
					amt *= 0.45
					amt += 0.5
					w[int(amt*WAVE_SIZE):WAVE_SIZE] = 1

			if shape == 'saw':
				for n, w in enumerate(shapedata):
					amt = (n/WAVE_NUMPOINTS)*2
					w *= 1+amt
					w %= 1
					w -= 0.5
					w *= 2

			wavestore.waves[shape] = shapedata
			wavetable_obj = plugin_obj.wavetable_add(shape)
			wavetable_obj.full_normalize = False
			wavetable_obj.remove_all_dc = False
			wavetable_src = wavetable_obj.add_source()

			for n, w in enumerate(wavestore.waves[shape]):
				waveid = shape+str(n)
				wave_obj = plugin_obj.wave_add(shape+str(n))
				wave_obj.set_all_range(list(w), 0, 1)
				wt_part = wavetable_src.parts.add_pos(n/WAVE_NUMPOINTS)
				wt_part.wave_id = waveid
			
		osc_obj = plugin_obj.osc_add()
		osc_obj.prop.type = 'wavetable'
		osc_obj.prop.nameid = shape


class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'amped', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):
		global loaded_plugtransform
		global plugts_obj

		if plugin_obj.type.subtype == 'VoltMini':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Vital', '')
			exttype = plugins.base.extplug_exists('vital', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('Amped Studio', 'Volt Mini')
	
				osc_active = plugin_obj.params.get("part/1/osc/1/active", 0).value
				osc_wave = int(plugin_obj.params.get("part/1/osc/1/wave", 0).value)
				osc_active = plugin_obj.params.get("part/1/osc/1/active", 0).value
				osc_unison = plugin_obj.params.get("part/1/osc/1/unison", 0).value
				osc_detune = plugin_obj.params.get("part/1/osc/1/detune", 0).value
				osc_octave = plugin_obj.params.get("part/1/osc/1/octave", 0).value
				osc_coarse = plugin_obj.params.get("part/1/osc/1/coarse", 0).value
				osc_fine = plugin_obj.params.get("part/1/osc/1/fine", 0).value
				osc_shape = plugin_obj.params.get("part/1/osc/1/shape", 0).value
				osc_gain = plugin_obj.params.get("part/1/osc/1/gain", 0).value
				osc_pan = plugin_obj.params.get("part/1/osc/1/pan", 0).value
	
				mod_pitch = plugin_obj.params.get("part/1/eg/1/pitch", 0).value
				mod_shape = plugin_obj.params.get("part/1/eg/1/shape", 0).value
				mod_detune = plugin_obj.params.get("part/1/eg/1/detune", 0).value

				wlfo_pitch = plugin_obj.params.get("part/1/lfo/1/pitch", 0).value
				wlfo_shape = plugin_obj.params.get("part/1/lfo/1/shape", 0).value
				wlfo_gain = plugin_obj.params.get("part/1/lfo/1/gain", 0).value
				wlfo_pan = plugin_obj.params.get("part/1/lfo/1/pan", 0).value

				lfo_amp = plugin_obj.params.get("part/1/lfo/3/amp", 0).value

				plugin_obj.replace('user', 'matt_tytel', 'vital')

				plugin_obj.env_asdr_copy('vol', 'vital_env_1')
				plugin_obj.env_asdr_copy('cutoff', 'vital_env_2')
				plugin_obj.env_asdr_copy('modenv', 'vital_env_3')

				amount_env = plugin_obj.env_asdr_get('vital_env_2')
				modlvl_env = plugin_obj.env_asdr_get('vital_env_3')

				amount = amount_env.amount
				modlvl = modlvl_env.amount

				modulation_obj = plugin_obj.modulation_add_native('env_2', 'filter_fx_cutoff')
				modulation_obj.amount = amount/6000

				modulation_obj = plugin_obj.modulation_add_native('env_3', 'osc_1_transpose')
				modulation_obj.amount = ((mod_pitch*modlvl)**4)/4
				modulation_obj.bipolar = True

				modulation_obj = plugin_obj.modulation_add_native('env_3', 'osc_1_wave_frame')
				modulation_obj.amount = mod_shape*modlvl
				modulation_obj.bipolar = True

				modulation_obj = plugin_obj.modulation_add_native('env_3', 'osc_1_unison_detune')
				modulation_obj.amount = (mod_detune*modlvl)*2
				modulation_obj.bipolar = True

				modulation_obj = plugin_obj.modulation_add()
				modulation_obj.source = ['lfo', 'modenv']
				modulation_obj.destination = ['native', 'osc_1_transpose']
				modulation_obj.amount = (wlfo_pitch**4)/4
				modulation_obj.bipolar = True

				modulation_obj = plugin_obj.modulation_add()
				modulation_obj.source = ['lfo', 'modenv']
				modulation_obj.destination = ['native', 'osc_1_level' if osc_wave != 4 else 'sample_level']
				modulation_obj.amount = wlfo_gain/2
				modulation_obj.bipolar = True

				modulation_obj = plugin_obj.modulation_add()
				modulation_obj.source = ['lfo', 'modenv']
				modulation_obj.destination = ['native', 'osc_1_pan' if osc_wave != 4 else 'sample_pan']
				modulation_obj.amount = wlfo_pan
				modulation_obj.bipolar = True

				modulation_obj = plugin_obj.modulation_add()
				modulation_obj.source = ['lfo', 'modenv']
				modulation_obj.destination = ['native', 'osc_1_wave_frame']
				modulation_obj.amount = wlfo_shape
				modulation_obj.bipolar = True

				modulation_obj = plugin_obj.modulation_add()
				modulation_obj.source = ['lfo', 'cutoff']
				modulation_obj.destination = ['native', 'lfo_amp']
				modulation_obj.amount = lfo_amp

				if osc_wave == 0: wavestore.create('sine', plugin_obj)
				if osc_wave == 1: wavestore.create('triangle', plugin_obj)
				if osc_wave == 2: wavestore.create('square', plugin_obj)
				if osc_wave == 3: wavestore.create('saw', plugin_obj)

				if osc_wave != 4:
					plugin_obj.params.add('osc_1_on', osc_active, 'float')
					plugin_obj.params.add('osc_1_level', osc_gain/2, 'float')
					plugin_obj.params.add('osc_1_pan', (osc_pan-0.5)*2, 'float')
					plugin_obj.params.add('osc_1_unison_detune', (osc_detune**3)*5, 'float')
					if osc_detune: plugin_obj.params.add('osc_1_unison_voices', osc_unison, 'float')
					plugin_obj.params.add('osc_1_transpose',(osc_octave*12)+osc_coarse, 'float')
					plugin_obj.params.add('osc_1_tune', osc_fine/100, 'float')
					plugin_obj.params.add('osc_1_wave_frame', osc_shape*256, 'float')
				else:
					plugin_obj.params.add('sample_on', osc_active, 'float')
					plugin_obj.params.add('sample_pan', (osc_pan-0.5)*2, 'float')
					plugin_obj.datavals.add('sample_generate_noise', True)

				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		if plugin_obj.type.subtype == 'Reverb':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Castello Reverb', '')
			exttype = plugins.base.extplug_exists('castello', extplugtype, 'castello')
			if exttype:
				extpluglog.extpluglist.success('Amped Studio', 'Reverb')
				plugin_obj.plugts_transform('./data_ext/plugts/amped_vst2.pltr', 'vst2_reverb', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		if plugin_obj.type.subtype == 'Distortion':
			distmode = plugin_obj.params.get('mode', 0).value
			boost = plugin_obj.params.get('boost', 0).value
			mix = plugin_obj.params.get('mix', 0).value

			if distmode in [0,1,4,5,6,7,8]:
				extpluglog.extpluglist.add('FOSS', 'VST', 'Density', 'Airwindows')
				plugin_obj.params_slot.add('wet', mix, 'float')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Density')
				if exttype:
					extpluglog.extpluglist.success('Amped Studio', 'Distortion')
					p_density = 0.2+(boost*0.3)
					p_outlvl = 1-(boost*(0.3 if distmode != 5 else 0.2))

					plugin_obj.replace('user', 'airwindows', 'Density')
					plugin_obj.params.add('density', p_density, 'float')
					plugin_obj.params.add('highpass', 0, 'float')
					plugin_obj.params.add('output', p_outlvl, 'float')
					plugin_obj.params.add('dry_wet', 1, 'float')
					plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
					return True

			if distmode in [2,3]:
				extpluglog.extpluglist.add('FOSS', 'VST', 'Drive', 'Airwindows')
				plugin_obj.params_slot.add('wet', mix, 'float')
				exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Drive')
				if exttype:
					extpluglog.extpluglist.success('Amped Studio', 'Distortion')
					p_drive = [0.6,0.8,1][int(boost)]

					plugin_obj.replace('user', 'airwindows', 'Drive')
					plugin_obj.params.add('drive', p_drive, 'float')
					plugin_obj.params.add('highpass', 0, 'float')
					plugin_obj.params.add('out_level', 0.5, 'float')
					plugin_obj.params.add('dry_wet', 1, 'float')
					plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
					return True

		if plugin_obj.type.subtype == 'CompressorMini':
			extpluglog.extpluglist.add('FOSS', 'VST', 'PurestSquish', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'PurestSquish')
			if exttype:
				extpluglog.extpluglist.success('Amped Studio', 'Compressor Mini')
				plugin_obj.plugts_transform('./data_ext/plugts/amped_vst2.pltr', 'vst2_compressormini', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		else: return False