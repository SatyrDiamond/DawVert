# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os
import math
import json
import xmodits
from functions import tracker
from functions import noteconv

class input_it(plugin_input.base):
    def __init__(self):
        pass

    def getname(self):
        return 'Tracker: Impulse Tracker Module'

    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'IMPM':
            return True
        else:
            return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        it_file = open(input_file, 'rb')

        modulename = os.path.splitext(os.path.basename(input_file))[0]
        
        if 'samplefolder' in extra_param:
            samplefolder = extra_param['samplefolder'] + modulename + '/'
        else:
            samplefolder = os.getcwd() + '/samples/' + modulename + '/'
            os.makedirs(os.getcwd() + '/samples/', exist_ok=True)
        os.makedirs(samplefolder, exist_ok=True)

        header_magic = it_file.read(4)
        if header_magic != b'IMPM':
            print('[error] Not an IT File')
            exit()
        
        header_songname = it_file.read(26).split(b'\x00' * 1)[0].decode("utf-8")
        print("[input-it] Song Name: " + str(header_songname))
        header_hilight_minor = it_file.read(1)
        header_hilight_major = it_file.read(1)
        header_ordnum = int.from_bytes(it_file.read(2), "little")
        print("[input-it] # of Orders: " + str(header_ordnum))
        header_insnum = int.from_bytes(it_file.read(2), "little")
        print("[input-it] # of Instruments: " + str(header_insnum))
        header_smpnum = int.from_bytes(it_file.read(2), "little")
        print("[input-it] # of Samples: " + str(header_smpnum))
        header_patnum = int.from_bytes(it_file.read(2), "little")
        print("[input-it] # of Patterns: " + str(header_patnum))
        
        header_cwtv = int.from_bytes(it_file.read(2), "little")
        header_cmwt = int.from_bytes(it_file.read(2), "little")
        
        header_flags = it_file.read(2)
        header_special = it_file.read(2)
        header_globalvol = int.from_bytes(it_file.read(1), "little")
        header_mv = int.from_bytes(it_file.read(1), "little")
        header_speed = int.from_bytes(it_file.read(1), "little")
        print("[input-it] Speed: " + str(header_speed))
        header_tempo = int.from_bytes(it_file.read(1), "little")
        print("[input-it] Tempo: " + str(header_tempo))
        header_sep = int.from_bytes(it_file.read(1), "little")
        header_pwd = int.from_bytes(it_file.read(1), "little")
        header_msglength = int.from_bytes(it_file.read(2), "little")
        header_msgoffset = int.from_bytes(it_file.read(4), "little")
        header_reserved = int.from_bytes(it_file.read(4), "little")
        chnpan = []
        for _ in range(64):
            chnpan.append(int.from_bytes(it_file.read(1), "little"))
        chnvol = []
        for _ in range(64):
            chnvol.append(int.from_bytes(it_file.read(1), "little"))
        orders = []
        for _ in range(header_ordnum):
            orders.append(int.from_bytes(it_file.read(1), "little"))
        
        offset_instruments = []
        for _ in range(header_insnum):
            offset_instruments.append(int.from_bytes(it_file.read(4), "little"))
        
        offset_samples = []
        for _ in range(header_smpnum):
            offset_samples.append(int.from_bytes(it_file.read(4), "little"))
        
        offset_patterns = []
        for _ in range(header_patnum):
            offset_patterns.append(int.from_bytes(it_file.read(4), "little"))
        
        xmodits.dump(input_file,samplefolder,index_only=True,index_raw=True)

        outputfx = []
        instJ_table = []
        instrumentcount = 0
        
        tabledata_inst = []
        tabledata_sample = []

        instrumentcount = 0
        for offset_instrument in offset_instruments:
            it_file.seek(offset_instrument)
            inst_header = it_file.read(4)
            if inst_header != b'IMPI':
                print('[input-it] Instrument not Valid')
                exit()
            print("[input-it] instrument " + str(instrumentcount) + ': at offset ' + str(offset_instrument))
            inst_filename_dos = it_file.read(12).split(b'\x00' * 1)[0].decode("latin_1")
            it_file.read(16)
            inst_name = it_file.read(26).split(b'\x00' * 1)[0].decode("latin_1")
            tabledata_inst.append([inst_filename_dos,inst_name])
            instrumentcount += 1

        samplecount = 0
        for offset_sample in offset_samples:
            it_file.seek(offset_sample)
            sample_header = it_file.read(4)
            if sample_header != b'IMPS':
                print('[input-it] Sample not Valid')
                exit()
            print("[input-it] Sample " + str(samplecount) + ': at offset ' + str(offset_sample))
            sample_filename_dos = it_file.read(12).split(b'\x00' * 1)[0].decode("latin_1")
            sample_name = it_file.read(26).split(b'\x00' * 1)[0].decode("latin_1")
            tabledata_sample.append([sample_name,sample_filename_dos])
            samplecount += 1

        if len(tabledata_inst) != 0:
            instnotfound = 0
            insttable = tabledata_inst
        else:
            instnotfound = 1
            insttable = tabledata_sample

        instrumentcount = 0
        for instentry in insttable:
            fxchannel = {}
            instJ = {}
            if instentry[0].rstrip() != '':
                fxchannel['name'] = instentry[0].rstrip()
                instJ['name'] = instentry[0].rstrip()
            elif instentry[1].rstrip() != '':
                fxchannel['name'] = instentry[1].rstrip()
                instJ['name'] = instentry[1].rstrip()
            instJ['id'] = 'it_inst_'+str(instrumentcount)
            instJ['associd'] = instrumentcount+1
            instJ['vol'] = 0.3
            instJ['fxrack_channel'] = instrumentcount+1
            instJ['type'] = 'instrument'
            if instnotfound == 0:
                instJ_data = {}
                instJ_data['plugin'] = "none"
            else:
                instJ_data = {}
                instJ_data['plugin'] = "sampler"
                instJ_plugin = {}
                instJ_plugin['file'] = samplefolder + '/' + str(instrumentcount+1).zfill(2) + '.wav'
                instJ_plugin['interpolation'] = "none"
                instJ_data['plugindata'] = instJ_plugin
            instJ_data['basenote'] = 12
            instJ_data['pitch'] = 0
            instJ_data['usemasterpitch'] = 1
            instJ['instrumentdata'] = instJ_data
            fxchannel['num'] = instrumentcount+1
            outputfx.append(fxchannel)
            instJ_table.append(instJ)
            instrumentcount += 1

        patterncount = 1
        patterntable_all = []
        for offset_pattern in offset_patterns:
            print("[input-it] Pattern " + str(patterncount),end=': ')
            patterntable_single = []
            if offset_pattern != 0:
                it_file.seek(offset_pattern)
                pattern_length = int.from_bytes(it_file.read(2), "little")
                pattern_rows = int.from_bytes(it_file.read(2), "little")
                print(str(pattern_rows) + ' Rows',end=', ')
                print('Size: ' + str(pattern_length) + ' at offset ' + str(offset_pattern))
                it_file.read(4)
                firstrow = 1
                rowcount = 0
                table_lastnote = []
                for _ in range(64):
                    table_lastnote.append(None)
                table_lastinstrument = []
                for _ in range(64):
                    table_lastinstrument.append(None)
                table_lastvolpan = []
                for _ in range(64):
                    table_lastvolpan.append(None)
                table_lastcommand = []
                for _ in range(64):
                    table_lastcommand.append([None, None])
                table_previousmaskvariable = []
                for _ in range(64):
                    table_previousmaskvariable.append(None)
                for _ in range(pattern_rows):
                    pattern_done = 0
                    pattern_row_local = []
                    for _ in range(64):
                        pattern_row_local.append([None, None, {}, {}])
                    pattern_row = [pattern_row_local, {}]
                    while pattern_done == 0:
                        channelvariable = bin(int.from_bytes(it_file.read(1), "little"))[2:].zfill(8)
                        cell_previous_maskvariable = int(channelvariable[0:1], 2)
                        cell_channel = int(channelvariable[1:8], 2) - 1
                        if int(channelvariable, 2) == 0:
                            pattern_done = 1
                        else:
                            #print('ch:' + str(cell_channel) + '|', end=' ')
                            if cell_previous_maskvariable == 1:
                                maskvariable = bin(int.from_bytes(it_file.read(1), "little"))[2:].zfill(8)
                                table_previousmaskvariable[cell_channel] = maskvariable
                            else:
                                maskvariable = table_previousmaskvariable[cell_channel]
                            maskvariable_note = int(maskvariable[7], 2) 
                            maskvariable_instrument = int(maskvariable[6], 2)
                            maskvariable_volpan = int(maskvariable[5], 2)
                            maskvariable_command = int(maskvariable[4], 2)
                            maskvariable_last_note = int(maskvariable[3], 2)
                            maskvariable_last_instrument = int(maskvariable[2], 2)
                            maskvariable_last_volpan = int(maskvariable[1], 2)
                            maskvariable_last_command = int(maskvariable[0], 2)
        
                            cell_note = None
                            cell_instrument = None
                            cell_volpan = None
                            cell_commandtype = None
                            cell_commandnum = None
        
                            if maskvariable_note == 1:
                                cell_note = int.from_bytes(it_file.read(1), "little")
                                table_lastnote[cell_channel] = cell_note
                                #print('n=' + str(cell_note), end=' ')
                            if maskvariable_instrument == 1:
                                cell_instrument = int.from_bytes(it_file.read(1), "little")
                                table_lastinstrument[cell_channel] = cell_instrument
                                #print('i=' + str(cell_instrument), end=' ')
                            if maskvariable_volpan == 1:
                                cell_volpan = int.from_bytes(it_file.read(1), "little")
                                table_lastvolpan[cell_channel] = cell_volpan
                                #print('vp=' + str(cell_volpan), end=' ')
                            if maskvariable_command == 1:
                                cell_commandtype = int.from_bytes(it_file.read(1), "little")
                                cell_commandnum = int.from_bytes(it_file.read(1), "little")
                                table_lastcommand[cell_channel] = [cell_commandtype, cell_commandnum]
                                #print('cmdt=' + str(cell_commandtype), end=' ')
                                #print('cmdn=' + str(cell_commandnum), end=' ')
        
        
                            if maskvariable_last_note == 1:
                                cell_note = table_lastnote[cell_channel]
                                #print('n=' + str(cell_note), end=' ')
                            if maskvariable_last_instrument == 1:
                                cell_instrument = table_lastinstrument[cell_channel]
                                #print('i=' + str(cell_instrument), end=' ')
                            if maskvariable_last_volpan == 1:
                                cell_volpan = table_lastvolpan[cell_channel]
                                #print('vp=' + str(cell_volpan), end=' ')
                            if maskvariable_last_command == 1:
                                cell_commandtype = table_lastcommand[cell_channel][0]
                                cell_commandnum = table_lastcommand[cell_channel][1]
                                #print('cmdt=' + str(cell_commandtype), end=' ')
                                #print('cmdn=' + str(cell_commandnum), end=' ')
        
                            if cell_volpan != None:
                                if cell_volpan <= 64:
                                    pattern_row[0][cell_channel][2]['vol'] = cell_volpan/64
                                elif 192 >= cell_volpan >= 128:
                                    pattern_row[0][cell_channel][2]['pan'] = ((cell_volpan-128)/64-0.5)*2
        
                            if cell_note != None:
                                pattern_row[0][cell_channel][0] = cell_note - 48
                            if cell_note == 254:
                                pattern_row[0][cell_channel][0] = 'Cut'
                            if cell_note == 255:
                                pattern_row[0][cell_channel][0] = 'Off'
                            if cell_note == 246:
                                pattern_row[0][cell_channel][0] = 'Fade'
        
                            if cell_instrument != None:
                                pattern_row[0][cell_channel][1] = cell_instrument
                                
                            if cell_commandtype == 1:
                                pattern_row[1]['tracker_speed'] = cell_commandnum
                            if cell_commandtype == 24:
                                pattern_row[0][cell_channel][2]['pan'] = ((cell_commandnum/255)-0.5)*2
                            if firstrow == 1:
                                pattern_row[1]['firstrow'] = 1
                            rowcount += 1
                    firstrow = 0
                    patterntable_single.append(pattern_row)
            patterntable_all.append(patterntable_single)
            patterncount += 1
        
        while 254 in orders:
            orders.remove(254)
        
        while 255 in orders:
            orders.remove(255)
        print("[input-it] Order List: " + str(orders))
        
        outputplaylist = []
        for current_channelnum in range(64):
            print('[input-it] Converting Channel: ' + str(current_channelnum+1))
            noteconv.timednotes2notelistplacement_track_start()
            channelsong = tracker.entire_song_channel(patterntable_all,current_channelnum,orders)
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
        rootJ['timesig_denominator'] = 4
        rootJ['title'] = header_songname
        rootJ['bpm'] = header_tempo
        rootJ['playlist'] = outputplaylist
        rootJ['fxrack'] = outputfx
        rootJ['instruments'] = instJ_table
        rootJ['cvpjtype'] = 'multiple'
        rootJ['mi2s_fixedblock'] = 1
        
        return json.dumps(rootJ)

