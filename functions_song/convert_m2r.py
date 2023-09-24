# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from functions import data_values
from functions import xtramath

def lanefit_checkoverlap(new_placementdata, placements_table, num):
    not_overlapped = True
    p_pl_pos = new_placementdata['position']
    p_pl_dur = new_placementdata['duration']
    p_pl_end = p_pl_pos+p_pl_dur
    for lanepl in placements_table[num]:
        e_pl_pos = lanepl['position']
        e_pl_dur = lanepl['duration']
        e_pl_end = e_pl_pos+e_pl_dur
        if bool(xtramath.overlap(p_pl_pos, p_pl_end, e_pl_pos, e_pl_end)) == True: not_overlapped = False
    return not_overlapped

def lanefit_addpl(new_placementdata, placements_table):
    lanenum = 0
    placement_placed = False
    while placement_placed == False:
        not_overlapped = lanefit_checkoverlap(new_placementdata, placements_table, lanenum)
        #print(lanenum, not_overlapped)
        if not_overlapped == True:
            placement_placed = True
            placements_table[lanenum].append(new_placementdata)
        if not_overlapped == False:
            placements_table.append([])
            lanenum += 1


def r_lanefit(projJ):
    if 'do_lanefit' in projJ:
        if projJ['do_lanefit'] == True:
            trackplacements = projJ['track_placements']
            for trackid in trackplacements:
                if 'laned' in trackplacements[trackid]:
                    if trackplacements[trackid]['laned'] == True:
                        old_lanedata = trackplacements[trackid]['lanedata']
                        old_laneordering = trackplacements[trackid]['laneorder']
                        print('[song-convert] LaneFit: '+ trackid+': '+str(len(old_laneordering))+' > ', end='')
                        new_lanedata = {}
                        new_laneordering = []

                        new_pltable = [[]]
                        for laneid in old_laneordering:
                            old_lanedata_data = old_lanedata[laneid]
                            old_lanedata_pl = old_lanedata_data['notes']
                            for old_lanedata_pl_s in old_lanedata_pl:
                                lanefit_addpl(old_lanedata_pl_s, new_pltable)

                        for plnum in range(len(new_pltable)):
                            if new_pltable[plnum] != []:
                                newlaneid = '_lanefit_'+str(plnum)
                                new_lanedata[newlaneid] = {}
                                new_lanedata[newlaneid]['notes'] = new_pltable[plnum]
                                new_laneordering.append(newlaneid)

                        print(str(len(new_laneordering)))
                        trackplacements[trackid]['lanedata'] = new_lanedata
                        trackplacements[trackid]['laneorder'] = new_laneordering


def split_insts(placement):
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

def addplacements(placements):
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
                total_overlap += xtramath.overlap(e_pla_s, e_pla_e, pla_s, pla_e)
            if total_overlap == 0:
                multiplacements[mpl_num].append(placement)
                success = 1
                break
            else:
                multiplacements.append([])
                mpl_num += 1
    return multiplacements

def convert(song):
    print('[song-convert] Converting from Multiple > Regular')
    cvpj_proj = json.loads(song)

    playlist = cvpj_proj['playlist']
    if 'instruments_data' in cvpj_proj:
        cvpjm_instruments = cvpj_proj['instruments_data'] 
        del cvpj_proj['instruments_data']
    else: cvpjm_instruments = {}

    if 'instruments_order' in cvpj_proj:
        cvpjm_instruments_order = cvpj_proj['instruments_order'] 
        del cvpj_proj['instruments_order']
    else: cvpjm_instruments_order = []

    del cvpj_proj['playlist']

    cvpj_trackdata = {}
    cvpj_trackorder = []
    cvpj_trackplacements = {}

    for instrument in cvpjm_instruments_order:
        if instrument in cvpjm_instruments:
            cvpj_trackplacements[instrument] = {}
            trackdata = cvpjm_instruments[instrument]
            cvpj_trackdata[instrument] = trackdata
            trackdata['type'] = 'instrument'
            cvpj_trackplacements[instrument]['laned'] = 1
            cvpj_trackplacements[instrument]['lanedata'] = {}
            cvpj_trackplacements[instrument]['laneorder'] = []
            
            cvpj_trackorder.append(instrument)

    for playlistentry in playlist:
        plrow = playlist[playlistentry]

        if 'placements_notes' in plrow:
            placements = plrow['placements_notes']
            if 'name' in playlist[playlistentry]:
                print('[song-convert] m2r: Track ' + playlistentry+' ['+playlist[playlistentry]['name']+']')
            else: print('[song-convert] m2r: Track ' + playlistentry)
            for placement in placements:
                splitted_insts = split_insts(placement)
                for instrument in splitted_insts:
                    if instrument in cvpj_trackdata:
                        lanedata = cvpj_trackplacements[instrument]['lanedata']
                        if playlistentry not in lanedata:
                            lanedata[playlistentry] = {}
                            if 'name' in playlist[playlistentry]: lanedata[playlistentry]['name'] = playlist[playlistentry]['name']
                            if 'color' in playlist[playlistentry]: lanedata[playlistentry]['color'] = playlist[playlistentry]['color']
                            cvpj_trackplacements[instrument]['laneorder'].append(playlistentry)
                            lanedata[playlistentry]['notes'] = []
                        cvpj_trackplacements[instrument]['lanedata'][playlistentry]['notes'].append(splitted_insts[instrument])

        if 'placements_audio' in plrow:
            placements = plrow['placements_audio']
            fxrack_sep_placements = {}
            for placement in placements:
                fxrack = -1
                if 'fxrack_channel' in placement:
                    fxrack = placement['fxrack_channel']
                    del placement['fxrack_channel']
                    data_values.nested_dict_add_to_list(fxrack_sep_placements, [fxrack], placement)

            for fxrack_sep_placement in fxrack_sep_placements:
                cvpj_audiotrackid = 'm2r_audiotrack_'+str(playlistentry)+'_'+str(fxrack_sep_placement)
                cvpj_trackdata[cvpj_audiotrackid] = {}
                trackdata = cvpj_trackdata[cvpj_audiotrackid]
                trackdata['type'] = 'audio'
                cvpj_trackorder.insert(0, cvpj_audiotrackid)
                cvpj_trackplacements[cvpj_audiotrackid] = {}
                cvpj_trackplacements[cvpj_audiotrackid]['audio'] = []

                if 'name' in playlist[playlistentry]: trackdata['name'] = playlist[playlistentry]['name']
                if 'color' in playlist[playlistentry]: trackdata['color'] = playlist[playlistentry]['color']

                if fxrack_sep_placement != -1: trackdata['fxrack_channel'] = fxrack_sep_placement
                for placement in fxrack_sep_placements[fxrack_sep_placement]:
                    cvpj_trackplacements[cvpj_audiotrackid]['audio'].append(placement)
            
    cvpj_proj['track_data'] = cvpj_trackdata
    cvpj_proj['track_order'] = cvpj_trackorder
    cvpj_proj['track_placements'] = cvpj_trackplacements

    r_lanefit(cvpj_proj)
    
    return json.dumps(cvpj_proj)
