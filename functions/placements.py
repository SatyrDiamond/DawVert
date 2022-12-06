
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