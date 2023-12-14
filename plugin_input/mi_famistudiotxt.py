# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import shlex
import plugin_input
import json
from functions import placements
from functions import note_data
from functions import data_values
from functions import plugins
from functions import placement_data
from functions import song
from functions import xtramath
from functions import audio_wav

from functions_tracks import fxslot
from functions_tracks import fxrack
from functions_tracks import tracks_mi
from functions_tracks import tracks_master

dpcm_rate_arr = [4181.71,4709.93,5264.04,5593.04,6257.95,7046.35,7919.35,8363.42,9419.86,11186.1,12604.0,13982.6,16884.6,21306.8,24858.0,33143.9]

def get_used_insts(channeldata):
    usedinsts = []
    PatternList = channeldata['Patterns']
    for Pattern in PatternList:
        PatData = PatternList[Pattern]
        for Note in PatData:
            NoteData = PatData[Note]
            if 'Instrument' in NoteData:
                if NoteData['Instrument'] not in usedinsts:
                    usedinsts.append(NoteData['Instrument'])
    return usedinsts

def read_regs(cmd_params, startname, size):
    regdata = [None for x in range(size)]
    for regnum in range(size):
        regname = startname+str(regnum)
        if regname in cmd_params: regdata[regnum] = int(cmd_params[regname])
    return regdata

