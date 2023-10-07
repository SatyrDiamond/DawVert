# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import params

def add(cvpj_l, fx_num, fx_vol, fx_pan, **kwargs):
    data_values.nested_dict_add_value(cvpj_l, ['fxrack', str(fx_num)], {})
    fxdata = cvpj_l['fxrack'][str(fx_num)]
    if 'name' in kwargs: 
        if kwargs['name'] != None: fxdata['name'] = kwargs['name']
    if 'color' in kwargs: 
        if kwargs['color'] != None: fxdata['color'] = kwargs['color']

    if fx_vol != None: params.add(fxdata, [], 'vol', fx_vol, 'float')
    if fx_pan != None: params.add(fxdata, [], 'pan', fx_pan, 'float')

def param_add(cvpj_l, fx_num, p_id, p_value, p_type):
    data_values.nested_dict_add_value(cvpj_l, ['fxrack', str(fx_num)], {})
    params.add(cvpj_l, ['fxrack',str(fx_num)], p_id, p_value, p_type)

def param_get(cvpj_l, fx_num, p_id, p_fallback):
    return params.get(cvpj_l, ['fxrack',str(fx_num)], p_id, p_fallback)

def addsend(cvpj_l, fx_num, fx_to_num, fx_amount, fx_sendautoid):
    senddata = {"amount": fx_amount, "channel": fx_to_num}
    if fx_sendautoid != None: senddata['sendautoid'] = fx_sendautoid
    data_values.nested_dict_add_to_list(cvpj_l, ['fxrack', str(fx_num), 'sends'], senddata)
