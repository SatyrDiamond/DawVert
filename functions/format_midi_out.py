
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
    global s_ppq
    global s_timemarkers

    s_ppq = ppq
    t_tracknum = 0
    s_tempo = {}
    s_timemarkers = []

    t_chan_auto = []
    for _ in range(channels): t_chan_auto.append({})

    t_chan_initial = []
    for _ in range(channels): t_chan_initial.append({})

def track_start(channels, startpos):
    global t_tracknum
    global t_trackname
    global t_chan_cmds
    global activenotes
    global midichanneltype
    global t_startpos

    t_startpos = startpos
    t_trackname = None

    midichanneltype = []
    for num in range(channels):
        if num == 9: midichanneltype.append(1)
        else: midichanneltype.append(0)

    t_tracknum += 1
    cmd_before_note = True
    cmd_before_program = True

    activenotes = []
    for _ in range(channels): activenotes.append([])

    t_chan_cmds = []
    for _ in range(channels): t_chan_cmds.append({})

def note_off(time, key, channel):
    global t_chan_cmds
    global activenotes

    for activenote in activenotes[channel]:
        if activenote[1] == key: 
            activenotes[channel].remove(activenote)
            position = activenote[0]
            key = activenote[1]
            for cmdnum in range(len(t_chan_cmds[channel][position])):
                mcmd = t_chan_cmds[channel][position][cmdnum]
                if mcmd[0] == 'NOTE':
                    if mcmd[1][1] == key:
                        t_chan_cmds[channel][position][cmdnum][1][0] = time - activenote[0]
    #print(str(time).ljust(8), 'NOTE OFF   ', str(key).ljust(4), str(channel).ljust(3))


def note_on(time, key, channel, vel):
    global t_chan_cmds
    global activenotes
    addpoint(t_chan_cmds[channel], time, ['NOTE', [None, key, vel]])
    activenotes[channel].append([time, key, vel])
    #print(str(time).ljust(8), 'NOTE ON    ', str(key).ljust(4), str(channel).ljust(3), str(vel).ljust(3))

def note(time, key, dur, channel, vel):
    global t_chan_cmds
    addpoint(t_chan_cmds[channel], time, ['NOTE', [dur, key, vel]])


def program_change(time, channel, program): 
    global t_chan_cmds
    addpoint(t_chan_cmds[channel], time, ['PROG', program])

def control_change(time, channel, control, value): 
    global t_chan_cmds
    addpoint(t_chan_cmds[channel], time, ['CTRL', [control, value]])

def tempo(time, tempo): 
    global s_tempo
    s_tempo[time] = 60000000/tempo

def track_name(name): 
    global t_trackname
    t_trackname = name

def marker(time, name):
    global s_timemarkers
    global s_ppq
    ppqstep = s_ppq/4
    s_timemarkers.append({'position':time/ppqstep, 'name': name})

def time_signature(time, numerator, denominator):
    global s_timemarkers
    global s_ppq
    ppqstep = s_ppq/4
    s_timemarkers.append({'position':time/ppqstep, 'name': str(numerator)+'/'+str(denominator), 'type': 'timesig', 'numerator': numerator, 'denominator': denominator})

