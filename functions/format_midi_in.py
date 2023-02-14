
from functions import values
from functions import note_mod

MIDIControllerName = values.getlist_gm_ctrl_names()
MIDIInstColors = values.getlist_gm_colors()
MIDIInstNames = values.getlist_gm_names()
MIDIDrumSetNames = values.getlist_gm_drumset_names()

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
    global t_chan_initial
    global s_tempo
    global s_ppqstep
    global s_timemarkers
    global t_trk_ch

    s_ppqstep = ppq/4
    t_tracknum = 0
    s_tempo = {}
    s_timemarkers = []

    t_trk_ch = [[] for x in range(channels)]

    t_chan_auto = []
    for _ in range(channels): t_chan_auto.append({})

    t_chan_initial = []
    for _ in range(channels): t_chan_initial.append({})

# -------------------------------------- TRACK --------------------------------------

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

    t_chan_usedinst = [[] for x in range(channels)]
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

        if midi_cmd[0] == 'note': 
            if t_cur_inst[midi_cmd[1]] not in t_chan_usedinst[midi_cmd[1]]:
                t_chan_usedinst[midi_cmd[1]].append(t_cur_inst[midi_cmd[1]])
            curinst = t_cur_inst[midi_cmd[1]]

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
            if t_cur_inst[midi_cmd[1]] not in t_chan_usedinst[midi_cmd[1]]:
                t_chan_usedinst[midi_cmd[1]].append(t_cur_inst[midi_cmd[1]])
            curinst = t_cur_inst[midi_cmd[1]]

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
                    notedata['vol'] = t_actnote[2]/127
                    notedata['duration'] = (t_actnote[1]-t_actnote[0])/s_ppqstep
                    notedata['instrument'] = 't'+str(t_actnote[3])+'_c'+str(channelnum)+'_b'+str(t_actnote[4])+'_i'+str(t_actnote[5])
                    t_cvpj_notelist.append(notedata)
            notekey += 1

    playlistrowdata = {}
    if t_trackname != None: playlistrowdata['name'] = str(t_trackname)
    playlistrowdata['color'] = [0.3, 0.3, 0.3]

    if t_cvpj_notelist != []:
        hasnotes = True
        cvpj_placement = {}
        cvpj_placement['position'] = t_startpos/s_ppqstep
        cvpj_placement['duration'] = note_mod.getduration(t_cvpj_notelist)
        cvpj_placement['type'] = 'instruments'
        cvpj_placement['notelist'] = note_mod.sortnotes(t_cvpj_notelist)
        playlistrowdata['placements_notes'] = [cvpj_placement]
    else:
        hasnotes = False

    cvpj_l_playlist[str(t_tracknum)] = playlistrowdata

def make_custominst(channelnum, cvpj_midibank, cvpj_midiinst, instdata):
    cvpj_instid = 't'+str(t_tracknum)+'_c'+str(channelnum)+'_b'+str(cvpj_midibank)+'_i'+str(cvpj_midiinst)
    cvpj_l_instruments[cvpj_instid] = instdata
    cvpj_l_instrumentsorder.append(cvpj_instid)

def make_inst(channelnum, cvpj_midibank, cvpj_midiinst):
    cvpj_instid = 't'+str(t_tracknum)+'_c'+str(channelnum)+'_b'+str(cvpj_midibank)+'_i'+str(cvpj_midiinst)
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
            cvpj_trackdata["name"] = MIDIInstNames[cvpj_midiinst] + ' [Ch' + str(channelnum+1) + ']'
            cvpj_trackdata["color"] = MIDIInstColors[cvpj_midiinst]
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

    for channelnum in range(channels):
        for s_chan_usedinst in t_chan_usedinst[channelnum]:
            usedinst_output.append([channelnum, s_chan_usedinst[0], s_chan_usedinst[1]])

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




def song_end(channels):
    global midi_cmds
    global s_ppqstep
    global t_trk_ch
    global t_chan_auto

    songduration = 0

    t_auto_tempo = []

    for s_tempo_point in s_tempo:
        t_auto_tempo.append({"position": s_tempo_point/s_ppqstep, 'type': 'instant', "value": s_tempo[s_tempo_point]})
        if songduration < s_tempo_point/s_ppqstep: songduration = s_tempo_point/s_ppqstep

    cvpj_l_automation = {}
    cvpj_l_automation['main'] = {}

    if t_auto_tempo != []:
        cvpj_autodata = {}
        cvpj_autodata["position"] = 0
        cvpj_autodata["duration"] = songduration
        cvpj_autodata["points"] = t_auto_tempo
        cvpj_l_automation['main']['bpm'] = [cvpj_autodata]

    cvpj_l_fxrack["0"] = {}
    cvpj_l_fxrack["0"]["name"] = "Master"

    for midi_channum in range(channels):
        cvpj_l_fxrack[str(midi_channum+1)] = {}

        s_chan_initial = t_chan_initial[midi_channum]

        fxdata = cvpj_l_fxrack[str(midi_channum+1)]
        fxdata["fxenabled"] = 1

        if 7 in s_chan_initial: fxdata["vol"] = s_chan_initial[7]/127
        else: fxdata["vol"] = 1.0

        if 10 in s_chan_initial: fxdata["pan"] = ((s_chan_initial[10]/127)-0.5)*2
        else: fxdata["pan"] = 1.0

        fxdata['color'] = [0.3, 0.3, 0.3]
        fxdata["name"] = "Channel "+str(midi_channum+1)

    #print(t_trk_ch)

    #autochannum = 0
    #for t_chan_auto_s in t_chan_auto:
    #    for t_chan_auto_s_t in t_chan_auto_s:
    #        print(autochannum, len(t_chan_auto_s[t_chan_auto_s_t]), t_chan_auto_s_t, MIDIControllerName[t_chan_auto_s_t])
    #        if t_chan_auto_s_t == 7: #volume
    #            print(t_chan_auto_s[t_chan_auto_s_t])
    #        if t_chan_auto_s_t == 10: #pan
    #            print(t_chan_auto_s[t_chan_auto_s_t])
    #    autochannum += 1

    cvpj_l['use_instrack'] = False
    cvpj_l['use_fxrack'] = True
    cvpj_l['automation'] = cvpj_l_automation
    cvpj_l['timemarkers'] = s_timemarkers
    cvpj_l['instruments_data'] = cvpj_l_instruments
    cvpj_l['instruments_order'] = cvpj_l_instrumentsorder
    cvpj_l['playlist'] = cvpj_l_playlist
    cvpj_l['fxrack'] = cvpj_l_fxrack
    cvpj_l['bpm'] = 140
    return cvpj_l