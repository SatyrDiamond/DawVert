# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
from functions import data_bytes
from functions import list_vst
from functions import params_vst
from functions import params_vital
from functions import params_vital_wavetable

rawChipWaves = {}
rawChipWaves["rounded"] = {"expression": 0.94, "samples": [0,0.2,0.4,0.5,0.6,0.7,0.8,0.85,0.9,0.95,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0.95,0.9,0.85,0.8,0.7,0.6,0.5,0.4,0.2,0,-0.2,-0.4,-0.5,-0.6,-0.7,-0.8,-0.85,-0.9,-0.95,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-0.95,-0.9,-0.85,-0.8,-0.7,-0.6,-0.5,-0.4,-0.2]}
rawChipWaves["triangle"] = {"expression": 1, "samples": [1/15,0.2,5/15,7/15,0.6,11/15,13/15,1,1,13/15,11/15,0.6,7/15,5/15,0.2,1/15,-1/15,-0.2,-5/15,-7/15,-0.6,-11/15,-13/15,-1,-1,-13/15,-11/15,-0.6,-7/15,-5/15,-0.2,-1/15]}
rawChipWaves["square"] = {"expression": 0.5, "samples": [1,-1]}
rawChipWaves["1/4 pulse"] = {"expression": 0.5, "samples": [1,-1,-1,-1]}
rawChipWaves["1/8 pulse"] = {"expression": 0.5, "samples": [1,-1,-1,-1,-1,-1,-1,-1]}
rawChipWaves["sawtooth"] = {"expression": 0.65, "samples": [1/31,3/31,5/31,7/31,9/31,11/31,13/31,15/31,17/31,19/31,21/31,23/31,25/31,27/31,29/31,1,-1,-29/31,-27/31,-25/31,-23/31,-21/31,-19/31,-17/31,-15/31,-13/31,-11/31,-9/31,-7/31,-5/31,-3/31,-1/31]}
rawChipWaves["double saw"] = {"expression": 0.5, "samples": [0,-0.2,-0.4,-0.6,-0.8,-1,1,-0.8,-0.6,-0.4,-0.2,1,0.8,0.6,0.4,0.2]}
rawChipWaves["double pulse"] = {"expression": 0.4, "samples": [1,1,1,1,1,-1,-1,-1,1,1,1,1,-1,-1,-1,-1]}
rawChipWaves["spiky"] = {"expression": 0.4, "samples": [1,-1,1,-1,1,0]}
rawChipWaves["sine"] = {"expression": 0.88, "samples": [8,9,11,12,13,14,15,15,15,15,14,14,13,11,10,9,7,6,4,3,2,1,0,0,0,0,1,1,2,4,5,6]}
rawChipWaves["flute"] = {"expression": 0.8, "samples": [3,4,6,8,10,11,13,14,15,15,14,13,11,8,5,3]}
rawChipWaves["harp"] = {"expression": 0.8, "samples": [0,3,3,3,4,5,5,6,7,8,9,11,11,13,13,15,15,14,12,11,10,9,8,7,7,5,4,3,2,1,0,0]}
rawChipWaves["sharp clarinet"] = {"expression": 0.38, "samples": [0,0,0,1,1,8,8,9,9,9,8,8,8,8,8,9,9,7,9,9,10,4,0,0,0,0,0,0,0,0,0,0]}
rawChipWaves["soft clarinet"] = {"expression": 0.45, "samples": [0,1,5,8,9,9,9,9,9,9,9,11,11,12,13,12,10,9,7,6,4,3,3,3,1,1,1,1,1,1,1,1]}
rawChipWaves["alto sax"] = {"expression": 0.3, "samples": [5,5,6,4,3,6,8,7,2,1,5,6,5,4,5,7,9,11,13,14,14,14,14,13,10,8,7,7,4,3,4,2]}
rawChipWaves["bassoon"] = {"expression": 0.35, "samples": [9,9,7,6,5,4,4,4,4,5,7,8,9,10,11,13,13,11,10,9,7,6,4,2,1,1,1,2,2,5,11,14]}
rawChipWaves["trumpet"] = {"expression": 0.22, "samples": [10,11,8,6,5,5,5,6,7,7,7,7,6,6,7,7,7,7,7,6,6,6,6,6,6,6,6,7,8,9,11,14]}
rawChipWaves["electric guitar"] = {"expression": 0.2, "samples": [11,12,12,10,6,6,8,0,2,4,8,10,9,10,1,7,11,3,6,6,8,13,14,2,0,12,8,4,13,11,10,13]}
rawChipWaves["organ"] = {"expression": 0.2, "samples": [11,10,12,11,14,7,5,5,12,10,10,9,12,6,4,5,13,12,12,10,12,5,2,2,8,6,6,5,8,3,2,1]}
rawChipWaves["pan flute"] = {"expression": 0.35, "samples": [1,4,7,6,7,9,7,7,11,12,13,15,13,11,11,12,13,10,7,5,3,6,10,7,3,3,1,0,1,0,1,0]}
rawChipWaves["glitch"] = {"expression": 0.5, "samples": [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1]}

