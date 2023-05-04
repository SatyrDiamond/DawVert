# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import varint
import argparse
import struct
from io import BytesIO
from functions import data_bytes

# ------------- Functions -------------
def create_bytesio(data):
    bytesio = BytesIO()
    bytesio.write(data)
    bytesio.seek(0,2)
    bytesio_filesize = bytesio.tell()
    bytesio.seek(0)
    return [bytesio, bytesio_filesize]

def calctempotimed(i_value):
    global FL_Main
    i_tempomul = FL_Main['Tempo']/120
    i_out = (i_value*i_tempomul)/125
    #print('VALUE', str(i_value).ljust(20), '| MUL', str(i_tempomul).ljust(20), '| OUT', str(i_out).ljust(20))
    return i_out

# ------------- parse -------------
def parse_arrangement(arrdata):
    bio_fldata = create_bytesio(arrdata)
    output = []
    while bio_fldata[0].tell() < bio_fldata[1]:
        placement = {}
        placement['position'] = int.from_bytes(bio_fldata[0].read(4), "little")
        placement['patternbase'] = int.from_bytes(bio_fldata[0].read(2), "little")
        placement['itemindex'] = int.from_bytes(bio_fldata[0].read(2), "little")
        placement['length'] = int.from_bytes(bio_fldata[0].read(4), "little")
        placement['trackindex'] = int.from_bytes(bio_fldata[0].read(4), "little")
        placement['unknown1'] = int.from_bytes(bio_fldata[0].read(2), "little")
        placement['flags'] = int.from_bytes(bio_fldata[0].read(2), "little")
        placement['unknown2'] = int.from_bytes(bio_fldata[0].read(2), "little")
        placement['unknown3'] = int.from_bytes(bio_fldata[0].read(2), "little")

        startoffset_bytes = bio_fldata[0].read(4)
        endoffset_bytes = bio_fldata[0].read(4)

        startoffset = int.from_bytes(startoffset_bytes, "little")
        endoffset = int.from_bytes(endoffset_bytes, "little")
        startoffset_float = struct.unpack('<f', startoffset_bytes)[0]
        endoffset_float = struct.unpack('<f', endoffset_bytes)[0]

        if placement['itemindex'] > placement['patternbase']:
            if startoffset != 4294967295 and startoffset != 3212836864: placement['startoffset'] = startoffset
            if endoffset != 4294967295 and endoffset != 3212836864: placement['endoffset'] = endoffset
        else:
            if startoffset_float > 0: placement['startoffset'] = calctempotimed(startoffset_float)
            if endoffset_float > 0: placement['endoffset'] = calctempotimed(endoffset_float)
        output.append(placement)
    return output

def parse_chanparams(chanparams, chanl):
    bio_chanparams = create_bytesio(chanparams)[0]
    bio_chanparams.read(9) # ffffffff 00000000 00 
    chanl['remove_dc'] = int.from_bytes(bio_chanparams.read(1), "little")
    chanl['delayflags'] = int.from_bytes(bio_chanparams.read(1), "little")
    chanl['main_pitch'] = int.from_bytes(bio_chanparams.read(1), "little")
    bio_chanparams.read(28) # ffffffff3c0000000000803f0000803f0000803f0000803f0000803f
    chanl['arpdirection'] = int.from_bytes(bio_chanparams.read(4), "little")
    chanl['arprange'] = int.from_bytes(bio_chanparams.read(4), "little")
    chanl['arpchord'] = int.from_bytes(bio_chanparams.read(4), "little")
    chanl['arptime'] = int.from_bytes(bio_chanparams.read(4), "little")
    chanl['arpgate'] = int.from_bytes(bio_chanparams.read(4), "little")
    chanl['arpslide'] = int.from_bytes(bio_chanparams.read(1), "little")
    bio_chanparams.read(1) # 00
    chanl['timefull_porta'] = int.from_bytes(bio_chanparams.read(1), "little")
    chanl['addtokey'] = int.from_bytes(bio_chanparams.read(1), "little")
    chanl['timegate'] = int.from_bytes(bio_chanparams.read(2), "little")
    bio_chanparams.read(2) # 05 00
    chanl['keyrange_min'] = int.from_bytes(bio_chanparams.read(4), "little")
    chanl['keyrange_max'] = int.from_bytes(bio_chanparams.read(4), "little")
    bio_chanparams.read(4) # 00 00 00 00
    chanl['normalize'] = int.from_bytes(bio_chanparams.read(1), "little")
    chanl['reversepolarity'] = int.from_bytes(bio_chanparams.read(1), "little")
    bio_chanparams.read(1) # 00
    chanl['declickmode'] = int.from_bytes(bio_chanparams.read(1), "little")
    chanl['crossfade'] = int.from_bytes(bio_chanparams.read(4), "little")
    chanl['trim'] = int.from_bytes(bio_chanparams.read(4), "little")
    chanl['arprepeat'] = int.from_bytes(bio_chanparams.read(4), "little")
    chanl['stretchingtime'] = int.from_bytes(bio_chanparams.read(4), "little")
    chanl['stretchingpitch'] = int.from_bytes(bio_chanparams.read(4), "little")
    chanl['stretchingmultiplier'] = int.from_bytes(bio_chanparams.read(4), "little", signed="True")
    chanl['stretchingmode'] = int.from_bytes(bio_chanparams.read(4), "little", signed="True")
    bio_chanparams.read(21) # b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff'
    chanl['start'] = bio_chanparams.read(4)
    bio_chanparams.read(4) # b'\x00\x00\x00\x00'
    chanl['length'] = bio_chanparams.read(4)
    bio_chanparams.read(3) # b'\x00\x00\x00'
    chanl['start_offset'] = bio_chanparams.read(4)
    bio_chanparams.read(5) # b'\xff\xff\xff\xff\x00'
    chanl['fix_trim'] = int.from_bytes(bio_chanparams.read(1), "little")

