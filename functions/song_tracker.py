# SPDX-FileCopyrightText: 2022 SatyrDiamond
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

def convertchannel2timednotes(patterntable_channel, startinststr):
    output_channel = []
    note_held = 0
    current_inst = None
    current_key = None
    first_seperate = 0
    for notecommand in patterntable_channel:
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
    return output_channel

def song2playlist(patterntable_all, number_of_channels, order_list, startinststr, color):
    projL_playlist = {}
    for current_channelnum in range(number_of_channels):
        print('[func-tracker] Converting Channel ' + str(current_channelnum+1))
        note_convert.timednotes2notelistplacement_track_start()
        channelsong = entire_song_channel(patterntable_all,current_channelnum,order_list)
        timednotes = convertchannel2timednotes(channelsong, startinststr)
        placements = note_convert.timednotes2notelistplacement_parse_timednotes(timednotes)
        projL_playlist[str(current_channelnum+1)] = {}
        projL_playlist[str(current_channelnum+1)]['color'] = color
        projL_playlist[str(current_channelnum+1)]['name'] = 'Channel ' + str(current_channelnum+1)
        projL_playlist[str(current_channelnum+1)]['placements'] = placements
    return projL_playlist