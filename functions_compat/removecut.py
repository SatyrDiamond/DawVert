# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import notelist_data

def do_placements(note_placements):
    for note_placement in note_placements:
        if 'cut' in note_placement: 
            cut_end = note_placement['duration']
            if note_placement['cut']['type'] == 'cut': 
                if 'start' in note_placement['cut']: cut_start = note_placement['cut']['start']
                cut_end += cut_start
                note_placement['notelist'] = notelist_data.trimmove(note_placement['notelist'], cut_start, cut_end)
                del note_placement['cut']

def process_r(projJ):
    if 'track_placements' in projJ:
        for track_placements_id in projJ['track_placements']:
            track_placements_data = projJ['track_placements'][track_placements_id]

            not_laned = True

            if 'laned' in track_placements_data:
                print('[compat] RemoveCut: laned: '+track_placements_id)
                if s_pldata['laned'] == 1:
                    not_laned = False
                    s_lanedata = s_pldata['lanedata']
                    s_laneordering = s_pldata['laneorder']
                    for t_lanedata in s_lanedata:
                        tj_lanedata = s_lanedata[t_lanedata]
                        if 'notes' in tj_lanedata:
                            do_placements(tj_lanedata['notes'])

            if not_laned == True:
                if 'notes' in track_placements_data:
                    print('[compat] RemoveCut: non-laned: '+track_placements_id)
                    do_placements(track_placements_data['notes'])
    return True


def process(cvpj_proj, cvpj_type, in__placement_cut, out__placement_cut):
    if in__placement_cut == True and out__placement_cut == False:
        if cvpj_type == 'r': return process_r(cvpj_proj)
        else: return False
    else: return False