# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_convert
from functions import auto
from functions import note_mod

global used_instruments_num
used_instruments_num = []

global used_instruments
used_instruments = []

global multi_used_instruments
multi_used_instruments = []

global slidediv
slidediv = 16

# ----------------------------------------------------------------------------------------------------

def splitbyte(value):
    first = value >> 4
    second = value & 0x0F
    return (first, second)

def getfineval(value):
    volslidesplit = splitbyte(value)
    volslideout = 0
    if volslidesplit[0] == 0 and volslidesplit[1] == 0: volslideout = 0
    elif volslidesplit[0] == 15 and volslidesplit[1] == 15: volslideout = volslidesplit[0]/16
    elif volslidesplit[0] == 0 and volslidesplit[1] == 15: volslideout = -15
    elif volslidesplit[0] == 0 and volslidesplit[1] != 0: volslideout = volslidesplit[1]*-1
    elif volslidesplit[0] != 0 and volslidesplit[1] == 0: volslideout = volslidesplit[0]
    elif volslidesplit[0] == 15 and volslidesplit[1] != 15: volslideout = (volslidesplit[0]*-1)/16
    elif volslidesplit[0] != 15 and volslidesplit[1] == 15: volslideout = volslidesplit[0]/16
    return volslideout

# ----------------------------------------------------------------------------------------------------

def get_used_instruments(): return used_instruments
def get_used_instruments_num(): return used_instruments_num
def get_multi_used_instruments(): return multi_used_instruments

def get_channeldata_inside_pattern(patterntable_single, channel):
    output_table = []
    position = 0
    patternsize = len(patterntable_single)
    while position < patternsize:
        output_table.append([patterntable_single[position][0],patterntable_single[position][1][channel]])
        position += 1
    return output_table

def entire_song_channel(patterntable_all, channel, orders):
    entire_song_channel_out = []
    for pattern_num in orders:
        patterntable_single = get_channeldata_inside_pattern(patterntable_all[pattern_num], channel)
        for patternrow in patterntable_single:
            entire_song_channel_out.append([patternrow[0], patternrow[1]])
    return entire_song_channel_out

def calcslidepower(slidepower, current_speed):
    if current_speed == 0: current_speed = 6
    divfirst = slidepower
    divsec = ((8/current_speed))
    return (divfirst/divsec)-(slidepower/8)

def calcbendpower_up(inval, current_speed):
    if current_speed == 0: current_speed = 6
    global slidediv
    return inval/(slidediv/current_speed)

def calcbendpower_down(inval, current_speed):
    if current_speed == 0: current_speed = 6
    global slidediv
    return (inval*-1)/(slidediv/current_speed)

def make_placement_data(pos, dur, nl, current_channelnum):
    if nl != []:
        single_placement = {}
        single_placement['position'] = pos
        single_placement['duration'] = dur
        single_placement['type'] = 'instruments'
        single_placement['notelist'] = nl
        single_placement['name'] = 'Chan #' + str(current_channelnum+1)
        return single_placement
    else: return None

