# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

def get_channeldata_inside_pattern(patterntable_single, channel):
    output_table = []
    position = 0
    patternsize = len(patterntable_single)
    while position < patternsize:
        output_table.append([patterntable_single[position][0][channel], patterntable_single[position][1]])
        position += 1
    return output_table

def entire_song_channel(patterntable_all, channel, orders):
    entire_song_channel_out = []
    for pattern_num in orders:
        patterntable_single = get_channeldata_inside_pattern(patterntable_all[pattern_num], channel)
        for patternrow in patterntable_single:
            entire_song_channel_out.append([patternrow[0], patternrow[1]])
    return entire_song_channel_out

def convertchannel2timednotes(patterntable_channel, tickrow):
    tickrowfinal = (int(tickrow)/6)/4
    output_channel = []
    note_held = 0
    current_inst = None
    current_key = None
    first_seperate = 0
    for notecommand in patterntable_channel:
        if notecommand[0][0] == None:
            if 'firstrow' in notecommand[0][3]:
                if first_seperate == 1:
                    output_channel.append('seperate;')
                if first_seperate == 0:
                    first_seperate = 1
        elif notecommand[0][0] == 'Fade' or notecommand[0][0] == 'Cut' or notecommand[0][0] == 'Off':
            if note_held == 1:
                output_channel.append('note_off;' + str(current_key))
            note_held = 0
            if 'firstrow' in notecommand[0][3]:
                if first_seperate == 1:
                    output_channel.append('seperate;')
                if first_seperate == 0:
                    first_seperate = 1
        else:
            if note_held == 1:
                output_channel.append('note_off;' + str(current_key))
            if 'firstrow' in notecommand[0][3]:
                if first_seperate == 1:
                    output_channel.append('seperate;')
                if first_seperate == 0:
                    first_seperate = 1
            if current_inst != notecommand[0][1] and isinstance(notecommand[0][1], int):
                output_channel.append('instrument;' + str(notecommand[0][1]))
                current_inst = notecommand[0][1]
            note_held = 1
            current_key = notecommand[0][0]
            volume = 1.0
            if "volume" in notecommand[0][2]:
                volume = notecommand[0][2]['volume']
            output_channel.append('note_on;' + str(notecommand[0][0])+','+str(volume))
        output_channel.append('break;' + str(tickrowfinal))
    return output_channel
