# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import song
from functions import notelist_data
from functions import data_values
from functions import xtramath
from functions import params
from functions import tracks
from functions import audio

from functions_compat import fxrack2trackfx
from functions_compat import trackfx2fxrack

from functions_compat import autopl_remove
from functions_compat import changestretch
from functions_compat import loops_add
from functions_compat import loops_remove
from functions_compat import removecut
from functions_compat import removelanes
from functions_compat import time_seconds
from functions_compat import timesigblocks
from functions_compat import trackpl_add
from functions_compat import unhybrid
from functions_compat import fxrack_moveparams

import json
import math

finished_processes = []
in__dc = {}
out__dc = {}

def process_part(process_name, classname, cvpj_proj, cvpj_type, in_compat, out_compat):
    global finished_processes
    if process_name not in finished_processes:
        if classname.process(cvpj_proj, cvpj_type, in_compat, out_compat):
            finished_processes.append(process_name)

def set_dawcapabilities(in_dawcapabilities, out_dawcapabilities):
    global in__dc
    global out__dc

    for list__setdc, arg__dc in [[in__dc,in_dawcapabilities],[out__dc,out_dawcapabilities]]:
        list__setdc['track_lanes'] = arg__dc['track_lanes'] if 'track_lanes' in arg__dc else False
        list__setdc['track_nopl'] = arg__dc['track_nopl'] if 'track_nopl' in arg__dc else False
        list__setdc['track_hybrid'] = arg__dc['track_hybrid'] if 'track_hybrid' in arg__dc else False

        list__setdc['placement_cut'] = arg__dc['placement_cut'] if 'placement_cut' in arg__dc else False
        list__setdc['placement_loop'] = arg__dc['placement_loop'] if 'placement_loop' in arg__dc else []

        list__setdc['fxrack'] = arg__dc['fxrack'] if 'fxrack' in arg__dc else False
        list__setdc['fxrack_params'] = arg__dc['fxrack_params'] if 'fxrack_params' in arg__dc else ['vol','enabled']
        list__setdc['auto_nopl'] = arg__dc['auto_nopl'] if 'auto_nopl' in arg__dc else False

        list__setdc['time_seconds'] = arg__dc['time_seconds'] if 'time_seconds' in arg__dc else False
        list__setdc['placement_audio_stretch'] = arg__dc['placement_audio_stretch'] if 'placement_audio_stretch' in arg__dc else []

    print('[compat] '+str(in__dc['placement_cut']).ljust(5)+' | '+str(out__dc['placement_cut']).ljust(5)+' | placement_cut')
    print('[compat] '+str(in__dc['placement_loop']).ljust(5)+' | '+str(out__dc['placement_loop']).ljust(5)+' | placement_loop')

    print('[compat] '+str(in__dc['track_hybrid']).ljust(5)+' | '+str(out__dc['track_hybrid']).ljust(5)+' | track_hybrid')
    print('[compat] '+str(in__dc['track_lanes']).ljust(5)+' | '+str(out__dc['track_lanes']).ljust(5)+' | track_lanes')
    print('[compat] '+str(in__dc['track_nopl']).ljust(5)+' | '+str(out__dc['track_nopl']).ljust(5)+' | track_nopl')

    print('[compat] '+str(in__dc['fxrack']).ljust(5)+' | '+str(out__dc['fxrack']).ljust(5)+' | fxrack')
    print('[compat] '+str(in__dc['fxrack_params']).ljust(5)+' | '+str(out__dc['fxrack_params']).ljust(5)+' | fxrack_params')
    print('[compat] '+str(in__dc['auto_nopl']).ljust(5)+' | '+str(out__dc['auto_nopl']).ljust(5)+' | auto_nopl')

    print('[compat] '+str(in__dc['time_seconds']).ljust(5)+' | '+str(out__dc['time_seconds']).ljust(5)+' | time_seconds')
    print('[compat] '+str(in__dc['placement_audio_stretch']).ljust(5)+' | '+str(out__dc['placement_audio_stretch']).ljust(5)+' | placement_audio_stretch')

currenttime = None

def makecompat(cvpj_l, cvpj_type):
    global in__dc
    global out__dc
    global finished_processes
    global currenttime

    cvpj_proj = json.loads(cvpj_l)

    if currenttime == None: currenttime = in__dc['time_seconds']

    if 'time_seconds' in finished_processes: currenttime = out__dc['time_seconds']

    process_part('trackfx2fxrack', trackfx2fxrack,           cvpj_proj, cvpj_type,  in__dc['fxrack'], out__dc['fxrack'])
    process_part('fxrack2trackfx', fxrack2trackfx,           cvpj_proj, cvpj_type,  in__dc['fxrack'], out__dc['fxrack'])

    if in__dc['fxrack'] == out__dc['fxrack'] == True:
        process_part('fxrack_moveparams', fxrack_moveparams, cvpj_proj, cvpj_type,  in__dc['fxrack_params'], out__dc['fxrack_params'])

    process_part('changestretch', changestretch,             cvpj_proj, cvpj_type,  in__dc['placement_audio_stretch'], out__dc['placement_audio_stretch'])
    process_part('unhybrid', unhybrid,                       cvpj_proj, cvpj_type,  in__dc['track_hybrid'], out__dc['track_hybrid'])
    process_part('removelanes', removelanes,                 cvpj_proj, cvpj_type,  in__dc['track_lanes'], out__dc['track_lanes'])

    if currenttime == False:
        process_part('autopl_remove', autopl_remove,         cvpj_proj, cvpj_type,  in__dc['auto_nopl'], out__dc['auto_nopl'])
        process_part('trackpl_add', trackpl_add,             cvpj_proj, cvpj_type,  in__dc['track_nopl'], out__dc['track_nopl'])
        process_part('loops_remove', loops_remove,           cvpj_proj, cvpj_type,  in__dc['placement_loop'], out__dc['placement_loop'])
        process_part('removecut', removecut,                 cvpj_proj, cvpj_type,  in__dc['placement_cut'], out__dc['placement_cut'])
        process_part('loops_add', loops_add,                 cvpj_proj, cvpj_type,  in__dc['placement_loop'], out__dc['placement_loop'])

    process_part('time_seconds', time_seconds,               cvpj_proj, cvpj_type,  in__dc['time_seconds'], out__dc['time_seconds'])

    return json.dumps(cvpj_proj)

