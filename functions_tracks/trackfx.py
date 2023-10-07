# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import params

def get_sendcvpjlocation(sendloc):
    out_location = None
    if sendloc[0] == 'master': out_location = ['track_master', 'returns']
    if sendloc[0] == 'group': out_location = ['groups', sendloc[1], 'returns']
    return out_location

def return_add(cvpj_l, i_location, i_returnname):
    out_location = get_sendcvpjlocation(i_location)
    print('[tracks] Adding Return: "'+i_returnname+'" in '+'/'.join(out_location))
    data_values.nested_dict_add_value(cvpj_l, out_location+[i_returnname], {})

def return_param_add(cvpj_l, i_location, i_returnname, p_id, p_value, p_type):
    out_location = get_sendcvpjlocation(i_location)
    if p_value != None: params.add(cvpj_l, out_location+[i_returnname], p_id, p_value, p_type)

def return_param_get(cvpj_l, i_location, i_returnname, p_id, p_fallback):
    out_location = get_sendcvpjlocation(i_location)
    return params.get(cvpj_l, out_location+[i_returnname], p_id, p_fallback)

def return_visual(cvpj_l, i_location, i_returnname, **kwargs):
    out_location = get_sendcvpjlocation(i_location)
    if 'name' in kwargs: 
        if kwargs['name'] != None: data_values.nested_dict_add_value(cvpj_l, out_location+[i_returnname, 'name'], kwargs['name'])
    if 'color' in kwargs: 
        if kwargs['color'] != None: data_values.nested_dict_add_value(cvpj_l, out_location+[i_returnname, 'color'], kwargs['color'])

def send_add(cvpj_l, i_trackid, i_sendname, i_amount, i_sendautoid):
    send_data = {'amount': i_amount, 'sendid': i_sendname}
    if i_sendautoid != None: send_data['sendautoid'] = i_sendautoid
    print('[tracks] Adding Send: "'+i_sendname+'"')
    data_values.nested_dict_add_to_list(cvpj_l, ['track_data', i_trackid, 'sends_audio'], send_data)

def group_add(cvpj_l, g_id, i_inside_group):
    data_values.nested_dict_add_value(cvpj_l, ['groups', g_id], {})
    if i_inside_group != None: 
        data_values.nested_dict_add_value(cvpj_l, ['groups', g_id, 'parent_group'], i_inside_group)
        data_values.nested_dict_add_value(cvpj_l, ['groups', g_id, 'audio_destination'], {'type': 'group', 'id': i_inside_group})
    else:
        data_values.nested_dict_add_value(cvpj_l, ['groups', g_id, 'audio_destination'], {'type': 'master'})

def group_visual(cvpj_l, g_id, **kwargs):
    out_location = get_sendcvpjlocation(i_location)
    if 'name' in kwargs: 
        if kwargs['name'] != None: data_values.nested_dict_add_value(cvpj_l, ['groups', g_id, 'name'], kwargs['name'])
    if 'color' in kwargs: 
        if kwargs['color'] != None: data_values.nested_dict_add_value(cvpj_l, ['groups', g_id, 'color'], kwargs['color'])

def group_param_add(cvpj_l, p_id, p_value, p_type):
    if p_value != None: params.add(cvpj_l, ['groups', g_id], p_id, p_value, p_type)

def group_param_get(cvpj_l, p_id, p_fallback):
    return params.get(cvpj_l, ['groups', g_id], p_id, p_fallback)