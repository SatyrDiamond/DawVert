# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes

def decode(model, device, command, data):
	devicename = 'unknown'
	mem_address = data[0:3]
	mem_data = data[3:][:-1]

	groups = [None, None]
	nameval = [None, None]
	isdatadump = False

	firstval = int(mem_data[0]) if len(mem_data) != 0 else 0

	#print(bytes.hex(mem_address), bytes.hex(mem_data))

	if model == 63: #sc88
		devicename = 'e_series'
		bytesplit = data_bytes.splitbyte(mem_address[1])
		if mem_address[0] == 64: #0x40
			groups[0] = 'system'
			if bytesplit[1] == 0:
				if mem_address[2] == 0: nameval = ['master_tune', mem_data]
				if mem_address[2] == 4: nameval = ['master_volume', mem_data]
				if mem_address[2] == 127: nameval = ['gs_reset', firstval]

	if model == 66: #sc88
		devicename = 'sc88'
		bytesplit = data_bytes.splitbyte(mem_address[1])

		if mem_address[0] == 0: #0x00
			if mem_address == b'\x00\x00\x7f': 
				groups[0] = 'main'
				nameval = ['sys_mode', int(mem_data[0])]

		if mem_address[0] == 32: #0x20
			groups[0] = 'user_tone_bank'

		if mem_address[0] == 33: #0x21
			groups = ['user_drumset',bytesplit[0]]
			groups += [mem_address[2]]
			
			if bytesplit[1] != 0:
				if bytesplit[1] == 1: nameval = ['play_note', firstval]
				elif bytesplit[1] == 2: nameval = ['level', firstval]
				elif bytesplit[1] == 3: nameval = ['assign_groupnum', firstval]
				elif bytesplit[1] == 4: nameval = ['pan', firstval]
				elif bytesplit[1] == 5: nameval = ['reverb_send', firstval]
				elif bytesplit[1] == 6: nameval = ['chorus_send', firstval]
				elif bytesplit[1] == 7: nameval = ['rx_note_off', firstval]
				elif bytesplit[1] == 8: nameval = ['rx_note_on', firstval]
				elif bytesplit[1] == 9: nameval = ['delay_send', firstval]
				elif bytesplit[1] == 10: nameval = ['source_drumset', firstval]
				elif bytesplit[1] == 11: nameval = ['program_number', firstval]
				elif bytesplit[1] == 12: nameval = ['source_note_num', firstval]

		if mem_address[0] == 34: #0x22
			groups[0] = 'user_efx'

		if mem_address[0] == 35: #0x23
			groups[0] = 'user_patch_common'

		if mem_address[0] == 36: #0x24
			groups[0] = 'user_patch_part1_1'

		if mem_address[0] == 37: #0x25
			groups[0] = 'user_patch_part2_1'

		if mem_address[0] == 38: #0x26
			groups[0] = 'user_patch_part1_2'

		if mem_address[0] == 39: #0x27
			groups[0] = 'user_patch_part2_2'

		if mem_address[0] == 64 or mem_address[0] == 80: #0x40
			if mem_address[0] == 64: groups[0] = 'patch_a'
			if mem_address[0] == 80: groups[0] = 'patch_b'

			if bytesplit[0] == 0:

				if bytesplit[1] == 0:
					if mem_address[2] == 0: nameval = ['master_tune', mem_data]
					if mem_address[2] == 4: nameval = ['master_volume', mem_data]
					if mem_address[2] == 5: nameval = ['master_keyshift', mem_data]
					if mem_address[2] == 6: nameval = ['master_pan', mem_data]
					if mem_address[2] == 127: nameval = ['gs_reset', firstval]

				if bytesplit[1] == 1:
					if mem_address[2] == 48: groups[1], nameval = 'reverb', ['macro', firstval]
					if mem_address[2] == 49: groups[1], nameval = 'reverb', ['character', firstval]
					if mem_address[2] == 50: groups[1], nameval = 'reverb', ['pre_lpf', firstval]
					if mem_address[2] == 51: groups[1], nameval = 'reverb', ['level', firstval]
					if mem_address[2] == 52: groups[1], nameval = 'reverb', ['time', firstval]
					if mem_address[2] == 53: groups[1], nameval = 'reverb', ['delay_feedback', firstval]
					if mem_address[2] == 55: groups[1], nameval = 'reverb', ['predelay', firstval]

					if mem_address[2] == 56: groups[1], nameval = 'chorus', ['macro', firstval]
					if mem_address[2] == 57: groups[1], nameval = 'chorus', ['pre_lpf', firstval]
					if mem_address[2] == 58: groups[1], nameval = 'chorus', ['level', firstval]
					if mem_address[2] == 59: groups[1], nameval = 'chorus', ['feedback', firstval]
					if mem_address[2] == 60: groups[1], nameval = 'chorus', ['delay', firstval]
					if mem_address[2] == 61: groups[1], nameval = 'chorus', ['rate', firstval]
					if mem_address[2] == 62: groups[1], nameval = 'chorus', ['depth', firstval]
					if mem_address[2] == 63: groups[1], nameval = 'chorus', ['send_reverb', firstval]
					if mem_address[2] == 64: groups[1], nameval = 'chorus', ['send_delay', firstval]

					if mem_address[2] == 80: groups[1], nameval = 'delay', ['macro', firstval]
					if mem_address[2] == 81: groups[1], nameval = 'delay', ['pre_lpf', firstval]
					if mem_address[2] == 82: groups[1], nameval = 'delay', ['time_center', firstval]
					if mem_address[2] == 83: groups[1], nameval = 'delay', ['time_ratio_l', firstval]
					if mem_address[2] == 84: groups[1], nameval = 'delay', ['time_ratio_r', firstval]
					if mem_address[2] == 85: groups[1], nameval = 'delay', ['lvl_center', firstval]
					if mem_address[2] == 86: groups[1], nameval = 'delay', ['level_l', firstval]
					if mem_address[2] == 87: groups[1], nameval = 'delay', ['level_r', firstval]
					if mem_address[2] == 88: groups[1], nameval = 'delay', ['level', firstval]
					if mem_address[2] == 89: groups[1], nameval = 'delay', ['feedback', firstval]
					if mem_address[2] == 90: groups[1], nameval = 'delay', ['send_reverb', firstval]

				if bytesplit[1] == 2:
					if mem_address[2] == 0: groups[1], nameval = 'eq', ['low_freq', firstval]
					if mem_address[2] == 1: groups[1], nameval = 'eq', ['low_gain', firstval]
					if mem_address[2] == 2: groups[1], nameval = 'eq', ['hi_freq', firstval]
					if mem_address[2] == 3: groups[1], nameval = 'eq', ['hi_gain', firstval]

				if bytesplit[1] == 3:
					if mem_address[2] == 0: groups[1], nameval = 'efx', ['type', firstval]
					if 22 >= mem_address[2] >= 3: groups[1], nameval = 'efx', ['param'+str(mem_address[2]-2), firstval]
					if mem_address[2] == 23: groups[1], nameval = 'efx', ['send_reverb', firstval]
					if mem_address[2] == 24: groups[1], nameval = 'efx', ['send_chorus', firstval]
					if mem_address[2] == 25: groups[1], nameval = 'efx', ['send_delay', firstval]
					if mem_address[2] == 27: groups[1], nameval = 'efx', ['ctrl_source1', firstval]
					if mem_address[2] == 28: groups[1], nameval = 'efx', ['ctrl_depth1', firstval]
					if mem_address[2] == 29: groups[1], nameval = 'efx', ['ctrl_source2', firstval]
					if mem_address[2] == 30: groups[1], nameval = 'efx', ['ctrl_depth2', firstval]
					if mem_address[2] == 31: groups[1], nameval = 'efx', ['send_eq_switch', firstval]

			if bytesplit[0] == 1:
				groups.append(bytesplit[1])
				subnum = data_bytes.splitbyte(mem_address[2])
				groups[1] = 'block'
				if mem_address[2] == 0: nameval = ['rx_tonenum', mem_data]
				if mem_address[2] == 2: nameval = ['rx_channel', firstval]
				if mem_address[2] == 3: nameval = ['rx_pitchbend', firstval]
				if mem_address[2] == 4: nameval = ['rx_ch_pressure', firstval]
				if mem_address[2] == 5: nameval = ['rx_program_change', firstval]
				if mem_address[2] == 6: nameval = ['rx_control_change', firstval]
				if mem_address[2] == 7: nameval = ['rx_poly_pressure', firstval]
				if mem_address[2] == 8: nameval = ['rx_note_message', firstval]
				if mem_address[2] == 9: nameval = ['rx_rpn', firstval]
				if mem_address[2] == 10: nameval = ['rx_nrpn', firstval]
				if mem_address[2] == 11: nameval = ['rx_modulation', firstval]
				if mem_address[2] == 12: nameval = ['rx_volume', firstval]
				if mem_address[2] == 13: nameval = ['rx_panpot', firstval]
				if mem_address[2] == 14: nameval = ['rx_expression', firstval]
				if mem_address[2] == 15: nameval = ['rx_hold1', firstval]
				if mem_address[2] == 16: nameval = ['rx_portamento', firstval]
				if mem_address[2] == 17: nameval = ['rx_sostenuto', firstval]
				if mem_address[2] == 18: nameval = ['rx_soft', firstval]
				if mem_address[2] == 19: nameval = ['mono_poly', firstval]
				if mem_address[2] == 20: nameval = ['assign', firstval]
				if mem_address[2] == 21: nameval = ['use_rhythm', firstval]

				if mem_address[2] == 22: nameval = ['pitch_key_shift', firstval]
				if mem_address[2] == 23: nameval = ['pitch_offset_fine', mem_data]

				if mem_address[2] == 25: nameval = ['part_level', firstval]
				if mem_address[2] == 26: nameval = ['vel_sense_depth', firstval]
				if mem_address[2] == 27: nameval = ['vel_sense_offset', firstval]
				if mem_address[2] == 28: nameval = ['part_panpot', firstval]
				if mem_address[2] == 29: nameval = ['kbd_range_low', firstval]
				if mem_address[2] == 30: nameval = ['kbd_range_hi', firstval]
				if mem_address[2] == 31: nameval = ['cc1_cont_num', firstval]
				if mem_address[2] == 32: nameval = ['cc2_cont_num', firstval]

				if mem_address[2] == 33: nameval = ['chorus_send', firstval]
				if mem_address[2] == 34: nameval = ['reverb_send', firstval]
				if mem_address[2] == 35: nameval = ['rx_bank', firstval]
				if mem_address[2] == 36: nameval = ['rx_bank_lsb', firstval]
				if mem_address[2] == 42: nameval = ['pitch_fine_tune', int(mem_data[0:2])]
				if mem_address[2] == 44: nameval = ['delay_send_level', firstval]

				if subnum[0] == 3: nameval = ['tone_modify_'+str(subnum[1]), firstval]
				if mem_address[2] == 64: nameval = ['scale_tuning', list(mem_data[0:12])]

			if bytesplit[0] == 2:
				groups.append(bytesplit[1])
				subnum = data_bytes.splitbyte(mem_address[2])
				lfo_name = 'unknown'
				if subnum[0] == 0: lfo_name = 'mod'
				if subnum[0] == 1: lfo_name = 'bend'
				if subnum[0] == 2: lfo_name = 'caf'
				if subnum[0] == 3: lfo_name = 'paf'
				if subnum[0] == 4: lfo_name = 'cc1'
				if subnum[0] == 5: lfo_name = 'cc2'

				groups[1] = 'block_lfo'
				if subnum[1] == 0: nameval = [lfo_name+'_pitch_ctrl', firstval]
				if subnum[1] == 1: nameval = [lfo_name+'_tvf_cutoff_ctrl', firstval]
				if subnum[1] == 2: nameval = [lfo_name+'_amp_ctrl', firstval]
				if subnum[1] == 3: nameval = [lfo_name+'_lfo1_rate', firstval]
				if subnum[1] == 4: nameval = [lfo_name+'_lfo1_pitch', firstval]
				if subnum[1] == 5: nameval = [lfo_name+'_lfo1_tvf', firstval]
				if subnum[1] == 6: nameval = [lfo_name+'_lfo1_tva', firstval]
				if subnum[1] == 7: nameval = [lfo_name+'_lfo2_rate', firstval]
				if subnum[1] == 8: nameval = [lfo_name+'_lfo2_pitch', firstval]
				if subnum[1] == 9: nameval = [lfo_name+'_lfo2_tvf', firstval]
				if subnum[1] == 10: nameval = [lfo_name+'_lfo2_tva', firstval]

			if bytesplit[0] == 4:
				groups[1] = 'block'
				groups.append(bytesplit[1])
				if mem_address[2] == 0: nameval = ['tone_map_num', firstval]
				if mem_address[2] == 1: nameval = ['tone_map_0_num', firstval]
				if mem_address[2] == 32: nameval = ['eq_on', firstval]
				if mem_address[2] == 33: nameval = ['output_assign', firstval]
				if mem_address[2] == 34: nameval = ['part_efx_assign', firstval]

		if mem_address[0] in [65, 81]: #0x41
			if mem_address[0] == 65: groups[0] = 'drum_a'
			if mem_address[0] == 81: groups[0] = 'drum_b'
			groups[1] = bytesplit[0]
			groups.append(mem_address[2])
			
			if bytesplit[1] != 0:
				nameval[1] = firstval
				if bytesplit[1] == 1: nameval[0] = 'pitch_coarse'
				elif bytesplit[1] == 2: nameval[0] = 'level'
				elif bytesplit[1] == 3: nameval[0] = 'assign_groupnum'
				elif bytesplit[1] == 4: nameval[0] = 'panpot'
				elif bytesplit[1] == 5: nameval[0] = 'reverb_send'
				elif bytesplit[1] == 6: nameval[0] = 'chorus_send'
				elif bytesplit[1] == 7: nameval[0] = 'rx_note_off'
				elif bytesplit[1] == 8: nameval[0] = 'rx_note_on'
				elif bytesplit[1] == 9: nameval[0] = 'delay_send'

		if mem_address[0] in [72, 73]:
			isdatadump = True

	if model == 69: #display
		devicename = 'display'
		bytesplit = data_bytes.splitbyte(mem_address[1])
		if mem_address[0] == 16:
			groups[0] = 'display'
			if mem_address[1] != 32:
				if bytesplit[1] != 0: groups[1], nameval = 'bitmap', [bytesplit[1], mem_data]
				else: groups[1], nameval = 'text', ['text', mem_data]
			else: 
				if mem_address[2] == 0: groups[1], nameval = 'displaypage', ['num', firstval]
				if mem_address[2] == 1: groups[1], nameval = 'time', ['sec', firstval/0.48]

	return devicename, groups, nameval