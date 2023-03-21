# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def get_lower_tempo(i_tempo, i_notelen, maxtempo):
    while i_tempo > maxtempo:
        i_tempo = i_tempo/2
        i_notelen = i_notelen/2
    return (i_tempo, i_notelen)

def add_timemarker_text(cvpj_l, i_position, i_name):
    if 'timemarkers' not in cvpj_l: cvpj_l['timemarkers'] = []
    cvpj_l['timemarkers'].append({'position':i_position, 'name': i_name})

def add_timemarker_looparea(cvpj_l, i_name, i_start, i_end):
    if 'timemarkers' not in cvpj_l: cvpj_l['timemarkers'] = []
    if i_name == None: cvpj_l['timemarkers'].append({'name': 'Loop', 'position': i_start, 'end': i_end, 'type': 'loop_area'})
    else: cvpj_l['timemarkers'].append({'name': i_name, 'position': i_start, 'end': i_end, 'type': 'loop_area'})