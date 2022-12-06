import shlex
import json
import plugin_input
import json
from functions import placements

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

def decode_fst(infile):
    f_fst = open(infile, 'r')
    famistudiotxt_lines = f_fst.readlines()
      
    FST_Main = {}
    
    FST_Instruments = {}
    FST_Songs = {}
    FST_DPCMSamples = {}
    FST_DPCMMappings = {}
    
    for line in famistudiotxt_lines:
        t_cmd = line.split(" ", 1)
        t_precmd = t_cmd[0]
        tabs_num = t_precmd.count('\t')
    
        cmd_name = t_precmd.split()[0]
        cmd_params = dict(token.split('=') for token in shlex.split(t_cmd[1]))
    
        #print(tabs_num, cmd_name, cmd_params)

        if cmd_name == 'Project' and tabs_num == 0:
            FST_Main = cmd_params
    
        elif cmd_name == 'DPCMSample' and tabs_num == 1:
            FST_DPCMSamples[cmd_params['Name']] = cmd_params['Data']
        elif cmd_name == 'DPCMMapping' and tabs_num == 1:
            mapnote = cmd_params['Note']
            FST_DPCMMappings[mapnote] = {}
            FST_DPCMMappings[mapnote]['Sample'] = cmd_params['Sample']
            FST_DPCMMappings[mapnote]['Pitch'] = cmd_params['Pitch']
            FST_DPCMMappings[mapnote]['Loop'] = cmd_params['Loop']
    
        elif cmd_name == 'Instrument' and tabs_num == 1:
            instname = cmd_params['Name']
            FST_Instruments[instname] = {}
            FST_Instrument = FST_Instruments[instname]
            FST_Instrument['Name'] = cmd_params['Name']
            FST_Instrument['Envelopes'] = {}
            if 'N163WavePreset' in cmd_params: FST_Instrument['N163WavePreset'] = cmd_params['N163WavePreset']
            if 'N163WaveSize' in cmd_params: FST_Instrument['N163WaveSize'] = cmd_params['N163WaveSize']
            if 'N163WavePos' in cmd_params: FST_Instrument['N163WavePos'] = cmd_params['N163WavePos']
            if 'N163WaveCount' in cmd_params: FST_Instrument['N163WaveCount'] = cmd_params['N163WaveCount']

            if 'Vrc7Patch' in cmd_params: FST_Instrument['Vrc7Patch'] = cmd_params['Vrc7Patch']
            if 'Vrc7Reg0' in cmd_params: FST_Instrument['Vrc7Reg0'] = cmd_params['Vrc7Reg0']
            if 'Vrc7Reg1' in cmd_params: FST_Instrument['Vrc7Reg1'] = cmd_params['Vrc7Reg1']
            if 'Vrc7Reg2' in cmd_params: FST_Instrument['Vrc7Reg2'] = cmd_params['Vrc7Reg2']
            if 'Vrc7Reg3' in cmd_params: FST_Instrument['Vrc7Reg3'] = cmd_params['Vrc7Reg3']
            if 'Vrc7Reg4' in cmd_params: FST_Instrument['Vrc7Reg4'] = cmd_params['Vrc7Reg4']
            if 'Vrc7Reg5' in cmd_params: FST_Instrument['Vrc7Reg5'] = cmd_params['Vrc7Reg5']
            if 'Vrc7Reg6' in cmd_params: FST_Instrument['Vrc7Reg6'] = cmd_params['Vrc7Reg6']
            if 'Vrc7Reg7' in cmd_params: FST_Instrument['Vrc7Reg7'] = cmd_params['Vrc7Reg7']
        elif cmd_name == 'Envelope' and tabs_num == 2:
            envtype = cmd_params['Type']
            FST_Instrument['Envelopes'][envtype] = {}
            FST_Instrument['Envelopes'][envtype] = cmd_params

        elif cmd_name == 'Song' and tabs_num == 1:
            songname = cmd_params['Name']
            FST_Songs[songname] = cmd_params
            FST_Song = FST_Songs[songname]
            FST_Song['PatternCustomSettings'] = {}
            FST_Song['Channels'] = {}
    
        elif cmd_name == 'PatternCustomSettings' and tabs_num == 2:
            pattime = cmd_params['Time']
            FST_Song['PatternCustomSettings'][pattime] = cmd_params

        elif cmd_name == 'Channel' and tabs_num == 2:
            chantype = cmd_params['Type']
            FST_Song['Channels'][chantype] = {}
            FST_Channel = FST_Song['Channels'][chantype]
            FST_Channel['Instances'] = {}
            FST_Channel['Patterns'] = {}
    
        elif cmd_name == 'Pattern' and tabs_num == 3:
            patname = cmd_params['Name']
            FST_Channel['Patterns'][patname] = {}
            FST_Pattern = FST_Channel['Patterns'][patname]
    
        elif cmd_name == 'PatternInstance' and tabs_num == 3:
            pattime = cmd_params['Time']
            FST_Channel['Instances'][pattime] = cmd_params
    
        elif cmd_name == 'Note' and tabs_num == 4:
            notetime = cmd_params['Time']
            FST_Pattern[notetime] = cmd_params
    
        else:
            print('unexpected command and/or wrong tabs')
            exit()
    
    FST_Main['Instruments'] = FST_Instruments
    FST_Main['Songs'] = FST_Songs
    FST_Main['DPCMSamples'] = FST_DPCMSamples
    FST_Main['DPCMMappings'] = FST_DPCMMappings
    return FST_Main
