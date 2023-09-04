# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import shlex
import plugin_input
import json
from functions import placements
from functions import note_data
from functions import data_values
from functions import tracks
from functions import plugins
from functions import placement_data
from functions import song

def average(lst):
    return sum(lst) / len(lst)

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
            fst_DPCMSamples[cmd_params['Name']] = cmd_params['Data']
        elif cmd_name == 'DPCMMapping' and tabs_num == 1:
            mapnote = cmd_params['Note']
            fst_DPCMMappings[mapnote] = {}
            fst_DPCMMappings[mapnote]['Sample'] = cmd_params['Sample']
            fst_DPCMMappings[mapnote]['Pitch'] = cmd_params['Pitch']
            fst_DPCMMappings[mapnote]['Loop'] = cmd_params['Loop']
    
        elif cmd_name == 'Instrument' and tabs_num == 1:
            instname = cmd_params['Name']
            fst_instruments[instname] = {}
            fst_Instrument = fst_instruments[instname]
            fst_Instrument['Name'] = cmd_params['Name']
            fst_Instrument['Envelopes'] = {}
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

def add_envelope(pluginid, fst_Instrument, cvpj_name, fst_name):
    if fst_name in fst_Instrument['Envelopes']:
        envdata = {}
        if fst_name == 'FDSWave':
            if 'Values' in fst_Instrument['Envelopes'][fst_name]: envdata['values'] = [int(i) for i in fst_Instrument['Envelopes'][fst_name]['Values'].split(',')]
            if 'Loop' in fst_Instrument['Envelopes'][fst_name]: envdata['loop'] = fst_Instrument['Envelopes'][fst_name]['Loop']
            if 'Release' in fst_Instrument['Envelopes'][fst_name]: envdata['release'] = fst_Instrument['Envelopes'][fst_name]['Release']
            plugins.add_plug_data(cvpj_l, pluginid, 'wave', envdata)
        elif fst_name == 'N163Wave':
            envdata['loop'] = 0
            if 'Values' in fst_Instrument['Envelopes'][fst_name]: envdata['values'] = [int(i) for i in fst_Instrument['Envelopes'][fst_name]['Values'].split(',')]
            if 'Loop' in fst_Instrument['Envelopes'][fst_name]: envdata['loop'] = int(fst_Instrument['Envelopes'][fst_name]['Loop'])
            envdata['preset'] = fst_Instrument['N163WavePreset']
            envdata['size'] = int(fst_Instrument['N163WaveSize'])
            envdata['pos'] = int(fst_Instrument['N163WavePos'])
            envdata['count'] = int(fst_Instrument['N163WaveCount'])
            plugins.add_plug_data(cvpj_l, pluginid, 'wave', envdata)

            waveids = []
            namco163_wave_chunks = data_values.list_chunks(envdata['values'], int(envdata['size']))
            for wavenum in range(len(namco163_wave_chunks)):
                wavedata = namco163_wave_chunks[wavenum]
                if len(wavedata) == int(envdata['size']):
                    plugins.add_wave(cvpj_l, pluginid, str(wavenum), wavedata, 0, 15)
                    waveids.append(str(wavenum))
            plugins.add_wavetable(cvpj_l, pluginid, 'N163', waveids, None, envdata['loop']/((envdata['size']*envdata['count'])-1))

        else:
            envdata_values = [int(i) for i in fst_Instrument['Envelopes'][fst_name]['Values'].split(',')]
            envdata_loop = None
            envdata_release = None
            if 'Loop' in fst_Instrument['Envelopes'][fst_name]: 
                envdata_loop = fst_Instrument['Envelopes'][fst_name]['Loop']
            if 'Release' in fst_Instrument['Envelopes'][fst_name]: 
                envdata_release = fst_Instrument['Envelopes'][fst_name]['Release']
            plugins.add_env_blocks(cvpj_l, pluginid, cvpj_name, envdata_values, 15, envdata_loop, envdata_release)


def add_envelopes(pluginid, fst_Instrument):
    if 'Envelopes' in fst_Instrument:
        add_envelope(pluginid, fst_Instrument, 'vol', 'Volume')
        add_envelope(pluginid, fst_Instrument, 'duty', 'DutyCycle')
        add_envelope(pluginid, fst_Instrument, 'pitch', 'Pitch')