def convertchannel2notelist(patterntable_channel, startinststr, current_channelnum):
    patterntable_channel[0][0]['firstrow'] = 1

    output_placements = []
    pos_global = 0
    pos_pl = 0
    pos_note = 0

    cvpj_notelist = []

    pos_note = 0
    lastinst = None
    plactive = False
    note_held = 0
    skip_rows = 0
    plpos = 0

    current_speed = 6
    slidecontval = 0

    slidediv = 16

    slidekey = 0
    slidepower = 1

    for notecommand in patterntable_channel:

        if notecommand[1][1] != None:  lastinst = notecommand[1][1]
        notecommand[1][1] = lastinst

        if 'firstrow' in notecommand[0]:
            if plactive == True:
                placedata = make_placement_data(plpos, pos_pl, cvpj_notelist, current_channelnum+1)
                if placedata != None: output_placements.append(placedata)
                cvpj_notelist = []
                plactive = False
            pos_pl = 0
            skip_rows = 0
            note_held = 0
            plpos = pos_global
            plactive = True

        if skip_rows == 0:

            instparam = notecommand[1][2]

            if notecommand[1][0] == None:
                pass 
            elif notecommand[1][0] == 'Fade' or notecommand[1][0] == 'Cut' or notecommand[1][0] == 'Off':
                note_held = 0
                pos_note = 0
            elif 'slide_to_note' not in instparam:
                note_mod.pitchmod2point_init()

                tone_porta_speed = 0
                tone_porta_key = 0

                note_held = 1
                pos_note = -1
                cvpj_note = {'position':pos_pl, 'duration':0, 'key':notecommand[1][0]}

                if 'vol' in notecommand[1][2]: cvpj_note['vol'] = notecommand[1][2]['vol']
                if 'pan' in notecommand[1][2]: cvpj_note['pan'] = notecommand[1][2]['pan']
                cvpj_note['instrument'] = startinststr+str(notecommand[1][1])

                instnumid = notecommand[1][1]
                instid = startinststr+str(notecommand[1][1])
                if instnumid != None:
                    if instnumid not in used_instruments_num: used_instruments_num.append(instnumid)
                    if instid not in used_instruments: used_instruments.append(instid)

                cvpj_notelist.append(cvpj_note)

            if pos_note != None: pos_note += 1

            pos_pl += 1
            pos_global += 1

            if 'speed' in notecommand[0]: 
                current_speed = notecommand[0]['speed']

            if note_held == 1:
                if notecommand[1][0] == None:
                    if 'slide_down' in instparam: 
                        note_mod.pitchmod2point(cvpj_notelist[-1], pos_note, 0, 1, 1, instparam['slide_down'])
                    if 'slide_up' in instparam: 
                        note_mod.pitchmod2point(cvpj_notelist[-1], pos_note, 0, 1, 1, instparam['slide_up'])
                cvpj_notelist[-1]['duration'] += 1

            if len(cvpj_notelist) != 0:
                if 'slide_down_cont' in instparam: 
                    if instparam['slide_down_cont'] != 0: slidecontval = instparam['slide_down_cont']
                    note_mod.pitchmod2point(cvpj_notelist[-1], pos_note, 0, 1, 1, slidecontval)
                if 'slide_up_cont' in instparam:  
                    if instparam['slide_up_cont'] != 0: slidecontval = instparam['slide_up_cont']
                    note_mod.pitchmod2point(cvpj_notelist[-1], pos_note, 0, 1, 1, slidecontval)
                if 'slide_to_note' in instparam: 
                    if notecommand[1][0] != None and notecommand[1][0] != 'Off': slidekey = notecommand[1][0]
                    if instparam['slide_to_note'] != 0: slidepower = instparam['slide_to_note'] 
                    note_mod.pitchmod2point(cvpj_notelist[-1], pos_note, 1, 1, slidepower, slidekey)

            #print(str(pos_global).ljust(5), end='')
            #print(str(pos_pl).ljust(5), end='')
            #print(str(pos_note).ljust(5), end='')
            #print(str(len(cvpj_notelist)).ljust(5), end='')
            #print(str(note_held).ljust(2), end='')
            #print(str(skip_rows).ljust(2), end='')
            #print(str(notecommand).ljust(40))
            #print(cvpj_notelist)
            #time.sleep(0.1)

        if 'break_to_row' in notecommand[0]:
            skip_rows = 1
            note_held = 0

    placedata = make_placement_data(plpos, pos_pl, cvpj_notelist, current_channelnum+1)
    if placedata != None:
        output_placements.append(placedata)
    return output_placements

def song2playlist(patterntable_all, number_of_channels, order_list, startinststr, color):
    projL_playlist = {}
    for current_channelnum in range(number_of_channels):
        print('[song-tracker] Converting Channel ' + str(current_channelnum+1))
        note_convert.timednotes2notelistplacement_track_start()
        channelsong = entire_song_channel(patterntable_all,current_channelnum,order_list)
        placements = convertchannel2notelist(channelsong, startinststr, current_channelnum)
        projL_playlist[str(current_channelnum+1)] = {}
        projL_playlist[str(current_channelnum+1)]['color'] = color
        projL_playlist[str(current_channelnum+1)]['name'] = 'Channel ' + str(current_channelnum+1)
        projL_playlist[str(current_channelnum+1)]['placements_notes'] = placements
    return projL_playlist

