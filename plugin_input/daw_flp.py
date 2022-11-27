# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
from functions import riff
from functions import datastore
from functions import notemod
import varint
import json
import struct
from io import BytesIO

def get_decode_text(textbytes):
        try:
            return textbytes.decode('utf-16le').rstrip('\x00')
        except:
            return textbytes.decode('utf-8').rstrip('\x00')

def parse_arrangement(arrangementsbytes):
    arrangementdata = BytesIO()
    arrangementdata.write(arrangementsbytes)
    arrangementdata.seek(0,2)
    arrangementdata_filesize = arrangementdata.tell()
    arrangementdata.seek(0)
    flarrangement = []
    while arrangementdata.tell() < arrangementdata_filesize:
        arrangementJ = {}
        placement_pos = int.from_bytes(arrangementdata.read(4), "little")
        placement_patbase = int.from_bytes(arrangementdata.read(2), "little")
        placement_item_idx = int.from_bytes(arrangementdata.read(2), "little")
        placement_length = int.from_bytes(arrangementdata.read(4), "little")
        placement_track = int.from_bytes(arrangementdata.read(4), "little")
        placement_unknown = int.from_bytes(arrangementdata.read(2), "little")
        placement_flags = int.from_bytes(arrangementdata.read(2), "little")
        placement_unknown2 = int.from_bytes(arrangementdata.read(4), "little")
        placement_start_offset = int.from_bytes(arrangementdata.read(4), "little")
        placement_start_offset_real = placement_start_offset/flp_ppq
        placement_end_offset = int.from_bytes(arrangementdata.read(4), "little")
        placement_end_offset_real = placement_end_offset/flp_ppq
        if placement_start_offset < 100000000 and placement_end_offset < 100000000:
            notecutJ = {}
            notecutJ['start'] = placement_start_offset_real
            notecutJ['end'] = placement_end_offset_real
            arrangementJ['notecut'] = notecutJ
        arrangementJ['fromindex'] = placement_item_idx - placement_patbase
        arrangementJ['position'] = placement_pos/flp_ppq
        arrangementJ['track'] = 499 - placement_track
        flarrangement.append(arrangementJ)
    return flarrangement

def parse_patternnotes(parse_patternnotesbytes):
    notelistdata = BytesIO()
    notelistdata.write(parse_patternnotesbytes)
    notelistdata.seek(0,2)
    notelistdata_filesize = notelistdata.tell()
    notelistdata.seek(0)
    notelist = []
    while notelistdata.tell() < notelistdata_filesize:
        noteJ = {}
        flpattern_pos = int.from_bytes(notelistdata.read(4), "little")/flp_ppq
        flpattern_flags = int.from_bytes(notelistdata.read(2), "little")
        flpattern_rackch = int.from_bytes(notelistdata.read(2), "little")+1
        flpattern_dur = int.from_bytes(notelistdata.read(4), "little")/flp_ppq
        flpattern_key = int.from_bytes(notelistdata.read(4), "little") - 60
        flpattern_finep = int.from_bytes(notelistdata.read(1), "little")
        flpattern_u1 = int.from_bytes(notelistdata.read(1), "little")
        flpattern_rel = int.from_bytes(notelistdata.read(1), "little")
        flpattern_midich = int.from_bytes(notelistdata.read(1), "little")
        flpattern_pan = (int.from_bytes(notelistdata.read(1), "little")-64)/64
        flpattern_velocity = int.from_bytes(notelistdata.read(1), "little")/128
        flpattern_mod_x = int.from_bytes(notelistdata.read(1), "little")
        flpattern_mod_y = int.from_bytes(notelistdata.read(1), "little")
        noteJ['position'] = flpattern_pos
        noteJ['duration'] = flpattern_dur
        noteJ['key'] = flpattern_key
        noteJ['vol'] = flpattern_velocity
        noteJ['pan'] = flpattern_pan
        noteJ['finepitch'] = (flpattern_finep-120)*10
        noteJ['instrument'] = flpattern_rackch
        notelist.append(noteJ)
    #for note in notelist:
    #   print(str(note))
    return notelist

