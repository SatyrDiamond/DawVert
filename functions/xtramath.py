# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def overlap(start1, end1, start2, end2):
    return max(max((end2-start1), 0) - max((end2-end1), 0) - max((start2-start1), 0), 0)

def betweenvalues(minval, maxval, value): 
    return (minval*(1-value))+(maxval*value)

def betweenvalues_r(minval, maxval, value): 
    if minval == maxval: return 0
    else: return (value-minval)/(maxval-minval)

def is_between(i_min, i_max, i_value): 
    return min(i_min, i_max) <= i_value <= max(i_min, i_max)

def gen_float_range(start,stop,step):
    istop = int((stop-start) // step)
    for i in range(int(istop)):
        yield start + i * step

def steps_to_one(audio_value, steps):
    prev_step = steps[0]
    maxlen = len(steps)-1
    for index_n in range(1, maxlen):
        step = steps[index_n]
        index = index_n-1
        if is_between(prev_step, step, audio_value) == True:
            return betweenvalues_r(prev_step, step, audio_value)*(1/maxlen)+(index/maxlen)
        prev_step = step
    return 0
