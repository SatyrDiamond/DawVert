# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os
import math
import json
from functions import tracker
from functions import noteconv
from io import BytesIO

def parse_xm_cell(databytes):
    cell_note = None
    cell_instrument = None
    cell_vol = None
    cell_effect = None
    cell_param = None

    packed_first = int.from_bytes(databytes.read(1), "little")
    packed_flags = bin(packed_first)[2:].zfill(8)

    packed_note = int(packed_flags[7], 2) 
    packed_instrument = int(packed_flags[6], 2)
    packed_vol = int(packed_flags[5], 2)
    packed_effect = int(packed_flags[4], 2)
    packed_param = int(packed_flags[3], 2)
    packed_msb = int(packed_flags[0], 2)
    if packed_msb == 1:
        if packed_note == 1:
            cell_note = int.from_bytes(databytes.read(1), "little")
        if packed_instrument == 1:
            cell_instrument = int.from_bytes(databytes.read(1), "little")
        if packed_vol == 1:
            cell_vol = int.from_bytes(databytes.read(1), "little")
        if packed_effect == 1:
            cell_effect = int.from_bytes(databytes.read(1), "little")
        if packed_param == 1:
            cell_param = int.from_bytes(databytes.read(1), "little")
    else:
        cell_note = packed_first
        cell_instrument = int.from_bytes(databytes.read(1), "little")
        cell_vol = int.from_bytes(databytes.read(1), "little")
        cell_effect = int.from_bytes(databytes.read(1), "little")
        cell_param = int.from_bytes(databytes.read(1), "little")

    output_note = cell_note
    if cell_note != None:
        if cell_note == 97:
            output_note = 'Off'
        else:
            output_note = cell_note - 49
    output_inst = cell_instrument
    output_param = {}
    output_extra = {}

    #print(cell_note,cell_instrument,cell_vol,cell_effect,cell_param)

    if cell_param != None:
        if cell_effect == 15:
            if 31 >= cell_param:
                output_extra['tracker_speed'] = cell_param

        if cell_effect == 8:
            if cell_param:
                output_param['pan'] = ((cell_param/255)-0.5)*2

        if cell_effect == 12:
            if cell_param:
                output_param['vol'] = (cell_param)/64

    if cell_vol != None:
        if 80 >= cell_vol >= 16:
            output_param['vol'] = (cell_vol-16)/64

    return [output_note, output_inst, output_param, output_extra]

def parse_xm_row(xmdata, numchannels,firstrow):
    table_row = []
    globaljson = {}
    for channel in range(numchannels):
        if firstrow == 1:
            globaljson['firstrow'] = 1
        celldata = parse_xm_cell(xmdata)
        rowdata_global = celldata[3]
        globaljson = rowdata_global | globaljson
        table_row.append(celldata)
    return [table_row, globaljson]

def parse_xm_row_none(numchannels,firstrow):
    table_row = []
    globaljson = {}
    for channel in range(numchannels):
        if firstrow == 1:
            globaljson['firstrow'] = 1
        celldata = [None, None, {}, {}]
        table_row.append(celldata)
    return [table_row, globaljson]



