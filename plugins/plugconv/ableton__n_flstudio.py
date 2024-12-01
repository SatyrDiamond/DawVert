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

def als_calc_pitch(infreq):
	Coarse = (infreq//1)+2
	Fine = (infreq%1)*800
	return Coarse, Fine

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'
	
	def get_priority(self):
		return -100
	
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'flstudio', None]]
		in_dict['in_daws'] = ['flstudio']
		in_dict['out_plugins'] = [['native', 'ableton', None]]
		in_dict['out_daws'] = ['ableton']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity center'):
			extpluglog.convinternal('FL Studio', 'Fruity Center', 'Ableton', 'StereoGain')
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('on', 'on', 0)
			plugin_obj.replace('native', 'ableton', 'StereoGain')
			manu_obj.to_param('on', 'DcFilter', None)
			return 0

		if plugin_obj.type.check_wildmatch('native', 'flstudio', '3x osc'):
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

			osc1_freq = (fl_osc1_coarse)/12
			osc2_freq = (fl_osc2_coarse)/12
			osc3_freq = (fl_osc3_coarse)/12

			plugin_obj.replace('native', 'ableton', 'Operator')

			plugin_obj.params.add('Operator.0/IsOn', True, 'bool')
			plugin_obj.params.add('Operator.1/IsOn', True, 'bool')
			plugin_obj.params.add('Operator.2/IsOn', True, 'bool')

			plugin_obj.params.add('Operator.0/WaveForm', op_3osc_shape[fl_osc1_shape], 'int')
			plugin_obj.params.add('Operator.1/WaveForm', op_3osc_shape[fl_osc2_shape], 'int')
			plugin_obj.params.add('Operator.2/WaveForm', op_3osc_shape[fl_osc3_shape], 'int')

			plugin_obj.params.add('Operator.0/Envelope/SustainLevel', 1, 'float')
			plugin_obj.params.add('Operator.1/Envelope/SustainLevel', 1, 'float')
			plugin_obj.params.add('Operator.2/Envelope/SustainLevel', 1, 'float')

			Coarse, Fine = als_calc_pitch(osc1_freq)
			plugin_obj.params.add('Operator.0/Tune/Coarse', Coarse, 'float')
			plugin_obj.params.add('Operator.0/Tune/Fine', Fine, 'float')

			Coarse, Fine = als_calc_pitch(osc2_freq)
			plugin_obj.params.add('Operator.1/Tune/Coarse', Coarse, 'float')
			plugin_obj.params.add('Operator.1/Tune/Fine', Fine, 'float')

			Coarse, Fine = als_calc_pitch(osc3_freq)
			plugin_obj.params.add('Operator.2/Tune/Coarse', Coarse, 'float')
			plugin_obj.params.add('Operator.2/Tune/Fine', Fine, 'float')

			plugin_obj.params.add('Operator.0/Volume', osc_vol0, 'float')
			plugin_obj.params.add('Operator.1/Volume', osc_vol1, 'float')
			plugin_obj.params.add('Operator.2/Volume', osc_vol2, 'float')

			plugin_obj.params.add('Operator.0/VelScale', 100, 'float')
			plugin_obj.params.add('Operator.1/VelScale', 100, 'float')
			plugin_obj.params.add('Operator.2/VelScale', 100, 'float')

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
			return 0
			
		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity dx10'):
			extpluglog.convinternal('FL Studio', 'Fruity DX10', 'Ableton', 'Operator')

			amp_att = plugin_obj.params.get("amp_att", 0).value/65536
			amp_dec = plugin_obj.params.get("amp_dec", 0).value/65536
			amp_rel = plugin_obj.params.get("amp_rel", 0).value/65536
			lforate = plugin_obj.params.get("lforate", 0).value/65536
			mod2_course = plugin_obj.params.get("mod2_course", 0).value/65536
			mod2_fine = plugin_obj.params.get("mod2_fine", 0).value/65536
			mod2_init = plugin_obj.params.get("mod2_init", 0).value/65536
			mod2_rel = plugin_obj.params.get("mod2_rel", 0).value/65536
			mod2_sus = plugin_obj.params.get("mod2_sus", 0).value/65536
			mod2_time = plugin_obj.params.get("mod2_time", 0).value/65536
			mod2_velsen = plugin_obj.params.get("mod2_velsen", 0).value/65536
			mod_course = plugin_obj.params.get("mod_course", 0).value/65536
			mod_fine = plugin_obj.params.get("mod_fine", 0).value/65536
			mod_init = plugin_obj.params.get("mod_init", 0).value/65536
			mod_rel = plugin_obj.params.get("mod_rel", 0).value/65536
			mod_sus = plugin_obj.params.get("mod_sus", 0).value/65536
			mod_thru = plugin_obj.params.get("mod_thru", 0).value/65536
			mod_time = plugin_obj.params.get("mod_time", 0).value/65536
			mod_velsen = plugin_obj.params.get("mod_velsen", 0).value/65536
			octave = plugin_obj.params.get("octave", 0).value
			vibrato = plugin_obj.params.get("vibrato", 0).value/65536
			waveform = plugin_obj.params.get("waveform", 0).value/65536

			mod_course = int((mod_course**2)*40)
			mod2_course = int((mod2_course**2)*40)

			plugin_obj.replace('native', 'ableton', 'Operator')

			plugin_obj.params.add('Lfo/LfoOn', True, 'float')
			plugin_obj.params.add('Lfo/LfoAmount', vibrato/5.5, 'float')
			plugin_obj.params.add('Lfo/LfoRate', lforate*127, 'float')

			plugin_obj.params.add('Operator.0/IsOn', True, 'bool')
			plugin_obj.params.add('Operator.0/Volume', 1, 'float')
			plugin_obj.params.add('Operator.0/Envelope/AttackTime', ((amp_att**6)*5)*1000, 'float')
			plugin_obj.params.add('Operator.0/Envelope/DecayTime', ((amp_dec**2)*5)*1000, 'float')
			plugin_obj.params.add('Operator.0/Envelope/SustainLevel', amp_dec**2, 'float')
			plugin_obj.params.add('Operator.0/Envelope/ReleaseTime', ((amp_rel**3)*5)*1000, 'float')
			plugin_obj.params.add('Operator.0/Envelope/DecaySlope', 1, 'float')
			plugin_obj.params.add('Operator.0/Envelope/AttackSlope', 1, 'float')
			plugin_obj.params.add('Operator.0/Envelope/ReleaseSlope', 1, 'float')
			plugin_obj.params.add('Operator.0/Tune/Coarse', [0,1,2,4,8,16,32][octave+3], 'float')

			plugin_obj.params.add('Operator.1/IsOn', not (mod_course == 0 and mod_fine == 0), 'bool')
			plugin_obj.params.add('Operator.1/Volume', 1, 'float')
			plugin_obj.params.add('Operator.1/Envelope/AttackTime', 0, 'float')
			plugin_obj.params.add('Operator.1/Envelope/AttackLevel', mod_init**2, 'float')
			plugin_obj.params.add('Operator.1/Envelope/DecayLevel', mod_init**2, 'float')
			plugin_obj.params.add('Operator.1/Envelope/DecayTime', ((mod_time**2)*5)*1000, 'float')
			plugin_obj.params.add('Operator.1/Envelope/SustainLevel', mod_sus**2, 'float')
			plugin_obj.params.add('Operator.1/Envelope/ReleaseTime', ((mod_rel**3)*5)*1000, 'float')
			plugin_obj.params.add('Operator.1/Envelope/DecaySlope', 0, 'float')
			plugin_obj.params.add('Operator.1/Envelope/AttackSlope', 0, 'float')
			plugin_obj.params.add('Operator.1/Envelope/ReleaseSlope', 0, 'float')
			plugin_obj.params.add('Operator.1/Tune/Coarse', ((mod_course-1)*2)+2, 'float')
			plugin_obj.params.add('Operator.1/Tune/Fine', (mod_fine**4)*180, 'float')

			plugin_obj.params.add('Operator.2/IsOn', not (mod2_course == 0 and mod2_fine == 0), 'bool')
			plugin_obj.params.add('Operator.2/Volume', 1, 'float')
			plugin_obj.params.add('Operator.2/Envelope/AttackTime', 0, 'float')
			plugin_obj.params.add('Operator.2/Envelope/AttackLevel', mod2_init**2, 'float')
			plugin_obj.params.add('Operator.2/Envelope/DecayLevel', mod2_init**2, 'float')
			plugin_obj.params.add('Operator.2/Envelope/DecayTime', ((mod2_time**2)*5)*1000, 'float')
			plugin_obj.params.add('Operator.2/Envelope/SustainLevel', mod2_sus**2, 'float')
			plugin_obj.params.add('Operator.2/Envelope/ReleaseTime', ((mod2_rel**3)*5)*1000, 'float')
			plugin_obj.params.add('Operator.1/Envelope/DecaySlope', 0, 'float')
			plugin_obj.params.add('Operator.2/Envelope/AttackSlope', 0, 'float')
			plugin_obj.params.add('Operator.2/Envelope/ReleaseSlope', 0, 'float')
			plugin_obj.params.add('Operator.2/Tune/Coarse', ((mod2_course-1)*2)+2, 'float')
			plugin_obj.params.add('Operator.2/Tune/Fine', (mod2_fine**4)*180, 'float')

			plugin_obj.datavals_global.add('middlenotefix', 24)
			return 0

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'plucked!'):
			extpluglog.convinternal('FL Studio', 'Plucked!', 'Ableton', 'StringStudio')
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
			manu_obj.from_param('decay', 'decay', 256)
			manu_obj.from_param('color', 'color', 128)
			manu_obj.calc('decay', 'div', 256, 0, 0, 0)
			manu_obj.calc('color', 'div', 128, 0, 0, 0)
			manu_obj.calc('decay', 'sub_r', 1, 0, 0, 0)
			manu_obj.calc('color', 'sub_r', 1, 0, 0, 0)
			plugin_obj.replace('native', 'ableton', 'StringStudio')
			manu_obj.to_param('color', 'GeoExcitatorPosition', None)
			manu_obj.to_param('decay', 'StringDecayRatio', None)
			manu_obj.to_value(0.6, 'StringDamping', 'StringDamping', 'float')
			return 0

		return 2
