# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_tracks import tracks_r
from functions_tracks import tracks_m
from functions import data_values
from functions import params

def track_create(cvpj_l, trackid, tracktype):
    return tracks_r.track_create(cvpj_l, trackid, tracktype)

def track_visual(cvpj_l, trackid, **kwargs):
    return tracks_r.track_visual(cvpj_l, trackid, **kwargs)

def track_param_add(cvpj_l, trackid, p_id, p_value, p_type):
    return tracks_r.track_param_add(cvpj_l, trackid, p_id, p_value, p_type)

def track_param_get(cvpj_l, trackid, p_id, p_fallback):
    return tracks_r.track_param_get(cvpj_l, trackid, p_id, p_fallback)

def track_fxrackchan_add(cvpj_l, trackid, fxrack_channel):
    return tracks_r.track_param_get(cvpj_l, trackid, fxrack_channel)

def track_fxrackchan_get(cvpj_l, trackid):
    return tracks_r.track_param_get(cvpj_l, trackid)

def track_inst_pluginid(cvpj_l, trackid, pluginid):
    return tracks_r.track_inst_pluginid(cvpj_l, trackid, pluginid)

def track_dataval_add(cvpj_l, trackid, datagroup, i_name, i_value):
    return tracks_r.track_dataval_add(cvpj_l, trackid, datagroup, i_name, i_value)

def track_dataval_get(cvpj_l, trackid, datagroup, i_name, i_fallback):
    return tracks_r.track_dataval_get(cvpj_l, trackid, datagroup, i_name, i_fallback)

def add_pl(cvpj_l, trackid, pl_type, placements_data):
    return tracks_r.add_pl(cvpj_l, trackid, pl_type, placements_data)

def add_pl_laned(cvpj_l, trackid, pl_type, placements_data, lanename):
    return tracks_r.add_padd_pl_laned(cvpj_l, trackid, pl_type, placements_data, lanename)

def iter(cvpj_l):
    return tracks_r.iter(cvpj_l)



def inst_create(cvpj_l, instid):
    return tracks_m.inst_create(cvpj_l, instid)

def inst_visual(cvpj_l, instid, **kwargs):
    return tracks_m.inst_visual(cvpj_l, instid, **kwargs)

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
