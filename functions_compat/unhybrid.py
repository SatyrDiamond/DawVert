# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions_tracks import tracks_r

def process_r(cvpj_l):
    new_trackdata = {}
    new_trackpl = {}
    new_trackordering = []
    for cvpj_trackid, s_trackdata, track_placements in tracks_r.iter(cvpj_l):
        tracktype = s_trackdata['type']
        trackauto = data_values.nested_dict_get_value(cvpj_l, ['automation', 'track', cvpj_trackid])
        if trackauto != None: del cvpj_l['automation']['track'][cvpj_trackid]
        if tracktype == 'hybrid':
            print('[unhybrid] '+cvpj_trackid+':', end=' ')
            for track_placement_type in track_placements:
                split_cvpj_trackid = cvpj_trackid+'_unhybrid_'+track_placement_type
                new_trackdata[split_cvpj_trackid] = s_trackdata.copy()
                if track_placement_type == 'notes': 
                    new_trackdata[split_cvpj_trackid]['type'] = 'instrument'
                    print('Notes', end=' ')
                if track_placement_type == 'audio': 
                    new_trackdata[split_cvpj_trackid]['type'] = 'audio'
                    print('Audio', end=' ')
                new_trackpl[split_cvpj_trackid] = {}
                new_trackpl[split_cvpj_trackid][track_placement_type] = track_placements[track_placement_type]
                new_trackordering.append(split_cvpj_trackid)
                if trackauto != None: 
                    data_values.nested_dict_add_value(cvpj_l, ['automation', 'track', split_cvpj_trackid], trackauto)
            print()
        else:
            new_trackdata[cvpj_trackid] = s_trackdata
            new_trackpl[cvpj_trackid] = track_placements
    cvpj_l['track_data'] = new_trackdata
    cvpj_l['track_placements'] = new_trackpl
    cvpj_l['track_order'] = new_trackordering
    return True

def process(cvpj_proj, cvpj_type, in__track_hybrid, out__track_hybrid):
    if in__track_hybrid == True and out__track_hybrid == False:
        if cvpj_type in ['r', 'ri', 'rm']: return process_r(cvpj_proj)
        else: return False
    else: return False