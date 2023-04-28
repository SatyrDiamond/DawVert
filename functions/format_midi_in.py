# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from functions import notelist_data
from functions import note_data
from functions import data_values
from functions import idvals
from functions import tracks

idvals_midi_ctrl = idvals.parse_idvalscsv('data_idvals/midi_ctrl.csv')
idvals_midi_inst = idvals.parse_idvalscsv('data_idvals/midi_inst.csv')
idvals_midi_inst_drums = idvals.parse_idvalscsv('data_idvals/midi_inst_drums.csv')

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
def get_trackid(t_tracknum, channelnum, cvpj_midibank, cvpj_midiinst):
    return 't'+str(t_tracknum)+'_c'+str(channelnum)+'_b'+str(cvpj_midibank)+'_i'+str(cvpj_midiinst)

def track_start(channels, startpos):
    global t_tracknum
    global t_trackname
    global t_trackcolor
    global t_startpos
    global midi_cmds
    global t_curpos

    global cvpj_notes
    global midichanneltype

    t_curpos = 0
    t_startpos = startpos
    t_trackname = None
    t_trackcolor = None

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
    global t_trackcolor
    global t_tracknum
    global t_trk_ch

    t_cvpj_notelist = []
    cvpj_inst_start = 't'+str(t_tracknum)

    t_cur_inst = [[0, -1] for x in range(channels)]

    t_chan_usedinst = [{} for x in range(channels)]
    t_active_notes = [[[] for x in range(128)] for x in range(channels)]

    curpos = 0
    for midi_cmd in midi_cmds:

        if midi_cmd[0] == 'break': curpos += midi_cmd[1]

        if midi_cmd[0] == 'program': 
            t_cur_inst[midi_cmd[1]][1] = midi_cmd[2]

        if midi_cmd[0] == 'control': 
            if midi_cmd[2] == 0:
                t_cur_inst[midi_cmd[1]][0] = midi_cmd[3]
            else:
                if midi_cmd[2] not in t_chan_auto[midi_cmd[1]]: t_chan_auto[midi_cmd[1]][midi_cmd[2]] = {}
                t_chan_auto[midi_cmd[1]][midi_cmd[2]][curpos] = midi_cmd[3]

        if midi_cmd[0] == 'pitch': 
            if 'pitch' not in t_chan_auto[midi_cmd[1]]: t_chan_auto[midi_cmd[1]]['pitch'] = {}
            t_chan_auto[midi_cmd[1]]['pitch'][curpos] = midi_cmd[2]

        if midi_cmd[0] in ['note', 'note_on']: 
            curinst = t_cur_inst[midi_cmd[1]]
            if curinst[0] not in t_chan_usedinst[midi_cmd[1]]: t_chan_usedinst[midi_cmd[1]][curinst[0]] = []
            if curinst[1] not in t_chan_usedinst[midi_cmd[1]][curinst[0]]: t_chan_usedinst[midi_cmd[1]][curinst[0]].append(curinst[1])
            trkname = get_trackid(t_tracknum, midi_cmd[1], curinst[0], curinst[1])
            if trkname not in t_chan_usedinst_all[midi_cmd[1]]: t_chan_usedinst_all[midi_cmd[1]].append(trkname)
            if midi_cmd[0] == 'note': t_active_notes[midi_cmd[1]][midi_cmd[2]].append([curpos,midi_cmd[4],midi_cmd[3],t_tracknum,curinst[0],curinst[1]])
            if midi_cmd[0] == 'note_on': t_active_notes[midi_cmd[1]][midi_cmd[2]].append([curpos,None,midi_cmd[3],t_tracknum,curinst[0],curinst[1]])

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
                    notedata = note_data.mx_makenote(get_trackid(t_actnote[3],channelnum,t_actnote[4],t_actnote[5]), t_actnote[0]/s_ppqstep, (t_actnote[1]-t_actnote[0])/s_ppqstep, notekey, t_actnote[2]/127, None)
                    notedata['channel'] = channelnum+1
                    t_cvpj_notelist.append(notedata)
            notekey += 1

    playlistrowdata = {}
    if t_trackname != None: playlistrowdata['name'] = str(t_trackname)
    if t_trackcolor != None: playlistrowdata['color'] = t_trackcolor
    else: playlistrowdata['color'] = [0.3, 0.3, 0.3]

    if t_cvpj_notelist != []:
        hasnotes = True
        cvpj_placement = {}
        cvpj_placement['position'] = t_startpos/s_ppqstep
        cvpj_placement['duration'] = notelist_data.getduration(t_cvpj_notelist)
        cvpj_placement['notelist'] = notelist_data.sort(t_cvpj_notelist)
        playlistrowdata['placements_notes'] = [cvpj_placement]
    else:
        hasnotes = False

    cvpj_l_playlist[str(t_tracknum)] = playlistrowdata

