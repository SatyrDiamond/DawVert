# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import math

def overlap(start1, end1, start2, end2):
    return max(max((end2-start1), 0) - max((end2-end1), 0) - max((start2-start1), 0), 0)

def removelanes(projJ):
    old_trackdata = projJ['track_data']
    old_trackordering = projJ['track_order']
    new_trackdata = {}
    new_trackordering = []

    for trackid in old_trackordering:
        if trackid in old_trackdata:
            lr_t_trdata = old_trackdata[trackid]
            if 'laned' in lr_t_trdata:
                lr_t_lanedata = lr_t_trdata['lanedata']
                lr_t_laneordering = lr_t_trdata['laneordering']
                if len(lr_t_laneordering) != 0:
                    trackbase = lr_t_trdata.copy()
                    del trackbase['laned']
                    del trackbase['lanedata']
                    del trackbase['laneordering']
                    for laneid in lr_t_laneordering:
                        lr_t_l_data = lr_t_lanedata[laneid]
                        splitnameid = trackid+'_Lane'+laneid
                        if 'placements' in lr_t_l_data: lr_t_l_placements = lr_t_l_data['placements']
                        else: lr_t_l_placements = []

                        if 'name' in lr_t_l_data: lr_t_l_name = lr_t_l_data['name']
                        else: lr_t_l_name = None

                        if 'name' in lr_t_trdata and lr_t_l_name != None: 
                            ntp_name = lr_t_trdata['name']+' ['+lr_t_l_name+']'
                        if 'name' in lr_t_trdata and lr_t_l_name == None: 
                            ntp_name = lr_t_trdata['name']

                        if 'name' not in lr_t_trdata and lr_t_l_name != None: 
                            ntp_name = 'none'+' ['+lr_t_l_name+']'
                        if 'name' not in lr_t_trdata and lr_t_l_name == None: 
                            ntp_name = 'none'

                        part_track_data = trackbase.copy()
                        part_track_data['name'] = ntp_name
                        part_track_data['placements'] = lr_t_l_placements

                        if 'color' not in part_track_data and 'color' in lr_t_l_data:
                            part_track_data['color'] = lr_t_l_data['color']

                        new_trackdata[splitnameid] = part_track_data
                        new_trackordering.append(splitnameid)
                else:
                    new_trackdata[trackid] = lr_t_trdata
                    new_trackordering.append(trackid)
            else:
                new_trackdata[trackid] = lr_t_trdata
                new_trackordering.append(trackid)
    projJ['track_data'] = new_trackdata
    projJ['track_order'] = new_trackordering


def lanefit_checkoverlap(new_placementdata, placements_table, num):
    not_overlapped = True
    p_pl_pos = new_placementdata['position']
    p_pl_dur = new_placementdata['duration']
    p_pl_end = p_pl_pos+p_pl_dur
    #print('----------------------------')
    for lanepl in placements_table[num]:
        e_pl_pos = lanepl['position']
        e_pl_dur = lanepl['duration']
        e_pl_end = e_pl_pos+e_pl_dur
        if bool(overlap(p_pl_pos, p_pl_end, e_pl_pos, e_pl_end)) == True: not_overlapped = False
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


def lanefit(projJ):
    if 'use_lanefit' in projJ:
        if projJ['use_lanefit'] == True:
            trackdata = projJ['track_data']
            trackordering = projJ['track_order']
            for trackid in trackordering:
                if trackid in trackdata:
                    lr_t_trdata = trackdata[trackid]
                    if 'laned' in lr_t_trdata:
                        new_lanedata = {}
                        new_laneordering = []
                        old_lanedata = lr_t_trdata['lanedata']
                        old_laneordering = lr_t_trdata['laneordering']

                        new_pltable = [[]]

                        for laneid in old_laneordering:
                            old_lanedata_data = old_lanedata[laneid]
                            old_lanedata_pl = old_lanedata_data['placements']
                            for old_lanedata_pl_s in old_lanedata_pl:
                                lanefit_addpl(old_lanedata_pl_s, new_pltable)

                        for plnum in range(len(new_pltable)):
                            if new_pltable[plnum] != []:
                                newlaneid = 'lanefit_'+str(plnum)
                                new_lanedata[newlaneid] = {}
                                new_lanedata[newlaneid]['placements'] = new_pltable[plnum]
                                new_laneordering.append(newlaneid)

                        lr_t_trdata['lanedata'] = new_lanedata
                        lr_t_trdata['laneordering'] = new_laneordering



