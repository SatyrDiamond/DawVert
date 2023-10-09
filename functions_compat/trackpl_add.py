# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_compat import timesigblocks
from functions_compat import split_single_notelist

def process_r(projJ):
    timesigposs, tsblocks = timesigblocks.create_points_cut(projJ)
    split_single_notelist.add_timesigblocks(tsblocks)

    if 'do_singlenotelistcut' in projJ:
        if projJ['do_singlenotelistcut'] == True:
            track_placements = projJ['track_placements']
            for trackid in track_placements:
                islaned = track_placements[trackid]['laned'] if 'laned' in track_placements[trackid] else 0

                if islaned == 0:
                    if 'notes' in track_placements[trackid]:
                        placementdata = track_placements[trackid]['notes']
                        if len(placementdata) == 1:
                            split_single_notelist.add_notelist([False, trackid], placementdata[0]['notelist'])
                else:
                    for s_lanedata in track_placements[trackid]['lanedata']:
                        placementdata = track_placements[trackid]['lanedata'][s_lanedata]['notes']
                        if len(placementdata) == 1:
                            split_single_notelist.add_notelist([True, trackid, s_lanedata], placementdata[0]['notelist'])

    for inid, out_placements in split_single_notelist.get_notelist():
        if inid[0] == False: track_placements[inid[1]]['notes'] = out_placements
        if inid[0] == True: track_placements[inid[1]]['lanedata'][inid[2]]['notes'] = out_placements

    projJ['do_singlenotelistcut'] = False
    return True

def process_m(projJ):
    timesigposs, tsblocks = timesigblocks.create_points_cut(projJ)
    split_single_notelist.add_timesigblocks(tsblocks)

    if 'do_singlenotelistcut' in projJ:
        if projJ['do_singlenotelistcut'] == True:
            track_playlist = projJ['playlist']
            for plnum in track_playlist:
                if 'placements_notes' in track_playlist[plnum]:
                    placementdata = track_playlist[plnum]['placements_notes']
                    if len(placementdata) == 1:
                        split_single_notelist.add_notelist([False, trackid], placementdata[0]['notelist'])

    projJ['do_singlenotelistcut'] = False
    return True



def process(cvpj_proj, cvpj_type, in__track_nopl, out__track_nopl):
    if in__track_nopl == True and out__track_nopl == False:
        if cvpj_type in ['r']: return process_r(cvpj_proj)
        elif cvpj_type in ['m']: return process_m(cvpj_proj)
        else: return False
    else: return False