# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import math

# -------------------- Shapes --------------------
def wave_sine(x): return math.sin((x-0.5)*(math.pi*2))
def wave_saw(x): return x-math.floor(x)
def wave_tri(x): return abs((x*2)%(2)-1)
def wave_squ(x, pw):
    if wave_tri(x) > pw: return 1
    else: return -1

def tripleoct(x, shape, pw, one, two):
    if shape == 'sine': samplepoint = wave_sine(x) + wave_sine(x*2)*one + wave_sine(x*4)*two
    elif shape == 'saw': samplepoint = wave_saw(x) + wave_saw(x*2)*one + wave_saw(x*4)*two
    elif shape == 'triangle': samplepoint = wave_tri(x) + wave_tri(x*2)*one + wave_tri(x*4)*two
    elif shape == 'square': samplepoint = wave_squ(x, pw) + wave_squ(x*2, pw)*one + wave_squ(x*4, pw)*two
    else: samplepoint = x
    return samplepoint

def resizewave(imputwave):
    dur_input = len(imputwave)
    vital_osc_shape = []
    for num in range(2048): 
        s_pos = num/2048
        vital_osc_shape.append(imputwave[math.floor(s_pos*dur_input)])
    return vital_osc_shape

def create_wave(shape, mul, pw):
    vital_osc_shape = []
    if shape == 'sine': 
        for num in range(2048): vital_osc_shape.append(wave_sine(num))
    if shape == 'saw':
        for num in range(2048): vital_osc_shape.append(wave_saw(num))
    if shape == 'triangle':
        for num in range(2048): vital_osc_shape.append(wave_tri(num))
    if shape == 'square':
        for num in range(2048): vital_osc_shape.append(wave_squ(num, pw))
    return vital_osc_shape

