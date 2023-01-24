# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
from functions import note_convert
#import time

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

            if 'tracker_speed' in patternrow[0]:
                current_speed = patternrow[0]['tracker_speed']
                speed_changed = True

            if 'tracker_tempo' in patternrow[0]:
                current_tempo = patternrow[0]['tracker_tempo']
                speed_changed = True

            if speed_changed == True:
                if current_speed/6 != 0: tempovalue = current_tempo/(current_speed/6)
                placement_points.append({"position": placement_currentpos, "value": tempovalue, "type": 'instant'})
                speed_changed = False

            if skip_rows == 0:
                tempo_pos += 1
                placement_duration += 1
                placement_currentpos += 1

            if 'tracker_break_to_row' in patternrow[0]:
                if patternrow[0]['tracker_break_to_row'] == 0:
                    skip_rows = 1

    if placement_data != None:
        placement_data['points'] = placement_points
        placement_data['duration'] = placement_duration
        if placement_points != []: tempo_placements.append(placement_data)
    return tempo_placements

def make_placement_data(pos, dur, nl):
    single_placement = {}
    single_placement['position'] = pos
    single_placement['duration'] = dur
    single_placement['type'] = 'instruments'
    single_placement['notelist'] = nl
    return single_placement

def convertchannel2notelist_experement(patterntable_channel, startinststr):
    output_placements = []
    pos_global = 0
    pos_pl = 0
    pos_note = 0
    changeposition = 0

    cvpj_notelist = []

    pos_note = None

    plactive = False
    note_held = 0
    skip_rows = 0
    plpos = 0
    for notecommand in patterntable_channel:

        if 'firstrow' in notecommand[0]:
            if plactive == True:
                output_placements.append(make_placement_data(plpos, pos_pl, cvpj_notelist))
                cvpj_notelist = []
                plactive = False
            pos_pl = 0
            skip_rows = 0
            note_held = 0
            plpos = pos_global
            plactive = True

        if skip_rows == 0:
            if notecommand[1][0] == None:
                pass
            elif notecommand[1][0] == 'Fade' or notecommand[1][0] == 'Cut' or notecommand[1][0] == 'Off':
                note_held = 0
                pos_note = None
            else:
                note_held = 1
                pos_note = -1
                cvpj_note = {}
                cvpj_note['position'] = pos_pl
                cvpj_note['duration'] = 0
                cvpj_note['key'] = notecommand[1][0]
                #if notecommand[1][2] != {}: print(notecommand[1][2])
                if 'vol' in notecommand[1][2]: cvpj_note['vol'] = notecommand[1][2]['vol']
                if 'pan' in notecommand[1][2]: cvpj_note['pan'] = notecommand[1][2]['pan']
                cvpj_note['instrument'] = startinststr+str(notecommand[1][1])
                cvpj_notelist.append(cvpj_note)

            if pos_note != None: pos_note += 1

            pos_pl += 1
            pos_global += 1

            if note_held == 1:
                cvpj_notelist[-1]['duration'] += 1

            #print(str(pos_global).ljust(5), end='')
            #print(str(pos_pl).ljust(5), end='')
            #print(str(pos_note).ljust(5), end='')
            #print(str(len(cvpj_notelist)).ljust(5), end='')
            #print(str(len(output_placements)).ljust(5), end='')
            #print(str(note_held).ljust(2), end='')
            #print(str(skip_rows).ljust(2), end='')
            #print(str(notecommand).ljust(40), end='')
            #print(cvpj_notelist)
            #time.sleep(0.1)

        if 'tracker_break_to_row' in notecommand[0]:
            skip_rows = 1
            note_held = 0


    output_placements.append(make_placement_data(plpos, pos_pl, cvpj_notelist))
    return output_placements

def song2playlist(patterntable_all, number_of_channels, order_list, startinststr, color):
    projL_playlist = {}
    for current_channelnum in range(number_of_channels):
        print('[song-tracker] Converting Channel ' + str(current_channelnum+1))
        note_convert.timednotes2notelistplacement_track_start()
        channelsong = entire_song_channel(patterntable_all,current_channelnum,order_list)
        placements = convertchannel2notelist_experement(channelsong, startinststr)
        projL_playlist[str(current_channelnum+1)] = {}
        projL_playlist[str(current_channelnum+1)]['color'] = color
        projL_playlist[str(current_channelnum+1)]['name'] = 'Channel ' + str(current_channelnum+1)
        projL_playlist[str(current_channelnum+1)]['placements'] = placements
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
            if 'tracker_break_to_row' in patglobalparam:
                if patglobalparam['tracker_break_to_row'] == 0:
                    parserow = 0
        lentable.append(outlen)
    return lentable