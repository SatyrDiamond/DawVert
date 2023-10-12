# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import params

def track_create(cvpj_l, trackid, tracktype):
    if 'track_data' not in cvpj_l: cvpj_l['track_data'] = {}
    if 'track_order' not in cvpj_l: cvpj_l['track_order'] = []
    cvpj_track = {}
    cvpj_track['type'] = tracktype
    cvpj_l['track_data'][trackid] = cvpj_track
    cvpj_l['track_order'].append(trackid)

def track_visual(cvpj_l, trackid, **kwargs):
    cvpj_track = cvpj_l['track_data'][trackid]
    if 'name' in kwargs: 
        if kwargs['name'] != None: cvpj_track['name'] = kwargs['name']
    if 'color' in kwargs: 
        if kwargs['color'] != None: cvpj_track['color'] = kwargs['color']

def track_param_add(cvpj_l, trackid, p_id, p_value, p_type):
    if p_value != None: params.add(cvpj_l, ['track_data', trackid], p_id, p_value, p_type)

def track_param_get(cvpj_l, trackid, p_id, p_fallback):
    return params.get(cvpj_l, ['track_data', trackid], p_id, p_fallback)

def track_fxrackchan_add(cvpj_l, trackid, fxrack_channel):
    data_values.nested_dict_add_value(cvpj_l, ['track_data', trackid, 'fxrack_channel'], fxrack_channel)

def track_fxrackchan_get(cvpj_l, trackid):
    value = data_values.nested_dict_get_value(cvpj_l, ['track_data', trackid, 'fxrack_channel'])
    return value if value != None else 0

def track_inst_pluginid(cvpj_l, trackid, pluginid):
    data_values.nested_dict_add_value(cvpj_l, ['track_data', trackid, 'instdata', 'pluginid'], pluginid)

def track_dataval_add(cvpj_l, trackid, datagroup, i_name, i_value):
    if datagroup == None: datagroup = 'data'
    data_values.nested_dict_add_value(cvpj_l, ['track_data', trackid, datagroup, i_name], i_value)

def track_dataval_get(cvpj_l, trackid, datagroup, i_name, i_fallback):
    if datagroup == None: datagroup = 'data'
    value = data_values.nested_dict_get_value(cvpj_l, ['track_data', trackid, datagroup, i_name])
    return value

def track_group(cvpj_l, trackid, groupid):
    data_values.nested_dict_add_value(cvpj_l, ['track_data', trackid, 'group'], groupid)

def add_pl(cvpj_l, trackid, pl_type, placements_data):
    data_values.nested_dict_add_to_list(cvpj_l, ['track_placements', trackid, pl_type], placements_data)

def add_pl_laned(cvpj_l, trackid, pl_type, placements_data, lanename):
    data_values.nested_dict_add_value(cvpj_l, ['track_placements', trackid, 'laned'], 1)
    data_values.nested_dict_add_to_list(cvpj_l, ['track_placements', trackid, 'lanedata', lanename, pl_type], placements_data)
    data_values.nested_dict_add_to_list(cvpj_l, ['track_placements', trackid, 'laneorder'], lanename)

def iter(cvpj_l):
    cvpj_track_placements = cvpj_l['track_placements'] if 'track_placements' in cvpj_l else {}
    cvpj_track_order = cvpj_l['track_order'] if 'track_order' in cvpj_l else []
    cvpj_track_data = cvpj_l['track_data'] if 'track_data' in cvpj_l else {}
    for trackid in cvpj_track_order:
        track_placements = cvpj_track_placements[trackid] if trackid in cvpj_track_placements else {}
        track_data = cvpj_track_data[trackid] if trackid in cvpj_track_data else {}
        yield trackid, track_data, track_placements