def addwarps(projJ):
    if 'use_addwrap' in projJ:
        if projJ['use_addwrap'] == True:
            trackdata = projJ['track_data']
            trackordering = projJ['track_order']
            for trackid in trackordering:
                if trackid in trackdata:
                    prevpp = None
                    #print(trackid)
                    new_placements = []
                    if 'placements' in trackdata[trackid]:
                        for placement in trackdata[trackid]['placements']:
                            p_pos = placement['position']
                            p_dur = placement['duration']
                            p_nl = placement['notelist']
                            ipnl = False
                            if prevpp != None:
                                isfromprevpos = prevpp[0]==p_pos-p_dur
                                isdursame = prevpp[1]==p_dur
                                issamenotelist = prevpp[2]==p_nl
                                isplacecut = 'cut' in placement
                                prevpp[0]==p_pos-p_dur
                                if isfromprevpos == True:
                                    if issamenotelist == True:
                                        if isdursame == True:
                                            if isplacecut == False:
                                                ipnl = True
                                                if 'cut' not in new_placements[-1]:
                                                    new_placements[-1]['cut'] = {}
                                                    new_placements[-1]['cut']['type'] = 'warp'
                                                    new_placements[-1]['cut']['start'] = 0
                                                    new_placements[-1]['cut']['loopstart'] = 0
                                                    new_placements[-1]['cut']['loopend'] = p_dur
                                                    new_placements[-1]['duration'] += p_dur
                                                else:
                                                    new_placements[-1]['duration'] += p_dur
                            if ipnl == False:
                                new_placements.append(placement)
                            prevpp = [p_pos, p_dur, p_nl]
                        trackdata[trackid]['placements'] = new_placements

def get_timesig(patternLength, notesPerBeat):
    MaxFactor = 1024
    factor = 1
    while (((patternLength * factor) % notesPerBeat) != 0 and factor <= MaxFactor):
        factor *= 2
    foundValidFactor = ((patternLength * factor) % notesPerBeat) == 0
    numer = 4
    denom = 4

    if foundValidFactor == True:
        numer = patternLength * factor / notesPerBeat
        denom = 4 * factor
    else: 
        print('Error computing valid time signature, defaulting to 4/4.')

    return [int(numer), denom]


def resize_nl_multi(placementsdata):
    for placement in placementsdata:
        resize_nl(placement)

def resize_nl(placementdata):
    in_pos = placementdata['position']
    in_dur = placementdata['duration']

    if 'notelist' in placementdata:
        if placementdata['notelist'] != []:
            in_nl = placementdata['notelist']
            duration_final = None
            for note in in_nl:
                notepos = note['position']
                if duration_final != None:
                    if duration_final > notepos: duration_final = notepos
                else: duration_final = notepos

            if duration_final != 0:
                placementdata['cut'] = {}
                placementdata['cut']['type'] = 'cut'
                placementdata['cut']['start'] = duration_final
                placementdata['cut']['end'] = in_dur

            placementdata['position'] = in_pos+duration_final


def make_timemarkers(timesig, PatternLengthList, LoopPos):
    prevtimesig = timesig
    timemarkers = []
    currentpos = 0
    blockcount = 0
    for PatternLengthPart in PatternLengthList:
        temptimesig = get_timesig(PatternLengthPart, timesig[1])
        if prevtimesig != temptimesig:
            timemarker = {}
            timemarker['position'] = currentpos
            timemarker['name'] = str(temptimesig[0])+'/'+str(temptimesig[1])
            timemarker['type'] = 'timesig'
            timemarker['numerator'] = temptimesig[0]
            timemarker['denominator'] = temptimesig[1]
            timemarkers.append(timemarker)
        if LoopPos == blockcount:
            timemarker = {}
            if prevtimesig != temptimesig:
                timemarker['name'] = str(temptimesig[0])+'/'+str(temptimesig[1]) + " & Loop"
            else:
                timemarker['name'] = "Loop"
            timemarker['position'] = currentpos
            timemarker['type'] = 'loop'
            timemarkers.append(timemarker)
        prevtimesig = temptimesig
        currentpos += PatternLengthPart
        blockcount += 1
    return timemarkers