def parse_patternnotes_old(parse_patternnotesbytes):
    notelistdata = BytesIO()
    notelistdata.write(parse_patternnotesbytes)
    notelistdata.seek(0,2)
    notelistdata_filesize = notelistdata.tell()
    notelistdata.seek(0)
    notelist = []
    while notelistdata.tell() < notelistdata_filesize:
        noteJ = {}
        flpattern_position = int.from_bytes(notelistdata.read(4), "little")/flp_ppq
        flpattern_flags = int.from_bytes(notelistdata.read(2), "little")
        flpattern_rack_channel = int.from_bytes(notelistdata.read(2), "little")+1
        flpattern_duration = int.from_bytes(notelistdata.read(4), "little")/flp_ppq
        flpattern_key = int.from_bytes(notelistdata.read(1), "little") - 72
        notelistdata.read(7)
        noteJ['position'] = flpattern_position
        noteJ['duration'] = flpattern_duration
        noteJ['key'] = flpattern_key
        noteJ['instrument'] = flpattern_rack_channel
        #print('position: ', flpattern_position)
        notelist.append(noteJ)
    #for note in notelist:
    #   print(str(note))
    return notelist


def parse_event(datastream):
    event_id = int.from_bytes(datastream.read(1), "little")
    if event_id <= 63 and event_id >= 0: # int8
        event_data = int.from_bytes(eventdatastream.read(1), "little")
    if event_id <= 127 and event_id >= 64 : # int16
        event_data = int.from_bytes(eventdatastream.read(2), "little")
    if event_id <= 191 and event_id >= 128 : # int32
        event_data = int.from_bytes(eventdatastream.read(4), "little")
    if event_id <= 224 and event_id >= 192 : # text
        eventpartdatasize = varint.decode_stream(datastream)
        event_data = datastream.read(eventpartdatasize)
    if event_id <= 255 and event_id >= 225 : # data
        eventpartdatasize = varint.decode_stream(datastream)
        event_data = datastream.read(eventpartdatasize)
    return [event_id, event_data]

