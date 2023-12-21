# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import song
from functions import notelist_data
from functions import data_values
from functions import xtramath
from functions import params
from functions import audio

from functions_compat import fxrack2trackfx
from functions_compat import trackfx2fxrack

from functions_compat import autopl_remove
from functions_compat import changestretch
from functions_compat import fxrack_moveparams
from functions_compat import loops_add
from functions_compat import loops_remove
from functions_compat import removecut
from functions_compat import removelanes
from functions_compat import time_seconds
from functions_compat import timesigblocks
from functions_compat import trackpl_add
from functions_compat import unhybrid
from functions_compat import sep_nest_audio

import json
import math


class song_compat:
    def __init__(self):
        self.finished_processes = []
        self.in__dc = {}
        self.out__dc = {}
        self.currenttime = None

    def process_part(self, process_name, classname, cvpj_d, cvpj_type, in_compat, out_compat):
        if process_name not in self.finished_processes:
            if classname.process(cvpj_d, cvpj_type, in_compat, out_compat):
                print('[compat] ' + process_name, 'Done.')
                self.finished_processes.append(process_name)

    def set_dawcapabilities(self, in_dawcapabilities, out_dawcapabilities):
        for list__setdc, arg__dc in [[self.in__dc,in_dawcapabilities],[self.out__dc,out_dawcapabilities]]:
            list__setdc['track_lanes'] = arg__dc['track_lanes'] if 'track_lanes' in arg__dc else False
            list__setdc['track_nopl'] = arg__dc['track_nopl'] if 'track_nopl' in arg__dc else False
            list__setdc['track_hybrid'] = arg__dc['track_hybrid'] if 'track_hybrid' in arg__dc else False
    
            list__setdc['placement_cut'] = arg__dc['placement_cut'] if 'placement_cut' in arg__dc else False
            list__setdc['placement_loop'] = arg__dc['placement_loop'] if 'placement_loop' in arg__dc else []
            list__setdc['placement_audio_nested'] = arg__dc['placement_audio_nested'] if 'placement_audio_nested' in arg__dc else False
    
            list__setdc['fxrack'] = arg__dc['fxrack'] if 'fxrack' in arg__dc else False
            list__setdc['fxrack_params'] = arg__dc['fxrack_params'] if 'fxrack_params' in arg__dc else ['vol','enabled']
            list__setdc['auto_nopl'] = arg__dc['auto_nopl'] if 'auto_nopl' in arg__dc else False
    
            list__setdc['time_seconds'] = arg__dc['time_seconds'] if 'time_seconds' in arg__dc else False
            list__setdc['placement_audio_stretch'] = arg__dc['placement_audio_stretch'] if 'placement_audio_stretch' in arg__dc else []
    
        print('[compat] '+str(self.in__dc['placement_audio_nested']).ljust(5)+' | '+str(self.out__dc['placement_audio_nested']).ljust(5)+' | placement_audio_nested')
        print('[compat] '+str(self.in__dc['placement_cut']).ljust(5)+' | '+str(self.out__dc['placement_cut']).ljust(5)+' | placement_cut')
        print('[compat] '+str(self.in__dc['placement_loop']).ljust(5)+' | '+str(self.out__dc['placement_loop']).ljust(5)+' | placement_loop')
    
        print('[compat] '+str(self.in__dc['track_hybrid']).ljust(5)+' | '+str(self.out__dc['track_hybrid']).ljust(5)+' | track_hybrid')
        print('[compat] '+str(self.in__dc['track_lanes']).ljust(5)+' | '+str(self.out__dc['track_lanes']).ljust(5)+' | track_lanes')
        print('[compat] '+str(self.in__dc['track_nopl']).ljust(5)+' | '+str(self.out__dc['track_nopl']).ljust(5)+' | track_nopl')
    
        print('[compat] '+str(self.in__dc['fxrack']).ljust(5)+' | '+str(self.out__dc['fxrack']).ljust(5)+' | fxrack')
        print('[compat] '+str(self.in__dc['fxrack_params']).ljust(5)+' | '+str(self.out__dc['fxrack_params']).ljust(5)+' | fxrack_params')
        print('[compat] '+str(self.in__dc['auto_nopl']).ljust(5)+' | '+str(self.out__dc['auto_nopl']).ljust(5)+' | auto_nopl')
    
        print('[compat] '+str(self.in__dc['time_seconds']).ljust(5)+' | '+str(self.out__dc['time_seconds']).ljust(5)+' | time_seconds')
        print('[compat] '+str(self.in__dc['placement_audio_stretch']).ljust(5)+' | '+str(self.out__dc['placement_audio_stretch']).ljust(5)+' | placement_audio_stretch')

    def makecompat(self, cvpj_l, cvpj_type):
        cvpj_d = json.loads(cvpj_l)
    
        if self.currenttime == None: self.currenttime = self.in__dc['time_seconds']
    
        if 'time_seconds' in self.finished_processes: self.currenttime = self.out__dc['time_seconds']
    
        self.process_part('trackfx2fxrack', trackfx2fxrack,           cvpj_d, cvpj_type,  self.in__dc['fxrack'], self.out__dc['fxrack'])
        self.process_part('fxrack2trackfx', fxrack2trackfx,           cvpj_d, cvpj_type,  self.in__dc['fxrack'], self.out__dc['fxrack'])
    
        if self.in__dc['fxrack'] == self.out__dc['fxrack'] == True:
            self.process_part('fxrack_moveparams', fxrack_moveparams, cvpj_d, cvpj_type,  self.in__dc['fxrack_params'], self.out__dc['fxrack_params'])
    
        self.process_part('changestretch', changestretch,             cvpj_d, cvpj_type,  self.in__dc['placement_audio_stretch'], self.out__dc['placement_audio_stretch'])
        self.process_part('unhybrid', unhybrid,                       cvpj_d, cvpj_type,  self.in__dc['track_hybrid'], self.out__dc['track_hybrid'])
        self.process_part('removelanes', removelanes,                 cvpj_d, cvpj_type,  self.in__dc['track_lanes'], self.out__dc['track_lanes'])
    
        if self.currenttime == False:
            self.process_part('autopl_remove', autopl_remove,         cvpj_d, cvpj_type,  self.in__dc['auto_nopl'], self.out__dc['auto_nopl'])
            self.process_part('trackpl_add', trackpl_add,             cvpj_d, cvpj_type,  self.in__dc['track_nopl'], self.out__dc['track_nopl'])
            self.process_part('loops_remove', loops_remove,           cvpj_d, cvpj_type,  self.in__dc['placement_loop'], self.out__dc['placement_loop'])
            self.process_part('removecut', removecut,                 cvpj_d, cvpj_type,  self.in__dc['placement_cut'], self.out__dc['placement_cut'])
            self.process_part('sep_nest_audio', sep_nest_audio,       cvpj_d, cvpj_type,  self.in__dc['placement_audio_nested'], self.out__dc['placement_audio_nested'])
            self.process_part('loops_add', loops_add,                 cvpj_d, cvpj_type,  self.in__dc['placement_loop'], self.out__dc['placement_loop'])
    
        self.process_part('time_seconds', time_seconds,               cvpj_d, cvpj_type,  self.in__dc['time_seconds'], self.out__dc['time_seconds'])
    
        return json.dumps(cvpj_d)