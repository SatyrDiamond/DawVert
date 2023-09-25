# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import song

def create_points_cut(projJ):
    songduration = song.r_getduration(projJ)
    if 'timesig_numerator' in projJ: timesig_numerator = projJ['timesig_numerator']
    else: timesig_numerator = 4

    timesigposs = []
    timesigblocks = []
    if 'timemarkers' in projJ:
        for timemarker in projJ['timemarkers']:
            if 'type' in timemarker:
                if timemarker['type'] == 'timesig':
                    timesigposs.append([timemarker['position'], timemarker['numerator']])

    if timesigblocks == []: timesigposs.append([0, 4])

    timesigposs.append([songduration, None])
    if timesigposs == []: timesigposs = [[0, timesig_numerator],[songduration, timesig_numerator]] 

    for timesigposnum in range(len(timesigposs)-1):
        timesigpos = timesigposs[timesigposnum]
        timesigblocks.append([timesigpos[0], timesigposs[timesigposnum+1][0], float(timesigpos[1])*4])

    return timesigposs, timesigblocks