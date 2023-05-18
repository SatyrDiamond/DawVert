# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import notelist_data

def makepl_n(t_pos, t_dur, t_notelist):
    pl_data = {}
    pl_data['position'] = t_pos
    pl_data['duration'] = t_dur
    pl_data['notelist'] = t_notelist
    return pl_data

def makepl_n_mi(t_pos, t_dur, t_fromindex):
    pl_data = {}
    pl_data['position'] = t_pos
    pl_data['duration'] = t_dur
    pl_data['fromindex'] = t_fromindex
    return pl_data

def nl2pl(cvpj_notelist):
    return [{'position': 0, 'duration': notelist_data.getduration(cvpj_notelist), 'notelist': cvpj_notelist}]

def time_from_steps(i_dict, i_name, i_stretched, i_value, i_bpm, i_rate):
    in_bpm = 120
    in_stretch = 1

    if i_bpm != None: in_bpm = i_bpm
    if i_rate != None: in_stretch = i_rate
    tempomul = (120/in_bpm)

    if i_stretched == False:
        i_dict[i_name+'_nonstretch'] = i_value
        i_dict[i_name] = i_value*i_rate
        i_dict[i_name+'_real_nonstretch'] = (i_value/8)*tempomul
        i_dict[i_name+'_real'] = ((i_value/8)*tempomul)/i_rate
    else:
        i_dict[i_name+'_nonstretch'] = i_value/i_rate
        i_dict[i_name] = i_value
        i_dict[i_name+'_real_nonstretch'] = ((i_value*tempomul)/8)/i_rate
        i_dict[i_name+'_real'] = (((i_value*tempomul)/8)/i_rate)/i_rate

def time_from_seconds(i_dict, i_name, i_stretched, i_value, i_bpm, i_rate):
    in_bpm = 120
    in_stretch = 1

    if i_bpm != None: in_bpm = i_bpm
    if i_rate != None: in_stretch = i_rate

    str_i_value = i_value/(120/in_bpm)

    if i_stretched == False:
        i_dict[i_name+'_nonstretch'] = str_i_value*8
        i_dict[i_name] = (str_i_value*8)*i_rate
        i_dict[i_name+'_real_nonstretch'] = i_value
        i_dict[i_name+'_real'] = i_value/i_rate
    else:
        i_dict[i_name+'_nonstretch'] = (str_i_value*i_rate)*8
        i_dict[i_name] = ((str_i_value*i_rate)*8)*i_rate
        i_dict[i_name+'_real_nonstretch'] = i_value*i_rate
        i_dict[i_name+'_real'] = i_value