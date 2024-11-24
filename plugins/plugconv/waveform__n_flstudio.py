# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog
from objects import globalstore

threeosc_shapes = {
	0: 1,
	1: 4,
	2: 2,
	3: 3,
	4: 2,
	5: 5,
	6: 4}

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'flstudio', None]]
		in_dict['in_daws'] = ['flp']
		in_dict['out_plugins'] = [['native', 'tracktion', None]]
		in_dict['out_daws'] = ['waveform_edit']
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.type.subtype == None: plugin_obj.type.subtype = ''
	
		if plugin_obj.type.subtype.lower() == 'fruity balance':  
			extpluglog.convinternal('FL Studio', 'Fruity Balance', 'Waveform', 'Volume')

			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('pan', 'pan', 0)
			manu_obj.from_param('vol', 'vol', 256)
			manu_obj.calc('vol', 'div', 256, 0, 0, 0)
			manu_obj.calc('pan', 'div', 128, 0, 0, 0)
			plugin_obj.replace('native', 'tracktion', 'volume')
			manu_obj.to_param('vol', 'volume', None)
			manu_obj.to_param('pan', 'pan', None)
			return 1
			
		if plugin_obj.type.subtype.lower() == 'fruity chorus':  
			extpluglog.convinternal('FL Studio', 'Fruity Chorus', 'Waveform', 'Chorus')
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_wet('wet', 1)
			manu_obj.from_param('delay', 'delay', 0)
			manu_obj.from_param('depth', 'depth', 0)
			manu_obj.from_param('freq', 'lfo1_freq', 0)
			manu_obj.calc('delay', 'valrange', 0, 1024, 0.05, 30)
			manu_obj.calc('depth', 'div', 1000, 0, 0, 0)
			manu_obj.calc('freq', 'div', 5000, 0, 0, 0)
			manu_obj.calc('freq', 'pow', 2, 0, 0, 0)
			manu_obj.calc('freq', 'mul', 5, 0, 0, 0)
			plugin_obj.replace('native', 'tracktion', 'chorusEffect')
			manu_obj.to_param('wet', 'mix', None)
			manu_obj.to_param('delay', 'delay', None)
			manu_obj.to_param('depth', 'depth', None)
			manu_obj.to_param('freq', 'rateSyncOff', None)
			return 0

		if plugin_obj.type.subtype.lower() == '3x osc':  
			extpluglog.convinternal('FL Studio', '3x Osc', 'Waveform', '4OSC')

			plugin_obj.datavals_global.add('middlenotefix', -12)

			fl_osc1_coarse = plugin_obj.params.get('osc1_coarse', 0).value
			fl_osc1_detune = plugin_obj.params.get('osc1_detune', 0).value
			fl_osc1_fine = plugin_obj.params.get('osc1_fine', 0).value
			fl_osc1_invert = plugin_obj.params.get('osc1_invert', 0).value
			fl_osc1_mixlevel = plugin_obj.params.get('osc1_mixlevel', 0).value/128
			fl_osc1_ofs = plugin_obj.params.get('osc1_ofs', 0).value/64
			fl_osc1_pan = plugin_obj.params.get('osc1_pan', 0).value/64
			fl_osc1_shape = plugin_obj.params.get('osc1_shape', 0).value

			fl_osc2_coarse = plugin_obj.params.get('osc2_coarse', 0).value
			fl_osc2_detune = plugin_obj.params.get('osc2_detune', 0).value
			fl_osc2_fine = plugin_obj.params.get('osc2_fine', 0).value
			fl_osc2_invert = plugin_obj.params.get('osc2_invert', 0).value
			fl_osc2_mixlevel = plugin_obj.params.get('osc2_mixlevel', 0).value/128
			fl_osc2_ofs = plugin_obj.params.get('osc2_ofs', 0).value/64
			fl_osc2_pan = plugin_obj.params.get('osc2_pan', 0).value/64
			fl_osc2_shape = plugin_obj.params.get('osc2_shape', 0).value

			fl_osc3_coarse = plugin_obj.params.get('osc3_coarse', 0).value
			fl_osc3_detune = plugin_obj.params.get('osc3_detune', 0).value
			fl_osc3_fine = plugin_obj.params.get('osc3_fine', 0).value
			fl_osc3_invert = plugin_obj.params.get('osc3_invert', 0).value
			fl_osc3_ofs = plugin_obj.params.get('osc3_ofs', 0).value/64
			fl_osc3_pan = plugin_obj.params.get('osc3_pan', 0).value/64
			fl_osc3_shape = plugin_obj.params.get('osc3_shape', 0).value

			mixvol_vol0 = (1.0*(-fl_osc1_mixlevel+1)*(-fl_osc2_mixlevel+1))**0.1
			mixvol_vol1 = (fl_osc1_mixlevel*(-fl_osc2_mixlevel+1))**0.1
			mixvol_vol2 = (fl_osc2_mixlevel)**0.1

			plugin_obj.replace('native', 'tracktion', '4osc')

			plugin_obj.params.add('waveShape1', threeosc_shapes[fl_osc1_shape], 'float')
			plugin_obj.params.add('waveShape2', threeosc_shapes[fl_osc2_shape], 'float')
			plugin_obj.params.add('waveShape3', threeosc_shapes[fl_osc3_shape], 'float')

			if fl_osc1_detune:
				plugin_obj.params.add('voices1', 2, 'float')
				plugin_obj.params.add('detune1', abs(fl_osc1_detune)/150, 'float')
			if fl_osc2_detune:
				plugin_obj.params.add('voices2', 2, 'float')
				plugin_obj.params.add('detune2', abs(fl_osc2_detune)/150, 'float')
			if fl_osc3_detune:
				plugin_obj.params.add('voices3', 2, 'float')
				plugin_obj.params.add('detune3', abs(fl_osc3_detune)/150, 'float')

			plugin_obj.params.add('tune1', fl_osc1_coarse, 'float')
			plugin_obj.params.add('fineTune1', fl_osc1_fine, 'float')
			plugin_obj.params.add('level1', ((-1)+mixvol_vol0)*100, 'float')
			plugin_obj.params.add('pan1', fl_osc1_pan, 'float')

			plugin_obj.params.add('tune2', fl_osc2_coarse, 'float')
			plugin_obj.params.add('fineTune2', fl_osc2_fine, 'float')
			plugin_obj.params.add('level2', ((-1)+mixvol_vol1)*100, 'float')
			plugin_obj.params.add('pan2', fl_osc2_pan, 'float')

			plugin_obj.params.add('tune3', fl_osc3_coarse, 'float')
			plugin_obj.params.add('fineTune3', fl_osc3_fine, 'float')
			plugin_obj.params.add('level3', ((-1)+mixvol_vol2)*100, 'float')
			plugin_obj.params.add('pan3', fl_osc3_pan, 'float')

			adsr_obj = plugin_obj.env_asdr_get('vol')
			plugin_obj.params.add('ampAttack', adsr_obj.attack, 'float')
			plugin_obj.params.add('ampDecay', adsr_obj.decay, 'float')
			plugin_obj.params.add('ampSustain', adsr_obj.sustain*100, 'float')
			plugin_obj.params.add('ampRelease', adsr_obj.release, 'float')

			poly_obj = plugin_obj.poly

			plugin_obj.params.add('voices', poly_obj.max if poly_obj.limited else 32, 'float')
			plugin_obj.params.add('voiceMode', 1 if poly_obj.slide_always else (2 if not poly_obj.mono else 0), 'float')
			plugin_obj.params.add('legato', poly_obj.porta_time.speed_seconds, 'float')
			return 0
			
		return 2
