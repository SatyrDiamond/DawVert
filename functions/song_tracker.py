# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later
from functions import note_convert

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
    for pattern_num in orders:
        for patternrow in patterntable_all[pattern_num]:
            if 'firstrow' in patternrow[0]:
                if placement_data != None:
                    placement_data['points'] = placement_points
                    placement_data['duration'] = placement_duration
                    tempo_placements.append(placement_data)
                    placement_data = None
                skip_rows = 0
                placement_data = {}
                placement_currentpos = 0
                placement_position = tempo_pos
                placement_duration = 0
                placement_points = []
                placement_data['position'] = placement_position

            if 'tracker_break_to_row' in patternrow[0]:
                if patternrow[0]['tracker_break_to_row'] == 0:
                    skip_rows = 1

            if 'tracker_speed' in patternrow[0]:
                current_speed = patternrow[0]['tracker_speed']

                placement_points.append({"position": placement_currentpos-0.01, "value": tempovalue})
                tempovalue = current_tempo/(current_speed/6)
                placement_points.append({"position": placement_currentpos, "value": tempovalue})

            if skip_rows == 0:
                tempo_pos += 1
                placement_duration += 1
                placement_currentpos += 1
    return tempo_placements

def convertchannel2timednotes(patterntable_channel, startinststr):
    output_channel = []
    note_held = 0
    current_inst = None
    current_key = None
    first_seperate = 0
    skip_rows = 0
    for notecommand in patterntable_channel:
        if 'firstrow' in notecommand[0]:
            skip_rows = 0
        if skip_rows == 0:
            if notecommand[1][0] == None:
                if 'firstrow' in notecommand[0]:
                    if first_seperate == 1: output_channel.append('seperate;')
                    if first_seperate == 0: first_seperate = 1
            elif notecommand[1][0] == 'Fade' or notecommand[1][0] == 'Cut' or notecommand[1][0] == 'Off':
                if note_held == 1:
                    output_channel.append('note_off;' + str(current_key))
                note_held = 0
                if 'firstrow' in notecommand[0]:
                    if first_seperate == 1: output_channel.append('seperate;')
                    if first_seperate == 0: first_seperate = 1
            else:
                if note_held == 1:
                    output_channel.append('note_off;' + str(current_key))
                if 'firstrow' in notecommand[0]:
                    if first_seperate == 1: output_channel.append('seperate;')
                    if first_seperate == 0: first_seperate = 1
                if current_inst != notecommand[1][1] and isinstance(notecommand[1][1], int):
                    output_channel.append('instrument;' + startinststr + str(notecommand[1][1]))
                    current_inst = notecommand[1][1]
                note_held = 1
                current_key = notecommand[1][0]
                vol = 1.0
                if "vol" in notecommand[1][2]: vol = notecommand[1][2]['vol']
                if "pan" in notecommand[1][2]: output_channel.append('pan;' + str(notecommand[1][2]['pan']))
                output_channel.append('note_on;' + str(notecommand[1][0])+','+str(vol))
            output_channel.append('break;' + str(1))
        if 'tracker_break_to_row' in notecommand[0]:
            if notecommand[0]['tracker_break_to_row'] == 0:
                skip_rows = 1
    return output_channel

def song2playlist(patterntable_all, number_of_channels, order_list, startinststr, color):
    projL_playlist = {}
    for current_channelnum in range(number_of_channels):
        print('[song-tracker] Converting Channel ' + str(current_channelnum+1))
        note_convert.timednotes2notelistplacement_track_start()
        channelsong = entire_song_channel(patterntable_all,current_channelnum,order_list)
        timednotes = convertchannel2timednotes(channelsong, startinststr)
        placements = note_convert.timednotes2notelistplacement_parse_timednotes(timednotes, '')
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