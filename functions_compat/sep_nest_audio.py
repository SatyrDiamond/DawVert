# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from functions import placement_data

def do_placements(cvpj_placements, out__placement_loop):
    new_placements = []
    for cvpj_placement in cvpj_placements:
        main_pos = cvpj_placement['position']
        main_dur = cvpj_placement['duration']
        main_cut = cvpj_placement['cut'] if 'cut' in cvpj_placement else None
        main_fxrack_channel = cvpj_placement['fxrack_channel'] if 'fxrack_channel' in cvpj_placement else None
        main_off = 0
        if main_cut != None: main_off = main_cut['start']
        main_events = cvpj_placement['events']
        trimpls = placement_data.audiotrim(main_events, main_pos-main_off,main_off, main_off+main_dur)
        for trimpl in trimpls:
            if main_fxrack_channel != None: trimpl['fxrack_channel'] = main_fxrack_channel
            new_placements.append(trimpl)

    return new_placements

def process_r(projJ, out__placement_loop):
    if 'track_placements' in projJ:
        for track_placements_id in projJ['track_placements']:
            track_placements_data = projJ['track_placements'][track_placements_id]

            not_laned = True

            if 'laned' in track_placements_data:
                if track_placements_data['laned'] == 1:
                    not_laned = False
                    s_lanedata = track_placements_data['lanedata']
                    s_laneordering = track_placements_data['laneorder']
                    for t_lanedata in s_lanedata:
                        tj_lanedata = s_lanedata[t_lanedata]
                        if 'audio_nested' in tj_lanedata:
                            tj_lanedata['audio'] = do_placements(tj_lanedata['audio_nested'], out__placement_loop)
                            del tj_lanedata['audio_nested']

            if not_laned == True:
                if 'audio_nested' in track_placements_data:
                    track_placements_data['audio'] = do_placements(track_placements_data['audio_nested'], out__placement_loop)
                    del track_placements_data['audio_nested']
    return True

def process(projJ, cvpj_type, in__placement_loop, out__placement_loop):
    if cvpj_type in ['r', 'ri', 'rm']: return process_r(projJ, out__placement_loop)
    else: return False