def decode_fst(infile):
    f_fst = open(infile, 'r')
    famistudiotxt_lines = f_fst.readlines()
      
    fst_Main = {}
    
    fst_instruments = {}
    fst_Arpeggios = {}
    fst_Songs = {}
    fst_DPCMSamples = {}
    fst_DPCMMappings = {}
    
    for line in famistudiotxt_lines:
        t_cmd = line.split(" ", 1)
        t_precmd = t_cmd[0]
        tabs_num = t_precmd.count('\t')
    
        cmd_name = t_precmd.split()[0]
        cmd_params = dict(token.split('=') for token in shlex.split(t_cmd[1]))
    
        #print(tabs_num, cmd_name, cmd_params)

        if cmd_name == 'Project' and tabs_num == 0: fst_Main = cmd_params
    
        elif cmd_name == 'DPCMSample' and tabs_num == 1:
            dpcm_data = bytes.fromhex(cmd_params['Data'])
            dpcm_data = ''.join(format(x, '08b') for x in dpcm_data)
            dpcm_name = cmd_params['Name']

            dpcm_samp = []
            dpcm_current = 0
            prev_val = 0

            for dpcm_part in dpcm_data:
                if dpcm_part == '1': dpcm_current += 1
                else: dpcm_current -= 1
                out_dpcm = dpcm_current/2 + prev_val/2
                dpcm_samp.append(out_dpcm)
                prev_val = dpcm_current

            samp_average = xtramath.average(dpcm_samp)
            dpcm_samp = [x-samp_average for x in dpcm_samp]

            normval = max(max(dpcm_samp),-min(dpcm_samp))/16

            dpcm_samp = [int(  xtramath.clamp( (x*2)+128,0,255)  ) for x in dpcm_samp]
            dpcm_proc = bytearray(dpcm_samp)

            fst_DPCMSamples[cmd_params['Name']] = dpcm_proc

        elif cmd_name == 'Instrument' and tabs_num == 1:
            instname = cmd_params['Name']
            fst_instruments[instname] = {}
            fst_Instrument = fst_instruments[instname]
            fst_Instrument['Name'] = cmd_params['Name']
            fst_Instrument['Envelopes'] = {}
            fst_Instrument['DPCMMapping'] = {}

            if 'N163WavePreset' in cmd_params: fst_Instrument['N163WavePreset'] = cmd_params['N163WavePreset']
            if 'N163WaveSize' in cmd_params: fst_Instrument['N163WaveSize'] = cmd_params['N163WaveSize']
            if 'N163WavePos' in cmd_params: fst_Instrument['N163WavePos'] = cmd_params['N163WavePos']
            if 'N163WaveCount' in cmd_params: fst_Instrument['N163WaveCount'] = cmd_params['N163WaveCount']

            if 'Vrc7Patch' in cmd_params: 
                if cmd_params['Vrc7Patch'] != '0': fst_Instrument['Vrc7Patch'] = cmd_params['Vrc7Patch']
                else: fst_Instrument['Vrc7Reg'] = read_regs(cmd_params, 'Vrc7Reg', 8)

            if 'EpsmPatch' in cmd_params: 
                fst_Instrument['EpsmReg'] = read_regs(cmd_params, 'EpsmReg', 31)

            #print(fst_Instrument)

        elif cmd_name == 'DPCMMapping' and tabs_num == 1:
            notekey = NoteToMidi(cmd_params['Note'])
            fst_DPCMMappings[notekey] = {}
            fst_DPCMMappings[notekey]['Sample'] = cmd_params['Sample']
            fst_DPCMMappings[notekey]['Pitch'] = cmd_params['Pitch']
            fst_DPCMMappings[notekey]['Loop'] = cmd_params['Loop']

        elif cmd_name == 'DPCMMapping' and tabs_num == 2:
            notekey = NoteToMidi(cmd_params['Note'])
            fst_instrument = fst_instruments[instname]['DPCMMapping']
            fst_instrument[notekey] = {}
            fst_instrument[notekey]['Sample'] = cmd_params['Sample']
            fst_instrument[notekey]['Pitch'] = cmd_params['Pitch']
            fst_instrument[notekey]['Loop'] = cmd_params['Loop']

        elif cmd_name == 'Arpeggio' and tabs_num == 1:
            arpname = cmd_params['Name']
            fst_Arpeggios[arpname] = cmd_params

        elif cmd_name == 'Envelope' and tabs_num == 2:
            envtype = cmd_params['Type']
            fst_Instrument['Envelopes'][envtype] = {}
            fst_Instrument['Envelopes'][envtype] = cmd_params

        elif cmd_name == 'Song' and tabs_num == 1:
            songname = cmd_params['Name']
            fst_Songs[songname] = cmd_params
            fst_Song = fst_Songs[songname]
            fst_Song['PatternCustomSettings'] = {}
            fst_Song['Channels'] = {}
    
        elif cmd_name == 'PatternCustomSettings' and tabs_num == 2:
            pattime = cmd_params['Time']
            fst_Song['PatternCustomSettings'][pattime] = cmd_params

        elif cmd_name == 'Channel' and tabs_num == 2:
            chantype = cmd_params['Type']
            fst_Song['Channels'][chantype] = {}
            fst_Channel = fst_Song['Channels'][chantype]
            fst_Channel['Instances'] = {}
            fst_Channel['Patterns'] = {}
    
        elif cmd_name == 'Pattern' and tabs_num == 3:
            patname = cmd_params['Name']
            fst_Channel['Patterns'][patname] = {}
            fst_Pattern = fst_Channel['Patterns'][patname]
    
        elif cmd_name == 'PatternInstance' and tabs_num == 3:
            pattime = cmd_params['Time']
            fst_Channel['Instances'][pattime] = cmd_params
    
        elif cmd_name == 'Note' and tabs_num == 4:
            notetime = cmd_params['Time']
            fst_Pattern[notetime] = cmd_params
    
        #else:
        #    print('unexpected command and/or wrong tabs:', cmd_name)
        #    exit()
    
    fst_Main['Instruments'] = fst_instruments
    fst_Main['Songs'] = fst_Songs
    fst_Main['Arpeggios'] = fst_Arpeggios
    fst_Main['DPCMSamples'] = fst_DPCMSamples
    fst_Main['DPCMMappings'] = fst_DPCMMappings
    return fst_Main

