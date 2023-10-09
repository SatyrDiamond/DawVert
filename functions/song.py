# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import params

def r_getduration(projJ):
    trackplacements = projJ['track_placements']
    songduration = 0
    for trackid in trackplacements:
        islaned = False
        if 'laned' in trackplacements[trackid]:
            if trackplacements[trackid]['laned'] == 1:
                islaned = True
        if islaned == False:
            if 'notes' in trackplacements[trackid]:
                for placement in trackplacements[trackid]['notes']:
                    p_pos = placement['position']
                    p_dur = placement['duration']
                    if songduration < p_pos+p_dur:
                        songduration = p_pos+p_dur
        else:
            if 'lanedata' in trackplacements[trackid]:
                for s_lanedata in trackplacements[trackid]['lanedata']:
                    placementdata = trackplacements[trackid]['lanedata'][s_lanedata]['notes']
                    for placement in placementdata:
                        p_pos = placement['position']
                        p_dur = placement['duration']
                        if songduration < p_pos+p_dur:
                            songduration = p_pos+p_dur
    return songduration + 64

def m_getduration(projJ):
    playlistdata = projJ['playlist']
    songduration = 0
    for plnum in playlistdata:
        for placement_type in ['placements_notes', 'placements_audio']:
            if placement_type in playlistdata[plnum]:
                for placement in playlistdata[plnum][placement_type]:
                    p_pos = placement['position']
                    p_dur = placement['duration']
                    if songduration < p_pos+p_dur: songduration = p_pos+p_dur
    return songduration + 64

def get_lower_tempo(i_tempo, i_notelen, maxtempo):
    while i_tempo > maxtempo:
        i_tempo = i_tempo/2
        i_notelen = i_notelen/2
    return (i_tempo, i_notelen)

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------ Time Markers ----------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

def add_timemarker_text(cvpj_l, i_position, i_name):
    if 'timemarkers' not in cvpj_l: cvpj_l['timemarkers'] = []
    cvpj_l['timemarkers'].append({'position':i_position, 'name': i_name})

def add_timemarker_loop(cvpj_l, i_position, i_name):
    if 'timemarkers' not in cvpj_l: cvpj_l['timemarkers'] = []
    cvpj_l['timemarkers'].append({'position':i_position, 'name': i_name, 'type': 'loop'})

def add_timemarker_looparea(cvpj_l, i_name, i_start, i_end):
    if 'timemarkers' not in cvpj_l: cvpj_l['timemarkers'] = []
    timemarker_data = {'position': i_start, 'end': i_end, 'type': 'loop_area'}
    if i_name == None: timemarker_data['name'] = 'Loop'
    else: timemarker_data['name'] = i_name
    cvpj_l['timemarkers'].append(timemarker_data)

def add_timemarker_timesig(cvpj_l, i_name, i_position, i_numerator, i_denominator):
    if 'timemarkers' not in cvpj_l: cvpj_l['timemarkers'] = []
    timemarker_data = {'position': i_position, 'numerator': i_numerator, 'denominator': i_denominator, 'type': 'timesig'}
    if i_name != None: timemarker_data['name'] = i_name
    cvpj_l['timemarkers'].append(timemarker_data)

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------- Song Meta -----------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

def add_info(cvpj_l, i_type, i_value):
    data_values.nested_dict_add_value(cvpj_l, ['info', i_type], i_value)

def add_info_msg(cvpj_l, i_datatype, i_value):
    data_values.nested_dict_add_value(cvpj_l, ['info', 'message'], {'type': i_datatype, 'text': i_value})

def add_param(cvpj_l, p_id, p_value, **kwargs):
    params.add(cvpj_l, [], p_id, p_value, 'float', **kwargs)