# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values

visname = {
    'bpm': 'Tempo',
    'vol': 'Volume',
    'pan': 'Pan',
    'solo': 'Solo',
    'enabled': 'On',
    'pitch': 'Pitch'
}

def add(cvpj_l, location, p_id, p_value, p_type, **kwargs):
    param_data = {}
    param_data['type'] = p_type

    if 'visname' not in kwargs:
        if p_id in visname: param_data['name'] = visname[p_id]
        else: param_data['name'] = p_id
    else: param_data['name'] = kwargs['visname']

    if p_type == 'float': param_data['value'] = float(p_value)
    if p_type == 'int': param_data['value'] = int(p_value)
    if p_type == 'bool': param_data['value'] = bool(p_value)
    if p_type == 'string': param_data['value'] = p_value

    paramsvalname = data_values.get_value(kwargs, 'groupname', 'params')
    data_values.nested_dict_add_value(cvpj_l, location+[paramsvalname, p_id], param_data)

def get(cvpj_l, location, p_id, fallbackval, **kwargs):
    paramsvalname = data_values.get_value(kwargs, 'groupname', 'params')
    paramdata = data_values.nested_dict_get_value(cvpj_l, location+[paramsvalname, p_id])
    if paramdata != None: return paramdata['value'], paramdata['type'], paramdata['name']
    return fallbackval, 'notfound', ''

def remove(cvpj_l, p_id):
    if 'params' in cvpj_l:
        if p_id in cvpj_l['params']:
            del cvpj_l['params'][p_id]