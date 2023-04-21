# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from functions import notelist_data
from functions import idvals
from functions import tracks


idvals_midi_ctrl = idvals.parse_idvalscsv('idvals/midi_ctrl.csv')
idvals_midi_inst = idvals.parse_idvalscsv('idvals/midi_inst.csv')
idvals_midi_inst_drums = idvals.parse_idvalscsv('idvals/midi_inst_drums.csv')

cvpj_l = {}
cvpj_l_playlist = {}
cvpj_l_instruments = {}
cvpj_l_instrumentsorder = []
cvpj_l_timemarkers = []
cvpj_l_fxrack = {}

def addpoint(dict_val, pos_val, value):
    if pos_val not in dict_val: dict_val[pos_val] = []
    dict_val[pos_val].append(value)

def song_start(channels, ppq):
    global t_tracknum
    global t_chan_auto
    global t_chan_usedinst_all
    global s_tempo
    global s_ppqstep
    global s_timemarkers
    global t_trk_ch

    s_ppqstep = ppq/4
    t_tracknum = 0
    s_tempo = {}
    s_timemarkers = []

    t_trk_ch = [[] for x in range(channels)]

    t_chan_usedinst_all = [[] for x in range(channels)]

    t_chan_auto = []
    for _ in range(channels): t_chan_auto.append({})

# -------------------------------------- TRACK --------------------------------------
def gettrackname(t_tracknum, channelnum, cvpj_midibank, cvpj_midiinst):
    return 't'+str(t_tracknum)+'_c'+str(channelnum)+'_b'+str(cvpj_midibank)+'_i'+str(cvpj_midiinst)

def track_start(channels, startpos):
    global t_tracknum
    global t_trackname
    global t_startpos
    global midi_cmds
    global t_curpos

    global cvpj_notes
    global midichanneltype

    t_curpos = 0
    t_startpos = startpos
    t_trackname = None

    midichanneltype = []
    for num in range(channels):
        if num == 9: midichanneltype.append(1)
        else: midichanneltype.append(0)

    t_tracknum += 1
    cmd_before_note = True
    cmd_before_program = True

    cvpj_notes = []
    for _ in range(channels): cvpj_notes.append([])

    midi_cmds = []

