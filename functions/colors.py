# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
import numpy as np
import math
from functions import xtramath

def closest_color_index(colors, color):
    colors = np.array(colors)
    color = np.array(color)
    distances = np.sqrt(np.sum((colors-color)**2,axis=1))
    index_of_smallest = np.where(distances==np.amin(distances))
    return index_of_smallest[0][0]

def hsv_to_rgb(h, s, v) -> tuple:

    h -= math.ceil(h)-1

    if s:
        if h == 1.0: h = 0.0
        i = int(h*6.0); f = h*6.0 - i
        w = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        if i==0: return (v, t, w)
        if i==1: return (q, v, w)
        if i==2: return (w, v, t)
        if i==3: return (w, q, v)
        if i==4: return (t, w, v)
        if i==5: return (v, w, q)
    else: return (v, v, v)

# from hex
def hex_to_rgb_int(hexcode):
    nonumsign = hexcode.lstrip('#')
    return tuple(int(nonumsign[i:i+2], 16) for i in (0, 2, 4))

def rgb_int_to_rgb_float(rgb_int): return [rgb_int[0]/255, rgb_int[1]/255, rgb_int[2]/255]

def hex_to_rgb_float(hexcode): return rgb_int_to_rgb_float(hex_to_rgb_int(hexcode))

# to hex
def rgb_float_2_rgb_int(rgb_float): return (int(rgb_float[0]*255),int(rgb_float[1]*255),int(rgb_float[2]*255))

def rgb_int_2_hex(rgb_int): return '%02x%02x%02x' % rgb_int

def rgb_float_2_hex(rgb_float): return rgb_int_2_hex(rgb_float_2_rgb_int(rgb_float))

# fx
def moregray(rgb_float): return [(rgb_float[0]/2)+0.25,(rgb_float[1]/2)+0.25,(rgb_float[2]/2)+0.25]
def darker(rgb_float, minus): 
    return [xtramath.clamp(rgb_float[0]-minus, 0, 1),xtramath.clamp(rgb_float[1]-minus, 0, 1),xtramath.clamp(rgb_float[2]-minus, 0, 1)]