class input_xm(plugin_input.base):
    def __init__(self):
        pass

    def getname(self):
        return 'Tracker: Extended Module'

    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(17)
        if bytesdata == b'Extended Module: ':
            return True
        else:
            return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        xmfile = open(input_file, 'rb')

        modulename = os.path.splitext(os.path.basename(input_file))[0]
        if 'samplefolder' in extra_param:
            samplefolder = extra_param['samplefolder'] + modulename + '/'
        else:
            samplefolder = os.getcwd() + '/samples/' + modulename + '/'
            os.makedirs(os.getcwd() + '/samples/', exist_ok=True)
        os.makedirs(samplefolder, exist_ok=True)

        header_magic = xmfile.read(17)
        if header_magic != b'Extended Module: ':
            print('Not an XM File')
            exit()
        header_songname = xmfile.read(20).split(b'\x00' * 1)[0].decode("utf-8")
        print("[input-xm] Song Name: " + str(header_songname))
        header_id = xmfile.read(1)
        header_trackername = xmfile.read(20).split(b'\x00' * 1)[0].decode("utf-8")
        print("[input-xm] Tracker Name: " + str(header_trackername))
        header_trackerrevision_high = int.from_bytes(xmfile.read(1), "little")
        header_trackerrevision_low = int.from_bytes(xmfile.read(1), "little")
        print("[input-xm] Tracker Revision: " + str(header_trackerrevision_low) + "." + str(header_trackerrevision_high))
        if header_trackerrevision_high != 4 and header_trackerrevision_low != 1: 
            print("Error | Tracker Revision Not 1.4")
            exit()
        header_headersize = int.from_bytes(xmfile.read(4), "little")
        print("[input-xm] Header Size: " + str(header_headersize))
        header_songlength_in_patterns = int.from_bytes(xmfile.read(2), "little")
        print("[input-xm] Song Length in Patterns: " + str(header_songlength_in_patterns))
        header_restart_position = int.from_bytes(xmfile.read(2), "little")
        print("[input-xm] Restart Position: " + str(header_restart_position))
        header_number_of_channels = int.from_bytes(xmfile.read(2), "little")
        print("[input-xm] # of Channels: " + str(header_number_of_channels))
        header_number_of_patterns = int.from_bytes(xmfile.read(2), "little")
        print("[input-xm] # of Patterns: " + str(header_number_of_patterns))
        header_number_of_instruments = int.from_bytes(xmfile.read(2), "little")
        print("[input-xm] # of Instruments: " + str(header_number_of_instruments))
        header_flags = int.from_bytes(xmfile.read(2), "little")
        print("[input-xm] Flags: " + str(header_flags))
        header_speed = int.from_bytes(xmfile.read(2), "little")
        print("[input-xm] Speed: " + str(header_speed))
        header_bpm = int.from_bytes(xmfile.read(2), "little")
        print("[input-xm] Tempo: " + str(header_bpm))
        order_list = []
        for number in range(256):
            ordernum = int.from_bytes(xmfile.read(1), "little")
            if number < header_songlength_in_patterns:
                order_list.append(ordernum)
        print("[input-xm] Order List: " + str(order_list))
        
        xmdata_patterns = []
        
        for header_number_of_pattern in range(header_number_of_patterns):
            pattern_headerlength = int.from_bytes(xmfile.read(4), "little")
            pattern_packingtype = int.from_bytes(xmfile.read(1), "little")
            if pattern_packingtype != 0:
                print("Error | Not a standard .XM file (possibly saved with OpenMPT)")
                exit()
            pattern_number_of_rows = int.from_bytes(xmfile.read(2), "little")
            if pattern_packingtype > 256:
                print("Error | Not a standard .XM file (possibly saved with OpenMPT)")
                exit()
            pattern_packed_data_size = int.from_bytes(xmfile.read(2), "little")
            currentdatapos = xmfile.tell()
            xmdata_packeddata = None
            if pattern_packed_data_size != 0:
                xmdata_packeddata = xmfile.read(pattern_packed_data_size)
            xmdata_patterns.append([pattern_headerlength, pattern_number_of_rows, xmdata_packeddata])
        
        outputfx = []
        instJ_table = []
        instrumentcount = 0
        
        for instnumber in range(header_number_of_instruments):
            fxchannel = {}
            instJ = {}
            instJ['id'] = 'xm_inst_'+str(instrumentcount)
            instJ['associd'] = instrumentcount+1
            instJ['vol'] = 0.3
            instJ['fxrack_channel'] = instrumentcount+1
            instJ['type'] = 'instrument'
            instJ_data = {}
            instJ_data['plugin'] = "none"
            instJ_data['basenote'] = 0
            instJ_data['pitch'] = 0
            instJ_data['usemasterpitch'] = 1
            instJ['instrumentdata'] = instJ_data
            fxchannel['name'] = str(instrumentcount+1)
            fxchannel['num'] = instrumentcount+1
            outputfx.append(fxchannel)
            instJ_table.append(instJ)
            instrumentcount += 1
        
        
        patterntable_all = []
        
        for xmdata_pattern in xmdata_patterns:
            xmdata_patterndata = BytesIO()
            if xmdata_pattern[2] != None:
                xmdata_patterndata.write(xmdata_pattern[2])
                xmdata_patterndata.seek(0)
                patterntable_single = []
                pattern_firstrow = 1
                for row in range(xmdata_pattern[1]):
                    patterntable_single.append(parse_xm_row(xmdata_patterndata, header_number_of_channels, pattern_firstrow))
                    pattern_firstrow = 0
                patterntable_all.append(patterntable_single)
            else:
                patterntable_single = []
                pattern_firstrow = 1
                for row in range(xmdata_pattern[1]):
                    patterntable_single.append(parse_xm_row_none(header_number_of_channels, pattern_firstrow))
                    pattern_firstrow = 0
                patterntable_all.append(patterntable_single)
        
        outputplaylist = []
        for current_channelnum in range(header_number_of_channels):
            print('[input-xm] Converting Channel: ' + str(current_channelnum+1))
            noteconv.timednotes2notelistplacement_track_start()
            channelsong = tracker.entire_song_channel(patterntable_all,current_channelnum,order_list)
            timednotes = tracker.convertchannel2timednotes(channelsong,header_speed)
            placements = noteconv.timednotes2notelistplacement_parse_timednotes(timednotes)
            trkJ = {}
            trkJ['name'] = "Channel " + str(current_channelnum+1)
            trkJ['placements'] = placements
            outputplaylist.append(trkJ)
        
        rootJ = {}
        rootJ['mastervol'] = 1.0
        rootJ['masterpitch'] = 0.0
        rootJ['timesig_numerator'] = 4
        rootJ['timesig_denominator'] = 6
        rootJ['title'] = header_songname
        rootJ['bpm'] = header_bpm
        rootJ['playlist'] = outputplaylist
        rootJ['fxrack'] = outputfx
        rootJ['instruments'] = instJ_table
        rootJ['cvpjtype'] = 'multiple'
        rootJ['mi2s_fixedblock'] = 1
        
        return json.dumps(rootJ)
        