def make_custominst(channelnum, cvpj_midibank, cvpj_midiinst, instdata):
    cvpj_instid = get_trackid(t_tracknum, channelnum, cvpj_midibank, cvpj_midiinst)
    cvpj_l_instruments[cvpj_instid] = instdata
    cvpj_l_instrumentsorder.append(cvpj_instid)

def make_inst(channelnum, cvpj_midibank, cvpj_midiinst):
    cvpj_instid = get_trackid(t_tracknum, channelnum, cvpj_midibank, cvpj_midiinst)
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
            cvpj_trackdata["name"] = 'Drums [Ch10]'
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
            cvpj_trackdata["name"] = 'Drums [Ch10]'
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

def track_color(name): 
    global t_trackcolor
    t_trackcolor = name

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

def add_auto_to_song(twopoints, autoname, channum, s_chan_trackids):
    if len(s_chan_trackids) == 1: tracks.a_auto_nopl_twopoints('track', s_chan_trackids[0], autoname, twopoints, 1, 'instant')
    elif len(s_chan_trackids) > 1: tracks.a_auto_nopl_twopoints('fxmixer', str(channum+1), autoname, twopoints, 1, 'instant')

def add_auto_to_song_no_mixer(twopoints, autoname, channum, s_chan_trackids):
    if len(s_chan_trackids) == 1: tracks.a_auto_nopl_twopoints('track', s_chan_trackids[0], autoname, twopoints, 1, 'instant')
    if len(s_chan_trackids) > 1:
        for s_chan_trackid in s_chan_trackids:
            tracks.a_auto_nopl_twopoints('track', s_chan_trackid, autoname, twopoints, 1, 'instant')

def add_auto_to_slot_gmfx(twopoints, autoname, slotname):
    tracks.a_auto_nopl_twopoints('slot', slotname, autoname, twopoints, 1, 'instant')

def do_slot_wet(schannum, slotendname, fxrack_chan):
    wetval = 0
    if len(schannum) == 1 and 0 in schannum: wetval = schannum[0]/127
    else: add_auto_to_slot_gmfx(midiauto2cvpjauto(schannum,127,0), 'wet', fxrack_chan+slotendname)
    return wetval

