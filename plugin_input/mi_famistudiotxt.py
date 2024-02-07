# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import shlex
import plugin_input
import json
from functions import data_values
from functions import xtramath
from functions import audio_wav

from objects import dv_dataset

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
            dpcm_data = ''.join(format(x, '08b')[::-1] for x in dpcm_data)

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

            if dpcm_samp:
                samp_average = xtramath.average(dpcm_samp)
                dpcm_samp = [x-samp_average for x in dpcm_samp]
                dpcm_samp = [x for x in dpcm_samp]
                normval = max( max(dpcm_samp),-min(dpcm_samp) )/128
                if normval == 0: normval = 1
                dpcm_samp = [int(  xtramath.clamp( (x*(1/normval))+128,0,255)  ) for x in dpcm_samp]
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

def add_envelope(plugin_obj, fst_Instrument, cvpj_name, fst_name):
    if fst_name in fst_Instrument['Envelopes']:
        f_env_data = fst_Instrument['Envelopes'][fst_name]
        envdata = {}
        if fst_name == 'FDSWave':
            if 'Values' in f_env_data: envdata['values'] = [int(i) for i in f_env_data['Values'].split(',')]
            if 'Loop' in f_env_data: envdata['loop'] = f_env_data['Loop']
            if 'Release' in f_env_data: envdata['release'] = f_env_data['Release']
            plugin_obj.datavals.add('wave', envdata)
        elif fst_name == 'N163Wave':
            envdata['loop'] = 0
            if 'Values' in f_env_data: envdata['values'] = [int(i) for i in f_env_data['Values'].split(',')]
            if 'Loop' in f_env_data: envdata['loop'] = int(f_env_data['Loop'])
            envdata['preset'] = fst_Instrument['N163WavePreset']
            envdata['size'] = int(fst_Instrument['N163WaveSize'])
            envdata['pos'] = int(fst_Instrument['N163WavePos'])
            envdata['count'] = int(fst_Instrument['N163WaveCount'])
            plugin_obj.datavals.add('wave', envdata)

            waveids = []
            namco163_wave_chunks = data_values.list_chunks(envdata['values'], int(envdata['size']))
            for wavenum in range(len(namco163_wave_chunks)):
                wavedata = namco163_wave_chunks[wavenum]
                if len(wavedata) == int(envdata['size']):
                    wave_obj = plugin_obj.wave_add(str(wavenum))
                    wave_obj.set_all_range(wavedata, 0, 15)
                    waveids.append(str(wavenum))
            plugin_obj.wavetable_add('N163', waveids, None, envdata['loop']/((envdata['size']*envdata['count'])-1))

        else:
            envdata_values = [int(i) for i in f_env_data['Values'].split(',')]
            envdata_loop = None
            envdata_release = None
            if 'Loop' in f_env_data: envdata_loop = f_env_data['Loop']
            if 'Release' in f_env_data: envdata_release = f_env_data['Release']
            plugin_obj.env_blocks_add(cvpj_name, envdata_values, 0.05, 15, envdata_loop, envdata_release)


def add_envelopes(plugin_obj, fst_Instrument):
    if 'Envelopes' in fst_Instrument:
        add_envelope(plugin_obj, fst_Instrument, 'vol', 'Volume')
        add_envelope(plugin_obj, fst_Instrument, 'duty', 'DutyCycle')
        add_envelope(plugin_obj, fst_Instrument, 'pitch', 'Pitch')

