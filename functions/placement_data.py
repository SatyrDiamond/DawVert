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

def time_mus(i_dict, i_name, i_type, i_value, i_bpm, i_rate):
    in_bpm = 120
    in_stretch = 1

    if i_bpm != None: in_bpm = i_bpm
    if i_rate != None: in_stretch = i_rate
    
    if i_type == 'beats':
        i_dict[i_name] = i_value*4
        i_dict[i_name+'_real'] = (i_value/2)*(120/in_bpm)
        i_dict[i_name+'_real_stretch'] = ((i_value/2)*(120/in_bpm))/i_rate
    if i_type == 'steps':
        i_dict[i_name] = i_value
        i_dict[i_name+'_real'] = (i_value/8)*(120/in_bpm)
        i_dict[i_name+'_real_stretch'] = ((i_value/8)*(120/in_bpm))/i_rate


#(120/in_bpm)

def time_sec(i_dict, i_name, i_type, i_value, i_bpm, i_rate):
    in_bpm = 120
    in_stretch = 1

    if i_bpm != None: in_bpm = i_bpm
    if i_rate != None: in_stretch = i_rate

    str_i_value = i_value/(120/in_bpm)

    if i_type == 'sec':
        i_dict[i_name] = str_i_value*8
        i_dict[i_name+'_real'] = i_value
        i_dict[i_name+'_real_stretch'] = i_value/i_rate

    if i_type == 'sec_stretch':
        i_dict[i_name] = (str_i_value*i_rate)*8
        i_dict[i_name+'_real'] = i_value*i_rate
        i_dict[i_name+'_real_stretch'] = i_value