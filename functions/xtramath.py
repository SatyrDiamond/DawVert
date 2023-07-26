# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def overlap(start1, end1, start2, end2):
    return max(max((end2-start1), 0) - max((end2-end1), 0) - max((start2-start1), 0), 0)

def between_from_one(minval, maxval, value): 
    return (minval*(1-value))+(maxval*value)

def between_to_one(minval, maxval, value): 
    if minval == maxval: return 0
    else: return (value-minval)/(maxval-minval)

def is_between(i_min, i_max, i_value): 
    return min(i_min, i_max) <= i_value <= max(i_min, i_max)

def gen_float_range(start,stop,step):
    istop = int((stop-start) // step)
    for i in range(int(istop)):
        yield start + i * step

def steps_to_one(in_val, steps):
    prev_step = steps[0]
    maxlen = len(steps)-1
    for index_n in range(1, maxlen):
        step = steps[index_n]
        index = index_n-1
        if is_between(prev_step, step, in_val) == True:
            return between_to_one(prev_step, step, in_val)*(1/maxlen)+(index/maxlen)
        prev_step = step
    return 0

def sep_pan_to_vol(i_left, i_right):
    val_vol = max(i_left, i_right)
    if val_vol != 0: 
        i_left = i_left/val_vol
        i_right = i_right/val_vol
    pan_val = (i_left*-1)+i_right
    return pan_val, val_vol