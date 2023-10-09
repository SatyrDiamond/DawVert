# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import song

def create_points_cut(projJ, cvpj_type):
    if cvpj_type == 'r': songduration = song.r_getduration(projJ)
    if cvpj_type == 'm': songduration = song.m_getduration(projJ)

    if 'timesig' in projJ: timesig_numerator = projJ['timesig'][0]
    else: timesig_numerator = 4

    timesigposs = []
    timesigblocks = []
    if 'timemarkers' in projJ:
        for timemarker in projJ['timemarkers']:
            if 'type' in timemarker:
                if timemarker['type'] == 'timesig':
                    numerator = timemarker['numerator']
                    denominator = timemarker['denominator']
                    outval = (numerator/denominator)*4
                    timesigposs.append([timemarker['position'], outval])

    if timesigposs == []: timesigposs.append([0, 4])

    timesigposs.append([songduration, None])
    if timesigposs == []: timesigposs = [[0, timesig_numerator],[songduration, timesig_numerator]] 

    for timesigposnum in range(len(timesigposs)-1):
        timesigpos = timesigposs[timesigposnum]
        timesigblocks.append([timesigpos[0], timesigposs[timesigposnum+1][0], float(timesigpos[1])*4])

    return timesigposs, timesigblocks