def create_inst(wavetype, FST_Instrument, cvpj_l_instruments, cvpj_l_instrumentsorder):
    instname = FST_Instrument['Name']
    cvpj_inst = {}
    cvpj_inst["enabled"] = 1
    cvpj_inst["instdata"] = {}
    cvpj_instdata = cvpj_inst["instdata"]
    cvpj_instdata['middlenote'] = 0
    cvpj_instdata['pitch'] = 0
    if wavetype == 'Square' or wavetype == 'Triangle' or wavetype == 'Noise':
        cvpj_instdata['plugin'] = 'famistudio'
        cvpj_instdata['plugindata'] = FST_Instrument
        cvpj_instdata['plugindata']['wave'] = wavetype
    if wavetype == 'VRC7FM':
        cvpj_instdata['plugin'] = 'famistudio-vrc7fm'
        cvpj_instdata['plugindata'] = FST_Instrument
    if wavetype == 'VRC6Square' or wavetype == 'VRC6Saw':
        cvpj_instdata['plugin'] = 'famistudio-vrc6'
        cvpj_instdata['plugindata'] = FST_Instrument
        if wavetype == 'VRC6Saw': cvpj_instdata['plugindata']['wave'] = 'Saw'
        if wavetype == 'VRC6Square': cvpj_instdata['plugindata']['wave'] = 'Square'
    if wavetype == 'FDS':
        cvpj_instdata['plugin'] = 'famistudio-fds'
        cvpj_instdata['plugindata'] = FST_Instrument
    if wavetype == 'N163':
        cvpj_instdata['plugin'] = 'famistudio-n163'
        cvpj_instdata['plugindata'] = FST_Instrument
    if wavetype == 'S5B':
        cvpj_instdata['plugin'] = 'famistudio-s5b'
        cvpj_instdata['plugindata'] = FST_Instrument
    cvpj_instdata['usemasterpitch'] = 1
    if wavetype == 'Square': cvpj_inst['color'] = [0.97, 0.56, 0.36]
    if wavetype == 'Triangle': cvpj_inst['color'] = [0.94, 0.33, 0.58]
    if wavetype == 'Noise': cvpj_inst['color'] = [0.33, 0.74, 0.90]
    if wavetype == 'FDS': cvpj_inst['color'] = [0.94, 0.94, 0.65]
    if wavetype == 'VRC7FM': cvpj_inst['color'] = [1.00, 0.46, 0.44]
    if wavetype == 'VRC6Square': cvpj_inst['color'] = [0.60, 0.44, 0.93]
    if wavetype == 'VRC6Saw': cvpj_inst['color'] = [0.46, 0.52, 0.91]
    if wavetype == 'S5B': cvpj_inst['color'] = [0.58, 0.94, 0.33]
    if wavetype == 'N163': cvpj_inst['color'] = [0.97, 0.97, 0.36]
    cvpj_inst["name"] = wavetype+'-'+instname
    cvpj_inst["pan"] = 0.0
    cvpj_inst["vol"] = 0.6
    cvpj_l_instruments[wavetype+'-'+instname] = cvpj_inst
    if wavetype+'-'+instname not in cvpj_l_instrumentsorder:
        cvpj_l_instrumentsorder.append(wavetype+'-'+instname)