def get_len_table(patterntable_all, orders):
    lentable = []
    for pattern_num in orders:
        patterntable_single = patterntable_all[pattern_num]
        outlen = 0
        parserow = 1
        for patternrow in patterntable_single:
            patglobalparam = patternrow[0]
            if parserow == 1:
                outlen += 1
            if 'break_to_row' in patglobalparam:
                if patglobalparam['break_to_row'] == 0:
                    parserow = 0
        lentable.append(outlen)
    return lentable

def tempo_auto(patterntable_all, orders, speed, tempo):
    skip_rows = 0
    tempo_pos = 0

    current_speed = speed
    current_tempo = tempo
    tempovalue = current_tempo/(current_speed/6)

    tempo_placements = []
    placement_data = None
    speed_changed = False

    for pattern_num in orders:
        for patternrow in patterntable_all[pattern_num]:
            if 'firstrow' in patternrow[0]:
                if placement_data != None:
                    placement_data['points'] = placement_points
                    placement_data['duration'] = placement_duration
                    if placement_points != []: tempo_placements.append(placement_data)
                    placement_data = None
                skip_rows = 0
                placement_data = {}
                placement_currentpos = 0
                placement_position = tempo_pos
                placement_duration = 0
                placement_points = []
                placement_data['position'] = placement_position

            if 'speed' in patternrow[0]:
                current_speed = patternrow[0]['speed']
                speed_changed = True

            if 'tempo' in patternrow[0]:
                current_tempo = patternrow[0]['tempo']
                speed_changed = True

            if speed_changed == True:
                if current_speed/6 != 0: tempovalue = current_tempo/(current_speed/6)
                placement_points.append({"position": placement_currentpos, "value": tempovalue, "type": 'instant'})
                speed_changed = False

            if skip_rows == 0:
                tempo_pos += 1
                placement_duration += 1
                placement_currentpos += 1

            if 'break_to_row' in patternrow[0]:
                if patternrow[0]['break_to_row'] == 0:
                    skip_rows = 1

    if placement_data != None:
        placement_data['points'] = placement_points
        placement_data['duration'] = placement_duration

        if placement_points != []: tempo_placements.append(placement_data)

    for tempo_placement in tempo_placements:
        auto.resize(tempo_placement)

    return tempo_placements


def multi_convert(cvpj_l, i_rows, i_patterns, i_orders, i_chantype, i_channames, i_typecolors):
    plnum = 1

    cvpj_l['playlist'] = {}
    cvpj_l_playlist = cvpj_l['playlist']

    cvpj_l['notelistindex'] = {}
    cvpj_l_notelistindex = cvpj_l['notelistindex']

    for channum in range(len(i_chantype)):
        s_chantype = i_chantype[channum]
        s_patterns = i_patterns[channum]
        s_orders = i_orders[channum]

        # --------------- playlist ---------------
        cvpj_l_playlist[plnum] = {}
        cvpj_l_playlist[plnum]['name'] = i_channames[channum]
        if s_chantype in i_typecolors: cvpj_l_playlist[plnum]['color'] = i_typecolors[s_chantype]
        cvpj_l_playlist[plnum]['placements_notes'] = []

        # --------------- notelistindex and placements ---------------

        if channum in s_patterns:
            for s_pattern in s_patterns:

                NLP = convertchannel2notelist(s_patterns[s_pattern], s_chantype+'_', channum)
                used_instruments = get_used_instruments()
                for used_instrument in used_instruments:
                    ui_split = used_instrument.split('_')
                    if ui_split not in multi_used_instruments: multi_used_instruments.append(ui_split)

                if NLP != []:
                    nli_data = {}
                    nli_data['name'] = str(i_channames[channum])+' ('+str(s_pattern)+')'
                    nli_data['color'] = i_typecolors[s_chantype]
                    nli_data['notelist'] = NLP[0]['notelist']
                    cvpj_l_notelistindex[str(channum)+'_'+str(s_pattern)] = nli_data

            curpos = 0
            for s_order in s_orders:
                if s_order in s_patterns:
                    cvpj_l_placement = {}
                    cvpj_l_placement['position'] = curpos
                    cvpj_l_placement['duration'] = i_rows
                    cvpj_l_placement['fromindex'] = str(channum)+'_'+str(s_order)
                    cvpj_l_playlist[plnum]['placements_notes'].append(cvpj_l_placement)
                curpos += i_rows

        # ---------------  ---------------
        plnum += 1


