
def removelanes(projJ):
    old_trackdata = projJ['trackdata']
    old_trackordering = projJ['trackordering']
    new_trackdata = {}
    new_trackordering = []

    for trackid in old_trackordering:
        if trackid in old_trackdata:
            lr_t_trdata = old_trackdata[trackid]
            if 'laned' in lr_t_trdata:
                trackbase = lr_t_trdata.copy()
                del trackbase['laned']
                del trackbase['lanedata']
                del trackbase['laneordering']
                lr_t_lanedata = lr_t_trdata['lanedata']
                lr_t_laneordering = lr_t_trdata['laneordering']
                for laneid in lr_t_laneordering:
                    lr_t_l_data = lr_t_lanedata[laneid]
                    splitnameid = trackid+'_Lane'+laneid
                    if 'name' in lr_t_l_data: lr_t_l_name = lr_t_l_data['name']
                    else: lr_t_l_name = ''
                    if 'placements' in lr_t_l_data: lr_t_l_placements = lr_t_l_data['placements']
                    else: lr_t_l_placements = []
                    if 'name' in lr_t_trdata: ntp_name = lr_t_trdata['name']+' ['+lr_t_l_name+']'
                    else: ntp_name = '['+lr_t_l_name+']'
                    part_track_data = trackbase.copy()
                    part_track_data['name'] = ntp_name
                    part_track_data['placements'] = lr_t_l_placements
                    new_trackdata[splitnameid] = part_track_data
                    new_trackordering.append(splitnameid)
            else:
                new_trackdata[trackid] = lr_t_trdata
                new_trackordering.append(trackid)
    projJ['trackdata'] = new_trackdata
    projJ['trackordering'] = new_trackordering

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