class input_flp(plugin_input.base):
    def __init__(self):
        pass

    def getname(self):
        return 'FL Studio'

    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'FLhd':
            return True
        else:
            return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):

        mainjson = {}        
        mainjson['mastervol'] = 1.0
        mainjson['masterpitch'] = 0.0
        mainjson['timesig_numerator'] = 4
        mainjson['timesig_denominator'] = 4
        flp_tempo = 0

        FL_folder = ''

        if extra_param != None:
            if 'extrapath' in extra_param:
                FL_folder = extra_param['extrapath']

        global fileobject
        fileobject = open(input_file, 'rb')
        headername = fileobject.read(4)
        rifftable = riff.readriffdata(fileobject, 0)
        for riffobj in rifftable:
            #print(str(riffobj[0]) + str(len(riffobj[1])))
            if riffobj[0] == b'FLhd':
                global flp_ppq
                flp_ppq = int.from_bytes(riffobj[1][4:6], "little")
                print('[input-flp] PPQ: '+ str(flp_ppq))
            if riffobj[0] == b'FLdt':
                mainevents = riffobj[1]

        global eventdatastream
        eventdatasize = len(mainevents)
        eventdatastream = BytesIO()
        eventdatastream.write(mainevents)
        eventdatastream.seek(0)
        
        flp_patterns = []
        flp_channels = []
        
        current_pattern = None
        current_channel = None
        
        flp_json_playlist = []

        patterns_stepseq = []

        while eventdatastream.tell() < int(eventdatasize):
            eventoutput = parse_event(eventdatastream)
            eventid = eventoutput[0]
            eventdata = eventoutput[1]
            #print(str(eventid) + ' ' + str(eventtable[eventid][1]))
        
            # - Pattern
            if eventid == 65: #NewPat
                current_pattern = eventdata
                #print('NewPat:', eventdata-1)
            if eventid == 193: #PatName
                datastore.add_to_id_json(flp_patterns, 'name' , get_decode_text(eventdata), current_pattern)
                #print('PatName:', eventdata.decode("utf-8"))
            if eventid == 150: #PatColor
                hexcolor = eventdata.to_bytes(4, 'little')
                color = [hexcolor[0]/255,hexcolor[1]/255,hexcolor[2]/255]
                datastore.add_to_id_json(flp_patterns, 'color' , color, current_pattern)
            if eventid == 224: #PatternNotes
                datastore.add_to_id_json(flp_patterns, 'notelist' , parse_patternnotes(eventdata), current_pattern)
        
            # - Pattern

            # - Channel
            if eventid == 64: #NewChan
                current_channel = eventdata
                print('[input-flp] NewChan:',eventdata)
            if eventid == 203: #PluginName
                datastore.add_to_id_json(flp_channels, 'name' , get_decode_text(eventdata), current_channel)
                print('[input-flp] PluginName:',get_decode_text(eventdata))
            if eventid == 128: #Color
                hexcolor = eventdata.to_bytes(4, 'little')
                color = [hexcolor[0]/255,hexcolor[1]/255,hexcolor[2]/255]
                datastore.add_to_id_json(flp_channels, 'color' , color, current_channel)

            if eventid == 21: #ChanType
                if eventdata == 0:
                    datastore.add_to_id_json(flp_channels, 'type' , 0, current_channel)
                    print('[input-flp] ChanType: Sampler')
                if eventdata == 1:
                    datastore.add_to_id_json(flp_channels, 'type' , 1, current_channel)
                    print('[input-flp] ChanType: TS-404')
                if eventdata == 2:
                    datastore.add_to_id_json(flp_channels, 'type' , 2, current_channel)
                    print('[input-flp] ChanType: Plugin-External')
                if eventdata == 3:
                    datastore.add_to_id_json(flp_channels, 'type' , 3, current_channel)
                    print('[input-flp] ChanType: Plugin-Internal')
            if eventid == 196: #SampleFileName
                datastore.add_to_id_json(flp_channels, 'samplefilename' ,FL_folder + get_decode_text(eventdata).replace('\\','/'), current_channel)

            # - Info
            if eventid == 194: #Title
                mainjson['title'] = get_decode_text(eventdata)
                print('[input-flp] Song Title:',get_decode_text(eventdata))

            if eventid == 199: #Version
                print('[input-flp] Version:',eventdata.decode('utf-8').rstrip('\x00'))

            if eventid == 156: #FineTempo
                flp_tempo = eventdata / 1000
                print('[input-flp] FineTempo:', eventdata)

            if eventid == 233: #PlayListItems
                flp_placements = parse_arrangement(eventdata)




        notelistindex_table = []
        instrumentjson_table = []
        
        #[pattern,[channel,pos]]
        for psse in patterns_stepseq:
            #print('StepSeqPattern: ' + str(psse[0]))
            ssp_json = {}
            ssp_json['associd'] = psse[0]
            ss_nl = []
            for psse_pat in psse[1]:
                #print(str(psse_pat[0]),str(psse_pat[1]))
                noteJ = {}
                noteJ['position'] = psse_pat[1]/4
                noteJ['duration'] = 0.25
                noteJ['key'] = 0
                noteJ['instrument'] = psse_pat[0]
                ss_nl.append(noteJ)
            ssp_json['notelist'] = ss_nl
            notelistindex_table.append(ssp_json)

        for flp_pattern in flp_patterns:
            #print('Pattern: ' + str(flp_pattern))\
            patjson = flp_pattern[1]
            notelistindexentryjson = {}
            notelistindexentryjson['associd'] = flp_pattern[0]
            notelistindexentryjson = patjson | notelistindexentryjson
            if 'notelist' in patjson:
                notelistindexentryjson['duration'] = notemod.getduration(patjson['notelist'])
            notelistindex_table.append(notelistindexentryjson)
        
        for flp_channel in flp_channels:
            print('[input-flp] Channel: ' + str(flp_channel[0]))
            instrumentjson = {}
            instrumentjson['associd'] = flp_channel[0]+1
            instrumentjson['color'] = flp_channel[1]['color']
            instrumentjson['name'] = flp_channel[1]['name']
            instrumentjson['vol'] = 1.0
            instrumentjson['type'] = 'instrument'
            instrumentjson_inst = {}
            instrumentjson_inst['plugin'] = "none"
            instrumentjson['instrumentdata'] = instrumentjson_inst
            instrumentjson_table.append(instrumentjson)

        outputplaylist = []
        
        for flpl in flp_placements:
            track = flpl['track']
            del flpl['track']
            datastore.add_to_seperated_object(flp_json_playlist, flpl, track)

        for flp_channel in flp_json_playlist:
            singletrack = {}
            singletrack['placements'] = flp_channel[1]
            outputplaylist.append(singletrack)

        mainjson['bpm'] = flp_tempo
        mainjson['notelistindex'] = notelistindex_table
        mainjson['playlist'] = outputplaylist
        mainjson['instruments'] = instrumentjson_table
        mainjson['cvpjtype'] = 'multiple_indexed'

        return json.dumps(mainjson)
