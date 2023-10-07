# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import params

def group_add(cvpj_l, i_id, i_inside_group):
    data_values.nested_dict_add_value(cvpj_l, ['groups', i_id], {})
    if i_inside_group != None: 
        #print('[tracks] Adding Group: "'+i_id+'" inside "'+i_inside_group+'"')
        data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'parent_group'], i_inside_group)
        data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'audio_destination'], {'type': 'group', 'id': i_inside_group})
    else:
        #print('[tracks] Adding Group: "'+i_id+'"')
        data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'audio_destination'], {'type': 'master'})

def group_basicdata(cvpj_l, i_id, i_name, i_color, i_vol, i_pan):
    if i_name != None: data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'name'], i_name)
    if i_color != None: data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'color'], i_color)
    if i_vol != None: params.add(cvpj_l, ['groups', i_id], 'vol', i_vol, 'float')
    if i_pan != None: params.add(cvpj_l, ['groups', i_id], 'pan', i_pan, 'float')