def create_inst(WaveType, fst_Instrument, fxrack_channel):
    instname = fst_Instrument['Name']

    instvolume = 0.2
    instpan = 0

    pluginid = plugins.get_id()

    if WaveType == 'Square1' or WaveType == 'Square2' or WaveType == 'Triangle' or WaveType == 'Noise':
        if WaveType == 'Square1' or WaveType == 'Square2': wavetype = 'square'
        if WaveType == 'Triangle': wavetype = 'triangle'
        if WaveType == 'Noise': wavetype = 'noise'
        plugins.add_plug(cvpj_l, pluginid, 'retro', wavetype)
        add_envelopes(pluginid, fst_Instrument)

    if WaveType == 'VRC7FM':
        plugins.add_plug(cvpj_l, pluginid, 'fm', 'vrc7')
        add_envelopes(pluginid, fst_Instrument)
        instvolume = 1
        if 'Vrc7Patch' in fst_Instrument:
            plugins.add_plug_data(cvpj_l, pluginid, 'use_patch', True)
            plugins.add_plug_data(cvpj_l, pluginid, 'patch', int(fst_Instrument['Vrc7Patch']))
        else:
            plugins.add_plug_data(cvpj_l, pluginid, 'use_patch', False)
            plugins.add_plug_data(cvpj_l, pluginid, 'regs', fst_Instrument['Vrc7Reg'])

    if WaveType == 'VRC6Square' or WaveType == 'VRC6Saw':
        if WaveType == 'VRC6Saw': wavetype = 'saw'
        if WaveType == 'VRC6Square': wavetype = 'square'
        plugins.add_plug(cvpj_l, pluginid, 'retro', wavetype)
        add_envelopes(pluginid, fst_Instrument)

    if WaveType == 'FDS':
        plugins.add_plug(cvpj_l, pluginid, 'fds', None)
        add_envelopes(pluginid, fst_Instrument)
        add_envelope(pluginid, fst_Instrument, 'wave', 'FDSWave')

    if WaveType == 'N163':
        instvolume = 1
        plugins.add_plug(cvpj_l, pluginid, 'namco163_famistudio', None)
        add_envelopes(pluginid, fst_Instrument)
        add_envelope(pluginid, fst_Instrument, 'wave', 'N163Wave')

    if WaveType == 'S5B':
        plugins.add_plug(cvpj_l, pluginid, 'sunsoft_5b', None)
        add_envelopes(pluginid, fst_Instrument)

    if WaveType == 'MMC5':
        plugins.add_plug(cvpj_l, pluginid, 'mmc5', None)

    if WaveType == 'EPSMSquare':
        plugins.add_plug(cvpj_l, pluginid, 'epsm_square', None)
        add_envelopes(pluginid, fst_Instrument)

    if WaveType == 'EPSMFM':
        instvolume = 0.7
        plugins.add_plug(cvpj_l, pluginid, 'fm', 'epsm')
        plugins.add_plug_data(cvpj_l, pluginid, 'regs', fst_Instrument['EpsmReg'])
        instpan += int(bool(fst_Instrument['EpsmReg'][1] & 0x80))*-1
        instpan += int(bool(fst_Instrument['EpsmReg'][1] & 0x40))

    if WaveType == 'EPSM_Kick':
        plugins.add_plug(cvpj_l, pluginid, 'epsm_rhythm', 'kick')

    if WaveType == 'EPSM_Snare':
        plugins.add_plug(cvpj_l, pluginid, 'epsm_rhythm', 'snare')

    if WaveType == 'EPSM_Cymbal':
        plugins.add_plug(cvpj_l, pluginid, 'epsm_rhythm', 'cymbal')

    if WaveType == 'EPSM_HiHat':
        plugins.add_plug(cvpj_l, pluginid, 'epsm_rhythm', 'hihat')

    if WaveType == 'EPSM_Tom':
        plugins.add_plug(cvpj_l, pluginid, 'epsm_rhythm', 'tom')

    if WaveType == 'EPSM_Rimshot':
        plugins.add_plug(cvpj_l, pluginid, 'epsm_rhythm', 'rimshot')

    #print('DATA ------------' , fst_Instrument)
    #print('OUT ------------' , plugname, cvpj_plugdata)

    inst_color = InstColors[WaveType]

    cvpj_instid = WaveType+'-'+instname

    tracks.m_inst_create(cvpj_l, cvpj_instid, name=cvpj_instid, color=inst_color)
    tracks.m_inst_pluginid(cvpj_l, cvpj_instid, pluginid)
    tracks.m_inst_add_param(cvpj_l, cvpj_instid, 'vol', instvolume, 'float')
    tracks.m_inst_add_param(cvpj_l, cvpj_instid, 'pan', instpan, 'float')
    tracks.m_inst_add_param(cvpj_l, cvpj_instid, 'pitch', 0, 'float')
    tracks.m_inst_add_param(cvpj_l, cvpj_instid, 'usemasterpitch', True, 'bool')

    if WaveType in ['EPSMFM', 'EPSMSquare']:
        tracks.m_inst_add_dataval(cvpj_l, cvpj_instid, None, 'middlenote', 12)

    tracks.m_inst_add_dataval(cvpj_l, cvpj_instid, None, 'fxrack_channel', fxrack_channel)


