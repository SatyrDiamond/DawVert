# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath

def do_placements(cvpj_placements, isaudio, out__placement_loop):
    new_placements = []
    for cvpj_placement in cvpj_placements:

        if 'cut' in cvpj_placement: 
            cuttype = cvpj_placement['cut']['type']
            if cuttype in ['loop', 'loop_off', 'loop_adv'] and cuttype not in out__placement_loop: 
                cvpj_placement_base = cvpj_placement.copy()
                cvpj_placement_cut = cvpj_placement['cut']
                del cvpj_placement_base['cut']
                del cvpj_placement_base['position']
                del cvpj_placement_base['duration']
                loop_base_position = cvpj_placement['position']
                loop_base_duration = cvpj_placement['duration']

                loop_start = 0
                loop_loopstart = 0
                loop_loopend = loop_base_duration
                if 'start' in cvpj_placement_cut: loop_start = cvpj_placement_cut['start']
                if 'loopstart' in cvpj_placement_cut: loop_loopstart = cvpj_placement_cut['loopstart']
                if 'loopend' in cvpj_placement_cut: loop_loopend = cvpj_placement_cut['loopend']

                cutpoints = xtramath.cutloop(loop_base_position, loop_base_duration, loop_start, loop_loopstart, loop_loopend)

                #print(cutpoints)
                for cutpoint in cutpoints:
                    cvpj_placement_cutted = cvpj_placement_base.copy()
                    cvpj_placement_cutted['position'] = cutpoint[0]
                    cvpj_placement_cutted['duration'] = cutpoint[1]
                    cvpj_placement_cutted['cut'] = {}
                    cvpj_placement_cutted['cut']['type'] = 'cut'
                    cvpj_placement_cutted['cut']['start'] = cutpoint[2]
                    cvpj_placement_cutted['cut']['end'] = cutpoint[3]
                    new_placements.append(cvpj_placement_cutted)
            else: new_placements.append(cvpj_placement)
        else: new_placements.append(cvpj_placement)
    return new_placements

def process_r(projJ, out__placement_loop):
    if 'track_placements' in projJ:
        for track_placements_id in projJ['track_placements']:
            track_placements_data = projJ['track_placements'][track_placements_id]

            not_laned = True

            if 'laned' in track_placements_data:
                print('[compat] RemoveLoops: laned: '+track_placements_id)
                if s_pldata['laned'] == 1:
                    not_laned = False
                    s_lanedata = s_pldata['lanedata']
                    s_laneordering = s_pldata['laneorder']
                    for t_lanedata in s_lanedata:
                        tj_lanedata = s_lanedata[t_lanedata]
                        if 'notes' in tj_lanedata:
                            track_placements_data['notes'] = do_placements(tj_lanedata['notes'], False, out__placement_loop)
                        if 'audio' in tj_lanedata:
                            track_placements_data['audio'] = do_placements(tj_lanedata['audio'], True, out__placement_loop)

            if not_laned == True:
                print('[compat] RemoveLoops: non-laned: '+track_placements_id)
                if 'notes' in track_placements_data:
                    track_placements_data['notes'] = do_placements(track_placements_data['notes'], False, out__placement_loop)
                if 'audio' in track_placements_data:
                    track_placements_data['audio'] = do_placements(track_placements_data['audio'], True, out__placement_loop)

def process_m(projJ, out__placement_loop):
    for playlist_id in projJ['playlist']:
        playlist_id_data = projJ['playlist'][playlist_id]
        if 'placements_notes' in playlist_id_data:
            playlist_id_data['placements_notes'] = do_placements(playlist_id_data['placements_notes'], False, out__placement_loop)