def add_envelope(inst_plugindata, fst_Instrument, cvpj_name, fst_name):
    if fst_name in fst_Instrument['Envelopes']:
        envdata = {}
        if fst_name == 'FDSWave':
            if 'Values' in fst_Instrument['Envelopes'][fst_name]: envdata['values'] = [int(i) for i in fst_Instrument['Envelopes'][fst_name]['Values'].split(',')]
            if 'Loop' in fst_Instrument['Envelopes'][fst_name]: envdata['loop'] = fst_Instrument['Envelopes'][fst_name]['Loop']
            if 'Release' in fst_Instrument['Envelopes'][fst_name]: envdata['release'] = fst_Instrument['Envelopes'][fst_name]['Release']
            inst_plugindata.dataval_add('wave', envdata)
        elif fst_name == 'N163Wave':
            envdata['loop'] = 0
            if 'Values' in fst_Instrument['Envelopes'][fst_name]: envdata['values'] = [int(i) for i in fst_Instrument['Envelopes'][fst_name]['Values'].split(',')]
            if 'Loop' in fst_Instrument['Envelopes'][fst_name]: envdata['loop'] = int(fst_Instrument['Envelopes'][fst_name]['Loop'])
            envdata['preset'] = fst_Instrument['N163WavePreset']
            envdata['size'] = int(fst_Instrument['N163WaveSize'])
            envdata['pos'] = int(fst_Instrument['N163WavePos'])
            envdata['count'] = int(fst_Instrument['N163WaveCount'])
            inst_plugindata.dataval_add('wave', envdata)

            waveids = []
            namco163_wave_chunks = data_values.list_chunks(envdata['values'], int(envdata['size']))
            for wavenum in range(len(namco163_wave_chunks)):
                wavedata = namco163_wave_chunks[wavenum]
                if len(wavedata) == int(envdata['size']):
                    inst_plugindata.wave_add(str(wavenum), wavedata, 0, 15)
                    waveids.append(str(wavenum))
            inst_plugindata.wavetable_add('N163', waveids, None, envdata['loop']/((envdata['size']*envdata['count'])-1))

        else:
            envdata_values = [int(i) for i in fst_Instrument['Envelopes'][fst_name]['Values'].split(',')]
            envdata_loop = None
            envdata_release = None
            if 'Loop' in fst_Instrument['Envelopes'][fst_name]: 
                envdata_loop = fst_Instrument['Envelopes'][fst_name]['Loop']
            if 'Release' in fst_Instrument['Envelopes'][fst_name]: 
                envdata_release = fst_Instrument['Envelopes'][fst_name]['Release']
            inst_plugindata.env_blocks_add(cvpj_name, envdata_values, 0.05, 15, envdata_loop, envdata_release)


def add_envelopes(inst_plugindata, fst_Instrument):
    if 'Envelopes' in fst_Instrument:
        add_envelope(inst_plugindata, fst_Instrument, 'vol', 'Volume')
        add_envelope(inst_plugindata, fst_Instrument, 'duty', 'DutyCycle')
        add_envelope(inst_plugindata, fst_Instrument, 'pitch', 'Pitch')

