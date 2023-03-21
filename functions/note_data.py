# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def rx_makenote(t_pos, t_dur, t_key, t_vol, t_pan):
    note_data = {}
    note_data['position'] = t_pos
    note_data['duration'] = t_dur
    note_data['key'] = t_key
    if t_pan != None: note_data['pan'] = t_pan
    if t_vol != None: note_data['vol'] = t_vol
    return note_data

def mx_makenote(t_inst, t_pos, t_dur, t_key, t_vol, t_pan):
    note_data = rx_makenote(t_pos, t_dur, t_key, t_vol, t_pan)
    note_data['instrument'] = t_inst
    return note_data