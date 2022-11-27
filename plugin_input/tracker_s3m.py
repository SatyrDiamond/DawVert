# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import json
import wave
import numpy as np
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

    def parse(self, input_file, extra_param):
        s3mfile = open(input_file, 'rb')

        modulename = os.path.splitext(os.path.basename(input_file))[0]
        if 'samplefolder' in extra_param:
            samplefolder = extra_param['samplefolder'] + modulename + '/'
        else:
            samplefolder = os.getcwd() + '/samples/' + modulename + '/'
            os.makedirs(os.getcwd() + '/samples/', exist_ok=True)
        os.makedirs(samplefolder, exist_ok=True)

        name = s3mfile.read(28).split(b'\x00' * 1)[0].decode("utf-8")
        print("[input-st3] Song Name: " + str(name))
        sig1 = s3mfile.read(1)
        type = s3mfile.read(1)
        reserved = int.from_bytes(s3mfile.read(2), "little")
        header_numorder = int.from_bytes(s3mfile.read(2), "little")
        header_numinst = int.from_bytes(s3mfile.read(2), "little")
        header_numpat = int.from_bytes(s3mfile.read(2), "little")
        header_flags = s3mfile.read(2)
        header_trkrvers = s3mfile.read(2)
        header_samptype = int.from_bytes(s3mfile.read(2), "little")
        header_sig2 = s3mfile.read(4)
        header_globalvol = int.from_bytes(s3mfile.read(1), "little")
        header_speed = int.from_bytes(s3mfile.read(1), "little")
        header_tempo = int.from_bytes(s3mfile.read(1), "little")
        print("[input-st3] Tempo: " + str(header_tempo))
        header_mastervol = s3mfile.read(1)
        header_ultraclickremoval = int.from_bytes(s3mfile.read(1), "little")
        header_defaultpan = s3mfile.read(1)
        header_reserved2 = s3mfile.read(8)
        header_numspecial = int.from_bytes(s3mfile.read(2), "little")
        header_chnlsettings = s3mfile.read(32)
        
        orderListBytes = s3mfile.read(header_numorder)
        orderList = []
        for orderListByte in orderListBytes:
            orderList.append(orderListByte)
        
        while 255 in orderList:
            orderList.remove(255)
        print("[input-st3] Order List: " + str(orderList))
        
        ptrInstruments = []
        for _ in range(header_numinst):
            ptrInstruments.append(int.from_bytes(s3mfile.read(2), "little")*16)
        print("[input-st3] Instruments: " + str(len(ptrInstruments)))
        if header_numinst > 255:
            print('[error] Not a S3M File')
            exit()
        
        ptrPatterns = []
        for _ in range(header_numpat):
            ptrPatterns.append(int.from_bytes(s3mfile.read(2), "little")*16)
        print("[input-st3] Patterns: " + str(len(ptrPatterns)))
        if header_numpat > 255:
            print('[error] Not a S3M File')
            exit()
        
        instJ_table = []
        outputfx = []
        outputplaylist = []
        
        defualtvol = []
        
        header_numinst = 0
        for ptrInstrument in ptrInstruments:
            fxchannel = {}
            s3mfile.seek(ptrInstrument)
            instJ = {}
            instrumenttype = int.from_bytes(s3mfile.read(1), "little")
            inst_vol = 1.0
            instrumentfilenamebytes = s3mfile.read(12)
            if instrumenttype == 0 or instrumenttype == 1:
                inst_ptrDataH = s3mfile.read(1)
                inst_ptrDataL = s3mfile.read(2)
                samplelocation = int.from_bytes(inst_ptrDataL + inst_ptrDataH, "little")*16
                inst_length = int.from_bytes(s3mfile.read(4), "little")
                inst_loopStart = int.from_bytes(s3mfile.read(4), "little")
                inst_loopEnd = int.from_bytes(s3mfile.read(4), "little")
                inst_vol = int.from_bytes(s3mfile.read(1), "little")/64
                inst_reserved = int.from_bytes(s3mfile.read(1), "little")
                inst_pack = int.from_bytes(s3mfile.read(1), "little")
                inst_flags = bin(int.from_bytes(s3mfile.read(1), "little"))[2:].zfill(8)
                inst_16bit = int(inst_flags[5], 2)
                inst_stereo = int(inst_flags[6], 2)
                inst_loopon = int(inst_flags[7], 2)
                inst_c2spd = int.from_bytes(s3mfile.read(4), "little")
                inst_internal = s3mfile.read(12)
                inst_namebytes = s3mfile.read(28)
                inst_sig = s3mfile.read(4)
            try:
                inst_filename = instrumentfilenamebytes.split(b'\x00' * 1)[0].decode("utf-8")
            except:
                inst_filename = ''
            try:
                inst_name = inst_namebytes.split(b'\x00' * 1)[0].decode("utf-8")
            except:
                inst_name = ''
            inst_trackname = inst_filename
            if inst_trackname != '':
                instJ['name'] = inst_trackname
            instJ['id'] = 's3m_inst_'+str(header_numinst)
            instJ['associd'] = header_numinst+1
            instJ['fxrack_channel'] = header_numinst+1
            instJ['vol'] = 0.3
            instJ_data = {}
            instJ_data['plugin'] = "sampler"
            instJ_data['basenote'] = 0
            instJ_data['pitch'] = 0
            instJ_data['usemasterpitch'] = 1
            instJ_plugin = {}
            instJ_plugin['file'] = samplefolder + '/' + str(header_numinst+1).zfill(2) + '.wav'
            instJ_data['plugindata'] = instJ_plugin
            instJ['instrumentdata'] = instJ_data
            instJ_table.append(instJ)
            fxchannel['name'] = inst_name
            fxchannel['num'] = header_numinst+1
            outputfx.append(fxchannel)
            if instrumenttype == 0:
                print("[input-st3] Message #" + str(header_numinst) + ': "' + inst_name + '", Filename:"' + inst_filename+ '"')
            else:
                print("[input-st3] Inst #" + str(header_numinst) + ': "' + inst_name + '", Filename:"' + inst_filename+ '"')
            defualtvol.append(inst_vol)

            if samplelocation != 0 and inst_length != 0:
                print("[input-st3] Ripping Sample " + str(header_numinst))
                s3mfile.seek(samplelocation)
                os.makedirs(os.getcwd() + '/samples/', exist_ok=True)
                os.makedirs(samplefolder, exist_ok=True)
                wavpath = samplefolder + str(header_numinst+1).zfill(2) + '.wav'
                wavobj = wave.open(wavpath,'wb')
                if inst_16bit == 0:
                    wavobj.setsampwidth(1)
                    wavobj.setnchannels(1)
                    wavobj.setframerate(inst_c2spd)
                    sampledata = s3mfile.read(inst_length)
                    if header_samptype == 1:
                        sampledatabytes = np.frombuffer(sampledata, dtype='uint8')
                        sampledatabytes = np.array(sampledatabytes) + 128
                        unsignedsampledata = sampledatabytes.tobytes('C')
                        wavobj.writeframesraw(unsignedsampledata)
                    if header_samptype == 2:
                        wavobj.writeframesraw(sampledata)
                if inst_16bit == 1:
                    wavobj.setsampwidth(2)
                    wavobj.setnchannels(1)
                    wavobj.setframerate(inst_c2spd)
                    sampledata = s3mfile.read(inst_length*2)
                    if header_samptype == 2:
                        sampledatabytes = np.frombuffer(sampledata, dtype='uint16')
                        sampledatabytes = np.array(sampledatabytes) + 32768
                        unsignedsampledata = sampledatabytes.tobytes('C')
                        wavobj.writeframesraw(unsignedsampledata)
                    if header_samptype == 1:
                        wavobj.writeframesraw(sampledata)
                wavobj.close()
            header_numinst += 1

        patterncount = 1
        patterntable_all = []
        print("[input-st3] Decoding Pattern:",end=' ')
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
                            packed_what_vol = int(packed_what[1], 2)
                            packed_what_note_instrument = int(packed_what[2], 2)
                            packed_what_channel = int(packed_what[3:8], 2)
        
                            packed_note = None
                            packed_instrument = None
                            packed_vol = None
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
                            if packed_what_vol == 1:
                                packed_vol = int.from_bytes(s3mfile.read(1), "little")
        
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
                            if packed_vol != None:
                                pattern_row[0][packed_what_channel][2]['vol'] = packed_vol/64
                            else:
                                if packed_instrument != None:
                                    pattern_row[0][packed_what_channel][2]['vol'] = defualtvol[packed_instrument-1]
                                else:
                                    pattern_row[0][packed_what_channel][2]['vol'] = 1.0
                            if firstrow == 1:
                                pattern_row[0][packed_what_channel][3]['firstrow'] = 1
                                pattern_row[1]['firstrow'] = 1
        
                            if packed_what_command_info == 1 and packed_command == 1:
                                pattern_row[0][packed_what_channel][3]['tracker_speed'] = packed_info
                                pattern_row[1]['tracker_speed'] = packed_info
        
                            #print(packed_what_command_info, packed_what_vol, packed_what_note_instrument, packed_what_channel)
                    firstrow = 0
                    patterntable_single.append(pattern_row)
                    rowcount += 1
            patterntable_all.append(patterntable_single)
            patterncount += 1
        print(' ')
        
        for current_channelnum in range(31):
            print('[input-st3] Converting Channel: ' + str(current_channelnum+1))
            noteconv.timednotes2notelistplacement_track_start()
            channelsong = tracker.entire_song_channel(patterntable_all,current_channelnum,orderList)
            timednotes = tracker.convertchannel2timednotes(channelsong,header_speed)
            placements = noteconv.timednotes2notelistplacement_parse_timednotes(timednotes)
            trkJ = {}
            trkJ['name'] = "Channel " + str(current_channelnum+1)
            trkJ['placements'] = placements
            outputplaylist.append(trkJ)
        
        rootJ = {}
        rootJ['mastervol'] = header_globalvol/64
        rootJ['masterpitch'] = 0.0
        rootJ['timesig_numerator'] = 4
        rootJ['timesig_denominator'] = 6
        rootJ['title'] = name
        rootJ['bpm'] = header_tempo
        rootJ['playlist'] = outputplaylist
        rootJ['fxrack'] = outputfx
        rootJ['instruments'] = instJ_table
        rootJ['cvpjtype'] = 'multiple'
        rootJ['mi2s_fixedblock'] = 1
        
        return json.dumps(rootJ)