def create_inst(WaveType, fst_Instrument, fxrackchan):
    instname = fst_Instrument['Name']

    instvolume = 0.2
    instpan = 0

    pluginid = plugins.get_id()

    if WaveType == 'Square1' or WaveType == 'Square2' or WaveType == 'Triangle' or WaveType == 'Noise':
        if WaveType == 'Square1' or WaveType == 'Square2': wavetype = 'square'
        if WaveType == 'Triangle': wavetype = 'triangle'
        if WaveType == 'Noise': wavetype = 'noise'
        inst_plugindata = plugins.cvpj_plugin('deftype', 'universal', 'synth-osc')
        inst_plugindata.osc_num_oscs(1)
        inst_plugindata.osc_opparam_set(0, 'shape', wavetype)
        add_envelopes(inst_plugindata, fst_Instrument)
        inst_plugindata.to_cvpj(cvpj_l, pluginid)

    if WaveType == 'VRC7FM':
        inst_plugindata = plugins.cvpj_plugin('deftype', 'fm', 'vrc7')
        add_envelopes(inst_plugindata, fst_Instrument)
        instvolume = 1
        if 'Vrc7Patch' in fst_Instrument:
            inst_plugindata.dataval_add('use_patch', True)
            inst_plugindata.dataval_add('patch', int(fst_Instrument['Vrc7Patch']))
        else:
            inst_plugindata.dataval_add('use_patch', False)
            inst_plugindata.dataval_add('regs', fst_Instrument['Vrc7Reg'])
        inst_plugindata.to_cvpj(cvpj_l, pluginid)

    if WaveType == 'VRC6Square' or WaveType == 'VRC6Saw':
        if WaveType == 'VRC6Saw': wavetype = 'saw'
        if WaveType == 'VRC6Square': wavetype = 'square'
        inst_plugindata = plugins.cvpj_plugin('deftype', 'universal', 'synth-osc')
        inst_plugindata.osc_num_oscs(1)
        inst_plugindata.osc_opparam_set(0, 'shape', wavetype)
        add_envelopes(inst_plugindata, fst_Instrument)
        inst_plugindata.to_cvpj(cvpj_l, pluginid)

    if WaveType == 'FDS':
        inst_plugindata = plugins.cvpj_plugin('deftype', 'fds', None)
        add_envelopes(inst_plugindata, fst_Instrument)
        add_envelope(inst_plugindata, fst_Instrument, 'wave', 'FDSWave')
        inst_plugindata.to_cvpj(cvpj_l, pluginid)

    if WaveType == 'N163':
        instvolume = 1
        inst_plugindata = plugins.cvpj_plugin('deftype', 'namco163_famistudio', None)
        add_envelopes(inst_plugindata, fst_Instrument)
        add_envelope(inst_plugindata, fst_Instrument, 'wave', 'N163Wave')
        inst_plugindata.to_cvpj(cvpj_l, pluginid)

    if WaveType == 'S5B':
        inst_plugindata = plugins.cvpj_plugin('deftype', 'universal', 'synth-osc')
        inst_plugindata.osc_num_oscs(1)
        inst_plugindata.osc_opparam_set(0, 'shape', 'square')
        add_envelopes(inst_plugindata, fst_Instrument)
        inst_plugindata.to_cvpj(cvpj_l, pluginid)

    if WaveType == 'MMC5':
        inst_plugindata = plugins.cvpj_plugin('deftype', 'universal', 'synth-osc')
        inst_plugindata.osc_num_oscs(1)
        inst_plugindata.osc_opparam_set(0, 'shape', 'square')
        inst_plugindata.to_cvpj(cvpj_l, pluginid)

    if WaveType == 'EPSMSquare':
        inst_plugindata = plugins.cvpj_plugin('deftype', 'universal', 'synth-osc')
        inst_plugindata.osc_num_oscs(1)
        inst_plugindata.osc_opparam_set(0, 'shape', 'square')
        add_envelopes(inst_plugindata, fst_Instrument)
        inst_plugindata.to_cvpj(cvpj_l, pluginid)

    if WaveType == 'EPSMFM':
        instvolume = 0.7
        inst_plugindata = plugins.cvpj_plugin('deftype', 'fm', 'epsm')
        inst_plugindata.dataval_add('regs', fst_Instrument['EpsmReg'])
        instpan += int(bool(fst_Instrument['EpsmReg'][1] & 0x80))*-1
        instpan += int(bool(fst_Instrument['EpsmReg'][1] & 0x40))
        inst_plugindata.to_cvpj(cvpj_l, pluginid)

    if WaveType == 'EPSM_Kick': 
        inst_plugindata = plugins.cvpj_plugin('deftype', 'epsm_rhythm', 'kick')
        inst_plugindata.to_cvpj(cvpj_l, pluginid)
    if WaveType == 'EPSM_Snare': 
        inst_plugindata = plugins.cvpj_plugin('deftype', 'epsm_rhythm', 'snare')
        inst_plugindata.to_cvpj(cvpj_l, pluginid)
    if WaveType == 'EPSM_Cymbal': 
        inst_plugindata = plugins.cvpj_plugin('deftype', 'epsm_rhythm', 'cymbal')
        inst_plugindata.to_cvpj(cvpj_l, pluginid)
    if WaveType == 'EPSM_HiHat': 
        inst_plugindata = plugins.cvpj_plugin('deftype', 'epsm_rhythm', 'hihat')
        inst_plugindata.to_cvpj(cvpj_l, pluginid)
    if WaveType == 'EPSM_Tom': 
        inst_plugindata = plugins.cvpj_plugin('deftype', 'epsm_rhythm', 'tom')
        inst_plugindata.to_cvpj(cvpj_l, pluginid)
    if WaveType == 'EPSM_Rimshot': 
        inst_plugindata = plugins.cvpj_plugin('deftype', 'epsm_rhythm', 'rimshot')
        inst_plugindata.to_cvpj(cvpj_l, pluginid)


    #print('DATA ------------' , fst_Instrument)
    #print('OUT ------------' , plugname, cvpj_plugdata)

    inst_color = InstColors[WaveType]

    cvpj_instid = WaveType+'-'+instname

    tracks_mi.inst_create(cvpj_l, cvpj_instid)
    tracks_mi.inst_visual(cvpj_l, cvpj_instid, name=cvpj_instid, color=inst_color)
    tracks_mi.inst_pluginid(cvpj_l, cvpj_instid, pluginid)
    tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'vol', instvolume, 'float')
    tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'pan', instpan, 'float')
    tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'pitch', 0, 'float')
    tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'usemasterpitch', True, 'bool')

    if WaveType in ['EPSMFM', 'EPSMSquare']:
        tracks_mi.inst_dataval_add(cvpj_l, cvpj_instid, None, 'middlenote', 12)

    tracks_mi.inst_fxrackchan_add(cvpj_l, cvpj_instid, fxrackchan)