def parse_basicparams(basicparamsdata, chanl):
    bio_basicparams = create_bytesio(basicparamsdata)[0]
    chanl['pan'] = ((int.from_bytes(bio_basicparams.read(4), "little")/12800)-0.5)*2
    chanl['volume'] = (int.from_bytes(bio_basicparams.read(4), "little")/12800)
    chanl['pitch'] = int.from_bytes(bio_basicparams.read(4), "little", signed="True")

def parse_poly(polydata, chanl):
    bio_poly = create_bytesio(polydata)[0]
    chanl['polymax'] = int.from_bytes(bio_poly.read(4), "little")
    chanl['polyslide'] = int.from_bytes(bio_poly.read(4), "little")
    chanl['polyflags'] = int.from_bytes(bio_poly.read(1), "little")

def parse_trackinfo(trackdata):
    bio_fltrack = create_bytesio(trackdata)[0]
    params = {}
    trackid = int.from_bytes(bio_fltrack.read(4), "little")
    params['color'] = int.from_bytes(bio_fltrack.read(4), "little")
    params['icon'] = int.from_bytes(bio_fltrack.read(4), "little")
    params['enabled'] = int.from_bytes(bio_fltrack.read(1), "little")
    params['height'] = struct.unpack('<f', bio_fltrack.read(4))[0]
    params['lockedtocontent'] = int.from_bytes(bio_fltrack.read(1), "little")
    params['motion'] = int.from_bytes(bio_fltrack.read(4), "little")
    params['press'] = int.from_bytes(bio_fltrack.read(4), "little")
    params['triggersync'] = int.from_bytes(bio_fltrack.read(4), "little")
    params['queued'] = int.from_bytes(bio_fltrack.read(4), "little")
    params['tolerant'] = int.from_bytes(bio_fltrack.read(4), "little")
    params['positionSync'] = int.from_bytes(bio_fltrack.read(4), "little")
    params['grouped'] = int.from_bytes(bio_fltrack.read(1), "little")
    params['locked'] = int.from_bytes(bio_fltrack.read(1), "little")
    if params['color'] == 5656904 and params['icon'] == 0 and params['enabled'] == 1 and params['height'] == 1.0 and params['lockedtocontent'] == 255 and params['motion'] == 16777215 and params['press'] == 0 and params['triggersync'] == 0 and params['queued'] == 5 and params['tolerant'] == 0 and params['positionSync'] == 1 and params['grouped'] == 0 and params['locked'] == 0:
        return [trackid, None]
    else:
        return [trackid, params]

def parse_fxrouting(fxroutingbytes):
    fxroutingdata = create_bytesio(fxroutingbytes)
    fxcount = 0
    routes = []
    while fxroutingdata[0].tell() < fxroutingdata[1]:
        fxchannel = int.from_bytes(fxroutingdata[0].read(1), "little")
        if fxchannel == 1:
            routes.append(fxcount)
        fxcount += 1
    return routes

def parse_flevent(datastream):
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

