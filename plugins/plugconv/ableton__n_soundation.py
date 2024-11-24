# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return -100
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native','soundation', None]]
		in_dict['in_daws'] = ['soundation']
		in_dict['out_plugins'] = [['native',' ableton', None]]
		in_dict['out_daws'] = ['ableton']
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):

		if plugin_obj.check_wildmatch('native', 'soundation', 'com.soundation.va_synth'):
			extpluglog.convinternal('Soundation', 'VA Synth', 'Ableton', 'UltraAnalog')
			manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)

			aatt = plugin_obj.params.get('aatt', 0).value**0.7
			adec = plugin_obj.params.get('adec', 0).value**0.7
			asus = plugin_obj.params.get('asus', 0).value
			arel = plugin_obj.params.get('arel', 0).value**0.7

			fatt = plugin_obj.params.get('fatt', 0).value**0.35
			fdec = plugin_obj.params.get('fdec', 0).value**0.35
			fsus = plugin_obj.params.get('fsus', 0).value
			frel = plugin_obj.params.get('frel', 0).value

			ffreq = plugin_obj.params.get('ffreq', 0).value
			fres = plugin_obj.params.get('fres', 0).value**0.7

			fdyn = plugin_obj.params.get('fdyn', 0).value
			feg = plugin_obj.params.get('feg', 0).value
			glide_bend = plugin_obj.params.get('glide_bend', 0).value
			glide_mode = plugin_obj.params.get('glide_mode', 0).value*5
			glide_rate = plugin_obj.params.get('glide_rate', 0).value
			lfolpf = plugin_obj.params.get('lfolpf', 0).value
			lfoosc = plugin_obj.params.get('lfoosc', 0).value
			lforate = plugin_obj.params.get('lforate', 0).value
			octave = plugin_obj.params.get('octave', 0).value
			osc_2_fine = plugin_obj.params.get('osc_2_fine', 0).value
			osc_2_mix = plugin_obj.params.get('osc_2_mix', 0).value
			osc_2_noise = plugin_obj.params.get('osc_2_noise', 0).value
			osc_2_octave = plugin_obj.params.get('osc_2_octave', 0).value
			tune = plugin_obj.params.get('tune', 0).value

			plugin_obj.replace('native', 'ableton', 'UltraAnalog')

			octave = (octave-0.5)*5

			osc_2_fine -= 0.5
			osc_2_fine *= 2

			osc_2_fine_t = abs(osc_2_fine)
			osc_2_fine_t **= 4

			osc_2_fine = osc_2_fine_t if osc_2_fine>0 else -osc_2_fine_t

			osc_2_fine /= 2
			osc_2_fine += 0.5

			plugin_obj.params.add('SignalChain1/OscillatorOct', octave, 'float')
			plugin_obj.params.add('SignalChain2/OscillatorOct', octave, 'float')

			plugin_obj.params.add('SignalChain2/OscillatorDetune', osc_2_fine, 'float')

			plugin_obj.params.add('SignalChain1/Envelope.1/AttackTime', aatt, 'float')
			plugin_obj.params.add('SignalChain1/Envelope.1/DecayTime', adec, 'float')
			plugin_obj.params.add('SignalChain1/Envelope.1/ReleaseTime', arel, 'float')
			plugin_obj.params.add('SignalChain1/Envelope.1/SustainLevel', asus, 'float')
			plugin_obj.params.add('SignalChain2/Envelope.1/AttackTime', aatt, 'float')
			plugin_obj.params.add('SignalChain2/Envelope.1/DecayTime', adec, 'float')
			plugin_obj.params.add('SignalChain2/Envelope.1/ReleaseTime', arel, 'float')
			plugin_obj.params.add('SignalChain2/Envelope.1/SustainLevel', asus, 'float')

			plugin_obj.params.add('SignalChain1/Envelope.0/AttackTime', fatt, 'float')
			plugin_obj.params.add('SignalChain1/Envelope.0/DecayTime', fdec, 'float')
			plugin_obj.params.add('SignalChain1/Envelope.0/ReleaseTime', frel, 'float')
			plugin_obj.params.add('SignalChain1/Envelope.0/SustainLevel', fsus, 'float')
			plugin_obj.params.add('SignalChain2/Envelope.0/AttackTime', fatt, 'float')
			plugin_obj.params.add('SignalChain2/Envelope.0/DecayTime', fdec, 'float')
			plugin_obj.params.add('SignalChain2/Envelope.0/ReleaseTime', frel, 'float')
			plugin_obj.params.add('SignalChain2/Envelope.0/SustainLevel', fsus, 'float')
 
			plugin_obj.params.add('SignalChain1/FilterEnvCutoffMod', feg, 'float')
			plugin_obj.params.add('SignalChain2/FilterEnvCutoffMod', feg, 'float')

			plugin_obj.params.add('SignalChain1/FilterCutoffFrequency', ffreq**0.7, 'float')
			plugin_obj.params.add('SignalChain2/FilterCutoffFrequency', ffreq**0.7, 'float')
			plugin_obj.params.add('SignalChain1/FilterQFactor', fres, 'float')
			plugin_obj.params.add('SignalChain2/FilterQFactor', fres, 'float')

			plugin_obj.params.add('NoiseToggle', True, 'bool')
			plugin_obj.params.add('NoiseColor', 1, 'float')
			plugin_obj.params.add('NoiseLevel', osc_2_noise, 'float')

			plugin_obj.params.add('VibratoAmount', abs((lfoosc-0.5)*1.8), 'float')
			plugin_obj.params.add('VibratoSpeed', lforate, 'float')
			plugin_obj.params.add('VibratoToggle', True, 'bool')

			plugin_obj.params.add('SignalChain2/AmplifierLevel', osc_2_mix, 'float')

			plugin_obj.params.add('Polyphony', 9 if glide_mode in [0,1,2] else 0, 'bool')
			plugin_obj.params.add('PortamentoLegato', glide_mode in [1,4], 'float')
			plugin_obj.params.add('PortamentoTime', glide_bend, 'float')
			plugin_obj.params.add('PortamentoToggle', glide_mode in [2,5], 'float')
			
			return 0

		if plugin_obj.check_wildmatch('native', 'soundation', 'com.soundation.noiser'):
			extpluglog.convinternal('Soundation', 'Noiser', 'Ableton', 'Operator')

			plugin_obj.replace('native', 'ableton', 'Operator')

			adsr_obj = plugin_obj.env_asdr_get('vol')
			plugin_obj.params.add('Operator.0/IsOn', True, 'bool')
			plugin_obj.params.add('Operator.0/Volume', 1, 'float')
			plugin_obj.params.add('Operator.0/WaveForm', 21, 'int')
			plugin_obj.params.add('Operator.0/Envelope/AttackTime', adsr_obj.attack*1000, 'float')
			plugin_obj.params.add('Operator.0/Envelope/DecayTime', adsr_obj.decay*1000, 'float')
			plugin_obj.params.add('Operator.0/Envelope/SustainLevel', adsr_obj.sustain, 'float')
			plugin_obj.params.add('Operator.0/Envelope/ReleaseTime', adsr_obj.release*1000, 'float')
			plugin_obj.params.add('Operator.0/Envelope/AttackSlope', 0, 'float')
			plugin_obj.params.add('Operator.0/Envelope/DecaySlope', 0, 'float')
			plugin_obj.params.add('Operator.0/Envelope/ReleaseSlope', 0, 'float')
			return 0

		if plugin_obj.check_wildmatch('native', 'soundation', 'com.soundation.simple'):
			extpluglog.convinternal('Soundation', 'Simple Synth', 'Ableton', 'Operator')

			opdata = []

			for oscnum in range(4):
				starttxt = 'osc_'+str(oscnum)+'_'
				osc_detune = plugin_obj.params.get(starttxt+'detune', 0).value
				osc_pitch = plugin_obj.params.get(starttxt+'pitch', 0).value
				osc_type = plugin_obj.params.get(starttxt+'type', 0).value
				osc_vol = plugin_obj.params.get(starttxt+'vol', 0).value
				opdata.append([osc_detune, (osc_pitch-0.5)*48, int(osc_type), osc_vol])

			plugin_obj.replace('native', 'ableton', 'Operator')

			adsr_obj = plugin_obj.env_asdr_get('vol')

			for num, oppart in enumerate(opdata):
				osc_detune, osc_pitch, osc_type, osc_vol = oppart
				starttxt = 'Operator.'+str(num)

				osc_pitch = int(osc_pitch)/12

				plugin_obj.params.add(starttxt+'/IsOn', True, 'bool')
				plugin_obj.params.add(starttxt+'/Volume', osc_vol, 'float')
				plugin_obj.params.add(starttxt+'/Tune/Coarse', [0,1,2,4,8][int((osc_pitch//1)+2)], 'float')
				plugin_obj.params.add(starttxt+'/Tune/Fine', (osc_pitch%1)*900, 'float')
				plugin_obj.params.add(starttxt+'/WaveForm', [10,17,0,19][osc_type], 'int')

				plugin_obj.params.add(starttxt+'/Envelope/AttackTime', adsr_obj.attack*1000, 'float')
				plugin_obj.params.add(starttxt+'/Envelope/DecayTime', adsr_obj.decay*1000, 'float')
				plugin_obj.params.add(starttxt+'/Envelope/SustainLevel', adsr_obj.sustain, 'float')
				plugin_obj.params.add(starttxt+'/Envelope/ReleaseTime', adsr_obj.release*1000, 'float')
				plugin_obj.params.add(starttxt+'/Envelope/AttackSlope', 0, 'float')
				plugin_obj.params.add(starttxt+'/Envelope/DecaySlope', 0, 'float')
				plugin_obj.params.add(starttxt+'/Envelope/ReleaseSlope', 0, 'float')

			adsr_cut_obj = plugin_obj.env_asdr_get('cutoff')
			plugin_obj.params.add('Filter/Envelope/AttackTime', adsr_cut_obj.attack*1000, 'float')
			plugin_obj.params.add('Filter/Envelope/DecayTime', adsr_cut_obj.decay*1000, 'float')
			plugin_obj.params.add('Filter/Envelope/SustainLevel', adsr_cut_obj.sustain, 'float')
			plugin_obj.params.add('Filter/Envelope/ReleaseTime', adsr_cut_obj.release*1000, 'float')
			plugin_obj.params.add('Filter/Envelope/AttackSlope', 0, 'float')
			plugin_obj.params.add('Filter/Envelope/DecaySlope', 0, 'float')
			plugin_obj.params.add('Filter/Envelope/ReleaseSlope', 0, 'float')
			plugin_obj.params.add('Filter/EnvelopeAmount', adsr_cut_obj.amount*100, 'float')
			plugin_obj.params.add('Filter/FrequencyKeyScale', 0, 'float')
			plugin_obj.params.add('Filter/OnOff', True, 'bool')
			plugin_obj.params.add('Filter/Frequency', plugin_obj.filter.freq, 'float')
			plugin_obj.params.add('Filter/Resonance', max(plugin_obj.filter.q-1, 0), 'float')

			plugin_obj.params.add('Globals/Algorithm', 10, 'int')
			
			plugin_obj.datavals_global.add('middlenotefix', 12)
			return 0

		return 2