def create_inst(convproj_obj, WaveType, fst_Instrument, fxchannel_obj, fx_num):
    instname = fst_Instrument['Name']

    cvpj_instid = WaveType+'-'+instname
    inst_obj = convproj_obj.add_instrument(cvpj_instid)
    inst_obj.fxrack_channel = fx_num
    inst_obj.params.add('vol', 0.2, 'float')

    if WaveType == 'Square1' or WaveType == 'Square2' or WaveType == 'Triangle' or WaveType == 'Noise':
        if WaveType == 'Square1' or WaveType == 'Square2': wavetype = 'square'
        if WaveType == 'Triangle': wavetype = 'triangle'
        if WaveType == 'Noise': wavetype = 'noise'
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
        osc_data = plugin_obj.osc_add()
        osc_data.shape = wavetype
        add_envelopes(plugin_obj, fst_Instrument)

    if WaveType == 'VRC7FM':
        inst_obj.params.add('vol', 1, 'float')
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('fm', 'vrc7')
        add_envelopes(plugin_obj, fst_Instrument)
        if 'Vrc7Patch' in fst_Instrument:
            plugin_obj.datavals.add('use_patch', True)
            plugin_obj.datavals.add('patch', int(fst_Instrument['Vrc7Patch']))
        else:
            plugin_obj.datavals.add('use_patch', False)
            plugin_obj.datavals.add('regs', fst_Instrument['Vrc7Reg'])

    if WaveType == 'VRC6Square' or WaveType == 'VRC6Saw':
        if WaveType == 'VRC6Saw': wavetype = 'saw'
        if WaveType == 'VRC6Square': wavetype = 'square'
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
        osc_data = plugin_obj.osc_add()
        osc_data.shape = wavetype
        add_envelopes(plugin_obj, fst_Instrument)

    if WaveType == 'FDS':
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('fds', None)
        add_envelopes(plugin_obj, fst_Instrument)
        add_envelope(plugin_obj, fst_Instrument, 'wave', 'FDSWave')

    if WaveType == 'N163':
        inst_obj.params.add('vol', 1, 'float')
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('namco163_famistudio', None)
        add_envelopes(plugin_obj, fst_Instrument)
        add_envelope(plugin_obj, fst_Instrument, 'wave', 'N163Wave')

    if WaveType == 'S5B':
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
        osc_data = plugin_obj.osc_add()
        osc_data.shape = 'square'
        add_envelopes(plugin_obj, fst_Instrument)

    if WaveType == 'MMC5':
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
        osc_data = plugin_obj.osc_add()
        osc_data.shape = 'square'

    if WaveType == 'EPSMSquare':
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
        osc_data = plugin_obj.osc_add()
        osc_data.shape = 'square'
        add_envelopes(plugin_obj, fst_Instrument)

    if WaveType == 'EPSMFM':
        instvolume = 0.7
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('fm', 'epsm')
        plugin_obj.datavals.add('regs', fst_Instrument['EpsmReg'])
        instpan = 0
        instpan += int(bool(fst_Instrument['EpsmReg'][1] & 0x80))*-1
        instpan += int(bool(fst_Instrument['EpsmReg'][1] & 0x40))
        inst_obj.params.add('pan', instpan, 'float')

    if WaveType == 'EPSM_Kick': 
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('epsm_rhythm', 'kick')
    if WaveType == 'EPSM_Snare': 
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('epsm_rhythm', 'snare')
    if WaveType == 'EPSM_Cymbal': 
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('epsm_rhythm', 'cymbal')
    if WaveType == 'EPSM_HiHat': 
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('epsm_rhythm', 'hihat')
    if WaveType == 'EPSM_Tom': 
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('epsm_rhythm', 'tom')
    if WaveType == 'EPSM_Rimshot': 
        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('epsm_rhythm', 'rimshot')

    #print('DATA ------------' , fst_Instrument)
    #print('OUT ------------' , plugname, cvpj_plugdata)

    _, inst_color = dataset.object_get_name_color('chip', WaveType)

    inst_obj.visual.name = instname
    inst_obj.visual.color = inst_color

    if WaveType in ['EPSMFM', 'EPSMSquare']: inst_obj.datavals.add('middlenote', 12)