def create_dpcm_inst(DPCMMappings, DPCMSamples, fxrackchan, fst_instrument):
    global samplefolder
    global dpcm_rate_arr

    instname = fst_instrument['Name'] if fst_instrument != None else None
    inst_color = [0.48, 0.83, 0.49]
    cvpj_instid = 'DPCM-'+instname if instname != None else 'DPCM'

    pluginid = plugins.get_id()

    tracks_mi.inst_create(cvpj_l, cvpj_instid)
    tracks_mi.inst_visual(cvpj_l, cvpj_instid, name='DPCM', color= [0.48, 0.83, 0.49])
    tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'vol', 0.6, 'float')
    tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'pitch', 0, 'float')
    tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'usemasterpitch', False, 'bool')
    tracks_mi.inst_fxrackchan_add(cvpj_l, cvpj_instid, fxrackchan)
    inst_plugindata = plugins.cvpj_plugin('multisampler', None, None)

    for dpcmmap in DPCMMappings:
        dpcmdata = DPCMMappings[dpcmmap]
        dpcm_pitch = int(dpcmdata['Pitch'])
        dpcm_sample = dpcmdata['Sample']

        if dpcm_sample in DPCMSamples:
            if instname:
                filename = samplefolder+'dpcm_'+instname+'_'+dpcm_sample+'_'+str(dpcm_pitch)+'.wav'
            else:
                filename = samplefolder+'dpcmg_'+dpcm_sample+'_'+str(dpcm_pitch)+'.wav'
            audio_wav.generate(filename, DPCMSamples[dpcm_sample], 1, int(dpcm_rate_arr[dpcm_pitch]), 8, None)

            correct_key = dpcmmap+24

            regionparams = {}
            regionparams['name'] = dpcm_sample
            regionparams['r_key'] = [correct_key, correct_key]
            regionparams['middlenote'] = correct_key
            regionparams['file'] = filename
            inst_plugindata.region_add(regionparams)

    inst_plugindata.to_cvpj(cvpj_l, pluginid)
    tracks_mi.inst_pluginid(cvpj_l, cvpj_instid, pluginid)

