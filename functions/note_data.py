# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def rx_makenote(t_pos, t_dur, t_key, t_vol, t_pan):
    note_data = {}
    note_data['position'] = t_pos
    if t_dur != None: note_data['duration'] = t_dur
    else: note_data['duration'] = 1
    note_data['key'] = t_key
    if t_pan != None: note_data['pan'] = t_pan
    if t_vol != None: note_data['vol'] = t_vol
    return note_data

def mx_makenote(t_inst, t_pos, t_dur, t_key, t_vol, t_pan):
    note_data = rx_makenote(t_pos, t_dur, t_key, t_vol, t_pan)
    note_data['instrument'] = t_inst
    return note_data

keytable_vals = [0,2,4,5,7,9,11] 
keytable = ['C','D','E','F','G','A','B']

def keynum_to_note(i_keynum, i_oct):
    return keytable_vals[i_keynum] + (i_oct)*12

def keyletter_to_note(i_keyletter, i_oct):
    return keytable_vals[keytable.index(i_keyletter)] + (i_oct)*12