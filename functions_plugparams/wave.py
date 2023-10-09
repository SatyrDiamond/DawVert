# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import math
import struct
from functions import data_values
from functions import data_bytes
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

def resizewave(inputwave, **kwargs):
    dur_input = len(inputwave)
    numpoints = kwargs['points'] if 'points' in kwargs else 2048
    numpointshalf = numpoints // 2
    wave_data = []
    smooth = kwargs['smooth'] if 'smooth' in kwargs else True if dur_input > 10 else False

    if smooth == False:
        for num in range(numpoints): 
            s_pos = num/numpoints
            wave_data.append(inputwave[math.floor(s_pos*dur_input)])

    else:
        inputwave += inputwave
        for num in range(numpoints): 
            s_pos = num/numpoints
            wpn_float = s_pos*dur_input
            wpn_floor = int(math.floor(wpn_float))
            betweenpoints = wpn_float-wpn_floor
            out_val = xtramath.between_from_one(inputwave[wpn_floor], inputwave[wpn_floor+1], betweenpoints)
            wave_data.append(out_val)

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
            wavedata_points = [xtramath.between_to_one(rangedata[0], rangedata[1], i) for i in wavedata_points]
        return resizewave(wavedata_points)
    else: return None

def wave2file(cvpj_l, pluginid, wave_name, fileloc):
    wavedata = cvpjwave2wave(cvpj_l, pluginid, wave_name)
    if wavedata != None:
        audiowavdata = [int(i*65535) for i in wavedata]
        wave_data = data_bytes.unsign_16(struct.pack('H'*len(audiowavdata), *audiowavdata))
        audio_wav.generate(fileloc, wave_data, 1, 44100, 16, None)

def cvpjharm2wave(cvpj_l, pluginid, harm_name):
    harmdata = plugins.get_harmonics(cvpj_l, pluginid, harm_name)
    if harmdata != None: 
        harmonics_data = harmdata['harmonics']
        wavedata_points = []
        for num in range(2048):
            s_pos = num/2048
            sample = 0
            for harm_num in range(len(harmonics_data)):
                sine_pitch = s_pos*(harm_num+1)
                sine_vol = harmonics_data[harm_num]
                sample += wave_sine(sine_pitch)*sine_vol
            wavedata_points.append(sample)
        min_value = min(wavedata_points)
        max_value = max(wavedata_points)
        wavedata_points = [xtramath.between_to_one(min_value, max_value, i) for i in wavedata_points]
        return wavedata_points
    else: return None

def harm2file(cvpj_l, pluginid, harm_name, fileloc):
    wavedata = cvpjharm2wave(cvpj_l, pluginid, harm_name)
    audiowavdata = [int(i*65535) for i in wavedata]
    wave_data = data_bytes.unsign_16(struct.pack('H'*len(audiowavdata), *audiowavdata))
    audio_wav.generate(fileloc, wave_data, 1, 44100, 16, None)
