# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog

op_3osc_shape = {
	0: 0,
	1: 19,
	2: 18,
	3: 10,
	4: 12,
	5: 21,
	6: 4
}

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self, plugconv_obj): 
		plugconv_obj.in_plugins = [['native-flstudio', None]]
		plugconv_obj.in_daws = ['flstudio']
		plugconv_obj.out_plugins = [['native-ableton', None]]
		plugconv_obj.out_daws = ['ableton']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):

		if plugin_obj.type.subtype == 'fruity balance':
			extpluglog.convinternal('FL Studio', 'Fruity Balance', 'Ableton', 'StereoGain')
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('pan', 'pan', 0)
			manu_obj.from_param('vol', 'vol', 256)
			manu_obj.calc('vol', 'div', 256, 0, 0, 0)
			manu_obj.calc('pan', 'div', 128, 0, 0, 0)
			plugin_obj.replace('native-ableton', 'StereoGain')
			manu_obj.to_param('vol', 'Gain', None)
			manu_obj.to_param('pan', 'Balance', None)

		if plugin_obj.type.subtype == 'fruity center':
			extpluglog.convinternal('FL Studio', 'Fruity Center', 'Ableton', 'StereoGain')
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('on', 'on', 0)
			plugin_obj.replace('native-ableton', 'StereoGain')
			manu_obj.to_param('on', 'DcFilter', None)

		if plugin_obj.type.subtype == '3x osc':
			extpluglog.convinternal('FL Studio', '3xOsc', 'Ableton', 'Operator')
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

			osc_vol0 = 1.0*(-fl_osc1_mixlevel+1)*(-fl_osc2_mixlevel+1)
			osc_vol1 = fl_osc1_mixlevel*(-fl_osc2_mixlevel+1)
			osc_vol2 = fl_osc2_mixlevel

			osc1_freq = (fl_osc1_coarse + fl_osc1_fine/100)/12
			osc2_freq = (fl_osc2_coarse + fl_osc2_fine/100)/12
			osc3_freq = (fl_osc3_coarse + fl_osc3_fine/100)/12

			

			plugin_obj.replace('native-ableton', 'Operator')

			plugin_obj.params.add('Operator.0/IsOn', True, 'bool')
			plugin_obj.params.add('Operator.1/IsOn', True, 'bool')
			plugin_obj.params.add('Operator.2/IsOn', True, 'bool')

			plugin_obj.params.add('Operator.0/WaveForm', op_3osc_shape[fl_osc1_shape], 'int')
			plugin_obj.params.add('Operator.1/WaveForm', op_3osc_shape[fl_osc2_shape], 'int')
			plugin_obj.params.add('Operator.2/WaveForm', op_3osc_shape[fl_osc3_shape], 'int')

			plugin_obj.params.add('Operator.0/Envelope/SustainLevel', 1, 'float')
			plugin_obj.params.add('Operator.1/Envelope/SustainLevel', 1, 'float')
			plugin_obj.params.add('Operator.2/Envelope/SustainLevel', 1, 'float')

			plugin_obj.params.add('Operator.0/Tune/Coarse', (osc1_freq//1)+2, 'float')
			plugin_obj.params.add('Operator.0/Tune/Fine', (osc1_freq%1)*800, 'float')

			plugin_obj.params.add('Operator.1/Tune/Coarse', (osc2_freq//1)+2, 'float')
			plugin_obj.params.add('Operator.1/Tune/Fine', (osc2_freq%1)*800, 'float')

			plugin_obj.params.add('Operator.2/Tune/Coarse', (osc3_freq//1)+2, 'float')
			plugin_obj.params.add('Operator.2/Tune/Fine', (osc3_freq%1)*800, 'float')

			plugin_obj.params.add('Operator.0/Volume', osc_vol0, 'float')
			plugin_obj.params.add('Operator.1/Volume', osc_vol1, 'float')
			plugin_obj.params.add('Operator.2/Volume', osc_vol2, 'float')

			adsr_obj = plugin_obj.env_asdr_get('vol')
			for n in range(3):
				starttxt = 'Operator.'+str(n)
				plugin_obj.params.add(starttxt+'/Envelope/AttackTime', adsr_obj.attack*1000, 'float')
				plugin_obj.params.add(starttxt+'/Envelope/DecayTime', adsr_obj.decay*1000, 'float')
				plugin_obj.params.add(starttxt+'/Envelope/SustainLevel', adsr_obj.sustain, 'float')
				plugin_obj.params.add(starttxt+'/Envelope/ReleaseTime', adsr_obj.release*1000, 'float')

				plugin_obj.params.add(starttxt+'/Envelope/AttackSlope', -adsr_obj.attack_tension, 'float')
				plugin_obj.params.add(starttxt+'/Envelope/DecaySlope', -adsr_obj.decay_tension, 'float')
				plugin_obj.params.add(starttxt+'/Envelope/ReleaseSlope', -adsr_obj.release_tension, 'float')

			plugin_obj.params.add('Globals/Algorithm', 10, 'int')
			

		return 2
