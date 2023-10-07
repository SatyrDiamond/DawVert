# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import params

def create(cvpj_l, i_vol):
    if 'track_master' not in cvpj_l: cvpj_l['track_master'] = {}
    cvpj_master = cvpj_l['track_master']
    if i_vol != None: params.add(cvpj_l, ['track_master'], 'vol', i_vol, 'float')

def visual(cvpj_l, **kwargs):
    cvpj_master = cvpj_l['track_master']
    if 'name' in kwargs: 
        if kwargs['name'] != None: cvpj_master['name'] = kwargs['name']
    if 'color' in kwargs: 
        if kwargs['color'] != None: cvpj_master['color'] = kwargs['color']

def param_add(cvpj_l, p_id, p_value, p_type):
    params.add(cvpj_l, ['track_master'], p_id, p_value, p_type)

def param_get(cvpj_l, trackid, p_id, p_fallback):
    return params.get(cvpj_l, ['track_master'], p_id, p_fallback)