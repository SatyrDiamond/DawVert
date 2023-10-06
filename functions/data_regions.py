# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def reverse(regions, num_len):
    return [[((num_len-region[0])-region[1])-1, region[1]] for region in regions]

def get_used_areas(regionsdata, num_len):
    used_areas = [False for _ in range(num_len)]
    for s_reg in regionsdata:
        for num in range(s_reg[0], s_reg[0]+s_reg[1]): 
            used_areas[num] = True
    return used_areas

def get_endpoints(endpoints, regionsdata):
    for s_reg in regionsdata:
        endpointval = s_reg[0]+s_reg[1]
        if endpointval not in endpoints: endpoints[endpointval] = 0
        endpoints[endpointval] += 1

def merge_used_areas(used1, used2):
    return [(used1[x] or used2[x]) for x in range(len(used1))]