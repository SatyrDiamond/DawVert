# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values

def process_r(convproj_obj):
    org_track_data = convproj_obj.track_data
    org_track_order = convproj_obj.track_order

    convproj_obj.track_order = []
    convproj_obj.track_data = {}

    for trackid in org_track_order:
        if trackid in org_track_data:
            track_obj = org_track_data[trackid]

            if_audio = len(track_obj.placements.data_audio) != 0
            if_notes = len(track_obj.placements.data_notes) != 0

            if track_obj.type == 'hybrid':
                a_track_obj = track_obj.make_base()
                n_track_obj = track_obj.make_base()

                n_track_obj.placements.data_notes = track_obj.placements.data_notes
                a_track_obj.placements.data_audio = track_obj.placements.data_audio

                if if_notes:
                    trackid_s = trackid+'_unhybrid_notes'
                    n_track_obj.type = 'instrument'
                    convproj_obj.track_order.append(trackid_s)
                    convproj_obj.track_data[trackid_s] = n_track_obj
                if if_audio:
                    trackid_s = trackid+'_unhybrid_audio'
                    a_track_obj.type = 'audio'
                    convproj_obj.track_order.append(trackid_s)
                    convproj_obj.track_data[trackid_s] = a_track_obj

    return True

def process(convproj_obj, in__track_hybrid, out__track_hybrid):
    if in__track_hybrid == True and out__track_hybrid == False:
        if convproj_obj.type in ['r', 'ri', 'rm']: return process_r(convproj_obj)
        else: return False
    else: return False