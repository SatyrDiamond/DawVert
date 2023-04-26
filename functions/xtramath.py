# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def clamp(n, minn, maxn):
	return max(min(maxn, n), minn)

def overlap(start1, end1, start2, end2):
    return max(max((end2-start1), 0) - max((end2-end1), 0) - max((start2-start1), 0), 0)

def float_range(start,stop,step):
    istop = int((stop-start) // step)
    for i in range(int(istop)):
        yield start + i * step

def betweenvalues(minval, maxval, value): 
    return (minval*(1-value))+(maxval*value)

def is_between(i_min, i_max, i_value): 
    return min(i_min, i_max) <= i_value <= max(i_min, i_max)
