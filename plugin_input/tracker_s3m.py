# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import json
from functions import tracker
from functions import noteconv

class input_s3m(plugin_input.base):
    def __init__(self):
        pass

    def getname(self):
        return 'Tracker: Scream Tracker 3 Module'

    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(44)
        bytesdata = bytestream.read(4)
        if bytesdata == b'SCRM':
            return True
        else:
            return False
        bytestream.seek(0)

    def parse(self, input_file):
        s3mfile = open(input_file, 'rb')

        samplefolder = os.path.splitext(os.path.abspath(input_file))[0]
        
        name = s3mfile.read(28).split(b'\x00' * 1)[0].decode("utf-8")
        print("Input-StreamTracker3 | Song Name: " + str(name))
        sig1 = s3mfile.read(1)
        type = s3mfile.read(1)
        reserved = int.from_bytes(s3mfile.read(2), "little")
        orderCount = int.from_bytes(s3mfile.read(2), "little")
        instrumentCount = int.from_bytes(s3mfile.read(2), "little")
        patternPtrCount = int.from_bytes(s3mfile.read(2), "little")
        flags = s3mfile.read(2)
        trackerVersion = s3mfile.read(2)
        sampleType = int.from_bytes(s3mfile.read(2), "little")
        sig2 = s3mfile.read(4)
        globalVolume = int.from_bytes(s3mfile.read(1), "little")
        initialSpeed = int.from_bytes(s3mfile.read(1), "little")
        initialTempo = int.from_bytes(s3mfile.read(1), "little")
        masterVolume = s3mfile.read(1)
        ultraClickRemoval = int.from_bytes(s3mfile.read(1), "little")
        defaultPan = s3mfile.read(1)
        reserved2 = s3mfile.read(8)
        ptrSpecial = int.from_bytes(s3mfile.read(2), "little")
        channelSettings = s3mfile.read(32)
        
        orderListBytes = s3mfile.read(orderCount)
        orderList = []
        for orderListByte in orderListBytes:
            orderList.append(orderListByte)
        
        while 255 in orderList:
            orderList.remove(255)
        print("Input-StreamTracker3 | Order List: " + str(orderList))
        
        ptrInstruments = []
        for _ in range(instrumentCount):
            ptrInstruments.append(int.from_bytes(s3mfile.read(2), "little")*16)
        print("Input-StreamTracker3 | Instruments: " + str(len(ptrInstruments)))
        if instrumentCount > 255:
            print('Input-StreamTracker3 | Not a S3M File')
            exit()
        
        ptrPatterns = []
        for _ in range(patternPtrCount):
            ptrPatterns.append(int.from_bytes(s3mfile.read(2), "little")*16)
        print("Input-StreamTracker3 | Patterns: " + str(len(ptrPatterns)))
        if patternPtrCount > 255:
            print('Input-StreamTracker3 | Not a S3M File')
            exit()
        
        instrumentjson_table = []
        outputfx = []
        outputplaylist = []
        
        defualtvolume = []
        
        instrumentcount = 0
        for ptrInstrument in ptrInstruments:
            fxchannel = {}
            s3mfile.seek(ptrInstrument)
            instrumentjson = {}
            instrumenttype = int.from_bytes(s3mfile.read(1), "little")
            instrument_volume = 1.0
            instrumentfilenamebytes = s3mfile.read(12)
            if instrumenttype == 0 or instrumenttype == 1:
                instrument_ptrDataH = int.from_bytes(s3mfile.read(1), "little")
                instrument_ptrDataL = int.from_bytes(s3mfile.read(2), "little")
                instrument_length = int.from_bytes(s3mfile.read(4), "little")
                instrument_loopStart = int.from_bytes(s3mfile.read(4), "little")
                instrument_loopEnd = int.from_bytes(s3mfile.read(4), "little")
                instrument_volume = int.from_bytes(s3mfile.read(1), "little")/64
                instrument_reserved = int.from_bytes(s3mfile.read(1), "little")
                instrument_pack = int.from_bytes(s3mfile.read(1), "little")
                instrument_flags = int.from_bytes(s3mfile.read(1), "little")
                instrument_c2spd = int.from_bytes(s3mfile.read(4), "little")
                instrument_internal = s3mfile.read(12)
                instrument_namebytes = s3mfile.read(28)
                instrument_sig = s3mfile.read(4)
            try:
                instrument_filename = instrumentfilenamebytes.split(b'\x00' * 1)[0].decode("utf-8")
                instrument_trackname = instrument_filename
            except:
                instrument_filename = ''
                instrument_trackname = str(instrumentcount)
            try:
                instrument_name = instrument_namebytes.split(b'\x00' * 1)[0].decode("utf-8")
            except:
                instrument_name = ''
            instrumentjson['id'] = instrumentcount+1
            instrumentjson['name'] = instrument_trackname
            instrumentjson['fxrack_channel'] = instrumentcount+1
            instrumentjson['volume'] = 0.3
            instrumentjson_inst = {}
            instrumentjson_inst['plugin'] = "sampler"
            instrumentjson_inst['basenote'] = 60
            instrumentjson_inst['pitch'] = 0
            instrumentjson_inst['usemasterpitch'] = 1
            instrumentjson_inst_plugindata = {}
            instrumentjson_inst_plugindata['file'] = samplefolder + '/' + str(instrumentcount+1).zfill(2) + '.wav'
            instrumentjson_inst['plugindata'] = instrumentjson_inst_plugindata
            instrumentjson['instrumentdata'] = instrumentjson_inst
            instrumentjson_table.append(instrumentjson)
            fxchannel['name'] = instrument_name
            fxchannel['num'] = instrumentcount+1
            outputfx.append(fxchannel)
            print("Input-StreamTracker3 | Inst: " + str(instrumentcount) + " | Type: " + str(instrumenttype) + " | Name: " + instrument_name + " | Filename: " + instrument_filename)
            defualtvolume.append(instrument_volume)
            instrumentcount += 1
        
        patterncount = 1
        patterntable_all = []
        print("Input-StreamTracker3 | Pattern:",end=' ')
        for ptrPattern in ptrPatterns:
            print(str(patterncount),end=' ')
            patterntable_single = []
            if ptrPattern != 0:
                s3mfile.seek(ptrPattern)
                pattern_packed_len = int.from_bytes(s3mfile.read(2), "little")
                firstrow = 1
                rowcount = 0
                for _ in range(64):
                    pattern_done = 0
                    pattern_row_local = []
                    for _ in range(32):
                        pattern_row_local.append([None, None, {}, {}])
                    pattern_row = [pattern_row_local, {}]
                    while pattern_done == 0:
                        packed_what = bin(int.from_bytes(s3mfile.read(1), "little"))[2:].zfill(8)
                        if int(packed_what, 2) == 0:
                            pattern_done = 1
                        else:
                            packed_what_command_info = int(packed_what[0], 2)
                            packed_what_volume = int(packed_what[1], 2)
                            packed_what_note_instrument = int(packed_what[2], 2)
                            packed_what_channel = int(packed_what[3:8], 2)
        
                            packed_note = None
                            packed_instrument = None
                            packed_volume = None
                            packed_command = None
                            packed_info = None
        
                            if packed_what_note_instrument == 1:
                                packed_note = int.from_bytes(s3mfile.read(1), "little")
                                if packed_note == 255:
                                    packed_note = None
        
                            if packed_what_note_instrument == 1:
                                packed_instrument = int.from_bytes(s3mfile.read(1), "little")
                                if packed_instrument == 0:
                                    packed_instrument = None
                            if packed_what_volume == 1:
                                packed_volume = int.from_bytes(s3mfile.read(1), "little")
        
                            if packed_what_command_info == 1:
                                packed_command = int.from_bytes(s3mfile.read(1), "little")
                            if packed_what_command_info == 1:
                                packed_info = int.from_bytes(s3mfile.read(1), "little")
                            if packed_note != None:
                                bits_packed_note = bin(packed_note)[2:].zfill(8)
                                bits_packed_note_oct = int(bits_packed_note[0:4], 2)-4
                                bits_packed_note_tone = int(bits_packed_note[4:8], 2)
                                final_note = bits_packed_note_oct*12 + bits_packed_note_tone
                                if packed_note == 254:
                                    pattern_row[0][packed_what_channel][0] = 'Cut'
                                else:
                                    pattern_row[0][packed_what_channel][0] = final_note
                            if packed_instrument != None:
                                pattern_row[0][packed_what_channel][1] = packed_instrument
                            if packed_volume != None:
                                pattern_row[0][packed_what_channel][2]['volume'] = packed_volume/64
                            else:
                                if packed_instrument != None:
                                    pattern_row[0][packed_what_channel][2]['volume'] = defualtvolume[packed_instrument-1]
                                else:
                                    pattern_row[0][packed_what_channel][2]['volume'] = 1.0
                            if firstrow == 1:
                                pattern_row[0][packed_what_channel][3]['firstrow'] = 1
                                pattern_row[1]['firstrow'] = 1
        
                            if packed_what_command_info == 1 and packed_command == 1:
                                pattern_row[0][packed_what_channel][3]['tracker_speed'] = packed_info
                                pattern_row[1]['tracker_speed'] = packed_info
        
                            #print(packed_what_command_info, packed_what_volume, packed_what_note_instrument, packed_what_channel)
                    firstrow = 0
                    patterntable_single.append(pattern_row)
                    rowcount += 1
            patterntable_all.append(patterntable_single)
            patterncount += 1
        print(' ')
        
        for current_channelnum in range(31):
            print('Input-StreamTracker3 | Channel ' + str(current_channelnum+1) + ': ', end='')
            noteconv.timednotes2notelistplacement_track_start()
            channelsong = tracker.entire_song_channel(patterntable_all,current_channelnum,orderList)
            timednotes = tracker.convertchannel2timednotes(channelsong,initialSpeed)
            placements = noteconv.timednotes2notelistplacement_parse_timednotes(timednotes)
            singletrack = {}
            singletrack['name'] = "Channel " + str(current_channelnum+1)
            singletrack['muted'] = 0
            print(str(len(placements)) + ' Placements')
            singletrack['placements'] = placements
            outputplaylist.append(singletrack)
        
        mainjson = {}
        mainjson['mastervol'] = 1.0
        mainjson['masterpitch'] = 0.0
        mainjson['timesig_numerator'] = 4
        mainjson['timesig_denominator'] = 6
        mainjson['title'] = name
        mainjson['bpm'] = initialTempo
        mainjson['playlist'] = outputplaylist
        mainjson['fxrack'] = outputfx
        mainjson['instruments'] = instrumentjson_table
        mainjson['convprojtype'] = 'multiple'

        return json.dumps(mainjson)