def parse(inputfile):
    global FL_Main
    fileobject = open(inputfile, 'rb')
    headername = fileobject.read(4)
    rifftable = data_bytes.riff_read(fileobject, 0)
    for riffobj in rifftable:
        ##print(str(riffobj[0]) + str(len(riffobj[1])))
        if riffobj[0] == b'FLhd':
            ##print('Channels:', int.from_bytes(riffobj[1][0:3], "big"))
            flp_ppq = int.from_bytes(riffobj[1][4:6], "little")
            ##print('PPQ:',str(flp_ppq))
        if riffobj[0] == b'FLdt':
            mainevents = riffobj[1]
            global eventdatastream
            eventdatasize = len(mainevents)
            eventdatastream = BytesIO()
            eventdatastream.write(mainevents)
            eventdatastream.seek(0)
            eventtable = []
            while eventdatastream.tell() < int(eventdatasize):
                event_id = int.from_bytes(eventdatastream.read(1), "little")
                if event_id <= 63 and event_id >= 0: # int8
                    event_data = int.from_bytes(eventdatastream.read(1), "little")
                if event_id <= 127 and event_id >= 64 : # int16
                    event_data = int.from_bytes(eventdatastream.read(2), "little")
                if event_id <= 191 and event_id >= 128 : # int32
                    event_data = int.from_bytes(eventdatastream.read(4), "little")
                if event_id <= 224 and event_id >= 192 : # text
                    eventpartdatasize = varint.decode_stream(eventdatastream)
                    event_data = eventdatastream.read(eventpartdatasize)
                if event_id <= 255 and event_id >= 225 : # data
                    eventpartdatasize = varint.decode_stream(eventdatastream)
                    event_data = eventdatastream.read(eventpartdatasize)
                eventtable.append([event_id, event_data])
    
    FL_Main = {}
    FL_Channels = {}
    #FL_Tracks = {}
    FL_Patterns = {}
    FL_Mixer = {}
    for fxnum in range(127):
        FL_Mixer[str(fxnum)] = {}

    TimeMarker_id = 0
    FL_Arrangements = {}
    FL_FXCreationMode = 0
    FL_TimeMarkers = {}
    FL_ChanGroupName = []
    T_FL_FXNum = -1

    for event in eventtable:
        event_id = event[0]
        event_data = event[1]

        if event_id == 199: 
            FLVersion = event_data.decode('utf-8').rstrip('\x00')
            FLSplitted = FLVersion.split('.')
            if int(FLSplitted[0]) < 20:
                print('[error] FL version '+FLSplitted[0]+' is not supported.') 
                exit()
            FL_Main['Version'] = FLVersion
        if event_id == 156: FL_Main['Tempo'] = event_data/1000
        if event_id == 80: FL_Main['MainPitch'] = event_data
        if event_id == 17: FL_Main['Numerator'] = event_data
        if event_id == 18: FL_Main['Denominator'] = event_data
        if event_id == 11: FL_Main['Shuffle'] = event_data
        if event_id == 194: FL_Main['Title'] = event_data.decode('utf-16le').rstrip('\x00\x00')
        if event_id == 206: FL_Main['Genre'] = event_data.decode('utf-16le').rstrip('\x00\x00')
        if event_id == 207: FL_Main['Author'] = event_data.decode('utf-16le').rstrip('\x00\x00')
        if event_id == 202: FL_Main['ProjectDataPath'] = event_data.decode('utf-16le').rstrip('\x00\x00')
        if event_id == 195: FL_Main['Comment'] = event_data.decode('utf-16le').rstrip('\x00\x00')
        if event_id == 197: FL_Main['URL'] = event_data.decode('utf-16le').rstrip('\x00\x00')
        if event_id == 237: FL_Main['ProjectTime'] = event_data
        if event_id == 10: FL_Main['ShowInfo'] = event_data
        if event_id == 231: FL_ChanGroupName.append(event_data.decode('utf-16le').rstrip('\x00\x00'))

        if event_id == 65: 
            T_FL_CurrentPattern = event_data
            if str(T_FL_CurrentPattern) not in FL_Patterns:
                FL_Patterns[str(T_FL_CurrentPattern)] = {}
            #print('Pattern:', event_data)
        if event_id == 223: #AutomationData
            #print('\\__AutomationData')
            autodata = create_bytesio(event_data)
            autopoints = []
            while autodata[0].tell() < autodata[1]:
                pointdata = {}
                pointdata['pos'] = int.from_bytes(autodata[0].read(4), "little")
                pointdata['control'] = autodata[0].read(4)
                pointdata['value'] = autodata[0].read(4)
                autopoints.append(pointdata)
            if str(T_FL_CurrentPattern) not in FL_Patterns:
                FL_Patterns[str(T_FL_CurrentPattern)] = {}
            FL_Patterns[str(T_FL_CurrentPattern)]['automation'] = autopoints

        if event_id == 224: #PatternNotes
            #print('\\__PatternNotes')
            fl_notedata = create_bytesio(event_data)
            notelist = []
            while fl_notedata[0].tell() < fl_notedata[1]:
                notedata = {}
                notedata['pos'] = int.from_bytes(fl_notedata[0].read(4), "little")
                notedata['flags'] = int.from_bytes(fl_notedata[0].read(2), "little")
                notedata['rack'] = int.from_bytes(fl_notedata[0].read(2), "little")
                notedata['dur'] = int.from_bytes(fl_notedata[0].read(4), "little")
                notedata['key'] = int.from_bytes(fl_notedata[0].read(2), "little")
                notegroup = int.from_bytes(fl_notedata[0].read(2), "little")
                if notegroup != 0: notedata['group'] = notegroup
                notedata['finep'] = int.from_bytes(fl_notedata[0].read(1), "little")
                notedata['u1'] = int.from_bytes(fl_notedata[0].read(1), "little")
                notedata['rel'] = int.from_bytes(fl_notedata[0].read(1), "little")
                notedata['midich'] = int.from_bytes(fl_notedata[0].read(1), "little")
                notedata['pan'] = int.from_bytes(fl_notedata[0].read(1), "little")
                notedata['velocity'] = int.from_bytes(fl_notedata[0].read(1), "little")
                notedata['mod_x'] = int.from_bytes(fl_notedata[0].read(1), "little")
                notedata['mod_y'] = int.from_bytes(fl_notedata[0].read(1), "little")
                notelist.append(notedata)
            FL_Patterns[str(T_FL_CurrentPattern)]['notes'] = notelist
    
        if event_id == 150: 
            if event_data != 5328737:
                FL_Patterns[str(T_FL_CurrentPattern)]['color'] = event_data
        if event_id == 193: 
            FL_Patterns[str(T_FL_CurrentPattern)]['name'] = event_data.decode('utf-16le').rstrip('\x00\x00')

        if event_id == 99: 
            T_FL_CurrentArrangement = event_data
            #print('NewArrangement:', event_data)
            if str(T_FL_CurrentArrangement) not in FL_Arrangements:
                FL_Arrangements[str(T_FL_CurrentArrangement)] = {}
            FL_Arrangements[str(T_FL_CurrentArrangement)]['tracks'] = {}
            FL_Arrangements[str(T_FL_CurrentArrangement)]['timemarkers'] = {}
            FL_TimeMarkers = FL_Arrangements[str(T_FL_CurrentArrangement)]['timemarkers']
            TimeMarker_id = 0
        if event_id == 241: 
            FL_Arrangements[str(T_FL_CurrentArrangement)]['name'] = event_data.decode('utf-16le').rstrip('\x00\x00')
        if event_id == 233: 
            playlistitems = parse_arrangement(event_data)
            FL_Arrangements[str(T_FL_CurrentArrangement)]['items'] = playlistitems
    
        if event_id == 238: #PLTrackInfo
            FLT_out = parse_trackinfo(event_data)
            currenttracknum = FLT_out[0]
            FL_Tracks = FL_Arrangements[str(T_FL_CurrentArrangement)]['tracks']
            if FLT_out[1] != None:
                FL_Tracks[str(currenttracknum)] = FLT_out[1]
        if event_id == 239: #PLTrackName
            if str(currenttracknum) not in FL_Tracks:
                FL_Tracks[str(currenttracknum)] = {}
            FL_Tracks[str(currenttracknum)]['name'] = event_data.decode('utf-16le').rstrip('\x00\x00')

    
        if event_id == 148: 
            TimeMarker_id += 1
            T_FL_CurrentTimeMarker = TimeMarker_id
            timemarkertype = event_data >> 24
            timemarkertime = event_data & 0x00ffffff
            #print('NewTimeMarker:', timemarkertime, timemarkertype)
            FL_TimeMarkers[str(T_FL_CurrentTimeMarker)] = {}
            FL_TimeMarkers[str(T_FL_CurrentTimeMarker)]['type'] = timemarkertype
            FL_TimeMarkers[str(T_FL_CurrentTimeMarker)]['pos'] = timemarkertime
        if event_id == 205: 
            event_text = event_data.decode('utf-16le').rstrip('\x00\x00')
            #print('\\__TimeMarkerName:', event_text)
            FL_TimeMarkers[str(T_FL_CurrentTimeMarker)]['name'] = event_text
        if event_id == 33: 
            #print('\\__TimeMarkerNumerator:', event_data)
            FL_TimeMarkers[str(T_FL_CurrentTimeMarker)]['numerator'] = event_data
        if event_id == 34: 
            #print('\\__TimeMarkerDenominator:', event_data)
            FL_TimeMarkers[str(T_FL_CurrentTimeMarker)]['denominator'] = event_data
    
    
        if event_id == 64: 
            EnvelopeNum = 0
            T_FL_CurrentChannel = event_data
            #print('Channel:', event_data)
            if str(T_FL_CurrentChannel) not in FL_Channels:
                FL_Channels[str(T_FL_CurrentChannel)] = {}
        if event_id == 21: 
            #print('\\__Type:', event_data)
            FL_Channels[str(T_FL_CurrentChannel)]['type'] = event_data
    
    
    
        if event_id == 38: 
            FL_FXCreationMode = 1
            T_FL_FXColor = None
            T_FL_FXIcon = None
        if FL_FXCreationMode == 0:
            if event_id == 201: 
                event_text = event_data.decode('utf-16le').rstrip('\x00\x00')
                #print('\\__DefPluginName:', event_text)
                DefPluginName = event_text
            if event_id == 212:
                #print('\\__NewPlugin')
                FL_Channels[str(T_FL_CurrentChannel)]['plugin'] = DefPluginName
                FL_Channels[str(T_FL_CurrentChannel)]['plugindata'] = event_data
                #print(event_data)

            if event_id == 203: 
                event_text = event_data.decode('utf-16le').rstrip('\x00\x00')
                #print('\\__PluginName:', event_text)
                FL_Channels[str(T_FL_CurrentChannel)]['name'] = event_text
            if event_id == 155: 
                FL_Channels[str(T_FL_CurrentChannel)]['icon'] = event_data
            if event_id == 128: 
                FL_Channels[str(T_FL_CurrentChannel)]['color'] = event_data
            if event_id == 213: FL_Channels[str(T_FL_CurrentChannel)]['pluginparams'] = event_data
            if event_id == 0: FL_Channels[str(T_FL_CurrentChannel)]['enabled'] = event_data
            if event_id == 218: 
                EnvelopeNum += 1
                if EnvelopeNum == 1: FL_Channels[str(T_FL_CurrentChannel)]['envlfo_pan'] = event_data
                if EnvelopeNum == 2: FL_Channels[str(T_FL_CurrentChannel)]['envlfo_vol'] = event_data
                if EnvelopeNum == 3: FL_Channels[str(T_FL_CurrentChannel)]['envlfo_modx'] = event_data
                if EnvelopeNum == 4: FL_Channels[str(T_FL_CurrentChannel)]['envlfo_mody'] = event_data
                if EnvelopeNum == 5: FL_Channels[str(T_FL_CurrentChannel)]['envlfo_pitch'] = event_data
            if event_id == 209: FL_Channels[str(T_FL_CurrentChannel)]['delay'] = event_data
            if event_id == 138: FL_Channels[str(T_FL_CurrentChannel)]['delayreso'] = event_data
            if event_id == 139: FL_Channels[str(T_FL_CurrentChannel)]['reverb'] = event_data
            if event_id == 89: FL_Channels[str(T_FL_CurrentChannel)]['shiftdelay'] = event_data
            if event_id == 69: FL_Channels[str(T_FL_CurrentChannel)]['fx'] = event_data
            if event_id == 86: FL_Channels[str(T_FL_CurrentChannel)]['fx3'] = event_data
            if event_id == 71: FL_Channels[str(T_FL_CurrentChannel)]['cutoff'] = event_data
            if event_id == 83: FL_Channels[str(T_FL_CurrentChannel)]['resonance'] = event_data
            if event_id == 74: FL_Channels[str(T_FL_CurrentChannel)]['preamp'] = event_data
            if event_id == 75: FL_Channels[str(T_FL_CurrentChannel)]['decay'] = event_data
            if event_id == 76: FL_Channels[str(T_FL_CurrentChannel)]['attack'] = event_data
            if event_id == 85: FL_Channels[str(T_FL_CurrentChannel)]['stdel'] = event_data
            if event_id == 131: FL_Channels[str(T_FL_CurrentChannel)]['fxsine'] = event_data
            if event_id == 70: FL_Channels[str(T_FL_CurrentChannel)]['fadestereo'] = event_data
            if event_id == 22: FL_Channels[str(T_FL_CurrentChannel)]['fxchannel'] = event_data
            if event_id == 219: parse_basicparams(event_data,FL_Channels[str(T_FL_CurrentChannel)])
            if event_id == 221: parse_poly(event_data,FL_Channels[str(T_FL_CurrentChannel)])
            if event_id == 215: parse_chanparams(event_data,FL_Channels[str(T_FL_CurrentChannel)])
            if event_id == 229: FL_Channels[str(T_FL_CurrentChannel)]['ofslevels'] = event_data
            if event_id == 132: FL_Channels[str(T_FL_CurrentChannel)]['cutcutby'] = event_data
            if event_id == 144: FL_Channels[str(T_FL_CurrentChannel)]['layerflags'] = event_data
            #if event_id == 145: FL_Channels[str(T_FL_CurrentChannel)]['filtergroup'] = event_data
            if event_id == 143: FL_Channels[str(T_FL_CurrentChannel)]['sampleflags'] = event_data
            if event_id == 20: FL_Channels[str(T_FL_CurrentChannel)]['looptype'] = event_data
            if event_id == 135: FL_Channels[str(T_FL_CurrentChannel)]['middlenote'] = event_data
            if event_id == 196: 
                samplefilename = event_data.decode('utf-16le').rstrip('\x00\x00')
                if samplefilename[:21] == '%FLStudioFactoryData%':
                    samplefilename = "C:\\Program Files\\Image-Line\\FL Studio 20" + samplefilename[21:]
                FL_Channels[str(T_FL_CurrentChannel)]['samplefilename'] = samplefilename
        else:
            if event_id == 149: 
                T_FL_FXColor = event_data
                #print('FXColor:', T_FL_FXColor)
            if event_id == 95: 
                T_FL_FXIcon = event_data
                #print('FXIcon:', T_FL_FXIcon)
            if event_id == 236: 
                T_FL_FXNum += 1
                #print('FXParams, Num', T_FL_FXNum)
                FL_Mixer[str(T_FL_FXNum)]['color'] = T_FL_FXColor
                FL_Mixer[str(T_FL_FXNum)]['icon'] = T_FL_FXIcon
                FL_Mixer[str(T_FL_FXNum)]['slots'] = {}
                FL_Mixer[str(T_FL_FXNum)]['data'] = event_data
                FXSlots = [{},{},{},{},{},{},{},{},{},{}]
                FXPlugin = None
                T_FL_FXColor = None
                T_FL_FXIcon = None
            if event_id == 201: 
                event_text = event_data.decode('utf-16le').rstrip('\x00\x00')
                #print('\\__DefPluginName:', event_text)
                DefPluginName = event_text
            if event_id == 212: 
                #print('\\__NewPlugin')
                FXPlugin = {}
                FXPlugin['plugin'] = DefPluginName
                FXPlugin['data'] = event_data
            if event_id == 155: FXPlugin['icon'] = event_data
            if event_id == 128: FXPlugin['color'] = event_data
            if event_id == 203: FXPlugin['name'] = event_data.decode('utf-16le').rstrip('\x00\x00')
            if event_id == 98: #FXToSlotNum
                FL_Mixer[str(T_FL_FXNum)]['slots'][event_data] = FXPlugin
                FXPlugin = None
            if event_id == 213: FXPlugin['pluginparams'] = event_data
            if event_id == 235: FL_Mixer[str(T_FL_FXNum)]['routing'] = parse_fxrouting(event_data)
            if event_id == 154: FL_Mixer[str(T_FL_FXNum)]['inchannum'] = event_data
            if event_id == 147: FL_Mixer[str(T_FL_FXNum)]['outchannum'] = event_data
            if event_id == 204: 
                event_text = event_data.decode('utf-16le').rstrip('\x00\x00')
                FL_Mixer[str(T_FL_FXNum+1)]['name'] = event_text

    output = {}
    FL_Main['ppq'] = flp_ppq
    output['FL_Main'] = FL_Main
    output['FL_Patterns'] = FL_Patterns
    output['FL_Channels'] = FL_Channels
    output['FL_Mixer'] = FL_Mixer
    output['FL_FilterGroups'] = FL_ChanGroupName
    output['FL_Arrangements'] = FL_Arrangements
    output['FL_TimeMarkers'] = FL_TimeMarkers
    return output
