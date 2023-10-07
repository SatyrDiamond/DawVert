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

def create_wave(shape, mul, pw):
    vital_osc_shape = []
    if shape == 'sine': vital_osc_shape = [wave_sine(num/2048) for num in range(2048)]
    if shape == 'saw': vital_osc_shape = [wave_saw(num/2048) for num in range(2048)]
    if shape == 'triangle': vital_osc_shape = [wave_tri(num/2048) for num in range(2048)]
    if shape == 'square': vital_osc_shape = [wave_squ(num/2048) for num in range(2048)]
    if shape == 'square_roundend':
        for num in range(2048): 
            if num <= 1024: vital_osc_shape.append((wave_sine(num/4096)*-1))
            else: vital_osc_shape.append(0)
    if shape == 'mooglike':
        for num in range(2048): 
            if num <= 1024: vital_osc_shape.append(num/1024)
            else: vital_osc_shape.append(wave_tri((num+1024)/2048)**3)
    if shape == 'exp': vital_osc_shape = [wave_tri((num+1024)/2048)**3 for num in range(2048)]
    return vital_osc_shape

