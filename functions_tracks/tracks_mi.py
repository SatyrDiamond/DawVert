# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_tracks import tracks_m
from functions import data_values
from functions import params

def inst_create(cvpj_l, instid):
    return tracks_m.inst_create(cvpj_l, instid)

def inst_visual(cvpj_l, instid, **kwargs):
    return tracks_m.inst_visual(cvpj_l, instid,  **kwargs)

def inst_pluginid(cvpj_l, instid, pluginid):
    return tracks_m.inst_pluginid(cvpj_l, instid, pluginid)

def inst_param_add(cvpj_l, trackid, p_id, p_value, p_type):
    return tracks_m.inst_param_add(cvpj_l, trackid, p_id, p_value, p_type)

def inst_param_get(cvpj_l, trackid, p_id, p_fallback):
    return tracks_m.inst_param_get(cvpj_l, trackid, p_id, p_fallback)

def inst_dataval_add(cvpj_l, trackid, datagroup, i_name, i_value):
    return tracks_m.inst_dataval_add(cvpj_l, trackid, datagroup, i_name, i_value)

def inst_dataval_get(cvpj_l, trackid, datagroup, i_name, i_fallback):
    return tracks_m.inst_dataval_get(cvpj_l, trackid, datagroup, i_name, i_fallback)

def inst_fxrackchan_add(cvpj_l, trackid, fxrack_channel):
    return tracks_m.inst_fxrackchan_add(cvpj_l, trackid, fxrack_channel)

def inst_fxrackchan_get(cvpj_l, trackid):
    return tracks_m.inst_fxrackchan_get(cvpj_l, trackid)




def playlist_add(cvpj_l, idnum):
    return tracks_m.playlist_add(cvpj_l, idnum)

def playlist_visual(cvpj_l, idnum, **kwargs):
    return tracks_m.playlist_visual(cvpj_l, idnum, **kwargs)

def add_pl(cvpj_l, idnum, pl_type, placements_data):
    return tracks_m.add_pl(cvpj_l, idnum, pl_type, placements_data)




def notelistindex_add(cvpj_l, patid, nle_notelist):
    data_values.nested_dict_add_value(cvpj_l, ['notelistindex', patid], {})
    playlist_nle = cvpj_l['notelistindex'][patid]
    playlist_nle['notelist'] = nle_notelist

def notelistindex_visual(cvpj_l, patid, **kwargs):
    playlist_nle = cvpj_l['notelistindex'][patid]
    if 'name' in kwargs: 
        if kwargs['name'] != None: playlist_nle['name'] = kwargs['name']
    if 'color' in kwargs: 
        if kwargs['color'] != None: playlist_nle['color'] = kwargs['color']