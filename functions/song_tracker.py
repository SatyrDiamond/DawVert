# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_convert
from functions import auto
from functions import note_mod

global used_instruments_num
used_instruments_num = []

global used_instruments
used_instruments = []

def get_used_instruments(): return used_instruments

def get_used_instruments_num(): return used_instruments_num

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

def make_placement_data(pos, dur, nl, current_channelnum):
    if nl != []:
        single_placement = {}
        single_placement['position'] = pos
        single_placement['duration'] = dur
        single_placement['type'] = 'instruments'
        single_placement['notelist'] = nl
        single_placement['name'] = 'Chan #' + str(current_channelnum+1)
        return single_placement
    else:
        return None

def calcslidepower(slidepower, current_speed):
    divfirst = slidepower
    divsec = ((17/current_speed)*1.1)
    return (divfirst/divsec)-(slidepower/17)

def convertchannel2notelist(patterntable_channel, startinststr, current_channelnum):

    patterntable_channel[0][0]['firstrow'] = 1

    output_placements = []
    pos_global = 0
    pos_pl = 0
    pos_note = 0
    changeposition = 0

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

        if notecommand[1][1] != None: 
            lastinst = notecommand[1][1]
        notecommand[1][1] = lastinst

        if 'firstrow' in notecommand[0]:
            if plactive == True:
                placedata = make_placement_data(plpos, pos_pl, cvpj_notelist, current_channelnum+1)
                if placedata != None:
                    output_placements.append(placedata)
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
                cvpj_note = {}
                cvpj_note['position'] = pos_pl
                cvpj_note['duration'] = 0
                cvpj_note['key'] = notecommand[1][0]

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
                        note_mod.pitchmod2point(cvpj_notelist[-1], pos_note, 0, 1, 1, (instparam['slide_down']*-1)/(slidediv/current_speed))
                    if 'slide_up' in instparam: 
                        note_mod.pitchmod2point(cvpj_notelist[-1], pos_note, 0, 1, 1, (instparam['slide_up'])/(slidediv/current_speed))

                cvpj_notelist[-1]['duration'] += 1

            if len(cvpj_notelist) != 0:
                if 'slide_down_c' in instparam: 
                    if instparam['slide_down_c'] != 0: slidecontval = (instparam['slide_down_c']*-1)/(slidediv/current_speed)
                    note_mod.pitchmod2point(cvpj_notelist[-1], pos_note, 0, 1, 1, slidecontval)
                if 'slide_up_c' in instparam: 
                    if instparam['slide_up_c'] != 0: slidecontval = instparam['slide_up_c']/(slidediv/current_speed)
                    note_mod.pitchmod2point(cvpj_notelist[-1], pos_note, 0, 1, 1, slidecontval)
                if 'slide_to_note' in instparam: 
                    if notecommand[1][0] != None: 
                        slidekey = notecommand[1][0]
                    if instparam['slide_to_note'] != 0:
                        slidepower = instparam['slide_to_note']
                    note_mod.pitchmod2point(cvpj_notelist[-1], pos_note, 1, 1, calcslidepower(slidepower, current_speed), slidekey)
                    #print(str(notecommand[1][0])+'|'+str(slidekey).ljust(5), str(instparam['slide_to_note'])+'|'+str(slidepower))

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