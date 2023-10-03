# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes

def decode(model, device, command, data):
	devicename = 'unknown'
	parsed = []

	mem_paramid = data[0:2]
	mem_data = data[2:]

	firstval = int(mem_data[0]) if len(mem_data) != 0 else 0

	fx_set = ['off']

	groups = [None, None]
	nameval = [None, None]

	if model == 73:
		devicename = 'db60xg_sw60xg'
		if command == 0 and mem_paramid[0] == 0: 
			groups[0] = 'system'
			if mem_paramid[1] == 0: groups[1], nameval = 'main', ['ad_12_part_on', firstval]
			if mem_paramid[1] == 1: groups[1], nameval = 'main', ['karaoke_on', firstval]

	elif model == 76:
		devicename = 'yamaha_xg'

		if command == 0 and mem_paramid[0] == 0:
			groups[0] = 'system'

			if mem_paramid[1] == 0: groups[1], nameval = 'main', ['tune', mem_data]
			if mem_paramid[1] == 4: groups[1], nameval = 'main', ['volume', firstval]
			if mem_paramid[1] == 6: groups[1], nameval = 'main', ['transpose', firstval]
			if mem_paramid[1] == 17: groups[1], nameval = 'main', ['ad_12_part_stereo', firstval]
			if mem_paramid[1] == 125:
				if firstval== 0: groups[1], nameval[0] = 'reset', 'drum_setup_1'
				if firstval== 1: groups[1], nameval[0] = 'reset', 'drum_setup_2'
			if mem_paramid[1] == 126 and firstval== 0: groups[1], nameval[0] = None, 'xg_on'
			if mem_paramid[1] == 126 and firstval== 0: 
				groups[1], nameval[0] = 'reset', 'all_params'

		elif command == 2 and mem_paramid[0] == 1:
			groups[0] = 'effects'

			if mem_paramid[1] == 0: groups[1], nameval = 'reverb', ['type', list(mem_data)]
			if mem_paramid[1] == 2: groups[1], nameval = 'reverb', ['time', firstval]
			if mem_paramid[1] == 3: groups[1], nameval = 'reverb', ['diffuse', firstval]
			if mem_paramid[1] == 4: groups[1], nameval = 'reverb', ['inital_delay', firstval]
			if mem_paramid[1] == 5: groups[1], nameval = 'reverb', ['hpf_cutoff', firstval]
			if mem_paramid[1] == 6: groups[1], nameval = 'reverb', ['lpf_cutoff', firstval]
			if mem_paramid[1] == 7: groups[1], nameval = 'reverb', ['width', firstval]
			if mem_paramid[1] == 8: groups[1], nameval = 'reverb', ['height', firstval]
			if mem_paramid[1] == 9: groups[1], nameval = 'reverb', ['depth', firstval]
			if mem_paramid[1] == 10: groups[1], nameval = 'reverb', ['wall_variation', firstval]
			if mem_paramid[1] == 11: groups[1], nameval = 'reverb', ['wet', firstval]
			if mem_paramid[1] == 12: groups[1], nameval = 'reverb', ['send_return', firstval]
			if mem_paramid[1] == 13: groups[1], nameval = 'reverb', ['pan', firstval]
			if mem_paramid[1] == 16: groups[1], nameval = 'reverb', ['delay', firstval]
			if mem_paramid[1] == 17: groups[1], nameval = 'reverb', ['density', firstval]
			if mem_paramid[1] == 18: groups[1], nameval = 'reverb', ['early_reflection', firstval]
			if mem_paramid[1] == 20: groups[1], nameval = 'reverb', ['feedback', firstval]

			if mem_paramid[1] == 32: groups[1], nameval = 'chorus', ['type', list(mem_data)]
			if mem_paramid[1] == 34: groups[1], nameval = 'chorus', ['lfo_frequency', firstval]
			if mem_paramid[1] == 35: groups[1], nameval = 'chorus', ['lfo_phase_mod_depth', firstval]
			if mem_paramid[1] == 36: groups[1], nameval = 'chorus', ['feedback', firstval]
			if mem_paramid[1] == 37: groups[1], nameval = 'chorus', ['delay_offset', firstval]

			if mem_paramid[1] == 39: groups[1], nameval = 'chorus', ['eq_low_freq', firstval]
			if mem_paramid[1] == 40: groups[1], nameval = 'chorus', ['eq_low_gain', firstval]
			if mem_paramid[1] == 41: groups[1], nameval = 'chorus', ['eq_hi_freq', firstval]
			if mem_paramid[1] == 42: groups[1], nameval = 'chorus', ['eq_hi_gain', firstval]
			if mem_paramid[1] == 43: groups[1], nameval = 'chorus', ['wet', firstval]
			if mem_paramid[1] == 44: groups[1], nameval = 'chorus', ['send_return', firstval]
			if mem_paramid[1] == 45: groups[1], nameval = 'chorus', ['pan', firstval]
			if mem_paramid[1] == 46: groups[1], nameval = 'chorus', ['send_reverb', firstval]

			if mem_paramid[1] == 51: groups[1], nameval = 'chorus', ['lfo_phase_diff', firstval]
			if mem_paramid[1] == 52: groups[1], nameval = 'chorus', ['input_mode', firstval]

			if mem_paramid[1] == 64: 
				value = list(mem_data)
				groups[1], nameval = 'variation', ['effect_type', value]
				if value == [0,0]: fx_set = ['off']
				if value[0] in [1,2,3,4]: 
					if value == [1,0]: fx_set = ['reverb', 'hall_1']
					if value == [1,1]: fx_set = ['reverb', 'hall_2']
					if value == [2,0]: fx_set = ['reverb', 'room_1']
					if value == [2,1]: fx_set = ['reverb', 'room_2']
					if value == [2,2]: fx_set = ['reverb', 'room_2']
					if value == [3,0]: fx_set = ['reverb', 'stage_1']
					if value == [3,1]: fx_set = ['reverb', 'stage_2']
					if value == [4,0]: fx_set = ['reverb', 'plate']

				if value == [5,0]: fx_set = ['delay_lcr']
				if value == [6,0]: fx_set = ['delay_lr']
				if value == [7,0]: fx_set = ['echo']
				if value == [8,0]: fx_set = ['delay_cross']
				if value[0] == 9: fx_set = ['early_reflect', str(value[1]+1)]
				if value[0] in [10, 11]: 
					if value[0] == [10,0]: fx_set = ['gate_reverb', 'normal']
					if value[0] == [11,0]: fx_set = ['gate_reverb', 'reverse']
				if value[0] == 20: fx_set = ['karaoke_reverb', str(value[1]+1)]
				if value == [64,0]: fx_set = ['thru']
				if value[0] in [65, 66, 67]: 
					if value[0] == 65: fx_set = ['chorus', str(value[1]+1)]
					if value[0] == 66: fx_set = ['celeste', str(value[1]+1)]
					if value[0] == 67: fx_set = ['flanger', str(value[1]+1)]
				if value == [68,0]: fx_set = ['symphonic']
				if value == [69,0]: fx_set = ['rotary_speaker']
				if value == [70,0]: fx_set = ['tremolo']
				if value == [71,0]: fx_set = ['auto_pan']
				if value[0] == 72: fx_set = ['phaser', str(value[1]+1)]
				if value[0] == 73: fx_set = ['distortion']
				if value[0] == 74: fx_set = ['overdrive']
				if value[0] == 75: fx_set = ['amp_sim']
				if value[0] == 76: fx_set = ['eq_3band']
				if value[0] == 77: fx_set = ['eq_2band']
				if value[0] == 78: fx_set = ['auto_wah']
				groups[1], nameval = 'variation', ['fx_set', fx_set]

			fxval = int.from_bytes(mem_data, "little")
			if mem_paramid[1] in [66,68,70,72,74,76,78,80,82,84]:
				groups[1], nameval[1] = 'variation_param', fxval
				if mem_paramid[1] == 66: nameval[0] = 0
				if mem_paramid[1] == 68: nameval[0] = 1
				if mem_paramid[1] == 70: nameval[0] = 2
				if mem_paramid[1] == 72: nameval[0] = 3
				if mem_paramid[1] == 74: nameval[0] = 4
				if mem_paramid[1] == 76: nameval[0] = 5
				if mem_paramid[1] == 78: nameval[0] = 6
				if mem_paramid[1] == 80: nameval[0] = 7
				if mem_paramid[1] == 82: nameval[0] = 8
				if mem_paramid[1] == 84: nameval[0] = 9

			if mem_paramid[1] == 86: groups[1], nameval = 'variation', ['return', firstval]
			if mem_paramid[1] == 87: groups[1], nameval = 'variation', ['panorama', firstval]
			if mem_paramid[1] == 88: groups[1], nameval = 'variation', ['send_reverb', firstval]
			if mem_paramid[1] == 89: groups[1], nameval = 'variation', ['send_chorus', firstval]
			if mem_paramid[1] == 90: groups[1], nameval = 'variation', ['connection', firstval]
			if mem_paramid[1] == 91: groups[1], nameval = 'variation', ['part', firstval]
			if mem_paramid[1] == 92: groups[1], nameval = 'variation', ['mod_wheel', firstval]
			if mem_paramid[1] == 93: groups[1], nameval = 'variation', ['bend_wheel', firstval]
			if mem_paramid[1] == 94: groups[1], nameval = 'variation', ['ch_aftertouch', firstval]
			if mem_paramid[1] == 95: groups[1], nameval = 'variation', ['ctrl_1', firstval]
			if mem_paramid[1] == 96: groups[1], nameval = 'variation', ['ctrl_2', firstval]

			if mem_paramid[1] == 112: groups[1], nameval = 'variation_param', [10, firstval]
			if mem_paramid[1] == 113: groups[1], nameval = 'variation_param', [11, firstval]
			if mem_paramid[1] == 114: groups[1], nameval = 'variation_param', [12, firstval]
			if mem_paramid[1] == 115: groups[1], nameval = 'variation_param', [13, firstval]
			if mem_paramid[1] == 116: groups[1], nameval = 'variation_param', [14, firstval]
			if mem_paramid[1] == 117: groups[1], nameval = 'variation_param', [15, firstval]

		elif command == 2 and mem_paramid[0] == 64:
			groups[0] = 'effects'
			if mem_paramid[1] == 0: groups[1], nameval = 'eq', ['type', firstval]

			if mem_paramid[1] == 1: groups[1], nameval = 'eq_1', ['gain', firstval]
			if mem_paramid[1] == 2: groups[1], nameval = 'eq_1', ['freq', firstval]
			if mem_paramid[1] == 3: groups[1], nameval = 'eq_1', ['q', firstval]
			if mem_paramid[1] == 4: groups[1], nameval = 'eq_1', ['shape', firstval]

			if mem_paramid[1] == 5: groups[1], nameval = 'eq_2', ['gain', firstval]
			if mem_paramid[1] == 6: groups[1], nameval = 'eq_2', ['freq', firstval]
			if mem_paramid[1] == 7: groups[1], nameval = 'eq_2', ['q', firstval]
			if mem_paramid[1] == 8: groups[1], nameval = 'eq_2', ['shape', firstval]

			if mem_paramid[1] == 9: groups[1], nameval = 'eq_3', ['gain', firstval]
			if mem_paramid[1] == 10: groups[1], nameval = 'eq_3', ['freq', firstval]
			if mem_paramid[1] == 11: groups[1], nameval = 'eq_3', ['q', firstval]
			if mem_paramid[1] == 12: groups[1], nameval = 'eq_3', ['shape', firstval]

			if mem_paramid[1] == 13: groups[1], nameval = 'eq_4', ['gain', firstval]
			if mem_paramid[1] == 14: groups[1], nameval = 'eq_4', ['freq', firstval]
			if mem_paramid[1] == 15: groups[1], nameval = 'eq_4', ['q', firstval]
			if mem_paramid[1] == 16: groups[1], nameval = 'eq_4', ['shape', firstval]

			if mem_paramid[1] == 17: groups[1], nameval = 'eq_5', ['gain', firstval]
			if mem_paramid[1] == 18: groups[1], nameval = 'eq_5', ['freq', firstval]
			if mem_paramid[1] == 19: groups[1], nameval = 'eq_5', ['q', firstval]
			if mem_paramid[1] == 20: groups[1], nameval = 'eq_5', ['shape', firstval]

		elif command == 3 and mem_paramid[0] == 0:
			groups[0] = 'effects'
			if mem_paramid[1] == 0: groups[1], nameval = 'xg_fx', ['type', list(mem_data)]
			if mem_paramid[1] == 2: groups[1], nameval = 'xg_fx_param', [0, firstval]
			if mem_paramid[1] == 3: groups[1], nameval = 'xg_fx_param', [1, firstval]
			if mem_paramid[1] == 4: groups[1], nameval = 'xg_fx_param', [2, firstval]
			if mem_paramid[1] == 5: groups[1], nameval = 'xg_fx_param', [3, firstval]
			if mem_paramid[1] == 6: groups[1], nameval = 'xg_fx_param', [4, firstval]
			if mem_paramid[1] == 7: groups[1], nameval = 'xg_fx_param', [5, firstval]
			if mem_paramid[1] == 8: groups[1], nameval = 'xg_fx_param', [6, firstval]
			if mem_paramid[1] == 9: groups[1], nameval = 'xg_fx_param', [7, firstval]
			if mem_paramid[1] == 10: groups[1], nameval = 'xg_fx_param', [8, firstval]
			if mem_paramid[1] == 11: groups[1], nameval = 'xg_fx_param', [9, firstval]
			if mem_paramid[1] == 12: groups[1], nameval = 'xg_fx', ['part', firstval]

			if mem_paramid[1] == 13: groups[1], nameval = 'xg_fx', ['mw_depth', firstval]
			if mem_paramid[1] == 14: groups[1], nameval = 'xg_fx', ['bend', firstval]
			if mem_paramid[1] == 15: groups[1], nameval = 'xg_fx', ['cat', firstval]
			if mem_paramid[1] == 16: groups[1], nameval = 'xg_fx', ['ac1', firstval]
			if mem_paramid[1] == 17: groups[1], nameval = 'xg_fx', ['ac2', firstval]

			if mem_paramid[1] == 32: groups[1], nameval = 'xg_fx_param', [10, firstval]
			if mem_paramid[1] == 33: groups[1], nameval = 'xg_fx_param', [11, firstval]
			if mem_paramid[1] == 34: groups[1], nameval = 'xg_fx_param', [12, firstval]
			if mem_paramid[1] == 35: groups[1], nameval = 'xg_fx_param', [13, firstval]
			if mem_paramid[1] == 36: groups[1], nameval = 'xg_fx_param', [14, firstval]

		elif command == 6 and mem_paramid[0] == 0:
			groups, nameval = ['display', 'text'], ['text', mem_data]

		elif command == 7:
			bmpext = data_bytes.splitbyte(mem_paramid[0])
			groups, nameval = ['display', 'bitmap'], [bmpext, mem_data]

		elif command == 8:
			groups = ['part', mem_paramid[0]]
			if mem_paramid[1] != 9: nameval[1] = firstval
			else: nameval[1] = mem_data
			if mem_paramid[1] == 0: nameval[0] = "element_reserve"
			if mem_paramid[1] == 1: nameval[0] = "bank_select_msb"
			if mem_paramid[1] == 2: nameval[0] = "bank_select_lsb"
			if mem_paramid[1] == 3: nameval[0] = "program_number"
			if mem_paramid[1] == 4: nameval[0] = "receive_midi_channel"
			if mem_paramid[1] == 5: nameval[0] = "mono_poly"
			if mem_paramid[1] == 6: nameval[0] = "same_note_number_key_on_assign"
			if mem_paramid[1] == 7: nameval[0] = "part_mode"
			if mem_paramid[1] == 8: nameval[0] = "note_shift"
			if mem_paramid[1] == 9: nameval[0] = "detune"
			if mem_paramid[1] == 11: nameval[0] = "volume"
			if mem_paramid[1] == 12: nameval[0] = "velocity_sense_depth"
			if mem_paramid[1] == 13: nameval[0] = "velocity_sense_offset"
			if mem_paramid[1] == 14: nameval[0] = "panorama"
			if mem_paramid[1] == 15: nameval[0] = "note_limit_low"
			if mem_paramid[1] == 16: nameval[0] = "note_limit_high"
			if mem_paramid[1] == 17: nameval[0] = "dry_level"
			if mem_paramid[1] == 18: nameval[0] = "chorus_send"
			if mem_paramid[1] == 19: nameval[0] = "reverb_send"
			if mem_paramid[1] == 20: nameval[0] = "variation_send"
			if mem_paramid[1] == 21: nameval[0] = "vibrato_rate"
			if mem_paramid[1] == 22: nameval[0] = "vibrato_depth"
			if mem_paramid[1] == 23: nameval[0] = "vibrato_delay"
			if mem_paramid[1] == 24: nameval[0] = "filter_cutoff_frequency"
			if mem_paramid[1] == 25: nameval[0] = "filter_resonance"
			if mem_paramid[1] == 26: nameval[0] = "eg_attack_time"
			if mem_paramid[1] == 27: nameval[0] = "eg_decay_time"
			if mem_paramid[1] == 28: nameval[0] = "eg_release_time"
			if mem_paramid[1] == 29: nameval[0] = "mw_pitch_control"
			if mem_paramid[1] == 30: nameval[0] = "mw_filter_control"
			if mem_paramid[1] == 31: nameval[0] = "mw_amplitude_control"
			if mem_paramid[1] == 32: nameval[0] = "mw_lfo_pitch_modulation_depth"
			if mem_paramid[1] == 33: nameval[0] = "mw_lfo_filter_modulation_depth"
			if mem_paramid[1] == 34: nameval[0] = "mw_lfo_amplitude_modulation_depth"
			if mem_paramid[1] == 35: nameval[0] = "bend_pitch_control"
			if mem_paramid[1] == 36: nameval[0] = "bend_filter_control"
			if mem_paramid[1] == 37: nameval[0] = "bend_amplitude_control"
			if mem_paramid[1] == 38: nameval[0] = "bend_lfo_pitch_modulation_depth"
			if mem_paramid[1] == 39: nameval[0] = "bend_lfo_filter_modulation_depth"
			if mem_paramid[1] == 40: nameval[0] = "bend_lfo_amplitude_modulation_depth"
			if mem_paramid[1] == 48: nameval[0] = "receive_pitch_bend"
			if mem_paramid[1] == 49: nameval[0] = "receive_channel_after_touch"
			if mem_paramid[1] == 50: nameval[0] = "receive_program_change"
			if mem_paramid[1] == 51: nameval[0] = "receive_control_change"
			if mem_paramid[1] == 52: nameval[0] = "receive_polyphonic_after_touch"
			if mem_paramid[1] == 53: nameval[0] = "receive_note_messages"
			if mem_paramid[1] == 54: nameval[0] = "receive_rpn"
			if mem_paramid[1] == 55: nameval[0] = "receive_nrpn"
			if mem_paramid[1] == 56: nameval[0] = "receive_modulation_wheel"
			if mem_paramid[1] == 57: nameval[0] = "receive_volume"
			if mem_paramid[1] == 58: nameval[0] = "receive_pan"
			if mem_paramid[1] == 59: nameval[0] = "receive_expression"
			if mem_paramid[1] == 60: nameval[0] = "receive_hold_pedal"
			if mem_paramid[1] == 61: nameval[0] = "receive_portamento"
			if mem_paramid[1] == 62: nameval[0] = "receive_sostenuto_pedal"
			if mem_paramid[1] == 63: nameval[0] = "receive_soft_pedal"
			if mem_paramid[1] == 64: nameval[0] = "receive_bank_select"
			if mem_paramid[1] == 65: nameval[0] = "scale_tuning_c"
			if mem_paramid[1] == 66: nameval[0] = "scale_tuning_c_s"
			if mem_paramid[1] == 67: nameval[0] = "scale_tuning_d"
			if mem_paramid[1] == 68: nameval[0] = "scale_tuning_d_s"
			if mem_paramid[1] == 69: nameval[0] = "scale_tuning_e"
			if mem_paramid[1] == 70: nameval[0] = "scale_tuning_f"
			if mem_paramid[1] == 71: nameval[0] = "scale_tuning_f_s"
			if mem_paramid[1] == 72: nameval[0] = "scale_tuning_g"
			if mem_paramid[1] == 73: nameval[0] = "scale_tuning_g_s"
			if mem_paramid[1] == 74: nameval[0] = "scale_tuning_a"
			if mem_paramid[1] == 75: nameval[0] = "scale_tuning_a_s"
			if mem_paramid[1] == 76: nameval[0] = "scale_tuning_b"
			if mem_paramid[1] == 77: nameval[0] = "cat_pitch_control"
			if mem_paramid[1] == 78: nameval[0] = "cat_filter_control"
			if mem_paramid[1] == 79: nameval[0] = "cat_amplitude_control"
			if mem_paramid[1] == 80: nameval[0] = "cat_lfo_pitch_modulation_depth"
			if mem_paramid[1] == 81: nameval[0] = "cat_lfo_filter_modulation_depth"
			if mem_paramid[1] == 82: nameval[0] = "cat_lfo_amplitude_modulation_depth"
			if mem_paramid[1] == 83: nameval[0] = "pat_pitch_control"
			if mem_paramid[1] == 84: nameval[0] = "pat_filter_control"
			if mem_paramid[1] == 85: nameval[0] = "pat_amplitude_control"
			if mem_paramid[1] == 86: nameval[0] = "pat_lfo_pitch_modulation_depth"
			if mem_paramid[1] == 87: nameval[0] = "pat_lfo_filter_modulation_depth"
			if mem_paramid[1] == 88: nameval[0] = "pat_lfo_amplitude_modulation_depth"
			if mem_paramid[1] == 89: nameval[0] = "ac1_controller_number"
			if mem_paramid[1] == 90: nameval[0] = "ac1_pitch_control"
			if mem_paramid[1] == 91: nameval[0] = "ac1_filter_control"
			if mem_paramid[1] == 92: nameval[0] = "ac1_amplitude_control"
			if mem_paramid[1] == 93: nameval[0] = "ac1_lfo_pitch_modulation_depth"
			if mem_paramid[1] == 94: nameval[0] = "ac1_lfo_filter_modulation_depth"
			if mem_paramid[1] == 95: nameval[0] = "ac1_lfo_amplitude_modulation_depth"
			if mem_paramid[1] == 96: nameval[0] = "ac2_controller_number"
			if mem_paramid[1] == 97: nameval[0] = "ac2_pitch_control"
			if mem_paramid[1] == 98: nameval[0] = "ac2_filter_control"
			if mem_paramid[1] == 99: nameval[0] = "ac2_amplitude_control"
			if mem_paramid[1] == 100: nameval[0] = "ac2_lfo_pitch_modulation_depth"
			if mem_paramid[1] == 101: nameval[0] = "ac2_lfo_filter_modulation_depth"
			if mem_paramid[1] == 102: nameval[0] = "ac2_lfo_amplitude_modulation_depth"
			if mem_paramid[1] == 103: nameval[0] = "portamento_switch"
			if mem_paramid[1] == 104: nameval[0] = "portamento_time"
			if mem_paramid[1] == 105: nameval[0] = "pitch_eg_initial_level"
			if mem_paramid[1] == 106: nameval[0] = "pitch_eg_attack_time"
			if mem_paramid[1] == 107: nameval[0] = "pitch_eg_release_level"
			if mem_paramid[1] == 108: nameval[0] = "pitch_eg_release_time"
			if mem_paramid[1] == 109: nameval[0] = "velocity_limit_low"
			if mem_paramid[1] == 110: nameval[0] = "velocity_limit_high"
			if mem_paramid[1] == 114: nameval[0] = "eq_bass_gain"
			if mem_paramid[1] == 115: nameval[0] = "eq_treble_gain"
			if mem_paramid[1] == 118: nameval[0] = "eq_bass_frequency"
			if mem_paramid[1] == 119: nameval[0] = "eq_treble_frequency"
		
	#else:
	#	print('[UNK Yamaha]', devicename, model, hex(model), command, groups, nameval)

	return devicename, groups, nameval