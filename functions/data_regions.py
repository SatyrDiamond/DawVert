# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath

def reverse(regions, num_len):
    return [[((num_len-region[0])-region[1])-1, region[1]] for region in regions]

def split(regionsdata, splitnum, mindur):
    out_regionsdata = []
    for region in regionsdata:
        if region[0] < splitnum < region[1]:
            if splitnum-region[0] >= mindur: out_regionsdata.append([region[0], splitnum])
            if region[1]-splitnum >= mindur: out_regionsdata.append([splitnum, region[1]])
        else: out_regionsdata.append(region)
    return out_regionsdata

def get_startendpoints(regionsdata, startpoints, endpoints, mindur):
    for region in regionsdata:
        if (region[1]-region[0]) >= mindur: 
            if region[0] not in startpoints: startpoints[region[0]] = 0
            startpoints[region[0]] += 1
            if region[1] not in endpoints: endpoints[region[1]] = 0
            endpoints[region[1]] += 1















def boollist_get(regionsdata, num_len):
    used_areas = [False for _ in range(num_len)]
    for s_reg in regionsdata:
        for num in range(s_reg[0], s_reg[0]+s_reg[1]): 
            used_areas[num] = True
    return used_areas

def boollist_merge(used1, used2):
    return [(used1[x] or used2[x]) for x in range(len(used1))]