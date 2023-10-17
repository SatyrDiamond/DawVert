# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import math

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def overlap(start1, end1, start2, end2):
    return max(max((end2-start1), 0) - max((end2-end1), 0) - max((start2-start1), 0), 0)

def average(lst):
    return sum(lst) / len(lst)

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

def gen_float_blocks(size,step):
    curval = size
    if step == 0: step = 1
    while curval > 0:
        yield min(curval,step)
        curval -= step

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

# -------------------------------------------- placement_loop --------------------------------------------

def loop_cutpoint(pl_pos, pl_dur, cut_start, cut_end):
    return [pl_pos, pl_dur, cut_start, cut_end]

def loop_before(bl_p_pos, bl_p_dur, bl_p_start, bl_l_start, bl_l_end):
    #print('BEFORE')
    cutpoints = []
    temppos = min(bl_l_end, bl_p_dur)
    cutpoints.append([(bl_p_pos+bl_p_start)-bl_p_start, temppos-bl_p_start, bl_p_start, min(bl_l_end, bl_p_dur)])
    bl_p_dur += bl_p_start
    placement_loop_size = bl_l_end-bl_l_start
    if bl_l_end < bl_p_dur and bl_l_end > bl_l_start:
        remainingcuts = (bl_p_dur-bl_l_end)/placement_loop_size
        while remainingcuts > 0:
            outdur = min(remainingcuts, 1)
            cutpoints.append([(bl_p_pos+temppos)-bl_p_start, placement_loop_size*outdur, bl_l_start, bl_l_end*outdur])
            temppos += placement_loop_size
            remainingcuts -= 1
    return cutpoints

def loop_after(bl_p_pos, bl_p_dur, bl_p_start, bl_l_start, bl_l_end):
    #print('AFTER')
    cutpoints = []
    placement_loop_size = bl_l_end-bl_l_start
    #print(bl_p_pos, bl_p_dur, '|', bl_p_start, '|', bl_l_start, bl_l_end, '|', placement_loop_size)
    bl_p_dur_mo = bl_p_dur-bl_l_start
    bl_p_start_mo = bl_p_start-bl_l_start
    bl_l_start_mo = bl_l_start-bl_l_start
    bl_l_end_mo = bl_l_end-bl_l_start

    if placement_loop_size != 0: remainingcuts = (bl_p_dur_mo+bl_p_start_mo)/placement_loop_size
    else: remainingcuts = 0
    #print(bl_p_pos, bl_p_dur, '|', bl_p_start_mo, '|', bl_l_start_mo, bl_l_end_mo, '|', placement_loop_size)
    temppos = bl_p_pos
    temppos -= bl_p_start_mo
    flag_first_pl = True
    while remainingcuts > 0:
        outdur = min(remainingcuts, 1)
        if flag_first_pl == True:
            cutpoints.append([
                    temppos+bl_p_start_mo, 
                    (outdur*placement_loop_size)-bl_p_start_mo, 
                    bl_l_start+bl_p_start_mo, 
                    outdur*bl_l_end
                    ])
        if flag_first_pl == False:
            cutpoints.append([temppos, outdur*placement_loop_size, bl_l_start, outdur*bl_l_end])
        temppos += placement_loop_size
        remainingcuts -= 1
        flag_first_pl = False
    return cutpoints

def cutloop(position, duration, startoffset, loopstart, loopend): 
    if loopstart > startoffset: cutpoints = loop_before(position, duration, startoffset, loopstart, loopend)
    else: cutpoints = loop_after(position, duration, startoffset, loopstart, loopend)
    return cutpoints

def similar(first, second):
    if first == second: return 1.0
    elif first == second == []: return 1.0
    else: return len(set(first) & set(second)) / float(len(set(first) | set(second)))

def logpowmul(value, multiplier):
    value = -math.log2(1/value)
    value = pow(2, value*multiplier)
    return value