def track_end(channels):
    global hasnotes
    global midi_cmds
    global s_ppqstep
    global t_chan_auto
    global t_chan_usedinst
    global t_trackname
    global t_tracknum
    global t_trk_ch

    t_cvpj_notelist = []
    cvpj_inst_start = 't'+str(t_tracknum)

    t_cur_inst = [[0, -1] for x in range(channels)]

    t_chan_usedinst = [{} for x in range(channels)]
    t_active_notes = [[[] for x in range(128)] for x in range(channels)]

    #for t_active_note_t in t_active_notes:
    #    print(t_active_note_t)

    curpos = 0
    for midi_cmd in midi_cmds:

        if midi_cmd[0] == 'break': curpos += midi_cmd[1]

        if midi_cmd[0] == 'program': 
            t_cur_inst[midi_cmd[1]][1] = midi_cmd[2]

        if midi_cmd[0] == 'control': 
            if midi_cmd[2] == 0:
                t_cur_inst[midi_cmd[1]][0] = midi_cmd[3]
            else:
                if midi_cmd[2] not in t_chan_auto[midi_cmd[1]]:
                    t_chan_auto[midi_cmd[1]][midi_cmd[2]] = {}
                t_chan_auto[midi_cmd[1]][midi_cmd[2]][curpos] = midi_cmd[3]

        if midi_cmd[0] == 'pitch': 
            if 'pitch' not in t_chan_auto[midi_cmd[1]]:
                t_chan_auto[midi_cmd[1]]['pitch'] = {}
            t_chan_auto[midi_cmd[1]]['pitch'][curpos] = midi_cmd[2]


        if midi_cmd[0] == 'note': 
            curinst = t_cur_inst[midi_cmd[1]]
            if curinst[0] not in t_chan_usedinst[midi_cmd[1]]:
                t_chan_usedinst[midi_cmd[1]][curinst[0]] = []
            if curinst[1] not in t_chan_usedinst[midi_cmd[1]][curinst[0]]:
                t_chan_usedinst[midi_cmd[1]][curinst[0]].append(curinst[1])

            trkname = gettrackname(t_tracknum, midi_cmd[1], curinst[0], curinst[1])
            if trkname not in t_chan_usedinst_all[midi_cmd[1]]:
                t_chan_usedinst_all[midi_cmd[1]].append(trkname)

            t_active_notes[midi_cmd[1]][midi_cmd[2]].append(
                [
                curpos, 
                midi_cmd[4], 
                midi_cmd[3], 
                t_tracknum,
                curinst[0],
                curinst[1]
                ]
            )

        if midi_cmd[0] == 'note_on': 
            curinst = t_cur_inst[midi_cmd[1]]
            if curinst[0] not in t_chan_usedinst[midi_cmd[1]]:
                t_chan_usedinst[midi_cmd[1]][curinst[0]] = []
            if curinst[1] not in t_chan_usedinst[midi_cmd[1]][curinst[0]]:
                t_chan_usedinst[midi_cmd[1]][curinst[0]].append(curinst[1])
                
            trkname = gettrackname(t_tracknum, midi_cmd[1], curinst[0], curinst[1])
            if trkname not in t_chan_usedinst_all[midi_cmd[1]]:
                t_chan_usedinst_all[midi_cmd[1]].append(trkname)

            t_active_notes[midi_cmd[1]][midi_cmd[2]].append(
                [
                curpos, 
                None, 
                midi_cmd[3], 
                t_tracknum,
                curinst[0],
                curinst[1]
                ]
            )

        if midi_cmd[0] == 'note_off': 
            for note in t_active_notes[midi_cmd[1]][midi_cmd[2]]:
                if note[1] == None:
                    note[1] = curpos
                    break

    for channelnum in range(channels):
        #print(channelnum)
        notekey = -60
        for c_active_notes in t_active_notes[channelnum]:
            for t_actnote in c_active_notes:
                #print(notekey, '-------------', t_actnote)
                if t_actnote[1] != None:
                    notedata = {}
                    notedata['position'] = t_actnote[0]/s_ppqstep
                    notedata['key'] = notekey
                    notedata['channel'] = channelnum+1
                    notedata['vol'] = t_actnote[2]/127
                    notedata['duration'] = (t_actnote[1]-t_actnote[0])/s_ppqstep
                    notedata['instrument'] = gettrackname(t_actnote[3], channelnum, t_actnote[4], t_actnote[5])
                    t_cvpj_notelist.append(notedata)
            notekey += 1

    playlistrowdata = {}
    if t_trackname != None: playlistrowdata['name'] = str(t_trackname)
    playlistrowdata['color'] = [0.3, 0.3, 0.3]

    if t_cvpj_notelist != []:
        hasnotes = True
        cvpj_placement = {}
        cvpj_placement['position'] = t_startpos/s_ppqstep
        cvpj_placement['duration'] = notelist_data.getduration(t_cvpj_notelist)
        cvpj_placement['type'] = 'instruments'
        cvpj_placement['notelist'] = notelist_data.sort(t_cvpj_notelist)
        playlistrowdata['placements_notes'] = [cvpj_placement]
    else:
        hasnotes = False

    cvpj_l_playlist[str(t_tracknum)] = playlistrowdata

def make_custominst(channelnum, cvpj_midibank, cvpj_midiinst, instdata):
    cvpj_instid = gettrackname(t_tracknum, channelnum, cvpj_midibank, cvpj_midiinst)
    cvpj_l_instruments[cvpj_instid] = instdata
    cvpj_l_instrumentsorder.append(cvpj_instid)

