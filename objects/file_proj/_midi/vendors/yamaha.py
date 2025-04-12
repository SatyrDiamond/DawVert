# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes

def decode(sysex_obj, bstream):
	mem_paramid = bstream.read(2)
	mem_data = bstream.read()

	firstval = int(mem_data[0]) if len(mem_data) != 0 else 0

	if sysex_obj.model_id == 73:
		sysex_obj.known = True
		sysex_obj.model_name = 'db60xg_sw60xg'
		if sysex_obj.command == 0 and mem_paramid[0] == 0: 
			sysex_obj.category = 'system'
			if mem_paramid[1] == 0: 
				sysex_obj.group, sysex_obj.param, sysex_obj.value = 'main', ['ad_12_part_on', firstval]
			if mem_paramid[1] == 1: 
				sysex_obj.group, sysex_obj.param, sysex_obj.value = 'main', ['karaoke_on', firstval]

	elif sysex_obj.model_id == 76:
		sysex_obj.known = True
		sysex_obj.model_name = 'yamaha_xg'

		if sysex_obj.command == 0 and mem_paramid[0] == 0:
			sysex_obj.category = 'system'

			if mem_paramid[1] == 0: sysex_obj.group, sysex_obj.param, sysex_obj.value = 'main', 'tune', mem_data
			if mem_paramid[1] == 4: sysex_obj.group, sysex_obj.param, sysex_obj.value = 'main', 'volume', firstval
			if mem_paramid[1] == 6: sysex_obj.group, sysex_obj.param, sysex_obj.value = 'main', 'transpose', firstval
			if mem_paramid[1] == 17: sysex_obj.group, sysex_obj.param, sysex_obj.value = 'main', 'ad_12_part_stereo', firstval
			if mem_paramid[1] == 125:
				if firstval== 0: sysex_obj.param, sysex_obj.value = 'reset', 'drum_setup_1'
				if firstval== 1: sysex_obj.param, sysex_obj.value = 'reset', 'drum_setup_2'
			if mem_paramid[1] == 126 and firstval== 0: sysex_obj.param = 'xg_on'
			if mem_paramid[1] == 126 and firstval== 0: sysex_obj.param, sysex_obj.value = 'reset', 'all_params'

		elif sysex_obj.command == 2 and mem_paramid[0] == 1:
			sysex_obj.category = 'effects'

			if mem_paramid[1] in [0,2,3,4,5,6,7,8,9,10,11,12,13,16,17,18,20]:
				sysex_obj.group = 'reverb'
				if mem_paramid[1] == 0: sysex_obj.param, sysex_obj.value = ['type', list(mem_data)]
				if mem_paramid[1] == 2: sysex_obj.param, sysex_obj.value = ['time', firstval]
				if mem_paramid[1] == 3: sysex_obj.param, sysex_obj.value = ['diffuse', firstval]
				if mem_paramid[1] == 4: sysex_obj.param, sysex_obj.value = ['inital_delay', firstval]
				if mem_paramid[1] == 5: sysex_obj.param, sysex_obj.value = ['hpf_cutoff', firstval]
				if mem_paramid[1] == 6: sysex_obj.param, sysex_obj.value = ['lpf_cutoff', firstval]
				if mem_paramid[1] == 7: sysex_obj.param, sysex_obj.value = ['width', firstval]
				if mem_paramid[1] == 8: sysex_obj.param, sysex_obj.value = ['height', firstval]
				if mem_paramid[1] == 9: sysex_obj.param, sysex_obj.value = ['depth', firstval]
				if mem_paramid[1] == 10: sysex_obj.param, sysex_obj.value = ['wall_variation', firstval]
				if mem_paramid[1] == 11: sysex_obj.param, sysex_obj.value = ['wet', firstval]
				if mem_paramid[1] == 12: sysex_obj.param, sysex_obj.value = ['send_return', firstval]
				if mem_paramid[1] == 13: sysex_obj.param, sysex_obj.value = ['pan', firstval]
				if mem_paramid[1] == 16: sysex_obj.param, sysex_obj.value = ['delay', firstval]
				if mem_paramid[1] == 17: sysex_obj.param, sysex_obj.value = ['density', firstval]
				if mem_paramid[1] == 18: sysex_obj.param, sysex_obj.value = ['early_reflection', firstval]
				if mem_paramid[1] == 20: sysex_obj.param, sysex_obj.value = ['feedback', firstval]

			if mem_paramid[1] in [32,34,35,36,37,39,40,41,42,43,44,45,46,51,52]:
				sysex_obj.group = 'chorus'

				if mem_paramid[1] == 32: sysex_obj.param, sysex_obj.value = ['type', list(mem_data)]
				if mem_paramid[1] == 34: sysex_obj.param, sysex_obj.value = ['lfo_frequency', firstval]
				if mem_paramid[1] == 35: sysex_obj.param, sysex_obj.value = ['lfo_phase_mod_depth', firstval]
				if mem_paramid[1] == 36: sysex_obj.param, sysex_obj.value = ['feedback', firstval]
				if mem_paramid[1] == 37: sysex_obj.param, sysex_obj.value = ['delay_offset', firstval]
	
				if mem_paramid[1] == 39: sysex_obj.param, sysex_obj.value = ['eq_low_freq', firstval]
				if mem_paramid[1] == 40: sysex_obj.param, sysex_obj.value = ['eq_low_gain', firstval]
				if mem_paramid[1] == 41: sysex_obj.param, sysex_obj.value = ['eq_hi_freq', firstval]
				if mem_paramid[1] == 42: sysex_obj.param, sysex_obj.value = ['eq_hi_gain', firstval]
				if mem_paramid[1] == 43: sysex_obj.param, sysex_obj.value = ['wet', firstval]
				if mem_paramid[1] == 44: sysex_obj.param, sysex_obj.value = ['send_return', firstval]
				if mem_paramid[1] == 45: sysex_obj.param, sysex_obj.value = ['pan', firstval]
				if mem_paramid[1] == 46: sysex_obj.param, sysex_obj.value = ['send_reverb', firstval]
	
				if mem_paramid[1] == 51: sysex_obj.param, sysex_obj.value = ['lfo_phase_diff', firstval]
				if mem_paramid[1] == 52: sysex_obj.param, sysex_obj.value = ['input_mode', firstval]

			if mem_paramid[1] == 64: 
				value = list(mem_data)
				fx_set = value
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
				sysex_obj.group, sysex_obj.param, sysex_obj.value = 'variation', 'fx_set', fx_set

			if mem_paramid[1] in [66,68,70,72,74,76,78,80,82,84]:
				fxval = int.from_bytes(mem_data, "little")
				sysex_obj.group, sysex_obj.value = 'variation_param', fxval
				if mem_paramid[1] == 66: sysex_obj.param = 0
				if mem_paramid[1] == 68: sysex_obj.param = 1
				if mem_paramid[1] == 70: sysex_obj.param = 2
				if mem_paramid[1] == 72: sysex_obj.param = 3
				if mem_paramid[1] == 74: sysex_obj.param = 4
				if mem_paramid[1] == 76: sysex_obj.param = 5
				if mem_paramid[1] == 78: sysex_obj.param = 6
				if mem_paramid[1] == 80: sysex_obj.param = 7
				if mem_paramid[1] == 82: sysex_obj.param = 8
				if mem_paramid[1] == 84: sysex_obj.param = 9

			if mem_paramid[1] in [86,87,88,89,90,91,92,93,94,95,96]:
				sysex_obj.group = 'variation'
				if mem_paramid[1] == 86: sysex_obj.param, sysex_obj.value = ['return', firstval]
				if mem_paramid[1] == 87: sysex_obj.param, sysex_obj.value = ['panorama', firstval]
				if mem_paramid[1] == 88: sysex_obj.param, sysex_obj.value = ['send_reverb', firstval]
				if mem_paramid[1] == 89: sysex_obj.param, sysex_obj.value = ['send_chorus', firstval]
				if mem_paramid[1] == 90: sysex_obj.param, sysex_obj.value = ['connection', firstval]
				if mem_paramid[1] == 91: sysex_obj.param, sysex_obj.value = ['part', firstval]
				if mem_paramid[1] == 92: sysex_obj.param, sysex_obj.value = ['mod_wheel', firstval]
				if mem_paramid[1] == 93: sysex_obj.param, sysex_obj.value = ['bend_wheel', firstval]
				if mem_paramid[1] == 94: sysex_obj.param, sysex_obj.value = ['ch_aftertouch', firstval]
				if mem_paramid[1] == 95: sysex_obj.param, sysex_obj.value = ['ctrl_1', firstval]
				if mem_paramid[1] == 96: sysex_obj.param, sysex_obj.value = ['ctrl_2', firstval]

			if mem_paramid[1] in [112,113,114,115,116,117]:
				sysex_obj.group = 'variation_param'
				if mem_paramid[1] == 112: sysex_obj.param, sysex_obj.value = [10, firstval]
				if mem_paramid[1] == 113: sysex_obj.param, sysex_obj.value = [11, firstval]
				if mem_paramid[1] == 114: sysex_obj.param, sysex_obj.value = [12, firstval]
				if mem_paramid[1] == 115: sysex_obj.param, sysex_obj.value = [13, firstval]
				if mem_paramid[1] == 116: sysex_obj.param, sysex_obj.value = [14, firstval]
				if mem_paramid[1] == 117: sysex_obj.param, sysex_obj.value = [15, firstval]

		elif sysex_obj.command == 2 and mem_paramid[0] == 64:
			sysex_obj.category = 'effects'
			if mem_paramid[1] == 0: sysex_obj.group, sysex_obj.param, sysex_obj.value = 'eq', 'type', firstval

			if 1 <= mem_paramid[1] <= 20:
				num = mem_paramid[1]-1
				sysex_obj.group = 'eq_'+str((num//4)+1)
				sysex_obj.param = ['gain','freq','q','shape'][num%4]

		elif sysex_obj.command == 3 and mem_paramid[0] == 0:

			sysex_obj.category = 'effects'

			if mem_paramid[1] in [0,12,13,14,15,16,17]:
				sysex_obj.group = 'xg_fx'
				if mem_paramid[1] == 0: sysex_obj.param, sysex_obj.value = ['type', list(mem_data)]
				if mem_paramid[1] == 12: sysex_obj.param, sysex_obj.value = ['part', firstval]
				if mem_paramid[1] == 13: sysex_obj.param, sysex_obj.value = ['mw_depth', firstval]
				if mem_paramid[1] == 14: sysex_obj.param, sysex_obj.value = ['bend', firstval]
				if mem_paramid[1] == 15: sysex_obj.param, sysex_obj.value = ['cat', firstval]
				if mem_paramid[1] == 16: sysex_obj.param, sysex_obj.value = ['ac1', firstval]
				if mem_paramid[1] == 17: sysex_obj.param, sysex_obj.value = ['ac2', firstval]

			if mem_paramid[1] in [2,3,4,5,6,7,8,9,10,11,32,33,34,35,36]:
				sysex_obj.group = 'xg_fx_param'
				if mem_paramid[1] == 2: sysex_obj.param, sysex_obj.value = [0, firstval]
				if mem_paramid[1] == 3: sysex_obj.param, sysex_obj.value = [1, firstval]
				if mem_paramid[1] == 4: sysex_obj.param, sysex_obj.value = [2, firstval]
				if mem_paramid[1] == 5: sysex_obj.param, sysex_obj.value = [3, firstval]
				if mem_paramid[1] == 6: sysex_obj.param, sysex_obj.value = [4, firstval]
				if mem_paramid[1] == 7: sysex_obj.param, sysex_obj.value = [5, firstval]
				if mem_paramid[1] == 8: sysex_obj.param, sysex_obj.value = [6, firstval]
				if mem_paramid[1] == 9: sysex_obj.param, sysex_obj.value = [7, firstval]
				if mem_paramid[1] == 10: sysex_obj.param, sysex_obj.value = [8, firstval]
				if mem_paramid[1] == 11: sysex_obj.param, sysex_obj.value = [9, firstval]
				if mem_paramid[1] == 32: sysex_obj.param, sysex_obj.value = [10, firstval]
				if mem_paramid[1] == 33: sysex_obj.param, sysex_obj.value = [11, firstval]
				if mem_paramid[1] == 34: sysex_obj.param, sysex_obj.value = [12, firstval]
				if mem_paramid[1] == 35: sysex_obj.param, sysex_obj.value = [13, firstval]
				if mem_paramid[1] == 36: sysex_obj.param, sysex_obj.value = [14, firstval]

		elif sysex_obj.command == 6 and mem_paramid[0] == 0:
			sysex_obj.category, sysex_obj.group = ['display', 'text'], 
			sysex_obj.param, sysex_obj.value = ['text', mem_data]

		elif sysex_obj.command == 7:
			sysex_obj.category, sysex_obj.group =  ['display', 'bitmap'], 
			sysex_obj.param, sysex_obj.value = [data_bytes.splitbyte(mem_paramid[0]), mem_data]

		elif sysex_obj.command == 8:
			sysex_obj.category, sysex_obj.group = ['part', mem_paramid[0]]
			if mem_paramid[1] != 9: sysex_obj.value = firstval
			else: sysex_obj.value = mem_data
			if mem_paramid[1] == 0: sysex_obj.param = "element_reserve"
			if mem_paramid[1] == 1: sysex_obj.param = "bank_select_msb"
			if mem_paramid[1] == 2: sysex_obj.param = "bank_select_lsb"
			if mem_paramid[1] == 3: sysex_obj.param = "program_number"
			if mem_paramid[1] == 4: sysex_obj.param = "receive_midi_channel"
			if mem_paramid[1] == 5: sysex_obj.param = "mono_poly"
			if mem_paramid[1] == 6: sysex_obj.param = "same_note_number_key_on_assign"
			if mem_paramid[1] == 7: sysex_obj.param = "part_mode"
			if mem_paramid[1] == 8: sysex_obj.param = "note_shift"
			if mem_paramid[1] == 9: sysex_obj.param = "detune"
			if mem_paramid[1] == 11: sysex_obj.param = "volume"
			if mem_paramid[1] == 12: sysex_obj.param = "velocity_sense_depth"
			if mem_paramid[1] == 13: sysex_obj.param = "velocity_sense_offset"
			if mem_paramid[1] == 14: sysex_obj.param = "panorama"
			if mem_paramid[1] == 15: sysex_obj.param = "note_limit_low"
			if mem_paramid[1] == 16: sysex_obj.param = "note_limit_high"
			if mem_paramid[1] == 17: sysex_obj.param = "dry_level"
			if mem_paramid[1] == 18: sysex_obj.param = "chorus_send"
			if mem_paramid[1] == 19: sysex_obj.param = "reverb_send"
			if mem_paramid[1] == 20: sysex_obj.param = "variation_send"
			if mem_paramid[1] == 21: sysex_obj.param = "vibrato_rate"
			if mem_paramid[1] == 22: sysex_obj.param = "vibrato_depth"
			if mem_paramid[1] == 23: sysex_obj.param = "vibrato_delay"
			if mem_paramid[1] == 24: sysex_obj.param = "filter_cutoff_frequency"
			if mem_paramid[1] == 25: sysex_obj.param = "filter_resonance"
			if mem_paramid[1] == 26: sysex_obj.param = "eg_attack_time"
			if mem_paramid[1] == 27: sysex_obj.param = "eg_decay_time"
			if mem_paramid[1] == 28: sysex_obj.param = "eg_release_time"
			if mem_paramid[1] == 29: sysex_obj.param = "mw_pitch_control"
			if mem_paramid[1] == 30: sysex_obj.param = "mw_filter_control"
			if mem_paramid[1] == 31: sysex_obj.param = "mw_amplitude_control"
			if mem_paramid[1] == 32: sysex_obj.param = "mw_lfo_pitch_modulation_depth"
			if mem_paramid[1] == 33: sysex_obj.param = "mw_lfo_filter_modulation_depth"
			if mem_paramid[1] == 34: sysex_obj.param = "mw_lfo_amplitude_modulation_depth"
			if mem_paramid[1] == 35: sysex_obj.param = "bend_pitch_control"
			if mem_paramid[1] == 36: sysex_obj.param = "bend_filter_control"
			if mem_paramid[1] == 37: sysex_obj.param = "bend_amplitude_control"
			if mem_paramid[1] == 38: sysex_obj.param = "bend_lfo_pitch_modulation_depth"
			if mem_paramid[1] == 39: sysex_obj.param = "bend_lfo_filter_modulation_depth"
			if mem_paramid[1] == 40: sysex_obj.param = "bend_lfo_amplitude_modulation_depth"
			if mem_paramid[1] == 48: sysex_obj.param = "receive_pitch_bend"
			if mem_paramid[1] == 49: sysex_obj.param = "receive_channel_after_touch"
			if mem_paramid[1] == 50: sysex_obj.param = "receive_program_change"
			if mem_paramid[1] == 51: sysex_obj.param = "receive_control_change"
			if mem_paramid[1] == 52: sysex_obj.param = "receive_polyphonic_after_touch"
			if mem_paramid[1] == 53: sysex_obj.param = "receive_note_messages"
			if mem_paramid[1] == 54: sysex_obj.param = "receive_rpn"
			if mem_paramid[1] == 55: sysex_obj.param = "receive_nrpn"
			if mem_paramid[1] == 56: sysex_obj.param = "receive_modulation_wheel"
			if mem_paramid[1] == 57: sysex_obj.param = "receive_volume"
			if mem_paramid[1] == 58: sysex_obj.param = "receive_pan"
			if mem_paramid[1] == 59: sysex_obj.param = "receive_expression"
			if mem_paramid[1] == 60: sysex_obj.param = "receive_hold_pedal"
			if mem_paramid[1] == 61: sysex_obj.param = "receive_portamento"
			if mem_paramid[1] == 62: sysex_obj.param = "receive_sostenuto_pedal"
			if mem_paramid[1] == 63: sysex_obj.param = "receive_soft_pedal"
			if mem_paramid[1] == 64: sysex_obj.param = "receive_bank_select"
			if mem_paramid[1] == 65: sysex_obj.param = "scale_tuning_c"
			if mem_paramid[1] == 66: sysex_obj.param = "scale_tuning_c_s"
			if mem_paramid[1] == 67: sysex_obj.param = "scale_tuning_d"
			if mem_paramid[1] == 68: sysex_obj.param = "scale_tuning_d_s"
			if mem_paramid[1] == 69: sysex_obj.param = "scale_tuning_e"
			if mem_paramid[1] == 70: sysex_obj.param = "scale_tuning_f"
			if mem_paramid[1] == 71: sysex_obj.param = "scale_tuning_f_s"
			if mem_paramid[1] == 72: sysex_obj.param = "scale_tuning_g"
			if mem_paramid[1] == 73: sysex_obj.param = "scale_tuning_g_s"
			if mem_paramid[1] == 74: sysex_obj.param = "scale_tuning_a"
			if mem_paramid[1] == 75: sysex_obj.param = "scale_tuning_a_s"
			if mem_paramid[1] == 76: sysex_obj.param = "scale_tuning_b"
			if mem_paramid[1] == 77: sysex_obj.param = "cat_pitch_control"
			if mem_paramid[1] == 78: sysex_obj.param = "cat_filter_control"
			if mem_paramid[1] == 79: sysex_obj.param = "cat_amplitude_control"
			if mem_paramid[1] == 80: sysex_obj.param = "cat_lfo_pitch_modulation_depth"
			if mem_paramid[1] == 81: sysex_obj.param = "cat_lfo_filter_modulation_depth"
			if mem_paramid[1] == 82: sysex_obj.param = "cat_lfo_amplitude_modulation_depth"
			if mem_paramid[1] == 83: sysex_obj.param = "pat_pitch_control"
			if mem_paramid[1] == 84: sysex_obj.param = "pat_filter_control"
			if mem_paramid[1] == 85: sysex_obj.param = "pat_amplitude_control"
			if mem_paramid[1] == 86: sysex_obj.param = "pat_lfo_pitch_modulation_depth"
			if mem_paramid[1] == 87: sysex_obj.param = "pat_lfo_filter_modulation_depth"
			if mem_paramid[1] == 88: sysex_obj.param = "pat_lfo_amplitude_modulation_depth"
			if mem_paramid[1] == 89: sysex_obj.param = "ac1_controller_number"
			if mem_paramid[1] == 90: sysex_obj.param = "ac1_pitch_control"
			if mem_paramid[1] == 91: sysex_obj.param = "ac1_filter_control"
			if mem_paramid[1] == 92: sysex_obj.param = "ac1_amplitude_control"
			if mem_paramid[1] == 93: sysex_obj.param = "ac1_lfo_pitch_modulation_depth"
			if mem_paramid[1] == 94: sysex_obj.param = "ac1_lfo_filter_modulation_depth"
			if mem_paramid[1] == 95: sysex_obj.param = "ac1_lfo_amplitude_modulation_depth"
			if mem_paramid[1] == 96: sysex_obj.param = "ac2_controller_number"
			if mem_paramid[1] == 97: sysex_obj.param = "ac2_pitch_control"
			if mem_paramid[1] == 98: sysex_obj.param = "ac2_filter_control"
			if mem_paramid[1] == 99: sysex_obj.param = "ac2_amplitude_control"
			if mem_paramid[1] == 100: sysex_obj.param = "ac2_lfo_pitch_modulation_depth"
			if mem_paramid[1] == 101: sysex_obj.param = "ac2_lfo_filter_modulation_depth"
			if mem_paramid[1] == 102: sysex_obj.param = "ac2_lfo_amplitude_modulation_depth"
			if mem_paramid[1] == 103: sysex_obj.param = "portamento_switch"
			if mem_paramid[1] == 104: sysex_obj.param = "portamento_time"
			if mem_paramid[1] == 105: sysex_obj.param = "pitch_eg_initial_level"
			if mem_paramid[1] == 106: sysex_obj.param = "pitch_eg_attack_time"
			if mem_paramid[1] == 107: sysex_obj.param = "pitch_eg_release_level"
			if mem_paramid[1] == 108: sysex_obj.param = "pitch_eg_release_time"
			if mem_paramid[1] == 109: sysex_obj.param = "velocity_limit_low"
			if mem_paramid[1] == 110: sysex_obj.param = "velocity_limit_high"
			if mem_paramid[1] == 114: sysex_obj.param = "eq_bass_gain"
			if mem_paramid[1] == 115: sysex_obj.param = "eq_treble_gain"
			if mem_paramid[1] == 118: sysex_obj.param = "eq_bass_frequency"
			if mem_paramid[1] == 119: sysex_obj.param = "eq_treble_frequency"
		