def create_dpcm_inst(DPCMMappings, DPCMSamples, fx_num, fst_instrument):
    global samplefolder
    global dpcm_rate_arr

    instname = fst_instrument['Name'] if fst_instrument != None else None
    cvpj_instid = 'DPCM-'+instname if instname != None else 'DPCM'

    inst_obj = convproj_obj.add_instrument(cvpj_instid)
    inst_obj.params.add('vol', 0.6, 'float')
    inst_obj.params.add('usemasterpitch', False, 'bool')
    _, inst_obj.visual.color = dataset.object_get_name_color('chip', 'DPCM')
    inst_obj.visual.name = 'DPCM'
    inst_obj.fxrack_channel = fx_num
    plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('sampler', 'multi')

    for dpcmmap in DPCMMappings:
        dpcmdata = DPCMMappings[dpcmmap]
        dpcm_pitch = int(dpcmdata['Pitch'])
        dpcm_sample = dpcmdata['Sample']

        if dpcm_sample in DPCMSamples:
            if instname: filename = samplefolder+'dpcm_'+instname+'_'+dpcm_sample+'_'+str(dpcm_pitch)+'.wav'
            else: filename = samplefolder+'dpcmg_'+dpcm_sample+'_'+str(dpcm_pitch)+'.wav'
            audio_wav.generate(filename, DPCMSamples[dpcm_sample], 1, int(dpcm_rate_arr[dpcm_pitch]), 8, None)
            correct_key = dpcmmap+24
            sampleref_obj = convproj_obj.add_sampleref(filename, filename)
            regionparams = {}
            regionparams['name'] = dpcm_sample
            regionparams['middlenote'] = correct_key
            regionparams['sampleref'] = filename
            plugin_obj.regions.add(correct_key, correct_key, regionparams)

