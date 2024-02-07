# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def create_points_cut(convproj_obj):
    songduration = convproj_obj.get_dur()
    ppq = convproj_obj.time_ppq
    timesig_numerator, timesig_numerator = convproj_obj.timesig

    timesigposs = []

    for p, v in convproj_obj.timesig_auto.iter():
        outval = (v[0]/v[1])
        timesigposs.append([p, int(outval*ppq)])

    #print(timesigposs)
    #exit()

    if timesigposs == []: timesigposs.append([0, int(4*ppq)])
    timesigposs.append([songduration, None])
    if timesigposs == []: timesigposs = [[0, timesig_numerator*ppq],[songduration, timesig_numerator*ppq]] 

    timesigblocks = []
    for timesigposnum in range(len(timesigposs)-1):
        timesigpos = timesigposs[timesigposnum]
        timesigblocks.append([timesigpos[0], timesigposs[timesigposnum+1][0], timesigpos[1]*4])

    splitpoints = []
    for timesigblock in timesigblocks:
        remaining = timesigblock[1]%timesigblock[2]
        for point in range(timesigblock[0], timesigblock[1], timesigblock[2]):
            #print('P', point)
            splitpoints.append(point)
        if remaining: 
            #print('R', point+remaining)
            splitpoints.append(point+remaining)

    return splitpoints, timesigposs