def make_inst(channelnum, cvpj_midibank, cvpj_midiinst):
    cvpj_instid = gettrackname(t_tracknum, channelnum, cvpj_midibank, cvpj_midiinst)
    if cvpj_instid not in t_trk_ch[channelnum]:
        t_trk_ch[channelnum].append(cvpj_instid)

    cvpj_l_instruments[cvpj_instid] = {}
    cvpj_trackdata = cvpj_l_instruments[cvpj_instid]
    cvpj_trackdata['fxrack_channel'] = channelnum+1

    cvpj_trackdata["instdata"] = {}

    if cvpj_midiinst == -1:
        if midichanneltype[channelnum] == 0: 
            cvpj_trackdata["instdata"] = {}
            cvpj_trackdata["instdata"]['plugin'] = 'none'
            cvpj_trackdata["color"] = [0,0,0]
        else: 
            cvpj_trackdata["instdata"]['plugin'] = 'general-midi'
            cvpj_trackdata["instdata"]['plugindata'] = {'bank':128, 'inst':cvpj_midiinst}
            cvpj_trackdata["instdata"]['usemasterpitch'] = 0
            cvpj_trackdata["name"] = 'Drums'
            cvpj_trackdata["color"] = [0.81, 0.80, 0.82]
    else:
        cvpj_trackdata["instdata"]['plugin'] = 'general-midi'
        if midichanneltype[channelnum] == 0: 
            cvpj_trackdata["instdata"]['plugindata'] = {'bank':cvpj_midibank, 'inst':cvpj_midiinst}
            cvpj_trackdata["instdata"]['usemasterpitch'] = 1
            cvpj_trackdata["name"] = idvals.get_idval(idvals_midi_inst, str(cvpj_midiinst), 'name') + ' [Ch' + str(channelnum+1) + ']'
            miditrkcolor = idvals.get_idval(idvals_midi_inst, str(cvpj_midiinst), 'color')
            if miditrkcolor != None:
                cvpj_trackdata["color"] = miditrkcolor
        else: 
            cvpj_trackdata["instdata"]['plugindata'] = {'bank':128, 'inst':cvpj_midiinst}
            cvpj_trackdata["instdata"]['usemasterpitch'] = 0
            cvpj_trackdata["name"] = 'Drums'
            cvpj_trackdata["color"] = [0.81, 0.80, 0.82]


    cvpj_l_instruments[cvpj_instid] = cvpj_trackdata
    cvpj_l_instrumentsorder.append(cvpj_instid)

def getusedinsts(channels):
    global t_chan_usedinst

    usedinst_output = []

    #print(t_chan_usedinst)

    for channelnum in range(channels):
        for s_chan_usedbank in t_chan_usedinst[channelnum]:
            for s_chan_usedinst in t_chan_usedinst[channelnum][s_chan_usedbank]:
                usedinst_output.append([channelnum, s_chan_usedbank, s_chan_usedinst])

    return usedinst_output

# -------------------------------------- FUNCTIONS --------------------------------------

def get_hasnotes(): 
    global hasnotes
    return hasnotes

# -------------------------------------- MIDI COMMANDS --------------------------------------

def resttime(addtime):
    global t_curpos
    global midi_cmds
    if addtime != 0:
        midi_cmds.append(['break', addtime])
    t_curpos += addtime

def note_on(key, channel, vel):
    global t_curpos
    global midi_cmds
    midi_cmds.append(['note_on', channel, key, vel])
    #print(str(t_curpos).ljust(8), 'NOTE ON    ', str(channel).ljust(3), str(key).ljust(4), str(vel).ljust(3))

def note_off(key, channel):
    global t_curpos
    global midi_cmds
    midi_cmds.append(['note_off', channel, key])
    #print(str(t_curpos).ljust(8), 'NOTE OFF   ', str(channel).ljust(3), str(key).ljust(7))

def note(key, dur, channel, vel):
    global t_curpos
    global midi_cmds
    midi_cmds.append(['note', channel, key, vel, t_curpos+dur])
    #print(str(t_curpos).ljust(8), 'NOTE       ', str(channel).ljust(3), str(key).ljust(4), str(vel).ljust(3), str(dur).ljust(3))

def pitchwheel(channel, pitch): 
    global t_curpos
    global midi_cmds
    midi_cmds.append(['pitch', channel, pitch])
    #print(str(t_curpos).ljust(8), 'PITCH      ', str(channel).ljust(3), str(pitch).ljust(4))

def program_change(channel, program): 
    global t_curpos
    global midi_cmds
    midi_cmds.append(['program', channel, program])
    #print(str(t_curpos).ljust(8), 'PROGRAM    ', str(channel).ljust(3), str(program).ljust(4))

def control_change(channel, control, value): 
    global t_curpos
    global midi_cmds
    midi_cmds.append(['control', channel, control, value])
    #print(str(t_curpos).ljust(8), 'CONTROL    ', str(channel).ljust(3), str(control).ljust(4), str(value).ljust(3))

def tempo(time, tempo): 
    global s_tempo
    s_tempo[time] = tempo

def track_name(name): 
    global t_trackname
    t_trackname = name

def marker(time, name):
    global s_timemarkers
    global s_ppqstep
    s_timemarkers.append({'position':time/s_ppqstep, 'name': name})

