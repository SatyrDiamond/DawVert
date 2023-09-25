# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import tracks

def process_r(cvpj_l):
    new_trackdata = {}
    new_trackpl = {}
    new_trackordering = []
    for cvpj_trackid, s_trackdata, track_placements in tracks.r_track_iter(cvpj_l):
        tracktype = s_trackdata['type']
        trackauto = data_values.nested_dict_get_value(cvpj_l, ['automation', 'track', cvpj_trackid])
        if trackauto != None: del cvpj_l['automation']['track'][cvpj_trackid]
        if tracktype == 'hybrid':
            print('[unhybrid] '+cvpj_trackid+':', end=' ')
            for track_placement_type in track_placements:
                if track_placement_type == 'notes': 
                    print('Notes', end=' ')
                    split_cvpj_trackid = cvpj_trackid+'_unhybrid_notes'
                    new_trackdata[split_cvpj_trackid] = s_trackdata.copy()
                    new_trackdata[split_cvpj_trackid]['type'] = 'instrument'
                    new_trackpl[split_cvpj_trackid] = {}
                    if track_placement_type == 'notes': new_trackpl[split_cvpj_trackid]['notes'] = track_placements['notes']
                    new_trackordering.append(split_cvpj_trackid)
                    if trackauto != None: 
                        data_values.nested_dict_add_value(cvpj_l, ['automation', 'track', split_cvpj_trackid], trackauto)
                if track_placement_type == 'audio': 
                    print('Audio', end=' ')
                    split_cvpj_trackid = cvpj_trackid+'_unhybrid_audio'
                    new_trackdata[split_cvpj_trackid] = s_trackdata.copy()
                    new_trackdata[split_cvpj_trackid]['type'] = 'audio'
                    new_trackpl[split_cvpj_trackid] = {}
                    new_trackpl[split_cvpj_trackid]['audio'] = track_placements['audio']
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
    return cvpj_l