def NoteToMidi(keytext):
    l_key = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    s_octave = (int(keytext[-1])-5)*12
    lenstr = len(keytext)
    if lenstr == 3: t_key = keytext[:-1]
    else: t_key = keytext[:-1]
    s_key = l_key.index(t_key)
    return s_key + s_octave

InstColors = {'Square1': [0.97, 0.56, 0.36],
            'Square2': [0.97, 0.56, 0.36],
            'Triangle': [0.94, 0.33, 0.58],
            'Noise': [0.33, 0.74, 0.90],
            'FDS': [0.94, 0.94, 0.65],
            'VRC7FM': [1.00, 0.46, 0.44],
            'VRC6Square': [0.60, 0.44, 0.93],
            'VRC6Saw': [0.46, 0.52, 0.91],
            'S5B': [0.58, 0.94, 0.33],
            'N163': [0.97, 0.97, 0.36],
            'MMC5': [0.65, 0.34, 0.84], 

            'EPSMSquare': [0.84, 0.84, 0.84], 
            
            'EPSMFM': [0.84, 0.84, 0.84], 

            'EPSM_Kick': [0.84, 0.84, 0.84], 
            'EPSM_Snare': [0.84, 0.84, 0.84], 
            'EPSM_Cymbal': [0.84, 0.84, 0.84], 
            'EPSM_HiHat': [0.84, 0.84, 0.84], 
            'EPSM_Tom': [0.84, 0.84, 0.84], 
            'EPSM_Rimshot': [0.84, 0.84, 0.84], 
            }

InstShapes = {'Square1': 'Square1', 
        'Square2': 'Square2', 
        'Triangle': 'Triangle', 
        'Noise': 'Noise', 

        'VRC6Square1': 'VRC6Square', 
        'VRC6Square2': 'VRC6Square', 
        'VRC6Saw': 'VRC6Saw', 

        'VRC7FM1': 'VRC7FM', 
        'VRC7FM2': 'VRC7FM', 
        'VRC7FM3': 'VRC7FM', 
        'VRC7FM4': 'VRC7FM', 
        'VRC7FM5': 'VRC7FM', 
        'VRC7FM6': 'VRC7FM', 

        'FDS': 'FDS', 

        'N163Wave1': 'N163', 
        'N163Wave2': 'N163', 
        'N163Wave3': 'N163', 
        'N163Wave4': 'N163', 

        'S5BSquare1': 'S5B', 
        'S5BSquare2': 'S5B', 
        'S5BSquare3': 'S5B',

        'MMC5Square1': 'MMC5', 
        'MMC5Square2': 'MMC5',

        'EPSMSquare1': 'EPSMSquare',
        'EPSMSquare2': 'EPSMSquare',
        'EPSMSquare3': 'EPSMSquare',

        'EPSMFM1': 'EPSMFM',
        'EPSMFM2': 'EPSMFM',
        'EPSMFM3': 'EPSMFM',
        'EPSMFM4': 'EPSMFM',
        'EPSMFM5': 'EPSMFM',
        'EPSMFM6': 'EPSMFM',

        'EPSMRythm1': 'EPSM_Kick',
        'EPSMRythm2': 'EPSM_Snare',
        'EPSMRythm3': 'EPSM_Cymbal',
        'EPSMRythm4': 'EPSM_HiHat',
        'EPSMRythm5': 'EPSM_Tom',
        'EPSMRythm6': 'EPSM_Rimshot',
        }


