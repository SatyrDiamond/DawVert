# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import params
from functions import placements

def r_getduration(projJ):
    trackplacements = projJ['track_placements'] if 'track_placements' in projJ else {}
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

def add_timesig_lengthbeat(cvpj_l, patternLength, notesPerBeat):
    timesig = placements.get_timesig(patternLength, notesPerBeat)
    cvpj_l['timesig'] = timesig
    return timesig

def add_timesig(cvpj_l, i_num, i_denom):
    cvpj_l['timesig'] = [i_num, i_denom]

def get_timesig(cvpj_l):
    return cvpj_l['timesig'] if 'timesig' in cvpj_l else [4,4]

def get_loopdata(cvpj_l, cvpj_type):
    if cvpj_type == 'r': loop_end = r_getduration(cvpj_l)-64
    if cvpj_type == 'm': loop_end = m_getduration(cvpj_l)-64

    loop_on, loop_start = False, 0
    if 'timemarkers' in cvpj_l:
        for timemarkdata in cvpj_l['timemarkers']:
            if 'type' in timemarkdata:
                if timemarkdata['type'] == 'loop': 
                    loop_start = timemarkdata['position']
                    loop_on = True
                    break
                if timemarkdata['type'] == 'loop_area': 
                    loop_start = timemarkdata['position']
                    loop_end = timemarkdata['end']
                    loop_on = True
                    break
    return loop_on, loop_start, loop_end

def add_info(cvpj_l, i_type, i_value):
    data_values.nested_dict_add_value(cvpj_l, ['info', i_type], i_value)

def add_info_msg(cvpj_l, i_datatype, i_value):
    data_values.nested_dict_add_value(cvpj_l, ['info', 'message'], {'type': i_datatype, 'text': i_value})

def add_param(cvpj_l, p_id, p_value, **kwargs):
    params.add(cvpj_l, [], p_id, p_value, 'float', **kwargs)