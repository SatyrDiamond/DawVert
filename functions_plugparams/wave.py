# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import math
import struct
from functions import data_values
from functions import plugins
from functions import xtramath
from functions import audio_wav

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

def resizewave(imputwave, **kwargs):
    dur_input = len(imputwave)
    numpoints = data_values.get_value(kwargs, 'points', 2048)
    numpointshalf = numpoints // 2
    wave_data = []
    for num in range(2048): 
        s_pos = num/2048
        wave_data.append(imputwave[math.floor(s_pos*dur_input)])
    return wave_data

def create_wave(shape, mul, pw, **kwargs):
    numpoints = data_values.get_value(kwargs, 'points', 2048)
    halfpoint = numpoints // 2
    wave_data = []
    if shape == 'sine': 
        for num in range(numpoints): wave_data.append(wave_sine(num/2048))
    if shape == 'saw':
        for num in range(numpoints): wave_data.append(wave_saw(num/2048))
    if shape == 'triangle':
        for num in range(numpoints): wave_data.append(wave_tri(num/2048))
    if shape == 'square':
        for num in range(numpoints): wave_data.append(wave_squ(num/2048, pw))
    if shape == 'square_roundend':
        for num in range(numpoints): 
            if num <= halfpoint: wave_data.append((wave_sine(num/4096)*-1))
            else: wave_data.append(0)
    if shape == 'mooglike':
        for num in range(numpoints): 
            if num <= halfpoint: wave_data.append(num/halfpoint)
            else: wave_data.append(wave_tri((num+halfpoint)/numpoints)**3)
    if shape == 'exp':
        for num in range(numpoints): wave_data.append(wave_tri((num+halfpoint)/numpoints)**3)
    return wave_data

def cvpjwave2wave(cvpj_l, pluginid, wave_name):
    wavedata = plugins.get_wave(cvpj_l, pluginid, wave_name)
    if wavedata != None:
        wavedata_points = wavedata['points']
        if 'range' in wavedata:
            rangedata = wavedata['range']
            wavedata_points = [xtramath.betweenvalues_r(rangedata[0], rangedata[1], i) for i in wavedata_points]
        return resizewave(wavedata_points)
    else: return None

def wave2file(cvpj_l, pluginid, wave_name, fileloc):
    wavedata = cvpjwave2wave(cvpj_l, pluginid, 'chipwave')
    audiowavdata = [int(i*255) for i in wavedata]
    wave_data = struct.pack('B'*len(audiowavdata), *audiowavdata)
    audio_wav.generate(fileloc, wave_data, 1, 44100, 8, None)

#[xtramath.betweenvalues_r(rangedata[0], rangedata[1], i) for i in wavedata_points]