def song_end(channels):
    global midi_cmds
    global s_ppqstep
    global t_trk_ch
    global t_chan_auto

    songduration = 0

    cvpj_l['bpm'] = 140
    if 0 in s_tempo:
        cvpj_l['bpm'] = s_tempo[0]
        del s_tempo[0]

    for s_tempo_point in s_tempo:
        tracks.a_auto_nopl_addpoint('main', None, 'bpm', s_tempo_point/s_ppqstep, s_tempo[s_tempo_point], 'instant')

    cvpj_l_automation = {}
    cvpj_l_automation['main'] = {}

    tracks.fxrack_add(cvpj_l, 0, "Master", [0.3, 0.3, 0.3], 1.0, None)

    for midi_channum in range(channels):
        fxrack_chan = str(midi_channum+1)
        tracks.fxrack_add(cvpj_l, fxrack_chan, "Channel "+fxrack_chan, [0.3, 0.3, 0.3], 1.0, None)

        s_chan_trackids = t_chan_usedinst_all[midi_channum]

        s_chan_auto = t_chan_auto[midi_channum]

        for s_chan_auto_num in s_chan_auto:
            schannum = s_chan_auto[s_chan_auto_num]

            if s_chan_auto_num == 1: 
                if len(schannum) == 1 and 0 in schannum: tracks.r_param(cvpj_l, schannum[0], 'modulation', schannum[0]/127)
                else: add_auto_to_song_no_mixer(midiauto2cvpjauto(schannum,127,0), 'modulation', midi_channum, s_chan_trackids)

            elif s_chan_auto_num == 7: 
                if len(schannum) == 1 and 0 in schannum: tracks.fxrack_param(cvpj_l, fxrack_chan, 'vol', schannum[0]/127)
                else: add_auto_to_song(midiauto2cvpjauto(schannum,127,0), 'vol', midi_channum, s_chan_trackids)

            elif s_chan_auto_num == 10: 
                if len(schannum) == 1 and 0 in schannum: tracks.r_param(cvpj_l, schannum[0], 'pan', (schannum[0]/64)-1)
                else: add_auto_to_song_no_mixer(midiauto2cvpjauto(schannum,64,-1), 'pan', midi_channum, s_chan_trackids)

            elif s_chan_auto_num == 11: 
                if len(schannum) == 1 and 0 in schannum: tracks.r_param(cvpj_l, schannum[0], 'expression', schannum[0]/127)
                else: add_auto_to_song_no_mixer(midiauto2cvpjauto(schannum,127,0), 'expression', midi_channum, s_chan_trackids)

            elif s_chan_auto_num == 91: 
                wetval = do_slot_wet(schannum, '_reverb', fxrack_chan)
                tracks.add_fxslot_native(cvpj_l, 'audio', 'general-midi', 'fxrack', fxrack_chan, 1, wetval, fxrack_chan+'_reverb', 'reverb', {})

            elif s_chan_auto_num == 92: 
                wetval = do_slot_wet(schannum, '_tremelo', fxrack_chan)
                tracks.add_fxslot_native(cvpj_l, 'audio', 'general-midi', 'fxrack', fxrack_chan, 1, wetval, fxrack_chan+'_tremelo', 'tremelo', {})

            elif s_chan_auto_num == 93: 
                wetval = do_slot_wet(schannum, '_chorus', fxrack_chan)
                tracks.add_fxslot_native(cvpj_l, 'audio', 'general-midi', 'fxrack', fxrack_chan, 1, wetval, fxrack_chan+'_chorus', 'chorus', {})

            elif s_chan_auto_num == 94: 
                wetval = do_slot_wet(schannum, '_detuning', fxrack_chan)
                tracks.add_fxslot_native(cvpj_l, 'audio', 'general-midi', 'fxrack', fxrack_chan, 1, wetval, fxrack_chan+'_detuning', 'detuning', {})

            elif s_chan_auto_num == 95: 
                wetval = do_slot_wet(schannum, '_phaser', fxrack_chan)
                tracks.add_fxslot_native(cvpj_l, 'audio', 'general-midi', 'fxrack', fxrack_chan, 1, wetval, fxrack_chan+'_phaser', 'phaser', {})

            elif s_chan_auto_num == 'pitch':
                add_auto_to_song_no_mixer(midiauto2cvpjauto(s_chan_auto['pitch'],1/8,0), 'pitch', midi_channum, s_chan_trackids)

            #else:
            #    midictname = idvals.get_idval(idvals_midi_ctrl, str(s_chan_auto_num), 'name')
            #    print('unknown controller', s_chan_auto_num, midictname)

    tracks.a_auto_nopl_to_cvpj(cvpj_l)
    cvpj_l['timemarkers'] = s_timemarkers
    cvpj_l['instruments_data'] = cvpj_l_instruments
    cvpj_l['instruments_order'] = cvpj_l_instrumentsorder
    cvpj_l['playlist'] = cvpj_l_playlist
    return cvpj_l