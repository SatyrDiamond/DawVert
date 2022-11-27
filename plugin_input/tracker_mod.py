# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import math
import json
import wave
import numpy as np
from functions import tracker
from functions import noteconv

def parse_mod_cell(modfile, firstrow):
    output_note = None
    output_inst = None
    output_param = {}
    output_extra = {}
    if firstrow == 1:
        output_extra['firstrow'] = 1
    cell_p1 = int.from_bytes(modfile.read(2), "big")
    cell_p2 = int.from_bytes(modfile.read(2), "big")
    sample_low = cell_p2 >> 12
    sample_high = cell_p1 >> 12
    period = (cell_p1 & 0x0FFF) 
    if period != 0:
        note_period = 447902/(period*2)
        output_note = (round(12 * math.log2(note_period / 440)) + 69)-72
    effect_type = (cell_p2 & 0xF00) >> 8
    effect_parameter = (cell_p2 & 0xFF) 
    samplenum = sample_high << 4 | sample_low
    if samplenum != 0:
        output_inst = samplenum

    if effect_type == 0 and effect_parameter != 0:
        arpeggio_first = effect_parameter >> 4
        arpeggio_second = effect_parameter & 0x0F
        output_param['tracker_arpeggio'] = [arpeggio_first, arpeggio_second]
    if effect_type == 1:
        output_param['tracker_slide_up'] = effect_parameter
    if effect_type == 2:
        output_param['tracker_slide_down'] = effect_parameter
    if effect_type == 3:
        output_param['tracker_slide_to_note'] = effect_parameter
    if effect_type == 4:
        vibrato_speed = effect_parameter >> 4
        vibrato_depth = effect_parameter & 0x0F
        vibrato_params = {}
        vibrato_params['speed'] = vibrato_speed
        vibrato_params['depth'] = vibrato_depth
        output_param['vibrato'] = vibrato_params
    if effect_type == 5:
        pos = effect_parameter >> 4
        neg = effect_parameter & 0x0F
        output_param['tracker_vol_slide_plus_slide_to_note'] = (neg*-1) + pos
    if effect_type == 6:
        pos = effect_parameter >> 4
        neg = effect_parameter & 0x0F
        output_param['tracker_vol_slide_plus_vibrato'] = (neg*-1) + pos
    if effect_type == 7:
        tremolo_speed = effect_parameter >> 4
        tremolo_depth = effect_parameter & 0x0F
        tremolo_params = {}
        tremolo_params['speed'] = tremolo_speed
        tremolo_params['depth'] = tremolo_depth
        output_param['tremolo'] = tremolo_params
    if effect_type == 8:
        output_param['pan'] = (effect_parameter-128)/128
    if effect_type == 9:
        output_param['audio_sample_offset'] = effect_parameter*256
    if effect_type == 10:
        pos = effect_parameter >> 4
        neg = effect_parameter & 0x0F
        output_param['tracker_vol_slide'] = (neg*-1) + pos
    if effect_type == 11:
        output_extra['tracker_jump_to_offset'] = effect_parameter
    #if output_inst != None:
    #   output_param['vol'] = samples[output_inst-1][3]/64
    if effect_type == 12:
        output_param['vol'] = effect_parameter/64
    if effect_type == 13:
        output_extra['tracker_break_to_row'] = effect_parameter
    if effect_type == 15:
        if effect_parameter < 32:
            output_extra['tracker_speed'] = effect_parameter
        else:
            output_extra['tempo'] = effect_parameter
    return [output_note, output_inst, output_param, output_extra]

def parse_mod_row(modfile, firstrow):
    global table_singlepattern
    global number_of_channels
    table_row = []
    globaljson = {}
    for channel in range(number_of_channels):
        celldata = parse_mod_cell(modfile, firstrow)
        rowdata_global = celldata[3]
        globaljson = rowdata_global | globaljson
        table_row.append(celldata)
    return [table_row, globaljson]