class input_famistudio(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'famistudio_txt'
    def getname(self): return 'FamiStudio Text'
    def gettype(self): return 'mi'
    def getdawcapabilities(self): 
        return {
        'samples_inside': True,
        'track_lanes': True,
        'auto_nopl': True,
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global cvpj_l
        global samplefolder

        samplefolder = extra_param['samplefolder']

        fst_Main = decode_fst(input_file)

        cvpj_l = {}
        
        fst_instruments = fst_Main['Instruments']
        fst_arpeggios = fst_Main['Arpeggios']

        songnamelist = list(fst_Main['Songs'].keys())

        #print(songnamelist)

        if 'songnum' in extra_param: fst_currentsong = fst_Main['Songs'][songnamelist[int(extra_param['songnum'])-1]]
        else: fst_currentsong = fst_Main['Songs'][songnamelist[0]]

        fst_channels = fst_currentsong['Channels']
        fst_beatlength = int(fst_currentsong['BeatLength'])
        fst_groove = fst_currentsong['Groove']

        PatternLength = int(fst_currentsong['PatternLength'])
        SongLength = int(fst_currentsong['Length'])
        NoteLength = int(fst_currentsong['NoteLength'])
        LoopPoint = int(fst_currentsong['LoopPoint'])
        DPCMMappings = fst_Main['DPCMMappings']
        DPCMSamples = fst_Main['DPCMSamples']

        groovetable = []
        groovesplit = fst_groove.split('-')
        for groovenumber in groovesplit:
            groovetable.append(int(groovenumber))
        bpm = 60/(xtramath.average(groovetable)/60*fst_beatlength)

        PatternLengthList = []
        for number in range(SongLength):
            if str(number) not in fst_currentsong['PatternCustomSettings']: PatternLengthList.append(PatternLength)
            else: PatternLengthList.append(int(fst_currentsong['PatternCustomSettings'][str(number)]['Length']))

        PointsPos = []
        PointsAdd = 0
        for number in range(SongLength):
            PointsPos.append(PointsAdd)
            PointsAdd += PatternLengthList[number]

        channum = 1
        for Channel in fst_channels:
            WaveType = None
            used_insts = get_used_insts(fst_channels[Channel])
            if Channel in InstShapes: WaveType = InstShapes[Channel]
            elif Channel == 'DPCM': 
                create_dpcm_inst(DPCMMappings, DPCMSamples, channum, None)
                for inst in used_insts:
                    create_dpcm_inst(fst_instruments[inst]['DPCMMapping'], DPCMSamples, channum, fst_instruments[inst])
                fxtrack_name = 'DPCM'
                fxtrack_color = [0.48, 0.83, 0.49]
            if WaveType != None:
                fxtrack_name = WaveType
                if WaveType == 'Square1': fxtrack_color = [0.97, 0.56, 0.36]
                if WaveType == 'Square2': fxtrack_color = [0.97, 0.56, 0.36]
                if WaveType == 'Triangle': fxtrack_color = [0.94, 0.33, 0.58]
                if WaveType == 'Noise': fxtrack_color = [0.33, 0.74, 0.90]
                if WaveType == 'FDS': fxtrack_color = [0.94, 0.94, 0.65]
                if WaveType == 'VRC7FM': fxtrack_color = [1.00, 0.46, 0.44]
                if WaveType == 'VRC6Square': fxtrack_color = [0.60, 0.44, 0.93]
                if WaveType == 'VRC6Saw': fxtrack_color = [0.46, 0.52, 0.91]
                if WaveType == 'S5B': fxtrack_color = [0.58, 0.94, 0.33]
                if WaveType == 'N163': fxtrack_color = [0.97, 0.97, 0.36]
                for inst in used_insts:
                    create_inst(WaveType, fst_instruments[inst], channum)

            fxrack.add(cvpj_l, channum, 1, 0, name=fxtrack_name, color=fxtrack_color)
            channum += 1

        playlistnum = 1
        for Channel in fst_channels:
            ChannelName = Channel
            tracks_mi.playlist_add(cvpj_l, playlistnum)
            tracks_mi.playlist_visual(cvpj_l, playlistnum, name=Channel, color=[0.13, 0.15, 0.16])
            Channel_Patterns = fst_channels[Channel]['Patterns']
            for Pattern in Channel_Patterns:
                t_patternnotelist = []
                for fst_note in Channel_Patterns[Pattern]:
                    notedata = Channel_Patterns[Pattern][fst_note]

                    if ChannelName != 'DPCM':
                        if 'Duration' in notedata and 'Instrument' in notedata:

                            t_instrument = InstShapes[Channel]+'-'+notedata['Instrument']
                            t_duration = int(notedata['Duration'])/NoteLength
                            t_position = int(notedata['Time'])/NoteLength
                            t_key = NoteToMidi(notedata['Value']) + 24

                            cvpj_multikeys = []
                            if 'Arpeggio' in notedata:
                                if notedata['Arpeggio'] in fst_arpeggios:
                                    cvpj_multikeys = fst_arpeggios[notedata['Arpeggio']]['Values'].split(',')
                                    cvpj_multikeys = [*set(cvpj_multikeys)]

                            cvpj_notemod = {}
                            if 'SlideTarget' in notedata:
                                t_slidenote = NoteToMidi(notedata['SlideTarget']) + 24
                                cvpj_notemod['slide'] = [{'position': 0, 'duration': t_duration, 'key': t_slidenote-t_key}]
                                cvpj_notemod['auto'] = {}

                                cvpj_notemod['auto']['pitch'] = [{'position': 0, 'value': 0}, {'position': t_duration, 'value': t_slidenote-t_key}]

                            if ChannelName[0:6] == 'EPSMFM': t_key -= 12

                            if cvpj_multikeys == []:
                                cvpj_note = note_data.mx_makenote(t_instrument, t_position, t_duration, t_key, None, None)
                                cvpj_note['notemod'] = cvpj_notemod
                                t_patternnotelist.append(cvpj_note)
                            else:
                                for cvpj_multikey in cvpj_multikeys:
                                    addkey = int(cvpj_multikey)
                                    cvpj_note = note_data.mx_makenote(t_instrument, t_position, t_duration, t_key+addkey, None, None)
                                    cvpj_note['notemod'] = cvpj_notemod
                                    t_patternnotelist.append(cvpj_note)

                    else:
                        if 'Duration' in notedata:
                            if 'Instrument' in notedata:
                                cvpj_note = note_data.mx_makenote('DPCM'+'-'+notedata['Instrument'], int(notedata['Time'])/NoteLength, int(notedata['Duration'])/NoteLength, NoteToMidi(notedata['Value'])+24, None, None)
                                t_patternnotelist.append(cvpj_note)
                            else:
                                cvpj_note = note_data.mx_makenote('DPCM', int(notedata['Time'])/NoteLength, int(notedata['Duration'])/NoteLength, NoteToMidi(notedata['Value'])+24, None, None)
                                t_patternnotelist.append(cvpj_note)

                cvpj_patternid = Channel+'-'+Pattern
                tracks_mi.notelistindex_add(cvpj_l, cvpj_patternid, t_patternnotelist)
                tracks_mi.notelistindex_visual(cvpj_l, cvpj_patternid, name=Pattern+' ('+Channel+')', color=[0.13, 0.15, 0.16])

            Channel_Instances = fst_channels[Channel]['Instances']
            durationnum = 0
            for fst_Placement in Channel_Instances:
                fst_PData = Channel_Instances[fst_Placement]
                fst_time = int(fst_PData['Time'])
                cvpj_l_placement = placement_data.makepl_n_mi(PointsPos[int(fst_time)], PatternLengthList[durationnum], Channel+'-'+fst_PData['Pattern'])
                tracks_mi.add_pl(cvpj_l, playlistnum, 'notes', cvpj_l_placement)
                durationnum += 1
            playlistnum += 1

        timesig = song.add_timesig_lengthbeat(cvpj_l, PatternLength, fst_beatlength)
        placements.make_timemarkers(cvpj_l, timesig, PatternLengthList, LoopPoint)
        if 'Name' in fst_Main: song.add_info(cvpj_l, 'title', fst_Main['Name'])
        if 'Author' in fst_Main: song.add_info(cvpj_l, 'author', fst_Main['Author'])

        cvpj_l['do_addloop'] = True
        
        cvpj_l['timesig'] = timesig
        song.add_param(cvpj_l, 'bpm', bpm)
        return json.dumps(cvpj_l)