# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import song_tracker
from functions import data_bytes

def do_fx(current_speed, trkd_global, trkd_param, fx_type, fx_value):

	if fx_type == 0 and fx_value != 0:
		arpeggio_first = fx_value >> 4
		arpeggio_second = fx_value & 0x0F
		trkd_param['arp'] = [arpeggio_first, arpeggio_second]

	if current_speed == None:
		if fx_type == 1: trkd_param['slide_up'] = fx_value
		if fx_type == 2: trkd_param['slide_down'] = fx_value
		if fx_type == 3: trkd_param['slide_to_note'] = fx_value
	else:
		if fx_type == 1: trkd_param['slide_up'] = song_tracker.calcbendpower_up(fx_value, current_speed)
		if fx_type == 2: trkd_param['slide_down'] = song_tracker.calcbendpower_down(fx_value, current_speed)
		if fx_type == 3: trkd_param['slide_to_note'] = song_tracker.calcslidepower(fx_value, current_speed)

	if fx_type == 4: 
		vibrato_params = {}
		vibrato_params['speed'], vibrato_params['depth'] = data_bytes.splitbyte(fx_value)
		trkd_param['vibrato'] = vibrato_params

	if fx_type == 5:
		pos, neg = data_bytes.splitbyte(fx_value)
		trkd_param['vol_slide'] = (neg*-1) + pos
		trkd_param['slide_to_note'] = (neg*-1) + pos

	if fx_type == 6:
		pos, neg = data_bytes.splitbyte(fx_value)
		trkd_param['vibrato'] = {'speed': 0, 'depth': 0}
		trkd_param['vol_slide'] = (neg*-1) + pos

	if fx_type == 7:
		tremolo_params = {}
		tremolo_params['speed'], tremolo_params['depth'] = data_bytes.splitbyte(fx_value)
		trkd_param['tremolo'] = tremolo_params

	if fx_type == 8: 
		trkd_param['pan'] = (fx_value-128)/128

	if fx_type == 9: 
		trkd_param['sample_offset'] = fx_value*256

	if fx_type == 10:
		pos, neg = data_bytes.splitbyte(fx_value)
		trkd_param['vol_slide'] = (neg*-1) + pos

	if fx_type == 14: 
		ext_type, ext_value = data_bytes.splitbyte(fx_value)
		if ext_type == 0: trkd_param['filter_amiga_led'] = ext_value
		if ext_type == 1: trkd_param['fine_slide_up'] = ext_value
		if ext_type == 2: trkd_param['fine_slide_down'] = ext_value
		if ext_type == 3: trkd_param['glissando_control'] = ext_value
		if ext_type == 4: trkd_param['vibrato_waveform'] = ext_value
		if ext_type == 5: trkd_param['set_finetune'] = ext_value
		if ext_type == 6: trkd_param['pattern_loop'] = ext_value
		if ext_type == 7: trkd_param['tremolo_waveform'] = ext_value
		if ext_type == 8: trkd_param['set_pan'] = ext_value
		if ext_type == 9: trkd_param['retrigger_note'] = ext_value
		if ext_type == 10: trkd_param['fine_vol_slide_up'] = ext_value
		if ext_type == 11: trkd_param['fine_vol_slide_down'] = ext_value
		if ext_type == 12: trkd_param['note_cut'] = ext_value
		if ext_type == 13: trkd_param['note_delay'] = ext_value
		if ext_type == 14: trkd_param['pattern_delay'] = ext_value
		if ext_type == 15: trkd_param['invert_loop'] = ext_value

	return current_speed