def track_end(channels):
    global midichanneltype
    global s_ppq
    global t_tracknum
    global t_trackname
    global t_chan_cmds
    global t_chan_usedinst
    global t_chan_used
    global t_startpos
    global s_tempo
    global hasnotes

    ppqstep = s_ppq/4

    t_chan_used = []
    for _ in range(channels): t_chan_used.append(0)

    t_chan_curinst = []
    for _ in range(channels): t_chan_curinst.append([0,0])

    t_chan_usedinst = []
    for _ in range(channels): t_chan_usedinst.append([])

    t_cvpj_notelist = []

    for channelnum in range(channels):
        s_chan_cmds = t_chan_cmds[channelnum]
        s_chan_cmds = dict(sorted(s_chan_cmds.items(), key=lambda item: item[0]))
        for position in s_chan_cmds:
            for s_cmd in s_chan_cmds[position]:
                
                if s_cmd[0] == 'PROG':
                    t_chan_curinst[channelnum][1] = s_cmd[1]

                if s_cmd[0] == 'NOTE':
                    if t_chan_curinst[channelnum] not in t_chan_usedinst[channelnum]: t_chan_usedinst[channelnum].append(t_chan_curinst[channelnum])
                    cvpj_inst = 't'+str(t_tracknum)+'_c'+str(channelnum)+'_b'+str(t_chan_curinst[channelnum][0])+'_i'+str(t_chan_curinst[channelnum][1])
                    #print(position, cvpj_inst, s_cmd[1])
                    notedata = {}
                    notedata['position'] = position/ppqstep
                    notedata['key'] = s_cmd[1][1]
                    notedata['vol'] = s_cmd[1][2]/127
                    notedata['duration'] = s_cmd[1][0]/ppqstep
                    notedata['instrument'] = cvpj_inst
                    t_cvpj_notelist.append(notedata)


        for s_chan_usedinst in t_chan_usedinst[channelnum]:
            cvpj_midibank = t_chan_curinst[channelnum][0]
            cvpj_midiinst = t_chan_curinst[channelnum][1]
            cvpj_instid = 't'+str(t_tracknum)+'_c'+str(channelnum)+'_b'+str(t_chan_curinst[channelnum][0])+'_i'+str(cvpj_midiinst)

            cvpj_l_instruments[cvpj_instid] = {}
            cvpj_trackdata = cvpj_l_instruments[cvpj_instid]
            cvpj_trackdata['fxrack_channel'] = channelnum+1

            cvpj_trackdata["instdata"] = {}
            cvpj_trackdata["instdata"]['plugin'] = 'general-midi'

            if midichanneltype[channelnum] == 0: 
                cvpj_trackdata["instdata"]['plugindata'] = {'bank':cvpj_midibank, 'inst':cvpj_midiinst}
                cvpj_trackdata["instdata"]['usemasterpitch'] = 1
                cvpj_trackdata["name"] = MIDIInstNames[cvpj_midiinst]
                cvpj_trackdata["color"] = MIDIInstColors[cvpj_midiinst]
            else: 
                cvpj_trackdata["instdata"]['plugindata'] = {'bank':128, 'inst':cvpj_midiinst}
                cvpj_trackdata["instdata"]['usemasterpitch'] = 0
                cvpj_trackdata["name"] = 'Drums'

            cvpj_l_instruments[cvpj_instid] = cvpj_trackdata
            cvpj_l_instrumentsorder.append(cvpj_instid)

    playlistrowdata = {}
    if t_trackname != None: playlistrowdata['name'] = str(t_trackname)
    playlistrowdata['color'] = [0.3, 0.3, 0.3]

    if t_cvpj_notelist != []:
        hasnotes = True
        cvpj_placement = {}
        cvpj_placement['position'] = t_startpos/ppqstep
        cvpj_placement['duration'] = note_mod.getduration(t_cvpj_notelist)
        cvpj_placement['type'] = 'instruments'
        cvpj_placement['notelist'] = t_cvpj_notelist
        playlistrowdata['placements'] = [cvpj_placement]
    else:
        hasnotes = False

    cvpj_l_playlist[str(t_tracknum)] = playlistrowdata

def track_hasnotes():
    global hasnotes
    return hasnotes

def song_end():
    global s_tempo
    global s_ppq
    global s_timemarkers
    ppqstep = s_ppq/4

    songduration = 0

    t_auto_tempo = []

    for s_tempo_point in s_tempo:
        t_auto_tempo.append({"position": s_tempo_point/ppqstep, 'type': 'instant', "value": s_tempo[s_tempo_point]})
        if songduration < s_tempo_point/ppqstep: songduration = s_tempo_point/ppqstep

    cvpj_l_automation = {}
    cvpj_l_automation['main'] = {}

    if t_auto_tempo != []:
        cvpj_autodata = {}
        cvpj_autodata["position"] = 0
        cvpj_autodata["duration"] = songduration
        cvpj_autodata["points"] = t_auto_tempo
        cvpj_l_automation['main']['bpm'] = [cvpj_autodata]

    cvpj_l['use_instrack'] = False
    cvpj_l['use_fxrack'] = False
    cvpj_l['timesig_numerator'] = 4
    cvpj_l['timesig_denominator'] = 4
    cvpj_l['automation'] = cvpj_l_automation
    cvpj_l['timemarkers'] = s_timemarkers
    cvpj_l['instruments_data'] = cvpj_l_instruments
    cvpj_l['instruments_order'] = cvpj_l_instrumentsorder
    cvpj_l['playlist'] = cvpj_l_playlist
    cvpj_l['bpm'] = 140
    return cvpj_l