def parse_pattern(modfile):
    global table_singlepattern
    table_singlepattern = []
    firstrow = 1
    for row in range(64):
        table_singlepattern.append(parse_mod_row(modfile, firstrow))
        firstrow = 0

def parse_song(modfile):
    print("[input-mod] Decoding Pattern:",end=' ')
    table_patterns = []
    for pattern in range(number_of_patterns+1):
        print(str(pattern),end=' ')
        parse_pattern(modfile)
        table_patterns.append(table_singlepattern)
    print(' ')
    return table_patterns

class input_mod(plugin_input.base):
    def __init__(self):
        pass

    def getname(self):
        return 'Tracker: Protracker Module'

    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(20)
        IsMod = 1
        for _ in range(31):
            bytestream.read(24)
            sample_finetune = int.from_bytes(bytestream.read(1), "big")
            if 15 < sample_finetune:
                IsMod = 0
            sample_defaultvol = int.from_bytes(bytestream.read(1), "big")
            if 64 < sample_defaultvol:
                IsMod = 0
            bytestream.read(4)
        if IsMod == 1:
            return True
        else:
            return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        global number_of_patterns
        global number_of_channels

        modulename = os.path.splitext(os.path.basename(input_file))[0]
        if 'samplefolder' in extra_param:
            samplefolder = extra_param['samplefolder'] + modulename + '/'
        else:
            samplefolder = os.getcwd() + '/samples/' + modulename + '/'
            os.makedirs(os.getcwd() + '/samples/', exist_ok=True)
        os.makedirs(samplefolder, exist_ok=True)

        modfile = open(input_file, 'rb')
        name = modfile.read(20).decode().rstrip('\x00')
        print("[input-mod] Song Name: " + str(name))
        samples = []
        bpm = 125
        print("[input-mod] Tempo: " + str(bpm))
        instrumentcount = 0
        for _ in range(31):
            sample_name = modfile.read(22).decode().rstrip('\x00')
            sample_length = int.from_bytes(modfile.read(2), "big")
            sample_finetune = int.from_bytes(modfile.read(1), "big")
            sample_defaultvol = int.from_bytes(modfile.read(1), "big")
            sample_loopstart = int.from_bytes(modfile.read(2), "big")
            sample_looplength = int.from_bytes(modfile.read(2), "big")
            print('[input-mod] Inst #' + str(instrumentcount) + ', Name:"' + sample_name + '"')
            samples.append([sample_name, sample_length, sample_finetune, sample_defaultvol, sample_loopstart, sample_looplength])
            instrumentcount += 1
        order_list_length = int.from_bytes(modfile.read(1), "big")
        extravalue = int.from_bytes(modfile.read(1), "big")
        order_list = []
        for number in range(128):
            ordernum = int.from_bytes(modfile.read(1), "big")
            if number < order_list_length:
                order_list.append(ordernum)
        print("[input-mod] Order List: " + str(order_list))
        sample_tag = modfile.read(4).decode()
        number_of_patterns = max(order_list)
        print("[input-mod] Patterns: " + str(number_of_patterns))
        number_of_channels = 4
        
        if sample_tag == '6CHN':
            number_of_channels = 6
        if sample_tag == '8CHN':
            number_of_channels = 8
        if sample_tag == 'CD81':
            number_of_channels = 8
        if sample_tag == 'OKTA':
            number_of_channels = 8
        if sample_tag == 'OCTA':
            number_of_channels = 8
        if sample_tag == '6CHN':
            number_of_channels = 6
        if sample_tag[-2:] == 'CH':
            number_of_channels = int(sample_tag[:2])
        if sample_tag == '2CHN':
            number_of_channels = 2
        if sample_tag[-2:] == 'CN':
            number_of_channels = int(sample_tag[:2])
        if sample_tag == 'TDZ1':
            number_of_channels = 1
        if sample_tag == 'TDZ2':
            number_of_channels = 2
        if sample_tag == 'TDZ3':
            number_of_channels = 3
        if sample_tag == '5CHN':
            number_of_channels = 5
        if sample_tag == '7CHN':
            number_of_channels = 7
        if sample_tag == '9CHN':
            number_of_channels = 9
        if sample_tag == 'FLT4':
            number_of_channels = 4
        if sample_tag == 'FLT8':
            number_of_channels = 8
        print("[input-mod] Sample Tag: " + str(sample_tag))
        print("[input-mod] Channels: " + str(number_of_channels))

        patterntable_all = parse_song(modfile)
        patterntable = patterntable_all[0]
        
        print("[input-mod] Ripping Sample:",end=' ')
        for sample in range(31):
            print(str(sample),end=' ')
            os.makedirs(os.getcwd() + '/samples/', exist_ok=True)
            os.makedirs(samplefolder, exist_ok=True)
            wavpath = samplefolder + str(sample+1).zfill(2) + '.wav'
            wavobj = wave.open(wavpath,'wb')
            wavobj.setsampwidth(1)
            wavobj.setnchannels(1)
            wavobj.setframerate(8272)
            sampledata = modfile.read(samples[sample][1]*2)
            sampledatabytes = np.frombuffer(sampledata, dtype='uint8')
            sampledatabytes = np.array(sampledatabytes) + 128
            unsignedsampledata = sampledatabytes.tobytes('C')
            wavobj.writeframesraw(unsignedsampledata)
            wavobj.close()
        print()

        current_channelnum = 0
        
        outputplaylist = []
        outputfx = []
        outputinsts = []
        
        veryfirstrow = patterntable_all[order_list[0]][0][1]
        
        if 'tempo' in veryfirstrow:
            bpm = veryfirstrow['tempo']
            print("[input-mod] Tempo Found: " + str(bpm))

        for current_channelnum in range(number_of_channels):
            print('[input-mod] Converting Channel ' + str(current_channelnum+1))
            noteconv.timednotes2notelistplacement_track_start()
            channelsong = tracker.entire_song_channel(patterntable_all,current_channelnum,order_list)
            timednotes = tracker.convertchannel2timednotes(channelsong,6)
            placements = noteconv.timednotes2notelistplacement_parse_timednotes(timednotes)
            singletrack = {}
            singletrack['name'] = "Channel " + str(current_channelnum+1)
            singletrack['placements'] = placements
            outputplaylist.append(singletrack)
        
        for sample in range(31):
            strsample = str(sample+1)
            trkJp = {}
            trkJp['plugin'] = "sampler"
            trkJp['basenote'] = 0
            trkJp['pitch'] = 0
            trkJp['usemasterpitch'] = 1
            trkJp_plugindata = {}
            trkJp_plugindata['file'] = samplefolder + '/' + strsample.zfill(2) + '.wav'
            trkJp['plugindata'] = trkJp_plugindata
            trkJ = {}
            trkJ['id'] = 'mod_inst_'+str(instrumentcount)
            trkJ['associd'] = sample+1
            trkJ['fxrack_channel'] = sample+1
            trkJ['vol'] = 0.3
            samplename = samples[sample][0]
            if samplename != '':
                trkJ['name'] = samplename
            trkJ['instrumentdata'] = trkJp
            outputinsts.append(trkJ)
            fxchannel = {}
            fxchannel['name'] = samplename
            fxchannel['num'] = sample+1
            outputfx.append(fxchannel)

        rootJ = {}
        rootJ['mastervol'] = 1.0
        rootJ['masterpitch'] = 0.0
        rootJ['timesig_numerator'] = 4
        rootJ['timesig_denominator'] = 4
        rootJ['title'] = name
        rootJ['bpm'] = bpm
        rootJ['playlist'] = outputplaylist
        rootJ['fxrack'] = outputfx
        rootJ['instruments'] = outputinsts
        rootJ['cvpjtype'] = 'multiple'
        rootJ['mi2s_fixedblock'] = 1
        
        return json.dumps(rootJ)