def convert(instdata):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']
	bb_type = plugindata['type']
	bb_data = plugindata['data']
	bb_data_fx = bb_data['effects']

	if bb_type == 'chip' or bb_type == 'custom chip' or bb_type == 'harmonics' or bb_type == 'PWM':

		if bb_type == 'chip': 
			if bb_data['wave'] in rawChipWaves:
				t_sample = rawChipWaves[bb_data['wave']]['samples']

		if bb_type == 'custom chip': 
			t_sample = []
			for samplenum in range(64):
				t_sample.append(bb_data['customChipWave'][str(samplenum)])

		if bb_type == 'harmonics': 
			bb_harmonics = bb_data['harmonics']
			t_sample = []
			for num in range(2048):
				s_pos = num/2048
				sample = 0
				for harm_num in range(28):
					sine_pitch = s_pos*(harm_num+1)
					sine_vol = (bb_harmonics[harm_num]/100)/(harm_num+1)
					sample += params_vital_wavetable.wave_sine(sine_pitch)*sine_vol
				for harm_num in range(3):
					sine_pitch = s_pos*(harm_num+29)
					sine_vol = (bb_harmonics[27]/100)/(harm_num+29)
					sample += params_vital_wavetable.wave_sine(sine_pitch)*sine_vol
				t_sample.append(sample)

		if bb_type == 'PWM': 
			t_sample = []
			for _ in range(bb_data['pulseWidth']):
				t_sample.append(1)
			for _ in range(100-bb_data['pulseWidth']):
				t_sample.append(-1)

		t_sample_invert = [i*-1 for i in t_sample]

		params_vital.create()
		params_vital.setvalue('osc_1_on', 1)
		params_vital.setvalue('effect_chain_order', 357202)

		bb_pitch = 0

		start_level = 0.4

		if 'panning' in bb_data_fx:
			params_vital.setvalue('osc_1_pan', bb_data['pan']/100)
			params_vital.setvalue('osc_2_pan', bb_data['pan']/100)
			params_vital.setvalue('osc_3_pan', bb_data['pan']/100)


		if 'pitch shift' in bb_data_fx:
			bb_pitch += bb_data['pitchShiftSemitones']-12


		if 'detune' in bb_data_fx:
			bb_pitch += bb_data['detuneCents']/100


		if 'vibrato' in bb_data_fx:
			if 'vibratoDepth' in bb_data:
				if bb_data['vibratoDepth'] != 0:
					params_vital.set_modulation(1, 'lfo_1', 'osc_1_tune', bb_data['vibratoDepth']/2, 0, 0, 0, 0)
					params_vital.set_modulation(1, 'lfo_1', 'osc_2_tune', bb_data['vibratoDepth']/2, 0, 0, 0, 0)
					params_vital.set_modulation(1, 'lfo_1', 'osc_3_tune', bb_data['vibratoDepth']/2, 0, 0, 0, 0)
			if 'vibratoSpeed' in bb_data:
				if bb_data['vibratoSpeed'] != 0:
					t_vibvalue = (bb_data['vibratoSpeed']/31)
					params_vital.setvalue('lfo_1_frequency', (t_vibvalue*t_vibvalue)*8  ) 
					params_vital.setvalue('lfo_1_sync', 0)
				#if bb_data['vibratoType'] == 0:
			params_vital.set_lfo(1, 3, [0,1,0.5,0,1,1], [0,0,0], True, 'Sin')
			if 'vibratoDelay' in bb_data:
				if bb_data['vibratoDelay'] != 0:
					params_vital.setvalue('lfo_1_delay_time', 0.5*(bb_data['vibratoDelay']/50))


		if 'distortion' in bb_data_fx:
			params_vital.setvalue('distortion_on', 1)
			params_vital.setvalue('distortion_drive', (bb_data['distortion']/100)*30)
			start_level = start_level/(1+(bb_data['distortion']/150))


		if 'chorus' in bb_data_fx:
			params_vital.setvalue('chorus_on', 1)
			params_vital.setvalue('chorus_dry_wet', bb_data['chorus']/100)


		if 'echo' in bb_data_fx:
			params_vital.setvalue('delay_on', 1)
			params_vital.setvalue('delay_sync', 0)
			t_echovalue = ((47-bb_data['echoSustain'])/58)
			params_vital.setvalue('delay_frequency', (t_echovalue*t_echovalue)*8 + 30 )


		if 'reverb' in bb_data_fx:
			params_vital.setvalue('reverb_on', 1)
			params_vital.setvalue('reverb_decay_time', 1.74)
			params_vital.setvalue('reverb_dry_wet', (bb_data['reverb']/100)*0.74)

		out_cents = int(bb_pitch)
		out_semi = bb_pitch - out_cents
		params_vital.setvalue('osc_1_transpose', out_cents)
		params_vital.setvalue('osc_1_tune', out_semi)

		params_vital.setvalue('osc_1_random_phase', 0)
		params_vital.setvalue('osc_2_random_phase', 0)
		params_vital.setvalue('osc_3_random_phase', 0)

		params_vital.replacewave(0, params_vital_wavetable.resizewave(t_sample))
		params_vital.replacewave(1, params_vital_wavetable.resizewave(t_sample))
		params_vital.replacewave(2, params_vital_wavetable.resizewave(t_sample))

		if 'unison' in bb_data:
			if bb_data['unison'] == 'shimmer':
				params_vital.setvalue('osc_1_unison_detune', 1.01)
				params_vital.setvalue('osc_1_unison_voices', 3)
			if bb_data['unison'] == 'hum':
				params_vital.setvalue('osc_1_unison_detune', 1.6)
				params_vital.setvalue('osc_1_unison_voices', 6)
			if bb_data['unison'] == 'honky tonk':
				params_vital.setvalue('osc_1_unison_detune', 2.3)
				params_vital.setvalue('osc_1_unison_voices', 6)
			if bb_data['unison'] == 'dissonant':
				params_vital.setvalue('osc_1_unison_detune', 3.5)
				params_vital.setvalue('osc_1_unison_voices', 3)
			if bb_data['unison'] == 'fifth':
				params_vital.setvalue('osc_2_on', 2)
				bb_pitch_fifth = 7 + bb_pitch
				out_cents_fifth = int(bb_pitch_fifth)
				out_semi_fifth = bb_pitch_fifth - out_cents_fifth
				params_vital.setvalue('osc_2_transpose', out_cents_fifth)
				params_vital.setvalue('osc_2_tune', out_semi_fifth)
				start_level = start_level/1.3
			if bb_data['unison'] == 'octave':
				params_vital.setvalue('osc_2_on', 2)
				params_vital.setvalue('osc_2_transpose', out_cents+12)
				params_vital.setvalue('osc_2_tune', out_semi)
				start_level = start_level/1.3
			if bb_data['unison'] == 'bowed':
				params_vital.replacewave(1, params_vital_wavetable.resizewave(t_sample_invert))
				params_vital.setvalue('osc_2_on', 2)
				params_vital.setvalue('osc_2_transpose', out_cents)
				params_vital.setvalue('osc_2_tune', out_semi+0.05)
				start_level = start_level/1.3
			if bb_data['unison'] == 'piano':
				params_vital.setvalue('osc_2_on', 2)
				params_vital.setvalue('osc_2_transpose', out_cents)
				params_vital.setvalue('osc_2_tune', out_semi+0.02)
				start_level = start_level/1.3
			if bb_data['unison'] == 'warbled':
				params_vital.setvalue('osc_1_unison_detune', 4)
				params_vital.setvalue('osc_1_unison_voices', 4)

		params_vital.setvalue('osc_1_level', start_level)
		params_vital.setvalue('osc_2_level', start_level)
		params_vital.setvalue('osc_3_level', start_level)

		params_vital.setvalue_timed('env_1_attack', bb_data['fadeInSeconds'])
		params_vital.setvalue_timed('env_1_release', abs((bb_data['fadeOutTicks']/96)*1.2))

		vitaldata = params_vital.getdata()
		list_vst.replace_data(instdata, 2, 'any', 'Vital', 'raw', vitaldata.encode('utf-8'), None)
