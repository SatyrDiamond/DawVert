# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

# [a]
#  /\
#   ⎸
#  \/
# [r] <--> [m] <--> [mi]
#  /\                /\
#   ⎸                 ⎸
#   ⎸                /
# [ri]--------------/

import json

def m2mi_checkdup(cvpj_notelistindex, nledata):
    for pattern in cvpj_notelistindex:
        patterndat = cvpj_notelistindex[pattern]
        if patterndat == nledata:
            return pattern
    else:
        return None

def m2mi(song):
    print('[song-convert] Converting from Multiple > MultipleIndexed')
    global cvpj_proj
    cvpj_proj = json.loads(song)
    cvpj_playlist = cvpj_proj['playlist']
    cvpj_notelistindex = {}
    pattern_number = 1
    for cvpj_playlistentry in cvpj_playlist:
        cvpj_playlistentry_data = cvpj_playlist[cvpj_playlistentry]
        cvpj_placements = cvpj_playlistentry_data['placements']
        for cvpj_placement in cvpj_placements:
            if cvpj_placement['type'] == 'instruments':
                cvpj_notelist = cvpj_placement['notelist']
                temp_nle = {}
                temp_nle['notelist'] = cvpj_notelist.copy()
                checksamenl = m2mi_checkdup(cvpj_notelistindex, temp_nle)
                if checksamenl != None:
                    cvpj_placement['fromindex'] = checksamenl
                else:
                    cvpj_notelistindex['m2mi_' + str(pattern_number)] = temp_nle
                    cvpj_placement['fromindex'] = 'm2mi_' + str(pattern_number)
                    del cvpj_placement['notelist']
                pattern_number += 1
    cvpj_proj['notelistindex'] = cvpj_notelistindex
    return json.dumps(cvpj_proj)

def r2m(song):
    print('[song-convert] Converting from Regular > Multiple')
    cvpj_proj = json.loads(song)
    if 'trackordering' not in cvpj_proj:
        print('[error] trackordering not found')

    t_s_trackordering = cvpj_proj['trackordering']
    t_s_trackdata = cvpj_proj['trackdata']
    del cvpj_proj['trackdata']
    del cvpj_proj['trackordering']

    cvpj_proj['instruments'] = {}
    cvpj_proj['instrumentsorder'] = []
    cvpj_proj['playlist'] = {}

    temp_num_playlist = 1
    for trackid in t_s_trackordering:
        if trackid in t_s_trackdata:
            singletrack_data = t_s_trackdata[trackid]
            singletrack_placements = singletrack_data['placements']
            del singletrack_data['placements']

            if singletrack_data['type'] == 'instrument':
                cvpj_proj['instrumentsorder'].append(trackid)
                cvpj_proj['playlist'][str(temp_num_playlist)] = {}
                playlistrow = cvpj_proj['playlist'][str(temp_num_playlist)]
                if 'name' in singletrack_data: playlistrow['name'] = singletrack_data['name']
                if 'color' in singletrack_data: playlistrow['color'] = singletrack_data['color']
                for singletrack_placement in singletrack_placements:
                    singletrack_placement['type'] = 'instruments'
                    if 'notelist' in singletrack_placement:
                        for t_note in singletrack_placement['notelist']:
                            t_note['instrument'] = trackid

                playlistrow['placements'] = singletrack_placements

                cvpj_proj['instruments'][trackid] = singletrack_data
            temp_num_playlist += 1
    return json.dumps(cvpj_proj)

def mi2m(song):
    cvpj_proj = json.loads(song)
    t_s_notelistindex = cvpj_proj['notelistindex']
    t_s_playlist = cvpj_proj['playlist']
    for pl_row in t_s_playlist:
        pl_row_data = t_s_playlist[pl_row]
        if 'placements' in pl_row_data:
            pl_row_placements = pl_row_data['placements']
            for pldata in pl_row_placements:
                if 'type' in pldata:
                    if pldata['type'] == 'instruments' and 'fromindex' in pldata:
                        fromindex = pldata['fromindex']
                        if fromindex in t_s_notelistindex:
                            index_pl_data = t_s_notelistindex[fromindex]
                            del pldata['fromindex']
                            if 'notelist' in index_pl_data:
                                pldata['notelist'] = index_pl_data['notelist']
                                if 'name' in index_pl_data: pldata['name'] = index_pl_data['name']
                                if 'color' in index_pl_data: pldata['color'] = index_pl_data['color']
    del cvpj_proj['notelistindex']
    return json.dumps(cvpj_proj)