def time_signature(time, numerator, denominator):
    global s_timemarkers
    global s_ppq
    s_timemarkers.append({'position':time/s_ppqstep, 'name': str(numerator)+'/'+str(denominator), 'type': 'timesig', 'numerator': numerator, 'denominator': denominator})

# -------------------------------------- COMMANDS --------------------------------------



def midiauto2cvpjauto(points, divi, add):
    auto_output = []
    for point in points:
        auto_output.append([point/s_ppqstep, (points[point]/divi)+add])

    return auto_output

def song_end(channels):
    global midi_cmds
    global s_ppqstep
    global t_trk_ch
    global t_chan_auto

    songduration = 0

    for s_tempo_point in s_tempo:
        tracks.a_auto_nopl_addpoint('main', None, 'bpm', s_tempo_point/s_ppqstep, s_tempo[s_tempo_point], 'instant')

    cvpj_l_automation = {}
    cvpj_l_automation['main'] = {}
    cvpj_l_automation['fxmixer'] = {}

    cvpj_l_fxrack["0"] = {}
    cvpj_l_fxrack["0"]["name"] = "Master"

    for midi_channum in range(channels):
        cvpj_l_fxrack[str(midi_channum+1)] = {}

        fxdata = cvpj_l_fxrack[str(midi_channum+1)]
        fxdata["fxenabled"] = 1

        fxdata['color'] = [0.3, 0.3, 0.3]
        fxdata["name"] = "Channel "+str(midi_channum+1)

    #print(t_trk_ch)

    #autochannum = 0
    #for t_chan_auto_s in t_chan_auto:
    #    for t_chan_auto_s_t in t_chan_auto_s:
    #        if t_chan_auto_s_t == 'pitch':
    #            print(autochannum, 'Pitch', t_chan_auto_s[t_chan_auto_s_t])
    #        elif t_chan_auto_s_t == 7: #volume
    #            print(autochannum, 'Volume', t_chan_auto_s[t_chan_auto_s_t])
    #        elif t_chan_auto_s_t == 10: #pan
    #            print(autochannum, 'Pan', t_chan_auto_s[t_chan_auto_s_t])
    #        else:
    #            midictname = idvals.get_idval(idvals_midi_ctrl, str(cvpj_midiinst), 'name')
    #            print(autochannum, midictname, t_chan_auto_s[t_chan_auto_s_t])
    #    autochannum += 1

    for channum in range(channels):
        s_chan_trackids = t_chan_usedinst_all[channum]
        s_chan_auto = t_chan_auto[channum]

        if 7 in s_chan_auto: 
            if len(s_chan_auto[7]) == 1 and 0 in s_chan_auto[7]: 
                cvpj_l_fxrack[str(channum+1)]["vol"] = s_chan_auto[7][0]/127
            else: 
                twopoints = midiauto2cvpjauto(s_chan_auto[7], 127, 0)
                tracks.a_auto_nopl_twopoints('fxmixer', str(channum+1), 'vol', twopoints, 1, 'instant')

        if len(s_chan_trackids) == 1:
            if 'pitch' in s_chan_auto: 
                twopoints = midiauto2cvpjauto(s_chan_auto['pitch'], 1/8, 0)
                tracks.a_auto_nopl_twopoints('track', s_chan_trackids[0], 'pitch', twopoints, 1, 'instant')

        if len(s_chan_trackids) > 1:
            if 7 in s_chan_auto: 
                twopoints = midiauto2cvpjauto(s_chan_auto[7], 127, 0)
                tracks.a_auto_nopl_twopoints('fxrack', str(channum+1), 'vol', twopoints, 1, 'instant')

            for s_chan_trackid in s_chan_trackids:
                if 'pitch' in s_chan_auto: 
                    twopoints = midiauto2cvpjauto(s_chan_auto['pitch'], 1/8, 0)
                    tracks.a_auto_nopl_twopoints('track', s_chan_trackid, 'pitch', twopoints, 1, 'instant')

    tracks.a_auto_nopl_to_cvpj(cvpj_l)
    cvpj_l['timemarkers'] = s_timemarkers
    cvpj_l['instruments_data'] = cvpj_l_instruments
    cvpj_l['instruments_order'] = cvpj_l_instrumentsorder
    cvpj_l['playlist'] = cvpj_l_playlist
    cvpj_l['fxrack'] = cvpj_l_fxrack
    cvpj_l['bpm'] = 140
    return cvpj_l