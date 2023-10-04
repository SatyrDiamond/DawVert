# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import song_tracker
from functions import data_bytes

t_retg_alg = [['mul', 1], ['minus', 1], ['minus', 2], ['minus', 4], ['minus', 8], ['minus', 16], ['mul', 2/3], ['mul', 1/2], ['mul', 1], ['plus', 1], ['plus', 2], ['plus', 4], ['plus', 8], ['plus', 16], ['mul', 3/2], ['mul', 2]]

def do_fx(current_speed, trkd_global, trkd_param, fx_type, fx_value):

    if fx_type == 1:
        trkd_global['speed'] = fx_value
        current_speed = fx_value

    if fx_type == 2: 
        trkd_global['pattern_jump'] = fx_value

    if fx_type == 3:
        trkd_global['break_to_row'] = fx_value

    if fx_type == 4: 
        trkd_param['vol_slide'] = song_tracker.getfineval(fx_value)

    if fx_type == 5:
        trkd_param['slide_down_cont'] = song_tracker.calcbendpower_down(fx_value, current_speed)

    if fx_type == 6:
        trkd_param['slide_up_cont'] = song_tracker.calcbendpower_up(fx_value, current_speed)

    if fx_type == 7:
        trkd_param['slide_to_note'] = song_tracker.calcslidepower(fx_value, current_speed)

    if fx_type == 8: 
        vibrato_params = {}
        vibrato_params['speed'], vibrato_params['depth'] = data_bytes.splitbyte(fx_value)
        trkd_param['vibrato'] = vibrato_params
    
    if fx_type == 9: 
        tremor_params = {}
        tremor_params['ontime'], tremor_params['offtime'] = data_bytes.splitbyte(fx_value)
        trkd_param['tremor'] = tremor_params
    
    if fx_type == 10: 
        arp_params = [0,0]
        arp_params[0], arp_params[1] = data_bytes.splitbyte(fx_value)
        trkd_param['arp'] = arp_params
    
    if fx_type == 11: 
        trkd_param['vol_slide'] = song_tracker.getfineval(fx_value)
        trkd_param['vibrato'] = {'speed': 0, 'depth': 0}
    
    if fx_type == 12: 
        trkd_param['vol_slide'] = song_tracker.getfineval(fx_value)
        trkd_param['slide_to_note'] = song_tracker.getfineval(fx_value)

    if fx_type == 13: 
        trkd_param['channel_vol'] = fx_value/64

    if fx_type == 14: 
        trkd_param['channel_vol_slide'] = song_tracker.getfineval(fx_value)

    if fx_type == 15: 
        trkd_param['sample_offset'] = fx_value*256

    if fx_type == 16: 
        trkd_param['pan_slide'] = song_tracker.getfineval(fx_value)*-1

    if fx_type == 17: 
        retrigger_params = {}
        retrigger_alg, retrigger_params['speed'] = data_bytes.splitbyte(fx_value)
        retrigger_params['alg'], retrigger_params['val'] = t_retg_alg[retrigger_alg]
        trkd_param['retrigger'] = retrigger_params
    
    if fx_type == 18: 
        tremolo_params = {}
        tremolo_params['speed'], tremolo_params['depth'] = data_bytes.splitbyte(fx_value)
        trkd_param['tremolo'] = tremolo_params

    if fx_type == 19: 
        ext_type, ext_value = data_bytes.splitbyte(fx_value)
        if ext_type == 1: trkd_param['glissando_control'] = ext_value
        if ext_type == 3: trkd_param['vibrato_waveform'] = ext_value
        if ext_type == 4: trkd_param['tremolo_waveform'] = ext_value
        if ext_type == 5: trkd_param['panbrello_waveform'] = ext_value
        if ext_type == 6: trkd_param['fine_pattern_delay'] = ext_value
        if ext_type == 7: trkd_param['it_inst_control'] = ext_value
        if ext_type == 8: trkd_param['set_pan'] = ext_value/16
        if ext_type == 9: trkd_param['it_sound_control'] = ext_value
        if ext_type == 10: trkd_param['sample_offset_high'] = ext_value*65536
        if ext_type == 11: trkd_param['loop_start'] = ext_value
        if ext_type == 12: trkd_param['note_cut'] = ext_value
        if ext_type == 13: trkd_param['note_delay'] = ext_value
        if ext_type == 14: trkd_param['pattern_delay'] = ext_value
        if ext_type == 15: trkd_param['it_active_macro'] = ext_value

    if fx_type == 21: 
        fine_vib_sp, fine_vib_de = data_bytes.splitbyte(fx_value)
        vibrato_params = {}
        vibrato_params['speed'] = fine_vib_sp/15
        vibrato_params['depth'] = fine_vib_sp/15
        trkd_param['vibrato'] = vibrato_params

    if fx_type == 22: 
        trkd_global['global_volume'] = fx_value/64
                            
    if fx_type == 23: 
        trkd_global['global_volume_slide'] = song_tracker.getfineval(fx_value)

    if fx_type == 24: 
        trkd_param['set_pan'] = fx_value/255

    if fx_type == 25: 
        panbrello_params = {}
        panbrello_params['speed'], panbrello_params['depth'] = data_bytes.splitbyte(fx_value)
        trkd_param['panbrello'] = panbrello_params

    return current_speed