def NoteToMidi(keytext):
    l_key = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    s_octave = (int(keytext[-1])-5)*12
    lenstr = len(keytext)
    if lenstr == 3: t_key = keytext[:-1]
    else: t_key = keytext[:-1]
    s_key = l_key.index(t_key)
    return s_key + s_octave

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
    def parse(self, i_convproj_obj, input_file, extra_param):
        global samplefolder
        global dataset
        global convproj_obj
        convproj_obj = i_convproj_obj

        convproj_obj.type = 'mi'
        convproj_obj.set_timings(4, True)

        samplefolder = extra_param['samplefolder']
        fst_Main = decode_fst(input_file)
        dataset = dv_dataset.dataset('./data_dset/famistudio.dset')
        
        fst_instruments = fst_Main['Instruments']
        fst_arpeggios = fst_Main['Arpeggios']
        DPCMMappings = fst_Main['DPCMMappings']
        DPCMSamples = fst_Main['DPCMSamples']
        songnamelist = list(fst_Main['Songs'].keys())
        if 'songnum' in extra_param: fst_currentsong = fst_Main['Songs'][songnamelist[int(extra_param['songnum'])-1]]
        else: fst_currentsong = fst_Main['Songs'][songnamelist[0]]

        fst_channels = fst_currentsong['Channels']
        fst_beatlength = int(fst_currentsong['BeatLength'])
        fst_groove = fst_currentsong['Groove']
        PatternLength = int(fst_currentsong['PatternLength'])
        SongLength = int(fst_currentsong['Length'])
        NoteLength = int(fst_currentsong['NoteLength'])
        LoopPoint = int(fst_currentsong['LoopPoint'])

        groovetable = [int(x) for x in fst_groove.split('-')]
        bpm = 60/(xtramath.average(groovetable)/60*fst_beatlength)

        PatternLengthList = []
        for number in range(SongLength):
            f_pcs = fst_currentsong['PatternCustomSettings']
            PatternLengthList.append(PatternLength if str(number) not in f_pcs else int(f_pcs[str(number)]['Length']))

        PointsPos = []
        PointsAdd = 0
        for number in range(SongLength):
            PointsPos.append(PointsAdd)
            PointsAdd += PatternLengthList[number]

        channum = 1
        for Channel in fst_channels:
            WaveType = InstShapes[Channel] if Channel in InstShapes else 'DPCM'
            used_insts = get_used_insts(fst_channels[Channel])
            fxchannel_obj = convproj_obj.add_fxchan(channum)

            if WaveType != 'DPCM':
                fxchannel_obj.visual.name, fxchannel_obj.visual.color = dataset.object_get_name_color('chip', WaveType)
                for inst in used_insts: create_inst(convproj_obj, WaveType, fst_instruments[inst], fxchannel_obj, channum)
            
            else: 
                create_dpcm_inst(DPCMMappings, DPCMSamples, channum, None)
                for inst in used_insts: create_dpcm_inst(fst_instruments[inst]['DPCMMapping'], DPCMSamples, channum, fst_instruments[inst])
                fxchannel_obj.visual.name, fxchannel_obj.visual.color = dataset.object_get_name_color('chip', 'DPCM')
            channum += 1

        for playlistnum, Channel in enumerate(fst_channels):
            ChannelName = Channel
            playlist_obj = convproj_obj.add_playlist(playlistnum, 1, True)
            playlist_obj.visual.name = Channel
            playlist_obj.visual.color = [0.13, 0.15, 0.16]

            Channel_Patterns = fst_channels[Channel]['Patterns']
            for pattern_id in Channel_Patterns:
                nle_obj = convproj_obj.add_notelistindex(Channel+'-'+pattern_id)
                nle_obj.visual.name = pattern_id+' ('+Channel+')'
                nle_obj.visual.color = [0.13, 0.15, 0.16]

                for fst_note in Channel_Patterns[pattern_id]:
                    notedata = Channel_Patterns[pattern_id][fst_note]

                    if 'Duration' in notedata:
                        t_duration = int(notedata['Duration'])/NoteLength
                        t_position = int(notedata['Time'])/NoteLength
                        t_key = NoteToMidi(notedata['Value'])+24
                        if ChannelName != 'DPCM':
                            if 'Instrument' in notedata:
                                t_instrument = InstShapes[Channel]+'-'+notedata['Instrument']
                                cvpj_multikeys = []
                                if 'Arpeggio' in notedata:
                                    if notedata['Arpeggio'] in fst_arpeggios:
                                        cvpj_multikeys = fst_arpeggios[notedata['Arpeggio']]['Values'].split(',')
                                        cvpj_multikeys = [*set(cvpj_multikeys)]

                                if ChannelName[0:6] == 'EPSMFM': t_key -= 12

                                if cvpj_multikeys == []: nle_obj.notelist.add_m(t_instrument, t_position, t_duration, t_key, 1, {})
                                else: nle_obj.notelist.add_m_multi(t_instrument, t_position, t_duration, [t_key+int(x) for x in cvpj_multikeys], 1, {})

                                if 'SlideTarget' in notedata:
                                    t_slidenote = NoteToMidi(notedata['SlideTarget']) + 24
                                    nle_obj.notelist.last_add_slide(0, t_duration, t_slidenote-t_key, None, None)
                                    nle_obj.notelist.last_add_auto('pitch', 0, 0, 'normal', 0)
                                    nle_obj.notelist.last_add_auto('pitch', t_duration, t_slidenote-t_key, 'normal', 0)

                        else:
                            if 'Instrument' in notedata: nle_obj.notelist.add_m('DPCM'+'-'+notedata['Instrument'], t_position, t_duration, t_key, 1, {})
                            else: nle_obj.notelist.add_m('DPCM', t_position, t_duration, t_key, 1, {})

            Channel_Instances = fst_channels[Channel]['Instances']

            for durationnum, fst_Placement in enumerate(Channel_Instances):
                fst_PData = Channel_Instances[fst_Placement]
                fst_time = int(fst_PData['Time'])

                cvpj_placement = playlist_obj.placements.add_notes()
                cvpj_placement.fromindex = Channel+'-'+fst_PData['Pattern']
                cvpj_placement.position = int(fst_PData['Time'])*(fst_beatlength*4)
                cvpj_placement.duration = PatternLengthList[durationnum]

        convproj_obj.add_timesig_lengthbeat(PatternLength, fst_beatlength)
        convproj_obj.patlenlist_to_timemarker(PatternLengthList, LoopPoint)

        if 'Name' in fst_Main: convproj_obj.metadata.name = fst_Main['Name']
        if 'Author' in fst_Main: convproj_obj.metadata.author = fst_Main['Author']

        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.params.add('bpm', bpm, 'float')