
from functions import data_bytes

def decode(sysex_obj, bstream):
	mem_address = bstream.read(3)
	mem_data = bstream.read()

	#isdatadump = False

	firstval = int(mem_data[0]) if len(mem_data) != 0 else 0

	#print(bytes.hex(mem_address), bytes.hex(mem_data))

	if sysex_obj.model_id == 63: #e_series
		sysex_obj.known = True
		sysex_obj.model_name = 'e_series'
		bytesplit = data_bytes.splitbyte(mem_address[1])
		if mem_address[0] == 64: #0x40
			sysex_obj.category = 'system'
			if bytesplit[1] == 0:
				if mem_address[2] == 0: sysex_obj.param, sysex_obj.value = ['master_tune', mem_data]
				if mem_address[2] == 4: sysex_obj.param, sysex_obj.value = ['master_volume', mem_data]
				if mem_address[2] == 127: sysex_obj.param, sysex_obj.value = ['gs_reset', firstval]

	if sysex_obj.model_id == 22: #mt32
		sysex_obj.known = True
		sysex_obj.model_name = 'mt32'

	if sysex_obj.model_id == 66: #sc88
		sysex_obj.known = True
		sysex_obj.model_name = 'sc88'
		bytesplit = data_bytes.splitbyte(mem_address[1])

		if mem_address[0] == 0: #0x00
			if mem_address == b'\x00\x00\x7f': 
				sysex_obj.category = 'main'
				sysex_obj.param, sysex_obj.value = ['sys_mode', int(mem_data[0])]

		if mem_address[0] == 32: #0x20
			sysex_obj.category = 'user_tone_bank'

		if mem_address[0] == 33: #0x21
			sysex_obj.category = 'user_drumset'
			sysex_obj.group = bytesplit[0]
			sysex_obj.subgroup = mem_address[2]
			
			if bytesplit[1] != 0:
				if bytesplit[1] == 1: sysex_obj.param, sysex_obj.value = ['play_note', firstval]
				elif bytesplit[1] == 2: sysex_obj.param, sysex_obj.value = ['level', firstval]
				elif bytesplit[1] == 3: sysex_obj.param, sysex_obj.value = ['assign_groupnum', firstval]
				elif bytesplit[1] == 4: sysex_obj.param, sysex_obj.value = ['pan', firstval]
				elif bytesplit[1] == 5: sysex_obj.param, sysex_obj.value = ['reverb_send', firstval]
				elif bytesplit[1] == 6: sysex_obj.param, sysex_obj.value = ['chorus_send', firstval]
				elif bytesplit[1] == 7: sysex_obj.param, sysex_obj.value = ['rx_note_off', firstval]
				elif bytesplit[1] == 8: sysex_obj.param, sysex_obj.value = ['rx_note_on', firstval]
				elif bytesplit[1] == 9: sysex_obj.param, sysex_obj.value = ['delay_send', firstval]
				elif bytesplit[1] == 10: sysex_obj.param, sysex_obj.value = ['source_drumset', firstval]
				elif bytesplit[1] == 11: sysex_obj.param, sysex_obj.value = ['program_number', firstval]
				elif bytesplit[1] == 12: sysex_obj.param, sysex_obj.value = ['source_note_num', firstval]

		if mem_address[0] == 34: #0x22
			sysex_obj.category = 'user_efx'

		if mem_address[0] == 35: #0x23
			sysex_obj.category = 'user_patch_common'

		if mem_address[0] == 36: #0x24
			sysex_obj.category = 'user_patch_part1_1'

		if mem_address[0] == 37: #0x25
			sysex_obj.category = 'user_patch_part2_1'

		if mem_address[0] == 38: #0x26
			sysex_obj.category = 'user_patch_part1_2'

		if mem_address[0] == 39: #0x27
			sysex_obj.category = 'user_patch_part2_2'

		if mem_address[0] == 64 or mem_address[0] == 80: #0x40
			if mem_address[0] == 64: sysex_obj.category = 'patch_a'
			if mem_address[0] == 80: sysex_obj.category = 'patch_b'

			if bytesplit[0] == 0:

				if bytesplit[1] == 0:
					if mem_address[2] == 0: sysex_obj.param, sysex_obj.value = ['master_tune', mem_data]
					if mem_address[2] == 4: sysex_obj.param, sysex_obj.value = ['master_volume', mem_data]
					if mem_address[2] == 5: sysex_obj.param, sysex_obj.value = ['master_keyshift', mem_data]
					if mem_address[2] == 6: sysex_obj.param, sysex_obj.value = ['master_pan', mem_data]
					if mem_address[2] == 127: sysex_obj.param, sysex_obj.value = ['gs_reset', firstval]

				if bytesplit[1] == 1:
					if mem_address[2] in [48, 49, 50, 51, 52, 53, 55]:
						sysex_obj.group = 'reverb'
						if mem_address[2] == 48: sysex_obj.param, sysex_obj.value = ['macro', firstval]
						if mem_address[2] == 49: sysex_obj.param, sysex_obj.value = ['character', firstval]
						if mem_address[2] == 50: sysex_obj.param, sysex_obj.value = ['pre_lpf', firstval]
						if mem_address[2] == 51: sysex_obj.param, sysex_obj.value = ['level', firstval]
						if mem_address[2] == 52: sysex_obj.param, sysex_obj.value = ['time', firstval]
						if mem_address[2] == 53: sysex_obj.param, sysex_obj.value = ['delay_feedback', firstval]
						if mem_address[2] == 55: sysex_obj.param, sysex_obj.value = ['predelay', firstval]

					if mem_address[2] in [56, 57, 58, 59, 60, 61, 62, 63, 64]:
						sysex_obj.group = 'chorus'
						if mem_address[2] == 56: sysex_obj.param, sysex_obj.value = ['macro', firstval]
						if mem_address[2] == 57: sysex_obj.param, sysex_obj.value = ['pre_lpf', firstval]
						if mem_address[2] == 58: sysex_obj.param, sysex_obj.value = ['level', firstval]
						if mem_address[2] == 59: sysex_obj.param, sysex_obj.value = ['feedback', firstval]
						if mem_address[2] == 60: sysex_obj.param, sysex_obj.value = ['delay', firstval]
						if mem_address[2] == 61: sysex_obj.param, sysex_obj.value = ['rate', firstval]
						if mem_address[2] == 62: sysex_obj.param, sysex_obj.value = ['depth', firstval]
						if mem_address[2] == 63: sysex_obj.param, sysex_obj.value = ['send_reverb', firstval]
						if mem_address[2] == 64: sysex_obj.param, sysex_obj.value = ['send_delay', firstval]

					if mem_address[2] in [80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90]:
						sysex_obj.group = 'delay'
						if mem_address[2] == 80: sysex_obj.param, sysex_obj.value = ['macro', firstval]
						if mem_address[2] == 81: sysex_obj.param, sysex_obj.value = ['pre_lpf', firstval]
						if mem_address[2] == 82: sysex_obj.param, sysex_obj.value = ['time_center', firstval]
						if mem_address[2] == 83: sysex_obj.param, sysex_obj.value = ['time_ratio_l', firstval]
						if mem_address[2] == 84: sysex_obj.param, sysex_obj.value = ['time_ratio_r', firstval]
						if mem_address[2] == 85: sysex_obj.param, sysex_obj.value = ['lvl_center', firstval]
						if mem_address[2] == 86: sysex_obj.param, sysex_obj.value = ['level_l', firstval]
						if mem_address[2] == 87: sysex_obj.param, sysex_obj.value = ['level_r', firstval]
						if mem_address[2] == 88: sysex_obj.param, sysex_obj.value = ['level', firstval]
						if mem_address[2] == 89: sysex_obj.param, sysex_obj.value = ['feedback', firstval]
						if mem_address[2] == 90: sysex_obj.param, sysex_obj.value = ['send_reverb', firstval]

				if bytesplit[1] == 2:
					sysex_obj.group = 'eq'
					if mem_address[2] == 0: sysex_obj.param, sysex_obj.value = ['low_freq', firstval]
					if mem_address[2] == 1: sysex_obj.param, sysex_obj.value = ['low_gain', firstval]
					if mem_address[2] == 2: sysex_obj.param, sysex_obj.value = ['hi_freq', firstval]
					if mem_address[2] == 3: sysex_obj.param, sysex_obj.value = ['hi_gain', firstval]

				if bytesplit[1] == 3:
					sysex_obj.group = 'efx'
					if mem_address[2] == 0: sysex_obj.param, sysex_obj.value = ['type', firstval]
					if 22 >= mem_address[2] >= 3: sysex_obj.param, sysex_obj.value = ['param'+str(mem_address[2]-2), firstval]
					if mem_address[2] == 23: sysex_obj.param, sysex_obj.value = ['send_reverb', firstval]
					if mem_address[2] == 24: sysex_obj.param, sysex_obj.value = ['send_chorus', firstval]
					if mem_address[2] == 25: sysex_obj.param, sysex_obj.value = ['send_delay', firstval]
					if mem_address[2] == 27: sysex_obj.param, sysex_obj.value = ['ctrl_source1', firstval]
					if mem_address[2] == 28: sysex_obj.param, sysex_obj.value = ['ctrl_depth1', firstval]
					if mem_address[2] == 29: sysex_obj.param, sysex_obj.value = ['ctrl_source2', firstval]
					if mem_address[2] == 30: sysex_obj.param, sysex_obj.value = ['ctrl_depth2', firstval]
					if mem_address[2] == 31: sysex_obj.param, sysex_obj.value = ['send_eq_switch', firstval]

			if bytesplit[0] == 1:
				sysex_obj.group = 'block'
				sysex_obj.num = bytesplit[1]
				subnum = data_bytes.splitbyte(mem_address[2])
				if mem_address[2] == 0: sysex_obj.param, sysex_obj.value = ['rx_tonenum', mem_data]
				if mem_address[2] == 2: sysex_obj.param, sysex_obj.value = ['rx_channel', firstval]
				if mem_address[2] == 3: sysex_obj.param, sysex_obj.value = ['rx_pitchbend', firstval]
				if mem_address[2] == 4: sysex_obj.param, sysex_obj.value = ['rx_ch_pressure', firstval]
				if mem_address[2] == 5: sysex_obj.param, sysex_obj.value = ['rx_program_change', firstval]
				if mem_address[2] == 6: sysex_obj.param, sysex_obj.value = ['rx_control_change', firstval]
				if mem_address[2] == 7: sysex_obj.param, sysex_obj.value = ['rx_poly_pressure', firstval]
				if mem_address[2] == 8: sysex_obj.param, sysex_obj.value = ['rx_note_message', firstval]
				if mem_address[2] == 9: sysex_obj.param, sysex_obj.value = ['rx_rpn', firstval]
				if mem_address[2] == 10: sysex_obj.param, sysex_obj.value = ['rx_nrpn', firstval]
				if mem_address[2] == 11: sysex_obj.param, sysex_obj.value = ['rx_modulation', firstval]
				if mem_address[2] == 12: sysex_obj.param, sysex_obj.value = ['rx_volume', firstval]
				if mem_address[2] == 13: sysex_obj.param, sysex_obj.value = ['rx_panpot', firstval]
				if mem_address[2] == 14: sysex_obj.param, sysex_obj.value = ['rx_expression', firstval]
				if mem_address[2] == 15: sysex_obj.param, sysex_obj.value = ['rx_hold1', firstval]
				if mem_address[2] == 16: sysex_obj.param, sysex_obj.value = ['rx_portamento', firstval]
				if mem_address[2] == 17: sysex_obj.param, sysex_obj.value = ['rx_sostenuto', firstval]
				if mem_address[2] == 18: sysex_obj.param, sysex_obj.value = ['rx_soft', firstval]
				if mem_address[2] == 19: sysex_obj.param, sysex_obj.value = ['mono_poly', firstval]
				if mem_address[2] == 20: sysex_obj.param, sysex_obj.value = ['assign', firstval]
				if mem_address[2] == 21: sysex_obj.param, sysex_obj.value = ['use_rhythm', firstval]

				if mem_address[2] == 22: sysex_obj.param, sysex_obj.value = ['pitch_key_shift', firstval]
				if mem_address[2] == 23: sysex_obj.param, sysex_obj.value = ['pitch_offset_fine', mem_data]

				if mem_address[2] == 25: sysex_obj.param, sysex_obj.value = ['part_level', firstval]
				if mem_address[2] == 26: sysex_obj.param, sysex_obj.value = ['vel_sense_depth', firstval]
				if mem_address[2] == 27: sysex_obj.param, sysex_obj.value = ['vel_sense_offset', firstval]
				if mem_address[2] == 28: sysex_obj.param, sysex_obj.value = ['part_panpot', firstval]
				if mem_address[2] == 29: sysex_obj.param, sysex_obj.value = ['kbd_range_low', firstval]
				if mem_address[2] == 30: sysex_obj.param, sysex_obj.value = ['kbd_range_hi', firstval]
				if mem_address[2] == 31: sysex_obj.param, sysex_obj.value = ['cc1_cont_num', firstval]
				if mem_address[2] == 32: sysex_obj.param, sysex_obj.value = ['cc2_cont_num', firstval]

				if mem_address[2] == 33: sysex_obj.param, sysex_obj.value = ['chorus_send', firstval]
				if mem_address[2] == 34: sysex_obj.param, sysex_obj.value = ['reverb_send', firstval]
				if mem_address[2] == 35: sysex_obj.param, sysex_obj.value = ['rx_bank', firstval]
				if mem_address[2] == 36: sysex_obj.param, sysex_obj.value = ['rx_bank_lsb', firstval]
				if mem_address[2] == 42: sysex_obj.param, sysex_obj.value = ['pitch_fine_tune', firstval]
				if mem_address[2] == 44: sysex_obj.param, sysex_obj.value = ['delay_send_level', firstval]

				if subnum[0] == 3: sysex_obj.param, sysex_obj.value = ['tone_modify_'+str(subnum[1]), firstval]
				if mem_address[2] == 64: sysex_obj.param, sysex_obj.value = ['scale_tuning', list(mem_data[0:12])]

			if bytesplit[0] == 2:
				subnum = data_bytes.splitbyte(mem_address[2])
				lfo_name = 'unknown'
				if subnum[0] == 0: lfo_name = 'mod'
				if subnum[0] == 1: lfo_name = 'bend'
				if subnum[0] == 2: lfo_name = 'caf'
				if subnum[0] == 3: lfo_name = 'paf'
				if subnum[0] == 4: lfo_name = 'cc1'
				if subnum[0] == 5: lfo_name = 'cc2'

				sysex_obj.group = 'block_lfo'
				sysex_obj.subgroup = bytesplit[1]
				if subnum[1] == 0: sysex_obj.param, sysex_obj.value = [lfo_name+'_pitch_ctrl', firstval]
				if subnum[1] == 1: sysex_obj.param, sysex_obj.value = [lfo_name+'_tvf_cutoff_ctrl', firstval]
				if subnum[1] == 2: sysex_obj.param, sysex_obj.value = [lfo_name+'_amp_ctrl', firstval]
				if subnum[1] == 3: sysex_obj.param, sysex_obj.value = [lfo_name+'_lfo1_rate', firstval]
				if subnum[1] == 4: sysex_obj.param, sysex_obj.value = [lfo_name+'_lfo1_pitch', firstval]
				if subnum[1] == 5: sysex_obj.param, sysex_obj.value = [lfo_name+'_lfo1_tvf', firstval]
				if subnum[1] == 6: sysex_obj.param, sysex_obj.value = [lfo_name+'_lfo1_tva', firstval]
				if subnum[1] == 7: sysex_obj.param, sysex_obj.value = [lfo_name+'_lfo2_rate', firstval]
				if subnum[1] == 8: sysex_obj.param, sysex_obj.value = [lfo_name+'_lfo2_pitch', firstval]
				if subnum[1] == 9: sysex_obj.param, sysex_obj.value = [lfo_name+'_lfo2_tvf', firstval]
				if subnum[1] == 10: sysex_obj.param, sysex_obj.value = [lfo_name+'_lfo2_tva', firstval]

			if bytesplit[0] == 4:
				sysex_obj.group = 'block'
				sysex_obj.num = bytesplit[1]
				if mem_address[2] == 0: sysex_obj.param, sysex_obj.value = ['tone_map_num', firstval]
				if mem_address[2] == 1: sysex_obj.param, sysex_obj.value = ['tone_map_0_num', firstval]
				if mem_address[2] == 32: sysex_obj.param, sysex_obj.value = ['eq_on', firstval]
				if mem_address[2] == 33: sysex_obj.param, sysex_obj.value = ['output_assign', firstval]
				if mem_address[2] == 34: sysex_obj.param, sysex_obj.value = ['part_efx_assign', firstval]

		if mem_address[0] in [65, 81]: #0x41
			if mem_address[0] == 65: sysex_obj.category = 'drum_a'
			if mem_address[0] == 81: sysex_obj.category = 'drum_b'
			sysex_obj.group = bytesplit[0]
			sysex_obj.subgroup = mem_address[2]
			
			if bytesplit[1] != 0:
				sysex_obj.value = firstval
				if bytesplit[1] == 1: sysex_obj.param = 'pitch_coarse'
				elif bytesplit[1] == 2: sysex_obj.param = 'level'
				elif bytesplit[1] == 3: sysex_obj.param = 'assign_groupnum'
				elif bytesplit[1] == 4: sysex_obj.param = 'panpot'
				elif bytesplit[1] == 5: sysex_obj.param = 'reverb_send'
				elif bytesplit[1] == 6: sysex_obj.param = 'chorus_send'
				elif bytesplit[1] == 7: sysex_obj.param = 'rx_note_off'
				elif bytesplit[1] == 8: sysex_obj.param = 'rx_note_on'
				elif bytesplit[1] == 9: sysex_obj.param = 'delay_send'

		#if mem_address[0] in [72, 73]:
		#	isdatadump = True

	if sysex_obj.model_id == 69: #display
		sysex_obj.known = True
		sysex_obj.model_name = 'display'
		bytesplit = data_bytes.splitbyte(mem_address[1])
		if mem_address[0] == 16:
			sysex_obj.category = 'display'
			if mem_address[1] != 32:
				if bytesplit[1] != 0: 
					sysex_obj.group = 'bitmap'
					sysex_obj.param, sysex_obj.value = [bytesplit[1], mem_data]
				else: 
					sysex_obj.group = 'text'
					sysex_obj.param, sysex_obj.value = ['text', mem_data]
			else: 
				if mem_address[2] == 0: 
					sysex_obj.group = 'displaypage'
					sysex_obj.param, sysex_obj.value = ['num', firstval]
				if mem_address[2] == 1: 
					sysex_obj.group = 'time'
					sysex_obj.param, sysex_obj.value = ['sec', firstval/0.48]