def overlap(start1, end1, start2, end2):
    return max(max((end2-start1), 0) - max((end2-end1), 0) - max((start2-start1), 0), 0)

def m2r_split_insts(placement):
    del placement['type']
    out_inst_pl = {}
    if 'notelist' in placement:
        pl_nl = placement['notelist']
        del placement['notelist']
        pl_base = placement
        splitted_instnotes = {}
        for note in pl_nl:
            note_inst = note['instrument']
            del note['instrument']
            if note_inst not in splitted_instnotes:
                splitted_instnotes[note_inst] = []
            splitted_instnotes[note_inst].append(note)
        for inst in splitted_instnotes:
            out_pl = {}
            out_pl['notelist'] = splitted_instnotes[inst]
            if inst not in out_inst_pl: out_inst_pl[inst] = pl_base | out_pl
    return out_inst_pl

def m2r_addplacements(placements):
    for placement in placements:
        mpl_num = 0
        success = 0
        pla_s = placement['position']
        pla_e = pla_s + placement['duration']
        multiplacements = [[]]
        while success == 0:
            total_overlap = 0
            for e_pla in multiplacements[mpl_num]:
                e_pla_s = e_pla['position']
                e_pla_e = e_pla_s + e_pla['duration']
                total_overlap += overlap(e_pla_s, e_pla_e, pla_s, pla_e)
            if total_overlap == 0:
                multiplacements[mpl_num].append(placement)
                success = 1
                break
            else:
                multiplacements.append([])
                mpl_num += 1
    return multiplacements

def m2r(song):
    cvpj_proj = json.loads(song)

    playlist = cvpj_proj['playlist']
    cvpjm_instruments = cvpj_proj['instruments']
    cvpjm_instrumentsorder = cvpj_proj['instrumentsorder']

    del cvpj_proj['playlist']
    del cvpj_proj['instruments']
    del cvpj_proj['instrumentsorder']

    cvpj_trackdata = {}
    cvpj_trackorder = []

    for instrument in cvpjm_instrumentsorder:
        if instrument in cvpjm_instruments:
            trackdata = cvpjm_instruments[instrument]
            cvpj_trackdata[instrument] = trackdata
            trackdata['type'] = 'instrument'
            cvpj_trackdata[instrument]['laned'] = 1
            cvpj_trackdata[instrument]['lanedata'] = {}
            cvpj_trackdata[instrument]['laneordering'] = []
            
            cvpj_trackorder.append(instrument)

    for playlistentry in playlist:
        plrow = playlist[playlistentry]
        if 'placements' in plrow:
            placements = plrow['placements']
            for placement in placements:
                if placement['type'] == 'instruments':
                    splitted_insts = m2r_split_insts(placement)
                    for instrument in splitted_insts:
                        lanedata = cvpj_trackdata[instrument]['lanedata']
                        if playlistentry not in lanedata:
                            lanedata[playlistentry] = {}
                            if 'name' in playlist[playlistentry]:
                                lanedata[playlistentry]['name'] = playlist[playlistentry]['name']
                            if 'color' in playlist[playlistentry]:
                                lanedata[playlistentry]['color'] = playlist[playlistentry]['color']
                            cvpj_trackdata[instrument]['laneordering'].append(playlistentry)
                            lanedata[playlistentry]['placements'] = []
                        cvpj_trackdata[instrument]['lanedata'][playlistentry]['placements'].append(splitted_insts[instrument])

    cvpj_proj['trackdata'] = cvpj_trackdata
    cvpj_proj['trackordering'] = cvpj_trackorder

    return json.dumps(cvpj_proj)