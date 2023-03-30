# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import math
from functions import note_mod
from functions import notelist_data

def float_range(start,stop,step):
    istop = int((stop-start) // step)
    for i in range(int(istop)):
        yield start + i * step

def overlap(start1, end1, start2, end2):
    return max(max((end2-start1), 0) - max((end2-end1), 0) - max((start2-start1), 0), 0)

def getsongduration(projJ):
    trackplacements = projJ['track_placements']
    songduration = 0
    for trackid in trackplacements:

        islaned = False
        if 'laned' in trackplacements[trackid]:
            if trackplacements[trackid]['laned'] == 1:
                islaned = True


        if islaned == False:
            if 'notes' in trackplacements[trackid]:
                for placement in trackplacements[trackid]['notes']:
                    p_pos = placement['position']
                    p_dur = placement['duration']
                    if songduration < p_pos+p_dur:
                        songduration = p_pos+p_dur
        else:
            if 'lanedata' in trackplacements[trackid]:
                for s_lanedata in trackplacements[trackid]['lanedata']:
                    placementdata = trackplacements[trackid]['lanedata'][s_lanedata]['notes']
                    for placement in placementdata:
                        p_pos = placement['position']
                        p_dur = placement['duration']
                        if songduration < p_pos+p_dur:
                            songduration = p_pos+p_dur

    return songduration + 64

points_items = None


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


def nl2pl(cvpj_notelist):
    return [{'position': 0, 'duration': notelist_data.getduration(cvpj_notelist), 'notelist': cvpj_notelist}]