def create_dpcm_inst(DPCMMappings, DPCMSamples, cvpj_l_instruments, cvpj_l_instrumentsorder):
    instname = 'DPCM'
    cvpj_inst = {}
    cvpj_inst["enabled"] = 1
    cvpj_inst["instdata"] = {}
    cvpj_instdata = cvpj_inst["instdata"]
    cvpj_instdata['middlenote'] = 0
    cvpj_instdata['pitch'] = 0
    cvpj_instdata['plugin'] = 'none'
    cvpj_instdata['usemasterpitch'] = 1
    cvpj_inst['color'] = [0.48, 0.83, 0.49]
    cvpj_inst["name"] = 'DPCM'
    cvpj_inst["pan"] = 0.0
    cvpj_inst["vol"] = 0.6
    cvpj_l_instruments['DPCM'] = cvpj_inst
    cvpj_l_instrumentsorder.append('DPCM')

def NoteToMidi(keytext):
    l_key = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    s_octave = (int(keytext[-1])-5)*12
    lenstr = len(keytext)
    if lenstr == 3:
        t_key = keytext[:-1]
    else:
        t_key = keytext[:-1]
    s_key = l_key.index(t_key)

    return s_key + s_octave

class input_famistudio(plugin_input.base):
    def __init__(self): pass
    def getshortname(self): return 'fs_txt'
    def getname(self): return 'FamiStudio Text'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        FST_Main = decode_fst(input_file)
        with open('fst.json', "w") as fileout:
            json.dump(FST_Main, fileout, indent=4, sort_keys=True)
        
        InstShapes = {'Square1': 'Square', 
        'Square2': 'Square', 
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
        'S5BSquare3': 'S5B'}

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_notelistindex = {}
        cvpj_l_playlist = {}
        
        FST_Instruments = FST_Main['Instruments']
        FST_currentsong = next(iter(FST_Main['Songs'].values()))
        FST_Channels = FST_currentsong['Channels']
        FST_BeatLength = int(FST_currentsong['BeatLength'])
        FST_Groove = FST_currentsong['Groove']
        PatternLength = int(FST_currentsong['PatternLength'])
        SongLength = int(FST_currentsong['Length'])
        NoteLength = int(FST_currentsong['NoteLength'])
        LoopPoint = int(FST_currentsong['LoopPoint'])
        DPCMMappings = FST_Main['DPCMMappings']
        DPCMSamples = FST_Main['DPCMSamples']

        groovetable = []
        groovesplit = FST_Groove.split('-')
        for groovenumber in groovesplit:
            groovetable.append(int(groovenumber))
        bpm = 60/(average(groovetable)/60*FST_BeatLength)

        PatternLengthList = []
        for number in range(SongLength):
            if str(number) not in FST_currentsong['PatternCustomSettings']: PatternLengthList.append(PatternLength)
            else: PatternLengthList.append(int(FST_currentsong['PatternCustomSettings'][str(number)]['Length']))
        print(PatternLengthList)

        PointsPos = []
        PointsAdd = 0
        for number in range(SongLength):
            PointsPos.append(PointsAdd)
            PointsAdd += PatternLengthList[number]
        print(PointsPos)

        for Channel in FST_Channels:
            WaveType = None
            used_insts = get_used_insts(FST_Channels[Channel])
            if Channel in InstShapes: WaveType = InstShapes[Channel]
            elif Channel == 'DPCM': 
                create_dpcm_inst(DPCMMappings, DPCMSamples, cvpj_l_instruments, cvpj_l_instrumentsorder)
            if WaveType != None:
                for inst in used_insts:
                    create_inst(WaveType, FST_Instruments[inst], cvpj_l_instruments, cvpj_l_instrumentsorder)

        playlistnum = 1
        for Channel in FST_Channels:
            ChannelName = Channel
            cvpj_l_playlist[str(playlistnum)] = {}
            cvpj_l_playlist[str(playlistnum)]['color'] = [0.13, 0.15, 0.16]
            cvpj_l_playlist[str(playlistnum)]['name'] = Channel
            cvpj_l_playlist[str(playlistnum)]['placements'] = []
            Channel_Patterns = FST_Channels[Channel]['Patterns']
            for Pattern in Channel_Patterns:
                cvpj_patternid = Channel+'-'+Pattern
                cvpj_l_notelistindex[cvpj_patternid] = {}
                cvpj_l_notelistindex[cvpj_patternid]['notelist'] = []
                cvpj_l_notelistindex[cvpj_patternid]['color'] = [0.13, 0.15, 0.16]
                cvpj_l_notelistindex[cvpj_patternid]['name'] = Pattern+' ('+Channel+')'
                patternnotelist = cvpj_l_notelistindex[cvpj_patternid]['notelist']
                for fst_note in Channel_Patterns[Pattern]:
                    notedata = Channel_Patterns[Pattern][fst_note]
                    if ChannelName != 'DPCM':
                        if 'Duration' in notedata and 'Instrument' in notedata:
                            cvpj_note = {}
                            cvpj_note['instrument'] = InstShapes[Channel]+'-'+notedata['Instrument']
                            cvpj_note['duration'] = int(notedata['Duration'])/NoteLength
                            cvpj_note['position'] = int(notedata['Time'])/NoteLength
                            cvpj_note['key'] = NoteToMidi(notedata['Value']) + 24
                            patternnotelist.append(cvpj_note)
                    else:
                        if 'Duration' in notedata:
                            cvpj_note = {}
                            cvpj_note['instrument'] = 'DPCM'
                            cvpj_note['duration'] = int(notedata['Duration'])/NoteLength
                            cvpj_note['position'] = int(notedata['Time'])/NoteLength
                            cvpj_note['key'] = NoteToMidi(notedata['Value']) + 24
                            patternnotelist.append(cvpj_note)
            Channel_Instances = FST_Channels[Channel]['Instances']
            for FST_Placement in Channel_Instances:
                FST_PData = Channel_Instances[FST_Placement]
                FST_time = int(FST_PData['Time'])
                cvpj_l_placement = {}
                cvpj_l_placement['type'] = "instruments"
                cvpj_l_placement['position'] = PointsPos[int(FST_time)]
                cvpj_l_placement['fromindex'] = Channel+'-'+FST_PData['Pattern']
                cvpj_l_playlist[str(playlistnum)]['placements'].append(cvpj_l_placement)
            playlistnum += 1

        timesig = placements.get_timesig(PatternLength, FST_BeatLength)
        cvpj_l['timesig_numerator'] = timesig[0]
        cvpj_l['timesig_denominator'] = timesig[1]

        prevtimesig = timesig
        currentpos = 0
        for PatternLengthPart in PatternLengthList:
            print(PatternLengthPart)
            temptimesig = placements.get_timesig(PatternLengthPart, FST_BeatLength)
            if prevtimesig != temptimesig:
                print('place', temptimesig)
            prevtimesig = temptimesig
            currentpos += PatternLengthPart

        cvpj_l['timemarkers'] = placements.make_timemarkers(timesig, PatternLengthList, LoopPoint)
        cvpj_l['notelistindex'] = cvpj_l_notelistindex
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = bpm
        return json.dumps(cvpj_l)