def create_dpcm_inst(DPCMMappings, DPCMSamples, fxrack_channel):
    tracks.m_inst_create(cvpj_l, 'DPCM', name='DPCM', color= [0.48, 0.83, 0.49])
    tracks.m_inst_add_param(cvpj_l, 'DPCM', 'vol', 0.6, 'float')
    tracks.m_inst_add_param(cvpj_l, 'DPCM', 'pitch', 0, 'float')
    tracks.m_inst_add_param(cvpj_l, 'DPCM', 'usemasterpitch', False, 'bool')
    tracks.m_inst_add_dataval(cvpj_l, 'DPCM', None, 'fxrack_channel', fxrack_channel)

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
        'fxrack': False,
        'track_lanes': True,
        'placement_cut': False,
        'placement_loop': False,
        'auto_nopl': True,
        'track_nopl': False
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global cvpj_l
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
        bpm = 60/(average(groovetable)/60*fst_beatlength)

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
                create_dpcm_inst(DPCMMappings, DPCMSamples, channum)
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

            tracks.fxrack_add(cvpj_l, channum, fxtrack_name, fxtrack_color, 1, 0)
            channum += 1

        playlistnum = 1
        for Channel in fst_channels:
            ChannelName = Channel
            tracks.m_playlist_pl(cvpj_l, playlistnum, Channel, [0.13, 0.15, 0.16], [])
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

                            if ChannelName[0:4] == 'VRC7': t_key -= 24

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
                            cvpj_note = note_data.mx_makenote('DPCM', int(notedata['Time'])/NoteLength, int(notedata['Duration'])/NoteLength, NoteToMidi(notedata['Value'])+24, None, None)
                            t_patternnotelist.append(cvpj_note)

                cvpj_patternid = Channel+'-'+Pattern
                tracks.m_add_nle(cvpj_l, cvpj_patternid, t_patternnotelist)
                tracks.m_add_nle_info(cvpj_l, cvpj_patternid, Pattern+' ('+Channel+')', [0.13, 0.15, 0.16])

            Channel_Instances = fst_channels[Channel]['Instances']
            durationnum = 0
            for fst_Placement in Channel_Instances:
                fst_PData = Channel_Instances[fst_Placement]
                fst_time = int(fst_PData['Time'])
                cvpj_l_placement = placement_data.makepl_n_mi(PointsPos[int(fst_time)], PatternLengthList[durationnum], Channel+'-'+fst_PData['Pattern'])
                tracks.m_playlist_pl_add(cvpj_l, playlistnum, cvpj_l_placement)
                durationnum += 1
            playlistnum += 1

        timesig = placements.get_timesig(PatternLength, fst_beatlength)
        placements.make_timemarkers(cvpj_l, timesig, PatternLengthList, LoopPoint)
        if 'Name' in fst_Main: song.add_info(cvpj_l, 'title', fst_Main['Name'])
        if 'Author' in fst_Main: song.add_info(cvpj_l, 'author', fst_Main['Author'])

        cvpj_l['do_addloop'] = True
        
        cvpj_l['timesig'] = timesig
        song.add_param(cvpj_l, 'bpm', bpm)
        return json.dumps(cvpj_l)